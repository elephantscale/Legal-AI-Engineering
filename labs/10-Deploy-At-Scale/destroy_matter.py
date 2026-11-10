#!/usr/bin/env python3
"""destroy_matter.py — Lab 10: end-of-matter destruction, and proof of it (Module 11).

    python3 destroy_matter.py plan    --work ../work --matter SYNTHETIC-DEMO-01
    python3 destroy_matter.py destroy --work ../work --matter SYNTHETIC-DEMO-01 \
            --confirm SYNTHETIC-DEMO-01 --by "A. Reviewer, Esq."
    python3 destroy_matter.py verify  --work ../work --matter SYNTHETIC-DEMO-01

Every engagement letter has a retention clause and every one of them eventually comes
due. "We deleted the documents" is not a true statement about an AI pipeline, because a
pipeline makes copies of the evidence in places nobody lists:

    extracted text          a verbatim copy of the document
    the search index        a copy, tokenized, from which text can be reconstructed
    chunks.jsonl            a copy, in windows, with offsets
    vectors.jsonl           a lossy copy — and lossy is not "not a copy"
    rendered prompts        a copy of whatever was retrieved, inside the prompt
    responses               quotes from the documents, by design
    the work queue DB       filenames, sizes, custodian paths
    OCR sidecars            the text of scanned pages
    the reproducibility     a deliberate, complete copy of all of the above
      bundle
    production sets         a copy you already sent to someone else

The design of this tool reflects one claim: **you cannot destroy by list alone.** A list
is written by someone who remembers; a pipeline grows files that nobody remembers. So
`verify` does not check the list — it searches what remains for traces, and it is allowed
to disagree with the plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".jsonl", ".json", ".md", ".csv", ".dat", ".opt", ".log",
                 ".yml", ".yaml", ".html", ".xml"}
BINARY_SUFFIXES = {".sqlite", ".db", ".png", ".jpg", ".jpeg", ".pdf", ".zip"}
SCAN_MAX_BYTES = 4_000_000


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Known artifact classes. This is the LIST, and the point of the lab is that the list is
# never complete — which is why `verify` does not consult it.
KNOWN = [
    ("text/",                     "extracted text — a verbatim copy of each document"),
    ("text-scaled/",              "extracted text from the scaled workers"),
    ("catalog.jsonl",             "the document catalog: paths, custodians, metadata"),
    ("exceptions.jsonl",          "the exception list"),
    ("manifest.json",             "the ingest manifest"),
    ("index.sqlite",              "the search index — reconstructible text"),
    ("index-manifest.json",       "index pins"),
    ("chunks.jsonl",              "chunked copies with offsets"),
    ("chunks-manifest.json",      "chunking pins"),
    ("vectors.jsonl",             "embeddings — a LOSSY copy, which is still a copy"),
    ("vectors-manifest.json",     "embedding pins"),
    ("rag-log.jsonl",             "questions, answers and citations"),
    ("rag-runs/",                 "every rendered prompt, with retrieved document text"),
    ("rag-eval.json",             "eval results, quoting documents"),
    ("decisions.jsonl",           "coding decisions with rationales"),
    ("richness.json",             "sample statistics"),
    ("metrics.json",              "validation metrics"),
    ("validation-protocol.md",    "the protocol"),
    ("attestation.json",          "the egress attestation"),
    ("attestation-tripwire.json", "the tripwire attestation"),
    ("entities.jsonl",            "entities with document offsets"),
    ("merge_log.jsonl",           "identity merges"),
    ("threads.jsonl",             "thread structure"),
    ("dropped_recipients.jsonl",  "header findings"),
    ("timeline.md",               "the chronology, citing documents"),
    ("timeline_gaps.jsonl",       "gap findings"),
    ("lineage_findings.jsonl",    "version diffs, quoting clause text"),
    ("collection_leads.jsonl",    "leads, quoting document context"),
    ("steps.jsonl",               "agent steps, with tool arguments"),
    ("exception_memo.md",         "the agent's memo"),
    ("approvals.jsonl",           "approval records"),
    ("queue.sqlite",              "the work queue: paths, sizes, custodians"),
    ("throughput.json",           "throughput measurements"),
    ("production/",               "the production set — ALREADY SENT; destruction here "
                                  "does not recall it"),
    ("_state/",                   "pipeline checkpoints and gate approvals"),
    ("sais100-baseline.json",     "the score"),
]


@dataclass
class Item:
    path: Path
    why: str
    bytes: int
    known: bool


def matter_tokens(work: Path, matter: str) -> list[str]:
    """What a trace of this matter looks like in a file.

    The matter id alone is not enough: most files never mention it. Custodian names and
    Bates prefixes are what actually appear, so they are read out of the catalog rather
    than guessed.
    """
    toks = {matter}
    cat = work / "catalog.jsonl"
    if cat.exists():
        # Read the WHOLE catalog. Sampling the first N rows misses the custodians who
        # happen to sort late, and a verification that misses a custodian is worse than
        # no verification: it returns "clean".
        for line in cat.open(encoding="utf-8"):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            c = (d.get("custodian") or "").strip()
            if c and c.lower() not in ("unknown", "none", "-"):
                toks.add(c)
            m = re.search(r"([A-Za-z]{3,6})\d{7}", d.get("source_path", ""))
            if m:
                toks.add(m.group(1))
    prod = work / "production"
    if prod.exists():
        for p in prod.rglob("*.dat"):
            m = re.search(rb"([A-Za-z]{3,6})\d{7}", p.read_bytes()[:4000])
            if m:
                toks.add(m.group(1).decode())
    return sorted(t for t in toks if len(t) >= 4)


def plan_items(work: Path, matter: str) -> tuple[list[Item], list[Item]]:
    """Returns (from_the_list, found_by_scanning_and_NOT_on_the_list)."""
    listed: list[Item] = []
    seen: set[Path] = set()
    for rel, why in KNOWN:
        p = work / rel.rstrip("/")
        if not p.exists():
            continue
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            for f in p.rglob("*"):
                seen.add(f.resolve())
            seen.add(p.resolve())
        else:
            size = p.stat().st_size
            seen.add(p.resolve())
        listed.append(Item(p, why, size, True))

    for b in sorted(work.glob("case-snapshot-*")):
        if b.resolve() not in seen:
            size = sum(f.stat().st_size for f in b.rglob("*") if f.is_file())
            for f in b.rglob("*"):
                seen.add(f.resolve())
            seen.add(b.resolve())
            listed.append(Item(b, "the reproducibility bundle — a deliberate complete "
                                  "copy of the review", size, True))

    # Now the part that matters: everything else in the work tree, checked for traces.
    toks = matter_tokens(work, matter)
    extra: list[Item] = []
    for p in sorted(work.rglob("*")):
        if not p.is_file() or p.resolve() in seen:
            continue
        hit = next((t for t in toks if t in p.as_posix()), None)
        if hit is None and (p.suffix.lower() in TEXT_SUFFIXES
                            and p.stat().st_size <= SCAN_MAX_BYTES):
            try:
                blob = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                blob = ""
            hit = next((t for t in toks if t in blob), None)
        if hit is not None:
            extra.append(Item(p, f"NOT ON THE LIST — contains {hit!r}",
                              p.stat().st_size, False))
    return listed, extra


def cmd_plan(work: Path, matter: str) -> int:
    listed, extra = plan_items(work, matter)
    total = sum(i.bytes for i in listed) + sum(i.bytes for i in extra)
    print(f"\n  matter : {matter}")
    print(f"  work   : {work}")
    print(f"  tokens searched for: {', '.join(matter_tokens(work, matter))}\n")
    print(f"  ON THE LIST ({len(listed)} artifact(s), "
          f"{sum(i.bytes for i in listed) / 1e6:.1f} MB)\n")
    for i in listed:
        print(f"    {i.bytes / 1e6:>8.2f} MB  {i.path.name}")
        print(f"                 {i.why}")
    print(f"\n  FOUND BY SCANNING, NOT ON THE LIST "
          f"({len(extra)}, {sum(i.bytes for i in extra) / 1e6:.1f} MB)\n")
    if extra:
        for i in extra[:30]:
            print(f"    {i.bytes / 1e6:>8.2f} MB  "
                  f"{i.path.relative_to(work).as_posix()}")
            print(f"                 {i.why}")
        if len(extra) > 30:
            print(f"    … and {len(extra) - 30} more")
        print("\n  ^^ THIS is the lesson. Every item above is matter data that a")
        print("     destruction list did not name. On a real system the list is")
        print("     written once and the pipeline keeps growing files.")
    else:
        print("    none — but do not take that as proof. It means the scan's token list")
        print("    found nothing, and the scan skips binaries it cannot read.")
    print(f"\n  TOTAL: {total / 1e6:.1f} MB across "
          f"{len(listed) + len(extra)} artifact(s)")
    print(f"\n  Nothing has been deleted. To destroy:")
    print(f"    python3 destroy_matter.py destroy --work {work} "
          f"--matter {matter} \\")
    print(f"        --confirm {matter} --by \"Your Name\"")
    return 0


def shred(p: Path, passes: int) -> None:
    """Overwrite before unlinking.

    Be honest about what this does and does not achieve. On an SSD with wear levelling,
    or any copy-on-write filesystem, overwriting a file's logical blocks does NOT
    necessarily overwrite the physical cells. Real destruction on modern storage means
    full-disk encryption and destroying the key, or physical destruction. This pass is
    defence in depth and a record of intent — and the certificate says exactly that
    rather than claiming more.
    """
    if passes <= 0:
        return
    try:
        size = p.stat().st_size
        with p.open("r+b") as fh:
            for _ in range(passes):
                fh.seek(0)
                fh.write(os.urandom(min(size, 1 << 20)) * 1 if size <= (1 << 20)
                         else os.urandom(1 << 20))
                fh.flush()
                os.fsync(fh.fileno())
    except OSError:
        pass


def cmd_destroy(work: Path, matter: str, confirm: str, by: str, passes: int,
                dry_run: bool, list_only: bool = False) -> int:
    if confirm != matter:
        print(f"\n  REFUSED. --confirm must be exactly the matter id.")
        print(f"  You passed {confirm!r}; the matter is {matter!r}.")
        print(f"\n  Typing the matter id is the control. A --force flag would be "
              f"muscle memory\n  by the third time you used it.")
        return 2
    if not by.strip():
        print("\n  REFUSED. --by must name the person authorizing destruction.")
        return 2

    listed, extra = plan_items(work, matter)
    # --list-only destroys ONLY what the hand-written list names, which is what every
    # real destruction script does on its first version. Use it once, then run `verify`,
    # and the gap between the two is the lesson of this part of the lab.
    items = listed if list_only else listed + extra
    if list_only and extra:
        print(f"\n  --list-only: skipping {len(extra)} artifact(s) that the scan found "
              f"but the list\n  does not name. This is deliberate. Run `verify` "
              f"afterwards.")
    if not items:
        print(f"\n  nothing found for matter {matter}.")
        return 0

    # Derive the verification tokens BEFORE deleting anything. They come from the
    # catalog, and the catalog is about to stop existing. Computing them after the
    # deletion loop yields the matter id and nothing else — which is exactly the bug
    # that makes a post-destruction scan report "clean" on a tree full of custodian
    # names. Order of operations is the control here.
    tokens = matter_tokens(work, matter)

    record = []
    freed = 0
    for i in items:
        files = [f for f in i.path.rglob("*") if f.is_file()] if i.path.is_dir() \
            else [i.path]
        for f in files:
            record.append({"path": f.relative_to(work).as_posix(),
                           "bytes": f.stat().st_size,
                           "sha256": hashlib.sha256(f.read_bytes()).hexdigest()
                           if f.stat().st_size <= SCAN_MAX_BYTES else None,
                           "on_destruction_list": i.known})
            freed += f.stat().st_size
        if dry_run:
            continue
        for f in files:
            shred(f, passes)
        if i.path.is_dir():
            shutil.rmtree(i.path, ignore_errors=True)
        else:
            i.path.unlink(missing_ok=True)

    cert = {
        "certificate": "matter destruction",
        "matter": matter,
        "authorized_by": by,
        "at": now(),
        # The tokens are recorded HERE because verification happens AFTER destruction,
        # and the tokens were derived from the catalog that destruction just deleted.
        # Without this field `verify` can only search for the matter id, which almost
        # no file contains — so it would report "clean" on a tree full of custodian
        # names. Writing the search terms into the certificate before you destroy the
        # source of those terms is the whole trick.
        "verification_tokens": tokens,
        "dry_run": dry_run,
        "list_only": list_only,
        "artifacts_destroyed": len(record),
        "bytes_freed": freed,
        "overwrite_passes": passes,
        "found_by_scanning_not_on_list": sum(1 for r in record
                                             if not r["on_destruction_list"]),
        "inventory": record,
        "claim": "The artifacts inventoried above were removed from this host.",
        "scope_and_limits": [
            "This covers this work directory on this host only.",
            "It does NOT cover backups, snapshots, replicas, or any volume not mounted "
            "here. Those are a separate, named task.",
            "It does NOT recall a production set already delivered to another party.",
            "Overwriting is defence in depth, not a guarantee: on SSDs with wear "
            "levelling and on copy-on-write filesystems, logical overwrites may not "
            "reach the physical cells. Assured destruction on modern storage means "
            "full-disk encryption plus key destruction, or physical destruction.",
            "The source collection (mounted read-only) is deliberately untouched; it is "
            "destroyed separately, under the custodian's own retention schedule.",
            "An automated inventory cannot prove completeness. Run `verify` and treat "
            "its findings as authoritative over this list.",
        ],
    }
    # The certificate lands OUTSIDE the work dir: it must survive the destruction of
    # the thing it certifies, and `rm -rf work/` is how most of these end.
    out = work.parent / f"destruction-certificate-{matter}.json" if not dry_run \
        else work / f"destruction-plan-{matter}.json"
    out.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    print(f"\n  {'DRY RUN — nothing deleted' if dry_run else 'DESTROYED'}")
    print(f"  artifacts  : {len(record)}")
    print(f"  bytes      : {freed / 1e6:.1f} MB")
    print(f"  not on list: {cert['found_by_scanning_not_on_list']}")
    print(f"  authorized : {by}")
    print(f"\n  certificate: {out}")
    print(f"\n  Read 'scope_and_limits'. A destruction certificate that does not say")
    print(f"  what it failed to cover is the kind of document that gets you in more")
    print(f"  trouble than having destroyed nothing at all.")
    if not dry_run:
        print(f"\n  Now verify:")
        print(f"    python3 destroy_matter.py verify --work {work} --matter {matter}")
    return 0


def load_cert_tokens(work: Path, matter: str) -> list[str]:
    """Recover the search terms from the destruction certificate, if there is one."""
    for cand in (work.parent / f"destruction-certificate-{matter}.json",
                 work / f"destruction-plan-{matter}.json"):
        if cand.exists():
            try:
                return list(json.loads(cand.read_text()).get(
                    "verification_tokens") or [])
            except (json.JSONDecodeError, OSError):
                pass
    return []


def cmd_verify(work: Path, matter: str) -> int:
    """Search what REMAINS. This does not consult the destruction list, on purpose."""
    if not work.exists():
        print(f"\n  {work} does not exist. Nothing remains.")
        return 0
    cert_toks = load_cert_tokens(work, matter)
    live_toks = matter_tokens(work, matter)
    toks = sorted(set(cert_toks) | set(live_toks) | {matter})
    if not cert_toks and len(toks) <= 1:
        print("\n  WARNING: no destruction certificate found and no catalog to derive")
        print("  search terms from, so this scan can only look for the matter id —")
        print("  which almost no file contains. A 'clean' result here means very")
        print("  little. Run `plan` or `destroy` first so the tokens are recorded.")
    findings = []
    scanned = skipped = 0
    for p in sorted(work.rglob("*")):
        if not p.is_file():
            continue
        hit = next((t for t in toks if t in p.as_posix()), None)
        if hit:
            findings.append({"path": p.relative_to(work).as_posix(),
                             "trace": hit, "where": "filename"})
            continue
        if p.suffix.lower() in BINARY_SUFFIXES:
            # A binary we cannot read is NOT a clean result. Report it as unexamined.
            skipped += 1
            findings.append({"path": p.relative_to(work).as_posix(),
                             "trace": None, "where": "UNEXAMINED (binary)"})
            continue
        if p.stat().st_size > SCAN_MAX_BYTES:
            skipped += 1
            findings.append({"path": p.relative_to(work).as_posix(),
                             "trace": None, "where": "UNEXAMINED (too large)"})
            continue
        scanned += 1
        try:
            blob = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hit = next((t for t in toks if t in blob), None)
        if hit:
            findings.append({"path": p.relative_to(work).as_posix(),
                             "trace": hit, "where": "contents"})

    traces = [f for f in findings if f["trace"]]
    unexamined = [f for f in findings if not f["trace"]]
    print(f"\n  matter  : {matter}")
    print(f"  tokens  : {', '.join(toks)}")
    print(f"            ({len(cert_toks)} recovered from the destruction certificate, "
          f"{len(live_toks)} derived from what is still here)")
    print(f"  scanned : {scanned} file(s); {skipped} not examined\n")
    if traces:
        print(f"  TRACES REMAINING: {len(traces)}\n")
        for f in traces[:40]:
            print(f"    {f['where']:<22} {f['path']}  (matched {f['trace']!r})")
        if len(traces) > 40:
            print(f"    … and {len(traces) - 40} more")
    else:
        print("  no traces found by this scan.")
    if unexamined:
        print(f"\n  NOT EXAMINED: {len(unexamined)} file(s)\n")
        for f in unexamined[:15]:
            print(f"    {f['where']:<22} {f['path']}")
        print("\n  These are not a pass. A binary the scanner cannot read is a file you")
        print("  have not checked, and saying so is the difference between a report and")
        print("  a reassurance.")
    verdict = "TRACES REMAIN" if traces else (
        "no traces found; some files unexamined" if unexamined else "clean")
    out = work / f"destruction-verification-{matter}.json"
    out.write_text(json.dumps({
        "matter": matter, "at": now(), "tokens": toks,
        "tokens_from_certificate": cert_toks,
        "files_scanned": scanned, "files_not_examined": skipped,
        "traces": traces, "unexamined": unexamined, "verdict": verdict,
        "note": "This verification searches what remains. It does not consult the "
                "destruction list, because the list is written by someone who remembers "
                "and the pipeline keeps growing files nobody remembers.",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\n  verdict : {verdict}")
    print(f"  wrote   : {out}")
    return 1 if traces else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "destroy", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--work", default="../work")
        s.add_argument("--matter", default="SYNTHETIC-DEMO-01")
        if name == "destroy":
            s.add_argument("--confirm", default="",
                           help="type the matter id exactly, to confirm")
            s.add_argument("--by", default="", help="who authorizes this destruction")
            s.add_argument("--passes", type=int, default=1,
                           help="overwrite passes before unlink (0 to skip)")
            s.add_argument("--dry-run", action="store_true")
            s.add_argument("--list-only", action="store_true",
                           help="destroy only what the hand-written list names "
                                "(then run verify, and see what the list missed)")
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if args.cmd == "plan":
        return cmd_plan(work, args.matter)
    if args.cmd == "destroy":
        return cmd_destroy(work, args.matter, args.confirm, args.by, args.passes,
                           args.dry_run, args.list_only)
    if args.cmd == "verify":
        return cmd_verify(work, args.matter)
    return 2


if __name__ == "__main__":
    sys.exit(main())
