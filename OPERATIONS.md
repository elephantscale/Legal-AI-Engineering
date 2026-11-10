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
| Slides | 13 decks (`00-about` + modules 01–12), ~4,200 lines of presenter-skeleton Markdown, ~170 slides, all with `Notes:` narration |
| Labs | **All 11 built and smoke-tested offline** (01–07 core, 08–11 optional Day 3), ~9,500 lines of Python, ~3,800 lines of lab README including Teacher's Playbooks |
| Course materials | 7 documents (design canvas, defensibility checklist, TAR metrics cheat sheet, privilege/egress attestation form, reproducibility manifest template, SAIS-100 legal overlay, capstone rubric) |
| Checks | `scripts/validate-course.sh`, `labs/verify-setup.sh`, `labs/test-all-labs.sh` — all green |

**Nothing is committed yet.** The work is in the working tree on `main`; the last commit is
`f698bb0 outline`.

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

## Current priorities

1. **Commit and push** the whole body of work. It is the largest outstanding risk — nothing
   is in version control yet.
2. **Mark's review of the three `outline.md` edits**, one of which removed a deliverable
   (below).
3. **A dry run of Day 1** against the clock. The timings in the playbooks are estimates, not
   measurements.
4. **Build the PPTX decks** — `slides/gen.sh` is wired to the shared assembler. By standing
   instruction Claude does not run it; Mark builds the decks himself.

## Customers and revenue connections

- **No booked delivery yet.** The course is a catalog addition, built ahead of demand.
  *(Needs CEO input: is there a target first delivery?)*
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

None fixed. *(Needs CEO input: a target first-delivery date would turn the dry run from a
priority into a deadline.)*

## Important TODOs

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
| **Uncommitted work.** The entire course exists only in one working tree. | **High** | Commit and push this session. |
| **Case-law currency.** *Morgan v. V2X* (D. Colo., Mar 2026) is cited as the anchor for "your AI use is discoverable". Legal-AI case law is moving fast and a stale citation is a credibility problem in this audience. | Medium | Re-check before each delivery. Treat the citation as perishable. |
| **Model-ID drift.** `qwen3:8b` / `qwen3:14b` / `nomic-embed-text` are named in CLAUDE.md, the slides, the labs and the manifests. | Medium | `validate-course.sh` checks the pins agree between `CLAUDE.md` and `labs/common/llm.py`. Extend if more pins appear. |
| **Reference outputs are corpus-dependent.** The playbooks quote numbers measured on the default corpus; a student running `--docs 300` sees different ones. | Low | Stated in `labs/README.md` and `labs/SETUP.md`. The *findings* are seeded to survive both sizes. |
| **Overclaiming.** This course's whole pitch is honesty about limits; a single overclaim costs more here than in any other course we teach. | Low | Honesty is enforced in the material itself — offline fallbacks announce that they are worse, and attestations carry a `scope_and_limits`. |

## Decisions needed from Mark

1. **The removed completion certificate.** A peer session flagged, and I verified, that
   `outline.md` promised "Assessment and Certification" with a certificate line that nothing
   in the course delivers. I replaced it with the capstone-repository deliverable and
   reworded the capstone deck and Lab 07 from "Certification" to "Completion". **This removed
   a promise from a published outline — reverse it if the certificate is intended**, in which
   case it needs an actual issuing process.
2. **FreeEed wording.** Five lines were softened from implying shipped capability to
   "reference platform / reference architecture the labs are designed against", naming only
   capabilities backed by `FreeEedCRM/docs/technical-primer.md`. Confirm this is how you want
   FreeEed positioned in course marketing.
3. **Day 3 packaging** — one optional day, or a separately sellable modular deep-dive?
4. **Target first delivery**, which would set the dry-run deadline.

## Next three highest-value actions

1. **Commit and push.** Eleven labs, thirteen decks, seven course documents and three check
   scripts currently exist in exactly one place.
2. **Dry-run Day 1 against the clock**, and correct the playbook timings from measurement
   rather than estimate.
3. **Decide the certificate question** (#1 above), since it is the one open item that changes
   a student-facing promise.
