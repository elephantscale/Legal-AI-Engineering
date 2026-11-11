#!/usr/bin/env python3
"""work_queue.py — Lab 11: a work queue and N workers (Module 11).

    python3 work_queue.py init    --work ../work --corpus ../assets/corpus
    python3 work_queue.py run     --work ../work --workers 4
    python3 work_queue.py status  --work ../work
    python3 work_queue.py curve   --work ../work --max-workers 8
    python3 work_queue.py reap    --work ../work            # recover expired leases

Three decisions and the distributed-systems part is done:

  1. **Lease, don't assign.** A lease with a timeout means a dead worker's item is
     retried instead of lost. Assignment loses work silently; leases do not.
  2. **Idempotent by key** — (doc_id, stage, config_hash). A retried unit must be safe
     to run twice, because it WILL be run twice.
  3. **Natives read-only.** Forensic soundness enforced by the filesystem, not by
     everyone remembering.

SQLite is the queue. That is not a toy choice: N processes against one SQLite file in WAL
mode handles millions of documents on one large box, which is the actual deployment shape
for most on-prem legal work — and it is far easier to attest about than a cluster. Swap in
Postgres when you need more than one box, and keep this exact state machine.

    pending ──lease──▶ leased ──┬──▶ done
                          │     ├──▶ failed      (retryable; attempts < MAX_ATTEMPTS)
                          │     └──▶ exception   (terminal, and a FIRST-CLASS output)
                          └──expiry──▶ pending
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import sqlite3
import sys
import time
import zipfile
from pathlib import Path

# NOTE on the filename: this file is work_queue.py, not queue.py. A module named queue.py
# in the working directory shadows the standard library's `queue`, which `multiprocessing`
# imports internally — so `mp.Pool()` dies with
# `ImportError: cannot import name 'Empty' from 'queue'`. It is a real bug that cost a
# real afternoon. Python puts the script's directory first on sys.path; name your modules
# accordingly.

HERE = Path(__file__).resolve().parent
LEASE_SECONDS = 60
MAX_ATTEMPTS = 3
MATTER = "SYNTHETIC-DEMO-01"

SCHEMA = """
PRAGMA journal_mode=WAL;          -- concurrent readers with one writer: the whole reason
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=5000;         -- block instead of raising when another worker writes

CREATE TABLE IF NOT EXISTS work (
    id            INTEGER PRIMARY KEY,
    matter        TEXT NOT NULL,
    doc_id        TEXT NOT NULL,
    stage         TEXT NOT NULL,
    config_hash   TEXT NOT NULL,
    source        TEXT NOT NULL,     -- "archive.zip!inner/path" or a filesystem path
    bytes         INTEGER NOT NULL,
    state         TEXT NOT NULL DEFAULT 'pending',
    attempts      INTEGER NOT NULL DEFAULT 0,
    worker        TEXT,
    lease_until   REAL,
    started_at    REAL,
    finished_at   REAL,
    error         TEXT,
    -- The idempotency key. A retry of the same unit with the same config must not
    -- produce a second row, and a CONFIG CHANGE must produce a new one.
    UNIQUE (matter, doc_id, stage, config_hash)
);
CREATE INDEX IF NOT EXISTS ix_claim ON work (state, bytes DESC);
CREATE INDEX IF NOT EXISTS ix_lease ON work (state, lease_until);

CREATE TABLE IF NOT EXISTS events (
    at       REAL NOT NULL,
    worker   TEXT,
    work_id  INTEGER,
    event    TEXT NOT NULL,
    detail   TEXT
);
"""


def db(work: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(work / "queue.sqlite", timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def now() -> float:
    return time.time()


def event(conn: sqlite3.Connection, worker: str, work_id: int | None,
          ev: str, detail: str = "") -> None:
    conn.execute("INSERT INTO events (at, worker, work_id, event, detail) "
                 "VALUES (?,?,?,?,?)", (now(), worker, work_id, ev, detail))


def config_hash(stage: str) -> str:
    """What makes a unit of work distinct beyond its id.

    Everything that changes the OUTPUT belongs in here. Leave something out and a
    re-run silently reuses stale results; put something irrelevant in (a timestamp, a
    hostname) and nothing is ever reused. Both failures are expensive.
    """
    material = {
        "stage": stage,
        "ocr": os.environ.get("LEGAL_AI_OCR", "tesseract-default"),
        "extractor": os.environ.get("LEGAL_AI_EXTRACTOR", "builtin"),
        "model": os.environ.get("LEGAL_AI_MODEL", "qwen3:8b"),
        "embed": os.environ.get("LEGAL_AI_EMBED", "nomic-embed-text"),
    }
    return hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[:12]


# ------------------------------------------------------------------------------ init
def cmd_init(work: Path, corpus: Path, stage: str) -> int:
    work.mkdir(parents=True, exist_ok=True)
    conn = db(work)
    ch = config_hash(stage)
    units: list[tuple] = []

    # Enumerate the work WITHOUT doing any of it. Enumeration is cheap and must be
    # restartable; extraction is expensive and must be leased.
    #
    # Choosing the UNIT OF WORK is the first scaling decision and the easiest to get
    # wrong. "One container" gives you 31 units for this corpus, so eight workers do
    # nothing: one of them unpacks the big mbox for two minutes while seven idle. The
    # unit has to be the DOCUMENT. So a mailbox is enumerated down to its messages, and
    # the queue holds ~1,200 units instead of 31.
    def enqueue_mbox(label: str, data: bytes) -> None:
        """One unit per message. Offsets are recorded so a worker can seek straight to
        its own message rather than re-parsing the whole mailbox."""
        starts = []
        idx = 0
        while True:
            i = data.find(b"\nFrom ", idx) if idx else (
                0 if data.startswith(b"From ") else data.find(b"\nFrom "))
            if i < 0:
                break
            starts.append(i + 1 if idx or not data.startswith(b"From ") else 0)
            idx = i + 6
        if not starts:
            units.append((MATTER, label, stage, ch, label, len(data)))
            return
        bounds = starts + [len(data)]
        for n in range(len(starts)):
            size = bounds[n + 1] - bounds[n]
            units.append((MATTER, f"{label}#{n:05d}", stage, ch,
                          f"{label}#{n:05d}@{bounds[n]}:{size}", size))

    for p in sorted(corpus.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(corpus).as_posix()
        if p.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(p) as z:
                    for info in z.infolist():
                        if info.is_dir():
                            continue
                        label = f"{rel}!{info.filename}"
                        if info.filename.lower().endswith(".mbox"):
                            enqueue_mbox(label, z.read(info.filename))
                        else:
                            units.append((MATTER, label, stage, ch, label,
                                          info.file_size))
            except zipfile.BadZipFile:
                # A corrupt container is an EXCEPTION, not a crash and not a skip.
                units.append((MATTER, rel, stage, ch, rel, p.stat().st_size))
        elif p.suffix.lower() == ".mbox":
            enqueue_mbox(rel, p.read_bytes())
        else:
            units.append((MATTER, rel, stage, ch, rel, p.stat().st_size))

    conn.execute("BEGIN")
    before = conn.execute("SELECT COUNT(*) FROM work").fetchone()[0]
    conn.executemany(
        "INSERT OR IGNORE INTO work (matter, doc_id, stage, config_hash, source, bytes)"
        " VALUES (?,?,?,?,?,?)", units)
    conn.execute("COMMIT")
    after = conn.execute("SELECT COUNT(*) FROM work").fetchone()[0]
    total_bytes = conn.execute("SELECT SUM(bytes) FROM work WHERE state='pending'"
                               ).fetchone()[0] or 0
    event(conn, "init", None, "enqueued", f"{after - before} new units")

    print(f"\n  config hash : {ch}")
    print(f"  enumerated  : {len(units)} units")
    print(f"  inserted    : {after - before} new  ({len(units) - (after - before)} "
          f"already queued with this config)")
    print(f"  pending     : {total_bytes / 1e6:.1f} MB of work")
    print(f"\n  Run init again — it inserts 0. That is the idempotency key doing its")
    print(f"  job. Now change one thing (LEGAL_AI_OCR=other) and run it again: every")
    print(f"  unit comes back, because the config hash changed and the old results no")
    print(f"  longer describe what you would produce today.")
    return 0


# ----------------------------------------------------------------------------- claim
def claim(conn: sqlite3.Connection, worker: str) -> sqlite3.Row | None:
    """Atomically take the largest pending unit and lease it.

    LONGEST-PROCESSING-TIME-FIRST: biggest first. A classic scheduling result, and it
    genuinely matters here — one 50 GB container and ten thousand 100 KB emails is the
    normal shape of legal data. Claim small-first and the big one starts last, runs
    alone, and sets your wall-clock single-handedly.

    The UPDATE … WHERE state='pending' is the lock. Two workers racing for the same row
    means one of them changes 0 rows and tries again. No external lock service, no
    leader election.
    """
    while True:
        row = conn.execute(
            "SELECT * FROM work WHERE state='pending' "
            "ORDER BY bytes DESC, id ASC LIMIT 1").fetchone()
        if row is None:
            return None
        cur = conn.execute(
            "UPDATE work SET state='leased', worker=?, lease_until=?, started_at=?, "
            "attempts=attempts+1 WHERE id=? AND state='pending'",
            (worker, now() + LEASE_SECONDS, now(), row["id"]))
        if cur.rowcount == 1:
            return conn.execute("SELECT * FROM work WHERE id=?",
                                (row["id"],)).fetchone()
        # lost the race; loop and take the next one


def finish(conn: sqlite3.Connection, work_id: int, state: str,
           error: str = "") -> None:
    conn.execute("UPDATE work SET state=?, finished_at=?, error=?, lease_until=NULL "
                 "WHERE id=?", (state, now(), error or None, work_id))


def cmd_reap(work: Path, verbose: bool = True) -> int:
    """Return expired leases to pending. This is the whole payoff of leasing."""
    conn = db(work)
    expired = conn.execute(
        "SELECT id, doc_id, worker, attempts FROM work "
        "WHERE state='leased' AND lease_until < ?", (now(),)).fetchall()
    recovered, dead = 0, 0
    for r in expired:
        if r["attempts"] >= MAX_ATTEMPTS:
            finish(conn, r["id"], "exception",
                   f"lease expired {r['attempts']} times; last worker {r['worker']}")
            event(conn, "reaper", r["id"], "gave_up", r["doc_id"])
            dead += 1
        else:
            conn.execute("UPDATE work SET state='pending', worker=NULL, "
                         "lease_until=NULL WHERE id=?", (r["id"],))
            event(conn, "reaper", r["id"], "requeued", r["doc_id"])
            recovered += 1
    if verbose:
        print(f"\n  expired leases : {len(expired)}")
        print(f"  requeued       : {recovered}")
        print(f"  gave up        : {dead}  (attempts >= {MAX_ATTEMPTS} -> exception)")
        if dead:
            print("\n  A unit that failed MAX_ATTEMPTS times becomes an exception, not a")
            print("  silent drop. It joins the exception list from Lab 02 and a human")
            print("  decides. 'The pipeline retried it and gave up' is not a disposition.")
    return 0


# ---------------------------------------------------------------------------- worker
# How much CPU one unit of work costs. Decoding a 1 KB email takes microseconds; real
# extraction (Tika on a 40-page PDF, tesseract on a scanned page) takes 50 ms to several
# seconds and is CPU-bound. With the microsecond version, a throughput curve measures
# process startup and teaches nothing.
#
# So each unit does a calibrated amount of real CPU work: repeated BLAKE2b over the
# document bytes. This is a STAND-IN and it is labelled as one — but it is CPU-bound in
# the same way extraction is, so the curve you measure is a genuine property of YOUR
# machine (cores, memory bandwidth, SQLite contention) rather than of the toy payload.
# Set it to 0 to see the degenerate curve for yourself; that comparison is worth doing.
EXTRACT_WORK_ROUNDS = int(os.environ.get("LAB10_WORK_ROUNDS", "1500"))


def simulated_extraction_cost(data: bytes) -> None:
    h = hashlib.blake2b(data, digest_size=32)
    for _ in range(EXTRACT_WORK_ROUNDS):
        h = hashlib.blake2b(h.digest() + data[:512], digest_size=32)


def do_extract(corpus: Path, work: Path, source: str) -> tuple[str, int]:
    """The actual unit of work: extract text for one item. Deliberately real enough to
    have a realistic cost profile, and deliberately NOT the ingester — Lab 02 owns that.

    Returns (state, chars). Raises nothing: a failure is a return value here, because a
    worker that raises loses the lease information it was holding.
    """
    out_dir = work / "text-scaled"
    out_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(source.encode()).hexdigest()[:16]
    dest = out_dir / f"{key}.txt"

    # IDEMPOTENT: if the output already exists for this key, the unit is done. This is
    # what makes a retry safe, and it is three lines.
    if dest.exists():
        return "done", len(dest.read_text(encoding="utf-8", errors="replace"))

    # "collection.zip!custodian_aray/mail.mbox#00003@12345:678" -> one message
    span = None
    if "#" in source and "@" in source.rsplit("#", 1)[-1]:
        source, tail = source.rsplit("#", 1)
        _n, _, where = tail.partition("@")
        off, _, size = where.partition(":")
        span = (int(off), int(size))
    try:
        if "!" in source:
            arch, inner = source.split("!", 1)
            with zipfile.ZipFile(corpus / arch) as z:
                data = z.read(inner)
        else:
            data = (corpus / source).read_bytes()
    except (OSError, zipfile.BadZipFile, KeyError, RuntimeError):
        return "exception", 0
    if span:
        data = data[span[0]:span[0] + span[1]]

    if not data:
        return "exception", 0
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("cp1252")
        except UnicodeDecodeError:
            return "exception", 0
    if not text.strip():
        return "exception", 0
    simulated_extraction_cost(data)        # the CPU cost extraction would really have
    dest.write_text(text, encoding="utf-8")
    return "done", len(text)


def worker_loop(work: Path, corpus: Path, worker: str, deadline: float,
                die_after: int = 0) -> dict:
    conn = db(work)
    stats = {"worker": worker, "done": 0, "exception": 0, "failed": 0, "chars": 0}
    event(conn, worker, None, "worker_start")
    n = 0
    while now() < deadline:
        row = claim(conn, worker)
        if row is None:
            break
        n += 1
        if die_after and n > die_after:
            # Simulate a hard kill: exit WITHOUT releasing the lease. The reaper has to
            # notice. This is the failure mode that assignment-based queues lose work to.
            event(conn, worker, row["id"], "killed_holding_lease", row["doc_id"])
            stats["killed_holding"] = row["doc_id"]
            return stats
        state, chars = do_extract(corpus, work, row["source"])
        finish(conn, row["id"], state,
               "" if state == "done" else "no extractable text")
        stats[state] = stats.get(state, 0) + 1
        stats["chars"] += chars
    event(conn, worker, None, "worker_stop", json.dumps(stats))
    return stats


def _worker_entry(args) -> dict:
    work, corpus, worker, deadline, die_after = args
    return worker_loop(Path(work), Path(corpus), worker, deadline, die_after)


def cmd_run(work: Path, corpus: Path, workers: int, timeout: float,
            kill_one: bool, quiet: bool = False) -> tuple[float, dict]:
    conn = db(work)
    pending = conn.execute("SELECT COUNT(*) FROM work WHERE state='pending'"
                           ).fetchone()[0]
    if not quiet:
        print(f"\n  workers : {workers}")
        print(f"  pending : {pending} units")
        if kill_one:
            print(f"  NOTE    : worker-1 will be killed while HOLDING A LEASE")
    deadline = now() + timeout
    jobs = [(str(work), str(corpus), f"worker-{i + 1}", deadline,
             3 if (kill_one and i == 0) else 0) for i in range(workers)]
    t0 = now()
    if workers == 1:
        results = [_worker_entry(jobs[0])]
    else:
        with mp.Pool(workers) as pool:
            results = pool.map(_worker_entry, jobs)
    elapsed = now() - t0

    agg = {"done": 0, "exception": 0, "chars": 0}
    for r in results:
        for k in ("done", "exception", "chars"):
            agg[k] += r.get(k, 0)
    agg["elapsed"] = elapsed
    agg["units"] = agg["done"] + agg["exception"]
    agg["rate"] = agg["units"] / elapsed if elapsed else 0.0
    if not quiet:
        print(f"\n  elapsed : {elapsed:6.2f}s")
        print(f"  done    : {agg['done']}   exceptions: {agg['exception']}")
        print(f"  rate    : {agg['rate']:.1f} units/s")
        for r in results:
            extra = f"  KILLED holding {r['killed_holding']}" \
                if r.get("killed_holding") else ""
            print(f"      {r['worker']}: done={r.get('done', 0)} "
                  f"exc={r.get('exception', 0)}{extra}")
        if kill_one:
            print("\n  worker-1 exited without releasing its lease. Check the queue:")
            print("      python3 work_queue.py status --work ... | grep leased")
            print("  then recover it:")
            print("      python3 work_queue.py reap --work ...")
            print("\n  Nothing was lost. That is the entire argument for leases.")
    return elapsed, agg


# ---------------------------------------------------------------------------- status
def cmd_status(work: Path) -> int:
    conn = db(work)
    print()
    rows = conn.execute("SELECT state, COUNT(*) n, SUM(bytes) b FROM work "
                        "GROUP BY state ORDER BY n DESC").fetchall()
    print(f"  {'state':<12}{'units':>8}{'MB':>10}")
    print("  " + "-" * 30)
    for r in rows:
        print(f"  {r['state']:<12}{r['n']:>8}{(r['b'] or 0) / 1e6:>10.1f}")
    stale = conn.execute("SELECT COUNT(*) FROM work WHERE state='leased' "
                         "AND lease_until < ?", (now(),)).fetchone()[0]
    held = conn.execute("SELECT worker, COUNT(*) n FROM work WHERE state='leased' "
                        "GROUP BY worker").fetchall()
    if held:
        print(f"\n  current leases:")
        for h in held:
            print(f"      {h['worker']}: {h['n']}")
    if stale:
        print(f"\n  {stale} lease(s) EXPIRED — run `reap` to requeue them")
    exc = conn.execute("SELECT doc_id, attempts, error FROM work "
                       "WHERE state='exception' LIMIT 5").fetchall()
    if exc:
        print(f"\n  exceptions (first 5):")
        for e in exc:
            print(f"      {e['doc_id'][:64]}  attempts={e['attempts']}  {e['error']}")
    return 0


# ----------------------------------------------------------------------------- curve
def cmd_curve(work: Path, corpus: Path, max_workers: int) -> int:
    """Measure throughput against worker count. Then explain where it flattens."""
    cores = os.cpu_count() or 1
    print(f"\n  this machine reports {cores} CPU(s)")
    print(f"  per-unit CPU cost: {EXTRACT_WORK_ROUNDS} hash rounds "
          f"(LAB10_WORK_ROUNDS; a labelled stand-in for extraction + OCR)\n")
    print(f"  {'workers':>8}{'elapsed':>10}{'units/s':>10}{'speedup':>10}"
          f"{'efficiency':>12}")
    print("  " + "-" * 52)
    base = None
    rows = []
    counts = [n for n in (1, 2, 4, 6, 8, 12, 16) if n <= max_workers]
    for n in counts:
        conn = db(work)
        # Reset to pending so each measurement does the SAME work. Note we do not delete
        # the extracted text: the units are idempotent, so a repeat run is fast. That is
        # realistic for a re-run and useless for a benchmark, so we clear the output too.
        conn.execute("UPDATE work SET state='pending', worker=NULL, lease_until=NULL, "
                     "attempts=0, finished_at=NULL, error=NULL")
        for f in (work / "text-scaled").glob("*.txt"):
            f.unlink()
        conn.close()
        elapsed, agg = cmd_run(work, corpus, n, timeout=600, kill_one=False, quiet=True)
        base = base or elapsed
        speed = base / elapsed if elapsed else 0
        rows.append({"workers": n, "elapsed": round(elapsed, 2),
                     "rate": round(agg["rate"], 1), "speedup": round(speed, 2),
                     "efficiency": round(speed / n, 2), "units": agg["units"]})
        print(f"  {n:>8}{elapsed:>10.2f}{agg['rate']:>10.1f}{speed:>10.2f}"
              f"{speed / n:>12.2f}")
    (work / "throughput.json").write_text(json.dumps({
        "cores_reported": cores, "measurements": rows,
        "units": rows[0]["units"] if rows else 0,
        "note": "Efficiency is speedup/workers. It falls below ~0.7 at the point where "
                "adding workers stops paying. WHY it falls there is the question: core "
                "count, one shared disk, SQLite write contention, or memory bandwidth. "
                "Say which, from your own numbers.",
    }, indent=2) + "\n")
    print(f"\n  wrote {work / 'throughput.json'}")
    print("\n  Now answer the only question that matters: WHERE did it flatten, and WHY?")
    print("  Candidates, in the order they usually bite:")
    print("    - core count            (efficiency falls off a cliff past ~N cores)")
    print("    - one shared disk       (flattens early, and iostat shows it)")
    print("    - SQLite write contention (flattens early, and `events` shows retries)")
    print("    - memory bandwidth      (flattens gradually, OCR and embeddings)")
    print("\n  A sizing estimate you cannot attribute to a bottleneck is a guess with")
    print("  a decimal point. Measure, attribute, then extrapolate — and say which")
    print("  stage you extrapolated from.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "run", "status", "curve", "reap"):
        s = sub.add_parser(name)
        s.add_argument("--work", default="../work")
        if name in ("init", "run", "curve"):
            s.add_argument("--corpus", default="../assets/corpus")
        if name == "init":
            s.add_argument("--stage", default="extract")
        if name == "run":
            s.add_argument("--workers", type=int, default=4)
            s.add_argument("--timeout", type=float, default=600)
            s.add_argument("--kill-one", action="store_true",
                           help="kill worker-1 while it holds a lease")
        if name == "curve":
            s.add_argument("--max-workers", type=int, default=8)
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if args.cmd == "init":
        return cmd_init(work, Path(args.corpus).resolve(), args.stage)
    if args.cmd == "run":
        cmd_run(work, Path(args.corpus).resolve(), args.workers, args.timeout,
                args.kill_one)
        return 0
    if args.cmd == "status":
        return cmd_status(work)
    if args.cmd == "curve":
        return cmd_curve(work, Path(args.corpus).resolve(), args.max_workers)
    if args.cmd == "reap":
        return cmd_reap(work)
    return 2


if __name__ == "__main__":
    sys.exit(main())
