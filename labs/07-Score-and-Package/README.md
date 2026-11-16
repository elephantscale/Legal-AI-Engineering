# Lab 07 — Score and Package

**Module 7 · Ship It — Workflow, Private Deployment, and Governance**

You have five working stages and a pile of artifacts. That is not a system yet. A system
is the stages wired together so they can be re-run, the gates a human has to pass
through, a container that cannot phone home, and a number you can put in front of a
client.

By the end of this lab you have:

- `run_matter.py` — the whole pipeline as one resumable workflow with three human gates
- a **production set**: Bates numbers, a `.dat` load file, a manifest with disclosures
- `sais100-score.json` — the SAIS-100 score, **before and after** one hardening pass
- `docker-compose.yml` — the stack running on a network with no route out

**Deliverable for the capstone bundle:** `sais100-score.json` (both scores), the
production set with its load file, and the compose file.

---

## Setup

Nothing new to install. `sais100.py` is stdlib-only on purpose — the person auditing you
should be able to run it on a bare machine.

```bash
cd labs/07-Score-and-Package
```

You need Labs 02–06 working. If you have been following the pipeline, your `labs/work/`
already has what this lab consumes. If not, `run_matter.py` builds it from scratch.

---

## Part 1 — One workflow, three gates

```bash
python3 run_matter.py --corpus ../assets/corpus --work ../work
```

That runs twelve stages in order. Three of them stop at a gate:

```
 [1] ingest ──▶ [2] index ──▶ [3] chunk ──▶ [4] embed ──▶ [5] rag ──▶ [6] attest
      │                                                                 ──▶ [7] tripwire
   ◆ GATE: exception list reviewed
                                                                            │
 [8] richness ──▶ [9] protocol ──▶ [10] classify ──▶ [11] measure ──▶ [12] bundle
                                        │                                 │
                                   ◆ GATE: privilege              ◆ GATE: production
                                     confirmed                      approved
                                                        ──▶ produce
```

The design rule is one sentence: **autonomy between the gates, a human at every gate.**
Automate everything up to a gate. Never automate through one.

Run it again:

```bash
python3 run_matter.py --work ../work
```

Every stage says `[skip] already done with this config`. That is not a cache — it is the
idempotency key `(stage, config_hash)`, where `config_hash` covers the command *and* the
`LEGAL_AI_*` environment that shapes its output. Change the model and every downstream
stage correctly becomes stale.

One stage does not play by that rule, and the exception is the interesting part:

```
  [keep] protocol   validation-protocol.md was already written (sha256 ...) -> adopted, not rebuilt
```

If you came straight from the Core you already wrote a validation protocol in Lab 06, and
`defensible_review.py protocol` **refuses to overwrite one**. So the orchestrator does not
try. It adopts the protocol that is on disk, hashes it into `_state/run.log`, and carries
on — and `metrics.json` then records `pre_registered: true` against *that* hash, which is
the strongest version of the claim: the numbers were measured against a protocol written
before anyone had seen a result. `--force` will not override this. The only way to revise a
pre-registration is Lab 06's own `protocol --force`, by hand, with the old version in version
control.

> Idempotency has a limit, and it is a legal one. Most stages may be rebuilt because the
> output is a function of the input. A pre-registration is not: its value comes from *when*
> it was written, so rebuilding it destroys the only property that made it evidence.

Then prove resumability the honest way — break something in the middle:

```bash
mv ../work/chunks.jsonl ../work/chunks.jsonl.bak
python3 run_matter.py --work ../work          # chunk re-runs, ingest and index do not
```

> Idempotent, append-only, checkpointed stages are not just good engineering here. The
> artifact chain **is** the chain of custody. Mutating stage 3's output in place destroys
> the evidence of what stage 2 produced.

---

## Part 2 — The production gate

Try to produce:

```bash
python3 run_matter.py --work ../work --stage produce
```

It refuses, and it tells you what to check first. There is no `--yes` flag and no
confidence threshold that opens this gate. Production is irreversible and outward-facing:
once documents go to the other side you cannot take them back.

Check the three things it names, then put your name on it:

```bash
python3 run_matter.py --work ../work --approve-gate ingest   "R. Patel (review lead)"
python3 run_matter.py --work ../work --approve-gate classify "R. Patel (review lead)"
python3 run_matter.py --work ../work --approve-production    "A. Reviewer, Esq."
python3 run_matter.py --work ../work --stage produce
```

```
  produced  : 15 documents  (Bates HOLL0000001–HOLL0000015)
  withheld  : 1181
      not responsive               1127
      pending human review           50
      PRIVILEGED — withheld           4
  approved  : A. Reviewer, Esq. at 2026-11-10T05:59:35Z
```

Look at what the withheld breakdown is doing. Three different reasons, counted
separately, in the manifest. "We produced 15 documents" is not a defensible statement;
"we produced 15, withheld 4 as privileged, withheld 50 pending human review, and coded
1,127 non-responsive" is.

Now read `../work/production/VOL001/manifest.json`, especially `disclosures`:

```json
"disclosures": [
  "5 document(s) did not process. The exception list is available.",
  "AI components used in this review are disclosed in attestation.json; the model is
   pinned by hash in the reproducibility bundle's manifest.json.",
  "The validation protocol was written before the classification run; its hash is
   recorded above."
]
```

Volunteering those three facts costs nothing. Being caught not volunteering them costs
the matter.

And look at the load file you wrote:

```bash
head -c 200 ../work/production/VOL001/VOL001.dat | cat -v
```

```
M-~BEGBATESM-~^TM-~ENDBATESM-~^TM-~CUSTODIANM-~^T...
```

`^T` is `\x14`, `M-~` is `\xfe`, one byte each — because the file is **cp1252**, not
UTF-8. Lab 02 read a load file; now you have written one, and had to make the same
encoding decision from the other side.

> A production is the one artifact in this course that leaves the building on purpose.
> Everything else in the pipeline exists so that this one is correct.

---

## Part 3 — Score it

```bash
python3 sais100.py --work ../work --save-baseline
```

Six categories, three questions each, 0–3 against anchored levels, weighted to 100. That
is standard SAIS-100 and this course does not fork it. What is different here is that
every answer is read **off your own artifacts**:

```
  category                  raw/9   weight   score
  --------------------------------------------------
  data security               8         20      18
  prompt security             9         20      20
  agent security              7         20      16
  model supply chain          8         15      13
  detection monitoring        8         15      13
  governance                  8         10       9
  --------------------------------------------------
  TOTAL                                100      89   Enterprise Ready
```

Run it without `--quiet-evidence` and read the per-question output. Every 3 cites a file:

```
    [3] T3  Is output quality measured against an independent ground truth?
           + metrics.json: recall 96.6% CI 82.8%–99.4%
           + elusion test vs pre-set threshold 2.0%: PASS
           + blind seeded samples; protocol hashed before the run
```

and every score below 3 says exactly what the next level costs:

```
    [1] A1  Do irreversible actions require human authorization?
           → the gate is defined but unexercised: no approval on record

    [2] M2  Are code and dependencies version-pinned?
           → level 3 needs hash-pinned installs (pip --require-hashes) and a container
             image referenced by digest, not tag

    [2] D2  Is case/matter data isolated from other matters?
           → level 3 needs an enforced boundary, not a convention: a per-matter index
             path and a test that a query against matter A cannot return a document
             from matter B
```

A self-assessed questionnaire is worth nothing under cross-examination. An evidence-based
score is a different artifact: each answer points at a file you can hand someone.

### The hardening pass

You already did most of it in Part 2 — recording those three approvals *is* a hardening
change. Add the last one:

```bash
cd ../06-Defensible-Review
python3 defensible_review.py verify --work ../work --corpus ../assets/corpus --replay
cd ../07-Score-and-Package
python3 sais100.py --work ../work --delta
```

```
  category                  before  after    Δ
  --------------------------------------------
  data security                 18     18    ·
  prompt security               20     20    ·
  agent security                16     20   +4
  model supply chain            13     13    ·
  detection monitoring          13     15   +2
  governance                     9     10   +1
  --------------------------------------------
  TOTAL                         89     96   +7
```

+7 for three recorded approvals and one verify run. Not one line of model code changed.
That ratio is the lesson: at this stage of a system's life, the cheap points are in
*evidence*, not in engineering.

---

## Part 4 — Make the number lie, then make it tell the truth

Weaken one control. Re-attest in observe-only mode, which is what a team does when
enforcement is inconvenient:

```bash
cd ../05-Local-Model-Egress-Proof
LEGAL_AI_EGRESS=observe python3 local_proof.py prove --work ../work
cd ../07-Score-and-Package
python3 sais100.py --work ../work --quiet-evidence
```

```
  TOTAL                                100      94   Enterprise Ready

  LEGAL AUTO-FAILS

    LEGAL-A  Egress is observed but not enforced
          evidence: attestation.json: egress_policy='OBSERVE ONLY — nothing was enforced'
          why: Observation tells you what happened. Only enforcement tells you what
               cannot happen. Run with policy=deny for a real matter.

  FINAL: DO NOT DEPLOY — legal auto-fail
```

**94 out of 100, and do-not-deploy.** The score went down by two points; the verdict went
from shippable to blocked. That is the whole reason the legal overlay exists. Four
conditions sit on top of the number:

| | condition | why it is absolute |
|---|---|---|
| **LEGAL-A** | case content can leave by an unapproved or unenforced path | one disclosure can waive privilege for the whole subject matter |
| **LEGAL-B** | data from different matters can mix | ethical walls are not a performance tuning parameter |
| **LEGAL-C** | a production went out with no recorded human approval | nobody is accountable for what left the building |
| **LEGAL-D** | the model cannot be pinned | an unreproducible review is an undefendable review |

Repair it and watch the verdict come back:

```bash
cd ../05-Local-Model-Egress-Proof && python3 local_proof.py prove --work ../work
cd ../07-Score-and-Package && python3 sais100.py --work ../work --quiet-evidence
```

> A number is a summary. An auto-fail is a condition. Never let a client read the first
> without the second.

---

## Part 5 — Package it

Read `docker-compose.yml` before you run anything. The control that matters is five
characters:

```yaml
networks:
  matter:
    internal: true
```

A Docker network marked `internal` has no gateway. It is not a firewall rule somebody can
edit, not a policy document, not a code review comment — the bridge simply has no route
out. Containers on it reach each other and nothing else.

That is the difference between *"we configured it not to call out"* and *"it cannot call
out"*. The first is a claim. The second is an architecture, and only the second survives
a deposition.

Three services, each for a reason:

| service | why it is separate |
|---|---|
| `llm` | the model, with **no published ports** — nothing outside the project reaches it, so two matters cannot accidentally share an endpoint |
| `tika` | parses attacker-supplied files for a living, so: own container, no credentials, no route out, **2 GB memory limit** |
| `pipeline` | corpus mounted `:ro` (forensic rule one), `/work` the only writable path, non-root user |

```bash
docker pull python:3.12-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim
#   -> paste that digest into the Dockerfile's FROM line
docker compose build
docker compose up -d llm
docker compose exec llm ollama pull qwen3:8b       # once, before going offline
docker compose run --rm pipeline --corpus /corpus --work /work
docker compose run --rm --entrypoint python3 pipeline sais100.py --work /work
```

Note `LEGAL_AI_EGRESS: deny-lan` in the compose file, not `deny`. Inside compose the model
and Tika sit on a private subnet, so loopback-only would block your own stack. `deny-lan`
allows RFC1918 and blocks the world. On a single bare-metal host, use `deny`. Say which
one you used in the attestation — the two claims are not the same claim.

If Docker is unavailable, read the two files and do Parts 1–4 on the host. The score and
the production set do not depend on the container.

---

## What to keep

| artifact | goes where |
|---|---|
| `sais100-score.json` (before and after) | capstone bundle |
| `../work/production/VOL001/` | capstone bundle |
| `docker-compose.yml`, `Dockerfile` | capstone bundle |
| `../work/_state/run.log`, `gate-*.json` | capstone bundle (the gate record) |

---

## Teacher's Playbook

### What good looks like

A student who gets this lab has a work tree where the gate files exist, the production set
has a real Bates range, and `sais100-score.json` has a `legal_auto_fails` array they can
explain line by line. The tell for real understanding is Part 4: they should be able to
say *why* 94-with-an-auto-fail is worse than 70-clean, without being prompted.

### Live demo script (12 minutes)

1. **The gate refuses** (2 min). Run `--stage produce` cold. Let the refusal sit on screen.
   Ask: "what flag would you add to make this go through?" Someone will say `--force`.
   Answer: there isn't one, and that is the design. Then show the four lines in
   `cmd_produce` that enforce it — it is not much code.
2. **Approve and produce** (3 min). Record the approval, produce, and open the manifest.
   Read the `disclosures` list out loud. Then `head -c 200 VOL001.dat | cat -v` and have
   them find the `\x14` and the `\xfe`. Callback to Lab 02: "you read one of these on day
   one; now you've written one."
3. **Score** (3 min). Run it with evidence on. Scroll slowly. Point out that every `3`
   has a filename next to it. Then scroll to an M2 or D2 line and read the gap text —
   "this is what the next level costs, in words, before anyone asks you."
4. **Break it** (4 min). This is the beat of the whole module. Re-attest with
   `LEGAL_AI_EGRESS=observe`, re-score, and let the room see **94 / DO NOT DEPLOY** at the
   same time. Then: "the score dropped two points and the verdict flipped. If you only
   report the number, you have misled your client by two points and one verdict."

### Common mistakes and fixes

| symptom | cause | fix |
|---|---|---|
| `run_matter.py` fails at `ingest` | corpus not generated | `python3 ../assets/make_corpus.py` |
| every stage re-runs every time | `LEGAL_AI_*` env differs between invocations | the config hash is doing its job; export the env once, or use a `.env` |
| `--stage produce` says "run classify first" | ran `produce` against a fresh work dir | run the pipeline first |
| `protocol` says `[keep] ... adopted, not rebuilt` | you finished Lab 06, so a pre-registration already exists | **nothing to fix — this is correct.** Re-running it would hit Lab 06's refusal and stop the pipeline; adopting it is what keeps `pre_registered: true` honest |
| score shows `model supply chain 0` | no reproducibility bundle, so no pins to read | run the `bundle` stage |
| `D2` stuck at 1 | catalog rows have no `matter` | re-ingest; `--matter` defaults to `SYNTHETIC-DEMO-01` |
| compose build fails on `FROM ... @sha256:REPLACE...` | the placeholder digest is deliberate | paste your own `docker inspect` digest |
| `docker compose up` cannot pull a model | `internal: true` is working | pull the model once on the connected host, into the named volume |
| score is 100 | they edited the scorer | check `git diff`; a scorer you can tune is not a control |

### Debrief questions

1. **"Your score went from 89 to 96 and you changed no model code. Is the system actually
   safer?"** Yes — and this is worth sitting with. Three of those points came from
   recording that a human reviewed something. Before, a human may well have reviewed it;
   there was no way to show that. Defensibility is largely the conversion of things that
   were true into things that are demonstrable. The system is no better at finding
   documents and is substantially better at surviving a challenge.

2. **"We scored 94 with an auto-fail. A client asks for 'the number.' What do you send?"**
   Not 94. The verdict, with the auto-fail named, and the one-line remediation. If you
   send 94 you have told the truth and created a false impression, which in this field is
   the thing that ends careers. Put the auto-fail in the subject line.

3. **"`internal: true` is five characters. Why is that worth more than a firewall rule?"**
   Because of who can change it and who can see it. A firewall rule lives outside your
   repo, changes without a commit, and is somebody else's job. `internal: true` is in the
   file that defines the system, shows up in a diff, and fails closed at container start.
   You can hand the compose file to opposing counsel's expert as the control itself.

4. **"The exception list has 5 documents out of 1,196. Why disclose it?"**
   Because the other side will ask, and the answer you give unprompted is worth more than
   the one extracted from you. Also because 5 is a fine number and the habit has to exist
   before the number is 5,000. The defensibility failure is never "some documents did not
   process" — it is "we did not know which ones."

5. **"What would D2 level 3 actually take?"** A per-matter index path (not one index with
   a `matter` column), a per-matter work volume, and a test in CI that queries matter A's
   index for a document only present in matter B and asserts zero hits. That test is the
   artifact. Until it exists, matter isolation is a convention, and conventions are what
   get violated at 2am before a deadline.

### Worked answer — the two scores

```
  BEFORE (pipeline just finished)            AFTER (gates recorded, bundle verified)
  data security          18                  data security          18
  prompt security        20                  prompt security        20
  agent security         16   A1 unexercised agent security         20
  model supply chain     13   M2 unpinned    model supply chain     13   M2 still 2
  detection monitoring   13   T2 untriaged   detection monitoring   15
  governance              9   G2 unverified  governance             10
  TOTAL                  89                  TOTAL                  96   (+7)

  Remaining honest gaps, both at level 2, both stated:
    D2  matter isolation is a convention, not an enforced boundary
    M2  dependencies pinned by version, not by hash; image by tag, not digest
```

Both remaining gaps are the right kind of gap: known, written down, with a named cost to
close. A student who reports 96 **and those two sentences** has done the lab. A student
who reports 96 has not.

### The one thing to say out loud

Every lab before this one produced an artifact. This lab is where the artifacts become a
system, and where the students see that the system's defensibility score is mostly a
function of whether the artifacts exist — not of how clever the code is. The clever code
was Labs 03 and 04. The defensibility was the filing.

---

**Next:** [Lab 08 — Capstone](../08-Capstone/README.md)
