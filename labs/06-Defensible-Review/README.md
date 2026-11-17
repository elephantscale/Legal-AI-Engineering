# Lab 06 — Defensible Review

**Module:** 6 — Defensible AI Review
**Duration:** 90 minutes
**Difficulty:** Advanced

---

## Goal

Measure an AI review against a **blind** ground truth and produce the **defensible case
snapshot** — a bundle someone else can use to re-run your review a year from now and get
the same determinations.

> In litigation, an **unmeasured** correct answer is worth less than a **measured**
> imperfect one.

## Files in this lab

```
06-Defensible-Review/
  README.md               <- you are here
  requirements.txt        <- nothing to install
  defensible_review.py    <- richness / protocol / classify / measure / bundle / verify
```

The metrics (`../common/metrics.py`) and the bundle writer (`../common/bundle.py`) are
small enough to check by hand. Read them — a metric you cannot verify yourself is a metric
you should not put in a declaration.

## Prerequisites

- Labs 02–05 complete. In particular `../work/attestation.json` from Lab 05 goes **into**
  the bundle.
- A local model makes the classification realistic (`ollama pull qwen3:8b`). Without one,
  the lab uses a **keyword baseline** — not a toy: keyword culling is how eDiscovery was
  done for twenty years and is still how search-term protocols are negotiated. Every
  measurement in this lab is just as real against it.

## Steps — and the order is the point

### 1. Richness first

```sh
python3 defensible_review.py richness --work ../work --corpus ../assets/corpus
```

Prevalence sets everything: your sample sizes, your cost model, and the honest answer to
*"should we even use AI on this corpus?"* Note the sample size the tool tells you you need
for ±5 points.

### 2. Pre-register the protocol — **before** you classify anything

```sh
python3 defensible_review.py protocol --work ../work --corpus ../assets/corpus
cat ../work/validation-protocol.md
```

Read it properly. The **acceptance threshold** (elusion ≤ 2.0%) is now fixed, and you
fixed it before you knew the answer. That is the only reason anyone should believe it.

Now try to run it twice:

```sh
python3 defensible_review.py protocol --work ../work --corpus ../assets/corpus
```

It refuses. **That refusal is the control.** A protocol you can rewrite after seeing the
result is not a pre-registration.

And try skipping it entirely — `classify` refuses too. The tool enforces the order
because the order is the legal argument.

### 3. Classify

```sh
python3 defensible_review.py classify --work ../work --corpus ../assets/corpus
```

**On a laptop with no GPU, add `--limit 150`.** This stage is one model call per document
across ~1,200 documents, which is a tea break on a GPU and not class-time work on a CPU.
Sampling is not a workaround here — `measure` handles it correctly and returns a wider
confidence interval, which is this module's subject. `--classifier keyword` is the other
route, and worth running either way.


Read the routing summary, and then read `classify_one` and the banding logic:

- **privilege never auto-codes.** There is no confidence threshold that makes an automated
  privilege call acceptable. Every flag goes to a human.
- **an unparseable response goes to a human**, not to "not responsive". Defaulting a parse
  failure to "not responsive" hides false negatives in the one place they are most
  dangerous.
- one document should come back with `injection_attempt: true`. That is planted finding
  **F6**, and the correct behavior is to flag it and keep coding — never to obey it.

### 4. Measure

```sh
python3 defensible_review.py measure --work ../work --corpus ../assets/corpus
```

You get recall, precision, elusion and richness — **each with a 95% Wilson interval** —
plus the reviewer-agreement ceiling, and a pass/fail against the threshold you set in
step 2.

Three things to look at, in this order:

1. **Elusion** against your pre-set threshold. This is the number that tests
   *"we did not throw away anything important"*, and unlike recall its denominator is a
   sample you can actually draw.
2. **Recall, at the lower bound of the interval.** If the point estimate meets your target
   and the lower bound does not, you have an estimate *consistent with* the target — not a
   demonstration of it. The tool says this out loud; say it the same way.
3. **Reviewer agreement.** That is your ceiling. If two humans agree 92% of the time, 92%
   is the ceiling and no classifier can be held to 100%.

Note what is deliberately **not** in the report: F1. It conceals the asymmetry between a
false positive (wasted review cost) and a false negative (a responsive document never
produced).

### 5. Bundle

```sh
python3 defensible_review.py bundle --work ../work --corpus ../assets/corpus
find ../work/case-snapshot-SYNTHETIC-DEMO-01 -type f | head -20
cat ../work/case-snapshot-SYNTHETIC-DEMO-01/manifest.json
```

Walk the tree and find the two things teams always omit:

- `runs/<run-id>/retrieval.jsonl` — **what the model saw.** Half the prompt is retrieved
  text; without this nothing can be replayed.
- `validation/protocol.md` — without it, your threshold was chosen after the fact.

### 6. Verify — and then break it on purpose

```sh
python3 defensible_review.py verify --work ../work --replay
```

You want `"certified": true` and `differed: 0`.

Now break a pin and watch it fail:

```sh
python3 -c "
import json,pathlib
p = pathlib.Path('../work/case-snapshot-SYNTHETIC-DEMO-01/manifest.json')
m = json.loads(p.read_text()); m['model']['weights_sha256'] = None
p.write_text(json.dumps(m, indent=2))"
python3 defensible_review.py verify --work ../work
```

`UNPINNED model has no weights hash — this review is not reproducible (legal auto-fail)`.
Re-bundle to fix it. **That failure is the lesson:** the bundle is only worth something
because it refuses to certify when a pin is missing.

Then try tampering with the catalog and re-verifying. The hash check catches it.

## Deliverable

`../work/case-snapshot-SYNTHETIC-DEMO-01/` that passes its own `verify --replay`,
containing:

1. `manifest.json` — every pin: model + hash + quantization, runtime, decoding, corpus
   hash, embeddings + dims + chunking, index, software git SHA
2. `validation/protocol.md` — pre-registered, hashed
3. `validation/metrics.json` — recall, elusion, precision, richness, **with intervals**
4. `runs/<run-id>/{prompts/, responses.jsonl, retrieval.jsonl}`
5. `decisions.jsonl` — one row per coding decision, with route and rationale
6. `attestation.json` — from Lab 05
7. `VERIFY.md` — and it must actually work

## Exercises

1. **Shrink the sample.** Re-run `measure --val-n 50`. Look at what happens to the recall
   interval. Then compute the sample size you would need for ±5 points
   (`python3 -c "import sys;sys.path.insert(0,'../common');from metrics import sample_size;print(sample_size(0.05, p=0.13))"`).
   This is the exercise that changes how students talk about numbers.
2. **Move the auto-code threshold.** `--auto-threshold 0.70` then `0.95`. Watch the human
   queue and the elusion rate move in opposite directions. Which direction is cheap, and
   which direction is risky?
3. **Keyword vs LLM.** Run `classify --classifier keyword`, then `--classifier llm`, and
   `measure` after each. Where does the keyword baseline lose? (Look for paraphrase.)
   Where does it *win*? (Explainability — you can show a judge the matched term.)
4. **Break determinism.** Change the decoding seed in `../common/llm.py`, re-bundle, and
   `verify --replay`. Then put it back. This is what a model bump looks like.
5. **Hunt the privileged document.** Set `--auto-threshold 0.50` so more documents
   auto-code, and check `metrics.json` → `privilege.missed_by_classifier`. Write one
   sentence on why this is scored separately from recall.

## Troubleshooting

- **`No validation protocol`** — intentional. Run `protocol` first; read step 2.
- **`A protocol already exists`** — also intentional. `--force` exists but think first and
  keep the old version in version control.
- **Richness resolves only a handful of documents** — your catalog's `metadata.message_id`
  does not match the corpus labels. Re-generate the corpus and re-ingest; Message-IDs are
  random per generation.
- **`unparseable -> human: <all of them>`** — your model is not returning JSON. Use
  `--classifier keyword`, or a larger model, or strengthen the prompt. Do **not** coerce
  parse failures into "not responsive".
- **`recall: not computable`** — your validation sample contains no responsive documents.
  The sample is too small for this richness; that *is* the finding, and the sample-size
  table tells you what you needed.
- **`NOT CERTIFIED: UNPINNED model`** — on a hosted model this is permanent and correct:
  you cannot pin somebody else's model. That is a legal auto-fail in Module 7 and the
  strongest reproducibility argument for local inference.
- **`verify --replay` reports differences** — report them. Usual causes: a different
  quantization of the same model, a different runtime version, or a non-deterministic GPU
  backend. A difference is information, not a failure to hide.

## Review Questions

1. Why is elusion often more useful than recall, even though recall is the number you get
   asked for?
2. Your recall is 84% with a 95% interval of 71–92% and your target was 80%. What is the
   precise, honest sentence you write?
3. Two human reviewers agree 88% of the time. A partner demands 99% accuracy from your
   classifier. What do you say?
4. Why does changing the embedding model require re-validating a *responsiveness*
   classifier that never touches embeddings?
5. What exactly can you not promise about replaying a GPU inference run, and what can you
   promise instead?

---

## Teacher's Playbook

### Worked model answer

On the default corpus (1,196 documents) with the keyword baseline (the no-Ollama path),
expect approximately:

```
richness   : 6.5%  (95% CI 4.5%–9.4%) from 400 documents, seed 20261109
responsive : 26 of 400 sampled
to measure at +/-5 points you need ~94 documents reviewed
```

```
auto-coded responsive     : 15
auto-coded not responsive : 1125
privilege -> human        : 6
low confidence -> human   : 50
unparseable -> human      : 0
injection attempts flagged: 1
```

```
validation sample : 400 docs, seed 884422, blind
elusion sample    : 400 docs from the null set, seed 775511

recall    :  96.6%  (95% CI 82.8%–99.4%)   [28/29]
precision : 100.0%  (95% CI 87.9%–100.0%)  [28/28]
elusion   :   0.5%  (95% CI  0.1%– 1.8%)   [2/400]
richness  :   5.6%  (95% CI  4.5%– 7.1%)   [67/1192]

reviewer agreement : 92.0% (kappa 0.56) on 400 double-reviewed documents
elusion threshold 2.0% -> PASS
recall target 80% -> point estimate met; lower bound met
```

Then `bundle` and `verify --replay` → `certified: true`, `15 matched, 0 differed`.

**Use the high keyword recall, don't apologize for it.** The planted documents use the
negotiated terms almost verbatim, which is exactly why keyword culling worked for twenty
years — *when the terms are right*. Ask: *"what happens to this number when the custodian
writes 'hold harmless' instead of 'indemnify'?"* That question is the entire case for the
LLM, and it is the setup for exercise 3.

Three numbers in that output are worth stopping on.

**The elusion interval is 0.1–1.8% on a 400-document sample, and the upper bound clears
the 2.0% threshold.** That is a materially stronger position than a passing point estimate
with an upper bound above the line, and the only thing that bought it was sample size. Run
`richness` again and read its last line — *"to measure at ±5 points you need ~94
documents"* — then ask what ±1 point would cost. This is where students stop treating
sample size as a formality.

**Precision is 100% and that is not good news.** A classifier that never produces a false
positive on a 400-document sample is almost certainly too narrow; the elusion test is what
keeps you honest about the other side of that trade. Say so before a student writes "100%
precision" in a declaration.

**Agreement is 92.0% but kappa fell to 0.56** — on the smaller corpus the same agreement
rate gave kappa 0.69. Nothing about the reviewers changed; richness did. Kappa discounts
the agreement you would get by chance, and when 94% of documents are non-responsive,
agreeing on "not responsive" is cheap. The lesson: report both, and never report kappa
without the prevalence next to it.

### Live-demo script (about 12 minutes)

1. `richness`. *"Six and a half percent. In a real matter it is usually one to ten. That
   number just decided your whole budget — and the interval around it decided how much
   review you have to buy to defend it."*
2. `protocol`, then run it **again** on the projector and let it refuse.
   *"That refusal is the control. I cannot rewrite my acceptance threshold after seeing
   the result, because the tool will not let me, and that is the only reason you should
   believe the number I am about to show you."*
3. Try `classify` with the protocol deleted. It refuses. Same point, from the other side.
4. `measure`. Read the recall interval aloud, then the agreement ceiling.
   *"Ninety-two percent is what two humans manage. Hold that number when a partner asks
   for ninety-nine."*
5. `measure --val-n 50`. The interval explodes to roughly ±14 points.
   *"Same system. Same quality. Unusable number. Sample size is not a detail."*
6. `bundle`, then `verify --replay` → certified. Then break the weights hash with the
   one-liner from step 6 and re-verify → **auto-fail**.
   *"The bundle is only worth something because it refuses to certify."*

### Common mistakes + fixes

- **Choosing the threshold after seeing the result.** The headline failure, and the tool
  blocks it. Make sure they understand *why* it is blocked, not just that it is.
- **Re-sampling until the number is acceptable.** Explicitly forbidden in the protocol
  text. Worse than p-hacking in this context, and an opposing expert will find it in the
  seeds.
- **Reporting a bare point estimate.** Insist on intervals, every time, out loud.
- **Reporting F1 to a court.** It hides exactly the asymmetry that matters.
- **Defaulting parse failures to "not responsive."** Walk them through why this is the
  most dangerous line of code in the file.
- **Auto-coding privilege.** Non-negotiable. Some student will propose a 0.99 threshold;
  the answer is still no.
- **Forgetting that the artifact chain is the chain of custody.** A student who edits
  `catalog.jsonl` in place and re-bundles will fail the hash check. Good.

### Debrief Q&A

- *Who actually produces ground truth?* Reviewers, blind, on a random seeded sample. The
  labels shipping with the corpus stand in for that one step; everything else is real.
- *Why Wilson and not the normal approximation?* Legal samples are small and the
  proportions are near 0 or 1 — exactly where the normal approximation hands you a
  negative lower bound. `metrics.py` is 200 readable lines; show them.
- *Is 2% elusion the right threshold?* There is no legal magic number. What matters is
  that it was set in advance, is reasonable for the matter, and is disclosed.
- *Can we use continuous active learning (TAR 2.0)?* Yes, and then you inherit the
  documentation burden: the model changed under you during the review, so you must version
  it at each checkpoint. Make the trade deliberately.
- *What if the override column is empty across 200,000 documents?* Then the humans were
  rubber-stamping, and an opposing expert will read it exactly that way.

### What good looks like

A student has a certified bundle that replays; can state recall **with its interval** and
explain the difference between meeting a target at the point estimate and at the lower
bound; set their elusion threshold *before* measuring and can prove it with the protocol
hash; routed privilege to humans with no exceptions; and has personally watched `verify`
refuse to certify an unpinned model.

The sentence you are listening for at debrief: *"elusion 0.5%, 95% interval 0.1 to 1.8,
on a 400-document blind sample from the discard pile, against a threshold I set before I
ran it — and here is the protocol hash."*

---
