# Privilege and Egress Attestation — Form

**Legal AI Engineering · Elephant Scale**

This is the document that supports claim 1 — **"here is exactly where the documents went, and
nowhere else."** It is signed by a named human, it is generated from a machine record rather
than typed from memory, and it states its own limits — because an attestation whose scope is
unstated is read as covering everything, and then it is wrong.

It is written for the strict case, where the answer is *nothing left the building*. A
vendor-approved or government-cloud boundary is attested with the same form against the
**allowlist that defines it** — the destinations change, the obligation to state the boundary
and show that it held does not.

Working code: `labs/common/egress.py` and `labs/05-Local-Model-Egress-Proof/local_proof.py`.
A filled example lands in `work/attestation.json` on every run.

---

## Part 1 — The machine record

The system produces this. Nobody types it.

```json
{
  "attestation_version": "1.0",
  "run_id": "<run-id>",
  "matter": "<MATTER-ID>",
  "window": { "start": "<ISO-8601 UTC>", "end": "<ISO-8601 UTC>" },

  "host": {
    "platform": "linux",
    "python": "3.12.7",
    "hostname_sha256": "<hashed, not clear — identity for correlation, not disclosure>"
  },

  "ai_components": {
    "chat":        { "endpoint": "http://localhost:11434/v1", "model": "qwen3:8b",
                     "runtime": "ollama <version>", "weights_sha256": "<digest>",
                     "quantization": "<e.g. Q4_K_M>", "local": true,
                     "decoding": { "temperature": 0, "seed": 42 } },
    "embeddings":  { "endpoint": "http://localhost:11434/v1", "model": "nomic-embed-text",
                     "dim": 768, "local": true },
    "ocr_extraction": { "engine": "tesseract 5.3.4 (local)", "local": true },
    "telemetry_and_logs": { "destination": "local files under ./work only", "local": true }
  },

  "egress_policy": "default-deny; loopback only",
  "connection_attempts_total": 0,
  "blocked_attempts": 0,
  "non_loopback_connections": 0,
  "non_loopback_detail": [],

  "documents_processed": 0,
  "claim": "No document content left this host during the window above.",

  "scope_and_limits": [
    "In-process guard: covers socket calls made by this Python process only.",
    "Does not cover subprocesses, other host processes, or kernel-level paths.",
    "Covers the time window stated above, not continuous operation.",
    "DNS lookups are counted as disclosures and are included above.",
    "Enforcement in production belongs to a firewall or an isolated network; this guard demonstrates the control and produces the record."
  ],

  "produced_by": "egress.py (Legal AI Engineering, Elephant Scale)",
  "artifact_sha256": "<hash of this file with this field removed>"
}
```

### The four components, and why all four are listed

| Component | The leak | Why it is on the form |
|---|---|---|
| **OCR / extraction** | A cloud document-intelligence API receives the **raw page** | It happens one step *before* the model, so a local LLM downstream is cosmetic |
| **Embeddings** | A hosted embedder receives the **full chunk text** | The leak people miss, because the chat model is the one they were thinking about |
| **Chat / extraction model** | Prompt text is document text | The one everybody checks |
| **Logs and telemetry** | An APM or error reporter ships **prompt text** to a third party | No one evaluated that vendor for privilege, and it has a nice dashboard |

> If any row says `local: false`, the attestation is not a privilege claim. It is a disclosure
> record, and it should be read as one.

### `egress_policy` — the field the whole form turns on

| Value | What it supports |
|---|---|
| `deny` / `default-deny; loopback only` | **Enforced.** Connections outside loopback are blocked. This is the only value that supports the claim. |
| `deny-lan` | Enforced, with a named internal host (a vLLM server, a Tika service) explicitly allowed. Name it, and say why it is inside the wall. |
| `observe` | **Nothing was enforced.** The record says what happened, not what could not. Under the legal overlay this is an **auto-fail (LEGAL-A)** for a real matter. |

Observe-only mode is useful exactly once: to find out what your pipeline *currently* reaches
for, before you turn enforcement on. Then turn it on.

### The tripwire — why zero is not evidence

`non_loopback_connections: 0` is consistent with a guard that works and with a guard that is
not running. So the run also attempts to reach a hosted model endpoint, a log aggregator and
a cloud OCR endpoint, on purpose, and records each one being **blocked**:

```json
"blocked_during_run": [
  { "what": "a hosted model API",   "host": "api.openai.com",            "port": 443, "blocked": true },
  { "what": "a SaaS log collector", "host": "in.logs.example-apm.com",   "port": 443, "blocked": true },
  { "what": "a cloud OCR endpoint", "host": "documentai.googleapis.com", "port": 443, "blocked": true }
]
```

A zero with a tripwire is evidence. A zero without one is an absence of evidence, and the
difference is the first thing a competent expert will probe.

---

## Part 2 — The human attestation

A person signs this. The machine record is the exhibit; this is the statement.

---

### PRIVILEGE AND EGRESS ATTESTATION

**Matter:** ................................................................

**Run id:** ....................................  **Period:** .......................... to ..........................

**System:** ................................................................ (version / commit: ....................)

I have reviewed the machine record identified below and I attest the following.

**1. Processing location.** All document text processing in the period above — text
extraction, OCR, embedding generation, and model inference — was performed on
.......................................................... (host or network), under the
control of .......................................................... .

**2. AI components.** Each AI component and its location:

| Component | Model / engine | Endpoint | Local? |
|---|---|---|---|
| Text extraction / OCR | | | ☐ yes ☐ no |
| Embeddings | | | ☐ yes ☐ no |
| Chat / extraction model | | | ☐ yes ☐ no |
| Logs / telemetry destination | | | ☐ yes ☐ no |

**3. Egress control.** The egress policy in force was ☐ **enforced (deny)**
☐ **enforced with named internal hosts (deny-lan)** ☐ *observe only — no enforcement*.
Non-loopback connections observed: ................ . Deliberate egress attempts made as a
control test and blocked: ................ .

**4. Retention and training.** Document content from this matter ☐ was not ☐ was used to
train, fine-tune or otherwise update any model. If "was", describe:
..........................................................................................

**5. Matter isolation.** Document content from this matter ☐ was not ☐ was accessible to
processing for any other matter. Isolation was demonstrated by:
..........................................................................................

**6. Third parties.** The following third parties received document content or derived
content, under the stated agreements (write **NONE** if none):

..........................................................................................

**7. Scope and limits.** This attestation is limited as follows (attach the machine
record's `scope_and_limits`; add anything a reader could otherwise over-read):

..........................................................................................

**8. Machine record.** `attestation.json`, sha256 ................................................................

I understand that this attestation may be relied upon in a legal proceeding, and that it is
limited to the period and scope stated above.

**Name:** ..........................................  **Role:** ..........................................

**Signature:** ..........................................  **Date:** ..........................

---

## How to fill section 7 honestly

Most attestations are undone by their scope, not their facts. The limits below are true of
almost every in-process guard, so start from them and add your own:

- It covers **this process**. Subprocesses, other processes on the host, and kernel-level
  paths are outside it.
- It covers **this window**, not continuous operation. Yesterday's run is yesterday's
  attestation.
- It covers **network egress**. It says nothing about a USB drive, a backup agent, a synced
  folder, or a screenshot.
- **DNS counts.** A resolver query for `documents-api.vendor.example` discloses that you are
  interested in it, and resolvers are third parties. Count DNS as a disclosure or state that
  you did not.
- In production, enforcement belongs to **a firewall or an isolated network**. An in-process
  guard demonstrates the control and produces the record; it is not the perimeter.

> An **empty** limits section is worse than a missing attestation. The second is incomplete;
> the first is an overclaim, and the overclaim is what gets tested.

---

## What this form does not cover

It is an **egress and location** attestation. It is not:

- a **privilege determination** — that is review work, by lawyers, recorded in a privilege log
- a **completeness** claim about collection — that is the catalog and the exception list
- a claim about **output quality** — that is `metrics.json`, measured against blind ground
  truth
- a claim that the **model is clean** — training-data provenance is a supply-chain question
  and belongs with the model pin

Say so when you hand it over. An attestation that is read as covering all four is an
attestation you will have to walk back.

---

*Module 5 and Module 7 · Lab 05 · `labs/common/egress.py`*
