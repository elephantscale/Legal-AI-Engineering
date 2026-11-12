# Course Materials

**Legal AI Engineering · Elephant Scale**

Nine documents. These are the artifacts students keep after the slides are closed and the
`work/` directory is deleted — the reusable paperwork behind the course's two claims:

1. **"Nothing left the building."** — confidentiality and privilege
2. **"Here is exactly what the system did, and you can re-run it."** — defensibility

Every one of them is designed to be used on a real matter, not read once. Where a document
has running code behind it, the code is named.

---

## The documents

| Document | Use it | When | Code behind it |
|---|---|---|---|
| **[legal-ai-design-canvas.md](legal-ai-design-canvas.md)** | Nine boxes to fill before the first commit. Forces the four leak points, the model pin, the measurement plan and the limits to be decided while they are still cheap. | **Before** you build | — |
| **[defensibility-checklist.md](defensibility-checklist.md)** | Nine sections, each line a question somebody will ask under oath, each with the file that answers it. | During, and before you ship | the whole pipeline |
| **[tar-metrics-cheatsheet.md](tar-metrics-cheatsheet.md)** | Recall / elusion / precision / richness, the sample-size table, Wilson intervals, and the sentences that get you in trouble. | Module 6 onward, permanently | `labs/common/metrics.py` |
| **[privilege-and-egress-attestation.md](privilege-and-egress-attestation.md)** | The machine record plus the human form that supports "nothing left the building" — including the scope section that keeps it honest. | Every run on a real matter | `labs/common/egress.py` |
| **[reproducibility-manifest-template.md](reproducibility-manifest-template.md)** | The one file that makes "we can re-run this" checkable. Every pin, plus the `VERIFY.md` skeleton. | Every run you may have to defend | `labs/common/bundle.py` |
| **[sais-100-legal-overlay.md](sais-100-legal-overlay.md)** | The evidence map for all 18 SAIS-100 questions, the four legal auto-fails, and the verified-assessment rules. | Module 7, and again at Module 12 | `labs/07-Score-and-Package/sais100.py`, `labs/12-Governance-Audit/audit.py` |
| **[sais-100-framework-mapping.md](sais-100-framework-mapping.md)** | Every SAIS-100 category translated into NIST AI RMF, ISO/IEC 42001, the EU AI Act and the governing legal authority — so you can answer a security reviewer in their own vocabulary. | Module 7, and whenever someone outside the room asks | `sais-100-legal-overlay.md` |
| **[capstone-rubric.md](capstone-rubric.md)** | How the capstone is graded, the band descriptors, the grading sequence, and the defense round. | **Day 2 morning** — not at the start of the capstone | — |
| **[legal-ai-job-market.md](legal-ai-job-market.md)** | Nine postings at six employers: which titles are J.D.-gated, which are not, what each pays, what they ask for that you built, and the three gaps this course does not cover. | **Module 1** — hand it out with the market-map slide | — |

**The job-market handout serves neither claim, deliberately.** Every other document here is
evidence for a court or a client. That one is for the student's own career, and it is in this
directory because it is the question they ask in the first hour and it deserves an
evidence-backed answer rather than an encouraging one. It is the companion to the Module 1
slide **What the Postings Actually Say**, and it is a dated snapshot — re-read
`job-market-research.md` before teaching from it.

---

## The order they are used in

```text
          BEFORE                    DURING                        BEFORE YOU SHIP
  ┌─────────────────────┐   ┌──────────────────────┐   ┌───────────────────────────┐
  │ design canvas       │──▶│ defensibility        │──▶│ reproducibility manifest  │
  │  the 9 boxes        │   │   checklist          │   │ privilege attestation     │
  │  (box 9 first)      │   │ TAR metrics          │   │ SAIS-100 legal overlay    │
  └─────────────────────┘   └──────────────────────┘   └───────────────────────────┘
                                                                     │
                                                        capstone rubric (graded)
```

The canvas and the rubric are the bookends. Fill the canvas before writing code; read the
rubric before assembling the capstone. Both are more useful early than they look.

---

## Two notes for the instructor

**Hand out the rubric on Day 2 morning.** A rubric read after the work is done is a grading
instrument. A rubric read before it is a design document, and it changes what students build —
which is the point.

**The canvas is worth twenty minutes of Day 1.** Students who fill box 9 ("what this system
cannot prove") on Day 1 write a materially better `DEFENSE.md` on Day 2. It is the single
highest-leverage twenty minutes in the course.

---

## On SAIS-100

SAIS-100 is the Elephant Scale Secure AI Score — six categories, three questions each, 0–3,
weighted to 100. This course **does not fork it.** The categories, weights, anchors and
verdict bands are the standard framework. The legal overlay adds the evidence each question
is answered from, four auto-fail conditions specific to legal matters, and the rule that
`UNVERIFIED` is a third answer worth neither 0 nor 3.

---

## Reuse

These are Elephant Scale course materials. Students may use them on their own matters and
inside their own organizations — that is what they are for. The attestation form in
particular is meant to be adapted: the sections are the point, not the layout.

**Nothing in this directory contains real case data.** The corpus the labs use is synthetic,
generated by `labs/assets/make_corpus.py`, and that rule holds for anything added here later.

---

*© Elephant Scale · LEGAL-AI-ENG-2026*
