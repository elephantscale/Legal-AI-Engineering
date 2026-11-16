# Module 11 — Deployment at Scale

Elective — booked on its own, or added to the Deep Dive

Elephant Scale

---

## The Shape of the Problem

A real matter: **two terabytes, four million documents, six weeks.**

* The AI layer is not your bottleneck. **Extraction and OCR** are.
* Nothing may leave the building, so "scale out to a cloud queue" is off the table
* The customer's hardware is what it is, and you will be asked to size it before you have
  seen the data

> Scale in legal processing is an **embarrassingly parallel** problem wearing a compliance
> costume.

Notes:

Open with the reassurance: the hard part is not distributed-systems theory, it is doing a
simple parallel pattern without violating forensic rules or losing the audit trail. That is
good news for the room.

---

## Where the Time Actually Goes

| Stage | Bound by | Scales with | Rough shape |
|---|---|---|---|
| **Container expansion** (zip/PST) | single-threaded I/O | **not** easily | the long pole; start it first |
| **Text extraction** (Tika) | CPU | cores | ~50–200 docs/sec/core, wildly format-dependent |
| **OCR** | CPU (or GPU) | cores | **~1–5 pages/sec/core** — the real bottleneck |
| **Indexing** | I/O + CPU | shards | commit batching matters enormously |
| **Embeddings** | GPU | GPU | one-time per corpus per embedding model |
| **LLM classification** | GPU | batching | vLLM, not Ollama |

* **OCR dominates.** Ten percent of a corpus as scanned paper can be 80% of your wall clock.
* **PST expansion is the serialization point.** One 50 GB PST is one slow worker. Split by
  folder where you can, and start the big ones first.

> Profile before you parallelize. In this pipeline the answer is almost always OCR, and the
> second answer is almost always one enormous PST.

Notes:

The "start the big ones first" scheduling point is worth its own sentence: longest-processing-
time-first scheduling on a work queue is a classic result and it genuinely matters when one
container is 50 GB and ten thousand are 100 KB.

---

## The Work-Queue Pattern

```text
            ┌──────────────┐
            │  work queue  │   one row per unit of work, with a state machine
            │  (SQLite /   │   pending -> leased -> done | failed | exception
            │   Postgres / │
            │   Redis)     │
            └──────┬───────┘
      ┌────────────┼────────────┬────────────┐
      ▼            ▼            ▼            ▼
  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
  │worker 1│  │worker 2│  │worker 3│  │worker N│   stateless, idempotent, restartable
  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
      └───────────┴───────────┴───────────┘
                      ▼
        shared storage: natives (ro) · text · index · logs (append-only)
```

* **Lease, don't assign.** A lease with a timeout means a dead worker's item is retried
  rather than lost.
* **Idempotent by key** — `(doc_id, stage, config_hash)`. A retried unit must be safe.
* **Workers are stateless.** All state is in the queue and on disk.
* **Natives mounted read-only.** Forensic soundness, enforced by the filesystem rather than
  by discipline.

> Lease with timeout, idempotent by key, natives read-only. Three decisions and the
> distributed-systems part is done.

Notes:

Keep this deliberately unglamorous. Students sometimes expect Spark or Kubernetes. A SQLite
work queue and N processes handles millions of documents on one large box, which is the
actual deployment shape for most on-prem legal work — and it is far easier to attest about.

FreeEed's scale-out work ("Piranha") is this pattern; mention it if asked.

---

## Scaling the AI Layer

* **Embeddings** — one-time cost per corpus **per embedding model.** Batch them; use the GPU;
  and remember: changing the model forces a full re-ingest (Module 4).
* **Classification at volume** — this is a **throughput** problem, so **vLLM**, not Ollama:
  continuous batching, paged attention, concurrent requests
* **Right-size the model to the task.** Responsiveness coding is a bounded classification;
  a 14B model at temp 0 with a good prompt will usually do it. Don't buy 70B inference for
  a yes/no.
* **Two-stage cascade** — cheap model screens, expensive model adjudicates the uncertain band
  - typically 70–85% of documents never need the big model
  - **but**: two models means two pins and two validation passes in the bundle. Document both.

> The cascade is the biggest cost lever in legal AI, and it is also an extra thing to
> document. Make the trade on purpose.

Notes:

The cascade is genuinely how you make a four-million-document review economic, and the
documentation caveat is the kind of detail that marks someone who has shipped one. Both
models, both hashes, both validation passes, and the band boundary — in the manifest.

---

## Hardware Sizing: An Honest Method

Don't guess. **Measure a sample and extrapolate.**

```text
1. Take a random 1,000-document sample of the actual corpus
2. Run the full pipeline on one box. Record per-stage wall clock.
3. Compute: docs/hour/core (extraction), pages/hour/core (OCR),
            docs/hour/GPU (classification)
4. Extrapolate to the real document and page counts
5. Add 40% for exceptions, retries, re-runs, and the things you did not see in 1,000 docs
6. THEN quote hardware
```

| Tier | Shape | Serves |
|---|---|---|
| **Workstation** | 16 cores, 64 GB RAM, 24 GB VRAM | < 500 K docs; solo/small firm; Ollama |
| **Single server** | 64 cores, 256 GB RAM, 1–2 × 48 GB GPU | few million docs; vLLM |
| **Small cluster** | 3–5 such nodes + shared storage | multi-matter service provider |
| **Appliance** | sealed box, shipped, no internet | regulated / air-gapped |

> Measure a thousand documents before you quote a server. The 40% is not padding — it is
> the exceptions you have not met yet.

Notes:

Step 5 is the one experience teaches. The 1,000-document sample never contains the 400 MB
spreadsheet, the password-protected archive, or the 900-page scanned deposition. Forty
percent is a defensible planning number; anything tighter is optimism.

---

## Regulated Environments

| Regime | Who | What it forces |
|---|---|---|
| **CJIS** | law enforcement, prosecutors | FedRAMP boundary for any third party, signed Security Addendum, **fingerprint-based personnel screening**, FIPS-validated crypto, data residency, MFA, full audit |
| **FedRAMP** | federal agencies | authorized boundary; an ongoing audit obligation |
| **HIPAA** | health-related matters | BAA, minimum necessary, audit |
| **State privacy / GLBA** | consumer, financial | varies; notice and minimization |
| **FERPA** | higher-ed matters | education records |
| **Air-gapped** | national security, some corporate | no network at all |

* **The local-first shortcut:** if the data never leaves the authorized boundary, most of
  the *third-party* burden evaporates — no vendor to vet, no addendum, no provider-side
  personnel screening, no residency question about someone else's cloud
* What remains is **your own** controls — which the customer was already operating for the
  case-management system holding the same documents

> The compliance win of local inference is not that the controls are weaker. It is that
> there is **no third party** to impose them on.

Notes:

This is the CJIS briefing compressed to one slide. The commercial point for product people:
"runs in your boundary" shortens a security review from months to weeks, and that is a
sales cycle argument, not just an architecture argument.

Add the standard caveat: CJIS is revised periodically and states add their own obligations —
verify the current version with the customer's CJIS Systems Officer rather than quoting from
a slide.

---

## Operating It: Multi-Matter Reality

* **One index per matter.** Shard by matter, never by date — matters start, end, and get
  **destroyed** as units.
* **Retention and destruction are features.** "Destroy everything for matter 7714" must be
  one command that covers natives, text, index, vectors, logs, prompts, and the model cache.
  - the vector store and the prompt logs are the two people forget, and both contain document
    text
* **Ethical walls** — matter A's team must not reach matter B. Enforce at the data layer,
  not in the UI.
* **Capacity**: matters arrive in bursts with court deadlines. Plan for peak, not mean.
* **Monitoring**: queue depth, exception rate, docs/hour, GPU utilization, **and the egress
  monitor** — which is a production service, not a lab tool.

> Write the destruction script on day one and test it. A system that cannot forget a matter
> is a liability that grows.

Notes:

The destruction point lands hard with anyone who has been through a data-retention audit.
Make them enumerate every place document text lives in their own design — the answer is
always more places than they expected, and the prompt logs are always one of them.

---

## Lab 11 — Containerize and Scale

* Wrap the ingestion stage in a worker that pulls from a **SQLite work queue** with
  **leases and timeouts**
* Run N workers; measure throughput at 1, 2, 4, 8 workers and **plot the curve** — find where
  it flattens and explain why
* **Kill a worker mid-document** and show the lease expire and the unit get retried exactly
  once
* `docker-compose.yml`: workers + Tika + Ollama on an `internal: true` network, pinned
  digests, natives mounted **read-only**
* Run the whole stack with **no internet** and emit the attestation
* Write and test `destroy_matter.py` — prove document text is gone from **every** store,
  including vectors and prompt logs

**Deliverable:** a throughput curve with your explanation of where it flattens, and a
destruction script with its verification output.

Notes:

Budget 90 minutes. The throughput curve flattening is the teaching moment — it flattens at
core count for extraction, or earlier if they are on one disk, and the student has to say
which. Either answer is fine if they can justify it from their own measurement.

The destruction script is the part students tell you about months later, because somebody
asked them for it at work.

---

## ▶ LAB BREAK — Lab 11

Debrief: **"Where did your curve flatten, and why? And did `destroy_matter.py` miss
anything on the first try?"**

Notes:

Almost everyone misses something on the first destruction run — usually the chunk JSONL, the
prompt logs, or the OCR sidecar files. Collect the misses on the board. That list is the
single most useful artifact from this module.
