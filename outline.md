# Legal AI Engineering
### Building Private, Defensible AI for Law — eDiscovery, Review, and Investigations

*© Elephant Scale · Jan 5 - 7, 2027*

- **Course Code:** LEGAL-AI-ENG-2026
- **Duration:** 2-day Core + a 1-day Deep Dive, scheduled separately (electives sell on their own)
- **Level:** Intermediate to Advanced

### Course Description
* Course goals
  * Turn software / AI engineers into **legal engineers** — the people who can actually *build* AI for legal work (eDiscovery, review, investigations).
  * Teach participants to build legal-AI systems that are **private** (nothing leaves the building), **defensible** (you can prove what they did), and **deployable on-prem** — the exact skills legal-tech firms and law departments are hiring for.
  * Do it in **two intensive, hands-on days** — the whole build path, and shipping it — with a **one-day technical Deep Dive**, scheduled separately, for oversight and governance. No fluff.

* **The Core — two days.** Participants build the full stack: ingest and extract messy real-world legal data, search and retrieve it, add retrieval-augmented generation (RAG) with **citations**, keep it **private** on a local model and prove it, run a **defensible AI review** with court-ready metrics, and assemble the whole thing as a capstone that scores itself with **SAIS-100**. **The Deep Dive — one day, scheduled separately.** Ship that system: a multi-step workflow with a human in the loop, private on-prem packaging, agentic orchestration with a designed human checkpoint, and a full governance audit against the AI-regulation landscape. Investigations and deployment at scale are available as electives.

* Special emphasis is placed on:
  * **Confidentiality and privilege** — where legal data actually goes, and how to keep it local and certifiable.
  * **Defensibility** — measuring, documenting, and reproducing an AI review so it holds up.
  * Grounding every concept in a real-world system: **FreeEed** (Apache-2.0, on-prem eDiscovery — Tika extraction across 1,400+ file types, OCR, imaging, PST/OST, Solr/Lucene search, review and export — ⛔ **not** Bates/load-file production, which is a written spec and issue #551, not shipped code, verified against tag v10.8.7 on 2026-11-15) is the reference platform the instructor ships and the labs are designed against.

### Learning Outcomes
* After the **Core (two days)** — the build path, and shipping it — participants will be able to:
  * Ingest and process messy real-world legal data (1,400+ file types, email/PST, scans, load files).
  * Build search + RAG over documents that **cites its sources** and keeps data local.
  * Choose local vs. cloud AI defensibly, and prove nothing left the machine.
  * Measure and document an AI review so it holds up in court (recall, elusion, precision, ground truth).
  * Package a private, defensible legal-AI application and score it with the **SAIS-100 (Elephant Scale Secure AI Score)** rubric.
* The **Deep Dive (one day)** adds: shipping a human-in-the-loop legal workflow and packaging it for private on-prem deployment, designing human oversight into an agentic workflow rather than promising it, attacking your own guardrails and watching them hold, and auditing a legal-AI system against the AI-regulation landscape.
* The **electives** add: investigative AI (entities, relationships, timelines) and on-prem deployment at scale in regulated environments (CJIS, government, higher-ed).

## Audience
* Software / AI engineers moving into legal tech
* Legal-tech company engineers who need legal-domain depth
* Technically-minded legal / eDiscovery / information-governance professionals who want to build, not just buy
* Anyone targeting the **"legal engineer" / "AI legal engineer"** role

## Skill Level
* Intermediate to Advanced

## Duration
* **Core — two days.** The complete hands-on build path, Modules 1–6 plus the capstone. The
  capstone and the SAIS-100 score sit on Day 2, so **the certificate bar is met by the Core alone**.
* **Deep Dive — one day, scheduled separately.** Modules 7, 10 and 12 — ship it, oversee it, prove
  it: the document production set, the container, the agentic workflow with a designed human
  checkpoint, and the governance audit. **It assumes the Core.**
* The two can still run back to back as three consecutive days when a buyer wants it that way. The
  split exists because three days in a row is the hardest thing to ask of a working legal team — not
  because the days are weaker apart.
* **Electives** — **investigations** and **deployment at scale** — are booked on their own, or added
  to the Deep Dive on request.

## Prerequisites
* Comfortable with Python and basic APIs
* **Bring your own AI subscription** — a working account with a frontier assistant (Claude, ChatGPT, Gemini or equivalent). You will use it as a coding assistant throughout the labs, the way you will on the job. No lab *depends* on it and no lab needs an API key — but a legal engineer who does not already work this way is starting a day behind.
* Helpful: familiarity with LLMs at a user level (no ML background required — we build the mental model)
* No legal background required — the legal concepts you need are taught in context
* **For the Deep Dive only:** the Core, and the `labs/work/` tree you built in it — or run `labs/resume-deep-dive.sh` before the day starts, which rebuilds it in a few minutes

## Format
* **Live online, 9:00–16:00 US Central** (Mark, 2026-11-15) — on site for private cohorts on request.
* Instructor-led, **highly hands-on** (learn by doing)
* Every module has a working lab; the labs compound into a real legal-AI application by the end
* Taught from the builder's seat — the instructor ships a real on-prem eDiscovery platform (FreeEed) and teaches AI security, so the labs reflect production reality rather than toy demos

## Lab environment
* **Any laptop from the last few years, and no GPU.** Measured rather than estimated: Python 3.10+,
  8 GB RAM (16 GB comfortable, which is what running a local 8B model alongside an editor wants),
  2 GB free disk (10 GB if you pull both local models), Linux, macOS, or Windows with WSL2. One
  lab — Lab 06's per-document classification — is genuinely slow on CPU, and the two ways round it
  are *taught* rather than tolerated. `labs/SETUP.md` carries the table and the reasoning.
* **Internet for the class, not for the labs.** Delivery is live online, so a connection is needed
  to attend, and one is needed once to pull the local models. **No lab reaches the network and no
  lab needs an API key** — that is a design rule of this course, not a convenience.
* A local model runtime (Ollama / vLLM, OpenAI-compatible) for the privacy and local-serving labs.
  Where a lab wants a model it also ships a deterministic offline fallback, so a participant who
  cannot install Ollama — a locked corporate laptop, say — still completes the lab and still
  learns the lesson
* The labs themselves are self-contained Python (standard library plus a short pinned requirements list) over a provided synthetic corpus; **FreeEed** is referenced throughout as the production reference architecture, and participants are pointed at it to install and run on their own machines
* Deliberately messy sample legal corpora are provided

## Course outline

### Core · Day 1: Build the Foundation — Ingest, Search, Retrieve

* **Module 1: The Legal Engineer's Landscape**
  * Learning objectives — understand the role, where AI fits in legal work, and the two risks that run through everything.
  * Topics
    * The legal AI implementation gap — what the 2026 ILTA, Wolters Kluwer and Thomson
      Reuters surveys show, and why buying legal AI software does not remove the need
      for engineering
    * The legal-engineer role and why it is being hired right now
    * **What the postings actually say** — a market map built from nine current postings at
      six employers: which titles are J.D.-gated, which are not, what each pays, which door
      this course opens, and what it deliberately does not teach *(handout included)*
    * Where AI fits: eDiscovery, review, contracts, research, investigations; the EDRM model in plain terms
    * Build vs. buy
    * The two risks that run through everything: **confidentiality/privilege** and **defensibility**

* **Module 2: Legal Data Is Messy — Ingestion and Extraction**
  * Learning objectives — handle the reality of legal data at scale.
  * Topics
    * 1,400+ file types, email and PST, scanned paper, load files (.dat/.opt); embedded metadata that matters
    * Text extraction (Tika), OCR, and de-duplication as a *choice*
  * **Lab: Ingestion** — build an ingestion pipeline over a deliberately messy document set (nested containers, email, scans, load files), with de-duplication as a documented legal decision

* **Module 3: Search and Retrieval — the Foundation**
  * Learning objectives — build the core eDiscovery primitive: find anything inside everything.
  * Topics — full-text search and indexing (Solr/Lucene); relevance, metadata and date filtering; search across OCR'd content
  * **Lab: eDiscovery Search** — index a corpus and run real eDiscovery-style searches, including inside OCR'd scans

* **Module 4: RAG for Legal Documents — with Citations**
  * Learning objectives — build RAG over legal documents that cites its sources.
  * Topics
    * Why **retrieval, not fine-tuning**, for sensitive material — the model never swallows the documents
    * Chunking, embeddings, and above all **citations / provenance**
    * Multi-document and thread summarization
  * **Lab: Legal RAG with Citations** — build a RAG Q&A over a document set that answers with source citations

---

### Core · Day 2: Make It Private and Defensible

* **Module 5: Privacy, Privilege, and Local Serving — the Privilege Trap**
  * Learning objectives — keep legal data local and be able to certify it.
  * Topics
    * Where the data actually goes when it hits a cloud AI
    * Privilege waiver, duty of competence, and the "private" spectrum (contractual vs. physical)
    * *Morgan v. V2X* — your AI use is itself discoverable, so choose the tool on the record
    * Serving **local models** (Ollama / vLLM) and **monitoring outbound** traffic
  * **Lab: Local Model + Egress Proof** — run a local model end-to-end and prove, with monitoring, that no data egressed

* **Module 6: Defensible AI Review**
  * Learning objectives — measure and document an AI review so it holds up.
  * Topics
    * The numbers that hold up in court: **recall, elusion, precision, ground-truth validation**; TAR / active learning
    * Transparency (why did it code this document?) and **reproducibility** — pin the model, fix the settings, log everything
    * The "defensible case snapshot" that lets someone re-run your review a year later and get the same result
  * **Lab: Defensible Review** — measure an AI review against a blind ground truth and produce a reproducibility bundle

> **Module 7 opens the Deep Dive, and it cannot come back into Day 2** — that was tried on
> paper and the clock refuses it: Day 2 is already about 35 minutes over 6.5 hours without it, and
> Module 7 plus Lab 07 is another 1:45. Nothing on Day 2 depends on it: the capstone drives Labs
> 02–06 itself and produces its own SAIS-100 score, so the certificate bar is met at the end of
> Day 2. What a Core-only buyer does not get is the **document production set** and the
> **containerized deployment** — say that in the sales conversation, not on Day 2.

### Capstone (integrated across Core Day 2)
* Build a **private, defensible legal-AI application end to end** — ingest a messy corpus, search it, answer questions over it with citations using a **local** model, measure a defensible review, and package it for private deployment.
* Participants leave with a portfolio project that *is* the legal-engineer job.

---

### Deep Dive — one day, scheduled separately: Ship It, Oversee It, Prove It

* **Module 7: Ship It — Workflow, Private Deployment, and Governance**
  * A multi-step legal workflow (ingest → search → summarize → review → produce) with
    **human-in-the-loop**; private/on-prem deployment essentials (containerize; keep the data in
    the building); AI governance for legal in brief, and **scoring the system with SAIS-100 (the
    Elephant Scale Secure AI Score)**
  * **Lab: Score and Package** — wire the workflow, score it with SAIS-100, and package it for
    private deployment. This is where the **document production set** and the **containerized
    deployment** come from

* **Module 10: Agentic and Multi-Step Legal Workflows (deep)**
  * Richer orchestration, contract analysis, multi-doc synthesis, tool use and guardrails as a
    design principle, and **human oversight as something you design rather than promise**
  * **Lab: Agentic Legal Workflow** — build a multi-step workflow with a human checkpoint

* **Module 12: Governance and Compliance Deep-Dive**
  * The AI-regulation landscape (100+ US state AI laws, the EU AI Act), audit requirements, and
    a full SAIS-100 governance audit
  * **Lab: Governance Audit** — audit a legal-AI system against a governance/defensibility
    checklist

### Electives — booked on their own, or added to the Deep Dive on request

* **Module 9: Investigations — Entities, Relationships, and Timelines** — extract
  people/orgs/dates, reconstruct email threads, build chronologies, map near-duplicates and
  document lineage. *Lab: build a timeline and entity/relationship view.* The module an
  eDiscovery audience asks for most often.
* **Module 11: Deployment at Scale** — on-prem and appliance deployment, distributed processing
  for large volumes, regulated environments (CJIS, government, higher-ed), hardware sizing.
  *Lab: containerize and scale a processing job across workers.* The module for public-sector
  and government-cloud buyers.

### Scheduling the two

There is no condensed version any more, and no floating module. The Core **is** the two-day
product — Modules 1–6 and the capstone — and the Deep Dive is the third day, sold and scheduled on
its own. Nothing is cut and no decision has to be made at 4pm on Day 2.

**The Deep Dive assumes the Core, technically and not just pedagogically.** Labs 07, 10 and 12 read
the Core's work tree — the catalog and exceptions from Lab 02, the index from Lab 03, the chunks and
vectors from Lab 04, the attestation from Lab 05. A student who arrives without those cannot start.
Two defences, and use both: tell the room to keep `labs/work/`, and run
**`labs/resume-deep-dive.sh`**, which rebuilds the seeded corpus and replays **Labs 02–05** offline
in a few minutes.

**Lab 06's artifacts are the one thing the replay leaves alone**, and that is a control rather than
an oversight: `defensible_review.py protocol` refuses to overwrite an existing pre-registration, so
a replay script must not write one. Lab 07's `run_matter.py` runs those stages itself at the start
of the Deep Dive, which is where the teaching order puts them anyway — so `metrics.json` and the
case snapshot arrive there. A student who *did* complete Lab 06 arrives with
`validation-protocol.md` already on disk, and `run_matter.py` **adopts** it rather than rebuilding
it: the hash goes in the stage ledger and the pre-registration still counts as one. Both routes
reach Lab 07, and the back-to-back route is the one that matters when the Core and the Deep Dive run
on consecutive days.

**Recommended gap: two to four weeks.** Long enough to be a separate commitment, short enough that
the environment, the vocabulary and the capstone are all still fresh.

## What participants take away

* **Comfort in the area of study** — you leave able to hold your own in a legal-AI conversation: the vocabulary, the two risks, where AI actually fits in a matter, and what still has to be *built* rather than bought.
* **The working system you built** — the capstone repository itself: a private, defensible legal-AI application with its `DEFENSE.md`, reproducibility bundle and SAIS-100 score. A portfolio artifact, not a slide deck.
* **The reusable paperwork** — the SAIS-100 legal overlay, the defensibility checklist, the reproducibility manifest template, the TAR metrics cheat sheet.
* **The Elephant Scale Legal AI Engineer Certificate**, signed by the instructor.
* **Six months of email support from the instructor** — on your own build, not just on the labs: architecture, what to measure, how to defend it. Best effort, by email, personal to you, starting the last day of class. **Please send no client data — a synthetic reproduction or a description of the problem.** Advice on a live matter, or work that turns out to be a project, is quoted separately.
* **Six months of updates to the course materials** — slides, labs and handouts, as the tooling and the regulations move.

## Assessment and Certification
* Evaluation — capstone project, lab completion, and class participation
* Requirements — minimum attendance, completion of the **Core** labs, and a capstone that passes its own `VERIFY.md` and trips **no** legal auto-fail condition
* Certificate Awarded — the **Elephant Scale Legal AI Engineer Certificate**
* **The certificate is earned on the Core.** The Deep Dive adds no second bar — it adds artifacts: the document production set, the container, the agentic workflow with its approval gate and refusal log, and the governance audit
* Participants also leave with the capstone repository itself: a private, defensible legal-AI application plus its `DEFENSE.md`, reproducibility bundle, and SAIS-100 score. That portfolio artifact is the evidence behind the certificate — the certificate says a bar was met, and the repository is how it is shown.

## Where this fits
* This is the **legal-vertical track of the Elephant Scale Secure AI Learning Path.**
* It pairs naturally with **Building Secure AI Applications** (builders) and **AI Security for Security Teams** (defenders), and applies the **SAIS-100** framework in its governance work.
* **FreeEed** (Apache-2.0, on-prem eDiscovery) is the reference architecture throughout — the real system that keeps the labs production-grade rather than slideware. Participants build their own pipeline in the labs and leave able to deploy FreeEed on their own hardware.
