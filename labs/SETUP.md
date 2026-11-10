# Lab Setup

**You need Python 3.10+. That is the only hard requirement in this course.**

Everything else is optional and every gap has a fallback. No lab needs an API key. No lab
needs the network. If a lab ever asks you for either, that is a bug — tell the instructor.

```sh
cd labs
./verify-setup.sh                  # what you have, what you are missing, what that costs
python3 assets/make_corpus.py      # generate the corpus (~1,200 documents, ~30 s)
```

If `verify-setup.sh` says you can run every lab, stop reading and go to
[01-Ingestion](01-Ingestion/README.md). Come back here when something degrades.

---

## The three run modes

One environment variable picks the mode. Copy `.env.example` to `.env` to keep your
settings, or just export what you need.

| `LEGAL_AI_MODE` | What it means | What you need |
|---|---|---|
| `local` *(default)* | Local model behind an OpenAI-compatible endpoint | Ollama + two pulled models |
| `offline` | Deterministic stdlib fallbacks, no model at all | nothing |
| `cloud` | A hosted API — **the contrast case, used once** | `LEGAL_AI_API_KEY` |

`offline` is not a degraded teaching experience with pieces missing. Every planted finding
is still found, every guardrail still fires, every metric is still computed, every artifact
is still produced. What you lose is seeing a real model's output, and in Labs 03 and 05 that
is worth having. What the fallbacks give you instead is a reproducible number the whole room
shares, which is why the Teacher's Playbooks quote offline figures.

`cloud` exists for exactly one exercise: Lab 04's `compare`, where you run the same
questions against a hosted model and record the delta honestly, having first been warned on
screen that the document text is about to leave the machine. With no key set, `compare`
reports the local row only and says so — which is the right default for a legal course, and
means the lab is complete without a key. Everywhere else in this course cloud is the thing
you are defending against, not the happy path.

---

## Mode 1 — Local (recommended)

### Install Ollama

```sh
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama && brew services start ollama

# Windows: download the installer from ollama.com
```

### Pull two models

```sh
ollama pull qwen3:8b            # chat / RAG / extraction        ~5 GB
ollama pull nomic-embed-text    # embeddings, 768 dimensions     ~275 MB
```

With a 24 GB+ GPU or a 32 GB Mac, use `qwen3:14b` for the chat model instead — the
difference shows most in Lab 05's structured extraction, where the 8B model's JSON is
noticeably less reliable.

```sh
export LEGAL_AI_MODEL=qwen3:14b
```

### Check it

```sh
ollama list
curl -s http://localhost:11434/v1/models | python3 -m json.tool | head
```

The endpoint is **OpenAI-compatible**, which is the entire reason the labs can treat local
and cloud as the same code path with a different base URL. That substitutability is itself
the Module 5 argument: if swapping a hosted model for a local one is a one-line change, the
reason to stay local is legal, not technical.

> **The embedding dimension is part of your schema.** `nomic-embed-text` is 768-dimensional;
> `mxbai-embed-large` is 1024. You cannot mix them in one collection, and changing the
> embedder forces a full re-ingest. That is why the model is pinned in your manifest, and it
> is the gotcha Module 4 teaches on purpose.

---

## Mode 2 — Offline (nothing to install)

```sh
export LEGAL_AI_MODE=offline
```

`common/llm.py` then uses:

- a **deterministic hashing embedder** instead of a trained one. It has no idea that
  "indemnify" and "hold harmless" are related, so semantic retrieval gets visibly worse.
  The lab says so out loud rather than hiding it — that gap *is* the argument for a trained
  embedder.
- an **extractive answer stub** instead of a chat model. It quotes retrieved passages
  rather than reasoning over them. Citations still resolve, so every verifier exercise in
  Lab 03 works unchanged.
- a **keyword baseline** in Lab 05 instead of model calls, labelled as
  `keyword-baseline (no model available)` in the run record. Recall and elusion are still
  measured against blind ground truth; the numbers are just worse, and the metrics code
  cannot tell the difference. That is the point of measuring — and the keyword baseline is
  worth running even when you *do* have a model, because a classifier that cannot beat
  keyword search is not earning its place in a protocol.

Each fallback prints a one-line warning the first time it is used. Do not silence those
warnings. A system that quietly substitutes a worse component is the exact failure the
course is about.

---

## Mode 3 — Cloud (Lab 04 only)

```sh
export LEGAL_AI_MODE=cloud
export LEGAL_AI_API_KEY=sk-...
export LEGAL_AI_BASE_URL=https://api.anthropic.com/v1   # or your provider's
export LEGAL_AI_MODEL=claude-sonnet-5
```

Lab 04 is the only lab that uses this, it is clearly marked, and it is skippable. Without a
key you get the local row, a printed explanation of what the missing row would have told
you, and the full egress exercise — which is the part of the lab that matters.

**Use a throwaway key and never point cloud mode at a real matter.** Everything in
`assets/corpus/` is synthetic, so sending it anywhere is harmless. That will not be true of
the next corpus you work on.

---

## Optional extras

| Thing | Install | What you lose without it |
|---|---|---|
| **pypdf** | `pip install pypdf==5.1.0` | PDFs become exceptions in Lab 01. The lab still runs — and a non-empty exception list is its real lesson — but you miss the PDF path. |
| **Pillow** | `pip install Pillow==11.0.0` | `make_corpus.py` cannot render the synthetic scans, so the whole OCR thread in Labs 01–02 is missing, including the `indemnif1cation` finding. **Install this one.** |
| **requests** | `pip install requests==2.32.3` | No local model, no Tika. Labs fall back automatically. |
| **tesseract** | `apt install tesseract-ocr tesseract-ocr-eng` / `brew install tesseract` | `--reocr` does nothing, so you accept the producer's OCR. Lab 02's three-different-hit-counts exercise needs this. |
| **Docker** | [docs.docker.com](https://docs.docker.com/engine/install/) | Labs 06 and 10 Part 4 become read-the-compose-file exercises. Nothing downstream depends on it. |
| **Apache Tika** | `docker run -d -p 9998:9998 apache/tika:2.9.2.1` then `export TIKA_URL=http://localhost:9998` | Lab 01's built-in extractors handle the corpus fine. Tika is what you would use in production; the builtins exist so the lab never blocks on a JVM. |

Or in one go:

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-all.txt
```

A virtualenv is worth it here only because the labs pin versions. There is no package in
`requirements-all.txt` that will fight with your system Python.

---

## Generate the corpus

```sh
python3 assets/make_corpus.py                 # ~1,200 documents (the default)
python3 assets/make_corpus.py --docs 300      # faster; every lesson still lands
python3 assets/make_corpus.py --seed 12345    # a different synthetic matter
```

Reference outputs in the Teacher's Playbooks were measured on the **default** corpus
(~1,196 catalogued documents, seed `20261109`). If you change `--docs` or `--seed`, your
numbers will differ from the playbook's and that is fine — the *findings* are seeded to
survive both.

Three things about this corpus that matter:

1. **Every byte is synthetic.** No client, no custodian, no matter. This is a hard rule in
   this course and it should be a hard rule in your own training material.
2. **The mess is deliberate.** A zip inside a zip, a message attached to a message with an
   image-only scan inside *that*, three versions of one contract, a zero-byte file, a
   truncated OOXML, a password-protected archive, a cp1252 load file with a row that has no
   corresponding native, and a document containing a prompt-injection payload aimed at your
   own pipeline. If your Lab 01 run reports zero exceptions, your handler is swallowing
   errors.
3. **There is blind ground truth** in `assets/corpus/_groundtruth/`. Lab 05 scores against
   it. Do not read it before Lab 05 — you will have un-blinded your own validation, which is
   precisely the error the module exists to prevent.

---

## Directory layout

```text
labs/
  README.md             module ↔ lab map, the pipeline diagram
  SETUP.md              you are here
  .env.example          copy to .env
  verify-setup.sh       environment check
  test-all-labs.sh      smoke-test every lab, offline
  requirements-all.txt
  assets/
    make_corpus.py      the generator
    corpus/             generated — gitignored
  common/               llm.py, egress.py, metrics.py, bundle.py
  work/                 ALL lab output lands here — gitignored
  01-Ingestion/ … 11-Governance-Audit/
```

**Labs 01–06 are a pipeline.** Lab `NN` reads lab `NN-1`'s output from `work/`. Run them in
order the first time. Labs 08–11 (optional Day 3) each read `work/` but not each other, so
they can be done in any order.

If you fall behind, Lab 01 ships a complete worked answer (`ingest_reference.py`) and every
later lab in the chain ships code that already runs end to end — the exercises are edits and
extensions to working programs, not blank files. Nobody gets stranded at the start of Lab 03
because Lab 01 did not finish; run the reference and move on.

---

## Resetting

```sh
rm -rf work work-offline work-none work-glob      # start the pipeline over
rm -rf assets/corpus && python3 assets/make_corpus.py   # regenerate the corpus
```

Nothing under `work/` is precious; it is all derived. Nothing under `work/` is committed
either, and knowing which of your files are evidence and which are derived is itself a
defensibility signal — it is why `.gitignore` is on the capstone rubric.

---

## If something is wrong

```sh
./verify-setup.sh        # first
./test-all-labs.sh       # then this: smoke-tests every lab end to end, offline
```

`test-all-labs.sh` runs in `LEGAL_AI_MODE=offline`, builds a throwaway corpus and work
directory, and deletes them. It needs nothing installed beyond Python. If it is green and
your lab still fails, the difference is your environment, not the code — and the diff
between those two runs is where to look.

Per-lab problems are in each lab's **Troubleshooting** section. The three that come up most:

- **`corpus not found`** — you skipped `make_corpus.py`, or you are in the wrong directory.
  Lab paths like `--corpus ../assets/corpus` are relative to the lab folder.
- **`run <stage> first` / `no catalog`** — the pipeline is ordered. Labs 01–06 in sequence.
- **`[llm] chat endpoint unavailable`** — Ollama is not running (`ollama serve`). The lab
  continues on the offline stub and warns once.
