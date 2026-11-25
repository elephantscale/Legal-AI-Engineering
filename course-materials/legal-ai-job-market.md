# The Legal AI Job Market — what the postings actually say

**Nine postings · six employers · read 2026-11-11.** A snapshot, not a market study. Read the
[caveats](#caveats-carry-these) before you quote any number in this document.

> **The finding in one sentence.** The job title *Legal AI Engineer* is, in four cases out of
> six, a **J.D.-gated adoption role** on a commercial platform. The roles that want what this
> course teaches — build the pipeline, prove the privacy, measure the review — exist, pay
> comparably or better, and are titled something else.

This handout exists so you apply to the right half of the market. The course is well aimed at
the engineer-titled roles and **mis-titled for the lawyer-titled ones**. Knowing which is which
is worth more than another lab.

---

## 1 · The split

### Lawyer-titled — a J.D. is a hard requirement

| Title | Employer | The gate, in their words | Published range |
|---|---|---|---|
| **Legal AI Engineer** | Dentons (Chicago) | *"at least two years of substantive legal practice"* plus two in legal engineering or AI | not published |
| **Legal AI Engineer** | Thomson Reuters (Eagan, MN) | *"J.D. from an accredited US law school required."* *"Prior experience practicing law required."* | $100,100–$185,900 |
| **Legal AI Engineer, Corporate** | Debevoise & Plimpton (NY) | **J.D. + 3 years** practising, innovation or KM attorney | the posting asks *you* to state it |
| **Legal AI Advisor** | Relativity (remote) | *"Juris Doctor (JD) and Bar admission."* 3+ years practising | $152,000–$228,000 |
| **Legal Technology & AI Attorney** | Gibson Dunn (per practice group) | *"J.D. or LL.B. and admitted to practice"*, 4+ years in a technology-focused practice | $250,000–$300,000 |

These are real jobs and they pay well. **No course can get you one.** They want a lawyer who
already practises, and the AI work sits on top of that. If you hold a J.D., see §4.

### Engineer-titled — no J.D., and this is your market

| Title | Employer | What they ask for | Published range |
|---|---|---|---|
| **Senior Software Engineer, AI** · CoCounsel FDE | Thomson Reuters (Frisco, TX) | 5+ yrs engineering, 2+ yrs production LLM apps, **RAG + vector DBs**, **MCP / A2A**, Python/FastAPI, IaC, observability, eval platforms, red-teaming | **$136,000–$253,000** |
| **AI Automation Engineer** | Dentons (Chicago) — *filled* | Copilot Studio, Power Platform, Azure AI Foundry, **RAG**, must meet *"client confidentiality, ethical wall, data privacy, security, responsible AI and data governance"* requirements | $99,500–$125,000 |
| **Legal AI Engineer (Contractor)** | Gusto — *closed* | *"walk through something you built from prompt to production"*, Claude, agentic workflows, **MCP**, working inside IT/security governance on tool approvals | **$150 / hour** |
| **Senior Legal AI Engineer** | Thomson Reuters | J.D. **or** equivalent depth in practice, **plus** software engineering; Python; LLM evaluation — *"measuring hallucination risk and citation quality"* | not published |

**The Dentons pair is the whole finding inside one firm.** Same city, same month. The posting
titled *Legal AI Engineer* wants a lawyer and publishes no salary. The posting titled *AI
Automation Engineer* wants an engineer, requires no J.D., names RAG and ethical walls, and
publishes $99,500–$125,000.

**The best-paid role in the set is engineer-titled.** Thomson Reuters' CoCounsel
forward-deployed engineer tops out at $253,000 and asks for a J.D. nowhere.

---

## 2 · What the postings ask for, against what you built

### They ask, and the course delivers

| What they ask for | Who asks | Where you built it |
|---|---|---|
| Ingestion of messy legal data, OCR, large document sets | TR Eagan, Relativity, Dentons AAE | **Lab 02** |
| Search and retrieval over a corpus | TR, Relativity | **Lab 03** |
| RAG architecture, chunking, vector databases | TR FDE *(required)*, Dentons AAE, Gusto | **Lab 04** |
| Citation quality and hallucination measurement | TR Senior Legal AI Engineer, **by name** | **Lab 04** verifier + **Lab 06** |
| Confidentiality, privilege, ethical walls, data governance | Dentons ×2, Debevoise, Gibson Dunn, Gusto | **Lab 05** |
| Multi-step agentic workflows, tool use, guardrails | TR FDE *(required)*, Gusto, Dentons AAE | **Lab 10** |
| Governance, responsible AI, audit | Gibson Dunn, Dentons AAE | **Lab 12** + SAIS-100 |
| Regulated-environment work (CJIS / FedRAMP-shaped) | TR FDE *(preferred)* | **Lab 11** |
| Legal fluency taught in context | all nine | Modules 1, 5, 6 |

### You are ahead of what they ask

Local serving with **enforced egress and an attestation**, **recall / elusion / precision
against blind ground truth**, and a **reproducibility bundle that replays** are asked for by
*nobody in this set by name*. Five postings require an *understanding* of confidentiality and
privilege; **not one asks for evidence that egress was enforced.**

That is the honest shape of it: this is the market's least articulated requirement and your
strongest material. Treat it as the thing you demonstrate rather than the thing you are asked
for — it is what makes a security review say yes, and it is the answer when someone asks what
you did that the other candidate did not.

### They ask, and the course does not teach it

| Gap | Who asks | What to do about it |
|---|---|---|
| **Commercial platform configuration** — Harvey, Copilot Studio, Azure AI Foundry, Relativity aiR / claiR, CoCounsel | Dentons ×2, TR ×3, Relativity | The largest gap. You built the layer underneath each of them; say that, and name what you still owe a court either way |
| **AI adoption and enablement** — demos, onboarding, training lawyers, driving usage | **five of six employers** — the most-repeated responsibility in the whole set | Not taught here. If you want these roles, get a pilot and a training session on your record |
| **MCP / A2A integration** | TR FDE *(required)*, Gusto *(required)* | A weekend. Wire one MCP server into your Lab 10 workflow and you have the line |
| **Eval and observability platforms** — LangSmith, Langfuse, Braintrust, W&B; Datadog, Grafana, tracing | TR FDE | You wrote the metrics by hand in Lab 06, which is better preparation than clicking one. Learn one product's vocabulary |
| **Orchestration frameworks** — LangChain, LangGraph, PydanticAI, AutoGen | TR FDE | The labs are stdlib-only on purpose. You will fail a screen if you have never seen LangGraph — read it once |
| **DMS integration** (iManage, NetDocuments) and **OAuth 2.0 / OIDC / JWT** | TR FDE, Dentons AAE | Real requirements, wrong course. Say so rather than pretend |

**Nothing on that list is a reason to doubt the course.** Every item is a named, learnable
thing you can add in days, on top of a system you can already defend. The reverse is not true:
nobody adds "I can prove exactly where the documents went" in a weekend.

---

## 3 · Which door this opens

Target the **engineer-titled** roles: *Forward-Deployed Engineer*, *AI Automation Engineer*,
*AI Solutions Engineer*, *Legal AI Engineer (Contractor)*, *Senior Software Engineer, AI* on a
legal product team. Also litigation support engineer, eDiscovery solutions architect, and
forensic technologist — same job, different decade's vocabulary.

**Lead with the capstone, not the certificate.** Your repository and `DEFENSE.md` answer in
artifacts what every one of these postings asks in prose. Gusto's screen is literally *"walk
through something you built from prompt to production"* — that is your capstone defense, and
you have already done it once under adversarial questioning.

Three sentences worth having ready:

- *"I built the retrieval and review pipeline, and I can show you the recall and elusion
  numbers against blind ground truth, with an interval."*
- *"I ran it against a local model with egress enforced, and the attestation is in the
  repository."*
- *"The bundle replays — pinned model, logged prompts, the decisions. You can re-run it."*

**What the skill is worth on its own:** Gusto paid **$150/hour** for a contractor doing
approximately this capstone in-house, ~20 hours a week on a three-month engagement. One data
point, and that posting is closed — but it is a real published number.

---

## 4 · If you hold a J.D.

The lawyer-titled roles above are open to you and this course is genuinely useful for them —
you will be the candidate who understands what the platform is doing rather than the one
repeating the vendor's slide. Dentons' *Legal AI Engineer* wants configuration of *"workflows,
agents or prompt libraries"* and the judgement to decide *"where human review is needed"*;
Module 7 and the SAIS-100 overlay are that conversation.

Two things to add that this course does not give you: **the named platforms** (§2) and
**adoption** — running a pilot, training attorneys, measuring usage honestly. Five of six
employers ask for the second, and it is the most-repeated responsibility in the entire set.

---

## Caveats — carry these

1. **Nine postings is a sample, not a market.** It is enough to establish the title split and
   the platform-naming pattern, both unambiguous. It is **not** enough to size demand. Say
   "these nine postings say," never "the market requires."
2. **Four of the nine could not be read from the employer's own page.** Dentons returns HTTP
   403 to automated fetch; Thomson Reuters and Relativity use JavaScript-rendered Workday
   pages that returned empty. Those rows are built from dated mirrors and are marked
   *active-unconfirmed* in the research file. **Verify before quoting.**
3. **Two salary figures were algorithmic estimates and are excluded here.** Debevoise is shown
   as "the posting asks you to state it," because that is what the posting does. Aggregator
   estimates of $92k–$300k for that role are not employer data and should not be repeated.
4. **"Active" is a snapshot of 2026-11-11, and the window moves weekly.** One Gibson Dunn
   posting was removed eleven days before its own published close date. Two rows here are
   already filled or closed and are labelled.
5. **Salary ranges are the top of the published band, not an offer.** Relativity's own posting
   says it: *"Hiring at the top end of the range would not be typical."*

Full postings with URLs, dates, requirement quotes and the complete skills matrix:
**`job-market-research.md`** in the course repository, compiled 2026-11-11.

---

*© Elephant Scale · LEGAL-AI-ENG-2026 · companion to Module 1, "What the Postings Actually Say"*
