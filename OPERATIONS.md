# Project Operations

**Last updated:** 2026-11-10
**Owner:** Mark Kerzner
**Status:** Green

## Purpose and business value

**Legal AI Engineering** (`LEGAL-AI-ENG-2026`) is the legal-vertical track of the Elephant
Scale Secure AI Learning Path: 2 days core plus an optional Day 3 / modular deep-dive,
Intermediate-to-Advanced, for software and AI engineers moving into legal tech.

Why it earns its place in the catalog:

- It is **differentiated**. Generic "AI for lawyers" training teaches prompting. This course
  teaches a build path and ends with a repository the student can be cross-examined on.
- It **pulls through FreeEed**. FreeEed is the reference architecture named throughout
  (Tika extraction, OCR, imaging, PST/OST, Solr/Lucene, review, Bates/load-file production).
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
| `outline.md` | Complete. Treated as the contract for module numbers and the Day split. |
| Slides | 13 decks (`00-about` + modules 01–12), ~4,340 lines of presenter-skeleton Markdown, 185 slides, all with `Notes:` narration |
| Labs | **All 11 built and smoke-tested offline** (01–07 core, 08–11 optional Day 3), ~9,500 lines of Python, ~3,800 lines of lab README including Teacher's Playbooks |
| Course materials | 7 documents (design canvas, defensibility checklist, TAR metrics cheat sheet, privilege/egress attestation form, reproducibility manifest template, SAIS-100 legal overlay, capstone rubric) |
| Checks | `scripts/validate-course.sh`, `labs/verify-setup.sh`, `labs/test-all-labs.sh` — all green |

**Lives in the Elephant Scale course tree, under the Elephant Scale GitHub org.** Relocated
2026-11-10 from `/media/mark/data1/scaia/Legal-AI-Engineering` to
`/media/mark/data1/ES/Legal-AI-Engineering` (= `/home/mark/projects/ES/...`), matching every
sibling ES course. Canonical remote is now **`git@github.com:elephantscale/Legal-AI-Engineering.git`**,
`main` at `e5e4f34`, with the full course history force-pushed over the stub initial commit
that repo was created with.

## Recent accomplishments

- **All 11 labs run end to end with no API key, no network and no model.** `test-all-labs.sh`
  reports **94 passed / 0 failed** in 16 seconds on a 300-document corpus, including the
  deliberate refusals (production without approval, destruction without confirmation) which
  are asserted to exit non-zero rather than merely "not crash".
- **The Labs 01–06 pipeline chain is verified on the default corpus** (~1,196 documents, seed
  `20261109`): 1,196 docs → 15 produced / 1,181 withheld → SAIS-100 baseline 89 → 96 after
  one hardening pass → break egress → 94 + LEGAL-A → Do Not Deploy → repair → 96.
- **All seven planted corpus findings land**, including the deleted §7.3 indemnification cap,
  the 39-day communication gap, the dropped Cc, and the side letter reachable by two
  independent routes.
- **Six agent attacks are blocked with log lines** (injection, cross-matter, leaky memo,
  self-approval, unregistered tool, step flood), and the approval gate is idempotent.
- **Lab 09 fixture hardened.** The offline plan hard-coded `DOC-000330`, which existed only on
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
  Lab 07 and the rubric are reworded back, and the gap that justified removing it is closed:
  the bar is objective, Lab 07's playbook has a four-check issuance checklist and the roster
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
  `labs/10-Deploy-At-Scale/work_queue.py` — lab source, not lab output — so the "no real case
  data" check failed the moment that file became tracked. It now matches directories only.

## Current priorities

1. **Mark's review of the three `outline.md` edits**, one of which removed a deliverable
   (below), plus the one topic bullet added for the new Module 1 section.
2. **A dry run of Day 1** against the clock. The timings in the playbooks are estimates, not
   measurements. Module 1 is now budgeted at 50 minutes rather than 45.
3. **Build the PPTX decks** — `slides/gen.sh` is wired to the shared assembler. By standing
   instruction Claude does not run it; Mark builds the decks himself.

## Customers and revenue connections

- **First student: Carlene Gordon.** Mark meets her **Tuesday 2026-11-17** to talk through
  the course and set expectations; **delivery dates are agreed later**, not in that meeting.
  This ends the course's build-ahead-of-demand phase.
  - **Day 3 stays optional** (Mark, 2026-11-10), partly because two days may already be too
    much material — see the Day 2 overload risk below.
  - **She is to receive the certificate.** The infrastructure is ready: Lab 07's four-check
    issuance checklist and the roster record. She becomes **roster row #1** for
    `LEGAL-AI-ENG-2026`, which is the row that has to answer "what did they actually have to
    do?" in five years. Issue it against the same bar as any paying student — a softened
    first issuance is the one thing that would devalue the credential permanently.
  - **Under consideration (Mark, 2026-11-10): course free, technical support paid.** She
    would get the course at no charge, with paid support afterwards on the issues the course
    covers. *(Needs CEO input — see Decisions needed from Mark.)*
- **FreeEed / SHMsoft** — the course is a demand channel for the platform, and the material
  tracks FreeEed's real design records (`docs/local-ai-cjis-briefing.md`,
  `docs/decisions/local-ai-architecture.md`). When FreeEed's pinned models or sizing tiers
  change, Module 5 and Module 11 change with them.
- **SAIS-100 / es-marketing** — the legal overlay is a worked example of a vertical overlay on
  SAIS-100 and may be reusable in the verified-assessment offering. Coordinate before
  publishing the overlay outside the course.
- **Elephant Scale Secure AI Learning Path** — this is its legal vertical. Sibling courses:
  `Building-Secure-AI-Applications`, `AI-Security-for-Security-Teams`, `Building-Agentic-AI`.

## Upcoming deadlines

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
- Nothing else fixed.

## Important TODOs

- **`labs/06-Score-and-Package/README.md` has no stated duration** — the only core lab
  without one, and it sits inside the Day 2 block that does not fit. Time it during the dry
  run and write the number in.
- **The capstone's pair exercises assume a classroom.** Lab 07 schedules a defense round "in
  pairs, 15 minutes each way" and a round-the-room reading of a partner's best question.
  With a single student Mark is the partner; that works and is faster, but the playbook
  should say so rather than leaving the instructor to improvise in the first delivery.

- Commit and push.
- Dry-run Day 1 with a timer; correct the playbook timings from measurement.
- Decide whether `slides/09`–`12` (the optional Day 3) ship as a separate sellable module.
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
| **Overclaiming.** This course's whole pitch is honesty about limits; a single overclaim costs more here than in any other course we teach. | Low | Honesty is enforced in the material itself — offline fallbacks announce that they are worse, and attestations carry a `scope_and_limits`. |

## Decisions needed from Mark

0. **Day 2 does not fit in a day, and the first delivery is the moment it will show.**
   Mark's own instinct (2026-11-10) that two days may be too much material is **confirmed by
   the stated lab durations**, and it is specifically Day 2, not Day 1:

   | | Lecture (slides × ~2 min) | Labs (as written) | Total | Fits 6.5 h? |
   |---|---|---|---|---|
   | **Day 1** — M1–M4, Labs 01–03 | 67 slides ≈ 2:15 | 3:00–3:45 + 0:30 discussion | **5:45–6:30** | yes, tight |
   | **Day 2** — M5–M7 + capstone, Labs 04–07 | 53 slides ≈ 1:45 | 6:45–7:15 | **8:30–9:00** | **no — over by 2:00+** |

   Day 2's labs alone (75 + 90 + ~60–90 + 180 capstone) exceed a whole teaching day before a
   single slide. One honest caveat: the capstone is "integrated across Day 2" and
   `run_matter.py` drives the earlier stages, so perhaps an hour is double-counted — even
   then Day 2 is over by an hour. Options, in Mark's order of preference, needed:
   **(a)** move Module 7 / Lab 06 to Day 3, **(b)** cut the capstone from 3:00 to ~2:15,
   **(c)** sell the course as 3 days with Day 3 required for the full artifact set, or
   **(d)** accept a long Day 2 and say so in the outline. This decision should be made
   **before** dates are agreed with Carlene, because it changes what is being sold.

1. **Free course now, paid technical support later** *(Mark's idea, 2026-11-10)*. The GM
   read: the model is sound and fits the FreeEed demand channel, but three things should be
   settled before it is offered on 2026-11-17.
   - **Do not call it free; call it what it is.** The Day 1 dry run has never happened, so
     Carlene *is* the dry run. "No fee, in exchange for structured feedback and your timing
     data" is a fair trade between two parties, and it does not anchor the list price at
     zero. Publish a list price alongside it.
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
   name, so the course now awards it and `outline.md`, the capstone deck, Lab 07 and the
   rubric all say so again. The teaching side is done: the bar is objective (attendance,
   module labs, and a capstone that passes its own `VERIFY.md` with no legal auto-fail), the
   issuance checklist and the borderline cases are in Lab 07's Teacher's Playbook, and the
   roster record is specified. What still needs Mark, as business rather than curriculum:
   - the certificate **artifact** itself (design, PDF, who signs it);
   - whether holders are **verifiable** — a registry, a serial number, or nothing;
   - the exact **name** on the document. HQ's `DEC-015` (2026-11-10) already takes a position:
     the **certificate form**, not the holder-form "Certified Legal AI Engineer", because a
     professional-title claim with no accrediting body is the one overclaim this course's own
     material would fail. It is now ES's brand call, but reversing it contradicts Module 1;
   - whether this is the **first of a family** across the Secure AI Learning Path, which would
     decide the naming now rather than after the first cohort.
3. **FreeEed wording.** Five lines were softened from implying shipped capability to
   "reference platform / reference architecture the labs are designed against", naming only
   capabilities backed by `FreeEedCRM/docs/technical-primer.md`. Confirm this is how you want
   FreeEed positioned in course marketing.
4. **Day 3 packaging** — *Decided 2026-11-10: Day 3 stays **optional**.* Still open is
   whether it is also sellable as a standalone modular series, which decision 0 may force
   anyway if Module 7 moves into it.
5. **Target first delivery** — *Superseded 2026-11-10:* Carlene Gordon is the first
   student; dates are set after the 2026-11-17 conversation.

## Next three highest-value actions

1. **Settle the Day 2 shape before quoting dates** (decision 0). The stated lab durations do
   not fit in a day, and the first thing a real delivery exposes is a timetable that was
   never run. Decide (a)–(d), then the outline and `labs/README.md` follow.
2. **Dry-run Day 1 against the clock** and replace the playbook estimates with measurements.
   Carlene's session is itself the Day 2 measurement, which is the honest argument for not
   charging for it.
3. **Prepare the 2026-11-17 conversation**: the artifact list as the thing being sold, the
   certificate bar stated plainly, the support offer bounded in writing, and
   `labs/verify-setup.sh` sent to her afterwards so her machine is known well before a date
   is agreed.
