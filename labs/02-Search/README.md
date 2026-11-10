# Lab 02 — eDiscovery Search: Find Anything Inside Everything

**Module:** 3 — Search and Retrieval
**Duration:** 45–60 minutes
**Difficulty:** Intermediate

---

## Goal

Index Lab 01's catalog and run the searches lawyers actually run — phrase, proximity,
wildcard, boolean, fuzzy, with custodian and date filters and family-aware results — then
produce the **hit report** that gets negotiated between counsel.

And discover, the hard way, that *"we searched and found nothing"* is a claim about your
index, not about the world.

## Files in this lab

```
02-Search/
  README.md          <- you are here
  requirements.txt   <- nothing to install
  search_index.py    <- build / search / hitreport. Complete and runnable.
  terms.txt          <- a proposed search-term list, the kind that gets negotiated
```

## Prerequisites

- Lab 01 complete: `../work/catalog.jsonl` and `../work/text/` exist
- Python 3.11+ with SQLite FTS5 (it ships with CPython; `requirements.txt` has the check)

Short on time? `python3 ../01-Ingestion/ingest_reference.py --corpus ../assets/corpus --out ../work`

## Steps

### 1. Build the index

```sh
python3 search_index.py build --work ../work
```

Read the output. Note `index_overhead` — the index is a real fraction of the text it
indexes, and that fraction is what you budget disk for (Module 3).

### 2. Read the analyzer before you run a single query

Open `search_index.py` and find `analyze()` and `STOPWORDS`. Two things matter:

- **One function**, called at index time *and* query time. The classic legal-search bug is
  stemming one side only, then wondering why `clause` misses `clauses`.
- **`LEGAL_KEEP`** — `shall`, `may`, `must`, `not`, `without`, `unless`. A stock English
  stopword list throws all of those away. *"Lessee shall not"* and *"Lessee may not"* are
  different obligations, and a default analyzer cannot tell them apart.

Try it: `python3 -c "import search_index as s; print(s.analyze('Lessee shall not terminate the Agreements'))"`

### 3. Run the queries lawyers run

```sh
python3 search_index.py search --work ../work -q '"discuss offline"'
python3 search_index.py search --work ../work -q 'acceptance W/10 certificate'
python3 search_index.py search --work ../work -q 'terminat*'
python3 search_index.py search --work ../work -q 'restatement AND auditor'
python3 search_index.py search --work ../work -q '"material adverse change"'
```

The last one returns zero. **Zero is an answer, and it needs a caveat** — look at the
OCR note the tool prints under every result.

### 4. Filter by the negotiated scope

```sh
python3 search_index.py search --work ../work -q restatement \
    --custodian jdoe,aray --from 2026-02-01 --to 2026-06-30
```

Full-text relevance picks the *order*. **Metadata picks the universe.** The custodian list
and the date range come out of a negotiated protocol — so they are parameters that get
logged, never constants in your code.

### 5. The OCR exercise — this is the lab

Run the same query three ways and compare the counts.

```sh
# A. the producer's OCR (what you were given)
python3 ../01-Ingestion/ingest_reference.py --corpus ../assets/corpus --out ../work-sidecar
python3 search_index.py build  --work ../work-sidecar
python3 search_index.py search --work ../work-sidecar -q 'indemnification'
python3 search_index.py search --work ../work-sidecar -q 'indemnification' --fuzzy
python3 search_index.py search --work ../work-sidecar -q 'indemnif*'

# B. your own local OCR
python3 ../01-Ingestion/ingest_reference.py --corpus ../assets/corpus --out ../work-reocr --reocr
python3 search_index.py build  --work ../work-reocr
python3 search_index.py search --work ../work-reocr -q 'indemnification'
```

You will get **three different hit counts for the same question.** Find out why:

```sh
grep -o 'indemnif[a-z0-9]*' ../work-sidecar/text/*.txt | sort -u
```

Then answer, in writing: *which count do you report, and what do you disclose alongside it?*

### 6. Produce the hit report

```sh
python3 search_index.py hitreport --work ../work --terms terms.txt
```

Look at the top row. One proposed term pulls far more documents than any other, and it is
not a term about the case. That table is what counsel argues over — a term that drags in
thousands of irrelevant documents is "overbroad" and gets narrowed or dropped.

Now edit `terms.txt`: propose a narrower version of the overbroad term and re-run.

### 7. Keep a search log

```sh
python3 search_index.py search --work ../work -q '"indemnification cap"' --json \
    >> ../work/search-log.jsonl
```

Every run records the query, the translated FTS expression, and the filters. That file is
a defensibility artifact: it is how you answer *"what exactly did you search for?"* six
months from now.

## Deliverable

1. `../work/hit-report.json` — term → document count → family count
2. `../work/search-log.jsonl` — the exact queries and filters you ran
3. Your three `indemnification` counts, with one written sentence on which you would
   report and what caveat goes with it

## Troubleshooting

- **`no catalog at ../work/catalog.jsonl`** — Lab 01 first, or run its reference.
- **`fts5: syntax error near ...`** — FTS5 is strict. Quote phrases; `AND OR NOT NEAR`
  must be uppercase. Run with `--json` to see the translated expression.
- **A phrase search returns nothing but the words are clearly there** — phrase search runs
  against the *keyword* field (unanalyzed). If the document says "Material Adverse Change"
  with different spacing or a line break, the phrase does not match. That is correct
  behavior and it is why hit reports include single terms as well as phrases.
- **Wildcards only work at the end** — `terminat*` yes, `*mination` no. Suffix matching
  needs a reversed index. Say so rather than promising it.
- **Everything matches `parking`** — yes. Look at the corpus. That is what an overbroad
  term looks like, and it is the point of step 6.
- **Zero results and you expected some** — check your date filter first. Documents with no
  `sent_utc` (loose files, attachments) are deliberately *kept* by the filter rather than
  excluded; if you change that, say so in the log.

## Review Questions

1. Why does the analyzer keep `shall` and `may` when every standard stopword list drops
   them?
2. You report "no hits for `material adverse change`." What must you say in the same
   sentence?
3. Why does a hit report need a family count as well as a document count?
4. BM25 rewards shorter documents. Why is that a problem in a corpus full of contracts and
   depositions, and what do you do about it?
5. Your index has 4 OCR'd documents today and 400,000 next month. What changes about how
   you report a negative search result?

---

## Teacher's Playbook

### Worked model answer

On the default corpus:

| Run | Query | Hits | Families | Scan found? |
|---|---|---|---|---|
| producer OCR | `indemnification` | **22** | 20 | **no** |
| producer OCR | `indemnif*` | 23 | 21 | yes |
| producer OCR | `indemnification --fuzzy` | 23 | 21 | yes |
| local re-OCR | `indemnification` | **25** | 23 | yes |

The producer's OCR sidecar for `scan_0042.png` reads **`indemnif1cation`** — a `1` where
the `l` should be. Exact keyword search cannot match it. Local tesseract reads it
correctly, which is why the re-OCR run finds three more documents.

Hit report, top rows: `parking` 144 documents (overbroad, and about nothing),
`indemnif*` 23 / 21 families, `indemnification` 22 / 20, `"side letter"` 3 / 3,
`"material adverse change"` 0 / 0.

### Live-demo script (about 10 minutes)

1. `python3 -c "import search_index as s; print(s.analyze('Lessee shall not terminate'))"`
   — show `shall` and `not` surviving. *"A default analyzer just deleted the obligation."*
2. Run `-q 'indemnification'` against the sidecar index: **22 hits**. Then `--fuzzy`:
   **23**. Then the re-OCR index: **25**.
   Ask the room: *"Which of those three numbers is the truth?"* Let them argue.
   Then: `grep -o 'indemnif[a-z0-9]*' ../work-sidecar/text/*.txt | sort -u` and put
   `indemnif1cation` on the screen. **This is the thirty seconds students remember from
   Day 1.**
3. Run the hit report. Point at `parking` on top — 144 documents, every one of them
   about a parking garage. *"This is what an overbroad term looks like. Now imagine
   billing review hours for all 144, at a per-document rate."*
4. Run a search with `--custodian` and a date range. *"The WHERE clause is where the legal
   scope lives. Those are negotiated values. Log which ones you used."*

### Common mistakes + fixes

- **Stemming the query but not the index** (or the reverse). The starter prevents it with
  one shared `analyze()`; make them notice *why* it is one function.
- **Treating a zero-hit result as proof of absence.** This is the professional failure the
  lab is built around. The tool prints the OCR caveat on every search; make them read it
  out loud once.
- **Reporting only document counts.** Families are what get reviewed and produced. A
  10-document hit across 9 families is a different cost than 10 hits in one family.
- **Hard-coding the date range.** It comes from the protocol and changes between matters.
- **Assuming fuzzy means edit distance.** It does not here — FTS5 has no edit-distance
  operator, and the tool prints exactly what it ran instead. Honesty about your own
  method is the habit being taught.
- **Reaching for embeddings immediately.** They come in Lab 03, and lexical search will
  still beat them on Bates numbers and defined terms. Both, fused — not one.

### Debrief Q&A

- *Why not Solr?* Production should be (FreeEed is). FTS5 is the same inverted index with
  the same BM25, installs instantly, and keeps the lab unblocked. Offer the Solr docker
  one-liner in `requirements.txt` to anyone who wants to compare.
- *Is the crude stemmer a cop-out?* It is a deliberate choice: you can read it, so you can
  predict it. A black-box stemmer that mangles defined terms is worse than a simple one
  you understand. Show the `len(word) < 5` guard that protects short defined terms.
- *How do I search inside 400,000 scans?* Index the OCR confidence, flag low-confidence
  documents, and run hybrid retrieval. Which is Lab 03.
- *Who decides the search terms?* Counsel, negotiated with the other side. You run them
  and report the counts honestly — including the ones that make your side's list look
  overbroad.

### What good looks like

A student can explain why `shall` survives the analyzer; has three different hit counts
for `indemnification` and a written sentence about which one they would report and what
they would disclose; produced a hit report with both document and family counts; and
narrowed an overbroad term and re-ran it.

The sentence you are listening for at debrief: *"no hits in extracted text; N documents
are OCR'd and may contain unmatched variants."*

---
