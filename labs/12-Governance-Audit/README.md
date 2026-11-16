# Lab 12 — Governance Audit: Verified, With Evidence

**Module 12 · Deep Dive · the last lab of the course**

In Lab 07 you scored your own system from your own artifacts, and the scorer believed
them. An auditor does not.

This lab is the same rubric with one word added: **verified**. Every sub-score must cite
evidence an auditor can independently open, and the audit **re-runs the checks it can**
instead of reading a conclusion somebody else wrote. Three rules the tool enforces:

1. **"We're careful" scores 0.** No evidence, no points. A control nobody can show you is
   indistinguishable from one that does not exist.
2. **Evidence must be independently resolvable.** Not "see `attestation.json`" but
   `attestation.json:egress_policy == 'default-deny; loopback only'` — so the auditor
   checks the claim, not the citation.
3. **A check that could not run is not a pass.** It is `UNVERIFIED`, which is different
   from 0 and different from 3, and it is the row an honest report leads with.

**Deliverables:** `sais100-verified.json` with evidence citations, `audit-findings.md`
(one page), and the before/after delta.

> **Swap systems with another pair if you can.** Auditing somebody else's system is far
> more instructive than auditing your own, and it is what the job actually looks like.

---

## Setup

```bash
cd labs/12-Governance-Audit
```

Nothing to install. `audit.py` imports Lab 07's `sais100.py` on purpose — it re-checks the
scorer the system scored itself with rather than reimplementing the rubric — and then
re-runs Labs 04, 05 and 06 as subprocesses.

---

## Part 1 — The nine artifacts

```bash
python3 audit.py artifacts --work ../work
```

```
  present: 7/9    missing: 2/9

  Missing and it is an ORGANIZATIONAL document, not a program output (2):
      1. Written AI use policy
      8. Access-control and ethical-wall evidence
```

Seven of nine, from a system you built in two days without once setting out to produce
compliance documentation. That is the module's thesis made concrete:

> Seven of the nine are **files your system emits**, not documents somebody writes
> afterwards. Build them as outputs and an audit is a morning. Write them afterwards and
> it is a quarter.

And the two that are missing are missing for the right reason. Note what the tool says
about them:

> Do not fake these by generating a file. #1 is a policy somebody with authority signs,
> and #8 is a TEST you run against a real second matter. An audit that accepts a generated
> policy document has taught the organization that generating documents is how you pass
> audits.

If you want #8, go earn it: create a second matter, index it separately, query matter A's
index for a document that exists only in matter B, and assert zero hits. Commit the test.
That test *is* the artifact — a policy saying the wall exists is not evidence that it does.

---

## Part 2 — The verified audit

```bash
python3 audit.py audit --work ../work
```

```
  running bundle_replays … PASS
  running egress_enforced … PASS
  running protocol_predates … PASS
  running exceptions_triaged … PASS
  running matter_isolation … UNVERIFIED
  running citations_enforced … PASS
```

Six independent re-checks. Read what each one actually does — the difference between this
and a questionnaire is in these six functions:

| check | what it does, rather than read |
|---|---|
| **V1** | re-runs `defensible_review.py verify --replay`. It does not read `certified: true`. |
| **V2** | re-runs `local_proof.py tripwire` for **capability**, and reads the run's own attestation for **configuration** |
| **V3** | hashes the protocol on disk and compares it to the hash recorded in the bundle manifest |
| **V4** | counts exceptions, checks each has a `next_step`, and looks for a recorded human review |
| **V5** | counts matters in the catalog and looks for an isolation *test* |
| **V6** | re-runs `legal_rag.py ask --break-citations` and checks the verifier caught the sabotage |

**V2 is worth stopping on**, because conflating its two halves is a real audit error:

- **capability** — *can* the control block? (re-run the tripwire)
- **configuration** — *was it on*, in the run that produced this work directory? (read
  that run's own attestation)

A system whose guard works perfectly but which ran in observe-only mode passes the first
and fails the second — and the second is the mode the documents were actually processed
under. An audit that scores capability alone certifies a system that was unprotected while
it handled the evidence.

**V5 comes back UNVERIFIED, and that is the correct result**, not a gap in the tool:

> One matter in one index is a *convention*. The evidence an auditor needs is a TEST.
> Until that test exists there is nothing to verify.

`UNVERIFIED` caps the sub-score at 2. It cannot earn a 3, and it is not marked 0 either —
because the control may well be fine and there is simply no evidence either way. Saying
that plainly is most of what distinguishes an audit report from a reassurance.

---

## Part 3 — Make the audit catch something

A clean audit teaches you less than a dirty one. Weaken exactly one control — the way a
team does when enforcement is inconvenient — and re-audit:

```bash
cd ../05-Local-Model-Egress-Proof
LEGAL_AI_EGRESS=observe python3 local_proof.py prove --work ../work
cd ../12-Governance-Audit
python3 audit.py audit --work ../work
```

```
  running egress_enforced … FAIL

  category                  claimed  verified    Δ
  ------------------------------------------------
  data security                  16        13   -3
  ...
  TOTAL                          94        91   -3

  verified verdict: DO NOT DEPLOY — legal auto-fail

  ADJUSTMENTS (1)

    D1: 2 -> 1
        V2 FAILED on re-check: The guard WORKS but was not ENFORCING for the run that
        produced this work directory: the tripwire blocks, while the run's own
        attestation records an observe-only policy. The documents were processed
        without the control on. Capability is not configuration.
```

**The system scored itself 94. The audit scores it 91 and do-not-deploy.** Both numbers
came from the same rubric and the same artifacts. The difference is that one of them
re-ran the check.

> A verified audit almost never scores *higher* than the self-assessment — and when it
> does, the self-assessment was being modest about evidence it actually had.

---

## Part 4 — The findings report

```bash
python3 audit.py findings --work ../work
```

```
  self-assessed : 94/100
  verified      : 91/100 — DO NOT DEPLOY — legal auto-fail
  open questions: 3

  cheapest three fixes:
      1 hour       +4.4   Enforce egress instead of observing it
      half a day   +2.2   Write a matter-isolation test
      half a day   +1.7   Hash-pin dependencies and reference the image by digest
```

Open `audit-findings.md`. It is one page and it has seven sections: the verdict, what was
re-checked, what was unverified, the score adjustments, the nine artifacts, the three
highest-value fixes with effort estimates, and everything else that is open.

Two things about how the fixes are ranked. They are sorted by **effort first, then points
available** — because "what can we do by Friday" is the question a client actually asks,
not "what is theoretically most important." And each one carries a *how*, because a finding
without a remediation is a complaint.

Note the header the report generates when an auto-fail is present:

> The score band and the final verdict differ because an auto-fail is a condition, not a
> deduction. Quote the Final line, never the score alone.

### The section the tool cannot write

The report ends with **Gaps consciously carried**, empty, with a table waiting:

| gap | why we are carrying it | revisit when |
|---|---|---|

Fill it in. Not every gap gets closed. Knowing which ones you are carrying, and being able
to say why, is what a senior legal engineer is paid for — and an audit report with that
section blank is incomplete, however good the score is.

---

## Part 5 — Fix one thing and record the delta

```bash
python3 audit.py delta --work ../work          # saves the current audit as the baseline
# now apply exactly ONE fix
cd ../05-Local-Model-Egress-Proof && python3 local_proof.py prove --work ../work
cd ../12-Governance-Audit
python3 audit.py audit --work ../work
python3 audit.py delta --work ../work
```

```
  TOTAL                         91     96   +5
  DO NOT DEPLOY — legal auto-fail  ->  Enterprise Ready

  questions that moved:
      D1: 1 -> 3
```

One command's worth of change: 91 → 96, and the verdict flips from blocked to shippable.
Save the baseline **while the system is broken**, or the delta measures nothing — the
order matters and the tool will tell you `Nothing moved` if you get it wrong.

That `Nothing moved` message is worth reading when you see it:

> Either the fix did not land, or it was not a fix the rubric measures — and the second
> case is worth more thought than the first.

---

## Exercises

1. **Audit a partner's system.** Swap work directories. Write their findings report, hand
   it over, and defend one finding they disagree with.
2. **Earn artifact #8.** Build the matter-isolation test described in Part 1 until `V5`
   returns PASS rather than UNVERIFIED. This is the single most valuable half-day in the
   lab.
3. **Add a seventh re-check.** Pick a sub-score that is currently scored from an artifact
   and write a function that re-runs it instead. `M1` (is the model pinned?) is a good
   one — re-read the digest from the runtime and compare it to the manifest.
4. **Break a re-check honestly.** Make `V3` fail: edit `validation-protocol.md` after the
   bundle was written. Read the resulting finding out loud. Then explain why that is the
   most damaging single finding in the whole list.
5. **Audit the auditor.** `audit.py` imports `sais100.py`. What stops a system from
   shipping a modified `sais100.py` that scores itself 100? What evidence would an
   auditor need?

---

## Review Questions

1. What is the difference between `UNVERIFIED` and a score of 0? Why must a report
   distinguish them?
2. `V2` checks two things. Name them, and give a case that passes one and fails the other.
3. Seven of the nine artifacts come out of your pipeline. Why does that change the cost of
   an audit so much?
4. Your verified score is 91 and there is one auto-fail. A client asks for "the number."
   What do you send?
5. Why is it better to audit somebody else's system than your own?

---

## Teacher's Playbook

### What good looks like

A student who gets this lab produces a findings report whose **Gaps consciously carried**
section has real entries with real reasons. The score is almost beside the point. The tell
is exercise 5: a student who sees that `audit.py` importing `sais100.py` is itself a trust
assumption has understood what an audit is.

### Live-demo script (about 15 minutes)

1. **The nine** (3 min). Run `artifacts`. **7/9.** Let that land — they did not try to
   produce compliance documentation and they have seven of nine. Then read the "do not
   fake these" paragraph aloud for the two missing, and say that #8 is a test, not a memo.
2. **The six re-checks** (3 min). Run `audit` and let the six lines print one at a time;
   it takes a few seconds each and the pacing is good for the room. *"Every one of those
   re-ran something. None of them read a conclusion."*
3. **UNVERIFIED** (3 min). Stop on V5. Ask: *"should matter isolation score 3? You have
   one matter and it is in one index."* Somebody will argue yes. Then read the note about
   the test. *"Neither of us knows. That is what UNVERIFIED means, and it is the honest
   answer."*
4. **Catch something** (4 min). This is the beat. Re-attest with `observe`, re-audit:
   **claimed 94, verified 91, D1 downgraded, do-not-deploy.** Read the adjustment text on
   screen — *capability is not configuration*. *"The self-assessment was not lying. It
   just did not check."*
5. **The fix** (2 min). One command, 91 → 96, verdict flips. Then end on the empty
   **Gaps consciously carried** table: *"this is the part I cannot generate for you, and
   it is the part with your name on it."*

### The debrief that ends the course

**"What was the cheapest point you bought, and what was the most expensive one you chose
not to?"**

The first half is easy and everyone has an answer — usually enforcing egress, or running
the tripwire, each about fifteen minutes.

**The second half is the whole question**, and it is the right note to end the course on.
Not every gap gets closed. Hash-pinned dependencies, a real matter-isolation test suite, a
bigger elusion sample — these cost real time and sometimes the answer is "not this
quarter." Knowing which gaps you are consciously carrying, and being able to say why in
one sentence to a partner or a GC, is what separates a senior legal engineer from someone
who ran the tool.

Push on anyone who says "none." Carrying no gaps means either they have not looked or they
are not shipping.

### Common mistakes and fixes

| symptom | cause | fix |
|---|---|---|
| `no work directory at …` | no pipeline run | `cd ../07-Score-and-Package && python3 run_matter.py` |
| all six re-checks UNVERIFIED | running from the wrong directory | run from `labs/12-Governance-Audit`; the subprocess paths are relative to `labs/` |
| `V1` fails with no obvious cause | the corpus moved since the bundle was built | re-bundle, or point `--corpus` at the right tree |
| `delta` says "Nothing moved" | baseline saved *after* the fix | save the baseline while it is still broken |
| verified score equals claimed score | every re-check passed | that is a clean audit — now do Part 3 |
| 9/9 artifacts present | somebody generated the policy file | ask who signed it; that is the audit question |
| student reports 96 with an auto-fail | read the band, not the verdict | the report header says this explicitly |

### Further debrief

1. **"Is `UNVERIFIED` just a cop-out?"** The opposite. `UNVERIFIED` is the only honest
   label for a control you could not test, and it is harder to write than either a pass or
   a fail because it invites the question "why not?" An audit with no unverified rows is
   either a very mature system or an auditor who was not looking.

2. **"We scored 96 verified. Are we done?"** No, and the report says so in two places: V5
   is still unverified, and two of the nine artifacts are missing. Both of those are
   organizational work the pipeline cannot do for you. 96 is the score of the part that
   is code.

3. **"Who audits `sais100.py`?"** Nobody, in this lab, and that is exercise 5. A scorer
   the audited party controls is a trust assumption. In practice the auditor brings their
   own copy, pinned by hash, and the SBOM from Module 7 is exactly how you would show
   which one was used. Students who get here have understood supply chain from the other
   side.

4. **"Why rank fixes by effort rather than by points?"** Because the client asks "what can
   we do by Friday," and because a fifteen-minute fix that lifts a verdict out of
   do-not-deploy is worth more than a half-day fix worth more points. Ranking by points
   alone produces a report nobody acts on.

### Timing

90 minutes. Part 1 in 10, Part 2 in 20, Part 3 in 15, Part 4 in 20 — including real time
to write **Gaps consciously carried** — Part 5 in 10, debrief in 15. If you are running
the pair-swap (recommended), add 20 and cut the exercises.

### Closing the course on this lab

If the Deep Dive ends here, this is the last thing the room hears, so close on the three keepers
rather than on the audit:

- **the four leak points** — OCR, embeddings, chat, logs. Count them every time.
- **recall and elusion, with the interval.** No bare point estimates.
- **"can you prove it?"** — asked of your own work, before someone else asks it of you.

Then the callback: at the end of the Core they could build a legal-AI system. The reason they
can now defend one is not that the code got better. It is that every stage emits an artifact,
and the artifacts are the defence.

---

**Back to:** [Lab 08 — Capstone](../08-Capstone/README.md) · [all labs](../README.md)
