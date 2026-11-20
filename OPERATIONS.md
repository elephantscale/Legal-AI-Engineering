# Project Operations

**Last updated:** 2026-11-20 (post-January plan recorded; outbound withdrawn, inbound is the channel)
**Owner:** Mark Kerzner
**Status:** Green

## Purpose and business value

**Legal AI Engineering** (`LEGAL-AI-ENG-2026`) is the legal-vertical track of the Elephant
Scale Secure AI Learning Path: a **2-day Core** plus a **1-day Deep Dive scheduled separately**,
with investigations and deployment-at-scale electives, Intermediate-to-Advanced, for software and
AI engineers moving into legal tech.

Why it earns its place in the catalog:

- It is **differentiated**. Generic "AI for lawyers" training teaches prompting. This course
  teaches a build path and ends with a repository the student can be cross-examined on.
- It **pulls through FreeEed**. FreeEed is the reference architecture named throughout
  (Tika extraction, OCR, imaging, PST/OST, Solr/Lucene, review, export). ⛔ **Not Bates/load-file production** — corrected 2026-11-15, see the risk register.
  A student who finishes has built against that architecture in miniature.
- It **carries SAIS-100 into a regulated vertical** with an evidence-based legal overlay —
  useful both as teaching and as the shape of a paid verified assessment.

Everything in the repo serves one of two claims a student must be able to make in front of a
court, a client, or a regulator: *"Nothing left the building"* and *"Here is exactly what the
system did, and you can re-run it."*

## Current status

**The course is written and runnable.** As of 2026-11-10 the repository contains:

| Component | State |
|---|---|
| `outline.md` | Complete. Treated as the contract for module numbers and the Core / Deep Dive split. |
| Slides | 13 decks (`00-about` + modules 01–12), ~4,340 lines of presenter-skeleton Markdown, 185 slides, all with `Notes:` narration |
| Labs | **All 11 built and smoke-tested offline** (02–06 + 08 Core, 07/10/12 Deep Dive, 09/11 electives), ~9,500 lines of Python, ~3,800 lines of lab README including Teacher's Playbooks |
| Course materials | 7 documents (design canvas, defensibility checklist, TAR metrics cheat sheet, privilege/egress attestation form, reproducibility manifest template, SAIS-100 legal overlay, capstone rubric) |
| Checks | `scripts/validate-course.sh`, `labs/verify-setup.sh`, `labs/test-all-labs.sh` — all green |

**Lives in the Elephant Scale course tree, under the Elephant Scale GitHub org.** Relocated
2026-11-10 from `/media/mark/data1/scaia/Legal-AI-Engineering` to
`/media/mark/data1/ES/Legal-AI-Engineering` (= `/home/mark/projects/ES/...`), matching every
sibling ES course. Canonical remote is now **`git@github.com:elephantscale/Legal-AI-Engineering.git`**,
`main` at `e5e4f34`, with the full course history force-pushed over the stub initial commit
that repo was created with.

**Positioning narrowed 2026-11-11 (HQ `DEC-018`).** Local AI is **not** an irrefutable win,
and the course no longer implies it is. Three architectures are accepted in practice:
**vendor-approved cloud** (the hosted review mainstream — privilege managed by contract and
process, and lawyers already accept it), **government cloud** (FedRAMP / StateRAMP / CJIS
authorization is the acceptance mechanism; every California county operates this way, as does
Scaia's own CJIS work), and **local or air-gapped** (the answer when the rule is absolute
rather than risk-based — military and classified first). Local keeps a real segment; it does
not take the field. Material changed the same day:

- **Module 5 gained a slide** — *Where Local Actually Wins — and Where It Does Not* — placed
  immediately after *Why Local Is Court-Defensible*, which was where the overclaim lived.
- **LEGAL-A was re-worded, not weakened.** It read "privileged content can reach a third
  party by any path". It now reads "case content can leave by an **unapproved or unenforced**
  path". The bar is identical — the code's test was always `D1 < 2` or observe-only — but the
  old wording described an approved hosted platform as an auto-fail, which is wrong in the
  field and is the sentence a student would have repeated to a firm. Changed in the overlay,
  the capstone rubric, Labs 07 and 08, deck `08-capstone`, and `sais100.py`'s condition
  string and D1 question text.
- **The strict reading still governs the capstone**, stated explicitly in both the rubric and
  the overlay: the system the student builds is local and has no approval package to point
  at, so it owes enforced egress, zero non-loopback connections, and a tripwire.

**Job-market review done 2026-11-11, course not yet changed.** Two new root documents:
`job-market-research.md` (nine postings at six named employers, with a skills matrix against
every module and lab) and `marketing-channels.md` (seven channels costed, the Govtra question
settled, and a 90-day experiment). **Per Mark's instruction nothing in the course has been
rewritten** — the gaps are recorded for review. The three findings that matter:

1. **The course is well aimed and mis-titled.** Four of six named employers **require a JD**
   for the role titled *Legal AI Engineer* (Relativity: *"JD and Bar admission"*; TR Eagan:
   *"J.D. ... required"*; Debevoise: JD + 3 years; Gibson Dunn: JD + admitted; Dentons asks two
   years of substantive practice). No course can satisfy those. The roles that match what we
   actually teach are titled differently and pay well: **TR CoCounsel FDE $136k–$253k** (RAG,
   evals, red-teaming, MLOps, MCP, Python, no JD), **Dentons AI Automation Engineer
   $99.5k–$125k** (now filled), **Gusto Legal AI Engineer contractor $150/hour**. Dentons ran
   both patterns in the same city in the same month, which is the cleanest illustration of the
   split available.
2. **Two gaps are absent, not thin.** **Commercial platform configuration** (Harvey, Copilot
   Studio, Azure AI Foundry, Relativity aiR/claiR, CoCounsel, iManage/NetDocuments — named
   constantly, taught nowhere here) and **AI adoption / lawyer training**, which is the
   most-repeated responsibility in the entire posting set and appears in five of six employers.
   Partial: prompt libraries as an artifact, human-oversight design, vendor evaluation.
3. **Our strongest material is what the market assumes rather than requests.** Five postings
   require an *understanding* of confidentiality, privilege and ethical walls; **none asks for
   evidence that egress was enforced**, and defensibility measurement is named once in the whole
   set (TR Senior Legal AI Engineer: *"measuring hallucination risk and citation quality"* —
   which is exactly Modules 4 and 6). That is simultaneously the differentiator and the
   over-investment. `DEC-018` is independently confirmed: every platform named in every posting
   is cloud.

## Recent accomplishments

- ✅ **THE COURSE NOW STATES WHAT A LAPTOP NEEDS — it never did (2026-11-16, Mark's question).**
  Before today the only hardware statement anywhere in the repo was `SETUP.md`'s "Python 3.10+
  is the only hard requirement", `verify-setup.sh` checked no hardware at all, and the
  freeeed.org page said "a modern laptop and reliable internet". **The answer is no GPU**, and
  it is now written down with measured numbers rather than asserted: corpus builds in 2 s,
  Labs 02–06 run end to end in ~12 s, work tree 17 MB, measured on a 12-core machine with no
  usable GPU. Floor **8 GB RAM / 2 GB disk / Python 3.10+**; comfortable 16 GB and 10 GB (the
  models are ~5.5 GB of it).
  - **The one place a GPU is genuinely felt, named precisely:** Lab 06's `classify` is one
    model call per document across ~1,198 documents, serially. A tea break on a GPU; not
    class-time work on a CPU. **Both CPU routes were tested, not assumed** — `--limit 150`
    works and `measure` handles it correctly, returning a *wider confidence interval*, which
    lands the module's own lesson harder ("an estimate consistent with the target, not a
    demonstration of it"); `--classifier keyword` is the other, and the course already argues
    it should be run either way.
  - **Where it went:** a measured requirements table and a "what does a GPU actually buy you"
    section in `labs/SETUP.md`; a new **Machine** block in `verify-setup.sh` (cores, RAM, free
    disk, GPU) that reports `no gpu — and that is fine` with the consequence attached, in the
    script's existing house style of never failing the class; and a `--limit 150` note at Lab
    06's classify step.
  - ⚠ **Separate finding, for Mark: this machine cannot demo local mode.** No Ollama
    installed, and no usable GPU (Intel UHD 630 + Radeon PRO WX 2100). Students are fine on
    CPU; **the instructor is the one who has to show a local model answering**, since
    local-first is the course's central claim. Added to Important TODOs.
- 🔴➡✅ **THE BACK-TO-BACK ROUTE WAS BROKEN, AND IT WAS THE ONE NOBODY HAD RUN (found and fixed
  2026-11-16, prompted by the first confirmed seat booking three consecutive days).** A student
  who **actually completed Lab 06** in the Core arrives at the Deep Dive with
  `work/validation-protocol.md` on disk but **no `_state/protocol.done` marker** — Lab 06's
  commands do not write pipeline markers, only `run_matter.py` does. So Lab 07's opening
  command, the first thing anyone types on Day 3, re-ran the `protocol` stage, hit
  `defensible_review.py protocol`'s deliberate **refusal to overwrite a pre-registration**,
  exited 1, and **stopped the pipeline**: `classify`, `measure` and `bundle` never ran. The
  failure was invisible because the designed route hid it — `resume-deep-dive.sh` deliberately
  *skips* Lab 06, so the replayed tree has no protocol and the stage runs clean. **Reproduced
  before the fix and verified after**, on both routes.
  - **Fix:** `Stage` gains `adopt_existing`, set only on `protocol`. The pipeline now adopts
    the protocol already on disk, hashes it into `_state/run.log` as
    `status: "adopted-preexisting"`, and continues — and `metrics.json` records
    `pre_registered: true` against **the hash of the protocol the student wrote on Day 2**,
    which is a *stronger* audit trail than the replay route produces. Deliberately ahead of
    `--force`: nothing the orchestrator does may overwrite a pre-registration. The only way to
    revise one stays Lab 06's own `protocol --force`, by hand.
  - ⛔ **Lab 06 was not touched.** The refusal is the control and it still fires exactly as
    taught. The bug was in the orchestrator treating a timestamped artifact as rebuildable.
  - **Taught, not just patched:** Lab 07's README gains the `[keep]` line, its meaning and a
    "nothing to fix" row in Common mistakes; `slides/07-ship-score-govern.md` gains a bullet
    and narration on the limit of idempotency — most stages may be recomputed because output
    is a function of input, but a pre-registration's value is *when* it was written, so
    rebuilding it destroys the only property that made it evidence. `resume-deep-dive.sh`'s
    header comment no longer implies Lab 07 always re-runs that stage.
- *** THE COURSE IS NOW TWO PRODUCTS, NOT THREE DAYS IN A ROW (Mark, 2026-11-15). *** A **2-day
  Core** (Modules 1–6 + the capstone; the certificate bar is met by it alone) and a **1-day Deep
  Dive** (Modules **7**, **10**, **12** — ship it, oversee it, prove it), **sold and scheduled
  separately**, with Modules 9 and 11 as **electives**. The two still run back to back as three
  consecutive days on request. **Mark's reason, recorded because it is the design rationale:**
  three days in a row is the hardest thing to ask of a working legal team. The repo says so
  throughout — `outline.md`, `README.md`, `CLAUDE.md`, `labs/README.md`, `labs/SETUP.md`, the
  capstone lab, and the day labels on eight decks (`Day 3 —` became `Deep Dive —`, the modular
  series became `Elective —`). **"Condensed two-day version" is gone as a concept**, and with it
  the 4pm-on-Day-2 cut decision: the Core *is* the two-day product.
  - **Module 7 was moved into Day 2 and moved straight back, in the same session.** The clock
    refused it: decision 0's table has Day 2 at **≈7:05 against 6.5 hours — already ~35 minutes
    over — without** Module 7, and Module 7 plus Lab 07 is another **1:45**, which would put Day 2
    near **8:50**. Keeping it in the Deep Dive also makes that day a real day: decision 4 flagged
    that 10 + 12 alone *"is the same shape as Day 1, not obviously a day"*, and 7 + 10 + 12 is.
    **Do not re-propose the move without new timings.**
  - **`labs/resume-deep-dive.sh` is new, and it is what makes a separately scheduled day work.**
    Labs 07, 10 and 12 all read the Core's `labs/work/` tree, so a student returning weeks later
    with a wiped laptop cannot start. The script rebuilds the **seeded** corpus (seed 20261109,
    pinned so the playbooks' document counts stay true) and replays **Labs 02–05** offline, then
    prints what the Deep Dive will look for. Verified end to end: replay → Lab 07's twelve stages
    and three gates → Lab 10 → Lab 12, all green offline.
  - It deliberately does **not** rebuild the tree with Lab 07's `run_matter.py`, because that
    one-line rebuild is the Deep Dive's opening lesson. **Why it stops at Lab 05 is a defect we
    found on the way** — see the risk table.
  - **Checks:** `validate-course.sh` green, `labs/test-all-labs.sh --docs 120` **94 passed / 0
    failed / 1 n/a**, `verify-setup.sh` green.

- **Module 1 now proves the need for the job, not just for the work** (Mark, 2026-11-12). Part 1
  always carried the firm-side adoption evidence; nothing carried the demand side. New slide
  **What the Postings Actually Say** (Part 2, after the role thesis) puts up nine postings at six
  employers: five lawyer-titled roles gated behind a J.D., four engineer-titled roles with no J.D.
  and the best-paid role in the set among them, the Dentons same-firm/same-month pair, and — said
  out loud rather than discovered later — the two things five of six employers ask for that this
  course does not teach (the commercial platforms by name, and adoption). Companion handout
  `course-materials/legal-ai-job-market.md` carries the full tables, the three résumé sentences,
  the $150/hour contractor data point, a section for J.D.-holders, and five caveats. The topic is
  named in `outline.md`, so it is in the contract and in the Word outline. Built entirely from
  `job-market-research.md` (2026-11-11); **no number is quoted that the research could not source
  to a posting**, and the two algorithmic salary estimates it flags are excluded. This closes P1
  item 1 of decision 8 and takes the JD-gated-title risk from **High** to Medium.
  Also repaired in the same pass: `outline.md` said *"and S score"* where it meant *"SAIS-100
  score"* — a truncated edit that had shipped into the contract. The Word outline in
  `~/Downloads` was rebuilt from the corrected source.

- **The outline now states what a participant takes away** (Mark, 2026-11-12): comfort in the
  area of study, the capstone repository, the reusable paperwork, a **certificate of completion
  signed by the instructor**, **six months of email support**, and **six months of course-material
  updates**. Also added as a prerequisite: students **bring their own AI subscription** (Claude,
  ChatGPT, Gemini or equivalent) and use it on the labs. Both appear in `outline.md` and on deck
  `00-about`; `labs/SETUP.md` was corrected because it claimed Python was the only requirement in
  the course. **The last three takeaways are commercial commitments, not curriculum** — see the
  risk row and decision 9.
- **All 11 labs run end to end with no API key, no network and no model.** `test-all-labs.sh`
  reports **94 passed / 0 failed** in 16 seconds on a 300-document corpus, including the
  deliberate refusals (production without approval, destruction without confirmation) which
  are asserted to exit non-zero rather than merely "not crash".
- **The Labs 02–07 pipeline chain is verified on the default corpus** (~1,196 documents, seed
  `20261109`): 1,196 docs → 15 produced / 1,181 withheld → SAIS-100 baseline 89 → 96 after
  one hardening pass → break egress → 94 + LEGAL-A → Do Not Deploy → repair → 96.
- **All seven planted corpus findings land**, including the deleted §7.3 indemnification cap,
  the 39-day communication gap, the dropped Cc, and the side letter reachable by two
  independent routes.
- **Six agent attacks are blocked with log lines** (injection, cross-matter, leaky memo,
  self-approval, unregistered tool, step flood), and the approval gate is idempotent.
- **Lab 10 fixture hardened.** The offline plan hard-coded `DOC-000330`, which existed only on
  the default corpus; on any other size the memo step turned into an out-of-matter refusal
  that *looked like a guardrail working*. The anchor is now resolved from the catalog at run
  time. `DOC-999999` stays hard-coded because it must be absent.
- **Course materials written** — including the SAIS-100 legal overlay with the evidence map
  for all 18 questions and the four legal auto-fail conditions.
- **Three documented corrections applied to `outline.md`** after independent verification
  (see *Decisions needed from Mark*).
- **The Legal AI Engineer Certificate is restored and now issuable.** It had been removed as
  an unbacked promise; Mark's decision is that it stays and becomes a brand name. `outline.md`
  carries "Assessment and Certification" and the certificate line again, the capstone deck and
  Lab 08 and the rubric are reworded back, and the gap that justified removing it is closed:
  the bar is objective, Lab 08's playbook has a four-check issuance checklist and the roster
  record, and the three borderline cases are decided in advance.
- **Committed and pushed** as `0349008` (92 files, +20,846 lines) to
  `git@github.com:Scaia-ai/Legal-AI-Engineering.git` `main`.
- **Module 1 gained a new opening section, "The Legal AI Implementation Gap"** (two slides,
  now Part 1; the existing parts renumbered 2–4). Every figure on it was taken from the
  primary report — ILTA's free 2026 executive summary, Wolters Kluwer's own Future Ready
  Lawyer 2026 data page, and the Thomson Reuters Institute's 2026 *AI in Professional
  Services* PDF and *Future of Professionals 2026 — Legal* page. Source URLs, respondent
  counts and **fieldwork dates** are in the presenter notes, together with an explicit list
  of the widely-quoted figures that were **left off** because no primary report carries them
  (ILTA product-level shares, the 85%–100% firm-size range, the 78% policy and 79% drafting
  aggregates, and the segment-level 2025 priors behind the 41%/47% split). `outline.md`
  gained a matching topic bullet.
- **One canonical repo.** `Scaia-ai/Legal-AI-Engineering` — the duplicate left behind by the
  move to the Elephant Scale org — was deleted by Mark on 2026-11-10, after a check confirmed
  its only branch (`main` at `e5e4f34`) was an ancestor of ours and nothing lived there alone.
  `git@github.com:elephantscale/Legal-AI-Engineering.git` is now the single source.
- **Five decks that would not assemble now build.** `slides/gen.sh` crashed on
  `02`, `09`, `10`, `11` and `12`, leaving those PPTX files missing from `assembly.out`.
  Both crashes are bugs in the shared assembler (`$ES_HOME/utils/presentations/md_astprocessor.py`)
  tripped by perfectly valid Markdown: a table cell of the form ``**`code`**`` (bold wrapping
  inline code) and an *emphasised* paragraph on a title slide, before the first slide heading.
  The assembler is another team's repo, so the fix was made on our side — `**tika-python**`
  in Module 2's Tika table, and an unitalicised `Optional Day 3 / modular` line on the four
  Day 3 title slides. All five parse clean; **the decks themselves are still Mark's to build.**
- **`validate-course.sh` glob bug fixed.** `labs/*/work*` matched
  `labs/11-Deploy-At-Scale/work_queue.py` — lab source, not lab output — so the "no real case
  data" check failed the moment that file became tracked. It now matches directories only.

## Current priorities

1. **Mark's review of the three `outline.md` edits**, one of which removed a deliverable
   (below), plus the one topic bullet added for the new Module 1 section.
2. 🔴 **A SOLO TIMED RUN-THROUGH OF DAY 1 — now the only rehearsal that exists
   (2026-11-18).** The timings in the playbooks are estimates, not measurements, and **Carlene
   cannot run before Jan 5** (Mark, 2026-11-18), so **the first paying room is the dry run**.
   The remaining measurement is Mark alone with a stopwatch, teaching Day 1 end to end and
   **working the labs as a student would** rather than skimming them, on something like the
   machine a student will bring. Module 1 is now budgeted at 50 minutes rather than 45.
   ➡ **The Day 2 overage is the live exposure**: decision 0 has it at ≈7:05 against 6.5 h,
   and with no rehearsal the choice of what gets dropped will otherwise be made at 3pm on
   Day 2, in front of paying students. **Decide the cut list in advance.**
   ✅ **The stopwatch now exists (2026-11-20).** `slides/gen-html.sh` builds a third release
   format — one self-contained reveal.js HTML file per module, from the same Markdown
   (`slides/release/` already held the PPTX and the PDF). Press **`S`** and the `Notes:`
   narration, the next slide, a clock and a **per-slide timer** open in a second window. That
   is the instrument for this run-through: it measures where the minutes actually go, per
   slide, which is exactly the number decision 0's clock table is currently guessing at. A
   slide that overruns the canvas scrolls instead of cropping, so "I had to scroll" is a
   second, free signal about which slides are too long.
3. **Build the PPTX decks** — `slides/gen.sh` is wired to the shared assembler. By standing
   instruction Claude does not run it; Mark builds the decks himself. ➡ The reveal.js build
   (`gen-html.sh`) is **separate and safe to run**: it never touches `gen.sh`, the assembler,
   or any PPTX. It also gives a route to a PDF that does not go through PowerPoint
   (`?print-pdf`), and a deck a student can keep and actually read afterwards — searchable,
   with working citation links, opening with no PowerPoint and no network on a client laptop.
   reveal.js is **vendored** in `slides/revealjs/` rather than loaded from a CDN: a course
   whose first claim is *"nothing left the building"* should not phone a CDN to render its
   own slides.

## Customers and revenue connections

- ⛔ **STUDENT ORGANISATION IS MARK'S, BY HIS OWN INSTRUCTION (2026-11-17, to the FreeEedCRM
  session): *"refrain from giving me advice on organizaing students. i will do it myself."***
  Recorded here as a standing preference because it binds this repo too — the entry below was
  written before it and has been cut back to facts. **What this repo does from here:** keep the
  course accurate about what it *requires* (the labs, the prerequisites, the certificate bar),
  and record what the roster actually is. **What it does not do:** rank who should attend how,
  recommend dates, propose tracks, or re-raise any of it as an action item. Same shape as the
  clock set-aside of 2026-11-15. ⛔ Do not re-propose unless Mark asks.
- ⚠ **ROSTER, 2026-11-17 — recorded with its uncertainty intact, because an earlier version of
  this entry overstated it.** Mark's words to the FreeEedCRM session were exactly *"I sent the
  invite and everyone accepted"*, **with no per-person detail**. I first wrote that up as "the
  cohort filled, all four accepted". **That was more than the source supports**, and a third
  session (`freeeedweb-9f`) independently had **three of the four invitations down as
  drafted-not-sent** (Wolfe by email, Chesler by LinkedIn DM, Bisk by DM on the sponsor line).
  So:
  - **No send date or channel is established** for Chesler, Bisk or the Wolfe invite, and **no
    seat is recorded for Bisk** — his route was always (c) sponsor, never a seat.
  - **Steve Wolfe's three-day commitment stands on its own** and does not depend on any of
    this: he committed directly to Mark on 2026-11-16, date-flexible. **He remains the one
    confirmed seat on record.**
  - **Carlene Gordon** had the advance-registration link emailed to her on 11-16; her reply is
    the record, and it is Mark's to have.
  - ➡ **The ambiguity is in the source, not in anyone's bookkeeping**, and it is not being
    resolved by inference. The contact rows live in `FreeEedCRM` and that session keeps them
    current. ⚠ **Consequence for this repo:** *"the class is guaranteed to run"* — which Mark
    put in writing to Carlene on 11-16 — is **better supported than it was on 11-15 and not yet
    established on headcount**. Do not restate it here as settled.
  - **What the course requires, stated as fact and not as advice about people.** This is the
    part that belongs in this repo, because it is a property of the course rather than a
    judgment about anyone's roster: **the Core is eleven Python labs plus a capstone
    repository**, the capstone is **assessed**, and the certificate bar is met by completing
    it (decision 2). A participant who does not write Python does not complete the labs, and
    nothing in the course softens that — by design, and `CLAUDE.md` forbids softening it.
    **Two of the invitees were assessed against that bar on 2026-11-15, before any invitation
    went out**, and those assessments live in `FreeEedCRM`:
    - **Reuven Bisk — marked NOT A SEAT since 2026-11-15.** J.D./M.B.A., practising attorney,
      part-time CFO. The assessment was: eleven Python labs plus a capstone repository, *"a
      practising attorney and CFO cannot complete them"*, *"selling him a seat would fail in
      week one"*. **His acceptance does not change what the labs require.** His bucket was
      always (c) sponsor / door-opener / private cohort.
    - **Robert Chesler — marked RAMP-UP, NOT DAY-ONE.** Princeton BSE EECS 1986, X Consortium,
      deep systems and C/X11; **no evidence of recent Python or LLM work**. The labs are within
      reach; starting them cold on day one is the risk. **Lead time is what the course can
      offer here and it already does**: Jan 5–7 gives seven weeks, and
      `verify-setup.sh` plus `labs/SETUP.md` are what a participant can use to arrive ready.
      Nothing further is needed from this repo.
  - **Available, not recommended — form 4129 already asks the question this repo needs
    answered.** The form asks *"How much Python do you
    write?"* down to *"None yet"*, so **their own stated answers make the track decision
    instead of Mark having to make it about them** — and it converts four LinkedIn-inferred
    Python levels into four stated ones, which is the measurement the audience question has
    always needed. It is also a documented opt-in under the page's narrow consent line; a
    reply saying "yes" is not. ⛔ Whether to use it is Mark's; this repo records only that the
    instrument exists and that **four stated Python levels would settle the audience question
    that `outline.md` and the signup page both still carry as open.**
  - ⛔ **CORRECTION to the remedy as relayed — do not offer Bisk the "Legal AI Implementation"
    track as a solution.** That checkbox (FreeEedWeb revision 01, C10) is **demand
    measurement that commits to nothing** — its own wording is *"if we run it"* — and the
    standing decision (Mark, 2026-11-15) is **stay with A, measure B**. Course B is not a
    smaller A: its substance is evaluating and configuring RelativityOne, CoCounsel, Harvey
    and Copilot Studio, products this instructor does not teach and which our own job-market
    handout names as the course's largest gap. **Ticking that box in November is not a seat in
    January.** What is genuinely available to Bisk today: **a private cohort** (real, on the
    page, and the right shape for a sponsor), or **attending without completing the labs** —
    which is honest only if it is said out loud, because the capstone is assessed and the
    certificate bar is met by completing it. ➡ Item 10 below records the constraints; the
    choice is Mark's.
- ⭐ **First confirmed seat: Steve Wolfe — three days, date-flexible** (Mark, 2026-11-16:
  *"steve wolfe is joining for three days, whenever the course runs"*). Three days = the
  **2-day Core plus the 1-day Deep Dive**, i.e. the full format and the largest purchase the
  page offers. Full record and the contact history are in `FreeEedCRM/contacts.csv`
  (`swolfe100@gmail.com`); what belongs here is what it changes for the course:
  - **It makes the back-to-back route the first cohort's real route, not the option.**
    `CLAUDE.md` describes three consecutive days as available "on request" — this is the
    request. Everything built for the 2 + 1 route still stands; the consequence was that
    the back-to-back route had **never been run**, and it was broken. See "Recent
    accomplishments" — Lab 07's pipeline stopped at the `protocol` stage for exactly the
    students who had completed Lab 06 properly. Found and fixed 2026-11-16.
  - **He removes himself as a date constraint.** Date-flexible, so the Nov 30 vs Dec 7
    choice is now decided by Carlene's dry run alone (see Upcoming deadlines).
  - ⚠ **Keep precise what his seat proves.** It validates **fit** — an engineer-titled
    person who can run all eleven Python labs on day one and still wants the legal
    vocabulary, which is the course's live audience question. It does **not** validate
    arm's-length willingness to pay: he is Mark's friend, currently self-employed, and would
    be on an individual rate. Carlene is the arm's-length demand evidence and is not yet a
    confirmed seat; Steve is the confirmed seat and is not arm's-length. **Complements, not
    substitutes** — reading them as two of a kind would overstate demand.
  - **Prerequisites: he meets the hardest one natively** (Ollama / local inference is his
    specialism). ⚠ Mild inverse risk: the Day 1 ingestion and search labs may sit below his
    level. Same shape as the Nov 20 session note — tell him where to skip ahead rather than
    pad the labs.
  - **Open for Mark:** whether he is paying, and at what rate. It is unrecorded, and it
    decides whether he counts toward "the class is guaranteed to run".
- **First student (dry run): Carlene Gordon.** Mark meets her **Tuesday 2026-11-17** to talk through
  the course and set expectations; **delivery dates are agreed later**, not in that meeting.
  This ends the course's build-ahead-of-demand phase.
  - **Run her as three days** (Mark, 2026-11-12). The course is now three days by default, and
    she is the dry run — measuring two days would measure a product we no longer lead with.
    - **Revisit under the 2026-11-15 split — Mark's call, not yet made.** The three days are now a
      2-day Core and a 1-day Deep Dive, so her dry run should be **2 + 1**: easier to schedule
      than three consecutive days, and it measures both products separately, including the gap and
      `resume-deep-dive.sh` on the way back in. Three days of teaching either way, so **$300 at
      $100/day is unaffected**. What does need deciding: whether her six months of support starts
      at the end of the Core or the end of the Deep Dive.
  - **She is to receive the certificate.** The infrastructure is ready: Lab 08's four-check
    issuance checklist and the roster record. She becomes **roster row #1** for
    `LEGAL-AI-ENG-2026`, which is the row that has to answer "what did they actually have to
    do?" in five years. Issue it against the same bar as any paying student — a softened
    first issuance is the one thing that would devalue the credential permanently.
  - **Decided 2026-11-12: she pays, at $100/day — $300 for the three days.** She asked to pay.
    Record *why* it is $300, because the number will be quoted back: she is the first cohort and
    the dry run, and the price buys her feedback and our timings. Three consequences. She is now
    a **paying student**, so the certificate bar and the **six months of email support** apply
    to her in full — she is the first live test of decision 9. **$300 must not reach Chandra's
    page or any channel conversation**; it is a pilot rate, not a list price, and the list price
    is still `Unknown`. And it is the course's **first revenue** — trivial in amount, material
    as a reference customer.
  - **Superseded by the above (Mark, 2026-11-10): course free, technical support paid.** She
    would get the course at no charge, with paid support afterwards on the issues the course
    covers. *(Needs CEO input — see Decisions needed from Mark.)*
- ⭐ **SECOND PAID QUOTE, AND THE PILOT RATE IS NOW THE COHORT-ONE INTRODUCTORY RATE
  (2026-11-17).** Andrew Stears replied to Mark's referral note asking whether there was a cost;
  Mark answered immediately: *"Offered at an introductory rate of $300."* The contact row is
  `FreeEedCRM`'s. What belongs here is what it changes about the price.
  - **The wording was right.** Decision 1 says the course is *discounted, not free*, because a
    discount keeps a list price on the table. "Introductory rate" is that framing, and it is
    time-bounded rather than permanent. **No guardrail was breached** — $300 was barred from
    Chandra's page and from channel conversations, and a private email to a friend is neither.
  - ⚠ **But the anchor it implies does not exist.** $300 is now introductory off a list price
    that is still `Unknown`, and the first person to ask *"introductory compared to what?"* gets
    no answer. The list price stops being a planning item and becomes what blocks the next quote.
  - ⚠ **$300 has left its justification behind.** It was priced for Carlene as $100/day × 3
    (2026-11-12), where the fee bought **feedback and our timings**. Andrew gives neither for the
    same number, so from today **$300 is the cohort-one introductory price**, not a dry-run rate.
    ➡ **Quote it consistently to everyone in this cohort.** These are friends who know each
    other; a second friend hearing a different number costs more than the discount does.
  - ✅ **FORMAT SETTLED THE SAME DAY (Mark, 2026-11-17): *"$300 covers all three days."***
    So the quote is the **2-day Core plus the 1-day Deep Dive**, and the cohort-one rate is not a
    number but a **rule — $100/day**, identical to Carlene's. That rule answers the next
    question before it is asked: **Core alone $200, Deep Dive day $100, all three $300**, and
    **Steve Wolfe's three days are $300** on the same basis. ⚠ Note what $300 carries at that
    rate: the **assessed certificate** and **six months of personal email support**
    (decision 9) — the expensive half is the support, not the teaching, and decision 9's fence
    (best effort, email, named participant, no client data, a project is quoted) is what keeps it
    affordable.
  - ⛔ **Guardrail unchanged and now one step closer to the edge:** $300 reaches no partner
    page, no channel conversation and no public page. A private email to a friend is not a
    channel; a forward of it is.
- **Partnership offer out to John Tredennick (Merlin Search Technologies), 2026-11-11.**
  Legal AI Engineering under the Merlin brand, Mark teaching it; email sent, awaiting a call.
  Tredennick founded and sold Catalyst and now runs Merlin, a commercial **cloud** review
  platform — so `DEC-018` is what makes the partnership coherent: under it his architecture is
  the mainstream, not a weakness the course corrects. If a call happens he may ask for
  `outline.md`, `course-materials/capstone-rubric.md` and the lab list; all three are
  presentable, and the LEGAL-A wording above is the line he would have read first.
- **The course is already published and for sale by a partner.** NobleProg lists *Legal AI
  Engineering* (14 h) on its country domains and on **Govtra**, its government-training front
  end. Investigated 2026-11-11: this is an **authorised partner listing**, not an unrelated
  offering — NobleProg is a live ES reseller with four contacts on the 22-name channel list,
  Chandra Tan published two ES courses in July 2026, and the page reproduces our outline down to
  the module titles and the certificate requirements. Three things follow:
  - **Their page is already stale** — it still shows Module 7 on Day 2. The outline Mark owes
    Chandra **by 2026-11-19** is now a correction, not a courtesy.
  - **It advertises the "Legal AI Engineer Certificate"**, including its requirements, on a
    third-party page, while the certificate's name is still an open ES brand decision
    (`DEC-015`) and none has ever been issued.
  - **First hard price anchor.** NobleProg prices ES courses at a flat **$193/h online,
    $278.80/h classroom** (21 h = $4,054/$5,854; 35 h = $6,757/$9,757). At 14 h that is
    **≈ $2,700 online / ≈ $3,900 classroom** retail. Ours is still `Unknown`.
- **FreeEed / SHMsoft** — the course is a demand channel for the platform, and the material
  tracks FreeEed's real design records (`docs/local-ai-cjis-briefing.md`,
  `docs/decisions/local-ai-architecture.md`). When FreeEed's pinned models or sizing tiers
  change, Module 5 and Module 11 change with them.
- **SAIS-100 / es-marketing** — the legal overlay is a worked example of a vertical overlay on
  SAIS-100 and may be reusable in the verified-assessment offering. Coordinate before
  publishing the overlay outside the course.
- **Elephant Scale Secure AI Learning Path** — this is its legal vertical. Sibling courses:
  `Building-Secure-AI-Applications`, `AI-Security-for-Security-Teams`, `Building-Agentic-AI`.

### Selling notes, moved out of `outline.md` (2026-11-17)

Mark, 2026-11-17: *"(electives sell on their own) sounds like sales talk."* It did, and it was
one of eight places where `outline.md` addressed **the seller rather than the student**. The
outline now carries only what a participant needs. These are the notes that were in it, and they
are worth keeping — here, where the audience is us:

- **Which elective to build out first: investigations.** It is the module an eDiscovery audience
  asks for most often — the single clearest signal in the material about demand order.
- **Deployment at Scale is the public-sector / government-cloud module.** CJIS, government and
  higher-ed sizing is what that buyer asks about first.
- **Say what the Core does not include in the sales conversation, not on Day 2.** A Core-only
  participant finishes without the document production set and the containerized deployment
  (both are Lab 07, on the Deep Dive). Raising that at 4pm on Day 2 turns a complete two-day
  course into a thing with a piece missing. ⛔ It belongs before the sale, never in the room.

### Competitive landscape for Course B — three independent reads, same conclusion (2026-11-18)

Prompted by a Harvey brochure Mark downloaded and a Bay Area university summary he forwarded.
**Dates and formats below were re-verified by search; prices were not found and stay `Unknown`.**

- **Harvey is running Course B itself.** *AI Fluency and the Future of Associate Development at
  Law Firms* (Harvey Law Schools, PDF created 2026-06-23) is a 10-page thought-leadership guide
  that closes by naming **Harvey Academy**, **Preparing for Legal Work** and **AI for Legal
  Basics** — fluency and adoption training sold by the platform vendor into the firm's L&D
  function, with quotes from Reed Smith's Global Head of L&D, Foley & Lardner's AI steering
  committee chair, and a Wilson Elser associate. ➡ **Course B's space is not empty, and the
  incumbent has firm relationships we do not.** This is evidence for the standing decision
  (**stay with A, measure B**), not against it.
- **UC Law SF (LexLab)** — **LAIC Lab**, an intensive three-day program on using, testing and
  implementing generative AI in legal work, **first run 2026-12-01 to 12-03**; the fourth
  **LAIC** runs **2027-03-08 to 03-10**; completion earns a **LAIC certificate** from UC Law SF.
  UC Law SF is also **making an AI-enabled lawyering lab required for all JD students**.
- **Stanford Law** — the **Stanford Legal Engineering Academy**, announced around 2026-11-03, is
  a **selective two-week residential** program for ~**50 participants**, **summer 2027**,
  application-based, awarding a **Certificate of Achievement after a capstone project**. A
  separate Stanford Law exec-ed course, *AI Strategy for Legal Leaders*, is priced at **$1,200**.
- ⚠ **NAMING COLLISION, AND IT CUTS BOTH WAYS.** Stanford is defining *"legal engineering"*
  right now, and its definition is **organizational AI strategy, workflow redesign, governance and
  prototyping for attorneys, operators and leaders** — which is **Course B's definition, not
  ours**. Tailwind: the category name gains institutional recognition, which our title rides.
  Risk: by 2027 a buyer hearing *"Legal AI Engineering"* will expect Stanford's meaning, so the
  audience sentence (**for engineers; Python labs; an assessed capstone**) has to get **louder,
  not softer**. ➡ This sharpens the standing top risk rather than adding a new one.
- ⚠ **Certificate exposure rises.** Both schools issue certificates and **Stanford's is
  capstone-gated exactly like ours**. Ours still has no settled name (`DEC-015`) and **SAIS-100
  still has no published spec**. Competing against a university-issued certificate with an
  unpublished rubric is the weakest form of that exposure.
- **Usable inside the course, with attribution and without reproducing their prose:** two
  citations from the Harvey guide — Reed Smith's *"However junior you are, you're the lawyer and
  you are responsible"* (Module 10, human oversight, currently asserted on our own authority) and
  Foley's *"AI fluency is an expectation, not an elective"* (Module 1 landscape).
- ⭐ **The absence in all three is the finding.** Ten pages from the best-funded player in the
  category, plus two university programs, and **privilege waiver by disclosure, recall/elusion
  measurement and reproducibility appear nowhere**. That is the **third independent confirmation**
  of the job-market result: the market conversation is about *fluency*, and nobody is asking for
  *proof*. Simultaneously our differentiator and our over-investment — and nobody is contesting
  that ground.

## Upcoming deadlines

- 🗓️ **DELIVERY DATES ARE SET: 2027-01-05 to 01-07.** Mark, 2026-11-17, to the FreeEedWeb
  session: ***"the dates are set, January 5-7. But leave open for waiting list."*** This
  **supersedes the tentative status of 2026-11-16** and every "nothing may state it as fixed"
  caveat that went with it. **Tuesday to Thursday**, three consecutive days = the **2-day Core
  on the 5th and 6th** plus the **1-day Deep Dive on the 7th**, back to back — the format the
  first confirmed seat booked. It clears Thanksgiving and year-end, starts in the first full
  working week of 2027, and leaves **seven weeks**.
  - 🆕 **A WAITING LIST NOW EXISTS, and it is half of the instruction.** The signup form's
    third option is *"No — put me on the waiting list for the next cohort"*, so the page is
    now collecting for **a second cohort that has no date and no plan**. ⛔ Per the rewritten
    guardrail 1 in `FreeEedWeb/docs/legal-ai-engineering-page-copy.md`, **that choice may never
    be dropped** — removing it would strand people who ticked it. ➡ Anyone who ticks it is a
    commitment we have made; where that list lives is `FreeEedCRM`'s, not this repo's.
  - ⭐ **The back-to-back fix of 2026-11-16 is now load-bearing, not a contingency.** Three
    consecutive days means every student arrives at Lab 07 on Jan 7 having **actually
    completed Lab 06** — which is precisely the path that stopped the Deep Dive at its first
    command until it was fixed and verified. `resume-deep-dive.sh` is **not** cohort 1's route;
    it is the recovery path for anyone who misses the Core. Both routes are tested.
  - ⛔ **`outline.md` does NOT change, and a future session should not "fix" it.** It describes
    the Deep Dive as *"one day, scheduled separately"* — that is the **product**, and the
    product is unchanged. Jan 5–7 is **this cohort's schedule**, which is the "back to back on
    request" case `CLAUDE.md` already allows. Product statement and cohort schedule are
    different things; do not collapse them.
  - **What the seven weeks are for, in priority order** — and these are now deadlines rather
    than intentions:
    (1) the **Day 1 dry run against the clock** — still never done; (2) the **PPTX decks**
    (Mark's to build); (3) **`verify-setup.sh` and `labs/SETUP.md` out to every registrant by
    2026-12-22**, a fortnight ahead — hard now that the date is fixed, because the failure
    modes are a 5 GB model download and corporate install restrictions and both are discovered
    too late by default; (4) **time Day 3**, which has never been timed and is now sold as a
    dated day.
  - ✅ **RESOLVED 2026-11-17, in two passes.** I rebuilt form 4129 field 12 to name January 5–7
    (label plus a **Core-only** option, which the old field could not capture — it now says
    *which product* each registrant wants, on the dates, in one tick), described as *"held, not
    booked"*, which was correct while the dates were tentative. **Mark then set the dates**, and
    the FreeEedWeb session completed it: the description now reads *"The dates are set"* and
    **choice 3 became the waiting list**. ⚠ **My half left the field self-contradictory for the
    interval** — label asserting a date, description denying it — and it also left *"The dates
    are set"* under a hero still reading *"Dates are being set now"*. That session corrected
    **four strings** in page 4132, two of which occur **twice** (*"Get the dates first"* → *"Reserve
    my seat"*, and *"scheduled separately"*). **Lesson worth keeping: the date was never one
    string.** Elementor cache cleared, verified signed out, guardrails intact. Detail in
    `FreeEedWeb` C12 and guardrail 1 (third version).

- ⛔ **Never quote freeeed.org copy from a saved fetch, and never tell a peer session that Mark
  approved wording he approved only in principle.** 2026-11-17: this session sent FreeEedWeb a
  hero-line change order quoting the "CURRENT" page text from a scratchpad fetch taken before
  revision 01's C9. The quoted phrase *"the job legal tech is hiring for and nobody trains"* had
  already been removed from the live page, and **guardrail 7 in
  `FreeEedWeb/docs/legal-ai-engineering-page-copy.md` forbids it and any synonym** — Mark bounded
  it on 2026-11-15: the page may claim scarcity of **integration**, never scarcity of training.
  Reinstating it would have been a regression, and it was caught only because that session
  re-fetched the page instead of trusting the quote. The occurrence count was verified against
  the string this session believed was live rather than against the page — which is the same
  class of error as assuming the date was one string, one level up. **Re-fetch before quoting,
  and say "approved in principle, wording unreviewed" when that is what it is.** A peer relaying
  Mark's approval is not Mark's approval, and FreeEedWeb was right to ask him.
  - 🔴 *(Original finding, kept — it is why the field was rebuilt.)* **The live form offered only
    Nov 30 and Dec 7 while the dates had moved to Jan 5–7.** Verified live 2026-11-17: form 4129 asks *"Which of these weeks could work
    for you?"* with **Week of November 30 / Week of December 7 / Neither — I would need a
    later date**. Jan 5–7 is *"Neither"*. So the first cohort is being asked to choose between
    two weeks the instructor has tentatively moved away from, on a page whose premise is
    *"registrants choose from the dates first"*. **Carlene's 11-16 invite points at this
    form**. ✅ **Resolved on the CRM side 2026-11-17:** that session had been reasoning toward
    Dec 7 from its own repo while the date decision lived in this one; it has struck that and
    recorded Jan 5–7 as tentative. **The page itself is still wrong** and that is the open
    part. ➡ Raised as **C12** in
    `FreeEedWeb/docs/legal-ai-engineering-page-revision-01.md` and sent back to that session.
    ⚠ Note for the record: **the built form diverged from the change order in exactly the way
    the change order warned against** — B2 specified a free-text *"Which weeks or months would
    work for you?"* precisely so the page would never name a week we had not committed to.
  - ⬜ *(Superseded 2026-11-17 by Mark setting the dates: "tentative, so nothing downstream may
    state it as fixed". It may now be stated as fixed.)*
  - ⚠ **Day 3 is the Deep Dive and it has never been timed.** Jan 5–7 sells it as a day. See
    the Risks table.
- **Week of 2026-11-16 — meeting with Carlene Gordon to set the delivery dates.** Exact day
  Unknown. Two things must be true before any date Mark agrees to in that meeting:
  1. **The Day 1 dry run against the clock has happened** (priority 2, still open). The
     playbook timings are estimates, never measured. Do not commit to a date that leaves no
     room to discover Day 1 runs long.
  2. **The student's environment has been checked at least a week ahead.** `verify-setup.sh`
     goes to her before the session, not on the morning. The failure modes are a 5 GB model
     download and corporate install restrictions, and both are discovered too late by default.
- **Calendar note for that conversation:** US Thanksgiving is **2026-11-26**, so the week of
  Nov 23 is effectively gone. The first clean two-day windows are the weeks of **2026-11-30**
  and **2026-12-07**; later December runs into year-end, which is a bad season for legal.
  - 🆕 **2026-11-16 — the choice got cheaper, not harder.** Steve Wolfe is in and
    date-flexible, so enrollment no longer argues for the earlier window. Against that: the
    dry run is the week of Nov 16, so **Nov 30 leaves one week** to act on whatever the labs
    surface and **Dec 7 leaves three**. Mark's call, and nothing in the course now pulls
    toward Nov 30.
- Nothing else fixed.

## Important TODOs

- 🆕 **Install Ollama and pull the two models on the teaching machine — before 2027-01-05.**
  This machine has no Ollama and no GPU it can use for inference, so local mode cannot be
  demonstrated on it today. Students can sit the whole course on CPU in `offline` mode and
  lose nothing measurable, but **the instructor cannot**: Modules 4, 5 and 6 argue local-first
  and the narration assumes a model answering on screen. Either `ollama pull qwen3:8b` +
  `nomic-embed-text` here and accept CPU latency on a *small* corpus for the demo, or teach
  the model-facing beats from a machine with a GPU. Decide which, then rehearse on it —
  `verify-setup.sh` now reports exactly this.
- **`labs/07-Score-and-Package/README.md` has no stated duration** — the only core lab
  without one, and it sits inside the Day 2 block that does not fit. Time it during the dry
  run and write the number in.
- **The capstone's pair exercises assume a classroom.** Lab 08 schedules a defense round "in
  pairs, 15 minutes each way" and a round-the-room reading of a partner's best question.
  With a single student Mark is the partner; that works and is faster, but the playbook
  should say so rather than leaving the instructor to improvise in the first delivery.

- Commit and push.
- Dry-run Day 1 with a timer; correct the playbook timings from measurement.
- ~~Decide whether `slides/09`–`12` (the optional Day 3) ship as a separate sellable module.~~
  **Decided 2026-11-15:** Modules 10 and 12 are the Deep Dive, with Module 7; 9 and 11 are
  electives.
- **Price the Deep Dive.** It is now a product a buyer can decline, which a three-day default hid.
- **Decide when the six months of support and updates start** when the Core and the Deep Dive are
  weeks apart. `outline.md` says "the last day of class" and that is now ambiguous.
- Re-verify Module 5 and Module 11 against FreeEed's current sizing tiers before first
  delivery.
- Consider a short student-facing one-pager on "your AI use is itself discoverable"
  (*Morgan v. V2X*) — it is the most quotable thing in the course and currently lives only
  inside Module 1.

## Blockers and dependencies

| Item | Depends on |
|---|---|
| PPTX decks | Mark running `slides/gen.sh` (standing instruction: Claude never regenerates them) |
| Module 5 / Module 11 accuracy | FreeEed's pinned model list and sizing tiers staying current |
| SAIS-100 overlay wording | SAIS-100 definition in `es-marketing/drafts/sais-100-*.md` |
| First delivery | No dependency — the material is ready to teach |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Perishable market statistics.** Module 1 Part 1 quotes the 2026 ILTA, Wolters Kluwer and Thomson Reuters surveys by number. Adoption figures age in months, and two of the three reports were already fielded in 2025. | Medium | Re-verify against the primary reports before each delivery; the presenter notes carry the URLs, respondent counts and fieldwork dates needed to do it in fifteen minutes. The slide's argument survives the numbers moving, because the argument is the gap between *adopted* and *implemented*. |
| **Case-law currency.** *Morgan v. V2X* (D. Colo., Mar 2026) is cited as the anchor for "your AI use is discoverable". Legal-AI case law is moving fast and a stale citation is a credibility problem in this audience. | Medium | Re-check before each delivery. Treat the citation as perishable. |
| **Model-ID drift.** `qwen3:8b` / `qwen3:14b` / `nomic-embed-text` are named in CLAUDE.md, the slides, the labs and the manifests. | Medium | `validate-course.sh` checks the pins agree between `CLAUDE.md` and `labs/common/llm.py`. Extend if more pins appear. |
| **Reference outputs are corpus-dependent.** The playbooks quote numbers measured on the default corpus; a student running `--docs 300` sees different ones. | Low | Stated in `labs/README.md` and `labs/SETUP.md`. The *findings* are seeded to survive both sizes. |
| **The course is named after a JD-gated job title.** Four of six employers require a JD for the role titled *Legal AI Engineer*; the roles our graduates can actually win are titled *Forward-Deployed Engineer*, *AI Automation Engineer* or *Legal AI Engineer (Contractor)*. A student who takes the title literally will conclude the course did not work. | Medium *(was High)* | **Mitigated 2026-11-12, not a rename.** The market map is built: slide **What the Postings Actually Say** in Module 1 Part 2 (the title split, the Dentons pair, the salaries, what we do *not* teach) plus the handout `course-materials/legal-ai-job-market.md`, and the topic is now named in `outline.md`. The residual risk is **currency, not silence** — the slide is a dated snapshot of nine postings and says so; re-read `job-market-research.md` before each delivery. |
| **A partner is advertising our certificate before we have defined it.** The NobleProg/Govtra page carries the Legal AI Engineer Certificate and its requirements. | Medium | Settle `DEC-015` and tell Chandra what partners may and may not say. Carlene's issuance is the first real test of the same bar. |
| **Stated audience is wider than the built course.** Mark's 2026-11-11 email to Merlin describes the audience as "legal professionals looking to upgrade, or engineers moving into legal tech". As built this is Intermediate-to-Advanced **for engineers**: eleven Python labs and a capstone repository. A lawyer upgrading cannot complete them. | Medium | It was one line in a first email and it is Mark's to resolve on the call. Before anyone treats a non-engineer track as covered: it is weeks of work, not an adjustment — a parallel no-code track with different deliverables and a different certificate bar. Resolve the audience sentence before any brochure or landing page repeats it. **No longer theoretical, 2026-11-15 (risk raised to High in practice, not yet in this column):** Mark's four lined-up targets are now recorded in `FreeEedCRM/contacts.csv`, and they split three ways — two engineers who can do the labs, one eDiscovery practitioner (the dry run), and one practising attorney who cannot complete them and is therefore a private-cohort sponsor rather than a seat. Two of four cannot take the same course, and the freeeed.org **advance signup** page now waiting on this decision has to say which one it is. ⭐ **2026-11-15 — this stops being an argument and starts being data.** Mark: *"perhaps we need both A and B"* — A being this course, B a **Legal AI Implementation** course for legal-technology professionals (adoption, configuration, vendor evaluation, workflow, governance; no coding). `FreeEedWeb` revision 01 C10 adds a checkbox for B to the live signup form, worded as demand measurement and committing to nothing, so the first fortnight of registrations answers what four hand-picked names currently decide. ⚠ **Before B is built, the real constraint is not demand:** its substance is evaluating and configuring RelativityOne, CoCounsel, Harvey and Copilot Studio — products this instructor does not teach, named in our own job-market handout as the course's **largest gap** — and B competes in the half of the market where *"nothing left the building, and here is the proof"* carries least. B is not a smaller A. |
| **Six months of support and updates is now a promise in the contract.** `outline.md` commits every participant to six months of the instructor's email support and six months of course-material updates. The volume is unbounded, the cost is unpriced, and when a **partner** sells the seat it is not stated who honours it — NobleProg's ~$2,700 online rate was set before this existed. | Medium | Decide the bounds before the first cohort (decision 9): what support covers, how updates are delivered (a repo invitation is the cheapest honest answer), and whether a partner seat includes both. Cheap to scope now, expensive to walk back after a cohort has been told. |
| ⬜ **Clock (set aside by Mark 2026-11-15).** 9–4 Central is ~5:45–6:10 of teaching against a Day 2 measured at ~7:05. Recorded in decision 0; **not an open action.** | — | Mark's call; do not re-propose. |
| 🔴 **A FreeEed capability this course names does not ship. Found 2026-11-15.** `outline.md`, `README.md` and the new freeeed.org course page all described FreeEed as doing **"Bates and load-file production."** Checked against **tag v10.8.7** and the published release notes: the only Bates code is a commented-out `// TODO this was for Bates, but this is not how it should be implemented` in `EmailUtil.java`; `docs/specs/esi-production-format.md` is a **specification** with tracking issue **#551**; the GitHub release notes for 10.8.4.1–10.8.7 say *"process, search, review, and **export**"* and never say Bates, Concordance, Opticon, load file or production. ⚠ **The canonical source carries the error too** — `FreeEedCRM/docs/technical-primer.md` line 19 lists `production (Bates/load files)` in the ships-today product line, and that primer is the anti-overclaim file everything else copies from. Corrected here; **the primer and the freeeed.org page still need it.** ⭐ The course's own Lab 07 production set is unaffected — students build that in Python; the claim at issue was only ever about the product. | **High** | ⭐ **2026-11-17 — the outline no longer needs the carve-out, because it no longer makes the claim.** Mark: *"this is too much details... just say in general."* The bullet had grown into a parts list (Tika, 1,400+ file types, OCR, imaging, PST/OST, Solr/Lucene, review, export) with the ⛔ Bates disclaimer, issue number and verification tag inline — provenance for us, printed in a document for participants. It now says FreeEed is the platform the instructor ships and the labs are designed against, and nothing about what it does feature by feature. **An enumeration is what created the overclaim; removing the enumeration removes the need for the disclaimer.** ⛔ The carve-out is still live wherever a capability list survives — if anyone re-enumerates FreeEed's features anywhere, the Bates/load-file exclusion comes back with it. ⬜ **DEFERRED by Mark, 2026-11-17 — "this is all beyond constructing the course. can i do it later." Yes.** **This course repo is clean**: every remaining Bates reference in it is about what students *build* (Lab 07's production set) or Bates as a search concept — no file here claims FreeEed ships production. The three left are all in other repos and none of them is Mark's to edit: **(1) `FreeEedCRM/docs/technical-primer.md`** — one line, and the one that compounds, because it is the designated anti-overclaim source every other document copies from, so the error regenerates while it stands; **(2) `FreeEedWeb/ask-freeeed/capability-map.md`** — derived from the primer, so fix it in the same pass or it is just re-derived wrong, and it feeds the assistant that answers visitors; **(3) the freeeed.org page** — state unverified from here, and ⛔ this session must not assert it (see the re-fetch rule): one grep by the session that has the page loaded settles it. ⚠ **The trigger that ends the deferral:** anyone writing new FreeEed capability copy from the primer — a quote, a brochure, the NobleProg or Chandra Tan listing. Until then it is a 10-minute handoff to two sessions, not a task on Mark's list. Then ask whether #551 is close enough to say "specified, not yet shipped" in public — which is a true and perfectly good sentence. |
| **Neither product has been run against a clock.** The Deep Dive is a sold day — Modules 7, 10, 12 and three labs — and no day of this course has ever been timed. Day 2 of the Core sits at ≈7:05 against 6.5 hours on paper (decision 0). If the Deep Dive does not fill a day we are charging for a short day; if it overflows, the electives have nowhere to go. **The 2026-11-15 split raises the stakes: the Deep Dive is now a separate purchase, so a thin day is visible on its own invoice.** | 🔴 **High, and now unmitigated (2026-11-18)** | ⚠ **The mitigation named in this row no longer exists.** Carlene cannot run before Jan 5 (Mark, 2026-11-18), so **no measurement precedes the first paying room** and Jan 5–7 is itself the dry run. What is left: **a solo timed run-through** (priority 2), and **deciding in advance what comes out of Day 2** rather than discovering the ≈35-minute overage live at 3pm. Time all three days during the January delivery and replace the playbook estimates with real numbers before any second cohort or channel re-pricing sticks. |
| **Lab 07's pipeline refuses to run on a work tree where Lab 06 was done by hand.** Found 2026-11-15 while building `resume-deep-dive.sh`. `defensible_review.py protocol` refuses to overwrite an existing `validation-protocol.md` — deliberately, *"that refusal IS the control"* — and Lab 07's `run_matter.py` re-runs that stage, so it fails at stage 9 and nothing after it runs. **This is the documented path**: Lab 07's README says *"if you have been following the pipeline, your `labs/work/` already has what this lab consumes."* `test-all-labs.sh` never catches it because it runs Lab 07 into a separate `work-matter` directory. **The split makes it worse** — the Deep Dive now opens with that command, weeks later, in front of a room. | **High** | Not fixed; **Mark's call, because every option changes lab behaviour or lab text.** Three candidates: (1) `run_matter.py` adopts pre-existing artifacts into `_state` instead of re-running them; (2) it passes `--force` to `protocol` only when no classification has run yet; (3) Lab 07's README tells the student to use a fresh `--work ../work-matter`, which is what the smoke test already does. **Whichever is chosen, `test-all-labs.sh` should also run Lab 07 over the hand-built tree, or the next regression hides in the same blind spot.** |
| **SAIS-100 has no external recognition, and its spec has never been published.** NobleProg's public page already names SAIS-100 to buyers who can search for it and find nothing; the rubric exists only as four July 2026 drafts in `es-marketing`. In a course whose brand is *do not overclaim*, teaching a proprietary score with no published spec is the one place the course is exposed to its own charge. | **High** | Two drafts written 2026-11-12. (1) **`course-materials/sais-100-framework-mapping.md`** — committed: every category translated into NIST AI RMF, ISO/IEC 42001, EU AI Act and the governing legal authority, with the honest "what it is not" section. (2) **A public one-page spec**, drafted but **not placed** — `es-marketing` is read-only, so it needs Mark to drop it in and publish. Until it is published the exposure stands. |
| **Overclaiming.** This course's whole pitch is honesty about limits; a single overclaim costs more here than in any other course we teach. | Low | Honesty is enforced in the material itself — offline fallbacks announce that they are worse, and attestations carry a `scope_and_limits`. |

## Decisions needed from Mark

0. **Day 2 overload** — *Decided 2026-11-11: **Module 7 / Lab 07 move to Day 3**, as the
   **floating module** — pulled forward into Day 2 whenever the room is fast enough. Mark is
   content to sell three days otherwise.* Effect on the clock:

   | | Lecture | Labs | Total | vs 6.5 h |
   |---|---|---|---|---|
   | **Day 1** — M1–M4, Labs 02–04 | ≈ 2:15 | 3:00–3:45 + 0:30 | **5:45–6:30** | fits |
   | **Day 2** — M5, M6 + capstone, Labs 05, 06, 08 | ≈ 1:20 | 5:45 | **≈ 7:05** | ~35 min over |

   ⬜ **SET ASIDE BY MARK, 2026-11-15 — recorded, not open.** The arithmetic below is kept because
   it is true and cheap to re-read; ⛔ **do not raise it as an action item or re-propose cuts
   unless Mark asks.** The course sells at 9–4 and the dry run will say what it says.

   **2026-11-15 — the "vs 6.5 h" column is wrong, and it was the column that said "fits."** Mark set the delivery window for freeeed.org: **live online, 9:00–16:00 US Central.**
   That is **7:00 gross**, and an online day cannot skip lunch or breaks: a 45-minute lunch plus two
   15-minute breaks leaves **5:45 of teaching**; a tight 30-minute lunch and two 10s leaves **6:10**.
   So the real bar is **5:45–6:10, not 6:30**. Against it:

   | | Content | vs 5:45–6:10 |
   |---|---|---|
   | **Day 1** | 5:45–6:30 | fits at best, **~45 min over at worst** |
   | **Day 2** | ≈ 7:05 | **~55–80 min over** |

   ⚠ Day 2 was "35 minutes over, close enough to absorb 1:1 or with a tight lunch." **An online
   9–4 day has no 1:1 and the tight lunch is already priced in above.** The honest reading is that
   Day 2 needs roughly an hour cut, or the window moves (9–4:30, or 8:30–4), or Lab 08's capstone
   time is formally shortened. ⭐ **Carlene's dry run is still the measurement** — but it should now
   be run **to the 9–4 clock**, not to a generous day, or it will not answer this.

   The move removes roughly 1:45 from Day 2, which was over by 2:00–2:30. **It is now about
   35 minutes over, not two hours** — close enough to absorb 1:1 or with a tight lunch. The
   only remaining lever is the capstone's 3:00 block; cutting it to 2:30 would close the gap
   outright, and that decision is still open.

   What the two-day room gives up when Module 7 is not pulled forward: the **document
   production set** (`production/VOL001/`) and the **containerized deployment**. What it does
   **not** give up: the certificate — the capstone drives Labs 02–06 itself and runs
   `sais100.py`, so `sais100-score.json` and issuance check 4 survive.

   *Superseded in part 2026-11-12:* Day 3 is **no longer a menu**. See decision 4.

   *Re-confirmed 2026-11-15, and this table is why:* the Core/Deep Dive split put Module 7 back
   into Day 2 on paper and reverted it in the same session. Day 2 without it is **≈7:05**; with it,
   **≈8:50**. The capstone's 3:00 block remains the only lever and the decision is still open.
   **Nothing should move into Day 2 until a measured Day 2 exists.**

1. **Monetisation model** — *Decided 2026-11-10. The ladder is:*

   > **discounted course → paid certificate → paid support → FreeEed**

   Note what was rejected: the course is **discounted, not free**. A discount keeps a list
   price on the table, so the first student is receiving a pilot rate rather than being
   taught that the course is worth nothing — and every later quote still has an anchor.
   The four rungs are settled; **every number in them is Unknown** (list price, pilot
   discount, certificate fee, support rate) and they are the next thing to set, after the
   Day 2 question in decision 0. Mark's stated second motive for the support rung is a
   **flow of real-world use cases** feeding FreeEed. The GM read on the rungs:
   - **Paid certificate is the cleaner line**, but note the difference from Ng: his bar is
     automated at scale, ours needs Mark to run `VERIFY.md` per student. That is what makes
     it worth more, and it is fine at low volume. The tension to settle *before* anyone pays:
     when the certificate is the revenue, failing a candidate costs money. Framing that
     resolves it — **the fee buys the assessment, not the pass** — plus the published four
     checks, the roster, and a free retake.
   - **The use-case flow cannot run on client data.** Module 5's own slide says disclosure to
     a third party can waive privilege; in a support channel Elephant Scale *is* the third
     party, and the privilege is the student's client's to waive, not the student's. Default
     answer to "will she have permission": no, and often she cannot grant it.
   - **The workable version** is problem shapes, not matter facts — volumes, file-type mixes,
     deadlines, constraints — reproduced **on the synthetic course corpus**. That is full
     value for FreeEed roadmap purposes, needs no permission, and is the classroom ground
     rule ("no client data in any tool") extended to support. Real matter detail would need
     an NDA, and for privileged material engagement through counsel.
   - **Reuse is a separate grant.** Marketing, case studies or course material built on these
     cases needs explicit written permission, anonymised — cheap as an opt-in at signup,
     awkward to retrofit.
   Still to settle before any offer is made:
   - **Do not call it free; call it what it is.** ⚠ **SUPERSEDED IN PART, 2026-11-18 —
     Carlene is no longer the dry run.** She cannot run before Jan 5 (Mark), so the rehearsal
     this clause was built on does not exist and **the first paying cohort absorbs the risk
     instead**. Two things survive the change. The fee question is already settled by the
     ★$100/day rule (she pays $300, like everyone in cohort one), so **no renegotiation
     follows from her date moving** — the rule set on 11-17 absorbed it. And the principle
     stands: publish a list price alongside any discount, so the discount has something to be
     a discount *from*. ⛔ **How Carlene's own dates are arranged is Mark's**, per the
     2026-11-17 standing instruction; what is recorded here is only the consequence for the
     course.
   - **Bound the support.** "Support on the issues covered" is unbounded as written. A
     defined window and channel (for example 30 days, email, course topics only) can be
     given away safely; anything open-ended cannot, and this student will have a real matter
     and a real deadline behind her questions.
   - **Decide what Elephant Scale gets.** A reference, a testimonial, permission to name the
     first certificate holder, or a case study — all of which are worth more than one
     student's fee at this stage, and none of which happen unless they are asked for on
     Tuesday.

2. **Certificate brand infrastructure.** *Decided 2026-11-10: the certificate stays.* Mark's
   direction is that the **Elephant Scale Legal AI Engineer Certificate** will become a brand
   name, so the course now awards it and `outline.md`, the capstone deck, Lab 08 and the
   rubric all say so again. The teaching side is done: the bar is objective (attendance,
   module labs, and a capstone that passes its own `VERIFY.md` with no legal auto-fail), the
   issuance checklist and the borderline cases are in Lab 08's Teacher's Playbook, and the
   roster record is specified. What still needs Mark, as business rather than curriculum:
   - the certificate **artifact** itself (design, PDF, who signs it);
   - whether holders are **verifiable** — a registry, a serial number, or nothing;
   - the exact **name** on the document. *Decided 2026-11-12: the name now carries the issuer —
     **Elephant Scale Legal AI Engineer Certificate** — in `outline.md`, deck 08, Lab 08 and the
     capstone rubric.* HQ's `DEC-015` (2026-11-10) already takes a position:
     the **certificate form**, not the holder-form "Certified Legal AI Engineer", because a
     professional-title claim with no accrediting body is the one overclaim this course's own
     material would fail. It is now ES's brand call, but reversing it contradicts Module 1;
   - whether this is the **first of a family** across the Secure AI Learning Path, which would
     decide the naming now rather than after the first cohort;
   - **Resolved 2026-11-12.** The outline briefly named the award two ways — a "certificate of
     completion" in the takeaway section and the branded certificate under Assessment. Mark's
     call: **one award, the branded one**, in both places and on deck `00-about`. So there is no
     completion-only tier: every certificate carries the SAIS-100 / no-auto-fail bar, and a
     participant who attends but does not pass the capstone gets no certificate. Say that to
     partners, because NobleProg is selling seats against it. **The signature line is still a new
     commitment** — somebody signs each one, which is a per-cohort task and an argument for a
     serial number rather than a wet signature.

   **Can ES award this with no outside body? Yes — as a certificate, not a certification**
   (analysis 2026-11-12). A certificate is a factual statement by its issuer: *ES taught this,
   this person met this bar.* No accreditor is needed or involved, which is how every vendor
   credential works. A *certification* asserts an external professional standard, and that is
   the claim ES cannot make alone — the reason `DEC-015` chose the certificate form. Three
   consequences:
   - **Name the issuer on the face of it** — the *Elephant Scale Legal AI Engineer Certificate*.
     That word converts a free-floating credential into an attributed one, and it is the brand
     asset anyway.
   - **Four claims to avoid**, each of which needs a body that does not exist: "Certified Legal
     AI Engineer" or any post-nominal; "accredited" / "approved" / "recognized"; **CLE credit**
     (states accredit the *provider*; ES is not one — the answer is "no CLE credit" until it is,
     and lawyers will ask in the first ten minutes); and any suggestion that employers require
     or recognise it, which `job-market-research.md` contradicts.
   - **Put the bar on the certificate** — hours, module labs, and a capstone that passed its own
     `VERIFY.md` with no legal auto-fail. Every other training certificate is an assertion; this
     one would carry its evidence, and the holder also has the repository. It is the only version
     that survives the cross-examination test Module 1 teaches.

   *Verify before print, not before deciding:* **"engineer" is a protected title** in some
   jurisdictions (Canadian provincial bodies enforce it; a few US states restrict it). The
   exposure is in the holder-form claim, not in a course named after a title employers advertise
   themselves — and NobleProg sells into Canada, so it is their exposure too.
3. **FreeEed wording.** Five lines were softened from implying shipped capability to
   "reference platform / reference architecture the labs are designed against", naming only
   capabilities backed by `FreeEedCRM/docs/technical-primer.md`. Confirm this is how you want
   FreeEed positioned in course marketing.
4. **Day 3 packaging** — *Decided 2026-11-12: **the course is three days**, with a condensed
   two-day version. This supersedes the 2026-11-10 "Day 3 stays optional" decision.* The whole
   repo now says so: `outline.md`, `README.md`, `CLAUDE.md`, `labs/README.md`, `labs/SETUP.md`,
   eight decks and five lab READMEs.

   **The shape:**
   - **Days 1–2** — the build path, unchanged. Capstone and SAIS-100 score on Day 2, so the
     certificate bar is met in two days either way.
   - **Day 3 — "ship it, oversee it, prove it"** — Modules **7** (Ship It), **10** (agentic,
     with human oversight designed rather than promised) and **12** (governance audit).
   - **Modular series** — Modules **9** (investigations) and **11** (deployment at scale),
     sold separately or swapped into Day 3 on request. 9 is what an eDiscovery audience asks
     for; 11 is what public-sector and government-cloud buyers ask for.
   - **Condensed two-day version** — Day 3 dropped, Module 7 floating forward into Day 2 when
     the room is fast enough. **The cut is decided before the class, not at 4pm on Day 2.**

   **Why three, and why the default matters.** The default is what a partner lists and what
   anchors the price; options get ignored. "Optional Day 3" means upselling a buyer who has
   already decided on two days — almost nobody is. "Condensed two-day" means the buyer asks for
   a discount and *we* choose what drops. At NobleProg's own flat rate this is **~$2,700 →
   ~$4,050 online** and **~$3,900 → ~$5,855 classroom** per seat, for material already written
   and already passing `test-all-labs.sh`. The counter-cost is real: a third day crosses an
   approval threshold at many firms where two days is only a calendar decision, so expect a
   lower conversion rate at a higher price per seat.

   **Still open:** Day 3 has never been run against a clock either, and Modules 7 + 10 + 12
   with three labs is the same shape as Day 1, not obviously a day. Measure it.

   *Superseded 2026-11-15: **the course is a 2-day Core plus a separately scheduled 1-day Deep
   Dive**, with Modules 9 and 11 as electives.* The contents are unchanged — Core = Modules 1–6 +
   capstone, Deep Dive = 7, 10, 12 — so this decision's shape survives; what changed is that the
   third day is **sold and scheduled on its own** rather than as day three of a block, because
   three consecutive days is the hardest thing to ask of a working legal team. Consequences:
   the "condensed two-day version" and the floating Module 7 are both **retired**; the Deep Dive
   needs **its own price**; and it needs the Core's work tree to exist weeks later, which is what
   `labs/resume-deep-dive.sh` is for. Three consecutive days stays available on request, so the
   ~$4,050 online / ~$5,855 classroom three-day figures above still apply to that booking.
5. **Target first delivery** — *Superseded 2026-11-10:* Carlene Gordon is the first
   student; dates are set after the 2026-11-17 conversation.
6. **Three open questions on the validation dimension.** Raised by HQ 2026-11-11 and drafted
   at `Scaia-Operations/drafts/tredennick-defensibility-rubric-ask-2026-11-11.md`. They are
   unresolved in the material as written, and this course grades people on them:
   - **"With an interval" may not be a real bar.** A student can report a confidence interval
     so wide it says nothing and still earn the marks. Either the rubric names a precision the
     interval has to reach, or it stops implying one.
   - **Elusion as the primary measure** is taught as settled, and probably is — but "probably"
     is doing work in a document that decides who is certified.
   - **LEGAL-D (the model cannot be pinned)** sits beside three genuine legal failure
     conditions while being an **engineering** instinct. Privilege waiver, ethical walls and
     unapproved production each have law behind them; "an unreproducible review is
     undefendable" may never have been tested where it mattered. It may still belong — as a
     named engineering condition rather than a legal one.
   - These are good questions to put to Tredennick if the call happens; he grades
     defensibility commercially. **Needs CEO input** — I have not changed the rubric on any of
     the three.

7. **Advertise or free webinar?** — *Answered by research 2026-11-11: **webinar, not
   advertising**, and not yet.* Mark emailed a partner's `customerservice` inbox on 2026-11-11
   asking this. The research answer, in `marketing-channels.md` §4: there is nowhere for an ad to
   land (no ES page, no published price, no dates, no dry run), the free educational webinar is
   the native format of this market (ACEDS runs them with sponsors as a standing series), a
   webinar produces the recording and the registrant list that advertising does not, and we now
   have a non-promotional topic — *what six Legal AI Engineer postings actually require*. Two
   process notes. A generic `customerservice` address is the weakest door into any of these
   organisations, each of which routes this to a named team (ILTA `sponsor@`/`events@`, CLOC
   `sponsorship@`, LawNext `info@lawnext.com`, ACEDS via its Affiliate Partner Program). And
   **if that email went to NobleProg — confirmed by Mark 2026-11-11 as the channel — the person
   to talk to is Chandra Tan, not customer service.** She asked for the outlines on 2026-11-05,
   she publishes the pages, and she already has this course listed for sale. The stronger pitch
   is not *"advertise or webinar?"* but *"I have research on legal-AI hiring and a 45-minute
   session built on it — who runs your education calendar?"*
8. **Which course gaps to close, and when** — *Needs CEO input. **P1 item 1 built
   2026-11-12** (Mark: "yes, build it") — the Module 1 market map slide and handout; the rest
   unstarted.*
   Recommended P1, all cheap and none touching a lab: ~~the Module 1 market map~~ **(done)**; a
   **platform-equivalence appendix** (what you built / what you would configure instead in aiR,
   CoCounsel, Harvey, Copilot Studio / what you still owe a court either way); and a
   **vendor-evaluation handout** in `course-materials/`, built on the Module 5 spectrum and the
   new three-architecture slide. P2, real work: human-oversight design, an adoption unit, MCP in
   Lab 10. P3: eval-platform and observability literacy, and naming LangGraph once. **Not
   recommended:** a no-code track for JD-holders — weeks of work, contradicts the positioning,
   and the JD-gated roles want a practising lawyer, not a lawyer with a Python certificate.

9. **Scope the six-month support and update promise** — *Support scope **decided 2026-11-12**;
   update delivery still open.*

   **What email support covers — decided.** The published scope was already "your own build, not
   just the labs"; the decision is the fence around it, now in `outline.md` and deck `00-about`:
   architecture, what to measure, how to defend it — **best effort, by email, personal to the
   named participant, six months from the last day of class**; **no client data, a synthetic
   reproduction or a description only**; a live matter, or work that turns out to be a project,
   is **quoted separately**.

   Four things that fence buys:
   - **The confidentiality hole is closed.** A student would otherwise paste a privileged
     document into a support thread to show why their extraction is failing. For a course whose
     argument is that privileged material should not land in someone else's inbox, it cannot
     land in ours. The deck now tells the instructor to say this out loud, not let them read it.
   - **Personal and non-transferable**, so one participant at a large firm does not become a
     help desk for forty.
   - **Best effort, no SLA** — a medium is promised, not a deadline. Delivery weeks are slow.
   - **"A project is quoted"** turns the cost into the top of the monetisation ladder. Someone
     asking a hard question six weeks after class is a qualified lead.

   **Cost — estimated, not measured.** A cohort of twelve, perhaps a quarter ask anything at all,
   one to three threads each: a handful of hours spread over six months. Revisit after the first
   two cohorts with real numbers.

   **Partner-sold seats — resolved by the wording, pending one confirmation.** Support is from
   *the instructor*, and ES supplies the instructor whether the seat was sold direct or through
   NobleProg, so there is no two-tier product and nothing to carve out. **Confirm with Chandra
   that NobleProg books the ES instructor rather than delivering with its own trainer** — if
   they ever deliver it themselves, support is theirs to provide or to buy from us.

   **Also settled in passing:** the support scope is what makes SAIS-100 answerable after class —
   a graduate asking "how do I explain our score to a security reviewer" is now a handout away
   (`course-materials/sais-100-framework-mapping.md`), not an email.

   **Still open — how updates are delivered.** A read invitation to the course repository costs
   nothing and is self-maintaining; a mailed archive per release is a recurring chore. The
   outline deliberately does not name a mechanism, so this can be settled without re-issuing it.

10. ⬜ **How any participant attends who does not write Python — RECORDED, NOT OPEN.** Mark
    runs student organisation himself (2026-11-17, above), so this is not a decision waiting on
    him and **must not be re-raised as an action item**. What is kept is the set of constraints
    the course itself imposes, because they are facts about the product that any future session
    will otherwise re-derive — or worse, soften:

    - **The Core is eleven Python labs plus a capstone repository, and the capstone is
      assessed.** Completing it is the certificate bar (item 2). ⛔ A softened first issuance
      would devalue the credential permanently — that holds for every participant, including
      the first cohort.
    - **Attending without completing the labs is possible and gives real value** — Module 1,
      Module 5's three-architectures choice, the governance material, and ~700 lines of
      non-code handouts in `course-materials/`. **It does not earn the certificate**, and the
      only unfair version of it is the one nobody said out loud in advance.
    - **A private cohort is a real, already-offered route** (`outline.md`, and the signup form
      has the checkbox) and is the shape that fits a sponsor rather than a lab-completing
      student.
    - ⛔ **Building course B is not an option on this timescale.** Weeks of work; its substance
      is RelativityOne / CoCounsel / Harvey / Copilot Studio, which this instructor does not
      teach and which our own job-market handout names as the course's largest gap. The
      standing decision (Mark, 2026-11-15) is **stay with A, measure B**.
    - **Lead time is the one lever this repo controls and it is already pulled:**
      `verify-setup.sh`, `labs/SETUP.md`'s measured requirements, and Jan 5–7 giving seven
      weeks.

    ⚠ **The one thing that would still change the course rather than the roster:** if the
    stated Python levels come back low across the cohort, that is the **paced cohort** the
    signup form already measures demand for — and that is a build decision with weeks in it,
    not a seating decision. Raise it only if the data says so.

11. **How long is an elective?** — *`Unknown`. Needs CEO input, and it is the hole the sales talk
    was covering.* `outline.md`'s Duration field read *"(electives sell on their own)"* — a
    commercial statement standing exactly where a length belongs, **because no length has ever
    been set.** Nowhere in the repo states one. What is known: each elective is one module plus
    one lab, and the Core's comparable pairing (Module 7 + Lab 07) was timed at **1:45**, so one
    elective is likely a **half day at most** — which does not obviously sell on its own at a
    day rate. Three shapes, and this is a pricing decision rather than a content one: a
    **half-day each**, **both together as one day**, or **bundled only as a Deep Dive add-on**.
    ⚠ Not urgent — nothing in the Jan 5–7 cohort depends on it, and no elective has been sold.
    It becomes urgent the moment an elective is quoted. The outline now says their length is not
    yet fixed, which is true and safe to publish.

## After January 5 — the post-delivery plan (recorded 2026-11-18)

**Precondition: a successful January 5–7 delivery.** Everything here assumes the room went
well and produced its artifacts. Nothing here is to be started before it.

### What we are actually selling from

**Builder standing, not institutional standing.** Mark wrote FreeEed, it ships, and Scaia has
delivered under CJIS constraints. Stanford has institutional standing; Harvey has product
standing plus the firm relationships that come with already being installed; UC Law SF has a
law school. ⛔ **Never compete on credential** — that fight is lost before it starts. Compete
on the one question we answer absolutely: *has this person built one and run it against a
regulator?* ➡ **Therefore every marketing asset is an artifact, not a claim.** The
reproducibility bundle a student produces on Day 3 outranks any brochure we could write.

### What the market is

**Not "lawyers who want AI."** `job-market-research.md` is unkind and clear: four of six
employers require a JD for the title, every platform named in every posting is cloud, and
defensibility measurement appears **once** in nine postings. The individual-learner market for
*"build a defensible local pipeline"* is thin. The buyers are organizations where the security
constraint binds, and **they buy for a team, not a seat**:

1. **eDiscovery service providers and litigation-support vendors** — they build pipelines,
   answer client security questionnaires, and compete on defensibility. Closest to our product.
2. **Government** — state, county, AG offices, CJIS-adjacent. Local is the rule, not a
   preference. This is Module 11 and it is Mark's own professional history.
3. **Regulated-industry legal ops** — defense, health, financial: cloud needs an approval package.
4. **Platform vendors' forward-deployed teams** — the TR CoCounsel FDE pattern, no JD.

### The fork, and the read

**Is the course the business, or the funnel?** As the business, the ceiling is Mark's calendar:
solo delivery plus six months of support per seat means a very good year is a modest one, and it
consumes him. As the funnel — which is what this file has said from the start, *"the course is a
demand channel for the platform"* — the metric is **how many target organizations put someone in
the room**, and one FreeEed integration or CJIS engagement outweighs a year of public cohorts.
⭐ **GM read: it is the funnel.** Price and market it as one that pays for itself.
⚠ **Needs CEO input** — this is Mark's call and it changes everything downstream.

### The motion: private cohorts, not public seats

Target private cohorts at **service providers and government**. Same teaching effort, one sale
instead of twelve, a buyer whose constraint makes our differentiator binding, and it lands
exactly where Harvey, Stanford and UC Law SF are not playing. It also solves the Bisk shape
structurally: a sponsor buying a private cohort is a real product, not a consolation.

### ⛔ CHANNEL CORRECTION — outbound is dead for us, and the first version of this plan got it wrong

**Mark, 2026-11-18: no reply from ILTACON, and *"most people do not reply to my emails."*** An
earlier draft of this section recommended building a named list of 30–50 organizations and
working it directly — **outbound, through the exact channel that is not working.** Withdrawn.

- **Non-reply is a channel verdict, not a rejection.** Every inbox now holds a hundred
  well-targeted, costless messages a day; the only defense is to stop reading the category. Our
  emails are not losing on quality, they are losing on being **indistinguishable at a glance from
  things that cost nothing to produce**. ➡ Stop paying into it. Do not chase ILTACON.
- **Counter-evidence that confirms it:** Andrew Stears replied to a warm, personal note **within
  a day** (2026-11-17). Warm works; cold does not.
- ⭐ **The two real assets are both inbound: Google visibility on `freeeed.org`, and FreeEed
  word of mouth.** People already arrive without being asked, and **who searches for an
  open-source eDiscovery platform is precisely our buyer profile** — builds or runs review
  pipelines, constrained enough on cost or security not to simply buy Relativity. The
  best-qualified traffic in this market already lands on our own domain. No competitor has that.
- ➡ **The motion inverts:** make the path from *"found FreeEed"* to *"talked to Mark about
  training"* short and obvious, and let the traffic qualify itself.
- **The FreeEed user base is the list, and reaching it is not cold email.** Release notes, the
  repository, the project README — a note to people already running the software is a **product
  announcement**, pre-filtered to people who build pipelines. If `ask-freeeed` does not know about
  the course, that is a ten-minute fix with better odds than a conference submission.

### Anti-slop doctrine: publish what is expensive to fake

Slop is generic, unverifiable and costless, so the antidote is anything that costs something real
and can be **checked**: running code; specific measured results with the method attached;
**saying where it loses** (already required by `CLAUDE.md`'s house style and almost nobody does
it); and the claim only Mark can make — *here is the platform, here is the GitHub*.

⭐ **P1 after January: extract Lab 06 as a standalone public open-source tool.** *Measure your
review pipeline's recall and elusion against blind ground truth — synthetic corpus included, runs
offline, no API key.* It already exists; extracting it is about a day. It is unfakeable because it
either runs or it does not, it is useful to someone who never buys the course, it lives where our
word of mouth already works, and **it needs nobody's reply or permission**. It also compounds:
repositories accumulate links, and links are what the Google asset is made of. ➡ This outranks
the webinar, the ILTACON submission and the research post combined.

### Consequence for the unpublished outline — revisits the 2026-11-17 reasoning

On 11-17 the conclusion was *outcomes public, mechanics in a versioned attachment*, with the loss
of discoverability accepted as fine for a soft launch. ⚠ **Given that search is the real channel,
that loss is now the main cost.** Google indexes text, and today the substance of this course is
invisible to it while NobleProg's stale version is not. **The split still holds; the public half
must get substantially bigger** — real material on measuring a review pipeline, enforcing egress,
what defensibility requires. **Publish the knowledge, keep the curriculum.** The knowledge ranks;
the curriculum was never the moat.

### Marketing sequence, from January 8

1. **Write the delivery up as evidence, not as a brochure** — *"engineers built a local review
   pipeline; here is the reproducibility bundle one produced and what it proves."* Permission
   required, synthetic data only. That is the only kind of story Ambrogi covers editorially, and
   a free mention beats a paid post.
2. **Run the webinar**, now that the demo has survived a live room: score a pipeline, break
   egress, watch **LEGAL-A** fire and the verdict flip to Do Not Deploy, repair, re-score. A
   number moving, live. Co-brand with NobleProg — they hold the list and the dates.
3. **Publish the SAIS-100 legal overlay spec.** Today it is the largest exposure (a proprietary
   score with no published rubric, in a course whose brand is *do not overclaim*); published, it
   is the thing people cite. Already drafted, blocked only on placement.
4. **Course visible from FreeEed's own surfaces** — release notes, README, `ask-freeeed`.

### ⛔ Explicitly not doing

Cold outreach of any kind. Conference submissions. Chasing ILTACON. Paid search or paid social.
Filling public cohorts.

### Kill criterion

**If no private cohort has been sold to a service provider or an agency by mid-2027, the answer
is not to market harder.** It is that the business is **FreeEed and the consulting**, and the
course is the best brochure we will ever have. That is a conclusion arriving by evidence, not a
failure — so build the course's economics such that this outcome is acceptable.

## Next highest-value actions

1. **Write to Chandra Tan once, not twice** (outline owed **2026-11-19**). Mark already sent
   her an outline; what she now needs is a single message covering **one change, not four**:
   *the course is a 2-day Core plus a separately scheduled 1-day Deep Dive — please re-price and
   re-list.* **Updated 2026-11-15 and this is now the third shape in two weeks**, which is exactly
   why the earlier correction was held: send one message describing the current shape, and say
   plainly that it is the one to publish. Folded into it: the Deep Dive contents (Modules 7, 10,
   12), the electives, the new **bring-your-own-AI-subscription** prerequisite, the full certificate
   name (**Elephant Scale Legal AI Engineer Certificate**, no completion-only tier), and the
   webinar proposal. **Hold back one item**: six months of email support and updates must not go
   on her page until decision 9 settles what it covers and whether a partner seat includes it.
   This was drafted as a Module-7-moved correction on 2026-11-12 and then held, deliberately,
   because the three-day decision landed the same day — two corrections in a week to a reseller
   reads as an unfinished product.
2. **Decide the audience sentence** before it is repeated anywhere (risk table above), and
   **answer the three validation questions** in decision 6. Both are cheap now and expensive
   once a brochure exists or a certificate has been issued against the rubric. The Merlin
   call is the forcing function for the first and the best available review of the second.
3. **Dry-run Day 1 against the clock** and replace the playbook estimates with measurements.
   Carlene's session is itself the Day 2 measurement, which is the honest argument for not
   charging for it. Day 2 now sits at roughly 7:05 against a 6.5-hour day (decision 0), so
   the remaining question is whether the capstone's 3:00 block comes down to 2:30.
4. **Prepare the 2026-11-17 conversation**: the artifact list as the thing being sold, the
   certificate bar stated plainly, the support offer bounded in writing, and
   `labs/verify-setup.sh` sent to her afterwards so her machine is known well before a date
   is agreed.
