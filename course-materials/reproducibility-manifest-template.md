# Reproducibility Manifest — Template

**Legal AI Engineering · Elephant Scale**

The manifest is the one file that makes "we can re-run this review" checkable instead of
asserted. Everything in it answers the same question: **what would change the output if it
were different?** If a thing can change a determination, it is pinned here. If it cannot, it
does not belong here.

Copy the JSON below, fill it, and ship it at the root of the case snapshot. Working code is
`labs/common/bundle.py`; a filled example is in every lab's `work/case-snapshot-<matter>/`.

---

## The bundle this manifest sits in

```text
case-snapshot-<matter>/
  manifest.json                     <- this file: every pin
  corpus/
    catalog.jsonl                   one row per document, hashed
    exceptions.jsonl                what did not process, and why
  runs/<run-id>/
    prompts/*.txt                   the RENDERED prompts, one per call
    responses.jsonl                 what came back, verbatim
    retrieval.jsonl                 the retrieved chunk set per query
  decisions.jsonl                   every coding decision, with rationale and citations
  validation/
    protocol.md                     pre-registered, dated, signed
    ground_truth.jsonl              the blind labels
    metrics.json                    recall / elusion / precision, with intervals
  attestation.json                  the privilege and egress record
  VERIFY.md                         how someone else re-runs it
  verification.json                 the result when they did
```

Two rules about that tree. **`VERIFY.md` must have been run by somebody else, in a different
directory** — untested instructions are a wish. And **the rendered prompt is not the
template**: the template plus a bug is not what ran.

---

## The template

```json
{
  "bundle_version": "1.0",
  "matter": "<MATTER-ID>",
  "run_id": "run-<YYYYMMDD>T<HHMMSS>Z",
  "window": { "start": "<ISO-8601 UTC>", "end": "<ISO-8601 UTC>" },

  "reproducibility_claim": "same determinations",
  "claim_meaning": "Replaying this bundle yields the same coding decisions. Achieved by greedy decoding (temperature 0), a pinned model and runtime, and the captured prompt plus retrieved context for every call.",

  "counts": { "queries": 0, "decisions": 0 },

  "model": {
    "mode": "local",
    "chat_endpoint": "http://localhost:11434/v1",
    "chat_model": "qwen3:8b",
    "runtime": "ollama <version>",
    "weights_sha256": "<digest of the weights, or the registry digest>",
    "quantization": "<e.g. Q4_K_M — changes the output; pin it>",
    "decoding": { "temperature": 0, "seed": 42 },
    "local": true
  },

  "corpus": {
    "catalog_sha256": "<hash of catalog.jsonl>",
    "document_count": 0,
    "exceptions_sha256": "<hash of exceptions.jsonl>",
    "exception_count": 0
  },

  "embeddings": {
    "model": "nomic-embed-text",
    "dim": 768,
    "chunk_tokens": 220,
    "chunk_overlap": 0.15,
    "chunking_strategy": "structure-aware (clause / Q-A / heading) then size-bounded windows",
    "note": "Changing the embedding model changes the vector dimension and forces a full re-ingest. It is a pinned part of the pipeline."
  },

  "index": {
    "path": "<path>",
    "sha256": "<hash of the index file>",
    "frozen": true,
    "note": "Retrieval must be replayable: either freeze the index or capture the retrieved set per query. Do both."
  },

  "software": {
    "git_sha": "<commit of the pipeline that ran>",
    "python": "3.12.7",
    "platform": "<os-release-arch-libc>",
    "dependencies_sha256": "<hash of the pinned requirements>",
    "ocr_engine": "tesseract 5.3.4",
    "built_at": "<ISO-8601 UTC>"
  },

  "validation": {
    "sample_seed": 0,
    "ground_truth_sha256": "<hash of the blind labels>",
    "protocol_sha256": "<hash of validation/protocol.md>",
    "protocol_fixed_at": "<ISO-8601 UTC — must PRECEDE the run window>",
    "protocol_fixed_by": "<named person>",
    "protocol_note": null
  },

  "attestation_sha256": "<hash of attestation.json>"
}
```

---

## Field notes — the ones that get argued about

**`reproducibility_claim`** — the two honest levels:

| Claim | What it means | When you can make it |
|---|---|---|
| **same determinations** | Replay produces the same coding decisions | Greedy decoding, pinned model and runtime, captured prompts and retrieved context |
| **bit-exact** | Replay produces byte-identical output | Deterministic kernels, same hardware, same build. On a GPU, usually **not** available |

Claim *same determinations* and say why, rather than claiming *bit-exact* and being wrong in
front of someone who knows that GPU reductions are non-associative. The honest sentence is:
*"We claim the same determinations, not byte-identical output, because GPU inference is not
bit-reproducible; the decisions are stable because decoding is greedy and every prompt and
retrieved context is captured."*

**`quantization`** — a pin, not a detail. `Q4_K_M` and `Q8_0` of the same model give
different answers on the same prompt. A manifest naming `qwen3:8b` without the quantization
has not pinned the model.

**`weights_sha256`** — *"can you still get those weights?"* is a real deposition question. A
registry tag can be re-pointed; a digest cannot. Record the digest, and keep the weights.

**`embeddings.dim`** — in the manifest because the dimension is part of the schema. 768 and
1024 vectors cannot share a collection, so changing the embedder forces a re-ingest. A
retrieval layer whose embedder changed without a recorded re-ingest is not reproducible, and
the symptom is quietly worse recall rather than an error.

**`index.frozen` *and* `runs/*/retrieval.jsonl`** — belt and braces, deliberately. Freezing
the index lets a replay re-retrieve; capturing the retrieved set lets a replay proceed even
if the index is gone. Either alone leaves a gap; the gap is where "we can re-run it" fails in
practice.

**`software.git_sha`** — of the pipeline that actually ran, taken at run time. A dirty working
tree means the sha does not describe the code; record that too, or refuse to bundle.

**`validation.protocol_fixed_at`** — must **precede** `window.start`, and an auditor will
check the order rather than the presence. This is the single most common defensibility
failure in the field: a protocol written after the run, in good faith, by someone who did not
realize the order was the point.

**`attestation_sha256`** — binds the privilege record to this run. The attestation is a
separate artifact because it is a separate claim, with a separate scope; the hash is what
stops the two drifting apart.

---

## Three things that are *not* pins, and should not be in here

- **Wall-clock timings and throughput.** They vary by machine and change nothing about the
  output. Put them in the run log.
- **Anything secret.** No API keys, no tokens, no credentials, no hostnames or usernames in
  clear. If you want host identity for correlation, store a hash of it, as `attestation.json`
  does.
- **Document content.** The manifest pins the corpus by hash and count. Document text lives
  in the corpus and the captured prompts, under the protections that apply to those.

---

## `VERIFY.md` — the minimum that actually works

```markdown
# VERIFY — <MATTER-ID> run <run-id>

## What this reproduces
The coding determinations in `decisions.jsonl` and the metrics in
`validation/metrics.json`. Claim level: same determinations, not bit-exact.

## You need
- Python 3.10+
- The corpus (path is the only thing you change)
- Ollama with `qwen3:8b` and `nomic-embed-text` pulled
  (or `LEGAL_AI_MODE=offline`, which reproduces the offline run only)

## Steps
1. `pip install -r requirements.txt`         # pinned
2. Check the pins:  `python3 -c "import json;print(json.load(open('manifest.json'))['model'])"`
   and confirm `ollama list` shows that model and quantization.
3. `python3 run_matter.py --corpus <your path> --work ./replay`
4. `python3 verify.py --bundle . --replay ./replay`

## A correct replay
`verification.json` reports `decisions_match: true` and every metric within its
stated interval. Differences, if any, are listed per document id.

## What this does NOT prove
It does not prove no data left the building — that is `attestation.json`, and its
own `scope_and_limits`. It does not prove the determinations are *correct*; that is
`validation/metrics.json`, measured against blind ground truth.
```

That last section is not modesty. A verify script that implies more than it checks is the
thing an expert will take apart first.

---

## Self-check before you ship the bundle

- [ ] Every field above is filled, or explicitly `null` with a reason
- [ ] `protocol_fixed_at` **precedes** `window.start`
- [ ] The hashes recompute — re-hash the files and compare, do not trust the field
- [ ] Someone **else** ran `VERIFY.md`, in a different directory, and `verification.json` is
      in the bundle
- [ ] No secrets, no bare hostnames, no document text in the manifest
- [ ] The reproducibility claim matches what you can actually demonstrate
- [ ] `attestation.json` is present and its hash matches `attestation_sha256`

---

*Module 6 and Module 11 · Labs 05, 06 and 10 · `labs/common/bundle.py`*
