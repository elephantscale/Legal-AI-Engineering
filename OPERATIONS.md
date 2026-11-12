# Project Operations

**Last updated:** 2026-11-12
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
  - **She is to receive the certificate.** The infrastructure is ready: Lab 08's four-check
    issuance checklist and the roster record. She becomes **roster row #1** for
    `LEGAL-AI-ENG-2026`, which is the row that has to answer "what did they actually have to
    do?" in five years. Issue it against the same bar as any paying student — a softened
    first issuance is the one thing that would devalue the credential permanently.
  - **Under consideration (Mark, 2026-11-10): course free, technical support paid.** She
    would get the course at no charge, with paid support afterwards on the issues the course
    covers. *(Needs CEO input — see Decisions needed from Mark.)*
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

- **`labs/07-Score-and-Package/README.md` has no stated duration** — the only core lab
  without one, and it sits inside the Day 2 block that does not fit. Time it during the dry
  run and write the number in.
- **The capstone's pair exercises assume a classroom.** Lab 08 schedules a defense round "in
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
| **The course is named after a JD-gated job title.** Four of six employers require a JD for the role titled *Legal AI Engineer*; the roles our graduates can actually win are titled *Forward-Deployed Engineer*, *AI Automation Engineer* or *Legal AI Engineer (Contractor)*. A student who takes the title literally will conclude the course did not work. | **High** | Not a rename — a **market map in Module 1** (`job-market-research.md` §4, priority P1): which titles are JD-gated, what each pays, which door this course opens. One slide and one handout, built from research already done. It also answers the question every paying student asks in the first hour, now with evidence. |
| **A partner is advertising our certificate before we have defined it.** The NobleProg/Govtra page carries the Legal AI Engineer Certificate and its requirements. | Medium | Settle `DEC-015` and tell Chandra what partners may and may not say. Carlene's issuance is the first real test of the same bar. |
| **Stated audience is wider than the built course.** Mark's 2026-11-11 email to Merlin describes the audience as "legal professionals looking to upgrade, or engineers moving into legal tech". As built this is Intermediate-to-Advanced **for engineers**: eleven Python labs and a capstone repository. A lawyer upgrading cannot complete them. | Medium | It was one line in a first email and it is Mark's to resolve on the call. Before anyone treats a non-engineer track as covered: it is weeks of work, not an adjustment — a parallel no-code track with different deliverables and a different certificate bar. Resolve the audience sentence before any brochure or landing page repeats it. |
| **Six months of support and updates is now a promise in the contract.** `outline.md` commits every participant to six months of the instructor's email support and six months of course-material updates. The volume is unbounded, the cost is unpriced, and when a **partner** sells the seat it is not stated who honours it — NobleProg's ~$2,700 online rate was set before this existed. | Medium | Decide the bounds before the first cohort (decision 9): what support covers, how updates are delivered (a repo invitation is the cheapest honest answer), and whether a partner seat includes both. Cheap to scope now, expensive to walk back after a cohort has been told. |
| **Overclaiming.** This course's whole pitch is honesty about limits; a single overclaim costs more here than in any other course we teach. | Low | Honesty is enforced in the material itself — offline fallbacks announce that they are worse, and attestations carry a `scope_and_limits`. |

## Decisions needed from Mark

0. **Day 2 overload** — *Decided 2026-11-11: **Module 7 / Lab 07 move to Day 3**, as the
   **floating module** — pulled forward into Day 2 whenever the room is fast enough. Mark is
   content to sell three days otherwise.* Effect on the clock:

   | | Lecture | Labs | Total | vs 6.5 h |
   |---|---|---|---|---|
   | **Day 1** — M1–M4, Labs 02–04 | ≈ 2:15 | 3:00–3:45 + 0:30 | **5:45–6:30** | fits |
   | **Day 2** — M5, M6 + capstone, Labs 05, 06, 08 | ≈ 1:20 | 5:45 | **≈ 7:05** | ~35 min over |

   The move removes roughly 1:45 from Day 2, which was over by 2:00–2:30. **It is now about
   35 minutes over, not two hours** — close enough to absorb 1:1 or with a tight lunch. The
   only remaining lever is the capstone's 3:00 block; cutting it to 2:30 would close the gap
   outright, and that decision is still open.

   What the two-day room gives up when Module 7 is not pulled forward: the **document
   production set** (`production/VOL001/`) and the **containerized deployment**. What it does
   **not** give up: the certificate — the capstone drives Labs 02–06 itself and runs
   `sais100.py`, so `sais100-score.json` and issuance check 4 survive. Day 3 is now
   explicitly a **menu, not a fixed day**: five modules' worth of material, selected from or
   sold as a modular series.

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
4. **Day 3 packaging** — *Decided 2026-11-10: Day 3 stays **optional**.* Still open is
   whether it is also sellable as a standalone modular series, which decision 0 may force
   anyway if Module 7 moves into it.
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
8. **Which course gaps to close, and when** — *Needs CEO input; no course changes made.*
   Recommended P1, all cheap and none touching a lab: the Module 1 market map; a
   **platform-equivalence appendix** (what you built / what you would configure instead in aiR,
   CoCounsel, Harvey, Copilot Studio / what you still owe a court either way); and a
   **vendor-evaluation handout** in `course-materials/`, built on the Module 5 spectrum and the
   new three-architecture slide. P2, real work: human-oversight design, an adoption unit, MCP in
   Lab 10. P3: eval-platform and observability literacy, and naming LangGraph once. **Not
   recommended:** a no-code track for JD-holders — weeks of work, contradicts the positioning,
   and the JD-gated roles want a practising lawyer, not a lawyer with a Python certificate.

9. **Scope the six-month support and update promise** — *Needs CEO input; added 2026-11-12.*
   Three questions, all cheap to answer now:
   - **What does email support cover?** Questions about the labs and the student's own build is
     the natural reading; it is not consulting on a live matter, and it is not a help desk for
     FreeEed. One sentence in the outline closes the gap.
   - **How are updates delivered?** A read invitation to the course repository costs nothing and
     is self-maintaining. A mailed zip per release is a recurring chore. Pick one.
   - **Does a partner-sold seat include both?** NobleProg is selling this course now at a flat
     rate set before these commitments existed. If a Govtra registrant gets six months of Mark's
     inbox, that is a cost inside someone else's price; if not, our outline and their page
     describe different products.

## Next highest-value actions

1. **Send Chandra Tan the Legal AI Engineering outline** (owed **2026-11-19**), with the
   Module 7 → Day 3 change and the **new "bring your own AI subscription" prerequisite** called
   out, and tell her what partners may say about the certificate.
   One email, zero cost, and it corrects a live public page that is selling our course today.
   This is Phase 1 of the 90-day plan in `marketing-channels.md` and the highest-return action
   available.
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
