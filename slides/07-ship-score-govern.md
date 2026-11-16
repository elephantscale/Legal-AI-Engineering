# Module 7 — Ship It: Workflow, Private Deployment, and Governance

Deep Dive — Ship It

Elephant Scale

---

## From Seven Scripts to One System

You have the pieces. Today they become a thing you can hand to someone.

* A **workflow** — ingest → search → summarize → review → produce, with human checkpoints
* A **deployment** — containerized, on-prem, data in the building
* A **score** — SAIS-100, so the security posture is a number you can re-run

> A pipeline of scripts is a prototype. A pipeline with checkpoints, a deployment, and a
> score is a product.

Notes:

This module is the bow on the course. Keep the energy up — it is the last content module
before the capstone and people are tired. Lots of concrete artifacts, less theory.

---

## The Five Stages, With Gates

```text
  [1] INGEST  ──▶ [2] SEARCH ──▶ [3] SUMMARIZE ──▶ [4] REVIEW ──▶ [5] PRODUCE
       │              │               │                │              │
    exceptions    hit report      citations        decisions       manifest
    must be       negotiated      verified         + overrides     + Bates
    triaged       with counsel                                     
       │                                              │              │
       ▼                                              ▼              ▼
    ◆ GATE: exception list      ◆ GATE: privilege calls   ◆ GATE: production
      reviewed by a human         confirmed by a human      signed off by a human
```

* Three gates, three signatures. Everything between gates can be automatic.
* **The gates are where the legal obligation lives.** Automate up to the gate, never
  through it.

> Autonomy between the gates. A human at every gate. That is the whole architecture.

Notes:

This slide is the answer to "how agentic should a legal workflow be?" and it is worth saying
simply: as agentic as you like *between* gates, never *across* one. That principle scales
from a script to a multi-agent system (and it is exactly the Module 10 content).

---

## State, Idempotency, and Resumability

Legal runs are long, large, and interrupted.

* **Checkpoint every stage.** A crash at document 840,000 must not restart at 1.
* **Make every stage idempotent** — keyed on `(doc_id, stage, config_hash)`
* **Never mutate in place.** Each stage writes a new artifact; the previous one survives.
* **Append-only logs**, one line per unit of work, with timestamps

```text
work/
  01-catalog.jsonl        02-index.sqlite      03-chunks.npy + chunks.jsonl
  04-attestation.json     05-decisions.jsonl   06-production/
  _state/
    01.done  02.done  03.done        <- stage markers with config hashes
    run.log                           <- append-only, every unit of work
```

* **Why this is not just good engineering:** the artifact chain *is* the chain of custody.
  Mutating stage 3 in place destroys the evidence that stage 2 produced what it produced.

> Idempotent, append-only, checkpointed. The engineering best practice and the legal
> requirement are the same thing here — which is unusual and worth noticing.

Notes:

Engineers already believe in idempotency; the news is that in this domain it has a legal
payoff. Make the connection explicitly — it is the kind of observation that makes a senior
engineer re-evaluate how they build everything else.

---

## Human-in-the-Loop, Concretely

Not a philosophy. Three mechanisms:

* **Confidence bands** — route by score
  ```text
  score > 0.90  ->  auto-code, sample 2% for QC
  0.60 - 0.90   ->  human review queue
  score < 0.60  ->  human review, high priority
  privilege ANY ->  human review, always, no exceptions
  ```
* **Approval gates** — irreversible actions require an explicit, recorded approval:
  production, deletion, any outbound transfer
* **Override capture** — make disagreement one click, and **log it with a reason**

> If disagreeing with the model is harder than agreeing with it, you have built a
> rubber stamp and your override rate will prove it.

Notes:

The threshold numbers are illustrative — the point is that the bands are a *written policy
decision*, set in the protocol, not a magic number in the code. Have students put their bands
in `validation/protocol.md`.

---

## On-Prem Is the Product

```text
┌─ the customer's boundary ──────────────────────────────────────────┐
│                                                                    │
│   ┌──────────┐   ┌─────────┐   ┌────────┐   ┌──────────────────┐  │
│   │ ingest   │   │  Tika   │   │ Solr / │   │ local LLM        │  │
│   │ workers  │──▶│ server  │──▶│ index  │◀──│ (Ollama / vLLM)  │  │
│   └──────────┘   └─────────┘   └────────┘   └──────────────────┘  │
│         │             │             │                │             │
│         ▼             ▼             ▼                ▼             │
│   ┌────────────────────────────────────────────────────────────┐  │
│   │ shared volume: natives · text · index · vectors · logs     │  │
│   └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│   ┌────────────┐      ┌──────────────────────────────────────┐    │
│   │ review UI  │      │ egress monitor  ──▶ attestation.json │    │
│   └────────────┘      └──────────────────────────────────────┘    │
│                                                                    │
└────────────── egress: DEFAULT DENY (loopback + LAN only) ──────────┘
```

* Every box runs with the network unplugged. That is the design constraint, not a bonus.
* The **egress monitor is a first-class service**, not a debugging tool

> Draw the boundary first, then put the boxes inside it. Architectures that start with
> boxes end up with a box outside the line.

Notes:

The last line is the practical advice. Teams design the system, then ask "where does the
privacy go?" The order has to be inverted: draw the boundary, then nothing crosses it
without a decision and a line in the attestation.

---

## Containerize It

* **One compose file** that brings up the whole stack. The customer runs one command.
* **Pin everything** — base images by digest, model by hash, Python deps locked
* **`network_mode` / explicit networks** — an internal network for the AI services with no
  route out; expose only the UI port
* **Volumes, not bind-mounts, for evidence** — and document where the data lives, because a
  customer will ask you to prove where it is
* Ship the **model weights** with the appliance, or pull once + verify hash + go offline
* Smoke test on install: `verify-setup` → model responds → index builds → attestation emits

```yaml
services:
  ollama:
    image: ollama/ollama@sha256:...        # pinned by digest
    networks: [internal]                   # no route to the internet
    volumes: [models:/root/.ollama]
  app:
    build: .
    networks: [internal, frontend]
    environment:
      OPENAI_BASE_URL: http://ollama:11434/v1
      MODEL: qwen3:14b
      EGRESS_POLICY: deny
networks:
  internal: { internal: true }             # <- the line that does the work
  frontend: {}
```

> `internal: true` is four words that turn a privacy *policy* into a privacy *mechanism*.

Notes:

Point at that one YAML line. It is the smallest possible illustration of the module's theme:
enforcement beats intention. A student can go back on Monday and add it.

Mention jpackage/jlink and bundled runtimes for desktop distribution — FreeEed's direction —
because "the customer must install Java first" kills small-firm adoption.

---

## Sizing, Briefly and Honestly

| Workload | Shape |
|---|---|
| **Extraction / OCR** | CPU- and I/O-bound. Scale by **worker count**. Embarrassingly parallel. |
| **Indexing** | I/O-bound; index ≈ 20–40% of extracted text size |
| **Embeddings** | GPU helps a lot; one-time per corpus (per embedding model) |
| **Chat / RAG** | GPU-bound; **VRAM sets your model tier** (Module 5 table) |
| **Review classification** | Batched inference; the throughput question, so vLLM not Ollama |

* A CPU-only box is fine for prototyping and **not** fine for throughput. Say that to the
  customer before they buy it.
* The honest sizing question: *documents per hour at what quality tier* — then work backwards.

> Prototype on a laptop. Do not **quote** a laptop.

Notes:

Students in product roles will be asked to size a deployment within a month of this course.
Give them the shape: OCR scales with cores, review scales with VRAM and batching, and the
quality tier is set by VRAM — which means the hardware conversation and the model-choice
conversation are the same conversation.

---

## AI Governance for Legal, In Brief

* The landscape, honestly: **100+ US state AI laws** and the **EU AI Act** are real, moving,
  and mostly not about you specifically — yet
* What is already binding on your users **today**:
  - **protective orders** in the matter (Morgan v. V2X: the order may name which tools are allowed)
  - **client outside-counsel guidelines** — increasingly contain AI clauses
  - **professional-responsibility duties** — competence, confidentiality, supervision
  - **sector regimes** — CJIS, HIPAA, GLBA, state privacy law
* What your system owes them:
  - a written **AI use policy** it can enforce
  - **disclosure** of which AI components touched the material (this is now discoverable)
  - an **audit trail** per matter
  - **re-assessment** when anything changes

> Your users' obligations become your product requirements. Design the audit trail they
> will be asked for before they are asked for it.

Notes:

Keep this tight — 10 minutes. The deep version is Module 12, later today. The actionable
point is the last one: the protective order and the client guidelines bind your users today,
and they are the near-term source of product requirements, not the EU AI Act.

---

## Scoring It: SAIS-100

> *"Is our AI secure?"* has no useful answer. **SAIS-100** replaces it with six sharper
> questions and one number out of 100.

| Category | Wt | The question |
|---|---|---|
| **Data Security** | 20 | Can it leak data? |
| **Prompt Security** | 20 | Can it be manipulated? |
| **Agent Security** | 20 | Can it misuse tools? |
| **Model & Supply Chain** | 15 | Can I trust what I didn't build? |
| **Detection & Monitoring** | 15 | Can I detect and trace an attack? |
| **Governance** | 10 | Can the program sustain it? |

* Three questions per category, each scored **0–3** against **anchored** levels
  (coverage × enforcement × verification)
* Category score = `round(raw / 9 × weight)`

| Total | Verdict |
|---|---|
| 85–100 | Enterprise Ready |
| 70–84 | Production Ready |
| 50–69 | Significant Risk |
| < 50 | **Do Not Deploy** |

**Override:** certain single findings force *Do Not Deploy* regardless of the total.

Notes:

SAIS-100 is the Elephant Scale Secure AI Score — the same framework taught in *Building
Secure AI Applications* and *AI Security for Security Teams*. It is not legal-specific, which
is the point: your legal-AI system is still an AI application and gets scored like one.

The anchored 0–3 levels are what make two assessors converge. "Mostly in place" is a feeling;
"enforced in code on the main paths, spot-checked" is a state you can point at.

---

## The Legal Overlay

Same six categories, same weights. **Legal-specific evidence**, and legal auto-fails.

| Category | What a legal system must show |
|---|---|
| **Data Security** | Egress attestation from Module 5; **matter isolation** (not tenant — *matter*); privilege-flag handling in logs |
| **Prompt Security** | Retrieved document text fenced as untrusted — remember, **the adversary may have written your corpus**; citation verifier enforced in code |
| **Agent Security** | Approval gates on **production**, deletion, and any outbound transfer |
| **Model & Supply Chain** | Model pinned **by hash**; weights verified; embedding model + dim recorded; reproducibility bundle replays |
| **Detection & Monitoring** | Per-matter audit trail; **rendered prompts + retrieved context** stored; override rate tracked |
| **Governance** | Written AI use policy; validation protocol **pre-registered**; re-score on model change |

**Legal auto-fails — any one is Do Not Deploy:**

* A **privileged document** can reach a third-party endpoint by any path (OCR, embeddings,
  chat, logs)
* **Cross-matter leakage** — matter A's documents retrievable in matter B's context
* A **production** can be triggered without recorded human approval
* The **model cannot be pinned**, so the review cannot be reproduced

> Six categories for the security posture. Four auto-fails for the legal posture. A
> legal-AI system that scores 92 and fails one auto-fail does **not** ship.

Notes:

The matter-isolation framing is the legal translation of SAIS-100's tenant-isolation question
and it is the one students most often get wrong, because matters are not tenants — the same
firm, the same users, and sometimes the same custodians appear in both, with an ethical wall
between them. That is harder than multi-tenancy, not easier.

The fourth auto-fail is the one that is genuinely new to the security world and it comes
straight out of Module 6. It is also a strong argument for local inference, which is why it
earns a place on the list.

---

## Scoring Walk-Through

Score the system you built in Labs 02–07, in pairs, in twenty minutes:

1. Walk the six categories **in order**. Don't skip to the one you're proud of.
2. Three questions each, 0–3 against the anchored levels. **Name the evidence** for each —
   a file, a config line, a test. "We're careful" is a 0.
3. `round(raw/9 × weight)` per category; total to /100.
4. Apply the verdict table, then the **four legal auto-fails**.
5. Name the **single change** that would raise the score the most.

> Then write the number down. The point of a score is the **next** score.

Notes:

Keep it fast — speed and repeatability are the framework's whole value. Debrief on where
pairs disagreed on a sub-score; that disagreement is where the rubric wording needs
sharpening, and students genuinely enjoy arguing about it.

The step-5 answer is almost always either "enforce egress rather than observe it" or "write
the validation protocol before the run." Both are cheap, and that is the encouraging note to
end on.

---

## Lab 07 — Score and Package

Wire the stages into one workflow, score it, and package it:

* A `run_matter.py` driver: ingest → index → RAG → review → metrics → bundle, with
  **checkpoints and resumability**
* **Confidence bands** and an approval gate before "production"
* Emit a production set: Bates-numbered, with a `.dat`/`.opt` **load file** and a manifest
* Score with `sais100.py` — six categories, anchored levels, legal auto-fails, one number
* Containerize: `Dockerfile` + `docker-compose.yml` with `internal: true`, pinned digests
* Re-score after one hardening change and record the **delta**

**Deliverable:** `sais100-score.json` (before and after), a production set with a load file,
and a compose file that runs the stack offline.

Notes:

Budget 75 minutes. The before/after score is the part students take back to work — it is a
format their management already understands, and it turns a training course into a Monday
morning proposal.

---

## ▶ LAB BREAK — Lab 07

Debrief: **"Your score, your verdict, and did you trip an auto-fail?"**

Notes:

Collect scores on the board. Expect a wide spread — 45 to 80 — and expect at least one
auto-fail in the room, usually an unpinned model or prompts shipped to a log aggregator.
That auto-fail is the most useful thing that happens in the lab.

---

## Module 7 — What You Should Leave With

* **Autonomy between the gates, a human at every gate**
* Idempotent, append-only, checkpointed stages — the artifact chain *is* the chain of custody
* `internal: true` — enforcement beats intention
* Your users' obligations (protective orders, OCGs, professional duties) are your product
  requirements
* **SAIS-100** with the legal overlay: six categories, one number, four auto-fails
* A score is only useful as a **baseline you re-run**

> Next: you build the whole thing, for yourself, and we try to break it.
