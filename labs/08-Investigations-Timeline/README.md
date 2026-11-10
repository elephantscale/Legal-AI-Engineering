# Lab 08 — Investigations: Entities, Threads, Timelines, Lineage

**Module 9 · optional Day 3**

Review asks what a document says. **Investigation asks what the documents, together,
imply** — including what is missing.

That difference changes the engineering. The four findings you are going to produce in
this lab share a property: **not one of them can be found by searching for a word.**

| finding | where it lives |
|---|---|
| a 39-day silence in a conversation that otherwise moves in hours | the *interval between* two documents |
| an indemnification cap that vanished between draft and execution | the *diff* of two near-duplicates |
| a recipient dropped from a thread, right before a sensitive line | the *change* in a header |
| a side letter referenced twice and present nowhere | an *absence* |

Search finds documents containing a term. These are structural queries over the catalog.
A keyword index cannot express any of them.

**Deliverables:** `entities.jsonl` (with spans), `merge_log.jsonl`, `threads.jsonl`,
`dropped_recipients.jsonl`, `timeline.md`, `lineage_findings.jsonl`,
`collection_leads.jsonl`.

---

## Setup

```bash
cd labs/08-Investigations-Timeline
```

Nothing to install. This lab reads Lab 01's `catalog.jsonl` and text store, and Lab 05's
`decisions.jsonl` for one of the timeline scopes. Everything runs offline.

---

## Part 1 — Entities that point at something

```bash
python3 investigate.py entities --work ../work
```

```
  gazetteer : 16 known surfaces from headers and custodians
  entities  : 4819 with verified spans
      PERSON     2424
      EMAIL      2367
      ORG          15
      MONEY         7
      CLAUSE        3
      DATE          3
  by source : gazetteer=4791, pattern=28
  by locator: body=85, headers=4734
  low confidence (<0.6): 46 — bare first names and address local-parts
```

Three design decisions in that output are worth more than the counts.

**Every entity carries a locator.** Each row has `doc_id`, `field`, `start`, `end`.
`field: "body"` indexes `text/<doc_id>.txt`; `field: "metadata.cc"` indexes that header
value in `catalog.jsonl`. Pick a row at random and resolve it by hand:

```bash
python3 -c "
import json
r = json.loads(open('../work/entities.jsonl').readline())
print(r)
t = open(f'../work/text/{r[\"doc_id\"]}.txt').read() if r['field']=='body' else ''
print(repr(t[r['start']:r['end']]))"
```

> An entity you cannot point at is a claim. An entity with a resolvable span is evidence.
> That is the whole difference, and it costs two integers.

**The hybrid is not a hedge.** The gazetteer — custodians, party names, counsel of record
— is deterministic and gets the entities whose misidentification is most expensive. The
model gets the long tail. In a real matter you *always* have the gazetteer; building an
entity pipeline that ignores it in favour of a model is a choice to be worse at the
important half.

**Confidence tracks ambiguity honestly.** `Anita Ray` in a header scores 1.0. A bare
`Anita` in running text scores 0.55, because it genuinely might be someone else. 46 rows
are below 0.6 and they are all bare first names and address local-parts.

Now add the model (skip if you have no Ollama — nothing below depends on it):

```bash
python3 investigate.py entities --work ../work --llm --limit 40
```

Read `extract_llm()` before you run it. The model's output is **verified back against the
document**: if the returned surface string cannot be found in the text, the entity is
dropped. A model that returns `Hollerith Inc.` for `Hollerith Industries, Inc.` has
normalized, which is helpful in a chatbot and disqualifying in evidence.

---

## Part 2 — Resolution, and why it needs a log

```bash
python3 investigate.py resolve --work ../work
```

```
  canonical identities : 5
  entity rows resolved : 4743
  merges logged        : 5  (0 same-address, 5 heuristic)
```

Open `merge_log.jsonl`:

```json
{"canonical": "Mei Chen", "merged": "M. Chen", "confidence": 0.60,
 "evidence": "initial + surname pattern only; no address co-occurrence",
 "basis": "heuristic", "reviewed_by": null}
```

Entity resolution is where investigation tooling quietly becomes an ethics problem.
Merging `M. Chen` into `Mei Chen` is probably right. Merging two different people who
share a surname **puts words in someone's mouth** — and because the merge is invisible
downstream, nobody ever checks it. A finding built on a bad merge is a finding about a
person who did not say the thing.

So: no merge without recorded evidence, two `basis` values with different confidence, and
a `reviewed_by` field that **starts null and stays null until a human clears it**. The
merge log ships with the findings.

This corpus has consistent display names, so you get 0 same-address merges and 5
heuristic ones. A real corpus inverts that ratio — same-address merges arrive in the
hundreds and are nearly all correct. The heuristic ones are the whole risk, which is why
they are the ones carrying 0.60.

---

## Part 3 — Threads, and the recipient who disappeared

```bash
python3 investigate.py threads --work ../work
```

```
  threads   : 1171  messages 1175
  of those  : 3 thread(s) with more than one message (7 messages)
  inclusive : 1173 of 1175 overall (100%)
              5 of 7 (71%) within the multi-message threads

  deepest threads:
      3 msgs (2 inclusive)  Q3 numbers look off
      2 msgs (2 inclusive)  MSA draft 2 — indemnification cap
      2 msgs (1 inclusive)  PRIVILEGED AND CONFIDENTIAL — Q3 acceptance language

  dropped-Cc events : 2
      DOC-000652  2026-02-02T16:40:00Z  lost m.chen@hollerith-industries.example
          subject: Re: Q3 numbers look off
```

**On the inclusive set, be honest.** An inclusive message is one whose participant set is
not a subset of a later message in the same thread; reading only those covers all the
text of the conversation. On a real custodian mailbox that removes 30–50% of the reading.
On *this* corpus it removes almost nothing, because the filler is single-message threads.
You are checking the mechanism today, not the saving — and the tool prints that caveat
itself rather than letting a flattering percentage stand.

And the defensibility catch: non-inclusive messages still have **distinct metadata and
distinct attachments**. Suppress them from *reading*. Never suppress them from the
catalog, and never produce as though they did not exist.

**The dropped Cc is the finding.** `m.chen` was on the thread and is not on the reply.
Read the reply's body — that is where "let's discuss offline" lives.

> A conversation that narrows is a conversation somebody wanted narrowed. The engineering
> is a set difference on two header fields. The finding is a motive.

---

## Part 4 — The timeline, and the gap

Try it wrong first, deliberately:

```bash
python3 investigate.py timeline --work ../work --pair aray,jdoe
```

```
  rows      : 180   median interval 0.5 days
  gaps      : 0
```

180 rows, no gaps. The two custodians emailed about *something* nearly every day, so
there is no silence anywhere. **A chronology of a mailbox is not a chronology, it is a
mailbox.** An investigator builds the timeline of an *issue*.

Scope it to the conversation:

```bash
python3 investigate.py timeline --work ../work --thread "Q3 numbers look off"
```

```
  scope     : thread matching 'Q3 numbers look off' (3 messages)
  rows      : 3   median interval 19.7 days
  gaps      : 1  (each judged against a leave-one-out baseline, floor 7 days)
        39.3 days  2026-02-02 -> 2026-03-14  (baseline 0.1, threshold 7.0)
               resumes with: Re: Q3 numbers look off
```

There it is. Two messages an hour apart, then **39 days of silence**, then the thread
resumes — and the resuming message is the one that references a side letter nobody has.

Two things made that visible, and both are in the code:

**The baseline is per-scope.** "39 days" means nothing until you know this conversation
otherwise moves in 0.1 days. A global baseline would have buried it.

**The baseline is leave-one-out.** Read `is_gap()`. In a three-message thread that ran for
an hour and then went quiet for 39 days, *the 39 days is the median* — so scoring each
interval against a baseline that includes it reports nothing at all. Each interval is
judged against the median of the others. This is the bug that hides the finding, and it
is an easy one to ship.

Other scopes worth trying:

```bash
python3 investigate.py timeline --work ../work --responsive
python3 investigate.py timeline --work ../work --terms "indemnification,side letter"
```

`timeline.md` states its scope at the top and cites a `doc_id` on every row.

> A gap is a question, not a conclusion. It has three innocent explanations — they moved
> to phone, the custodian was on leave, the collection is incomplete — and one that is
> not. Which it is, is a collection question you ask next, not an inference you publish.

---

## Part 5 — Lineage: the clause that vanished

```bash
python3 investigate.py diff --work ../work                 # list the groups
python3 investigate.py diff --work ../work --group ND-0001
```

```
  group ND-0001: 6 documents, 3 distinct text(s)
    DOC-000003  .../Contracts/MSA_draft1.txt
    DOC-000004  .../Contracts/MSA_draft2.txt
        (3 identical copies, held by aray, bsingh)
    DOC-000002  .../Contracts/MSA_EXECUTED.txt
        (2 identical copies, held by aray, bsingh)

  --- DOC-000004 -> DOC-000002 (4 removed, 2 added)
      - 7.3 INDEMNIFICATION CAP. Notwithstanding anything to the contrary, the
      - aggregate indemnification obligation of either Party shall not exceed
      - $2,000,000 in the aggregate.
      + 7.3 [INTENTIONALLY OMITTED]

  substantive removals: 2
      DOC-000004 -> DOC-000002  7.3
      DOC-000004 -> DOC-000002  $2,000,000
```

A $2,000,000 liability cap was in Draft 2 and is not in the signed contract. Nobody wrote
an email saying "we removed the cap" — the email says *"strike the 7.3 cap from the
execution copy"*, and you only know what that cost once you have the diff.

Two details in `cmd_diff` matter:

- **Exact text duplicates are collapsed first.** A near-dupe group spans custodians, so
  path-sorted members produce a meaningless `A → B → A` chain. One row per distinct text,
  each listing who held it — which also preserves the possession fact that Lab 01's
  per-custodian dedupe exists to protect.
- **The clause pattern catches bare numbering.** Contracts write `7.3 INDEMNIFICATION
  CAP.`, not `§7.3`. A regex requiring the `§` sigil looks reasonable in review and
  silently misses the clause you were hired to find.

> This is Lab 01's threshold decision cashing out. At a near-dupe threshold of 0.80 the
> executed contract lands in a *different group* from its own drafts, this diff never
> happens, and the removed cap is never found.

---

## Part 6 — Collection leads: the finding that is an absence

```bash
python3 investigate.py leads --work ../work
```

```
  named-document references found : 2
  referenced but ABSENT            : 2

    'side letter' — 3 mention(s)
        DOC-000330 (bsingh, 2026-02-24): …Per the side letter, strike the 7.3 cap from
                                          the execution copy…
    'redline' — 2 mention(s)

  plus 1 row(s) from the producer's LOAD FILE with no native:
    HOLL0000010–HOLL0000011  /NATIVE/001/side_letter.pdf  (custodian jdoe)
```

The side letter is referenced three times in documents you have, listed in the producer's
own load file, and present nowhere in the collection.

> Two independent routes to the same lead — the text says it exists, and the producer's
> load file lists it — is the strongest form of this finding. One route is a question.
> Two is a letter to opposing counsel.

`collection_leads.jsonl` carries, per lead: the phrase, the mention count, quoted context
with character spans, and a `next_step`. That is a letter someone can send without doing
the work again.

---

## Exercises

1. **Add a relationship edge list.** From `threads.jsonl`, emit `(person_a, person_b,
   message_count, first, last)` for canonical identities. Then answer, honestly: what
   would a reader wrongly conclude from a thick edge? (Hint: a distribution list.)
2. **Break the leave-one-out baseline.** Construct a scope where it reports a gap that is
   not interesting. Then say in one sentence what scope would have been right.
3. **Widen the lead detector.** `NAMED_DOC_RE` catches a fixed vocabulary. Find a
   reference it misses, and decide whether to extend the pattern or to use the model —
   and what verification the model's answer would need.
4. **Entity precision.** Sample 20 rows with `confidence < 0.6` and resolve each span by
   hand. Report precision with a Wilson interval using `common/metrics.py`. You now have
   a measured entity layer instead of an assumed one.

---

## Review Questions

1. Which of this lab's four findings could a keyword search have found? Why not?
2. Your merge log has 300 same-address merges and 12 heuristic ones. Which do you hand to
   a reviewer, and why that one?
3. You report a 39-day gap. Opposing counsel says the custodian was on parental leave.
   What do you say, and what do you *not* say?
4. You suppress non-inclusive emails from review. Opposing counsel asks for a document
   count. What is the honest answer?
5. Why does an entity need a character offset rather than just a document id?

---

## Teacher's Playbook

### What good looks like

A student who gets this lab produces all four findings and, asked how they found each one,
describes a *structural* query rather than a search. The strongest tell is Part 4: they
should run the unscoped timeline, see 180 rows and no gaps, and diagnose the scope problem
themselves before reading ahead.

### Live-demo script (about 15 minutes)

1. **The locator** (2 min). Run `entities`, then resolve one span by hand on the projector
   with the one-liner above. *"Two integers is the difference between a claim and
   evidence."*
2. **The merge log** (2 min). Open it, point at `"reviewed_by": null`. *"This field is
   empty on purpose and it stays empty until a person looks. Who here would sign a finding
   that rests on a 0.60 merge?"*
3. **The dropped Cc** (3 min). Run `threads`. Put `DOC-000652` on screen, then open its
   body and read *"let's discuss offline"* aloud, out of the body, after showing that
   `m.chen` was removed from the Cc line of that same message. Let the room react. It is a
   set difference on two header fields.
4. **The scope failure** (4 min). This is the beat of the module. Run
   `timeline --pair aray,jdoe` → **180 rows, 0 gaps**. Ask: *"is there a gap in this
   collection?"* Let someone say no. Then run `--thread "Q3 numbers look off"` →
   **39.3 days**. *"Same data. Same code. The scope was the finding."* Then open
   `is_gap()` and show that a naive median would have reported nothing even with the right
   scope.
5. **The diff** (3 min). `diff --group ND-0001`. Read the removed clause. Then callback:
   *"Lab 01, Tuesday. A threshold of 0.80 and we never see this."*
6. **The absence** (2 min). `leads`. Two routes to the side letter. *"This is the only
   output of your whole system that is a document you do not have."*

### Common mistakes and fixes

| symptom | cause | fix |
|---|---|---|
| `no catalog at …` | Lab 01 not run | run `ingest_reference.py` first |
| ~39 entities only | body-only extraction; headers ignored | the headers are where the people are — `extract_headers()` |
| every `Anita` at confidence 1.0 | gazetteer with no ambiguity model | bare first names get 0.55, and say why |
| `Ray` matching inside `Rayburn` | substring match | word-boundary regex; a substring match invents people |
| `--thread` finds nothing | subject fragment wrong | run `threads` and copy from the deepest-threads list |
| timeline reports no gap with the right scope | threshold includes the gap in its own baseline | leave-one-out |
| `references` crash | the header is a list in the catalog, not a string | normalize at the single point headers enter |
| diff shows `A → B → A` | exact duplicates across custodians not collapsed | dedupe by `text_sha256` first |

### Debrief question (the one the deck names)

**"What did you find that the keyword search in Lab 02 could never have found?"**

The answer you want is the **gap** and the **missing side letter**. Neither is a document
containing a term — one is an interval, the other is nothing at all. Investigative
findings are frequently about absences, and absences are structural queries.

If a student answers "the removed cap," push once: a keyword search for `indemnification`
*does* return all three MSA versions. What it does not do is tell you they differ, or how.
The finding is in the comparison, not the retrieval. That is a good answer too, just a
different one.

### Further debrief

1. **"The dropped Cc — is that evidence of concealment?"** No. It is evidence that a
   recipient was removed, and a reason to read what was said next. The engineer's job ends
   at the structural fact plus the citation; characterizing intent is counsel's job and
   getting that boundary wrong is how a technical expert gets discredited.

2. **"Your entity layer has no measured precision. Can you use it?"** For generating
   leads, yes — a false entity costs a wasted look. For a finding or a production
   decision, no, not until you have sampled it. Exercise 4 is the fix and it takes twenty
   minutes.

3. **"Relationship graphs look impressive. What is the risk?"** A thick edge between two
   people may be a distribution list, a calendar bot, or one person on everything. Graphs
   invite inference from visual weight, and visual weight is not evidence. If you ship a
   graph, ship the edge list with counts and date ranges next to it.

### Timing

90 minutes. Parts 1–3 in 35, Part 4 in 20 (it is the valuable one — do not rush the
scope failure), Parts 5–6 in 20, debrief in 15.

---

**Next:** [Lab 09 — Agentic Legal Workflow](../09-Agentic-Legal-Workflow/README.md)
