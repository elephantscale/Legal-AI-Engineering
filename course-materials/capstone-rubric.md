# Capstone Rubric

**Legal AI Engineering · Elephant Scale**

**Hand this out on Day 2 morning, not at the start of the capstone.** It should change what
students build, which it cannot do if they read it after building.

The capstone is one repository that **an engineer can clone and run, and a lawyer can read
and rely on.** It is assembled from Labs 02–07, which the students have already built. The
full assembly instructions are in `labs/08-Capstone/README.md`.

---

## Weights

| Dimension | Wt | What earns full marks |
|---|---|---|
| **Privacy — provable** | 25 | Local chat **and** embeddings **and** OCR; egress **enforced** and observed; attestation with 0 non-loopback connections, a tripwire showing blocked attempts, and an honest `scope_and_limits` |
| **Defensibility — measured** | 25 | Blind seeded sample; pre-registered, hashed protocol dated **before** the run; recall + elusion + precision each with an interval; the bundle replays via `VERIFY.md` |
| **Citations — enforced** | 15 | A verifier **in code**: no fabricated markers, no uncited claims, quotations verbatim; "not found in the provided documents" works and sometimes fires |
| **Ingestion — honest** | 15 | Recursive containers; OCR; a documented dedupe policy; a **non-empty, triaged** exception list; the producer's load file read and reconciled |
| **Shippability** | 10 | Runs offline from compose; checkpointed and resumable; digests pinned, not tags |
| **Score & governance** | 10 | SAIS-100 with the legal overlay, before and after one hardening change, no auto-fail; `DEFENSE.md` names real limits |

---

## Auto-fail, regardless of total

Any one of the four legal conditions:

- **LEGAL-A** — privileged content can reach a third party by any path, **or** egress was
  observed rather than enforced
- **LEGAL-B** — cross-matter leakage
- **LEGAL-C** — a production emitted without a recorded human approval
- **LEGAL-D** — the model cannot be pinned

A 96 with an auto-fail is a Do Not Deploy. Record the total anyway: it says how far the
system is from deployable once the condition is cleared.

---

## Band descriptors

| Band | What it looks like |
|---|---|
| **Excellent (90–100)** | Runs from a clean clone with one command. Every stage emits its artifact. `DEFENSE.md` answers all six questions, and question 6 names at least three specific limits with what they would measure. The student says "I don't know" to the right question and then says how they would find out. |
| **Strong (75–89)** | The pipeline and the artifacts are there; one or two artifacts are thin. The limits section is real but general. `VERIFY.md` works with one undocumented step. |
| **Adequate (60–74)** | It runs and produces a measurement, but something is asserted rather than shown — an attestation with no tripwire, a protocol whose date is not checkable, or a verifier in the prompt rather than in code. |
| **Not yet (<60)** | An empty exception list, no elusion measurement, a protocol written after the run, or a limits section that says "none". Each of these is a specific habit to fix, not a verdict on the engineering. |

---

## The three failures that cost marks most often

Check these first; it takes ninety seconds and it tells you most of what you need to know.

1. **An empty exception list.** It means documents were dropped silently, or nobody looked.
2. **No elusion measurement.** Recall alone says nothing about what was missed, and elusion is
   the cheaper number to sample.
3. **A protocol written after the classification run.** The tool refuses; people work around
   the tool. Check the dates, not the file's presence.

---

## `DEFENSE.md` — the differentiator

One page, six questions, in writing. This is the document that would go to a general counsel.

| # | Question | Full marks |
|---|---|---|
| 1 | **What did the system do?** | One paragraph a non-engineer follows. No architecture, no model names. |
| 2 | **Where did the documents go?** | Every hop — extraction, OCR, embeddings, chat, logs. Cites `attestation.json` **and says what it covers**. |
| 3 | **How good is it?** | Recall, elusion, precision, with intervals. Cites `metrics.json`. Names the threshold and when it was fixed. |
| 4 | **Why was this document coded this way?** | One real document by id, with rationale, citations, and the rendered prompt from `runs/<run-id>/prompts/`. |
| 5 | **How do I re-run it?** | Points at `VERIFY.md`. States which bar — *same determinations* or *bit-exact* — and why. |
| 6 | **What are the limits?** | Where it is weak, what it cannot prove, what a human must check. |

> **Question 6 is worth more than questions 1–5 combined.** "No significant limitations" fails
> the module, not the engineering. A student with a mediocre pipeline and an excellent limits
> section has understood this course better than the reverse, and should be graded that way.

---

## Grading sequence (about twelve minutes per capstone)

1. **Exception list.** Non-empty? Does every row have a next step? *(10 seconds, highest
   signal)*
2. **`DEFENSE.md` question 6.** Read it before anything else you read. *(1 minute)*
3. **`metrics.json`.** Three metrics, three intervals, a sample size, a protocol hash.
4. **`validation/protocol.md` dates** against the run window. Order, not presence.
5. **`attestation.json`.** `egress_policy`, non-loopback count, tripwire, and a non-empty
   `scope_and_limits`.
6. **One command from a clean directory.** Does it run?
7. **`VERIFY.md`** on at least two capstones in front of the room — one you expect to work,
   one at random.
8. **`sais100-score.json`.** Two scores, one documented hardening change, zero auto-fails.

---

## The defense round

Fifteen minutes each way, in pairs. Each student is opposing counsel's expert and must break
their partner's system — politely, specifically, and **in writing**.

1. "Show me your exception list. What happened to those documents?"
2. "What is your recall, and what is the confidence interval?"
3. "Who chose the validation threshold, and when?"
4. "Walk me through why document `<id>` was coded responsive."
5. "Prove no document content left this machine. What exactly does your monitor cover?"
6. "Re-run this review in front of me."
7. "What model version? Can you still get those weights?"

Each student hands their partner their **three weakest answers in writing**, then they swap.
Grade the questions asked as well as the answers given — a student who finds a real hole in a
partner's system has demonstrated the course's actual skill.

---

## Certification

The course awards the **Legal AI Engineer Certificate** (Elephant Scale). It requires
attendance, the module labs, and a capstone that **passes its own `VERIFY.md`** and trips
**no** legal auto-fail.

Note what is *not* on that list: the rubric score. A capstone can score 72 and certify, or
score 94 and not. The score measures how well the system is built; the three requirements
measure whether it does what its author says it does. Those are different questions, and only
the second one can be checked by someone who was not in the room.

The student also leaves with the repository, which demonstrates that they can build a
legal-AI system that is private, measured and reproducible, and that they can defend it in
writing. The certificate records the bar; the repository is how they show it — sooner or later
somebody will skip the certificate and ask them to re-run their review in front of them.

Issuance mechanics, the roster record, and the pre-decided borderline cases are in
[Lab 08's Teacher's Playbook](../labs/08-Capstone/README.md#issuing-the-certificate).

---

## Instructor notes

- **Enforce the silent writing block** (45 minutes for `DEFENSE.md` and `README.md`).
  Engineers will polish code until the clock runs out and then hand in a system nobody can
  explain — precisely the failure the course exists to prevent.
- **An empty `scope_and_limits` is worse than a missing attestation.** The second is
  incomplete; the first is an overclaim.
- When two capstones are close, prefer the one whose author can name the weakness. Controls
  can be fixed in a week. In a deposition you have the author, not the week.
- The strongest signal is not any artifact. It is whether the student says "I don't know" to
  the right question and then says what they would measure to find out.

---

*Lab 08 · `labs/08-Capstone/README.md` · see also [defensibility-checklist.md](defensibility-checklist.md) and [sais-100-legal-overlay.md](sais-100-legal-overlay.md)*
