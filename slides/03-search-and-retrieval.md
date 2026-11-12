# Module 3 — Search and Retrieval: The Foundation

Elephant Scale

---

## The Core eDiscovery Primitive

**Find anything inside everything.**

* Before AI, this *was* eDiscovery: keyword searches negotiated between counsel, run against
  an index, the hits reviewed by humans
* After AI, it is the **retrieval** half of every RAG system you will ever build
* Same index. Two customers: a paralegal typing a query, and a model asking for context.

> If your search is bad, your AI is bad. RAG does not fix retrieval — it **inherits** it.

Notes:

This is the slide that justifies spending a module on 1990s information retrieval in an AI
course. Engineers want to skip to embeddings. The uncomfortable truth is that BM25 keyword
search beats naive vector search on legal corpora more often than anyone expects, because
legal queries are full of proper nouns, Bates numbers, and defined terms — exactly what
lexical search is good at and embeddings blur.

---

## Two Customers, One Index

| | The human | The model |
|---|---|---|
| Query looks like | `("force majeure" OR pandemic) AND NOT draft` | a natural-language question |
| Wants | a **list** to review, with counts | the **top-k passages**, with provenance |
| Cares about | recall, and being able to explain the query | token budget, relevance, citability |
| Judges you on | "did we miss anything?" | "did it answer correctly?" |

* Build one index. Serve both. The needs differ in **ranking and payload**, not in storage.

> A search engine that cannot tell you *why* a document matched is useless to a lawyer and
> dangerous to a model.

Notes:

Make the point that the human's query is auditable and the model's is not. A negotiated
keyword list is a document both sides agreed to; "the vector store returned these five
chunks" is not. That asymmetry comes back in Module 6 as a transparency problem.

---

## The Inverted Index

```text
Documents                      Inverted index
  D1: "the merger closed"        merger  -> D1(1), D3(2)
  D2: "indemnify the buyer"      closed  -> D1(1)
  D3: "merger merger talks"      indemnify -> D2(1)
                                 buyer   -> D2(1)
                                 talks   -> D3(1)
```

* Term → **posting list** of (document, positions, frequency)
* This is Lucene. It is also Solr, Elasticsearch, SQLite FTS5, and Whoosh.
* Positions are what make **phrase** and **proximity** search possible
  - `"force majeure"~5` — within five words of each other, which is how lawyers actually
    think about a concept

> Three decades old, sub-millisecond, and completely explainable. Do not be too proud to
> use it.

Notes:

Lucene (2000) → Solr (2006) → Elasticsearch (2010) are the same core engine with different
clothes. FreeEed runs Lucene/Solr. Our lab uses SQLite FTS5 because it installs in zero
seconds and teaches the identical primitive — say that explicitly so nobody thinks FTS5 is
the production answer.

---

## Analysis: The Step That Decides Your Recall

The pipeline every term goes through, **at index time and query time — identically**:

```text
"Re: FORCE-MAJEURE clauses (Smith's)" 
  -> tokenize   -> [Re, FORCE, MAJEURE, clauses, Smith's]
  -> lowercase  -> [re, force, majeure, clauses, smith's]
  -> stopwords  -> [force, majeure, clauses, smith's]   ("re" dropped)
  -> stem       -> [forc, majeur, claus, smith]
```

* **Index-time and query-time analysis must match.** The classic bug: stemming one side only,
  then wondering why `clause` misses `clauses`.
* **Stemming is a trade**: better recall, worse precision, and it breaks on defined terms
* **Stopwords are a trap in legal text.** `"will"`, `"may"`, `"shall"`, `"no"` are stopwords
  in a web search engine and *load-bearing* in a contract

> In legal search, default analyzers lose cases. Ship a legal analyzer: keep `shall` and
> `may`, keep numbers, keep hyphenated terms whole.

Notes:

The `may`/`shall` point lands with anyone who has read a contract. "Lessee shall not" and
"Lessee may not" are different obligations, and a stock English analyzer throws both verbs
away.

The other one to mention: never stem the field you search for proper nouns and Bates
numbers. Index twice — one analyzed field, one keyword field.

---

## Relevance: BM25, In One Slide

A document scores higher when:

* The term appears **more often** in it — with diminishing returns (saturation)
* The term is **rare across the corpus** — IDF; `plaintiff` tells you nothing in a litigation
  corpus, `Hollerith` tells you everything
* The document is **shorter** — a hit in a 2-line email outweighs a hit in a 900-page manual

```text
score(q, D) = Σ  IDF(term) · ( tf · (k1+1) ) / ( tf + k1 · (1 - b + b · |D|/avgdl) )
              term∈q                 ^ saturation        ^ length normalization
```

* `k1` ≈ 1.2 (how fast term frequency saturates), `b` ≈ 0.75 (how much length matters)
* You will rarely tune these. You **will** be asked to explain a ranking — and now you can.

> BM25 is why "the document that mentions it twice in one page" beats "the manual that
> mentions it forty times in nine hundred."

Notes:

Don't teach the formula to be memorized — teach the three intuitions above it. Then point
out the practical consequence for legal work: length normalization systematically demotes
long documents, and long documents (contracts, policies, depositions) are often the
important ones. Mitigation: search at the *chunk* level too, which is exactly what Module 4
sets up.

---

## The Queries Lawyers Actually Run

* **Boolean with proximity** — `(fraud OR misrepresent*) W/10 (invoice OR billing)`
* **Phrase** — `"material adverse change"`
* **Wildcard / truncation** — `terminat*` catches terminate, terminated, termination
* **Field-scoped** — `custodian:jdoe AND sent:[2026-01-01 TO 2026-06-30]`
* **Negation** — `NOT draft`, which is how a reviewer excludes a whole sub-collection
* **Hit counts per term** — because the keyword list gets *negotiated*, and the negotiation
  is about how many documents each term drags in

> The deliverable is often not the documents. It is the **hit report**: term, document
> count, family count. That report is what the parties argue over.

Notes:

The hit-report point is new to almost every engineer in the room and is immediately useful.
Search-term negotiation is a real procedural step: one side proposes terms, the other side
runs them and says "that term alone returns 340,000 documents, it is overbroad." Your system
needs to produce that table on demand.

---

## Metadata and Date Filtering Carry the Load

* Date-range filtering is the **highest-leverage** filter in eDiscovery
  - the relevant period is usually negotiated and narrow
  - and it is where timezone bugs from Module 2 come due
* Custodian filtering drives cost and interview strategy
* **Family-aware results** — when a document hits, surface its family, not an orphan page
* File-type filtering — "no system files, no images under 10 KB"

```sql
-- the shape you actually run
SELECT d.doc_id, d.custodian, bm25(fts) AS score
  FROM fts JOIN catalog d USING (doc_id)
 WHERE fts MATCH '"material adverse change"'
   AND d.sent_utc BETWEEN '2026-01-01' AND '2026-06-30'
   AND d.custodian IN ('jdoe','aray')
 ORDER BY score LIMIT 50;
```

> Full-text relevance picks the order. **Metadata picks the universe.** Get the universe
> wrong and the ranking does not matter.

Notes:

Emphasize that the `WHERE` clause is where the legal scope lives — the date range and
custodian list come out of a negotiated protocol, not out of engineering judgment. Hard-code
nothing; make them parameters and log which values a given run used. That log line is a
defensibility artifact.

---

## Searching OCR'd Content: Expect to Miss

* OCR at 92% character accuracy ≈ a meaningful fraction of words contain at least one error
* Keyword search is **exact**. `Agreernent` is not `Agreement`.
* What you do about it:
  - **Fuzzy / edit-distance search** on OCR'd fields (`agreement~1`)
  - **Index the OCR confidence** and mark low-confidence documents
  - **Never report a clean negative on OCR'd text.** Say: *"no hits in extracted text;
    N documents are OCR'd with mean confidence 0.87 and may contain unmatched variants"*
  - Vector search genuinely helps here — an embedding of `Agreernent` still lands near
    `Agreement`, which is a real argument for hybrid retrieval

> "We searched and found nothing" is a claim about your index, not about the world.
> On OCR'd paper, say so.

Notes:

This is the most intellectually honest slide in the module and it tends to be the one people
quote back. The professional move is to disclose the limitation in the search report rather
than let it be discovered.

It also motivates Module 4: the first genuinely good reason for embeddings in this course is
robustness to OCR noise and vocabulary mismatch — not "AI magic."

---

## Hybrid Retrieval, Previewed

| | Lexical (BM25) | Vector (embeddings) |
|---|---|---|
| Finds | the exact words | the meaning |
| Great at | names, Bates numbers, defined terms, quotes | paraphrase, synonyms, OCR noise |
| Fails at | synonyms, misspellings, paraphrase | exact strings, negation, numbers |
| Explainable | **yes** — "matched these terms here" | not really |
| Cost | ~nothing | embedding the whole corpus |

* **Hybrid** = run both, fuse the ranks (Reciprocal Rank Fusion), then re-rank
* On legal corpora, hybrid beats either alone — reliably

> Keep the lexical index. It is cheap, exact, and it is the only half of your retrieval you
> can explain to a judge.

Notes:

RRF in one sentence: for each document, sum `1/(60 + rank)` across the result lists, sort
descending. Sixty is the conventional constant; it damps the influence of any single list's
top position.

Flag that we build the vector half in Lab 04 and fuse there. This slide is the promise.

---

## Scale: When FTS5 Stops Being Enough

| Corpus | Use | Why |
|---|---|---|
| < 1 M docs, single box | **SQLite FTS5** / Lucene embedded | Zero ops. Genuinely fine. |
| 1–50 M docs | **Solr** / OpenSearch, single node + replicas | Faceting, hit highlighting, ops tooling |
| 50 M+ / multi-matter | **Sharded** Solr/OpenSearch | Shard by matter, never by date |
| Any size, air-gapped | the same, **on-prem** | All of these run with no internet |

* Shard by **matter**: matters start, end, and get destroyed as units
* Budget the index at roughly **20–40% of extracted text size**; positions and highlighting
  are not free

> Everything on this slide runs on-prem with the network unplugged. That is not an accident
> — it is why the legal industry standardized on Lucene.

Notes:

The "shard by matter" rule has a legal driver worth naming: a matter's data has a retention
and destruction obligation. If a matter's documents are smeared across date-based shards,
"destroy everything for matter 7714" becomes a hard engineering problem instead of a drop.

---

## Lab 03 — eDiscovery Search

Index `catalog.jsonl` from Lab 02 and run real eDiscovery searches:

* Build a **dual-field** index: analyzed text + un-analyzed keyword field
* Run phrase, proximity, wildcard, and boolean queries
* Filter by custodian and negotiated date range; return **families**, not orphans
* Search *inside the OCR'd scans* — and find the hit the keyword list would have missed
* Produce a **hit report**: term → document count → family count

**Deliverable:** a hit report, and a search run log recording the exact queries and
filters used.

Notes:

Budget 45–60 minutes. The intended "aha" is the OCR'd document: there is a planted hit in a
scan whose OCR text has a character error, so the exact term misses and fuzzy finds it.
Students who report "no hits" have learned the lesson the hard way, which is the better way.

---

## ▶ LAB BREAK — Lab 03

Debrief question: **"Who reported zero hits for `indemnification`, and who found it in a
scan?"**

Notes:

Run that debrief as a show of hands before explaining. Then show the OCR text of the scan on
the projector with the mangled character highlighted. It is the most memorable thirty seconds
of Day 1.
