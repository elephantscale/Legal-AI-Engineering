#!/usr/bin/env python3
"""local_proof.py — Lab 04: run the RAG locally and PROVE nothing left (Module 5).

    python3 local_proof.py observe  --work ../work      # what does it do TODAY?
    python3 local_proof.py prove    --work ../work      # enforce + attest
    python3 local_proof.py tripwire --work ../work      # watch a deliberate leak get blocked
    python3 local_proof.py compare  --work ../work      # local vs cloud, honestly

Build order matters, and it is the order of the subcommands:

    1. OBSERVE  — on a system you did not build, find out what it ACTUALLY does before
                  you change anything. Teams are routinely surprised.
    2. ENFORCE  — default-deny, loopback only.
    3. ATTEST   — emit the artifact: the window, the components, every connection, and
                  the claim.

Teams that enforce first break things and learn nothing.

The attestation this writes states its own limits (in-process scope, a time window, DNS
counted as disclosure, enforcement properly belonging to a firewall). A narrow claim with
an artifact behind it beats a broad claim with a brochure behind it — every time.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "03-Legal-RAG-Citations"))

from egress import EgressGuard, EgressBlocked, write_attestation  # noqa: E402
import llm                                                         # noqa: E402

MATTER = "SYNTHETIC-DEMO-01"


def ai_components() -> dict:
    """Enumerate every AI component honestly. There are only ever four kinds.

    Module 5's four leak points: OCR/extraction, embeddings, the chat model, and logs.
    Localizing only the chat model buys you nothing — your posture is set by the leakiest
    stage, not the last one.
    """
    info = llm.model_info()
    ocr_engine = os.environ.get("LEGAL_AI_OCR", "tesseract (local)")
    return {
        "chat": {"endpoint": info.chat_endpoint, "model": info.chat_model,
                 "runtime": info.runtime, "weights_sha256": info.weights_sha256,
                 "quantization": info.quantization, "local": info.local,
                 "decoding": info.decoding},
        "embeddings": {"endpoint": info.chat_endpoint, "model": info.embed_model,
                       "dim": info.embed_dim, "local": info.local},
        "ocr_extraction": {"engine": ocr_engine, "local": True,
                           "note": "If OCR is a cloud document-intelligence API, the raw "
                                   "page leaked one step before your local LLM and the "
                                   "LLM decision was cosmetic."},
        "telemetry_and_logs": {
            "destination": "local files under ../work only",
            "local": True,
            "note": "THE LEAK POINT PEOPLE FORGET. An APM/tracing SDK or an error "
                    "reporter can ship prompt text — i.e. document text — to a third "
                    "party you never evaluated. Audit this one by name.",
        },
    }


def _load_questions(work: Path, evalset: Path | None, limit: int) -> list[str]:
    if evalset and evalset.exists():
        spec = json.loads(evalset.read_text(encoding="utf-8"))
        return [c["question"] for c in spec["cases"]][:limit]
    return ["What was the indemnification cap in Section 7.3?"][:limit]


def _run_rag(work: Path, questions: list[str]) -> list[dict]:
    """Import the Lab 03 pipeline and answer each question. One place, so the guard
    wraps the whole AI layer."""
    import legal_rag
    out = []
    for q in questions:
        r = legal_rag.ask(work, q, log=True)
        out.append({"question": q, "answer": r["answer"],
                    "citations": [c["doc_id"] for c in r["citations"]],
                    "verifier_ok": r["verdict"]["ok"],
                    "refused": r["verdict"]["refused"]})
    return out


# ----------------------------------------------------------------------------- observe
def cmd_observe(work: Path, questions: list[str]) -> int:
    """Step 1: change nothing, record everything."""
    print("OBSERVE — nothing is being enforced. Recording what this pipeline actually "
          "does.\n")
    with EgressGuard(policy="observe") as g:
        results = _run_rag(work, questions)
    print(f"  questions answered     : {len(results)}")
    print(f"  connection attempts    : {len(g.attempts)}")
    print(f"  non-loopback           : {g.non_loopback}")
    print("\n  by peer:")
    for row in g.summary()["by_peer"]:
        flag = "loopback" if row["loopback"] else "*** EXTERNAL ***"
        print(f"    {row['peer']:<32} {row['count']:>5}x  {row['kind']:<8} {flag}")
    path = write_attestation(work / "attestation-observe.json", guard=g, matter=MATTER,
                             ai_components=ai_components(),
                             documents_processed=len(results))
    print(f"\n  wrote {path}")
    if g.non_loopback:
        print("\n  !! This pipeline reached outside the host. Find out what, and why, "
              "BEFORE you enforce — then enforce.")
    else:
        print("\n  Nothing left the host in observe mode. Now enforce it, so it cannot.")
    return 0


# ------------------------------------------------------------------------------- prove
def cmd_prove(work: Path, questions: list[str]) -> int:
    """Steps 2 + 3: enforce default-deny, run for real, emit the attestation."""
    policy = os.environ.get("LEGAL_AI_EGRESS", "deny")
    print(f"ENFORCE + ATTEST — policy '{policy}'. Loopback only; everything else is "
          f"blocked and logged.\n")
    blocked_during_run = []
    with EgressGuard(policy=policy) as g:
        try:
            results = _run_rag(work, questions)
        except EgressBlocked as e:
            print(f"  !! The pipeline tried to leave the host and was STOPPED:\n     {e}\n")
            print("     This is the guard working. Find the component that did it — it is")
            print("     one of the four leak points — point it at a local endpoint, and")
            print("     run again.")
            results = []
            blocked_during_run.append(str(e))
    ok = sum(1 for r in results if r["verifier_ok"])
    refused = sum(1 for r in results if r["refused"])
    print(f"  questions answered     : {len(results)}  "
          f"(verifier pass {ok}, refusals {refused})")
    print(f"  connection attempts    : {len(g.attempts)}")
    print(f"  blocked                : {g.blocked}")
    print(f"  non-loopback           : {g.non_loopback}")
    path = write_attestation(work / "attestation.json", guard=g, matter=MATTER,
                             ai_components=ai_components(),
                             documents_processed=len(results),
                             extra={"questions_answered": len(results),
                                    "blocked_during_run": blocked_during_run})
    doc = json.loads(Path(path).read_text())
    print(f"\n  claim : {doc['claim']}")
    print(f"  wrote : {path}")
    print("\n  Read 'scope_and_limits' in that file before you show it to anyone. Naming "
          "your limits is what makes the artifact credible.")
    return 0 if g.non_loopback == 0 else 1


# ---------------------------------------------------------------------------- tripwire
def cmd_tripwire(work: Path) -> int:
    """Attempt a deliberate leak and watch it get blocked AND logged.

    This is the part that makes the lesson physical: your own code gets stopped, with a
    log line naming the destination.
    """
    print("TRIPWIRE — deliberately trying to leave the host. Each attempt should be "
          "blocked and recorded.\n")
    targets = [
        ("a hosted model API", "api.openai.com", 443),
        ("a SaaS log aggregator", "in.logs.example-apm.com", 443),
        ("a cloud OCR endpoint", "documentai.googleapis.com", 443),
        ("a bare IP, no DNS", "93.184.216.34", 443),
        ("the LOCAL model (should succeed)", "127.0.0.1", 11434),
    ]
    with EgressGuard(policy="deny") as g:
        for label, host, port in targets:
            try:
                s = socket.create_connection((host, port), timeout=2)
                s.close()
                print(f"  {label:<36} -> CONNECTED  ({host}:{port})")
            except EgressBlocked as e:
                print(f"  {label:<36} -> BLOCKED")
                print(f"  {'':<36}    {e}")
            except OSError:
                print(f"  {label:<36} -> allowed by policy, nothing listening "
                      f"({host}:{port})")
    path = write_attestation(work / "attestation-tripwire.json", guard=g, matter=MATTER,
                             ai_components=ai_components(), documents_processed=0)
    print(f"\n  attempts {len(g.attempts)}  blocked {g.blocked}  "
          f"non-loopback {g.non_loopback}")
    print(f"  wrote {path}")
    print("\n  Note that the blocked attempts are IN the attestation. An attestation that "
          "hides the attempts is worth nothing; one that records them is evidence that "
          "the control is live.")
    return 0


# ----------------------------------------------------------------------------- compare
def cmd_compare(work: Path, questions: list[str]) -> int:
    """Local vs cloud on the same questions. Record the delta honestly.

    Some students will find the local model clearly worse. That is the correct, valuable
    outcome, and it is what a real validation pass looks like. The answer is not to hide
    it: size the hardware, pick a bigger tier, or document the delta and the mitigation.
    """
    import importlib
    import legal_rag
    rows = []
    for mode in ("local", "cloud"):
        if mode == "cloud" and not os.environ.get("LEGAL_AI_API_KEY"):
            print("  (skipping cloud: no LEGAL_AI_API_KEY set — which is the right "
                  "default for a legal course)")
            continue
        if mode == "cloud":
            print("\n  !! MODE=cloud. Document text WILL leave this machine. The corpus "
                  "is synthetic, which is the only reason this is allowed.")
        os.environ["LEGAL_AI_MODE"] = mode
        importlib.reload(llm)
        importlib.reload(legal_rag)
        t0 = time.time()
        with EgressGuard(policy="observe") as g:
            res = _run_rag(work, questions)
        info = llm.model_info()
        rows.append({
            "mode": mode, "model": info.chat_model, "embed": info.embed_model,
            "local": info.local,
            "questions": len(res),
            "verifier_pass": sum(1 for r in res if r["verifier_ok"]),
            "refusals": sum(1 for r in res if r["refused"]),
            "cited_docs_total": sum(len(r["citations"]) for r in res),
            "non_loopback_connections": g.non_loopback,
            "wall_clock_s": round(time.time() - t0, 1),
        })
    out = {"matter": MATTER, "comparison": rows,
           "how_to_read_this": [
               "verifier_pass is a floor, not a quality score: it proves the answer was "
               "well-formed and citable, not that it was right.",
               "non_loopback_connections is the column that decides whether you are "
               "allowed to use the row at all.",
               "If local loses on quality, the honest moves are: a bigger VRAM tier, a "
               "larger model, better chunking — or documenting the delta and the "
               "mitigation. Hiding it is not on the list.",
           ]}
    (work / "local-vs-cloud.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n{'mode':<8} {'model':<22} {'pass':>5} {'refus':>6} {'cites':>6} "
          f"{'egress':>7} {'sec':>6}")
    print("-" * 66)
    for r in rows:
        print(f"{r['mode']:<8} {r['model'][:22]:<22} {r['verifier_pass']:>5} "
              f"{r['refusals']:>6} {r['cited_docs_total']:>6} "
              f"{r['non_loopback_connections']:>7} {r['wall_clock_s']:>6}")
    print(f"\nwrote {work / 'local-vs-cloud.json'}")
    return 0


# -------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["observe", "prove", "tripwire", "compare"])
    ap.add_argument("--work", default="../work")
    ap.add_argument("--evalset",
                    default=str(HERE.parents[0] / "03-Legal-RAG-Citations" / "evalset.json"))
    ap.add_argument("--limit", type=int, default=5, help="questions to run (default 5)")
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if not (work / "chunks.jsonl").exists():
        print(f"error: no chunks at {work} — run Lab 03 `chunk` and `embed` first",
              file=sys.stderr)
        return 2
    qs = _load_questions(work, Path(args.evalset), args.limit)

    if args.cmd == "observe":
        return cmd_observe(work, qs)
    if args.cmd == "prove":
        return cmd_prove(work, qs)
    if args.cmd == "tripwire":
        return cmd_tripwire(work)
    return cmd_compare(work, qs)


if __name__ == "__main__":
    sys.exit(main())
