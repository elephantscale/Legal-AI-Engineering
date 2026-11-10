# Legal AI Design Canvas

**Legal AI Engineering · Elephant Scale · one page, before you write any code**

Fill this in before the first commit. It takes twenty minutes and it is the cheapest point at
which to discover that the thing being asked for cannot be defended.

The canvas has nine boxes. Box 9 is the one that matters, and most projects are improved by
filling it first.

---

## 1. The matter and the question

**Matter / project:** ................................................................

**The decision this system informs:** ..............................................................

..........................................................................................

**Who makes that decision, by name or role:** ..........................................................

Write the decision, not the capability. "Rank documents by responsiveness so a reviewer sees
the likely-responsive ones first" is a decision. "Use AI for document review" is a budget
line.

**Volume:** ................ documents / ................ GB  **Custodians:** ................

**Deadline, and what is actually fixed about it:** ..........................................................

---

## 2. The claim you will have to make

Pick the ones that apply. Each one has a cost, listed.

- [ ] **"Nothing left the building."** → local OCR, local embeddings, local model, local logs,
      enforced egress, and an attestation with a stated scope
- [ ] **"Here is exactly what the system did, and you can re-run it."** → pinned model,
      rendered prompts logged, retrieval captured, reproducibility bundle, a `VERIFY.md` that
      somebody else has run
- [ ] **"We found what was responsive."** → blind ground truth, a pre-registered protocol,
      recall **and** elusion with intervals
- [ ] **"We did not produce privileged material."** → rule plus human review, a privilege log,
      and a production gate
- [ ] **"A human approved what went out."** → a named, timestamped approval that predates the
      production, and a producer that refuses without it

**Claims you will NOT make:** ..........................................................................

That last line saves more arguments than any other line on this page. Write it down now,
while nobody wants anything.

---

## 3. The data, honestly

| | |
|---|---|
| **Formats** | |
| **Containers** (zip, pst, mbox, nested?) | |
| **How much needs OCR** | |
| **Load files in / out** (format, encoding) | |
| **Known mess** (truncated, encrypted, zero-byte) | |
| **Languages** | |
| **What you have *not* seen yet** | |

> The last row is the honest one. Every ingestion estimate is wrong in proportion to how
> confidently it was made before looking at the data.

---

## 4. The four leak points — decide each, now

| Leak point | Decision | If not local, what covers it |
|---|---|---|
| **Text extraction / OCR** | ☐ local ☐ hosted | |
| **Embeddings** | ☐ local ☐ hosted | |
| **Chat / extraction model** | ☐ local ☐ hosted | |
| **Logs / traces / telemetry** | ☐ local ☐ hosted | |

All four, or the exercise is theatre. The second and fourth rows are where real systems leak,
because the first and third are the ones people were thinking about.

**Egress policy:** ☐ `deny` ☐ `deny-lan` (named internal hosts: ....................) ☐ `observe`

`observe` is a legal auto-fail for a real matter. It is for finding out what your pipeline
currently reaches for, and then you turn it on.

---

## 5. The model, and the pin

| | |
|---|---|
| **Chat / extraction model + quantization** | |
| **Embedding model + dimension** | |
| **Serving** (Ollama laptop / vLLM server / other) | |
| **Hardware available** | |
| **How it is pinned** (digest, weights hash) | |
| **Can you still get these weights in two years?** | ☐ yes ☐ no |

If the answer to the last row is no, the model cannot be pinned and the review cannot be
reproduced. That is **LEGAL-D**, and it is a procurement decision, not an engineering one.

**What you give up by staying local, stated plainly:** ..........................................................

..........................................................................................

A local open-weight model is worse at long contract reasoning than a frontier model. Say so
in writing now, and the conversation later is about trade-offs rather than surprises.

---

## 6. Measurement — decided before you build

| | |
|---|---|
| **Richness estimate** (and how) | |
| **Acceptance threshold**, and who fixes it | |
| **Validation sample size** and margin | |
| **Elusion sample size** | |
| **Who holds ground truth, and how blindness is kept** | |
| **Stop rule** | |
| **Protocol fixed by / on** | |

The protocol is written and hashed **before** the classification run. Nothing else on this
canvas is as easy to get wrong in good faith, or as hard to repair afterwards.

---

## 7. The human in the loop

| Step | Who | Recorded how |
|---|---|---|
| Privilege calls | | |
| Responsiveness QC | | |
| Threshold decisions | | |
| **Production approval** | | |
| Destruction authorization | | |

Approval is a **command the system records**, never a tool the automation can invoke. If
anything in this table can be done by the system on its own behalf, it is not a gate.

---

## 8. The artifacts — name the files now

| Artifact | File |
|---|---|
| Catalog | |
| Exception list | |
| Search log | |
| Rendered prompts + retrieval | |
| Decisions with citations | |
| Validation protocol (hashed) | |
| Metrics with intervals | |
| Attestation | |
| Reproducibility bundle + `VERIFY.md` | |
| Production manifest with disclosures | |
| SAIS-100 score with the legal overlay | |

Naming them in advance is what makes the pipeline emit them rather than reconstruct them
later. Every stage should write one.

---

## 9. What this system cannot prove

The most important box. Three things minimum, each one specific enough to be checked.

1. ..........................................................................................
2. ..........................................................................................
3. ..........................................................................................

**Where a competent opponent would attack first:** ..........................................................

**What you would measure to find out if you are wrong:** ..........................................................

Honest answers from real projects: OCR confidence on degraded scans; the quality gap between
a local 8B model and a frontier model on long contract reasoning; sample size — a
400-document sample cannot resolve a 1% elusion difference; GPU non-determinism, which is why
the claim is *same determinations* and not *bit-exact*; and the monitor's scope, which covers
this process and not the whole host.

> A system whose author can name its limits is a system someone can rely on. "No significant
> limitations" is a failing answer here, and it is a failing answer in a deposition.

---

## Sign-off

**Engineer:** ..........................................  **Date:** ..........................

**Counsel:** ..........................................  **Date:** ..........................

Both signatures. The engineer cannot decide the dedupe policy or the acceptance threshold;
counsel cannot decide the embedding dimension. The failures in this field live exactly where
those two stop talking.

---

*Use before Module 2, revisit at Module 7, sign before the capstone. Modules 1–12.*
