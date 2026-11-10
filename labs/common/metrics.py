"""metrics.py — the numbers that hold up in court (Module 6).

Recall, elusion, precision, richness — each with a Wilson confidence interval, because a
point estimate with no error bars is a number pretending to be a fact.

    from metrics import confusion, recall, elusion, precision, richness, sample_size

Everything here is deliberately small and readable. You should be able to check it by
hand, which is the only reason to trust a metric you are going to put in a declaration.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ------------------------------------------------------------------ interval maths
def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion. 95% by default.

    Preferred over the textbook normal approximation because legal samples are small and
    the proportions are often near 0 or 1 — exactly where the normal approximation goes
    embarrassingly wrong (it will happily hand you a negative lower bound).
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def sample_size(margin: float, *, p: float = 0.5, z: float = 1.96,
                population: int | None = None) -> int:
    """How many documents must a human review to get +/- `margin` at 95% confidence?

    p=0.5 is the conservative worst case and the right default when you do not yet know
    the proportion. Pass your richness estimate for a smaller, still-honest sample.

    >>> sample_size(0.05)
    385
    >>> sample_size(0.05, p=0.04)
    60
    """
    n = (z * z * p * (1 - p)) / (margin * margin)
    if population:                       # finite population correction
        n = n / (1 + (n - 1) / population)
    return math.ceil(n)


# ------------------------------------------------------------------------ confusion
@dataclass
class Confusion:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    @property
    def n(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    def as_dict(self) -> dict:
        return {"tp": self.tp, "fp": self.fp, "fn": self.fn, "tn": self.tn, "n": self.n}


def confusion(predicted: dict[str, bool], truth: dict[str, bool]) -> Confusion:
    """Build the matrix over the documents present in BOTH maps.

    `truth` is the blind human sample, so it is normally much smaller than `predicted`.
    Only the overlap is scored — and that is why the sample has to be *random*, or the
    overlap is not representative of anything.
    """
    c = Confusion()
    for doc_id, actual in truth.items():
        if doc_id not in predicted:
            continue
        pred = predicted[doc_id]
        if pred and actual:
            c.tp += 1
        elif pred and not actual:
            c.fp += 1
        elif not pred and actual:
            c.fn += 1
        else:
            c.tn += 1
    return c


# -------------------------------------------------------------------------- metrics
def _rate(num: int, den: int, label: str) -> dict:
    lo, hi = wilson(num, den)
    return {
        "metric": label,
        "value": (num / den) if den else None,
        "numerator": num,
        "denominator": den,
        "ci95": [lo, hi] if den else None,
        "note": None if den else "not computable: denominator is zero",
    }


def recall(c: Confusion) -> dict:
    """TP / (TP + FN) — of all the responsive documents, what fraction did we find?

    THE eDiscovery metric. Note the denominator: you cannot get it from your own output,
    only from a sample of what you rejected. That is why elusion exists.
    """
    return _rate(c.tp, c.tp + c.fn, "recall")


def precision(c: Confusion) -> dict:
    """TP / (TP + FP) — of what we called responsive, how much was. Your review cost."""
    return _rate(c.tp, c.tp + c.fp, "precision")


def elusion(c: Confusion) -> dict:
    """FN / (FN + TN) — of what we set aside, what fraction was actually responsive.

    Measured on a random sample of the DISCARD pile. This is the number that directly
    tests "we did not throw away anything important", and unlike recall its denominator
    is a sample you can actually draw.
    """
    return _rate(c.fn, c.fn + c.tn, "elusion")


def richness(truth: dict[str, bool]) -> dict:
    """Prevalence of responsive documents in a random sample of the whole corpus.

    Measure this FIRST. It sets your sample sizes, your cost model, and the honest answer
    to "should we even use AI on this corpus?"
    """
    resp = sum(1 for v in truth.values() if v)
    return _rate(resp, len(truth), "richness")


def f1(c: Confusion) -> dict:
    """Harmonic mean of precision and recall.

    Useful for tuning. **Do not report this to a court**: it hides the asymmetry between
    a false positive (wasted money) and a false negative (a document you never produced).
    """
    p = c.tp / (c.tp + c.fp) if (c.tp + c.fp) else None
    r = c.tp / (c.tp + c.fn) if (c.tp + c.fn) else None
    val = (2 * p * r / (p + r)) if (p and r) else None
    return {"metric": "f1", "value": val, "ci95": None,
            "note": "for tuning only; do not report in a validation declaration"}


def agreement(a: dict[str, bool], b: dict[str, bool]) -> dict:
    """Reviewer-vs-reviewer agreement on the overlap, plus Cohen's kappa.

    This is your CEILING. If two humans agree only 85% of the time, a system cannot be
    held to 100%. Say so before anyone demands perfection.
    """
    keys = set(a) & set(b)
    n = len(keys)
    if not n:
        return {"metric": "agreement", "value": None, "n": 0,
                "note": "no overlapping documents — overlap your reviewers on purpose"}
    same = sum(1 for k in keys if a[k] == b[k])
    po = same / n
    pa = sum(1 for k in keys if a[k]) / n
    pb = sum(1 for k in keys if b[k]) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (po - pe) / (1 - pe) if pe != 1 else None
    lo, hi = wilson(same, n)
    return {"metric": "agreement", "value": po, "ci95": [lo, hi], "n": n,
            "cohens_kappa": kappa,
            "note": "this is the ceiling for any automated classifier on this task"}


def report(predicted: dict[str, bool], truth_sample: dict[str, bool],
           *, discard_sample: dict[str, bool] | None = None,
           richness_sample: dict[str, bool] | None = None,
           second_reviewer: dict[str, bool] | None = None) -> dict:
    """Assemble the full validation block for `metrics.json`.

    truth_sample     a blind random sample over the WHOLE corpus (for recall/precision)
    discard_sample   a blind random sample of the documents the system REJECTED (elusion)
    richness_sample  a random sample used to estimate prevalence
    second_reviewer  overlapping calls from a second human, for the agreement ceiling
    """
    c = confusion(predicted, truth_sample)
    out: dict = {
        "confusion": c.as_dict(),
        "recall": recall(c),
        "precision": precision(c),
        "f1": f1(c),
    }
    if discard_sample:
        cd = confusion(predicted, discard_sample)
        out["elusion"] = elusion(cd)
        out["elusion_confusion"] = cd.as_dict()
    else:
        out["elusion"] = {"metric": "elusion", "value": None,
                          "note": "NOT MEASURED — no discard sample was drawn. The "
                                  "central claim of a defensible review is unsupported."}
    if richness_sample:
        out["richness"] = richness(richness_sample)
    if second_reviewer:
        out["reviewer_agreement"] = agreement(truth_sample, second_reviewer)
    return out


# ----------------------------------------------------------------------------- demo
if __name__ == "__main__":
    import json
    print("Sample sizing (95% confidence):")
    for m in (0.10, 0.05, 0.03, 0.02):
        print(f"  +/-{m:.0%}  worst case p=0.5 -> {sample_size(m):>5} docs"
              f"   |  p=0.04 -> {sample_size(m, p=0.04):>4} docs")

    truth = {f"D{i}": (i % 25 == 0) for i in range(400)}         # ~4% richness
    pred = {k: (v if i % 7 else not v) for i, (k, v) in enumerate(truth.items())}
    print("\nWorked example on a synthetic 400-document sample:")
    print(json.dumps(report(pred, truth, discard_sample={k: v for k, v in truth.items()
                                                         if not pred[k]},
                            richness_sample=truth), indent=2))
