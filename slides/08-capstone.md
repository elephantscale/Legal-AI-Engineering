# Capstone — A Private, Defensible Legal-AI Application

Elephant Scale

---

## What You Are Building

**End to end, on your own machine, with the network off if you like:**

1. **Ingest** a messy corpus — containers, email, scans, load files — with an exception list
2. **Search** it — real eDiscovery queries, a hit report, families not orphans
3. **Answer questions** over it with **citations**, using a **local** model
4. **Prove** nothing left the building — `attestation.json`
5. **Measure** a review against blind ground truth — recall, elusion, precision, with CIs
6. **Package** it — reproducibility bundle, SAIS-100 score, container that runs offline

> You are not building a demo. You are assembling the portfolio project that **is** the
> legal-engineer job description.

Notes:

The capstone is integrated across Day 2 rather than bolted on at the end — students have
been building it since Lab 02. This deck is the framing, the rubric, and the defense.

Say the last line plainly. Students should leave with a repository they can show a hiring
manager or a client, and the six bullets above are, nearly verbatim, what a legal-tech
engineering interview asks about.

---

## The Deliverable: One Repository

```text
my-legal-ai/
  README.md                      <- what it does, how to run it, what it claims
  docker-compose.yml             <- runs offline; internal network; pinned digests
  run_matter.py                  <- the driver: ingest -> ... -> bundle
  work/                          <- stage artifacts, checkpointed
  case-snapshot-<matter>/
    manifest.json                <- every pin
    corpus/{catalog,exceptions}.jsonl
    runs/<run-id>/{prompts/,responses.jsonl,retrieval.jsonl}
    decisions.jsonl
    validation/{protocol.md,ground_truth.jsonl,metrics.json}
    attestation.json
    VERIFY.md
  sais100-score.json             <- before and after one hardening change
  DEFENSE.md                     <- your one-page defense (next slide)
```

* `VERIFY.md` must actually work. Someone else will run it — that is the point.

Notes:

Insist on `README.md` and `DEFENSE.md`. Engineers will ship the code and skip the prose, and
the prose is the differentiator in this field. A system nobody can explain is not defensible
regardless of how good it is.

---

## DEFENSE.md — Your One Page

Answer these seven, in writing, in one page. This is the document you would hand a GC.

1. **What did the system do?** One paragraph a non-engineer can follow.
2. **Where did the documents go?** Every hop. Cite `attestation.json`.
3. **How good is it?** Recall, elusion, precision, **with intervals**. Cite `metrics.json`.
4. **Why was this document coded this way?** Pick one real document. Show the rationale,
   the citations, and the rendered prompt.
5. **How do I re-run it?** Point at `VERIFY.md`. State which bar you claim — *same
   determinations* or *bit-exact*.
6. **What are the limits?** Where it is weak, what it cannot prove, what a human must check.
7. **Would you build this, or buy it?** Which parts you would keep, replace or integrate —
   and **what you would make the vendor prove** to answer 2 and 3 for you.

> Question 6 is worth more than questions 1–5 combined. A system whose author can name its
> limits is a system someone can rely on.

Notes:

Question 7 is the one they will use first. Nobody's first job is to rebuild Relativity; it is
to decide what to buy and then make it behave. Say out loud that they cannot evaluate a
product from this room and are not being asked to — what they can write, having built the
thing, is the list of questions a vendor has to answer before their component stands where
yours stands. Point back at Module 1's Build vs. Buy slide: the usual answer is both, and the
part that has to be yours is the part that touches the data.

Grade question 6 hardest. Students who write "no significant limitations" have failed the
module, not the engineering. The honest answers in the room usually include: OCR confidence,
local model quality delta, sample size, non-determinism on GPU, and the monitor's scope.

---

## Capstone Rubric

| Dimension | Wt | What earns full marks |
|---|---|---|
| **Privacy — provable** | 25 | Local chat **and** embeddings **and** OCR; egress enforced *and* observed; attestation with 0 non-loopback and honest scope |
| **Defensibility — measured** | 25 | Blind seeded sample; pre-registered protocol; recall + elusion + precision with CIs; bundle replays via `VERIFY.md` |
| **Citations — enforced** | 15 | Verifier in code: no fabricated markers, no uncited claims, quotes verbatim; "not found" works |
| **Ingestion — honest** | 15 | Recursive containers; OCR; documented dedupe policy; **non-empty, triaged exception list**; load file read |
| **Shippability** | 10 | Runs offline from compose; checkpointed and resumable; pinned digests |
| **Score & governance** | 10 | SAIS-100 with legal overlay, before/after, no auto-fail; `DEFENSE.md` names real limits and ends with build/buy/integrate |

**Auto-fail (regardless of total):** any of the four legal auto-fails from Module 7 —
case content can leave by an unapproved or unenforced path; cross-matter leakage; production
without recorded approval; the model cannot be pinned.

> Full marks on the first two dimensions is the whole course. The other four are how you
> keep them.

Notes:

Hand this out at the start of Day 2, not at the capstone. Students who know the rubric on
Day 2 morning build toward it through every lab, which is the intended behavior.

Note the weighting: the two course claims are worth 50 together. Ingestion is 15 despite
being the most work, because without the privacy and measurement layers a great pipeline is
just a pipeline.

---

## Extensions, If You Have Time

Pick one. They map to the Deep Dive and the electives.

* **Investigations** — entities, a reconstructed email thread, a timeline *(Module 9)*
* **Agentic** — a multi-step workflow with a real human checkpoint *(Module 10)*
* **Scale** — containerize the ingest workers and scale across cores *(Module 11)*
* **Governance audit** — a full SAIS-100 verified assessment with evidence for every
  sub-score *(Module 12)*
* **Attribution checking** — use the local model as a judge: does chunk `[n]` actually
  *support* this sentence? Measure how often your citations are merely *plausible*
* **Hybrid tuning** — sweep the RRF constant and top-k; show the recall curve

> The attribution-checking extension is the most interesting unsolved problem in this
> course. If something in the room is going to turn into a product, it is that.

Notes:

The attribution extension is genuinely research-adjacent and strong students love it. Be
honest that LLM-as-judge attribution checking is itself imperfect, and that measuring *how*
imperfect is the interesting part.

---

## The Defense Round

Fifteen minutes each, in pairs. **You are opposing counsel's expert.** Your job is to break
your partner's system — politely, specifically, and in writing.

Ask these, in this order:

1. "Show me your exception list. What happened to those documents?"
2. "What is your recall, and what is the confidence interval?"
3. "Who chose the validation threshold, and when?"
4. "Walk me through why document `DOC-000417` was coded responsive."
5. "Prove no document content left this machine. What exactly does your monitor cover?"
6. "Re-run this review in front of me."
7. "What model version? Can you still get those weights?"
8. "What would you buy instead of this — and what would you make the vendor prove?"

Hand your partner their three weakest answers, in writing.

> You will be asked these questions for the rest of your career in this field. Better in
> here first.

Notes:

This exercise is the highest-value thirty minutes of the course and students consistently
rate it so. Insist on the adversarial posture — politeness without pressure teaches nothing.

Question 3 catches the most people. Question 6 catches the rest. Keep the pairs mixed between
software-background and legal-background students if you have both; they ask completely
different questions and each finds what the other missed.

---

## What You Walk Out With

* The **Elephant Scale Legal AI Engineer Certificate**
* **The capstone repository** — the evidence behind it, and the thing a hiring manager reads
* Certification requires:
  - minimum attendance
  - completion of the module labs
  - a capstone that passes its own `VERIFY.md` and trips **no** legal auto-fail
* What it demonstrates: you can build a legal-AI system that is **private, measured, and
  reproducible** — and you can defend it in writing

> The certificate records that you cleared the bar. The repository is how you prove it, because
> the first thing anyone serious will ask is that you re-run your review in front of them.

Notes:

Say the requirements out loud before the capstone session, not after it. The bar is objective
on purpose — `VERIFY.md` either replays or it does not, and the four legal auto-fails either
trip or they do not — which is what keeps this certificate worth having. Do not award it on
effort or on attendance alone; the moment it is handed out for showing up, it is worth nothing
to the person who earned it properly.

Issuance mechanics and the roster record are in Lab 08's Teacher's Playbook.

---

## Where This Fits

* The **legal-vertical track** of the Elephant Scale Secure AI Learning Path
* Pairs with:
  - **Building Secure AI Applications** — the builder's security course (injection, output
    handling, RAG security, agent safety). Your corpus is written by adversaries; take it.
  - **AI Security for Security Teams** — the defender's chair, same threat model
  - **Building Agentic AI** — if you want more than Module 10 gives you on orchestration
* Applies **SAIS-100** in its governance work, with the legal overlay you now own
* **FreeEed** — the open-source reference system; go install it and point it at your own data,
  on your own machine, which is the entire point

> Two days ago you could build a legal-AI system. Now you can **defend** one. That is the
> job, and that is the difference.

---

## Thank You

Keep three things:

* The **four leak points** — OCR, embeddings, chat, logs. Count them every time.
* **Recall and elusion** — and the confidence interval. No bare point estimates.
* **"Can you prove it?"** — asked of your own work, before someone else asks it of you.

<img src="../images/practice.png" style="width:55%;"/>

Notes:

Close on the three. If a student remembers nothing else in a year, those three are the ones
that keep them out of trouble and make them money.

Then do the round-the-room: read back the "what I want to walk out with" answers captured on
Day 1 and check them off. Cheapest and most effective close there is.
