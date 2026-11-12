# Lab 11 — Deploy at Scale, and Destroy at the End

**Module 11 · modular series — swapped into Day 3 on request**

Two things happen to a legal-AI system that works: it gets pointed at a collection ten
times bigger, and eventually somebody asks you to delete the whole matter.

This lab builds both ends. The scaling half is deliberately unglamorous — a SQLite work
queue and N processes, which handles millions of documents on one large box and is far
easier to attest about than a cluster. The destruction half is the part students come back
and tell you about, because somebody asked them for it at work.

**Deliverables:** `throughput.json` with **your** explanation of where the curve flattens,
and a destruction certificate with its verification output.

---

## Setup

```bash
cd labs/11-Deploy-At-Scale
```

Nothing to install. Note the filename: `work_queue.py`, **not** `queue.py` — a module
called `queue.py` in the working directory shadows the standard library's `queue`, which
`multiprocessing` imports internally, and `mp.Pool()` then dies with
`ImportError: cannot import name 'Empty' from 'queue'`. That is a real bug that cost a real
afternoon while this lab was being written.

---

## Part 1 — Enumerate the work

```bash
python3 work_queue.py init --work ../work-scale --corpus ../assets/corpus
```

```
  config hash : a94e4dc44dab
  enumerated  : 1206 units
  inserted    : 1206 new  (0 already queued with this config)
  pending     : 1.2 MB of work
```

Run it again:

```
  inserted    : 0 new  (1206 already queued with this config)
```

Now change the configuration and run it a third time:

```bash
LEGAL_AI_OCR=other python3 work_queue.py init --work ../work-scale --corpus ../assets/corpus
```

```
  config hash : 26db849616aa
  inserted    : 1206 new  (0 already queued with this config)
```

Every unit comes back, because the idempotency key is `(matter, doc_id, stage,
config_hash)` and the config hash changed. Read `config_hash()`: everything that changes
the *output* belongs in there. Leave something out and a re-run silently reuses stale
results; put something irrelevant in — a timestamp, a hostname — and nothing is ever
reused. Both failures are expensive and only one of them is visible.

### The unit of work is the first scaling decision

Read `enqueue_mbox()` in `cmd_init`. If the unit were "one container," this corpus gives
**31 units** — so eight workers do nothing useful: one unpacks the big mbox while seven
idle. The unit has to be the *document*, so a mailbox is enumerated down to its messages
with byte offsets recorded, and the queue holds ~1,200 units instead of 31.

> Pick the unit wrong and no amount of workers helps. That is the first thing to check
> when somebody says "we scaled it out and it didn't get faster."

---

## Part 2 — Run workers, then kill one

```bash
python3 work_queue.py run --work ../work-scale --corpus ../assets/corpus --workers 4
```

```
  elapsed :   1.45s
  done    : 1195   exceptions: 10
  rate    : 830.0 units/s
```

Read `claim()`. Two decisions in eight lines:

**Lease, don't assign.** The row goes to `leased` with a `lease_until` timestamp. Nothing
is handed to a worker that cannot be taken back.

**Biggest first.** `ORDER BY bytes DESC` — longest-processing-time-first, a classic
scheduling result that genuinely matters here. One 50 GB container and ten thousand 100 KB
emails is the normal shape of legal data; claim small-first and the big one starts last,
runs alone, and sets your wall-clock single-handedly.

And note what does the locking: `UPDATE … WHERE id=? AND state='pending'`. Two workers
racing for the same row means one of them changes zero rows and takes the next one. No
lock service, no leader election, no broker.

### Now kill a worker while it holds a lease

```bash
python3 work_queue.py init --work ../work-scale --corpus ../assets/corpus
python3 work_queue.py run  --work ../work-scale --corpus ../assets/corpus --workers 4 --kill-one
```

```
      worker-1: done=2 exc=1  KILLED holding production/IMAGES/001/HOLL0000003.png
      worker-2: done=387 exc=1
      worker-3: done=397 exc=3
      worker-4: done=409 exc=5
```

`worker-1` exited without releasing anything. Check the queue:

```bash
python3 work_queue.py status --work ../work-scale
```

```
  state          units        MB
  ------------------------------
  done            1195       1.1
  exception         10       0.2
  leased             1       0.0

  current leases:
      worker-1: 1
```

One unit is stuck in `leased`, held by a process that no longer exists. Wait for the lease
to expire (60s) or force it, then:

```bash
python3 work_queue.py reap --work ../work-scale
```

```
  expired leases : 1
  requeued       : 1
  gave up        : 0  (attempts >= 3 -> exception)
```

Nothing was lost. **That is the entire argument for leases**, and it is the failure mode
an assignment-based queue loses work to silently.

Note the other half of `reap`: a unit that has expired `MAX_ATTEMPTS` times becomes an
**exception**, not a silent drop. It joins the exception list from Lab 02 and a human
decides. *"The pipeline retried it and gave up"* is not a disposition.

---

## Part 3 — The throughput curve

```bash
python3 work_queue.py curve --work ../work-scale --corpus ../assets/corpus --max-workers 16
```

```
  this machine reports 12 CPU(s)
  per-unit CPU cost: 1500 hash rounds (LAB10_WORK_ROUNDS; a labelled stand-in for
                     extraction + OCR)

   workers   elapsed   units/s   speedup  efficiency
  ----------------------------------------------------
         1      1.65     731.5      1.00        1.00
         2      1.33     908.7      1.24        0.62
         4      0.55    2184.7      2.99        0.75
         6      0.42    2844.2      3.89        0.65
         8      0.40    3040.6      4.16        0.52
        12      0.34    3588.9      4.91        0.41
        16      0.31    3845.8      5.26        0.33
```

Those are numbers from one 12-core laptop. **Yours will differ, and that is the point** —
the curve is a property of your machine, not of this code.

**About the per-unit cost, honestly:** decoding a 1 KB email takes microseconds, while real
extraction (Tika on a 40-page PDF, tesseract on a scanned page) takes 50 ms to several
seconds and is CPU-bound. With the microsecond version a throughput curve measures process
startup and teaches nothing. So each unit does a calibrated amount of real CPU work —
repeated BLAKE2b over the document bytes. It is a stand-in and it is labelled as one in the
output, but it is CPU-bound the same way extraction is, so what you measure is genuinely
your hardware. Set `LAB10_WORK_ROUNDS=0` and run the curve again to see the degenerate
version; that comparison is worth the thirty seconds.

### The deliverable is the explanation, not the curve

Efficiency here falls to 0.33 by 16 workers on a 12-core machine, and it is already
sagging at 2. Write down which bottleneck you think it is and what evidence supports it:

| candidate | what it looks like | how to check |
|---|---|---|
| core count | efficiency falls off a cliff past ~N cores | `nproc`, and the knee lands at N |
| one shared disk | flattens early and hard | `iostat -x 1` during a run |
| SQLite write contention | flattens early; retries climb | the `events` table; try `--workers 1` with 10× the work |
| memory bandwidth | flattens gradually, worst on OCR and embeddings | scales with per-unit data size, not unit count |

> A sizing estimate you cannot attribute to a bottleneck is a guess with a decimal point.
> Measure, attribute, then extrapolate — and say which stage you extrapolated from, because
> OCR and embedding scale differently and the client will quote whichever number is lower.

---

## Part 4 — Scale out in containers

Read `docker-compose.scale.yml`. Exactly two things differ from Lab 07:

1. `worker` is a scalable service — `--scale worker=6` — and **nothing coordinates them**.
2. `internal: true` is still there. Scaling out is precisely where a team adds a route to
   the internet "just for the model download" and never removes it.

```bash
docker compose -f docker-compose.scale.yml up --build --scale worker=6
docker compose -f docker-compose.scale.yml run --rm tools \
    /app/11-Deploy-At-Scale/work_queue.py status --work /work
```

Note there is no `depends_on: init` on the worker. A worker that starts before the queue is
populated finds nothing pending and exits; `restart: on-failure` brings it back. Designing
for *"the work might not be there yet"* is cheaper than orchestrating startup order — and
it is the same property that makes a worker safe to kill.

---

## Part 5 — Destroy the matter

Every engagement letter has a retention clause and every one of them comes due.

```bash
python3 destroy_matter.py plan --work ../work --matter SYNTHETIC-DEMO-01
```

The plan has two sections. The first is the hand-written list — extracted text, the index,
chunks, vectors, rendered prompts, decisions, the queue DB, the bundle, the production set.
Read the `why` on each one:

```
    0.03 MB  vectors.jsonl
             embeddings — a LOSSY copy, which is still a copy
    1.63 MB  case-snapshot-SYNTHETIC-DEMO-01
             the reproducibility bundle — a deliberate complete copy of the review
    0.00 MB  production/
             the production set — ALREADY SENT; destruction here does not recall it
```

The second section is the one that matters:

```
  FOUND BY SCANNING, NOT ON THE LIST (1, 0.0 MB)

        0.00 MB  bundle-path.txt
                 NOT ON THE LIST — contains 'SYNTHETIC-DEMO-01'
```

**You cannot destroy by list alone.** A list is written once, by someone who remembers; a
pipeline keeps growing files nobody remembers. So destruction scans, and verification does
not consult the list at all.

### Destroy by list only, on purpose, and watch it fail

```bash
python3 destroy_matter.py destroy --work ../work --matter SYNTHETIC-DEMO-01 \
    --confirm SYNTHETIC-DEMO-01 --by "A. Reviewer, Esq." --list-only
python3 destroy_matter.py verify --work ../work --matter SYNTHETIC-DEMO-01
```

```
  tokens  : SYNTHETIC-DEMO-01, aray, bsingh, counsel, jdoe, mchen
            (6 recovered from the destruction certificate, 1 derived from what is here)

  TRACES REMAINING: 1
    contents               bundle-path.txt  (matched 'SYNTHETIC-DEMO-01')

  verdict : TRACES REMAIN
```

Three details in that output are each worth a minute:

**The confirmation is the matter id, typed out.** There is no `--force`. A force flag
becomes muscle memory by the third time you use it; typing `SYNTHETIC-DEMO-01` does not.

**The tokens came from the certificate, not from the catalog.** Verification runs *after*
destruction, and the search terms — custodian names, Bates prefixes — were derived from the
catalog that destruction just deleted. Compute them after the deletion loop and you can
only search for the matter id, which almost no file contains, so a tree full of custodian
names reports **clean**. `cmd_destroy` derives the tokens *before* deleting and writes them
into the certificate. Order of operations is the control.

**The certificate lands outside the work directory.** It has to survive the destruction of
the thing it certifies, and `rm -rf work/` is how most of these end.

### Then do it properly

```bash
python3 destroy_matter.py destroy --work ../work --matter SYNTHETIC-DEMO-01 \
    --confirm SYNTHETIC-DEMO-01 --by "A. Reviewer, Esq."
python3 destroy_matter.py verify --work ../work --matter SYNTHETIC-DEMO-01
```

Now read `scope_and_limits` in the certificate. It says, in writing, that this covers one
work directory on one host; that it does **not** cover backups, snapshots or replicas; that
it does **not** recall a production set already delivered; that overwriting is defence in
depth and **not** a guarantee, because on SSDs with wear levelling and on copy-on-write
filesystems a logical overwrite may never reach the physical cells; and that an automated
inventory cannot prove completeness.

> A destruction certificate that does not say what it failed to cover is the kind of
> document that gets you in more trouble than having destroyed nothing at all.

And note what `verify` reports as `UNEXAMINED` — binaries it cannot read, files too large
to scan. Those are **not** a pass. A file you did not check is a file you did not check,
and saying so is the difference between a report and a reassurance.

---

## Exercises

1. **Find the real bottleneck.** Run the curve with `iostat -x 1` in another terminal.
   Then run it again with the corpus on a RAM disk. Which line moved?
2. **Break the lease.** Set `LEASE_SECONDS = 2` and run 8 workers. Units get reaped out
   from under live workers and processed twice. Why is that *safe* here, and what one
   property of `do_extract` makes it safe?
3. **Add a stage.** Extend the state machine with an `embed` stage that depends on
   `extract`. Where does the dependency live — in the queue, or in the config hash?
4. **Postgres.** Swap SQLite for Postgres without changing the state machine. Which
   single query has to change, and why does `claim()` get *simpler*?
5. **Beat the destruction scan.** Put a trace of the matter somewhere `verify` will miss
   it. Then fix `verify`. (Start with the binaries it reports as `UNEXAMINED`.)

---

## Review Questions

1. Why lease rather than assign? Name the failure mode assignment loses work to.
2. Your throughput flattened at 4 workers on a 16-core box. Give two candidate causes and
   the measurement that distinguishes them.
3. A client asks: "you deleted our data, right?" What are the four things your answer must
   mention?
4. Why does the destruction certificate record the verification tokens?
5. You destroyed the matter and `verify` says clean. What have you actually proven?

---

## Teacher's Playbook

### What good looks like

A student who gets this lab can say where their curve flattened **and why**, from their own
measurement, and can name three places matter data hides that a destruction list would
miss. The strongest tell is question 5: the honest answer is *"that a filename and
content scan over one work directory on one host found no traces of six search terms, with
N files unexamined"* — not *"the data is gone."*

### Live-demo script (about 15 minutes)

1. **The idempotency key** (3 min). `init`, `init`, then `LEGAL_AI_OCR=other init`. Three
   commands, and the third one re-enqueues everything. *"The hash is the difference
   between a cache and a correctness bug."*
2. **Kill a worker** (4 min). Run with `--kill-one`, then `status` — leave the `leased: 1`
   row on screen. *"That unit is held by a process that does not exist. In an
   assignment-based queue it is now lost, and nothing will ever tell you."* Then `reap`.
3. **The curve** (4 min). Run it live; it takes about 15 seconds. Put the efficiency column
   on the board and ask the room to vote on the bottleneck before you say anything. Then
   be explicit that the per-unit cost is a labelled stand-in — students will spot it in the
   source and you want to have said it first.
4. **Destruction** (4 min). This is the beat. Run `plan` and read the `why` lines aloud —
   especially *"embeddings — a LOSSY copy, which is still a copy."* Then `--list-only`
   destroy, then `verify` → **TRACES REMAIN**. *"That is your first destruction script, and
   it is everybody's first destruction script."* Close on `scope_and_limits`.

### The debrief the deck names

**"Where did your curve flatten, and why? And did `destroy_matter.py` miss anything on the
first try?"**

Almost everyone misses something on the first destruction run — usually the chunk JSONL,
the prompt logs, or the OCR sidecar files. **Collect the misses on the board.** That list
is the single most useful artifact from this module, and it is better than anything you
could have handed out, because the room produced it.

On the curve: either answer is fine if it is justified from their own measurement. Core
count and single-disk are both common and both correct on different laptops. What is not
acceptable is a number with no attributed cause.

### Common mistakes and fixes

| symptom | cause | fix |
|---|---|---|
| `ImportError: cannot import name 'Empty' from 'queue'` | a file named `queue.py` shadows the stdlib | it is `work_queue.py` for this reason; check for a stray `queue.py` |
| 31 units enumerated | the unit of work is the container | `enqueue_mbox` — the unit is the document |
| adding workers changes nothing | 31 units, or `LAB10_WORK_ROUNDS=0` | fix the unit, then re-measure |
| `database is locked` | no WAL, or no busy timeout | both are in `SCHEMA`; check it was applied |
| curve is pure noise | the baseline run is under a second | raise `LAB10_WORK_ROUNDS` |
| `reap` finds nothing after a kill | the lease has not expired yet | wait 60s, or force `lease_until` in SQL |
| `verify` says clean on a full tree | tokens derived after deletion | derive before; that is the bug the lab plants |
| destruction misses the bundle | it is a directory with a dated name | the `case-snapshot-*` glob |

### Further debrief

1. **"SQLite for a distributed queue? Really?"** Yes, for one box, and one box is the
   deployment shape for most on-prem legal work. N processes against a WAL-mode SQLite
   file handles millions of documents, and it is dramatically easier to attest about than
   a cluster: one file, one host, one thing to destroy. Move to Postgres when you need a
   second machine, and keep the same state machine. Students who expected Kubernetes should
   leave understanding that the boring answer is also the defensible one.

2. **"Why is processing a unit twice safe?"** Because `do_extract` checks whether its
   output already exists and returns early. Three lines. That property is what lets you
   lease aggressively, kill workers freely, and reap without thinking — and the moment a
   stage stops being idempotent, every other decision in this design becomes unsafe.

3. **"Is overwrite-before-unlink worth doing at all?"** It is defence in depth and a
   record of intent, and the certificate says exactly that rather than claiming more.
   Assured destruction on modern storage means full-disk encryption plus key destruction,
   or physical destruction. If a student wants to argue the passes are theatre, let them —
   then ask what they would write in the certificate instead.

4. **"The production set is on the destruction list but marked 'already sent'. Why keep
   it on the list?"** Because destroying your copy is still required, and because the line
   forces someone to notice that destruction does not recall a delivery. The legal
   follow-up — a clawback request, a certification from the receiving party — is a task
   this script cannot do, and naming it is how it gets assigned.

### Timing

90 minutes. Part 1 in 15, Part 2 in 20, Part 3 in 20, Part 4 in 10 (skip if Docker is
unavailable — nothing downstream depends on it), Part 5 in 20, debrief in 15. If you are
short, cut Part 4 and never Part 5.

---

**Next:** [Lab 12 — Governance Audit](../12-Governance-Audit/README.md)
