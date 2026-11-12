# Lab 08 — Capstone

**Integrated across Day 2 · the deliverable you keep**

This is not a new lab. You have been building it since Lab 02. This file is the
assembly instructions, the rubric you are graded against, and the defense round.

Read the rubric **now**, before you start assembling. It is the whole point of the
exercise and it should change what you do in the next two hours.

---

## What you are assembling

One repository that an engineer can clone and run, and that a lawyer can read and rely on.

```text
my-legal-ai/
  README.md                      <- what it does, how to run it, what it claims
  DEFENSE.md                     <- your one page (below). This is the differentiator.
  docker-compose.yml             <- runs offline; internal network; pinned digests   [Lab 07]
  Dockerfile                                                                      [Lab 07]
  run_matter.py                  <- the driver: ingest → … → bundle
  sais100.py
  common/                        <- llm.py, egress.py, metrics.py, bundle.py
  pipeline/                      <- your stage code from Labs 02–06 (+ 07 if you did it)
  work/                          <- stage artifacts, checkpointed (gitignored)
  case-snapshot-<matter>/
    manifest.json                <- every pin
    corpus/{catalog,exceptions}.jsonl
    runs/<run-id>/{prompts/,responses.jsonl,retrieval.jsonl}
    decisions.jsonl
    validation/{protocol.md,ground_truth.jsonl,metrics.json}
    attestation.json
    VERIFY.md
  production/VOL001/{VOL001.dat,TEXT/,manifest.json}                              [Lab 07]
  sais100-score.json             <- before and after one hardening change
```

Three rules about that tree:

0. **The `[Lab 07]` lines are there only if you did Lab 07.** Module 7 is taught on Day 3,
   so a condensed two-day class may not have reached it. Without it you have no document
   production set and no container — the capstone and the certificate do not require either, because the capstone
   drives Labs 02–06 itself and produces its own SAIS-100 score. Say so in `DEFENSE.md`
   rather than leaving a grader to wonder.

1. **`VERIFY.md` must actually work.** Someone else will run it. Test it from a clean
   checkout in a different directory, with the corpus path as the only thing you change.
2. **Nothing in `work/` or `case-snapshot-*/` is committed.** They are outputs. Your
   `.gitignore` says so, and the fact that it says so is itself a defensibility signal —
   it means you know which files are evidence and which are derived.

---

## Assembly, step by step

### 1. Make it one command

```bash
python3 run_matter.py --corpus ./corpus --work ./work
```

If a grader has to run six scripts in the right order, you have not shipped a system. Lab
07's `run_matter.py` is the template; copy it and point it at your own stage modules.

### 2. Make it run with the network off

```bash
# Linux
sudo ip link set <iface> down          # or: nmcli networking off
python3 run_matter.py --corpus ./corpus --work ./work-offline
```

Everything must complete. If a stage fails, you have a dependency on something outside the
building and you have found it the good way.

### 3. Produce the two scores

```bash
python3 sais100.py --work ./work --save-baseline
# harden exactly ONE thing, and write down which
python3 sais100.py --work ./work --delta --out sais100-score.json
```

### 4. Write `DEFENSE.md`

One page. Six questions. In writing. This is the document you would hand a general counsel.

1. **What did the system do?** One paragraph a non-engineer can follow. No architecture
   diagrams, no model names.
2. **Where did the documents go?** Every hop — extraction, OCR, embeddings, chat, logs.
   Cite `attestation.json` and say what it covers.
3. **How good is it?** Recall, elusion, precision, **with intervals**. Cite `metrics.json`.
   Name the threshold and say when it was fixed.
4. **Why was this document coded this way?** Pick one real document by id. Show the
   rationale, the citations, and the rendered prompt from `runs/<run-id>/prompts/`.
5. **How do I re-run it?** Point at `VERIFY.md`. State which bar you claim — *same
   determinations* or *bit-exact* — and why.
6. **What are the limits?** Where it is weak, what it cannot prove, what a human must check.

> Question 6 is worth more than questions 1–5 combined. A system whose author can name its
> limits is a system someone can rely on. "No significant limitations" is a failing answer.

Honest answers to question 6 from past rooms: OCR confidence on the degraded scans; the
quality gap between a local 8B model and a frontier model on long contract reasoning;
sample size (a 400-document sample cannot resolve a 1% elusion difference); GPU
non-determinism, which is why the claim is *same determinations* and not *bit-exact*; and
the monitor's scope — it observes this process, not the whole host.

### 5. Write `README.md`

What it does, how to run it, what it claims. Three sections, one screen. Engineers skip
this and it is the first thing anyone else reads.

---

## Rubric

| Dimension | Wt | What earns full marks |
|---|---|---|
| **Privacy — provable** | 25 | Local chat **and** embeddings **and** OCR; egress enforced *and* observed; attestation with 0 non-loopback and an honest `scope_and_limits` |
| **Defensibility — measured** | 25 | Blind seeded sample; pre-registered, hashed protocol; recall + elusion + precision with CIs; bundle replays via `VERIFY.md` |
| **Citations — enforced** | 15 | Verifier in code: no fabricated markers, no uncited claims, quotes verbatim; "not found in the provided documents" works |
| **Ingestion — honest** | 15 | Recursive containers; OCR; documented dedupe policy; **non-empty, triaged exception list**; load file read and reconciled |
| **Shippability** | 10 | Runs offline from compose; checkpointed and resumable; pinned digests |
| **Score & governance** | 10 | SAIS-100 with the legal overlay, before/after, no auto-fail; `DEFENSE.md` names real limits |

**Auto-fail, regardless of total** — any of the four legal conditions:

- case content can leave by an unapproved or unenforced path
- cross-matter leakage
- a production emitted without a recorded human approval
- the model cannot be pinned

Three things cost marks more often than anything else, so check them first:

- an **empty** exception list (it means you dropped documents silently, or you are not
  looking)
- **no elusion measurement** (recall alone says nothing about what you missed)
- a protocol written **after** the classification run (the tool refuses; people work
  around the tool)

---

## The Defense Round

Fifteen minutes each, in pairs. **You are opposing counsel's expert.** Break your
partner's system — politely, specifically, and in writing.

Ask these, in this order:

1. "Show me your exception list. What happened to those documents?"
2. "What is your recall, and what is the confidence interval?"
3. "Who chose the validation threshold, and when?"
4. "Walk me through why document `DOC-000417` was coded responsive."
5. "Prove no document content left this machine. What exactly does your monitor cover?"
6. "Re-run this review in front of me."
7. "What model version? Can you still get those weights?"

Hand your partner their three weakest answers, in writing. Then swap.

> You will be asked these questions for the rest of your career in this field. Better in
> here first.

---

## Certification

This course awards the **Elephant Scale Legal AI Engineer Certificate**. It requires:

1. minimum attendance,
2. completion of the module labs, and
3. a capstone that **passes its own `VERIFY.md`** and trips **no** legal auto-fail.

Requirement 3 is the one that matters, and it is deliberately not a judgment call. Either the
bundle replays for someone else or it does not; either a privileged document is reachable, a
matter leaks, a production went out unapproved and a model cannot be pinned — or none of those
is true. Nobody passes this on effort.

You also leave with the repository itself, and you should treat it as the more useful half.
The certificate records that you cleared a bar. The repository is how you show it — because
sooner or later somebody will skip the certificate and ask you to re-run your review in front
of them.

---

## Extensions

Pick one if you have time. They map to the Day 3 modules and the modular series (Labs 09–12).

| extension | module | lab |
|---|---|---|
| Entities, a reconstructed thread, a timeline | 9 | [08](../09-Investigations-Timeline/README.md) |
| A multi-step workflow with a real human checkpoint | 10 | [09](../10-Agentic-Legal-Workflow/README.md) |
| Containerize the ingest workers and scale across cores | 11 | [10](../11-Deploy-At-Scale/README.md) |
| A full SAIS-100 verified audit with evidence per sub-score | 12 | [11](../12-Governance-Audit/README.md) |
| **Attribution checking** — local model as judge: does chunk `[n]` actually *support* this sentence? Measure how often your citations are merely *plausible* | — | — |
| **Hybrid tuning** — sweep `RRF_K` and `TOP_K`; plot the recall curve | — | — |

> Attribution checking is the most interesting unsolved problem in this course. If
> something in this room turns into a product, it is that.

---

## Teacher's Playbook

### What good looks like

A repository you could hand to a legal-tech hiring manager without a covering explanation.
Concretely: `run_matter.py` works from a clean clone; the exception list is non-empty and
each entry has a next step; `metrics.json` has three intervals and a pre-registered
protocol hash; `attestation.json` has a `scope_and_limits` the student can defend out loud;
`DEFENSE.md` question 6 names at least three real limits; `sais100-score.json` has two
scores and zero auto-fails.

The strongest signal is not any artifact. It is whether the student says "I don't know" to
the right question and then says what they would measure to find out.

### Timing (about 3 hours, integrated)

| | |
|---|---|
| 0:00 | hand out the rubric (do this on **Day 2 morning**, not here) |
| 0:00–1:15 | assembly: driver, offline run, two scores |
| 1:15–2:00 | `DEFENSE.md` and `README.md` — **silent writing time, enforced** |
| 2:00–2:30 | defense round, pairs, 15 minutes each way |
| 2:30–2:50 | round-the-room: each student reads their partner's *best* question aloud |
| 2:50–3:00 | close on the three keepers |

Enforce the silent writing block. Engineers will keep polishing code until the clock runs
out and then hand in a system nobody can explain, which is precisely the failure mode the
course exists to prevent.

### Grading notes

- Grade **question 6 hardest.** "No significant limitations" fails the module, not the
  engineering. A student with a mediocre pipeline and an excellent limits section has
  understood this course better than the reverse, and should be graded accordingly.
- Check the exception list before anything else. It takes ten seconds and it tells you
  whether the student is honest about their own output.
- Run `VERIFY.md` on at least two capstones in front of the room. Pick one you expect to
  work and one at random.
- An **empty** `scope_and_limits` is worse than a missing attestation. The second is
  incomplete; the first is an overclaim.

### Issuing the certificate

The certificate is only worth what the bar is worth, so run the bar as a checklist, per
student, in front of them:

| # | Check | How you check it, in under a minute |
|---|---|---|
| 1 | Attendance | Your roster. |
| 2 | Module labs complete | Their `work/` has the stage artifacts for Labs 02–07. |
| 3 | `VERIFY.md` replays | Run it yourself from a clean directory, changing only the corpus path. |
| 4 | No legal auto-fail | `sais100-score.json` — LEGAL-A/B/C/D all absent. |

Keep the result. One line per student is enough — name, date, course code
(`LEGAL-AI-ENG-2026`), the four checks, and the `VERIFY.md` verdict. If this credential is
going to mean something in five years, the first person who asks "what did they actually have
to do?" has to get an answer, and that answer is this row.

Borderline cases, decided in advance so you are not deciding them at 4:55pm:

- **`VERIFY.md` fails for an environment reason** (missing tesseract, no local model) and
  replays once that is supplied — that passes. The bar is reproducibility, not the student's
  laptop.
- **`VERIFY.md` fails because the bundle is incomplete** — that does not pass. Offer a
  deadline to send a working bundle rather than an exception; most students will take it.
- **An auto-fail the student found and documented in `DEFENSE.md`** still trips. Say why
  plainly: the four conditions are about what the system does, not about whether its author
  understood it. Document the honesty, award the certificate when it is fixed.

### Debrief questions

1. **"Whose capstone would you rather defend: one scoring 96 with a thin DEFENSE.md, or
   one scoring 78 whose author can name every weakness?"** The 78. The score measures
   controls; the defense measures whether a human understands the system. You can fix
   controls in a week. In a deposition you have the author, not the week.

2. **"You ran with the network off and everything worked. What have you proven?"** That
   the pipeline has no runtime network dependency — which is real and worth having. Not
   that no data left during development, not that the model is clean, not that your logs
   stay local in production. Say what the test covers. That habit is the course.

3. **"A client asks for your recall number in an email. What do you send?"** The point
   estimate, the interval, the sample size, the date the protocol was fixed, and its hash.
   Five facts, one sentence. Anyone who sends one number has unlearned Module 6.

4. **"What is the first thing you would add with another week?"** Listen for the elusion
   sample size or the attribution check, not for a better model. Students who answer
   "a bigger model" have optimized the dimension that matters least here.

### The one thing to say out loud

Two days ago these students could build a legal-AI system. The reason they can now defend
one is not that the code got better — most of it is the same code they would have written
on Day 1. It is that every stage now emits an artifact, and the artifacts are the defense.
Say that, and then say the three keepers: the four leak points, recall *and* elusion with
an interval, and "can you prove it?" asked of your own work before someone else asks it of
you.

---

**Day 3 starts here:** [Lab 07 — Score and Package](../07-Score-and-Package/README.md)
