# Defensibility Checklist

**Legal AI Engineering · Elephant Scale · bring this to the next project**

Every line is a question somebody will eventually ask you under oath, in a deposition, in a
26(f) conference, or in an email from a client at 6pm. Each one has a **file** that answers
it. If the answer is a memory or an intention, it is not an answer.

Work through it in order. The order is the discipline.

---

## 1. Collection and ingestion — *"what did you actually have?"*

- [ ] Every container was walked **recursively** — zip in zip, message attached to message,
      scan inside the attached message. Containers are not documents.
- [ ] Every document has a **hash of the native** (`native_sha256`), computed on the bytes as
      received, before any processing.
- [ ] **Families** are preserved: an email and its attachments are separate documents sharing
      a `family_id`. Families are what get reviewed and produced, so family counts are
      reported alongside document counts.
- [ ] Timestamps are stored in **UTC with the original offset kept separately**. "Did he know
      before the 3pm call?" is unanswerable once you have normalized to local time.
- [ ] The **dedupe policy is written down** and was chosen by counsel, not by the engineer.
      Possession is evidence: six custodians holding the same memo may be more probative
      than the memo.
- [ ] Near-duplicates are **grouped, never suppressed**, and the grouping threshold is
      recorded. The threshold decides whether anybody ever diffs the executed contract
      against its drafts — it is a litigation decision wearing a parameter's clothes.
- [ ] The **exception list is non-empty**, triaged, and every row has a **next step**. A
      pipeline reporting zero exceptions over real data is lying to you or swallowing
      errors.
- [ ] The producer's **load file was read and reconciled**, and rows with no corresponding
      native were escalated. Nobody else checks this, and it is a quiet source of
      professional credibility.
- [ ] `extracted_by` records the extractor and **version** for every document. An OCR engine
      upgrade is a pipeline change.

> **The sentence to be able to say:** *"We processed N documents in M families. K did not
> process, for these reasons, and here is the disposition of each."* Two numbers and a list,
> not one number.

---

## 2. Search and culling — *"how did you decide what to look at?"*

- [ ] The **query translation is symmetric**: the analyzer on the query path is the same one
      that built the index. Break the symmetry and recall falls silently.
- [ ] Every search is **logged** — the query as typed, the query as translated, the hit count
      and the date.
- [ ] Hit counts are reported as **documents and families**.
- [ ] Hybrid retrieval keeps its **lexical half**. It is exact on names, defined terms and
      Bates numbers, it is cheap, and it is the only half you can explain to a judge.
- [ ] Where retrieval is semantic, the **embedding model and dimension** are recorded, and
      you know that changing either forces a full re-ingest.

---

## 3. Privilege and confidentiality — *"did anything leave the building?"*

All four leak points, every time:

- [ ] **OCR / text extraction** is local. A cloud document-intelligence API ships the raw
      page one step before your "private" model ever sees it.
- [ ] **Embeddings** are local. A hosted embedder receives the full chunk text — this is the
      leak point people miss, because the chat model is the one they were thinking about.
- [ ] The **chat / extraction model** is local, or its data handling is contractually covered
      and you can produce the contract.
- [ ] **Logs, traces and telemetry** stay local. An error tracker that uploads a stack trace
      containing document text is an egress path with a nice dashboard.

Then:

- [ ] Egress is **enforced**, not observed. A monitor in observe-only mode tells you what did
      happen; only enforcement tells you what cannot.
- [ ] A **tripwire test** exists: a deliberate connection attempt to a hosted model, a log
      aggregator and a cloud OCR endpoint, each blocked and logged.
- [ ] The **attestation** records non-loopback connection count (should be 0), the policy in
      force, the date, and an honest **`scope_and_limits`** — what the monitor covers and
      what it does not. An empty limits field is an overclaim.
- [ ] **Matter isolation** is bound server-side. The matter id is held by the system, never
      accepted from the model, and a cross-matter request produces a logged refusal.
- [ ] Privileged material is handled by **rule plus human review**, and the privilege log is
      an output of the system, not a spreadsheet beside it.
- [ ] **Fine-tuning on case data was considered and rejected**, for the *retention* reason:
      weights trained on one matter's documents carry that matter forward into every later
      use, and you cannot un-train them.

---

## 4. Review and measurement — *"how good is it, and how do you know?"*

- [ ] **Richness was estimated first**, on a random sample, before any classifier was built.
- [ ] The **protocol was written and hashed before the classification run**, and the dates
      prove the order. This is the single most common failure, and the tool should refuse to
      proceed without it.
- [ ] The protocol names the **threshold, the sample sizes, the stop rule, and the person**
      who fixed them.
- [ ] Ground truth is **blind** — held where the pipeline cannot read it, and not opened
      before measurement.
- [ ] **Recall, elusion and precision** are all three reported, each with a **confidence
      interval**. Recall alone says nothing about what you missed; elusion samples the
      discard pile directly.
- [ ] The **sample size is adequate for the claim**. A 400-document sample cannot resolve a
      1% elusion difference, and saying so is better than implying otherwise.
- [ ] Reviewer-vs-reviewer **agreement** was measured on double-reviewed documents, and you
      know that kappa falls as prevalence falls even when agreement does not.
- [ ] Every coding decision has a **rationale and citations** that resolve to a document and
      a character offset.
- [ ] A **human reviewed** every document in the categories where a mistake is not
      recoverable: privilege, and anything going out the door.

---

## 5. Model output — *"why does it say that?"*

- [ ] Citations are **enforced in code**, not requested in the prompt. Three checks: no
      fabricated markers, no uncited claims, quotations verbatim in the source.
- [ ] The system can say **"not found in the provided documents"** and sometimes does. A
      system that never refuses is making things up and you have not caught it yet.
- [ ] Retrieved text is **fenced** and declared to be data. Some of your documents were
      written by the opposing party — in discovery, that is the definition, not a
      hypothetical.
- [ ] An embedded instruction in a document is **reported and cited, never obeyed**, and the
      instruction is preserved rather than stripped: tampering with a review is itself a
      finding.
- [ ] The **rendered prompt** is logged, with the retrieved chunk set. The template plus a
      bug is not what ran.
- [ ] Temperature, seed and the stop conditions are recorded, and you are honest that **GPU
      inference is not bit-reproducible** — which is why the claim is *same determinations*
      and not *bit-exact*.

---

## 6. Agents and automation — *"what could it have done?"*

- [ ] The tool registry is **closed**. `produce`, `delete`, `flag_privileged` and
      `code_document` are **absent from the registry**, not present and disabled.
- [ ] **Approval is a command, not a tool.** An agent that can call `approve` has no approval
      gate.
- [ ] Irreversible steps **refuse** without a recorded approval and exit non-zero. A warning
      is not a gate.
- [ ] Every doc id the model names is **validated server-side** against the matter's catalog.
      Out-of-matter and unknown are indistinguishable from the model's side — telling it that
      a document exists elsewhere is itself a cross-matter disclosure.
- [ ] Step and context **budgets** are enforced before execution. A refusal that still did
      the work is not a refusal.
- [ ] Every step, **including every refusal**, is in a log. The refusals are the valuable
      part: they show the system was asked and said no.

---

## 7. Reproducibility — *"re-run it in front of me."*

- [ ] A **reproducibility bundle** exists: manifest, corpus catalog and exceptions, rendered
      prompts and responses, retrieval records, decisions, protocol, ground truth, metrics,
      attestation, and a `VERIFY.md`.
- [ ] The manifest pins **everything that changes the output**: model and digest, embedding
      model and dimension, chunking, prompts, code hash, dependency versions, OCR engine
      version, random seeds.
- [ ] **`VERIFY.md` has been run by someone else**, in a different directory, and it worked.
      Untested instructions are a wish.
- [ ] The **claim is stated at the right level** — *same determinations* or *bit-exact* — and
      the reason is given.
- [ ] Stage artifacts are **checkpointed and idempotent** on `(matter, doc_id, stage,
      config_hash)`, so a resumed run cannot silently mix two configurations.
- [ ] You can state **which files are evidence and which are derived**, and the `.gitignore`
      proves you know the difference.

---

## 8. Production and disposal — *"what went out, and what is left?"*

- [ ] Every production carries a **named human approval** with a timestamp that predates it.
- [ ] The production manifest lists **what was withheld and why**, by reason and count.
- [ ] Load files are written in the **encoding the recipient expects** (cp1252 and CRLF for
      Concordance-style `.dat`, in 2026, really) and the delimiters are the industry's, not
      a CSV guess.
- [ ] Disclosures made with the production are recorded in the manifest — including OCR
      quality, exceptions, and anything the system could not resolve.
- [ ] **Destruction can be verified.** Verification tokens are derived and recorded *before*
      deletion, because the catalog you need to verify against is the thing you just
      deleted.
- [ ] The destruction certificate names **every artifact class** considered, including the
      ones people forget: extracted text, the search index, chunks, vectors, rendered
      prompts, responses, the work queue database, the reproducibility bundle, and any
      production set already sent.
- [ ] You are honest that **overwriting is defence in depth, not a guarantee** — SSD wear
      levelling and copy-on-write filesystems mean the bytes may persist. Encrypt-then-
      destroy-keys is the stronger story.

---

## 9. Governance — *"who is accountable?"*

- [ ] A named human **owns** the output. Not a team, not a vendor, not the model.
- [ ] Every claim has a **written limit**. "No significant limitations" is a failing answer.
- [ ] The system has been **scored against SAIS-100 with the legal overlay**, before and
      after a hardening change, with **no auto-fail**.
- [ ] Gaps consciously carried are **written down as carried**, with who decided and why. An
      undocumented known gap is the finding; a documented one is a decision.
- [ ] Your own **AI use is discoverable**. The tool you chose, and the terms you accepted,
      may themselves be ordered disclosed — so choose on the record.

---

## The seven questions, for the fifteen seconds you will get

1. Show me your **exception list**. What happened to those documents?
2. What is your **recall**, and what is the confidence interval?
3. Who chose the **validation threshold**, and when?
4. Walk me through why **this document** was coded responsive.
5. Prove **no document content left this machine**. What exactly does your monitor cover?
6. **Re-run** this review in front of me.
7. What **model version**? Can you still get those weights?

If you can answer all seven with a file, you are defensible. If you can answer six, you know
which one to go fix.

---

*Modules 2–12 · the whole course on one checklist*
