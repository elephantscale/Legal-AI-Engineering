# Working on this course with Claude

This is the **Legal AI Engineering** course (Elephant Scale) — a hands-on, engineer-level course on
building **private, defensible** AI for legal work, sold as a **2-day Core plus a 1-day Deep Dive**:
eDiscovery, document review, and investigations. This file orients a Claude session
started in this directory.

## What's here

- `outline.md` — the course outline. **Treat it as the contract.** Module numbers, lab
  names, and the product split come from here. **Two products as of 2026-11-15** (Mark): the
  **Core** is two days, Modules 1–6 plus the capstone — the build path, and the certificate bar is
  met by it alone. The **Deep Dive** is one day, Modules 7, 10 and 12 ("ship it, oversee it, prove
  it"), scheduled separately and **assuming the Core**. Modules 9 and 11 are **electives**, booked
  on their own or added to the Deep Dive. The two can still run back to back as three consecutive
  days on request — the split exists because three days in a row is the hardest thing to ask of a
  working legal team. There is no "condensed version" and **Module 7 no longer floats**: it was
  moved into Day 2 on paper on 2026-11-15 and moved straight back, because Day 2 is already ~35
  minutes over without it (OPERATIONS.md decision 0 carries the clock table). Don't re-propose it
  without new timings.
- `slides/NN-name.md` — one Markdown deck per module (`00-about` + modules `01`–`12`).
  **The Markdown is the source of truth.** Listed in `slides/slide-list.txt`.
- `labs/NN-Name/README.md` — one lab per module, with runnable starter code and a
  `## Teacher's Playbook`.
- `labs/assets/make_corpus.py` — generates the deliberately messy legal corpus the labs
  share. Labs 02–08 are a **pipeline**: each one consumes the previous one's output.
- `course-materials/` — the artifacts students keep (SAIS-100 legal overlay, defensibility
  checklist, reproducibility manifest template, TAR metrics cheat sheet, capstone rubric).
- `scripts/validate-course.sh`, `labs/test-all-labs.sh`, `labs/verify-setup.sh` — structure
  and smoke checks (keep them green).

## The two claims the whole course serves

Everything in this repo exists to support one of two claims a student must be able to make
in front of a court, a client, or a regulator:

1. **"Here is exactly where the documents went — and nowhere else."** — confidentiality and
   privilege. An explicit boundary, enforced in code, and a *monitor that attests to it*.
2. **"Here is exactly what the system did — and you can re-run it."** — defensibility.
   Citations, recall/elusion/precision against blind ground truth, pinned model, logged
   prompts, a reproducibility bundle.

If a slide or a lab doesn't serve one of those two, cut it. That discipline is the course's
differentiator against generic "AI for lawyers" training.

**Claim 1 is about the boundary, not about locality (Mark, 2026-11-25).** *"Nothing left the
building"* is the strict **default** this course builds and the capstone grades — it is not a
universal requirement of the role, and the repo used to state it as though it were. The
boundary is a parameter of the matter: vendor-approved cloud and government cloud are the two
other accepted architectures, each with its own acceptance mechanism, and Module 5's *"Where
Local Actually Wins — and Where It Does Not"* is the slide that says so. Keep the slogan where
it describes the strict architecture; don't restate it as the principle. The principle is
knowing **which boundary applies to this matter, and proving the one you chose actually held.**

## House style (match it)

- **Presenter-skeleton slides:** prose collapsed into bullet / nested-bullet skeletons the
  instructor narrates. Keep slide titles, `---` separators, and `>` blockquotes (they double
  as the visual beat / key takeaway per slide). Keep worked-example / code / JSON / ASCII
  diagram blocks verbatim. Every content deck opens with a title slide (`# Title` +
  `Elephant Scale`) and ends with a `## Lab NN` hand-off slide. `Notes:` blocks carry the
  instructor's narration — they are for Mark, not the student.
- **Legal concepts taught in context, never assumed.** The audience is engineers. Define
  privilege, responsiveness, elusion, TAR, load file, custodian *at the moment they first
  matter* — and always say what the engineer has to *build* because of it.
- **Local-first, and provable.** The default in every lab is a local model behind an
  OpenAI-compatible endpoint (Ollama for a laptop, vLLM for a server). Cloud is the
  *contrast case*, used to show what it costs you legally — never the happy path.
- **Never blocked.** Every lab runs with no API key and no network. Where a lab wants a
  local LLM, embedding model, OCR engine, Tika, or Solr, it ships a **deterministic
  stdlib/offline fallback** and says so out loud. A student without Ollama still completes
  the lab and still learns the lesson.
- **Honest about limits.** Say plainly where a local open-weight model is worse, where
  GPU inference is non-deterministic, and where a claim would not survive cross-examination.
  Overclaiming is a worse look in this course than in any other we teach.
- **No real case data. Ever.** Every byte in `labs/assets/` is synthetic, generated by
  `make_corpus.py`. Do not commit anything derived from a real matter, custodian, or client.

## Current model IDs

- **Local (default):** chat/RAG `qwen3:8b` (entry) / `qwen3:14b` (recommended); structured
  extraction `qwen3:14b`; embeddings `nomic-embed-text` (768-dim) or `mxbai-embed-large`
  (1024-dim). Served by Ollama at `http://localhost:11434/v1`, OpenAI-compatible.
- **Cloud (contrast only):** Anthropic — Opus `claude-opus-5`, Sonnet `claude-sonnet-5`,
  Haiku `claude-haiku-5-5`. OpenAI — `gpt-4.1` / `gpt-4o` family. Don't invent IDs.
- Changing the embedding model changes the **vector dimension** and forces a re-ingest.
  That gotcha is taught in Module 4 — keep it.

## Labs

- Copy-ready code and commands **at point of use**. State what to install, how to run, what
  a correct run looks like, and what artifact to keep.
- Labs 02–07 write into `labs/work/` (gitignored). Lab `NN` reads lab `NN-1`'s output.
  Don't break that chain; if you change a filename, change the consumer in the same commit.
- **The Deep Dive runs weeks after the Core**, so `labs/resume-deep-dive.sh` rebuilds the seeded
  corpus and replays Labs 02–05 into `labs/work/` offline — Labs 07, 10 and 12 read
  `catalog.jsonl`, `exceptions.jsonl`, `index.sqlite`, `chunks.jsonl` and `attestation.json`, so a
  student arriving with an empty work tree cannot start. It deliberately replays the Core labs with
  **their own commands** rather than Lab 07's `run_matter.py`, which would spoil the Deep Dive's
  first lesson. It also stops **before** Lab 06: `protocol` refuses to overwrite a pre-registration
  and that refusal is the control, so `metrics.json` and the case snapshot are left for Lab 07's
  `run_matter.py` to produce — and when a student ran the Core back to back and already has
  `validation-protocol.md`, `run_matter.py` adopts it rather than rebuilding it. That script is a **consumer of
  every Core lab's output filenames**: if you rename one, fix it in the same commit.
- Each lab ends with a rich `## Teacher's Playbook`: worked model answer with realistic
  output, live-demo script, common mistakes + fixes, debrief Q&A, "what good looks like."
- Each lab names its **deliverable** — the artifact that goes in the capstone bundle.

## Naming conventions (keep filenames stable)

- Decks: `slides/NN-topic.md`, `NN` two digits, listed in `slides/slide-list.txt`.
- Labs: `labs/NN-Topic-Name/README.md`, `NN` two digits matching the module ↔ lab map in
  `labs/README.md`. **Module N uses Lab N** — the numbers agree exactly, so the instructor
  never has to translate between them out loud. Module 1 has a discussion, not a lab, so
  there is no Lab 01 and the numbering starts at 02. Renumbering anything breaks that
  identity; don't.
- A deck's `## Lab NN` hand-off slide may carry a **different title** from the lab's own
  `# Lab NN —` heading (Labs 10, 11, 12 do). That is deliberate (Mark, 2026-11-11): the
  slide title says what the student is about to *do*, the lab title names the lab. The
  numbers must match; the words need not. Don't "fix" these.

## Build & workflow

- **Never regenerate the PPTX decks — Mark builds them himself.** `slides/gen.sh` calls the
  shared assembler (`$ES_HOME/utils/presentations/slides-assembler.sh`) and then **strips the
  assembler's `NN__` counter prefix**, so `slides/assembly.out/` holds decks named after their
  source: `01-legal-engineer-landscape.pptx`, not `01__01-legal-engineer-landscape.pptx`
  (Mark, 2026-11-12). The source filenames already carry the module number, so the counter was
  both redundant and off by one. Same second pass as `Building-Agentic-AI/slides/gen.sh`; the
  shared assembler stays untouched. To refresh the manifest without assembling:
  `ls slides/[0-9][0-9]-*.md | sed 's#slides/##' | sort > slides/slide-list.txt`.
- Add a slide image: put the file in `images/` and reference it as
  `<img src="../images/foo.png" style="width:60%;"/>`. Keep md image tags to `src` + `width`;
  final layout lives in the PPTX.
- After structural changes run `./scripts/validate-course.sh`, `./labs/test-all-labs.sh`, and
  `./labs/verify-setup.sh`. Keep them green.
- Keep `OPERATIONS.md` current — it is the durable operational record for this course.

## Provenance

- This repo lives at `/media/mark/data1/ES/Legal-AI-Engineering` (= `/home/mark/projects/ES/...`)
  and pushes to `git@github.com:elephantscale/Legal-AI-Engineering.git`. It was moved here from
  `/media/mark/data1/scaia/` on 2026-11-10; if you find a reference to the old path or to the
  `Scaia-ai` remote anywhere, it is stale.
- Built from `outline.md` (Elephant Scale, 2026-07-21). House style borrowed from the sibling
  Elephant Scale courses `Building-Agentic-AI`, `Building-Secure-AI-Applications`, and
  `Artificial-Intelligence-for-Federal-Decision-Making-Training` — now literally siblings, in
  the same `ES/` directory.
- The privacy/local-serving and reproducibility material tracks FreeEed's real design records:
  `/media/mark/data1/SHMsoft/FreeEed/docs/local-ai-cjis-briefing.md` and
  `docs/decisions/local-ai-architecture.md`. Keep them in sync — when FreeEed's pinned models
  or sizing tiers change, Module 5 and Module 11 change too.
- SAIS-100 is the Elephant Scale Secure AI Score as defined in
  `/media/mark/data1/ES/es-marketing/drafts/sais-100-*.md` (six categories, 20/20/20/15/15/10,
  3 questions each scored 0–3, `round(raw/9 × weight)`). This course **does not fork it** — it
  adds a legal *overlay* of evidence and auto-fail conditions in
  `course-materials/sais-100-legal-overlay.md`.
