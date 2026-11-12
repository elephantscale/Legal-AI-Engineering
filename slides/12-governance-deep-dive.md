# Module 12 — Governance and Compliance Deep-Dive

Day 3 — Prove It

Elephant Scale

---

## Why an Engineer Needs This

You will not write the policy. You will be the person asked:

* *"Does our system do this?"*
* *"Can you show me the evidence?"*
* *"What changes if this regulation applies to us?"*

> Governance is the part of compliance that becomes **product requirements**. That is why
> it is in an engineering course.

Notes:

Frame it as requirements engineering, not law. Engineers switch off when a module smells
like a compliance briefing; they lean in when it is "here are six things somebody will ask
your system to prove."

---

## The Landscape, Without the Hype

**What is actually binding on your users today:**

* **The protective order in the matter** — the most immediate and most concrete. Post
  *Morgan v. V2X*, it may name which AI tools are permitted and require disclosure of which
  tools touched confidential material.
* **Client outside-counsel guidelines** — increasingly carry AI clauses: approval before
  use, no training on client data, disclosure obligations
* **Professional-responsibility rules** — competence, confidentiality, supervision of
  non-lawyer (and now non-human) assistance
* **Sector regimes** — CJIS, HIPAA, GLBA, FERPA, state privacy laws

**What is coming, and matters more for product strategy than for Monday:**

* **100+ US state AI laws** — a patchwork; disclosure, impact assessments, sector rules
* **The EU AI Act** — risk-tiered. Note: AI used in the **administration of justice** sits
  in a high-risk category, which is a direction-of-travel signal for legal AI even where it
  does not bind you today.

> The protective order binds you this quarter. The EU AI Act shapes your roadmap. Do not
> confuse the two in a planning meeting.

Notes:

That distinction is the most useful thing in the module. Teams either panic about the AI Act
or ignore everything — the correct posture is to treat the protective order and the OCGs as
today's requirements, and the statutory landscape as roadmap pressure.

Be careful and current: this landscape moves. Say explicitly that specifics should be checked
rather than taken from a slide.

---

## What an Auditor Will Actually Ask For

Nine artifacts. If you have them, an audit is a morning. If you don't, it is a quarter.

| # | Artifact | Where it comes from |
|---|---|---|
| 1 | **Written AI use policy** — what's allowed, by whom, with what data | the organization |
| 2 | **System description** — data flows, every hop, every component | your architecture doc |
| 3 | **Egress attestation** per matter | Module 5 / Lab 05 |
| 4 | **Validation protocol**, pre-registered, + results | Module 6 / Lab 06 |
| 5 | **Reproducibility bundle** that replays | Module 6 / Lab 06 |
| 6 | **Audit trail** per matter: prompts, retrieved context, decisions, overrides | Modules 6–7 |
| 7 | **Model inventory** — name, version, hash, quantization, provenance (an AI SBOM) | Module 7 |
| 8 | **Access-control and ethical-wall** evidence | your deployment |
| 9 | **Incident and exception records** — including the processing exception list | Modules 2, 7 |

> Every one of those nine is a **file your system emits**, not a document somebody writes
> afterwards. Build them as outputs.

Notes:

This is the module's thesis and the most actionable slide in it. The reframe — compliance
artifacts as *program outputs* rather than *documentation projects* — is what separates a
system that is auditable from one that is audited.

Have students check off which of the nine their Lab 02–07 system already produces. The honest
answer is usually six or seven, which is encouraging and also shows them the gaps.

---

## Pre-Registration: The Cheapest Credibility You Can Buy

Write the validation protocol **before** the run. Commit it. Hash it.

```markdown
# validation/protocol.md   (written 2026-11-09, before any classification run)
Matter: SYNTHETIC-DEMO-01
Richness estimate: 4.1% (from a 600-doc random sample, seed 20261109)
Classifier: qwen3:14b, Q4_K_M, weights sha256 9ab3..., temp 0, seed 42
Validation design:
  - elusion test on a random sample of the null set, n = 400, seed 884422
  - reviewers blind to the model's call
  - ACCEPTANCE THRESHOLD (set now, before the test): elusion <= 2.0%
  - if elusion > 2.0%: lower the responsiveness threshold and re-run; do not re-sample
Recall target: >= 80%, reported with a 95% confidence interval
Overlap: 50 documents double-reviewed to measure reviewer agreement
```

* The threshold is chosen **before** the result is known. That is the entire point.
* Hash the protocol and put the hash in the manifest. Now the ordering is provable.

> Choosing your acceptance criterion after seeing the result is the one thing an opposing
> expert can destroy you with. Pre-registration costs ten minutes.

Notes:

Borrowed, deliberately, from clinical-trial methodology — and if the room includes anyone
with a science background, say so, because the parallel makes it immediately legible.

The "do not re-sample" line in the protocol is important: re-drawing a sample until you like
the number is p-hacking, and in this context it is worse than p-hacking.

---

## SAIS-100: The Verified Assessment

The self-assessment is fast. The **verified** assessment is the one with teeth.

* Same six categories, same weights, same anchored 0–3 levels
* The difference: **every sub-score cites evidence** — a file path, a config line, a test
  result, a log sample. Not a claim.
* Levels rise along three axes together:

| Level | Coverage | Enforcement | Verification |
|---|---|---|---|
| **0** | none / unknown | ad hoc or absent | none |
| **1** | some paths | manual, bypassable | none / anecdotal |
| **2** | main paths | enforced in code, known gaps | spot-checked |
| **3** | every surface | enforced by design | tested + monitored |

* So **"we're careful about that"** is a **0**. There is no partial credit for intention.

> The anchors are what make two assessors converge on the same number. That convergence is
> the difference between a score and an opinion.

Notes:

Dwell on the "we're careful" → 0 point; it is the most clarifying rule in the framework and
it is what makes the score mean something when a client re-runs it.

---

## Worked Example: Two Sub-Scores, Legal Flavor

**Data Security Q2 — matter isolation** *(the legal translation of tenant isolation)*

| | State |
|---|---|
| **0** | Shared index/context across matters; a user could retrieve matter B's documents. Never tested. |
| **1** | A `matter_id` filter in application code only; easy to bypass; retrieval not scoped; no test. |
| **2** | Enforced at the **data layer** — per-matter index or row-level security, retrieval scoped by metadata; tested for common cases, **not adversarially**. |
| **3** | Enforced by design at the data layer **and verified adversarially** — someone actively tried to cross matters via prompt, retrieval, and API and failed; a continuous test guards it. |

**Evidence:** the per-matter index config or RLS policy; the retrieval filter code; the
cross-matter red-team test result.
**🚩 Auto-fail:** a confirmed cross-matter retrieval = **0 = Do Not Deploy.**

**Model & Supply Chain Q1 — provenance and pinning**

| | State |
|---|---|
| **0** | Model and embedder unknown or floating (`latest`); no hashes; the review cannot be reproduced. |
| **1** | Names known, versions floating; no integrity check. |
| **2** | Model, quantization, embedder, and dims pinned and recorded for the main paths; hash verified for the model. |
| **3** | All of the above plus a maintained **AI SBOM**; the reproducibility bundle **replays and certifies match**; a model bump triggers re-validation by policy. |

**Evidence:** `manifest.json`; the weights hash; a successful `verify-snapshot` run.
**🚩 Auto-fail (legal):** the model **cannot be pinned** → the review is not reproducible.

Notes:

Walk both tables. The matter-isolation one is the hardest engineering problem in legal AI
because matters are not tenants — same firm, same users, sometimes the same custodians, with
an ethical wall between them.

The supply-chain auto-fail is this course's addition to SAIS-100 and it is the one that
pushes toward local inference on purely defensibility grounds, independent of privacy.

---

## Re-Scoring: A Score Is a Baseline, Not a Verdict

Re-score when **any** of these change:

* the **model** or its quantization (a bump is a code change)
* the **embedding model** (and therefore the whole index)
* **chunking** or retrieval parameters
* the **prompt templates**
* the **deployment boundary** or the egress policy
* a new **matter type** or data category
* after any **incident**

* Put it in CI if you can: a SAIS-100 self-score as a release gate, with the score recorded
  per release. Then you have a **trend**, which is the thing management actually wants.

> One score is a snapshot. A dated series of scores is a program.

Notes:

The trend framing is how a student sells this internally on Monday. Managers cannot act on
"our AI security is decent." They can act on "we were 62, we are 78, and here is what the
next five points cost."

---

## Lab 12 — Full SAIS-100 Verified Audit

Audit the system you built in Labs 02–07 — as an **assessor**, not as its author:

* All six categories, three questions each, 0–3 against the anchored levels
* **Every sub-score cites real evidence**: a path, a line, a test result, a log sample.
  "We're careful" scores 0.
* Check all **four legal auto-fails** explicitly, with evidence for each
* Produce the nine audit artifacts list — present or missing, with the gap named
* Write a **findings report**: score, verdict, the three highest-value fixes with effort
  estimates
* Then **apply the cheapest fix** and re-score. Record the delta.

**Deliverable:** `sais100-verified.json` with evidence citations, a one-page findings report,
and the before/after delta.

Notes:

Budget 90 minutes. Swap systems between pairs if you can — auditing somebody else's system is
far more instructive than auditing your own, and it is what the job actually looks like.

The "apply the cheapest fix and re-score" step is what makes the module feel like engineering
rather than paperwork. Usually it is enforcing egress rather than observing it, or pinning
the embedding model in the manifest.

---

## ▶ LAB BREAK — Lab 12

Debrief: **"What was the cheapest point you bought, and what was the most expensive one you
chose not to?"**

Notes:

That second clause is the professional judgment question and it is the right note to end the
course on. Not every gap gets closed. Knowing which ones you are consciously carrying — and
being able to say why — is what a senior legal engineer is paid for.
