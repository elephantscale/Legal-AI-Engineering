# SAIS-100 → the frameworks a reviewer already recognizes

**SAIS-100 is an instrument, not a standard.** It is Elephant Scale's scoring rubric: six
categories, eighteen questions, anchored 0–3, with a legal overlay that demands evidence and
voids the score on four conditions. It has no accrediting body and no external recognition, and
you should never present it as though it does.

That is not a weakness as long as you can translate. A GC, a CISO, a client's security reviewer
or a regulator each has a vocabulary already, and every SAIS-100 question lands somewhere in it.
This page is the translation table.

> **The sentence that does the work:**
> *"We score this internally against a rubric called SAIS-100. The control you are asking about
> is our Data Security question D1, which is NIST AI RMF Measure 2.7 and EU AI Act Article 15 —
> here is the artifact."*
>
> You lead with their framework and their artifact. SAIS-100 is how you organised the work, not
> what you are asking them to accept.

---

## 1 · Data Security — weight 20

**D1** unapproved egress prevented · **D2** matter isolation · **D3** source data preserved and
provably unmodified

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Measure 2.7** — *"AI system security and resilience … are evaluated and documented."* **Measure 2.10** — *"Privacy risk of the AI system … is examined and documented."* |
| **ISO/IEC 42001** | Data for development and enhancement of the AI system · Acquisition of data · Data provenance |
| **EU AI Act** | **Art. 10** (data governance) · **Art. 15** (cybersecurity) |
| **Legal authority** | **ABA Model Rule 1.6(c)** — reasonable efforts to prevent inadvertent disclosure · **FRE 502(b)** — reasonable steps to prevent and to rectify · **FRCP 37(e)** — ESI preservation · ethical-wall screening (**Rules 1.10, 1.18**) for D2 · **CJIS Security Policy** where criminal-justice data is in scope |

**What SAIS-100 adds here:** D1 is scored against an *attestation artifact* — an enforced egress
policy and a connection record — not against a policy document. Auto-fail **LEGAL-A** fires when
content can leave by a path that is neither approved nor enforced. None of the frameworks above
make that a pass/fail; they ask you to evaluate and document it.

---

## 2 · Prompt Security — weight 20

**P1** untrusted document content isolated from instructions · **P2** outputs verified against
sources · **P3** every prompt recorded

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Measure 2.7** (security and resilience — prompt injection is an input-channel attack) · **Measure 2.6** — the system *"can fail safely, particularly if made to operate beyond its knowledge limits"* · **Measure 2.9** — *"The AI model is explained, validated, and documented, and AI system output is interpreted within its context."* |
| **ISO/IEC 42001** | AI system recording of event logs · AI system verification and validation |
| **EU AI Act** | **Art. 12** (record-keeping / automatic logs) · **Art. 15** (robustness against adversarial manipulation) |
| **Legal authority** | **Model Rule 1.1 cmt. [8]** — technology competence · **ABA Formal Opinion 512 (2024)** on generative AI — verify outputs · **Model Rule 3.3** — candor; a fabricated citation is a candor problem before it is a technical one |

**What SAIS-100 adds here:** P2 is scored on whether verification is *mechanical and logged*, not
on whether a human was told to check. That is the difference between a citation checker and a
policy that says "lawyers should review AI output."

---

## 3 · Agent Security — weight 20

**A1** irreversible actions require human authorization · **A2** autonomy bounded by policy ·
**A3** every automated step logged and replayable

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Govern 3.2** — *"roles and responsibilities for human-AI configurations and oversight of AI systems"* · **Manage 2.4** — mechanisms to *"supersede, disengage, or deactivate AI systems"* · **Manage 4.1** — monitoring plans *"including … appeal and override"* |
| **ISO/IEC 42001** | Objectives for responsible use of the AI system · Intended use of the AI system · AI system operation and monitoring |
| **EU AI Act** | **Art. 14** (human oversight) · **Art. 26** (deployer obligations) |
| **Legal authority** | **Model Rule 5.3** — responsibilities regarding nonlawyer assistance, which is the closest existing analogue to supervising an agent · **FRCP 26(g)** — a *named human* signs the discovery response |

**What SAIS-100 adds here:** A1 is scored on a recorded approval attached to the irreversible act
itself. Auto-fail **LEGAL-C** fires when a production is emitted with no recorded human approval.
Art. 14 requires oversight be *possible*; SAIS-100 asks for the receipt.

---

## 4 · Model and Supply Chain — weight 15

**M1** model pinned to a verifiable version · **M2** code and dependencies version-pinned ·
**M3** retrieval layer reproducible

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Map 4.1** — *"Approaches for mapping AI technology and legal risks of its components – including the use of third-party data or software – are in place, followed, and documented"* · **Govern 6.1** — policies addressing third-party AI risks · **Manage 3.2** — pre-trained models monitored as part of regular maintenance |
| **ISO/IEC 42001** | Suppliers · Allocating responsibilities · Tooling resources |
| **EU AI Act** | **Art. 11** (technical documentation) · **Art. 25** (responsibilities along the value chain) |
| **Legal authority** | **Model Rule 5.3** (vendor supervision) · reproducibility as the practical precondition for defending a review a year later |

**What SAIS-100 adds here:** M1 is scored on a weights hash, not a model name. Auto-fail
**LEGAL-D** fires when the model cannot be pinned to a verifiable version — because without the
pin you cannot reproduce the review, and a review you cannot reproduce is one you cannot defend.

---

## 5 · Detection and Monitoring — weight 15

**T1** an attempted disclosure would be detected · **T2** processing failures surfaced and
triaged · **T3** output quality measured against independent ground truth

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Manage 4.1** — post-deployment monitoring, incident response, recovery · **Manage 4.3** — *"Incidents and errors are communicated to relevant AI actors"* · **Measure 2.13** — *"Effectiveness of the employed TEVV metrics and processes … are evaluated and documented."* |
| **ISO/IEC 42001** | AI system operation and monitoring · Communication of incidents · External reporting |
| **EU AI Act** | **Art. 72** (post-market monitoring) · **Art. 73** (serious incident reporting) · **Art. 15** (accuracy) |
| **Legal authority** | **FRE 502(b)(2)–(3)** — reasonable steps to prevent *and to rectify* · **FRCP 26(g)** · Sedona Conference guidance on TAR validation |

**What SAIS-100 adds here:** T3 requires the ground truth be *independent and blind* — recall and
elusion with an interval, not a point estimate from the same people who trained the classifier.
"Measure 2.13" asks whether your metrics are effective; SAIS-100 asks to see the sample.

---

## 6 · Governance — weight 10

**G1** a written protocol fixed before the run · **G2** independent reproduction ·
**G3** limits of each claim stated explicitly

| Framework | Where this lands |
|---|---|
| **NIST AI RMF 1.0** | **Govern 1.1** — *"Legal and regulatory requirements involving AI are understood, managed, and documented."* · **Measure 2.8** — *"Risks associated with transparency and accountability … are examined and documented."* |
| **ISO/IEC 42001** | AI policy · Review of the AI policy · System documentation and information for users |
| **EU AI Act** | **Art. 17** (quality management system) · **Art. 11** (technical documentation) · **Art. 13** (transparency to deployers) |
| **Legal authority** | **FRCP 26(g)** · protocol disclosure in TAR disputes · Sedona Conference principles on process transparency |

**What SAIS-100 adds here:** G1 is scored on whether the protocol was fixed *before* the run, which
is checkable from timestamps. A protocol written afterwards describes what happened; a protocol
written beforehand is a commitment you can be held to. The frameworks ask for documentation and
do not care when it was written.

---

## What SAIS-100 has that none of them have

1. **A number that moves.** Break egress, watch the score drop and the verdict flip. The
   frameworks are qualitative; a score makes a regression visible to someone who does not read
   the control text.
2. **Evidence per question, not attestation per control.** Every answer cites an artifact in the
   bundle. A questionnaire answered from memory is worth nothing under cross-examination.
3. **Four auto-fail conditions** — LEGAL-A through LEGAL-D — that void the score regardless of
   the number. No framework above is pass/fail; all of them are "evaluate and document."

## What it does not have, and do not claim it does

- **No accrediting body, no certification scheme, no registry of assessors.** A SAIS-100 score is
  a self-assessment unless an independent party re-ran it — which is exactly what G2 scores.
- **No regulatory standing.** A SAIS-100 of 96 satisfies nothing in law. It is evidence that you
  worked systematically, and that is all it is.
- **No coverage of fairness, bias, environmental impact or societal effect.** NIST Measure 2.11
  and 2.12 have no SAIS-100 equivalent. In a legal-review context that is a deliberate scope
  choice, not an oversight — say so rather than letting someone discover the gap.

---

## Currency

**Verify before you cite in front of a reviewer.** Clause numbers move and this field is young.

- **NIST AI RMF** subcategory wording above is quoted from NIST's own
  *AI RMF to ISO/IEC FDIS 42001 Crosswalk* (`airc.nist.gov`). AI RMF 1.0 is NIST AI 100-1
  (January 2023) and has been under revision.
- **ISO/IEC 42001** control *topics* are named rather than numbered, deliberately: NIST's
  crosswalk is against the **FDIS** draft and uses a different annex numbering from the published
  ISO/IEC 42001:2023. Check the clause number against the published standard before quoting one.
- **EU AI Act** is Regulation (EU) 2024/1689; high-risk obligations phase in on a staged timetable.
  Check EUR-Lex for the current text and dates.
- **ABA Model Rules** are model rules. Your jurisdiction's adopted version governs, and state
  guidance on generative AI is appearing steadily.

*Elephant Scale · Legal AI Engineering · first issued 2026-11-12*
