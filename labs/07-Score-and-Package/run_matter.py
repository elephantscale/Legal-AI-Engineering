#!/usr/bin/env python3
"""run_matter.py — Lab 07: the whole workflow, with checkpoints and gates (Module 7).

    python3 run_matter.py --corpus ../assets/corpus --work ../work
    python3 run_matter.py --work ../work --resume          # pick up where it stopped
    python3 run_matter.py --work ../work --stage produce   # one stage
    python3 run_matter.py --work ../work --approve-production "A. Reviewer"

Stages and gates:

    [1] ingest ──▶ [2] index ──▶ [3] chunk ──▶ [4] embed ──▶ [5] rag
         │                                                     │
      ◆ GATE: exception list reviewed                           │
                                                                ▼
    [6] richness ──▶ [7] protocol ──▶ [8] classify ──▶ [9] measure ──▶ [10] bundle
                                           │                               │
                                      ◆ GATE: privilege confirmed      ◆ GATE: production
                                                                            approved
                                                       ──▶ [11] produce

Autonomy BETWEEN the gates. A human AT every gate. Everything automatable is automated up
to a gate and never through one.

Why idempotent, append-only and checkpointed is not merely good engineering here: the
artifact chain IS the chain of custody. Mutating stage 3's output in place destroys the
evidence of what stage 2 produced. The best practice and the legal requirement are the
same thing, which is unusual and worth noticing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
MATTER = "SYNTHETIC-DEMO-01"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Stage:
    name: str
    cmd: list[str]
    cwd: Path
    produces: list[str]
    gate: str | None = None
    # An artifact that, if it is ALREADY on disk, this pipeline must adopt rather than
    # rebuild. Only `protocol` has one: a pre-registration that the orchestrator can
    # silently rewrite is not a pre-registration. See the loop in main().
    adopt_existing: str | None = None


def stages(corpus: Path, work: Path) -> list[Stage]:
    py = sys.executable
    return [
        Stage("ingest", [py, "ingest_reference.py", "--corpus", str(corpus),
                         "--out", str(work)],
              LABS / "02-Ingestion", ["catalog.jsonl", "exceptions.jsonl"],
              gate="exception list must be reviewed by a human before production"),
        Stage("index", [py, "search_index.py", "build", "--work", str(work)],
              LABS / "03-Search", ["index.sqlite"]),
        Stage("chunk", [py, "legal_rag.py", "chunk", "--work", str(work)],
              LABS / "04-Legal-RAG-Citations", ["chunks.jsonl"]),
        Stage("embed", [py, "legal_rag.py", "embed", "--work", str(work)],
              LABS / "04-Legal-RAG-Citations", ["vectors.jsonl"]),
        Stage("rag", [py, "legal_rag.py", "eval", "--work", str(work)],
              LABS / "04-Legal-RAG-Citations", ["rag-eval.json", "rag-log.jsonl"]),
        Stage("attest", [py, "local_proof.py", "prove", "--work", str(work)],
              LABS / "05-Local-Model-Egress-Proof", ["attestation.json"]),
        Stage("tripwire", [py, "local_proof.py", "tripwire", "--work", str(work)],
              LABS / "05-Local-Model-Egress-Proof", ["attestation-tripwire.json"]),
        Stage("richness", [py, "defensible_review.py", "richness", "--work", str(work),
                           "--corpus", str(corpus)],
              LABS / "06-Defensible-Review", ["richness.json"]),
        Stage("protocol", [py, "defensible_review.py", "protocol", "--work", str(work),
                           "--corpus", str(corpus)],
              LABS / "06-Defensible-Review", ["validation-protocol.md"],
              adopt_existing="validation-protocol.md"),
        Stage("classify", [py, "defensible_review.py", "classify", "--work", str(work),
                           "--corpus", str(corpus)],
              LABS / "06-Defensible-Review", ["decisions.jsonl"],
              gate="every privilege flag must be confirmed by a human"),
        Stage("measure", [py, "defensible_review.py", "measure", "--work", str(work),
                          "--corpus", str(corpus)],
              LABS / "06-Defensible-Review", ["metrics.json"]),
        Stage("bundle", [py, "defensible_review.py", "bundle", "--work", str(work),
                         "--corpus", str(corpus)],
              LABS / "06-Defensible-Review", ["bundle-path.txt"]),
    ]


# ------------------------------------------------------------------------ checkpoints
def config_hash(stage: Stage) -> str:
    """Idempotency key material: the command, plus the AI config that shapes its output."""
    env = {k: v for k, v in os.environ.items() if k.startswith("LEGAL_AI_")}
    return hashlib.sha256(
        json.dumps({"cmd": stage.cmd[1:], "env": env}, sort_keys=True).encode()
    ).hexdigest()[:16]


def state_dir(work: Path) -> Path:
    d = work / "_state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def is_done(work: Path, stage: Stage) -> bool:
    """Idempotent on (stage, config_hash) AND on the artifacts actually existing."""
    marker = state_dir(work) / f"{stage.name}.done"
    if not marker.exists():
        return False
    try:
        rec = json.loads(marker.read_text())
    except json.JSONDecodeError:
        return False
    if rec.get("config_hash") != config_hash(stage):
        return False
    return all((work / p).exists() for p in stage.produces)


def mark_done(work: Path, stage: Stage, elapsed: float) -> None:
    (state_dir(work) / f"{stage.name}.done").write_text(json.dumps({
        "stage": stage.name, "at": now(), "elapsed_s": round(elapsed, 1),
        "config_hash": config_hash(stage),
        "produces": {p: (work / p).stat().st_size if (work / p).exists() else None
                     for p in stage.produces},
    }, indent=2) + "\n")


def log(work: Path, row: dict) -> None:
    with (state_dir(work) / "run.log").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": now()}) + "\n")


# ----------------------------------------------------------------------------- gates
def gate_file(work: Path, name: str) -> Path:
    return state_dir(work) / f"gate-{name}.json"


def record_approval(work: Path, name: str, who: str, note: str = "") -> Path:
    p = gate_file(work, name)
    p.write_text(json.dumps({"gate": name, "approved_by": who, "note": note,
                             "at": now()}, indent=2) + "\n")
    return p


def approval(work: Path, name: str) -> dict | None:
    p = gate_file(work, name)
    return json.loads(p.read_text()) if p.exists() else None


# --------------------------------------------------------------------------- produce
def cmd_produce(work: Path) -> int:
    """Emit the production set: Bates numbers, a load file, and a manifest.

    This is the irreversible, outward-facing step. It requires a recorded human approval
    — not a config flag, not a confidence threshold. Someone's name goes next to this.
    """
    appr = approval(work, "production")
    if not appr:
        print("PRODUCTION GATE — no recorded approval.\n")
        print("  A production is irreversible and outward-facing: once documents go to")
        print("  the other side you cannot take them back. It needs a human's name.\n")
        print("  Record the approval with:")
        print('    python3 run_matter.py --work ../work --approve-production "Your Name"\n')
        print("  Before you do, check:")
        print("    - metrics.json: is the elusion test PASSING against the pre-set threshold?")
        print("    - decisions.jsonl: has every privilege flag been confirmed by a human?")
        print("    - exceptions.jsonl: has the exception list been triaged?")
        return 2

    dec_path = work / "decisions.jsonl"
    if not dec_path.exists():
        raise SystemExit("run `classify` first")
    decisions = [json.loads(l) for l in dec_path.open(encoding="utf-8") if l.strip()]
    cat = {json.loads(l)["doc_id"]: json.loads(l)
           for l in (work / "catalog.jsonl").open(encoding="utf-8") if l.strip()}

    # what goes out: responsive, NOT privileged, and not still sitting in a human queue
    out_docs, withheld = [], []
    for d in decisions:
        reason = None
        if d["decision"] != "responsive":
            reason = "not responsive"
        elif d.get("privileged"):
            reason = "PRIVILEGED — withheld"
        elif d["route"].endswith("human-review"):
            reason = "pending human review"
        (withheld if reason else out_docs).append({**d, "withheld_reason": reason})

    prod = work / "production" / "VOL001"
    prod.mkdir(parents=True, exist_ok=True)
    D, Q = "\x14", "\xfe"
    header = ["BEGBATES", "ENDBATES", "CUSTODIAN", "SOURCE_PATH", "TEXT_PATH",
              "RESPONSIVE", "PRODUCED_IN"]
    lines = [D.join(f"{Q}{h}{Q}" for h in header)]
    bates = 0
    text_dir = prod / "TEXT"
    text_dir.mkdir(exist_ok=True)
    for d in out_docs:
        bates += 1
        beg = f"HOLL{bates:07d}"
        src = work / "text" / f"{d['doc_id']}.txt"
        rel = f"\\TEXT\\{beg}.txt"
        if src.exists():
            (text_dir / f"{beg}.txt").write_bytes(src.read_bytes())
        row = [beg, beg, d.get("custodian") or "", (d.get("source_path") or ""),
               rel, "Y", MATTER]
        lines.append(D.join(f"{Q}{f}{Q}" for f in row))
    # cp1252 and CRLF, because that is what the receiving review platform expects. If a
    # custodian name or path will not encode, that is a real problem to solve now, not a
    # character to silently drop on the other side.
    (prod / "VOL001.dat").write_bytes(
        ("\r\n".join(lines) + "\r\n").encode("cp1252", errors="replace"))

    met = work / "metrics.json"
    metrics = json.loads(met.read_text()) if met.exists() else {}
    exc = work / "exceptions.jsonl"
    n_exc = sum(1 for _ in exc.open(encoding="utf-8")) if exc.exists() else 0
    manifest = {
        "matter": MATTER, "volume": "VOL001", "produced_at": now(),
        "approved_by": appr["approved_by"], "approved_at": appr["at"],
        "documents_produced": len(out_docs),
        "bates_range": [f"HOLL{1:07d}", f"HOLL{bates:07d}"] if bates else None,
        "withheld": {
            "total": len(withheld),
            "by_reason": {r: sum(1 for w in withheld if w["withheld_reason"] == r)
                          for r in {w["withheld_reason"] for w in withheld}},
        },
        "processing_exceptions": n_exc,
        "validation": {
            "recall": (metrics.get("metrics", {}).get("recall") or {}).get("value"),
            "recall_ci95": (metrics.get("metrics", {}).get("recall") or {}).get("ci95"),
            "elusion": (metrics.get("metrics", {}).get("elusion") or {}).get("value"),
            "elusion_threshold": (metrics.get("verdict") or {}).get("elusion_threshold"),
            "elusion_passed": (metrics.get("verdict") or {}).get("elusion_passed"),
            "protocol_sha256": (metrics.get("protocol") or {}).get("sha256"),
        },
        "disclosures": [
            f"{n_exc} document(s) did not process. The exception list is available.",
            "AI components used in this review are disclosed in attestation.json; the "
            "model is pinned by hash in the reproducibility bundle's manifest.json.",
            "The validation protocol was written before the classification run; its hash "
            "is recorded above.",
        ],
        "load_file": {"format": "Concordance .dat", "encoding": "cp1252",
                      "line_ending": "CRLF",
                      "field_delimiter": "\\x14", "quote": "\\xfe"},
    }
    (prod / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log(work, {"stage": "produce", "documents": len(out_docs),
               "approved_by": appr["approved_by"]})

    print(f"\n  produced  : {len(out_docs)} documents  "
          f"(Bates HOLL0000001–HOLL{bates:07d})")
    print(f"  withheld  : {len(withheld)}")
    for r, n in manifest["withheld"]["by_reason"].items():
        print(f"      {r:<28} {n}")
    print(f"  approved  : {appr['approved_by']} at {appr['at']}")
    print(f"\n  wrote {prod}/VOL001.dat, manifest.json, TEXT/")
    print("\n  Read the 'disclosures' list in manifest.json. Volunteering the exception "
          "count\n  and the AI disclosure is what a competent producing party does — and "
          "it is the\n  first thing a competent opposing expert asks for anyway.")
    return 0


# ------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default="../assets/corpus")
    ap.add_argument("--work", default="../work")
    ap.add_argument("--stage", help="run exactly one stage (or 'produce')")
    ap.add_argument("--resume", action="store_true",
                    help="skip stages already done with the same config (the default)")
    ap.add_argument("--force", action="store_true", help="re-run every stage")
    ap.add_argument("--approve-production", metavar="NAME",
                    help="record the human approval for the production gate")
    ap.add_argument("--approve-gate", nargs=2, metavar=("GATE", "NAME"),
                    help="record approval for a named gate, e.g. exceptions 'A. Reviewer'")
    args = ap.parse_args()
    work, corpus = Path(args.work).resolve(), Path(args.corpus).resolve()
    work.mkdir(parents=True, exist_ok=True)

    if args.approve_production:
        p = record_approval(work, "production", args.approve_production,
                            "reviewed metrics, privilege queue and exception list")
        print(f"recorded production approval: {args.approve_production}\n  {p}")
        return 0
    if args.approve_gate:
        g, who = args.approve_gate
        p = record_approval(work, g, who)
        print(f"recorded approval for gate '{g}': {who}\n  {p}")
        return 0
    if args.stage == "produce":
        return cmd_produce(work)

    plan = stages(corpus, work)
    if args.stage:
        plan = [s for s in plan if s.name == args.stage]
        if not plan:
            print(f"unknown stage {args.stage!r}. Stages: "
                  f"{', '.join(s.name for s in stages(corpus, work))}, produce",
                  file=sys.stderr)
            return 2

    print(f"\nmatter {MATTER}   work {work}\n")
    for s in plan:
        # A student who actually finished the Core arrives with a pre-registration already
        # written by Lab 06. Re-running `protocol` would hit Lab 06's refusal — correctly —
        # and stop the Deep Dive at its first command. The artifact on disk IS this stage's
        # output, so adopt it, hash it into the ledger, and move on. Deliberately ahead of
        # --force: nothing this orchestrator does may overwrite a pre-registration. The only
        # way to revise one is Lab 06's own `protocol --force`, by hand, on purpose.
        if s.adopt_existing and (work / s.adopt_existing).exists():
            art = work / s.adopt_existing
            sha = hashlib.sha256(art.read_bytes()).hexdigest()
            print(f"  [keep] {s.name:<10} {s.adopt_existing} was already written "
                  f"(sha256 {sha[:12]}) -> adopted, not rebuilt")
            mark_done(work, s, 0.0)
            log(work, {"stage": s.name, "status": "adopted-preexisting",
                       "artifact": s.adopt_existing, "sha256": sha})
            continue
        if is_done(work, s) and not args.force:
            print(f"  [skip] {s.name:<10} already done with this config")
            continue
        print(f"  [run ] {s.name:<10} ", end="", flush=True)
        t0 = time.time()
        r = subprocess.run(s.cmd, cwd=s.cwd, capture_output=True, text=True)
        el = time.time() - t0
        if r.returncode != 0:
            print(f"FAILED after {el:.1f}s")
            print("\n" + (r.stdout or "")[-1500:])
            print((r.stderr or "")[-1500:])
            log(work, {"stage": s.name, "status": "failed", "elapsed_s": round(el, 1),
                       "returncode": r.returncode})
            print(f"\n  Stage '{s.name}' failed. Nothing after it ran. Fix it and re-run "
                  f"with --resume;\n  completed stages are not repeated.")
            return 1
        mark_done(work, s, el)
        log(work, {"stage": s.name, "status": "ok", "elapsed_s": round(el, 1)})
        print(f"ok  {el:5.1f}s  -> {', '.join(s.produces)}")
        if s.gate:
            ap_rec = approval(work, s.name)
            flag = f"approved by {ap_rec['approved_by']}" if ap_rec \
                else "NOT APPROVED — a human must sign this off"
            print(f"         ◆ GATE: {s.gate}\n           {flag}")

    print("\n  pipeline complete. Next:")
    print("    python3 sais100.py   --work ../work        # score it")
    print("    python3 run_matter.py --work ../work --stage produce   # hits the gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
