# Module 9 — Investigations: Entities, Relationships, and Timelines

Modular series — swapped into Day 3 on request

Elephant Scale

---

## A Different Question

Discovery asks: **"which documents are responsive?"**

An investigation asks: **"what happened, who knew, and when?"**

* Same corpus. Same ingestion. Completely different output.
* The deliverable is not a document set — it is a **narrative with citations**: a timeline,
  a network, and a set of claims each tied to a document
* Internal investigations, regulatory inquiries, fraud, harassment, trade-secret matters,
  M&A diligence

> Discovery produces documents. An investigation produces a **chronology** — and a
> chronology is an argument.

Notes:

Set the frame early: the investigative output is closer to journalism than to search. Every
line of the timeline is a claim, and every claim needs a citation, which is why Module 4's
citation discipline is a prerequisite for this module rather than a nice-to-have.

---

## Entity Extraction That Earns Its Keep

What you extract from legal/investigative text:

* **People** — and the hard part: `J. Doe`, `jdoe@`, `John`, `JD`, `Dad` are one person
* **Organizations** — including the shells, the subsidiaries, and the misspellings
* **Dates and times** — absolute *and* relative (`"last Thursday"`, `"the day after the call"`)
* **Money** — amounts, currencies, accounts
* **Documents referenced but not present** — *"as we discussed in the side letter"* — the
  single most valuable extraction in an investigation
* **Locations**, systems, project code names

* Two approaches, and you want both:
  - **Rules / gazetteers** — precise, explainable, auditable. Use for the custodian list,
    the known entity list, Bates numbers, account numbers.
  - **LLM extraction to a schema** — recall on messy prose. Temperature 0, validate against
    the schema, **cite the span**.

> The highest-value extraction is a reference to a document you do not have. It tells you
> what to go collect.

Notes:

That takeaway is the one experienced investigators nod at. "Per our conversation" and "see
attached" with no attachment are collection leads, and no keyword list finds them. An LLM
pass asking "does this text reference a document not included here?" is cheap and genuinely
novel.

Insist on span citation for every extracted entity — an entity table with no provenance is
unusable in a report.

---

## Entity Resolution: The Actual Hard Part

```text
  "John Doe" <j.doe@acme.com>        ─┐
  "Doe, John" <jdoe@acme-legal.com>   ├──▶  PERSON-0007
  "JD"                                │        aliases: 5
  "Dad" (in a personal thread)        │        addresses: 3
  <j.doe@gmail.com>                  ─┘        custodian: jdoe
```

* Signals that work: email-address graph, signature blocks, display-name variants,
  co-occurrence, the custodian list, org chart if you have one
* **Never auto-merge silently.** Every merge is a **reviewable decision** with evidence and
  a confidence.
* A wrong merge attributes someone's words to someone else. In a harassment or fraud matter,
  that is not a data-quality issue — it is a false accusation.

> Entity resolution is where an investigation tool can do real harm. Make every merge
> visible, evidenced, and reversible.

Notes:

This is the ethical heart of the module. Engineers treat entity resolution as a clustering
problem with an F1 score. Here a false merge has a victim. Build the merge log, show the
evidence, let a human confirm, and keep it reversible.

---

## Thread Reconstruction

```text
Message-ID / In-Reply-To / References  ──▶  the true tree
                                              │
subject normalization ("Re: Re: FW: ")  ──▶  fallback when headers are missing
                                              │
quoted-text matching                    ──▶  last resort; catches forwards that broke the chain
```

* Build the tree from **headers first** — it is the only reliable signal
* **De-duplicate quoted history** or your summaries will double-count
* **Inclusive emails**: the messages that contain all prior content. Reviewing only the
  inclusive set is a large, legitimate cost saving — *and a documented decision*
* Watch for: the **branch** where someone was dropped from the Cc, and the fork where the
  conversation moved to a new thread or a new channel

> The interesting thing in a thread is usually **who was removed from it**, and when.

Notes:

The dropped-recipient observation is the investigative gold in email threads, and it is a
structural query, not a content query: diff the recipient set between parent and child. It
is twenty lines of code and it finds things no LLM pass will surface.

---

## Timelines: The Deliverable

```text
2026-02-02 09:14 -05:00  DOC-000091  aray → jdoe        "Q3 numbers look off"        [1]
2026-02-02 11:40 -05:00  DOC-000112  jdoe → aray        "let's discuss offline"      [2]
2026-02-03 08:02 -05:00  DOC-000118  jdoe → outside counsel  (privileged — excluded) [3]
2026-03-14 19:02 -05:00  DOC-000417  jdoe → aray  +attachment  Q3_final.xlsx         [4]
        ▲
        └── GAP: 39 days with no communication between these custodians
```

* **Normalize to UTC, display with the original offset.** The Module 2 timezone discipline
  pays off exactly here.
* Every row carries a **citation**. No uncited rows, ever.
* **Gaps are findings.** A silence between two custodians who emailed daily is a lead.
* **Channel switches are findings.** Email → phone → Signal is a pattern with a name.
* Mark the **privileged** rows and exclude their content, but keep the fact of the
  communication where appropriate.

> A timeline with a gap in it is more interesting than a timeline without one. Build the
> tool to surface gaps, not just events.

Notes:

The gap-detection point is what elevates a timeline view from a feature to an analytic. Most
tools render events; few compute expected-communication baselines and flag the silences.
That is a differentiator a student could build in a week.

The privilege handling on timelines is subtle and worth naming: the existence and
participants of a communication with counsel are often loggable; the content is not.

---

## Near-Duplicates and Document Lineage

* **Near-duplicate detection** — shingling + MinHash / SimHash. Cheap, scales, explainable.
* What it gives an investigation:
  - **version lineage** — v1 → v7 of a contract, and **which clause changed between them**
  - the **clause that disappeared** in the version that got signed
  - the same memo circulated to different audiences with different numbers
* Group near-dupes and **diff them**; the diff is the finding, not the grouping

```text
  ND-0031  ├─ DOC-000204  "Draft 2026-02-02"   §7.3 cap: $2,000,000
           ├─ DOC-000288  "Draft 2026-02-19"   §7.3 cap: $2,000,000
           └─ DOC-000431  "EXECUTED"           §7.3 cap: REMOVED      ◀── the finding
```

> Nobody cares that two documents are 94% similar. Everybody cares about the 6%.

Notes:

That takeaway reframes near-dupe detection correctly. Vendors ship similarity scores;
investigators need the *diff*, rendered clause by clause. Build the diff view.

---

## Relationship Graphs — Useful, and Easy to Abuse

* Nodes = people and organizations; edges = communications, weighted by volume and recency
* Genuinely useful views:
  - **who talks to whom**, and how that changed around a key date
  - **brokers** — the person connecting two otherwise separate clusters
  - **after-hours and weekend** communication patterns
* The honest caution: a graph is **suggestive, not probative**. Volume is not intent,
  centrality is not guilt, and a pretty visualization is persuasive out of proportion to
  its evidentiary weight.

> A network diagram will convince a room of something it has not proved. Use it to decide
> **where to read**, not what to conclude.

Notes:

Say this one firmly. Link-analysis visuals are extraordinarily persuasive and that is
precisely the problem — an engineer who hands a jury-ready graph built on noisy entity
resolution has done harm. The professional use is triage: the graph tells you which 200
documents to read first.

---

## Lab 09 — Investigations: Entities, Threads, and a Timeline

Over the same corpus from Labs 02–04:

* Extract entities with a **hybrid** approach: gazetteer for known custodians, local LLM to
  a JSON schema for the rest — **every entity carries a source span**
* Resolve people into canonical identities; emit a **merge log** with evidence and confidence
* Rebuild email threads from headers; identify the **inclusive** set and the **dropped-Cc**
  branch
* Build a cited timeline; **detect gaps** against a per-pair communication baseline
* Group near-duplicates and **diff** a contract's versions — find the clause that vanished
* Find the **referenced-but-absent** documents (your collection leads)

**Deliverable:** `timeline.md` with a citation on every row, `entities.jsonl` with spans,
`merge_log.jsonl`, and a short list of collection leads.

Notes:

Budget 90 minutes. The planted findings in the synthetic corpus are: a 39-day gap, a removed
indemnity cap between contract versions, a dropped-Cc branch, and two references to a side
letter that is not in the corpus. Students who find all four have done the module.

---

## ▶ LAB BREAK — Lab 09

Debrief: **"What did you find that the keyword search in Lab 03 could never have found?"**

Notes:

The answer should be the gap and the missing side letter — neither is a document that
contains a keyword. That is the point of the module: investigative findings are often about
*absences*, and absences are structural queries, not search queries.
