# Lab 02 — Ingestion: Build the Pipeline

**Module:** 2 — Legal Data Is Messy
**Duration:** 60–75 minutes
**Difficulty:** Intermediate

---

## Goal

Build the ingestion pipeline the rest of the course reads. You will walk a recursive
container tree, extract text by type, OCR the image-only scans, hash the natives, apply a
**documented** dedupe policy, group near-duplicates, reconcile the producer's load file,
and emit a catalog plus an **exception list you would be willing to hand to opposing
counsel**.

Nobody demos ingestion. Every legal-AI project dies there.

## Files in this lab

```
02-Ingestion/
  README.md             <- you are here
  requirements.txt      <- optional; the starter runs on the stdlib alone
  ingest.py             <- the starter: a complete walker with FOUR TODOs
  ingest_reference.py   <- the worked answer. Read yours first.
```

## Prerequisites

- Python 3.11+
- `tesseract` on your PATH for the OCR step (see `requirements.txt` for the one-liner).
  No tesseract? The lab still completes — you accept the producer's OCR instead, which is
  itself a realistic and instructive choice.

## Steps

### 1. Generate the corpus

```sh
cd labs/assets
python3 make_corpus.py                # ~1200 documents
# or, for a faster lab:
python3 make_corpus.py --docs 300
```

Watch the summary it prints. Note the richness figure — you will need it in Lab 06.

Everything it writes is synthetic. **No client data in any lab, ever.**

### 2. Look at the mess before you write code

```sh
cd ../02-Ingestion
unzip -l ../assets/corpus/collection.zip | head -30
xxd ../assets/corpus/production/VOL001.dat | head -3      # note \x14 and \xfe
cat ../assets/corpus/production/VOL001.opt
ls ../assets/corpus/exceptions_src/
```

Five minutes here saves you thirty later. Find, by eye:

- the zip inside the zip
- a message attached to a message, with an image-only scan inside *that*
- three versions of the same contract
- the `.ocr.txt` sidecars — the producer's OCR output, which is all the text you have for
  the scans unless you re-OCR them yourself

### 3. Run the starter and read the output

```sh
python3 ingest.py --corpus ../assets/corpus --out ../work
```

It already walks the tree correctly, which is the part people get wrong. Then:

```sh
head -1 ../work/catalog.jsonl | python3 -m json.tool
cat ../work/exceptions.jsonl | python3 -m json.tool
cat ../work/manifest.json | python3 -m json.tool
```

### 4. Read `ingest.py` top to bottom

Find these, because they are the design and not the detail:

- `handle()` — the dispatcher. Containers **recurse**; they are not documents.
- `_own_parts()` — and the comment explaining why `msg.walk()` is the wrong tool. An
  attachment of an attached message belongs to the inner message's family.
- `message_metadata()` — UTC **and** the original offset, stored separately.
- `emit()` — where a document with no text becomes an **exception** instead of a
  silently-empty row.
- The three forensic rules in the module docstring, and where each one is enforced.

### 5. Implement the four TODOs

| TODO | Method | What it is really about |
|---|---|---|
| **1** | `ocr_image` | OCR locally. A cloud OCR API leaks the raw page one step before your "private" LLM. |
| **2** | `apply_dedupe` | Dedupe is a **documented legal decision**, not data cleaning. Possession is evidence. |
| **3** | `group_near_duplicates` | **Group**, never suppress. The 6% difference is the finding. |
| **4** | `reconcile_load_file` | A row in the load file with no native is a **collection lead**. |

Each docstring tells you what to build and what to return. Work in order.

### 6. Compare dedupe policies and explain the difference

```sh
python3 ingest.py --corpus ../assets/corpus --out ../work-none  --dedupe none
python3 ingest.py --corpus ../assets/corpus --out ../work-glob  --dedupe global
python3 ingest.py --corpus ../assets/corpus --out ../work       --dedupe per-custodian
grep -c . ../work-none/catalog.jsonl ../work-glob/catalog.jsonl ../work/catalog.jsonl
```

Your document count changes. Be able to say **why**, and which number you would put in a
declaration.

### 7. OCR, both ways

```sh
python3 ingest.py --corpus ../assets/corpus --out ../work --reocr
```

Compare the extracted text for `scan_0042.png` against the producer's `.ocr.txt` sidecar.
They differ. Decide which one you would index, and write down why.

### 8. Tune the near-duplicate threshold

```sh
python3 ingest.py --corpus ../assets/corpus --out ../work --nd-threshold 0.80
python3 ingest.py --corpus ../assets/corpus --out ../work --nd-threshold 0.60
```

Then check whether `MSA_EXECUTED.txt` lands in the same group as its own drafts. This is
the most important thirty seconds of the lab — see the Playbook.

## Deliverable

1. `../work/catalog.jsonl` — one row per document, hashed, with family and custodian
2. `../work/exceptions.jsonl` — **non-empty**, triaged, with a next step on every row
3. `../work/manifest.json` — the policies you chose, including the dedupe policy and
   whether you re-OCR'd
4. One sentence, written down: *"We processed N documents. M did not process, for these
   reasons."*

Labs 03–08 all read `../work/catalog.jsonl`. If you are short on time, run
`ingest_reference.py` and move on — nobody gets stranded.

## Troubleshooting

- **`corpus not found`** — you skipped step 1, or you are in the wrong directory. The
  default `--corpus ../assets/corpus` is relative to this lab folder.
- **Zero exceptions** — your pipeline is lying to you. The shipped corpus contains a
  zero-byte file, a truncated OOXML, and a password-protected zip. If none of them
  surfaced, your handler is swallowing errors.
- **OCR returns nothing** — is `tesseract` on your PATH? `tesseract --version`. Without
  it the scans stay as exceptions unless you accept the producer sidecar.
- **The same document appears many times** — you are seeing families. An email and its
  attachments are separate documents with a shared `family_id`. That is correct.
- **`UnicodeDecodeError`** — some legal text genuinely is not UTF-8. Decode with a
  fallback and **log the problem on the document**; do not drop it.
- **Near-dupe grouping is slow** — the reference is O(n²) on purpose because it is
  readable. At production scale you band the sketches (LSH). Use `--docs 300`.

## Review Questions

1. You ran a global dedupe and produced 287 documents. Opposing counsel asks how many
   custodians possessed the executed contract. What do you say?
2. Your pipeline reports "1,284,112 documents processed." What is the second number you
   must report alongside it, and why?
3. The producer's OCR sidecar says `indemnif1cation`. Your own tesseract run says
   `indemnification`. Which goes in the index, and what do you disclose?
4. Why must OCR be local if the LLM is local?
5. An email has an attachment that is itself an email with an attachment. How many
   documents is that, and what links them?

---

## Teacher's Playbook

### Worked model answer

Run `ingest_reference.py` with `--reocr`. On the default corpus you should see
approximately:

```
ingested   : 1198 documents
exceptions : 3  <- look at these
dedupe     : per-custodian  unique=1196 duplicate=2
near-dupes : 20 group(s)
ocr        : re-OCR locally (engine: tesseract-5.3.4)
load file  : 4 rows, 3 matched, 1 missing

  !! 1 row(s) are listed in the producer's load file with no corresponding native in the
     collection. Report this to counsel: these documents exist and were not produced to
     you. (/NATIVE/001/side_letter.pdf)
```

Without `--reocr` it is 1196 documents and 5 exceptions — the two in-email scans stay
unresolved because the producer's sidecars only exist for the `scans/` folder. That delta
of two documents is the whole OCR lesson in one number.

### Live-demo script (about 12 minutes)

1. `python3 make_corpus.py` on the projector. Let the mess appear. (`--docs 300` if you
   want it to finish faster; every teaching moment below survives the smaller corpus.)
2. `xxd ../assets/corpus/production/VOL001.dat | head -3` — point at `\x14` and `\xfe`.
   *"This is how the legal industry moves data. In 2026."* Reliable laugh, real point.
3. Run the starter. Show `exceptions.jsonl`. *"Five documents did not process. A vendor
   would have reported a clean total of 1,196. What would you report?"*
4. Run with `--dedupe global` vs `--dedupe per-custodian` side by side. Put both document
   counts on the board. *"Which number is true?"* Both are. That is the point.
5. **The threshold demo.** Run `--nd-threshold 0.80`, then `0.60`, and grep the near-dupe
   group for the three MSA files:
   ```sh
   python3 -c "import json;[print(r['dedupe']['near_dupe_group'], r['source_path'])
     for r in map(json.loads, open('../work/catalog.jsonl')) if 'Contracts/MSA' in r['source_path']]"
   ```
   At **0.80** the executed version sits in a *different* group from its own drafts. At
   **0.60** they group together. Their actual measured similarity is **0.651** — because
   the executed version is the one with §7.3 deleted.
   Say it plainly: *"A vendor default of 0.80 would have put the executed contract in a
   different group from its drafts, nobody would have diffed them, and the removed
   indemnification cap would never have been found. Your threshold is a litigation
   decision."* This is the single best moment in the lab.

### Common mistakes + fixes

- **Using `msg.walk()` for attachments.** It descends into `message/rfc822`, so a nested
  message's attachments get attributed to the outer message too — double-counted and in
  the wrong family. The starter already has `_own_parts()`; make them read the comment.
- **Dropping unparseable files.** The instinct is `try/except: continue`. Insist every
  failure becomes an exception row with a *next step*. "Log it" is not enough; a human
  has to know what to do.
- **Deduping aggressively because it is "free accuracy."** Possession is evidence. Six
  custodians holding the same memo may be more probative than the memo.
- **Suppressing near-duplicates instead of grouping them.** Catch this early; it is the
  error that loses findings.
- **Normalizing timestamps to local time.** Then "did he know before the 3pm call?" is
  unanswerable. UTC plus the original offset, stored separately.
- **Forgetting `extracted_by`.** It is part of the reproducibility story in Module 6. An
  OCR engine version change is a pipeline change.

### Debrief Q&A

- *Why not just use Tika for everything?* In production you should, and the starter has a
  `--tika-url` path. The builtin extractors exist so the lab never blocks on a JVM.
- *Why JSONL instead of a database?* So students can `grep` their own pipeline's output.
  Append-only JSONL is also the honest shape for an audit trail.
- *Who decides the dedupe policy?* Counsel, in the protocol. The engineer's job is to
  implement it faithfully and record which one ran.
- *Is the load-file reconciliation really our job?* Yes, and it is a quiet source of
  professional credibility. Nobody else checks.
- *What about PST?* `readpst` / libpff in production. We ship mbox because it needs no
  native dependency and teaches the identical recursion.

### What good looks like

A student can point at any line of `handle()` and say whether it is handling a container
or a document; has a **non-empty** exception list where every row has a next step; can
state their dedupe policy and defend it; found the missing `side_letter.pdf` in the load
file; and can explain why their near-duplicate threshold determines whether they would
have caught the deleted indemnification cap.

---
