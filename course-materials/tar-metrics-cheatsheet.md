# TAR Metrics — Cheat Sheet

**Legal AI Engineering · Elephant Scale · the one page to keep on the desk**

One page. The definitions, the arithmetic, the sample sizes, and the sentences that get you
in trouble.

---

## The confusion matrix, in legal words

|  | **truly responsive** | **truly not responsive** |
|---|---|---|
| **you coded responsive** | TP — correctly produced | FP — over-produced (cost, and possible privilege risk) |
| **you coded not responsive** | **FN — missed. This is the one that ends careers.** | TN — correctly withheld |

Everything below is four numbers and a sample.

---

## The four metrics

| Metric | Formula | The question it answers | Who asks |
|---|---|---|---|
| **Recall** | TP / (TP + FN) | *Of everything responsive, what fraction did we find?* | Opposing counsel, the court |
| **Precision** | TP / (TP + FP) | *Of what we produced, what fraction should have been?* | Your client, paying for review |
| **Elusion** | FN / (FN + TN) | *Of what we **discarded**, what fraction was responsive?* | The expert who will cross-examine you |
| **Richness / prevalence** | (TP + FN) / N | *How much responsive material is in here at all?* | You, **before** anything else |

> **Recall and elusion are not the same number restated.** Recall is measured on the
> responsive set; elusion is measured on the **discard pile**. Elusion is the direct estimate
> of how much you are about to not produce, and it is the number you can actually sample
> cheaply. Report both.

### Also worth knowing

- **F1** = 2·(P·R)/(P+R). A convenience. Nobody in a courtroom asks for F1, and averaging a
  recall you must defend with a precision you merely prefer is a strange thing to do.
- **Depth for recall (DFR)** — how far down the ranked list you had to go. A cost measure,
  not a quality measure.
- **Cohen's kappa** — reviewer-vs-reviewer agreement corrected for chance:
  κ = (p_o − p_e)/(1 − p_e). Use it on double-reviewed documents, never on model-vs-truth.

---

## Richness first, always

Richness drives everything: sample sizes, whether TAR is worth running, and whether your
recall estimate will have a usable interval. Estimate it on a random sample **before** you
build a classifier.

```
responsive in sample / sample size   →   richness
richness × N                         →   expected responsive population
```

At 2% richness in 1,000,000 documents there are ~20,000 responsive documents, and a
400-document random sample will contain about **eight** of them. You cannot measure recall to
±5% from eight documents, and no amount of modelling fixes that. Low richness is a
**sampling** problem, so it gets a sampling answer: stratify, or sample the discard pile
directly (elusion), or accept a wide interval and say so.

---

## Sample size: how many documents a human must read

For a proportion at **95% confidence**, n = z²·p(1−p)/margin², z = 1.96.

| ± margin | p=0.50 *(worst case)* | p=0.20 | p=0.10 | p=0.04 | p=0.01 |
|---|---|---|---|---|---|
| **±10%** | 97 | 62 | 35 | 15 | 4 |
| **±5%** | 385 | 246 | 139 | 60 | 16 |
| **±3%** | 1,068 | 683 | 385 | 164 | 43 |
| **±2%** | 2,401 | 1,537 | 865 | 369 | 96 |
| **±1%** | 9,604 | 6,147 | 3,458 | 1,476 | 381 |

Two things to read off that table:

1. **p = 0.5 is the conservative default** when you do not yet know the proportion — which is
   exactly why you measure richness first. Knowing p ≈ 0.04 takes a ±5% sample from 385
   documents to **60**.
2. **Precision costs little; tight precision costs a lot.** Going from ±5% to ±1% is a
   25-fold increase in human review. Choose the margin deliberately and write it in the
   protocol, because the alternative is choosing it after you see the result.

**Finite population correction** — divide by (1 + (n−1)/N). It matters when the sample is a
meaningful fraction of the collection: ±5% at p=0.5 needs 385 documents from a million, but
only **291** from 1,196.

---

## Confidence intervals: use Wilson

Normal-approximation intervals break at the edges — a 0/50 sample gives you the interval
[0.0, 0.0], which claims certainty from fifty documents. The **Wilson score interval**
behaves at 0 and at 1, and it is four lines of code:

```python
def wilson(successes, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)                 # no data is not a narrow interval
    p = successes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))
```

> A point estimate with no interval is not a measurement. It is a number you found.

---

## What to say, and what not to say

| Don't say | Say |
|---|---|
| "Recall is 82%." | "Recall is **82%, 95% CI [74%, 88%]**, on a 300-document blind random sample drawn 2026-03-04 under the protocol fixed 2026-03-01 (sha256 `a1b2…`)." |
| "The model is 94% accurate." | Accuracy is meaningless at low richness — calling everything non-responsive scores 98% at 2% richness. Give recall, elusion, precision. |
| "We achieved 80% recall, the accepted standard." | There is no numeric standard in the rules. Proportionality is the standard; your number has to be reasonable **for this matter** and you have to show how you got it. |
| "Validation showed the threshold was right." | Name who fixed the threshold and **when** relative to the run. A threshold chosen after seeing the result is not a threshold. |
| "The sample was random." | State the frame, the method, the seed, and who could see the labels. "Random" without a frame is a claim, not a method. |

---

## The five facts that travel with every recall number

Send these five together or send none of them:

1. the **point estimate**
2. the **confidence interval** and confidence level
3. the **sample size** and how the sample was drawn
4. the **date the protocol was fixed** — before the run
5. the **protocol hash**

Anyone who emails a client one number has unlearned the module.

---

## Ordering (this is the whole discipline)

```
1. richness        estimate prevalence on a random sample
2. protocol        pre-register: thresholds, sample sizes, stop rule, who signs — then HASH it
3. classify        run the system
4. measure         recall + elusion + precision, each with an interval, against BLIND truth
5. bundle          protocol, sample, labels, metrics, pins — one directory
6. verify          someone else re-runs it
```

Steps 1 and 2 come before step 3. Every defensibility failure in this field is a reordering
of that list.

> **Blind means blind.** If the person coding documents can see the ground-truth labels, you
> have measured agreement with yourself. Keep the labels in a directory the pipeline cannot
> read and do not open it before step 4.

---

## Validation protocol — the minimum contents

A protocol a court can read is one page and contains:

- the **matter**, the **date**, and the **named person** who fixed it
- the **responsiveness definition** being applied, verbatim
- the **acceptance threshold** and what happens if it is missed
- the **sampling frame**, method, size and seed, for each of validation and elusion
- who holds the ground truth and how blindness is maintained
- the **stop rule** — when review ends, decided in advance
- **what the claim will not cover**

Then hash it and store the hash with the result. The hash is what makes "fixed in advance"
checkable rather than asserted.

---

*Module 6 · Labs 05–06 · `labs/05-Defensible-Review/` and `labs/common/metrics.py`*
