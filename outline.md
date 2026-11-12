# Legal AI Engineering
### Building Private, Defensible AI for Law — eDiscovery, Review, and Investigations

*© Elephant Scale · Nov 10, 2026*

- **Course Code:** LEGAL-AI-ENG-2026
- **Duration:** 2 Days (optional Day 3 / modular deep-dive available)
- **Level:** Intermediate to Advanced

### Course Description
* Course goals
  * Turn software / AI engineers into **legal engineers** — the people who can actually *build* AI for legal work (eDiscovery, review, investigations).
  * Teach participants to build legal-AI systems that are **private** (nothing leaves the building), **defensible** (you can prove what they did), and **deployable on-prem** — the exact skills legal-tech firms and law departments are hiring for.
  * Do it in two intensive, hands-on days — the whole build path, no fluff.

* In two days, participants build the full core stack: ingest and extract messy real-world legal data, search and retrieve it, add retrieval-augmented generation (RAG) with **citations**, keep it **private** on a local model and prove it, run a **defensible AI review** with court-ready metrics, and package the result for deployment. An optional Day 3 / modular deep-dive extends into investigations, agentic workflows, and on-prem scale.

* Special emphasis is placed on:
  * **Confidentiality and privilege** — where legal data actually goes, and how to keep it local and certifiable.
  * **Defensibility** — measuring, documenting, and reproducing an AI review so it holds up.
  * Grounding every concept in a real-world system: **FreeEed** (Apache-2.0, on-prem eDiscovery — Tika extraction across 1,400+ file types, OCR, imaging, PST/OST, Solr/Lucene search, review, and Bates/load-file production) is the reference platform the instructor ships and the labs are designed against.

### Learning Outcomes
* After the **two-day core**, participants will be able to:
  * Ingest and process messy real-world legal data (1,400+ file types, email/PST, scans, load files).
  * Build search + RAG over documents that **cites its sources** and keeps data local.
  * Choose local vs. cloud AI defensibly, and prove nothing left the machine.
  * Measure and document an AI review so it holds up in court (recall, elusion, precision, ground truth).
  * Package a private, defensible legal-AI application and score it with the **SAIS-100 (Elephant Scale Secure AI Score)** rubric.
* The **optional Day 3 / deep-dive** adds: investigative AI (entities, relationships, timelines), agentic multi-step legal workflows, and on-prem deployment at scale in regulated environments.

## Audience
* Software / AI engineers moving into legal tech
* Legal-tech company engineers who need legal-domain depth
* Technically-minded legal / eDiscovery / information-governance professionals who want to build, not just buy
* Anyone targeting the **"legal engineer" / "AI legal engineer"** role

## Skill Level
* Intermediate to Advanced

## Duration
* **Two days** (recommended) — the complete hands-on build path.
* An **optional Day 3** (or the same material as a **modular series**) extends into investigations,
  agentic workflows, and deployment at scale for teams that want the depth.

## Prerequisites
* Comfortable with Python and basic APIs
* **Bring your own AI subscription** — a working account with a frontier assistant (Claude, ChatGPT, Gemini or equivalent). You will use it as a coding assistant throughout the labs, the way you will on the job. No lab *depends* on it and no lab needs an API key — but a legal engineer who does not already work this way is starting a day behind.
* Helpful: familiarity with LLMs at a user level (no ML background required — we build the mental model)
* No legal background required — the legal concepts you need are taught in context

## Format
* Instructor-led, **highly hands-on** (learn by doing)
* Every module has a working lab; the labs compound into a real legal-AI application by the end
* Taught from the builder's seat — the instructor ships a real on-prem eDiscovery platform (FreeEed) and teaches AI security, so the labs reflect production reality rather than toy demos

## Lab environment
* A modern laptop and reliable internet access
* A local model runtime (Ollama / vLLM, OpenAI-compatible) for the privacy and local-serving labs
* The labs themselves are self-contained Python (standard library plus a short pinned requirements list) over a provided synthetic corpus; **FreeEed** is referenced throughout as the production reference architecture, and participants are pointed at it to install and run on their own machines
* Deliberately messy sample legal corpora are provided

## Course outline

### Day 1: Build the Foundation — Ingest, Search, Retrieve

* **Module 1: The Legal Engineer's Landscape**
  * Learning objectives — understand the role, where AI fits in legal work, and the two risks that run through everything.
  * Topics
    * The legal AI implementation gap — what the 2026 ILTA, Wolters Kluwer and Thomson
      Reuters surveys show, and why buying legal AI software does not remove the need
      for engineering
    * The legal-engineer role and why it is being hired right now
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

### Day 2: Make It Private, Defensible, and Shippable

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

> **Module 7 is the floating module.** It is scheduled on Day 3 so that Day 2 fits in a day,
> and it is pulled forward into Day 2 whenever the room is moving fast enough to take it.
> Nothing on Day 2 depends on it: the capstone drives Labs 02–06 itself and produces its own
> SAIS-100 score, so the certificate bar is met either way.

### Capstone (integrated across Day 2)
* Build a **private, defensible legal-AI application end to end** — ingest a messy corpus, search it, answer questions over it with citations using a **local** model, measure a defensible review, and package it for private deployment.
* Participants leave with a portfolio project that *is* the legal-engineer job.

---

### Optional Day 3 / Advanced Modules (deliverable as a 3rd day or a modular series)

Day 3 is a **menu, not a fixed day** — there is more material here than fits in one, and it
is selected from, or sold as a modular series.

* **Module 7 · Ship It — Workflow, Private Deployment, and Governance** *(the floating
  module — taught on Day 2 instead whenever that day has room)* — a multi-step legal
  workflow (ingest → search → summarize → review → produce) with **human-in-the-loop**;
  private/on-prem deployment essentials (containerize; keep the data in the building); AI
  governance for legal in brief, and **scoring the system with SAIS-100 (the Elephant Scale
  Secure AI Score)**. *Lab: wire the workflow, score it with SAIS-100, and package it for
  private deployment.* Taking it on Day 3 rather than Day 2 is what moves the **document
  production set** and the **containerized deployment** out of the two-day deliverable.
* **Investigations: Entities, Relationships, and Timelines** — extract people/orgs/dates, reconstruct email threads, build chronologies, map near-duplicates and document lineage. *Lab: build a timeline and entity/relationship view.*
* **Agentic and Multi-Step Legal Workflows (deep)** — richer orchestration, contract analysis, multi-doc synthesis, tool use and guardrails as a design principle. *Lab: build a multi-step workflow with a human checkpoint.*
* **Deployment at Scale** — on-prem and appliance deployment, distributed processing for large volumes, regulated environments (CJIS, government, higher-ed), hardware sizing. *Lab: containerize and scale a processing job across workers.*
* **Governance and Compliance Deep-Dive** — the AI-regulation landscape (100+ US state AI laws, the EU AI Act), audit requirements, and a full SAIS-100 governance audit. *Lab: audit a legal-AI system against a governance/defensibility checklist.*

## What participants take away

* **Comfort in the area of study** — you leave able to hold your own in a legal-AI conversation: the vocabulary, the two risks, where AI actually fits in a matter, and what still has to be *built* rather than bought.
* **The working system you built** — the capstone repository itself: a private, defensible legal-AI application with its `DEFENSE.md`, reproducibility bundle and SAIS-100 score. A portfolio artifact, not a slide deck.
* **The reusable paperwork** — the SAIS-100 legal overlay, the defensibility checklist, the reproducibility manifest template, the TAR metrics cheat sheet.
* **A certificate of completion, signed by the instructor.**
* **Six months of email support from the instructor** — on your own build, not just on the labs.
* **Six months of updates to the course materials** — slides, labs and handouts, as the tooling and the regulations move.

## Assessment and Certification
* Evaluation — capstone project, lab completion, and class participation
* Requirements — minimum attendance, completion of the module labs, and a capstone that passes its own `VERIFY.md` and trips **no** legal auto-fail condition
* Certificate Awarded — **Legal AI Engineer Certificate**
* Participants also leave with the capstone repository itself: a private, defensible legal-AI application plus its `DEFENSE.md`, reproducibility bundle, and SAIS-100 score. That portfolio artifact is the evidence behind the certificate — the certificate says a bar was met, and the repository is how it is shown.

## Where this fits
* This is the **legal-vertical track of the Elephant Scale Secure AI Learning Path.**
* It pairs naturally with **Building Secure AI Applications** (builders) and **AI Security for Security Teams** (defenders), and applies the **SAIS-100** framework in its governance work.
* **FreeEed** (Apache-2.0, on-prem eDiscovery) is the reference architecture throughout — the real system that keeps the labs production-grade rather than slideware. Participants build their own pipeline in the labs and leave able to deploy FreeEed on their own hardware.
