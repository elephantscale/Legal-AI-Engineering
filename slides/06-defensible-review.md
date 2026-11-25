# Module 6 — Defensible AI Review

Elephant Scale

---

## The Second Claim

> **"Here is exactly what the system did, and you can re-run it."**

* Nobody read all the documents. That is the entire point of using AI.
* So the review is not judged on being **right** — it is judged on being **reasonable,
  measured, and documented**
* Which means the real output of your system is not the classification. It is the **record.**

Notes:

Open by restating the uncomfortable premise: no human reviewed the whole corpus, so nobody —
including you — knows the true answer. Defensibility is the discipline of making decisions
under that condition in a way that survives scrutiny. Engineers find this genuinely
disorienting for about ten minutes, and then it clicks.

---

## What "Defensible" Means in Practice

Three properties. All three, or you have none.

* **Measured** — you have numbers from a **blind** sample: recall, elusion, precision
* **Transparent** — you can answer *"why was this document coded this way?"* for any
  document, a year later
* **Reproducible** — someone else can re-run your process and get the **same
  determinations**

* And one process property wrapping them: **documented** — the protocol was written down
  *before* the run, and the run matched it

> An unmeasured correct review is worth less, legally, than a measured imperfect one.

Notes:

This is the sentence from Module 1 coming due. Have the argument if the room wants it — the
engineer's objection ("surely accuracy is what matters") is reasonable and the answer is that
accuracy is unobservable here, so the only thing anyone can evaluate is the process and the
evidence you produced about it.

---

## The Confusion Matrix, In Legal Terms

```text
                      TRUTH (from a human-reviewed sample)
                      Responsive        Not responsive
                   +------------------+------------------+
  SYSTEM  Called   |   True Positive  |  False Positive  |
          responsive|       TP        |       FP         |  <- wasted review cost
                   +------------------+------------------+
          Called   |  False Negative  |  True Negative   |
          not resp.|       FN         |       TN         |
                   +------------------+------------------+
                      ^ THE DANGEROUS ONE
                        a responsive document you never produced
```

* **FP costs money.** A reviewer reads a document that didn't matter.
* **FN costs the case.** A responsive document was never produced. That is the sanctionable
  one, and the one nobody can see without a sample.

> In litigation the two error types are not symmetric, and your threshold decision should
> not pretend they are.

Notes:

Spend real time here. Most engineers optimize F1 by reflex, which weights FP and FN equally.
In eDiscovery, FN is categorically worse. That argues for a threshold tuned to recall, and
for stating the chosen threshold and its rationale in the protocol *before* the run.

---

## Recall — The Number You Will Be Asked For

**Of all the responsive documents in the corpus, what fraction did we find?**

```text
  Recall = TP / (TP + FN)
```

* This is **the** eDiscovery metric. If you learn one, learn this.
* You cannot compute it from your output — you need a **sample of what you rejected**
* There is no magic threshold in law, but practitioners commonly target **~75–80%+**, and
  what actually matters is that the number is **measured, disclosed, and reasonable** for the
  matter

* **Report a confidence interval, not a point estimate.** "Recall 82% (95% CI: 76–87%)"
  is a defensible statement. "Recall 82%" is a number with no error bars pretending to be a
  fact.

> Recall is the question. Everything else on this slide deck is in service of being able to
> answer it with a straight face.

Notes:

Insist on the interval. A sample of 400 documents gives you roughly ±5 points at 95%
confidence; a sample of 50 gives you ±14 and is nearly useless for a recall claim. Students
should know how to size a sample before they promise a number — the cheat sheet in
`course-materials/` has the table.

---

## Elusion — Recall's Honest Sibling

**Of the documents we set aside as non-responsive, what fraction were actually responsive?**

```text
  Elusion = FN / (FN + TN)        -- measured on a random sample of the DISCARD pile
```

* You take a random sample of what you **rejected** and have humans review it
* It directly tests the scary claim: *"we did not throw away anything important"*
* **Why it is often preferred to recall:** elusion is measured on a sample you can actually
  draw. Recall requires knowing the total number of responsive documents, which you don't.
* A low elusion rate on a properly-sized random sample is the strongest single piece of
  evidence a review produces

> Recall asks *"did we find them?"* Elusion asks *"what did we miss?"* — and elusion is the
> one you can actually measure.

Notes:

This is the slide that separates people who have read a blog post about TAR from people who
have run one. Elusion testing is the standard validation protocol in practice, and it is
cheap: a random sample of the null set, human-reviewed, with a defined acceptance threshold
set *in advance*.

Set the threshold before the test. Choosing the acceptance criterion after seeing the result
is the thing an opposing expert will crucify you for.

---

## Precision, Richness, and the Cost Conversation

* **Precision** = `TP / (TP + FP)` — of what we called responsive, how much actually was.
  This is your **review cost** metric. Low precision means paying reviewers to read noise.
* **Richness (prevalence)** = what fraction of the whole corpus is responsive. Usually
  **1–10%**. Measure it first, from a random sample.
  - Richness drives everything: sample sizes, cost estimates, and whether AI is worth it at
    all
* **F1** — the harmonic mean. Useful for model tuning. **Do not report F1 to a court**; it
  hides the asymmetry between FP and FN behind a single number.

```text
  10,000 docs · richness 4%  =>  ~400 responsive documents in there somewhere
  recall 80%  =>  ~320 found,  ~80 missed
  precision 50%  =>  reviewers read ~640 docs to see those 320
```

> Richness first. It sets the sample sizes, the cost model, and the honest answer to
> "should we even use AI here?"

Notes:

Walk the arithmetic on the projector; it is the most practical slide in the module. The
richness-4% example is realistic and it shows why precision is a budget line and recall is a
risk line.

The F1 warning is worth saying firmly. Reporting F1 in a validation report invites the
question "which of your two error types does that conceal?"

---

## Ground Truth: The Part You Cannot Fake

* Ground truth is **human judgment**, on a **random** sample, **blind** to the system's
  prediction
* Three rules, each of which exists because somebody broke it:
  1. **Random.** Not "interesting documents." Not a keyword-selected set. Random, seeded,
     and record the seed.
  2. **Blind.** The reviewer must not see the model's call. Anchoring is real and it
     destroys the measurement.
  3. **Before, not after.** Size the sample and set the acceptance threshold **in the
     protocol**, before the run.

* Measure **reviewer agreement** too. Two humans on the same 50 documents will disagree on
  a meaningful share — overlap them and report the rate.

> If human reviewers agree with each other only ~85% of the time, then **85% is your
> ceiling**, not 100%. Say that out loud before anyone demands perfection.

Notes:

The agreement-ceiling point reframes the whole conversation and it is the most useful thing
you can hand a student arguing with a skeptical partner. Responsiveness is a judgment call;
human-to-human agreement on real matters is often in the 70s and 80s. A system that matches
human reviewers as well as humans match each other is performing at the ceiling of the task.

---

## TAR and Active Learning, In One Slide

**TAR** = Technology Assisted Review. The workflow around the model, not a model.

```text
 TAR 1.0 (simple passive learning)        TAR 2.0 (continuous active learning, CAL)
 ---------------------------------        ---------------------------------------
 1. train on a seed set                   1. start reviewing the best-ranked docs
 2. STOP training                         2. every human call retrains the ranker
 3. classify the whole corpus             3. the queue re-ranks continuously
 4. validate (elusion test)               4. stop when marginal yield drops
 5. one defensible snapshot               5. validate with an elusion test

 easier to document                       finds responsive docs faster
 stable, pinnable, reproducible           a moving target to document
```

* **The defensibility tension is real:** CAL is more effective and *harder to reproduce*,
  because the model changed under you during the review
* The answer is not to avoid CAL. It is to **snapshot**: version the model at each
  checkpoint, log every training event, and be able to say what the ranker looked like when
  document X was coded

> Any system that learns during the review must **version itself** during the review.

Notes:

This is where LLM classification and classical TAR meet. An LLM-based coder with a fixed
prompt and a pinned model is essentially TAR 1.0 — and that is a feature, because it is
trivially reproducible. The moment you add few-shot examples that grow as reviewers work,
you have built CAL and inherited its documentation burden. Make that trade deliberately.

---

## "Why Did It Code This Document That Way?"

You will be asked this about a specific document, months later. What you need stored:

* The **document** (hash) and the **coding decision** with a timestamp
* The **exact prompt**, fully rendered — including every retrieved chunk, in order
* The **model** name, version, **weights hash**, quantization, runtime + version
* **Decoding parameters** — temperature, top-p, seed
* The **model's stated rationale** and its **citations**
* The **reviewer** who confirmed, overrode, or sampled it

```json
{"doc_id":"DOC-000417","decision":"responsive","confidence":0.88,
 "rationale":"Discusses the Q3 revenue restatement [2] and names the auditor [1].",
 "citations":["DOC-000091#c3","DOC-000417#c1"],
 "model":{"name":"qwen3:14b","weights_sha256":"9ab3...","quant":"Q4_K_M",
          "runtime":"ollama 0.5.4"},
 "decoding":{"temperature":0,"seed":42},
 "prompt_sha256":"5c2f...","prompt_path":"runs/run-7f3a/prompts/DOC-000417.txt",
 "reviewed_by":"areviewer","reviewed_at":"2026-11-09T15:02:00Z","override":null}
```

* **Store the rendered prompt, not the template.** The template plus a bug is not what ran.

> One row per decision. Append-only. Hashed. This file is your witness.

Notes:

"Store the rendered prompt, not the template" is the line that saves people. Teams store the
template and the doc id and believe they can reconstruct the prompt. They can't — retrieval
is non-deterministic across index rebuilds, and the chunk set is half the prompt.

The `override` field matters legally: a human disagreeing with the model, recorded, is
evidence of meaningful human review. An empty override column across 200,000 documents
suggests the humans were rubber-stamping.

---

## Reproducibility: What You Must Pin

To re-run a review and get the **same determinations**:

| Pin | Why |
|---|---|
| **Model weights** (by hash) + **quantization** | A different quant is a different model |
| **Runtime** engine + version | Inference kernels change between versions |
| **Decoding**: temperature 0, fixed seed | Greedy decoding removes sampling variance |
| **Every prompt**, rendered | Half the prompt is the retrieved context |
| **Embedding model** + version + **chunking params** | Changes retrieval, therefore the prompt |
| **The index** — frozen, or the retrieved sets captured | Retrieval must be replayable |
| **Software build** — git SHA + build time | Your own glue code is part of the pipeline |
| **Corpus** — hash + document count | The inputs must be the same inputs |

* **You cannot pin a hosted model.** It is not yours, and it is silently replaced. That is
  not a hypothetical — point releases change behavior without changing the name you call.

> Reproducibility is the strongest argument for local inference, and it is the one nobody
> in legal has fully priced in yet.

Notes:

This table is lifted from FreeEed's reproducibility-bundle design and it is the most
commercially valuable slide in the course. The "cannot pin a hosted model" line is the
durable differentiator for local deployment — privacy gets the attention, but reproducibility
is the argument that cannot be answered with a better contract.

---

## Determinism: Be Precise, Don't Overclaim

* **Greedy decoding (temperature 0)** removes sampling variance. It does **not** make GPU
  inference bit-exact — parallel floating-point reduction order varies.
* So define two bars, and sell the right one:

| Bar | What you promise | How |
|---|---|---|
| **Same determinations** | Re-running yields the same coding decisions | temp 0 + pinned model/runtime + captured prompts. Robust in practice. |
| **Bit-exact replay** | Identical token-for-token output | run the verify pass on a **deterministic backend** (CPU / fixed config) |

* Ship "same determinations" as the default claim. Offer bit-exact as an archival **mode**.

> Promise determinations, deliver determinations, and offer bit-exact as a mode. A
> reproducibility product that overclaims reproducibility is the worst possible look.

Notes:

This slide exists because the temptation to say "fully deterministic" is enormous and it is
false on GPU. The nuance is not a weakness — presenting it correctly is what makes an expert
in the room trust everything else you said.

---

## The Defensible Case Snapshot

A single exportable bundle that lets someone re-run your review a year later:

```text
case-snapshot-SYNTHETIC-DEMO-01/
  manifest.json          <- the pins: model+hash+quant, runtime, decoding, corpus hash,
                            embeddings+chunking, software SHA, ground-truth metrics
  corpus/
    catalog.jsonl        <- one row per document, hashed (Lab 02)
    exceptions.jsonl     <- what did not process, and why
  runs/run-7f3a/
    prompts/             <- every rendered prompt
    responses.jsonl      <- every output, with citations and rationales
    retrieval.jsonl      <- the retrieved chunk set per query  (the half people forget)
  decisions.jsonl        <- one row per coding decision, with reviewer + override
  validation/
    protocol.md          <- written BEFORE the run: sample size, threshold, acceptance
    ground_truth.jsonl   <- blind human calls, with the seed
    metrics.json         <- recall, elusion, precision, richness, CIs, agreement rate
  attestation.json       <- Module 5: where the documents went
  model/                 <- the weights, for external hand-off (optional, large)
  VERIFY.md              <- how to re-run this and what "match" means
```

* `verify-snapshot <bundle>` → load the pinned model → replay each logged query with its
  captured context → diff against archived outputs → **certify match**

> This is the "hand it to opposing counsel and let them re-run it" proof. Nobody else in
> legal AI can currently offer it, because nobody else is running the model locally.

Notes:

This bundle is the capstone deliverable and it is FreeEed's Phase-3 differentiator. Walk the
tree and name the two directories teams always omit: `retrieval.jsonl` and
`validation/protocol.md`. Without the first you cannot replay. Without the second your
metrics were chosen after you saw the results.

The `model/` directory is optional because weights are large — the normal case is pin by
hash and keep weights in a content-addressed store; materialize them into the bundle only
for external hand-off.

---

## Human-in-the-Loop Is a Legal Requirement, Not a UX Choice

* A fully autonomous privilege call is not a thing you should ship
* **Where humans must sit:**
  - the **privilege** determination — always
  - the **validation sample** — always, blind
  - **low-confidence** bands — route them, don't guess
  - any **production** decision — documents go out the door under a signature
* Record the human's call **and** their disagreements. The override rate is evidence that
  review was meaningful.

> Design for the signature. Someone's name goes next to this, and they are entitled to a
> system that lets them actually check.

Notes:

The override-rate point is the practical teaching: build the UI so disagreeing is as easy as
agreeing, and log both. A 0% override rate is not a sign of a great model; it is a sign of a
rubber-stamp workflow, and an opposing expert will read it that way.

---

## Lab 06 — Defensible Review

Measure an AI review against a blind ground truth and produce the bundle:

* Estimate **richness** from a random sample; size the validation samples properly
* Run the LLM classifier (local, temp 0, pinned) over the corpus with rationales + citations
* Draw a **blind, seeded** ground-truth sample; take the human calls (pre-labeled in the
  synthetic corpus)
* Compute **recall, elusion, precision, F1, richness — with confidence intervals**
* Run an **elusion test** on the discard pile against a threshold you set *first*
* Emit `metrics.json`, `decisions.jsonl`, and a **reproducibility bundle**; then
  **verify it replays**

**Deliverable:** `case-snapshot-*/` that passes its own `verify-snapshot` check.

Notes:

Budget 90 minutes — this is the heaviest lab and the most valuable. The moment that lands is
the verify step: students change one pin (the seed, or the model tag) and watch verification
*fail*. That failure is the lesson.

Make them write `validation/protocol.md` before they run anything. Students who skip it and
then pick a threshold will feel exactly why that is not allowed.

---

## ▶ LAB BREAK — Lab 06

Debrief: **"Read me your recall with its interval, and your elusion rate. Then tell me
whether you'd sign it."**

Notes:

That last clause is the whole module. Some students will have a defensible number and some
will have a number with a ±14 interval off a 50-document sample. Both outcomes teach. Ask the
second group what sample size they would need, and make them compute it.
