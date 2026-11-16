# Job-Market Research — Legal AI Engineering

**Compiled:** 2026-11-11 · **For:** course-market review, not a course rewrite
**Method:** web search plus direct fetch of the primary posting where the employer's own page
could be read; aggregator mirrors where it could not. Every row says which.

> **Read this first.** The market is **split**, and the split runs straight through the job
> title we named the course after. Roles titled *Legal AI Engineer* at law firms and legal
> publishers are, in four cases out of six, **JD-gated adoption and configuration roles** on
> commercial platforms. Roles that match what this course actually teaches — build the
> pipeline, prove the privacy, measure the review — exist, pay comparably, and are titled
> something else: *Forward-Deployed Engineer*, *AI Automation Engineer*, *Legal AI Engineer
> (Contractor)*. The course is well aimed at the second group and **mis-titled for the first**.
> Nothing in this document argues for rewriting the labs. It argues for being precise about
> who is in the room.

---

## 1. The postings

Salary figures are annual USD and are the employer's own published range unless the row says
otherwise. "Active" means a live posting page or a dated mirror with an open window as of
2026-11-11; it does not mean the requisition is unfilled.

### 1.1 Dentons — Legal AI Engineer

| | |
|---|---|
| **Employer** | Dentons US LLP |
| **Location** | Chicago, hybrid |
| **Posted** | October 2026 (URL path `/2026/october/`); a search index read it as ~12 days old on 2026-11-11 |
| **Salary** | Not published |
| **Status** | **Active** — employer page exists. Dentons' site returned HTTP 403 to automated fetch, so the content below is a search engine's read of that page plus aggregator corroboration. **Verify by hand before quoting.** |
| **Source** | [dentons.com](https://www.dentons.com/en/careers/careers-in-the-united-states/business-services-in-the-united-states/2026/october/legal-ai-engineer) · cross-listed on [reframe.lawyer](https://reframe.lawyer/jobs) |

**Legal experience:** "at least two years of substantive legal practice" **and** at least two
years in a legal engineering, innovation attorney, or AI engineering role. Law-firm innovation
team or legal-AI/legal-software company preferred.

**Technical:** building and refining AI workflows, prompts and agents — explicitly *"not only
using AI tools as an end user."* Hands-on configuration of **workflows, agents or prompt
libraries on Harvey and Microsoft Copilot**. Redesigning legal processes for AI and **deciding
where human review is needed**. Coordination with Information Security, Risk and Knowledge
Management to protect **confidential and privileged client data**.

**Why it matters to us:** this is the closest thing to a job description *for* our Module 5 and
Module 7 content — privilege, human-in-the-loop, security coordination — wrapped around a
platform stack we do not teach at all.

### 1.2 Dentons — AI Automation Engineer *(historical — filled)*

| | |
|---|---|
| **Location** | Chicago (parallel DC posting) |
| **Salary** | **$99,500–$125,000** Chicago; $102,000–$130,000 Washington DC — Dentons' own page |
| **Status** | **Closed.** `careers.dentons.com` now returns *"Sorry, this position has been filled."* |
| **Source** | [careers.dentons.com](https://careers.dentons.com/job/Chicago-AI-Automation-Engineer-IL-60290/1373752557/) · [dentons.com](https://www.dentons.com/en/careers/careers-in-the-united-states/business-services-in-the-united-states/2026/october/ai-automation-engineer) |

**Requirements:** design, build, deploy and maintain AI-augmented workflows, agents, Copilot
extensions and integrations using **Microsoft Copilot Studio, Power Platform, Azure AI Foundry,
Microsoft 365**. Evaluate and prototype generative AI for summarization, contract-review
support, intake automation and **retrieval-augmented generation**. Solutions must meet **client
confidentiality, ethical wall, data privacy, security, responsible AI and data governance**
requirements. Azure AI services and prompt engineering expected; **iManage / NetDocuments** a
plus; Claude / Codex experience a plus. **No JD requirement.**

> **The two Dentons postings are the whole finding in one firm.** Same firm, same month, same
> city. The one titled *Legal AI Engineer* wants a lawyer and does not publish a salary. The one
> titled *AI Automation Engineer* wants an engineer, requires no JD, names RAG and ethical walls
> — and pays **$99.5k–$125k**. Our graduate is a candidate for the second, not the first.

### 1.3 Thomson Reuters — Legal AI Engineer (Eagan, MN · JREQ204195)

| | |
|---|---|
| **Posted** | 2026-10-14, updated 2026-10-21, **closes 2026-12-31** |
| **Salary** | **$100,100–$185,900** base, plus possible annual bonus |
| **Status** | **Active** (mirror-dated). The Workday page is JavaScript-rendered and returned empty to fetch; details from a Workday-sourced mirror. |
| **Source** | [Workday req](https://thomsonreuters.wd5.myworkdayjobs.com/external_career_site/job/united-states-of-america-eagan-minnesota/legal-ai-engineer_jreq204195-1) · mirror: [freehire.me](https://freehire.me/jobs/legal-ai-engineer-thomson-reuters-v4lm4dsy) |

**Required:** *"J.D. from an accredited US law school required."* *"Prior experience practicing
law required."* Customer-facing experience, enterprise preferred. Familiarity with **due
diligence, eDiscovery, large document review**. *"Demonstrable experience with generative
artificial intelligence applications."* Travel **25–30%**.

**Preferred:** LLM architecture; *"workflow automation, APIs, integrations, technical
prototyping, data analysis, Python."* **Python is preferred, not required.**

**Named tools:** Westlaw, Practical Law, HighQ, **Relativity, Everlaw**, Thomson Reuters Legal AI.

### 1.4 Thomson Reuters — Senior Legal AI Engineer (JREQ202169)

| | |
|---|---|
| **Salary** | Unknown |
| **Status** | **Active-unconfirmed** — requisition URL resolves; content from aggregators only |
| **Source** | [Workday req](https://thomsonreuters.wd5.myworkdayjobs.com/en-US/External_Career_Site/job/Senior-Legal-AI-Engineer_JREQ202169) · [remotive.com](https://remotive.com/remote/jobs/legal/senior-legal-ai-engineer-5289590) |

JD **or** equivalent depth in legal practice, **plus** software engineering on AI/ML or
LLM-powered applications. **Python proficiency**, LLM evaluation methods, prompt engineering, AI
system design. Responsibilities include leading **LLM evaluation for legal use cases — measuring
hallucination risk and citation quality.**

> **This is the single closest match in the set to Modules 4 and 6.** "Hallucination risk and
> citation quality" is the commercial name for our citation verifier and our recall/elusion
> measurement. It is also the only posting that asks for a JD *or* equivalent rather than a JD.

### 1.5 Thomson Reuters — Senior Software Engineer, AI · CoCounsel FDE

| | |
|---|---|
| **Location** | Frisco, TX |
| **Posted** | ~2026-11-05 ("6d ago" on 2026-11-11) |
| **Salary** | **$136,000–$253,000** (NYC, SF, LA, Irvine, McLean, DC); **$118,400–$219,800** other eligible US locations |
| **Status** | **Active** |
| **Source** | [dreamworkhq.com mirror](https://www.dreamworkhq.com/job/67c272a4-3cd3-44e4-8245-302c9fac3efe) · [zapply.jobs](https://zapply.jobs/jobs/27808426-6464-4614-b5a2-ae201cb03fe8/) |

**Required:** 5+ years software engineering; **2+ years AI/ML in production including LLM apps**;
orchestration frameworks (**LangChain, LangGraph, PydanticAI, AutoGen**); **RAG architectures and
vector databases**; **MCP and A2A** workflow patterns; strong **Python** (FastAPI); cloud + **IaC
(Terraform/CDK)**; **observability (Datadog, Grafana, Prometheus)**; **AI evaluation platforms
(LangSmith, Langfuse, Braintrust, W&B)**; secure APIs (**OAuth 2.0, OIDC, JWT**); prompt
engineering; AI-assisted dev tools (**Claude Code**, Cursor, Copilot).

**Responsibilities:** RAG pipelines and custom agents integrated into client environments
**including document management systems**; multi-step agentic workflows over CoCounsel, Westlaw
and Practical Law; **MLOps/LLMOps with monitoring, logging and tracing**; **evaluations and
red-teaming grounded in legal workflows**, with legal SMEs setting benchmarks; *"Ensure all
solutions comply with ethical AI principles, data protection standards, and enterprise security
requirements."*

**Preferred:** legal terminology fluency; **regulated-industry experience (legal, fintech,
healthcare)**; legal platforms and DMS; Docker/Kubernetes.

> **This is the job our course is actually training people for** — and it is the best-paid role
> in the set. It is titled *Senior Software Engineer*. **No JD.**

### 1.6 Debevoise & Plimpton — Legal AI Engineer, Corporate

| | |
|---|---|
| **Team** | Practice Systems & Applied AI, Information Services Department |
| **Location** | New York, on-site · **Posted** Oct 19 |
| **Salary** | **Unknown.** Legal.io shows a $92,612–$240,040 *algorithmic estimate*, not an employer figure; Indeed/Glassdoor aggregator pages suggest $240k–$300k. The posting itself **asks the applicant to state salary requirements**. |
| **Status** | **Active-unconfirmed** — aggregator only; no Debevoise careers page read |
| **Source** | [legal.io](https://www.legal.io/jobs/5876106/Full-time/Practice-Systems-Applied-AI-Legal-AI-Engineer-Corporate) |

**Required:** **J.D. plus 3+ years** practising attorney, legal innovation, KM attorney or
practice-support attorney. Knowledge of corporate practice and transactional workflows. Strong
working knowledge of **generative AI, LLMs and prompt design**. Understanding of
*"confidentiality, privilege, data governance, professional responsibility, privacy, and ethical
considerations."*

**Responsibilities:** lead **client-facing presentations, demonstrations and trainings**; advise
corporate clients on applying AI in legal departments; serve as a hands-on resource for lawyers
on specific matters, including **quality control and attorney review**; translate legal needs into
functional requirements. **No AI platform is named.** No security tooling is required.

### 1.7 Relativity — Legal AI Advisor (req 26-0396)

| | |
|---|---|
| **Location** | Remote/hybrid, many US metros · **Posted** 2026-09-06 |
| **Salary** | **$152,000–$228,000** plus bonus and long-term incentives; *"Hiring at the top end of the range would not be typical."* Senior variant published to **$276,000**. |
| **Status** | **Active** |
| **Source** | [Workday req](https://kcura.wd1.myworkdayjobs.com/en-US/External_Career_Site/job/Legal-AI-Advisor_26-0396) · [purpose.jobs](https://www.purpose.jobs/discover/companies/relativity/jobs/92411695-legal-ai-advisor) · [himalayas.app (senior)](https://himalayas.app/companies/relativity-com/jobs/senior-legal-ai-advisor) |

**Required:** *"Juris Doctor (JD) and Bar admission."* *"3+ years of experience practicing law at a
law firm [AmLaw is a plus] and/or in-house legal team (litigation experience preferred)."*
*"Hands on experience with legal AI tools, including Relativity aiR."* First-hand knowledge of
litigation workflows.

**Responsibilities:** pre-sales demos that *"connect Relativity's AI capabilities to real legal
use cases"*; *"Help secure the 'legal win'"*; onboarding, training and sustained-usage adoption;
*"Guide customers through workflow transformation and AI integration into legal processes"*; voice
of the legal customer into Product. Named products: **RelativityOne, aiR, claiR**.

**Notably absent:** validation, metrics beyond "measurable impact", and prompt work. The word
*defensibly* appears once, as an adjective. **This is an adoption role, not a defensibility role.**

### 1.8 Gibson Dunn — Legal Technology & AI Attorney *(a family of postings)*

Gibson Dunn is running this title **per practice group**, and the individual postings churn
weekly. As of 2026-11-11:

| Variant | Location | Salary | Status |
|---|---|---|---|
| Tech & Innovation | Century City, CA | **$250,000–$300,000** | Posted 2026-11-02 — [jobs.cccba.org](https://jobs.cccba.org/job/1462/legal-technology-ai-attorney-tech-innovation/) |
| M&A/PE | Palo Alto, CA | $250,000–$300,000 | Posted 2026-11-01 — [gobiglaw.com](https://www.gobiglaw.com/jobs/635951326-legal-technology-ai-attorney-m-a-pe-at-gibson-dunn) |
| Business Restructuring | US offices | Unknown | Window closes 2026-11-16 — [greenhouse](https://job-boards.greenhouse.io/gibsondunn/jobs/4332828009) |
| Tech & Innovation | NYC / remote | $250k–$300k | **Removed 2026-11-05** despite an advertised 11-16 close — [builtinnyc](https://www.builtinnyc.com/job/legal-technology-ai-attorney-tech-innovation/11300167) |
| Real Estate | — | Unknown | **Closed** 2026-08-18 — [gibsondunn.com](https://www.gibsondunn.com/job_staff_gh/legal-technology-ai-attorney-real-estate/) |
| Investment Funds | — | Unknown | **Closed** 2026-08-17; reported to **Senior Director & Counsel of Knowledge & AI** |
| Litigation | — | Unknown | Expired 2026-10-05 |

**Required** (Tech & Innovation): *"Demonstrated passion for AI and emerging technology"*;
*"Minimum of 4 years of experience in a technology-focused practice"*; **J.D. or LL.B. and
admitted to practice**; *"Ability to handle confidential and sensitive information with
appropriate discretion."*

**Responsibilities:** *"Evaluate, prototype, and implement AI-assisted tools, document automation
solutions, prompt libraries"*; *"Participate in technology pilots and assessments"*; *"Lead
training sessions for attorneys and staff"*; capture feedback for continuous improvement. **No
platform is named.** Human review appears only as *"structured review mechanisms"* and
*"independent judgment."*

### 1.9 Gusto — Legal AI Engineer (Contractor) *(historical — closed)*

$150/hour, ~20 h/week, 3-month engagement, remote. **No JD required.** Required: shipping
AI-assisted workflows and being able to *"walk through something you built from prompt to
production"*; **Claude** and comparable LLMs; prompt engineering and agentic workflows; **MCP**
integrations; working within **IT and security governance on tool approvals, data access and
security reviews**. Deliverables include a **queryable knowledge layer** over existing research
and precedent, prompt libraries, and *"a maintenance runbook for every system built"* plus
training the team to administer it.
Source: [jobs.generalcatalyst.com](https://jobs.generalcatalyst.com/companies/gusto/jobs/76306432-legal-ai-engineer-contractor)

> Closed, but the most useful single data point for pricing: a **contractor** doing exactly our
> capstone, in-house, at **$150/hour**. That is the number to quote when a student asks what the
> skill is worth, and it is evidence for the support-and-consulting tier of the ladder.

---

## 2. What the market is actually buying

**Observations across the eight live/recent postings:**

1. **JD-gating is the dominant pattern in the firm/publisher roles, and it is absolute where it
   appears.** Relativity: *"JD and Bar admission."* TR Eagan: *"J.D. ... required."* Debevoise:
   J.D. + 3 years. Gibson Dunn: J.D. + admitted. Dentons *Legal AI Engineer*: two years of
   substantive practice. **Our course cannot satisfy any of these**, and no course can.
2. **The engineer-titled roles are the real addressable market, and they pay well.** TR CoCounsel
   FDE $136k–$253k; Dentons AI Automation Engineer $99.5k–$125k; Gusto $150/hour. None requires a
   JD. All three name RAG, and two name MCP.
3. **Adoption is the most-repeated responsibility in the entire set** — demos, onboarding,
   training lawyers, driving usage. It appears in Dentons, TR Eagan, Relativity, Debevoise and
   Gibson Dunn: **five of six named employers.** It appears in our course **nowhere**.
4. **Commercial platforms are named constantly; we name almost none of them.** Harvey, Microsoft
   Copilot / Copilot Studio, Azure AI Foundry, Microsoft 365, Relativity aiR / claiR /
   RelativityOne, CoCounsel, Westlaw, Practical Law, HighQ, Everlaw, iManage, NetDocuments.
5. **Confidentiality and privilege are table stakes, and nobody asks you to prove them.** Five
   postings require an *understanding* of confidentiality, privilege, ethical walls or data
   governance. **Not one asks for evidence that egress was enforced.** Our strongest material is
   the market's least articulated requirement — which is either our differentiator or our
   over-investment, and the honest answer is that it is both.
6. **Defensibility measurement is asked for once, by name, in the whole set** — TR Senior Legal AI
   Engineer: *"measuring hallucination risk and citation quality."* Our Modules 4 and 6 are built
   for exactly that sentence.
7. **DEC-018 is confirmed by the hiring market.** Every platform named above is cloud. The
   postings that mention architecture mention **Azure AI Foundry** and client-environment
   integration, not air-gaps. Local-first remains correct for the absolute-rule segment and is
   now correctly bounded in Module 5.

---

## 3. Skills matrix — employer requirements against our modules and labs

**Coverage key:** ✅ strong · 🟡 partial · ❌ absent

| Requirement cluster | Who asks for it | Our module / lab | Coverage |
|---|---|---|---|
| Ingestion of messy legal data, OCR, large document sets | TR Eagan (eDiscovery, large review), Relativity, Dentons AAE | **M2 / Lab 02** | ✅ |
| Search and retrieval over a corpus | TR, Relativity | **M3 / Lab 03** | ✅ |
| RAG architecture, vector databases, chunking | TR FDE (required), Dentons AAE, Gusto | **M4 / Lab 04** | ✅ |
| Citation quality / hallucination measurement | TR Senior Legal AI Eng | **M4 verifier + M6 / Labs 04, 06** | ✅ |
| Review metrics against ground truth (recall, elusion, precision) | TR Senior (implicit); nobody by name | **M6 / Lab 06** | ✅ — ahead of the market |
| Confidentiality, privilege, ethical walls, data governance | Dentons (both), Debevoise, Gibson Dunn, Gusto | **M5 / Lab 05** | ✅ — far ahead of the market |
| Local / on-prem serving and egress proof | Nobody in this set | **M5 / Lab 05** | ✅ — no stated demand in these eight postings |
| Reproducibility bundle, pinned models, replay | Nobody by name | **M6 / Lab 06** | ✅ — no stated demand |
| Prompt engineering and **prompt libraries as an artifact** | Dentons LAIE, Gibson Dunn, TR FDE, Gusto, Debevoise | M4, M7 (prompts are written, never curated) | 🟡 |
| Human-in-the-loop / attorney review design, QC | Dentons LAIE (*where human review is needed*), Debevoise (*quality control, attorney review*), Gibson Dunn | **M7 / Lab 07**, LEGAL-C approval gate | 🟡 — we gate production; we do not design review |
| Multi-step agentic workflows, tool use, guardrails | TR FDE (required), Gusto, Dentons AAE | **M10 / Lab 10** (Deep Dive) | ✅ but Deep Dive |
| **MCP / A2A integration** | TR FDE (required), Gusto | — | ❌ |
| **AI evaluation platforms** (LangSmith, Langfuse, Braintrust, W&B) | TR FDE | our own eval code only | ❌ |
| **Observability / MLOps-LLMOps** (Datadog, Grafana, Prometheus; tracing) | TR FDE | M11 (scale), egress monitor | 🟡 |
| **Orchestration frameworks** (LangChain, LangGraph, PydanticAI, AutoGen) | TR FDE | deliberately stdlib-only | ❌ *(by design — reconsider as an appendix, not a rewrite)* |
| Cloud + IaC (Terraform/CDK), containers, Kubernetes | TR FDE, Dentons AAE | **M11 / Lab 11** (compose, not IaC) | 🟡 |
| Secure APIs: OAuth 2.0 / OIDC / JWT | TR FDE | — | ❌ |
| **Commercial platform configuration** (Harvey, Copilot Studio, Azure AI Foundry, aiR, CoCounsel) | Dentons (both), TR (all three), Relativity | Relativity named in passing only | ❌ **largest gap** |
| **DMS integration** (iManage, NetDocuments) | TR FDE, Dentons AAE | — | ❌ |
| **Vendor evaluation, pilots, tool assessment** | Gibson Dunn (core), Dentons AAE (*evaluate and prototype*), Gusto (*tool approvals, security reviews*) | M5 "private spectrum" + the new three-architecture slide | 🟡 — the raw material exists, the artifact does not |
| **AI adoption, lawyer training, demos, change management** | Dentons, TR Eagan, Relativity, Debevoise, Gibson Dunn | — | ❌ **most-repeated requirement in the set** |
| Governance, AI regulation, audit | Gibson Dunn (adjacent), Dentons AAE (responsible AI) | **M12 / Lab 12 + SAIS-100 overlay** | ✅ but Deep Dive |
| Regulated-environment experience (CJIS/FedRAMP-type) | TR FDE (regulated industry, preferred) | **M11** | ✅ |
| Legal domain fluency taught in context | all eight | M1, M5, M6 | ✅ |

**Score, bluntly:** of the five clusters the review was asked to look for, we are **absent on
two** (platform integration, adoption), **partial on three** (workflow/prompt-library
configuration, human oversight design, vendor evaluation). Everything we are *strong* on, the
market currently assumes rather than requests.

---

## 4. Gaps, prioritised

**P1 — cheap, high-leverage, no lab changes.**

1. **A market map in Module 1.** Teach the split: which titles are JD-gated, which are not, what
   each pays, and which door this course opens. One slide plus one handout, built from this
   document. It also answers the question every paying student asks in the first hour, and the
   honest answer is now evidence-backed rather than aspirational.
2. **A platform-equivalence appendix.** One page per core lab: *what you built / what you would
   configure instead in Relativity aiR, CoCounsel, Harvey or Copilot Studio / what you still owe a
   court either way.* This converts our biggest gap into our strongest teaching move, costs no lab
   work, and makes the course legible to a firm buyer and to a cloud-platform partner.
3. **A vendor-evaluation artifact** in `course-materials/`, built on the Module 5 spectrum and the
   new three-architecture slide: the questions to ask a vendor, the evidence to demand, what an
   authorisation package does and does not prove. Gibson Dunn's entire job is this.

**P2 — real work, worth scoping.**

4. **Human-oversight design** as a taught unit: where review goes, sampling rates, QC protocols,
   what an approval gate must record. We *enforce* an approval (LEGAL-C) without ever teaching how
   to design the review around it. Natural home: Module 7, which is now the floating module.
5. **Adoption and enablement.** The most-requested responsibility in the set. A half-module:
   running a pilot, measuring adoption honestly, training lawyers, and the failure modes. This is
   also the piece a non-engineer could consume, which connects it to the open audience question.
6. **MCP as a first-class topic.** Named as *required* by TR FDE and by Gusto; we have an agentic
   lab with no MCP in it. Lab 10 is the place.

**P3 — note and defer.**

7. **Eval-platform and observability literacy** (LangSmith/Langfuse; Datadog/Grafana; tracing) —
   an appendix naming what the production equivalents of our own eval code are.
8. **Orchestration frameworks.** Our stdlib-only rule is a deliberate pedagogical choice and I
   would keep it. But a student who has never seen LangGraph will fail a TR FDE screen, so name it
   and show the mapping once.
9. **OAuth/OIDC/JWT and DMS integration** — real requirements, wrong course. Say so rather than
   pretend coverage.

**Explicitly not recommended:** building a no-code track so that JD-holders can take this course.
It is weeks of work, it contradicts the Intermediate-to-Advanced positioning, and the JD-gated
roles want a lawyer *who already practises*, not a lawyer with a Python certificate. If the
lawyer market is wanted, it is a different product with a different name. This is the same open
question already logged against the audience sentence in `OPERATIONS.md`.

---

## 5. Caveats a reader must carry

- **Four of nine postings could not be read from the employer's own page.** Dentons blocks
  automated fetch (403); Thomson Reuters and Relativity use JavaScript-rendered Workday pages that
  returned empty. Those rows are built from dated mirrors and search-engine reads and are marked
  *active-unconfirmed*. **Verify any figure before it goes in marketing copy.**
- **Two salary figures are algorithmic estimates, not employer data** (Legal.io on Debevoise;
  aggregator ranges on the same role). They are labelled as such and should not be quoted.
- **"Active" is a snapshot of 2026-11-11.** The Gibson Dunn family proves how fast it moves: one
  posting was removed eleven days before its own published deadline.
- **Eight postings is a sample, not a market.** It is enough to establish the JD-gating pattern
  and the platform-naming pattern, both of which are unambiguous. It is not enough to size demand.
