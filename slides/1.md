# Module 2 — Legal Data Is Messy: Ingestion and Extraction

Elephant Scale

---

## The Unglamorous Module That Decides Everything

Nobody demos ingestion. Every legal-AI project dies there.

* Your RAG is only as good as your extracted text
* Your search is only as good as your OCR
* Your defensibility is only as good as your hashes and your chain of custody
* Your cost is mostly determined by what you chose **not** to process

> The AI layer is three hundred lines. The ingestion layer is the product.

Notes:

Say this bluntly. Engineers arrive wanting to build the model layer and treat ingestion as
plumbing to be delegated. In legal AI, ingestion *is* the differentiator — it is why FreeEed
exists, it is where the 1,400 file types live, and it is the part no LLM will do for you.

If you only land one slide in this module, land this one.

---

## What Actually Shows Up

A single mid-size matter, realistically:

| What | Why it hurts |
|---|---|
| **Email** — PST, OST, mbox, MSG, EML | Nested containers; threads; attachments inside attachments |
| **Office** — 20 years of .doc/.docx/.xls/.ppt | Tracked changes, comments, hidden columns, macros |
| **Scanned paper** — image-only PDF, TIFF | **Zero** extractable text until you OCR it |
| **Modern chat** — Slack, Teams exports | JSON blobs with no document boundary at all |
| **Media** — voicemail, recorded calls, video | Needs transcription before it is text |
| **Databases / exports** | CSV with 400 columns, 3 of which matter |
| **Load files** — `.dat`, `.opt` | The format the industry moves data in. Delimited by `\x14`. |
| **Encrypted / password-protected** | A real category, with a real workflow (ask, don't guess) |
| **Corrupt / truncated / zero-byte** | Must be *logged as an exception*, never silently dropped |

**1,400+ file types** is not marketing. It is Apache Tika's detector list, and you will
meet the long tail.

Notes:

Ask the room what the worst file they ever had to process was. You will get WordPerfect,
Lotus Notes NSF, AutoCAD, and at least one "a zip of zips of PSTs." Lotus Notes and JPST
are exactly why FreeEed has two jars that cannot come from Maven Central.

The last two rows are the ones that get engineers in trouble. A pipeline that drops
unparseable files silently has destroyed the completeness of the production.

---

## The Container Problem

```text
collection.zip
└── custodian_jdoe.pst
    └── Inbox
        └── "Re: Q3 numbers"  (message)
            ├── body text
            ├── Q3_final.xlsx           (attachment)
            └── forwarded.msg           (attachment, itself a message)
                └── scan_0042.pdf       (attachment, image-only)
                    └── [OCR needed]
```

* Legal data is **recursive**. You do not ingest files; you *walk a tree*.
* Every node needs: an **id**, a **parent**, a **custodian**, a **hash**, and a **path**
* **Family relationships matter legally** — an attachment is produced *with* its parent.
  Your schema needs a family group from the start, or you will rebuild it under deadline.

> Build the walker first and make it depth-unlimited. Then everything else is a
> handler registration.

Notes:

The family-group rule surprises engineers every time. If a parent email is responsive, the
attachments generally go out with it even if an attachment standing alone is not responsive.
That is a *schema* consequence, not a filter you bolt on later.

Point at the ASCII tree during Lab 01 — the generated corpus has exactly this shape,
including a message attached to a message and a scan attached to that.

---

## Extraction: Apache Tika Is the Answer

* One API, ~1,400 formats, returns **text + metadata**
* Battle-tested since 2007; it is what the industry actually runs
* Three ways to use it:

| Mode | How | Use when |
|---|---|---|
| **In-process (Java)** | `AutoDetectParser` | You're on the JVM (FreeEed's engine) |
| **Server** | `tika-server`, REST on `:9998` | Polyglot stack; isolates crashes |
| **tika-python** | wraps the server | Python pipelines (our labs) |

* **Run it as a server and treat it as hostile.** Parsers crash, hang, and occasionally
  blow the heap on a malformed file. One bad document should not take the run down.
  - timeout per document, retry once, then **log an exception row and move on**

> Never let a parser failure become a silent omission. An exception log *is* a
> defensibility artifact.

Notes:

The "treat it as hostile" line comes from real operational pain: a 400 MB spreadsheet with a
pathological formula graph will sit there consuming heap until something dies. Isolation and
per-document timeouts are not optional at volume.

In Lab 01 we provide stdlib extractors plus an optional Tika path, so nobody is blocked on
a Java install — but say clearly that production means Tika.

---

## OCR: Where the Case Is Usually Hiding

* An image-only PDF yields **zero** characters. To your search index it does not exist.
* Scanned paper is where the old contracts, the signed agreements, and the handwritten
  margin notes live — i.e. the interesting documents

* The decision ladder:
  1. Does the PDF already have a text layer? **Check first** — don't OCR what you can extract
  2. Is it image-only? **OCR it** — Tesseract, PaddleOCR, or a commercial engine
  3. Is it handwritten or terrible? **Flag it for a human.** Don't pretend.

* **OCR must be local if the documents are confidential.**
  - Otherwise you have a local LLM and a cloud OCR, and the raw document leaked one step
    earlier in the pipeline
  - This is the most common mistake in "private AI" architectures. Full stop.

> Your privacy posture is set by the **leakiest** stage, not the last one.

Notes:

That takeaway is the single highest-value sentence in the module, and it previews Module 5.
Teams spend weeks choosing a local LLM and then pipe every scan through a hosted
document-intelligence API. The document left the building at the OCR step and the LLM
decision was cosmetic.

OCR quality matters too: a 92%-accurate OCR pass means keyword search misses roughly one
hit in twelve. Say what you do about it — fuzzy search, and never claiming a negative on
OCR'd text without saying so.

---

## Metadata That Carries Legal Weight

Extracted text is half the job. These fields carry legal consequences:

* **Custodian** — whose data this is. Drives scope, cost, and interview order.
* **Sent / received / created / modified** — *and the timezone*. Chronologies live or die here.
* **From / To / Cc / Bcc** — Bcc is how privilege gets discussed and how it gets waived
* **Message-ID / In-Reply-To / References** — the only reliable way to rebuild a thread
* **Author / last-modified-by** — who actually wrote it, which is often not who sent it
* **Original path** — context no content model can recover (`\HR\Terminations\Smith\`)
* **MD5 / SHA-256 of the native file** — identity, dedupe, and chain of custody

> Timezone bugs are the most common cause of a wrong chronology — and a wrong chronology
> is how you reach a wrong conclusion about who knew what, when.

Notes:

Insist on storing timestamps as UTC plus the original offset, never as a normalized local
string. The day someone asks "did he know before the 3pm call?" you need the offset.

Bcc deserves a beat: "I'm bcc'ing counsel" is both the mechanism by which privilege is
asserted and, when a recipient replies-all, the mechanism by which it is blown.

---

## De-duplication Is a *Choice*, Not a Cleanup

Three levels, three different legal meanings:

| Level | Key | Meaning |
|---|---|---|
| **Exact** | SHA-256 of the native bytes | Same file. Safe to suppress. |
| **Global vs. per-custodian** | hash + scope | **A legal decision, not a technical one.** |
| **Near-duplicate** | shingles / MinHash similarity | Same document, edited. *Group, don't suppress.* |
| **Email thread** | `Message-ID` chain | Inclusive emails only. Big savings, real risk. |

* **Global dedupe** (one copy across all custodians) is cheapest — but it destroys the fact
  that *six people had this document*, which can be the point
* **Per-custodian dedupe** keeps possession, costs more
* **Near-dupes must be grouped and reviewed together.** v1 and v7 of a contract differ in
  exactly the clause that matters

> Dedupe decisions are **documented decisions**. Write down what you suppressed and why,
> because you will be asked.

Notes:

This is the slide where engineers realize legal processing is not data cleaning. The instinct
is "dedupe aggressively, it's free accuracy." In a matter, possession *is* evidence. Who had
the memo is frequently more probative than the memo.

Make them write the dedupe policy into the manifest in Lab 01. It is a one-line JSON field
and it is the difference between a choice and an accident.

---

## Load Files: The Industry's Interchange Format

```text
VOL001.dat  — delimited metadata, one row per document
  þ delimited by \x14 (ASCII 20), quoted with \xFE (ASCII 254)
  BEGBATES þ ENDBATES þ CUSTODIAN þ FROM þ TO þ SENT þ NATIVE_PATH þ TEXT_PATH

VOL001.opt  — Opticon page/image map, one row per PAGE
  IMG0000001,VOL001,\IMAGES\001\IMG0000001.tif,Y,,,3
  IMG0000002,VOL001,\IMAGES\001\IMG0000002.tif,,,,
         ^ page id   ^ volume  ^ relative path      ^ "Y" = new doc, ^ page count
```

* Yes, really: **`\x14` and `\xFE`** as delimiters, because commas and quotes appear in
  legal text
* Paths are **Windows-relative to the volume root**. Expect backslashes forever.
* Flavors differ by platform (Concordance, Relativity, Opticon). Build a reader, not a
  one-off regex.

> Load files are how your beautiful pipeline talks to the rest of the legal world.
> You will write a reader *and* a writer. Lab 01 writes the reader.

Notes:

Students find this slide funny, then they find it useful. The format is genuinely from the
1990s and genuinely still universal. A legal engineer who can read and emit clean load files
is immediately employable, which is worth saying out loud.

The `Y` flag in the `.opt` file marks the first page of a document — that is how you
reconstruct document boundaries from a flat page list.

---

## The Output: One Row Per Document

Everything downstream — search, RAG, review, production — reads **one catalog**:

```json
{
  "doc_id": "DOC-000417",
  "parent_id": "DOC-000416",
  "family_id": "FAM-000416",
  "custodian": "jdoe",
  "source_path": "collection.zip/custodian_jdoe.pst/Inbox/Re: Q3 numbers/scan_0042.pdf",
  "native_sha256": "8f2a...e91",
  "media_type": "application/pdf",
  "extracted_by": "tesseract-5.3.4",
  "text_sha256": "a01c...77b",
  "text_chars": 4812,
  "metadata": { "sent_utc": "2026-03-14T19:02:00Z", "tz_offset": "-05:00",
                "from": "j.doe@example.com", "to": ["a.ray@example.com"],
                "message_id": "<CA+9f...@mail>", "in_reply_to": "<CA+77...@mail>" },
  "dedupe": { "policy": "per-custodian", "status": "unique", "near_dupe_group": "ND-0031" },
  "exceptions": []
}
```

* **`extracted_by` matters.** The OCR engine version is part of your reproducibility story.
* `exceptions: []` is a promise. A non-empty list is a document somebody has to look at.

> One line per document, JSONL, hashed and append-only. Boring on purpose — boring is
> what survives an audit.

Notes:

Walk this record field by field; it is the schema for the next five labs. The two fields
engineers always omit are `extracted_by` and the `tz_offset`, and both come back to bite.

JSONL rather than a database for the lab is deliberate: students can `grep` their own
pipeline's output, which teaches faster than an ORM.

---

## Processing Exceptions Are a First-Class Output

* Encrypted / password-protected
* Corrupt or truncated
* Unsupported format
* Timed out
* OCR produced nothing (a blank scan — or a failure?)

For each: **document id, reason, what we tried, what a human should do.**

> "We processed 1,284,112 documents" is not a true statement unless you can also say
> what happened to the other 3,901.

Notes:

This is a slide about professional honesty that happens to also be about engineering. Vendors
quietly drop exceptions and report clean totals. A legal engineer reports both numbers,
because the exception list is the first thing a competent opposing expert asks for.

---

## Forensic Soundness: Three Hard Rules

1. **Never modify the source.** Read-only, always. Work on copies; keep the original hash.
2. **No outbound network calls during processing.** A parser that fetches a remote DTD or a
   linked image has altered the evidence and leaked its existence.
3. **Log everything, append-only.** What ran, what version, what it produced, how long.

* These are FreeEed's actual engine rules, not an abstraction
* Rule 2 is the one that surprises people — and it is why "just use a cloud parsing API" is
  not available to you

> Processing is a **measurement**, not a transformation. Measurements don't change the
> thing being measured.

Notes:

Rule 2 is worth dwelling on. Office formats can reference external resources; HTML and
email bodies are full of remote images. A parser that resolves them (a) tells a third party
that the document is being processed and when, and (b) pulls in content that was not in the
evidence. Both are real problems. Disable remote entity resolution explicitly.

---

## Lab 01 — Ingestion

Build the ingestion pipeline over a deliberately messy corpus:

* Walk the recursive container tree (zip → mbox → message → attachment → scan)
* Extract text by type; OCR the image-only scans
* Hash natives, apply a **documented** dedupe policy, group near-duplicates
* Parse the `.dat`/`.opt` load file and reconcile it against what you found
* Emit `catalog.jsonl` **and** `exceptions.jsonl` **and** a run manifest

**Deliverable:** a catalog every later lab reads, and an exception list you would be
willing to hand to opposing counsel.

> This is the lab people think is the warm-up. It is the one that gets them hired.

Notes:

Set the lab up by generating the corpus live on the projector — `python make_corpus.py` —
so they see the mess appear. Then let them loose.

Budget 60–75 minutes. The OCR step is where people stall; the shipped sidecar fallback keeps
anyone without Tesseract moving.

---

## ▶ LAB BREAK — Lab 01

Set up, then students run the lab. Debrief on return: compare document counts, then compare
**exception** counts. The counts will differ, and *why* they differ is the debrief.

Notes:

The count mismatch is the teaching moment. Students who dedupe globally get fewer documents.
Students who skip the nested `.msg` get fewer still. Put three students' numbers on the board
side by side and reconstruct the cause. That five-minute reconciliation teaches more about
eDiscovery than an hour of slides.
