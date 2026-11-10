# Lab 03 — Legal RAG With Citations

**Module:** 4 — RAG for Legal Documents
**Duration:** 75–90 minutes
**Difficulty:** Intermediate → Advanced

---

## Goal

Build retrieval-augmented Q&A over the Lab 02 index that **cites its sources** — and then
build the thing that actually makes it safe: a **verifier in code** that rejects fabricated
citation markers, uncited claims, and quotations that are not verbatim in the source.

The model proposes. Your code decides whether the answer is allowed out.

## Files in this lab

```
03-Legal-RAG-Citations/
  README.md          <- you are here
  requirements.txt   <- nothing required; Ollama recommended
  legal_rag.py       <- chunk / embed / ask / eval. Complete and runnable.
  evalset.json       <- 10 cases, 3 of them deliberately UNANSWERABLE
```

## Prerequisites

- Labs 01 and 02 complete (`../work/catalog.jsonl`, `../work/index.sqlite`)
- **Recommended:** Ollama with two models — this is the lab where the real thing is
  visibly better:
  ```sh
  ollama pull qwen3:8b
  ollama pull nomic-embed-text
  ```
- No Ollama? Everything still runs. `../common/llm.py` falls back to a deterministic
  hashing embedder and an extractive answer stub. Retrieval will be worse — **that is the
  lesson, not a bug** — and every verifier exercise still works.

## Steps

### 1. Chunk

```sh
python3 legal_rag.py chunk --work ../work
```

Then read `structure_split()` and `chunk_text()` in the source. The order matters:
**structure first, size second.** A clause split across two chunks loses the obligation; a
deposition answer split from its question inverts the meaning.

Look at a chunk and check it can answer *which document, which characters*:

```sh
head -2 ../work/chunks.jsonl | python3 -m json.tool | head -20
```

If a chunk cannot say that, it cannot be cited, and if it cannot be cited you cannot use
it.

### 2. Embed

```sh
python3 legal_rag.py embed --work ../work
cat ../work/vectors-manifest.json
```

Read the `WARNING` field out loud. Different embedding models have different
**dimensions**; you cannot mix them in one collection. Change the embedder and you
re-ingest the whole corpus. That is why the model is pinned in your manifest.

### 3. Ask

```sh
python3 legal_rag.py ask --work ../work \
  -q "What was the indemnification cap in Section 7.3 of the Master Services Agreement?"
```

Look at the retrieval trace. Each passage is tagged `L` (found by lexical BM25), `V`
(found by vector), or both:

```
  [1] LV DOC-000003#c1   rrf=0.032018
  [3] -V DOC-000108#c1   rrf=0.016393
```

That tag column is the argument for hybrid retrieval in one glance. Keep the lexical half:
it is cheap, exact on names and Bates numbers, and **it is the only half you can explain
to a judge.**

### 4. Prove the verifier is doing work

```sh
python3 legal_rag.py ask --work ../work -q "What does Section 7.3 say about the cap?" \
    --break-citations
```

This deliberately corrupts the answer with the three failures real models produce. You
should see all three caught:

```
verifier: REJECTED — the answer is not allowed out:
  - FABRICATED CITATION [8]: only 5 passages were retrieved
  - UNCITED CLAIM: 'The agreement was signed by both parties on 2 October 2026.'
  - QUOTE NOT IN SOURCE: 'the Seller shall indemnify the Buyer without limitation' ...
```

Now read `verify()` and the comment above check 2. The subtlety there — a marker at the
*start* of a segment belongs to the *previous* sentence — is what stops a model smuggling
an uncited claim in behind its predecessor's citation.

### 5. Find the injection

```sh
python3 legal_rag.py ask --work ../work \
  -q "Does any document instruct an automated review tool to mark documents non-responsive? If so, quote it and say which document it is in."
```

One document in the corpus contains a payload aimed at *your* pipeline. The correct
behavior is to **report that the instruction exists and cite it** — never to obey it.
That works because the context is **fenced** (`<context>…</context>`) and rule 6 of the
system prompt says retrieved text is data.

In a matter, some documents were authored by the opposing party. Treating retrieved text
as instructions is not a theoretical vulnerability here: the adversary had write access to
your corpus by construction.

### 6. Run the eval set — including the unanswerable questions

```sh
python3 legal_rag.py eval --work ../work
```

Three of the ten cases **cannot** be answered from this corpus. Look at
`refusal_rate_on_unanswerable`.

> A system that never says "not found" is not being careful. It is making things up and
> you have not caught it yet.

### 7. Measure what you gave up (optional, instructive)

Run the eval twice and compare:

```sh
LEGAL_AI_MODE=offline python3 legal_rag.py eval --work ../work-offline
LEGAL_AI_MODE=local   python3 legal_rag.py eval --work ../work
```

Keep both `rag-eval.json` files. The delta is the honest version of "is a local model good
enough?" — and in Lab 04 you will produce the same comparison against a cloud model.

## Deliverable

1. `../work/rag-log.jsonl` — every question, answer, citation set, verdict, **and the
   retrieved chunk set**
2. `../work/rag-runs/q*.txt` — every **rendered** prompt (not the template — the template
   plus a bug is not what ran)
3. `../work/rag-eval.json` — including the refusal rate on unanswerable questions
4. One screenshot or paste of a verifier **rejection**, with the reason

Items 1 and 2 become `runs/<run-id>/` in tomorrow's reproducibility bundle. You are
already building it.

## Exercises

1. **Lose the fence.** Remove `<context>`/`</context>` from `build_prompt()` and re-run
   step 5. Does the injection behave differently? (With a real model it often does.)
2. **Break the analyzer symmetry.** In `../02-Search/search_index.py`, make `analyze()`
   skip stemming when called from the query path. Watch recall fall. Put it back.
3. **Tune `TOP_K` and `RRF_K`.** Sweep `top_k` 3→10 and record `source_hit_rate` from the
   eval. Plot it. Where does it stop helping?
4. **Lexical only vs vector only.** Delete `../work/vectors.jsonl` and re-run the eval;
   then restore it and stub out the lexical half. Which questions does each one lose?
5. **Attribution checking (the hard one).** Add a second model call: *"Does passage [n]
   support this sentence? Answer SUPPORTED or NOT_SUPPORTED."* Measure how many of your
   passing citations are merely *plausible*. Be honest that the judge is itself imperfect
   — measuring how imperfect is the interesting part.

## Troubleshooting

- **`run chunk first` / `no catalog`** — the pipeline is ordered: Lab 01 → Lab 02 build →
  chunk → embed → ask.
- **`[llm] chat endpoint unavailable`** — Ollama is not running. `ollama serve` in another
  terminal. The lab continues on the offline stub; the warning prints once.
- **Embedding takes forever** — it is one call per chunk. Use `make_corpus.py --docs 300`,
  or stay offline for the first pass.
- **`fts5: syntax error`** — you are editing the query translation. Every operand must be
  a quoted literal; legal text is full of `7.3` and `W/10`, which are FTS5 syntax.
- **Retrieval returns nothing relevant in offline mode** — expected. The hashing embedder
  has no idea that "indemnify" and "hold harmless" are related. That is exactly why a
  trained embedder is worth installing, and saying so is more useful than hiding it.
- **The verifier rejects everything** — read the reasons. If they are all `UNCITED CLAIM`,
  your model is ignoring rule 1; strengthen the system prompt, lower the temperature, or
  use a larger model. Do not weaken the verifier.
- **Mixed dimensions** — `ValueError` on cosine, or nonsense results, after switching
  embedders. Delete `vectors.jsonl` and re-embed. You cannot mix dimensions.

## Review Questions

1. Why is fine-tuning close to disqualifying for a legal corpus? Give the **retention**
   argument, not the quality argument.
2. A `[3]` marker resolves to a retrieved chunk. What does that prove, and what does it
   *not* prove?
3. Your vector store is a managed SaaS. What exactly have you put there?
4. Two documents in the corpus disagree about the acceptance date. What should the answer
   look like, and what must it not do?
5. Why must the **rendered** prompt be logged rather than the template plus the document
   id?

---

## Teacher's Playbook

### Worked model answer

With Ollama + `qwen3:8b` + `nomic-embed-text` on the default corpus (1,196 documents →
1,225 chunks), the cap question
should return §7.3 of the drafts and the execution version, with markers resolving, and an
answer that says the cap was **$2,000,000** in Draft 1 and Draft 2 and is **[INTENTIONALLY
OMITTED]** in the execution version. That contrast *is* planted finding F2 and it is the
first time students see the case's actual story come out of their own system.

Offline-stub numbers for reference (they are deliberately unimpressive, and they do not
move with corpus size because the eval set is fixed):

```
cases: 10   answerable: 7   unanswerable: 3
refusal_rate_on_unanswerable: 0.0        <- the headline
answered_when_it_should_not_have: 3
source_hit_rate: 1.0
verifier_rejections: 0
```

Use that 0.0 rather than apologizing for it: *"this system answered every single question
it could not possibly know the answer to. Your production system does this too, and you
will not notice unless you build this eval set."*

### Live-demo script (about 12 minutes)

1. `ask` the cap question with Ollama running. Point at the `LV` / `-V` tag column.
   *"Lexical found it by the words. Vector found it by the meaning. Fusion ranked it."*
2. `ask --break-citations`. All three verifier checks fire on screen.
   *"Every one of those is something a real model did to me in production."*
3. Open `verify()` and read check 3 aloud — the quote check.
   *"A model paraphrasing inside quotation marks has fabricated a quotation from a legal
   document. Nothing in the prompt prevents it. Forty lines of code do."*
4. `ask` the injection question. The system reports the instruction and cites it.
   *"The adversary wrote some of the documents in your corpus. That is not a hypothetical
   in this domain — it is the definition of discovery."*
5. `eval`, then point at `refusal_rate_on_unanswerable`.
6. Close Day 1 with: *"you believe this ran locally. Tomorrow you learn the difference
   between believing it and being able to prove it."*

### Common mistakes + fixes

- **Enforcing citations in the prompt only.** The single most important correction in the
  lab. Asking nicely works most of the time, and "most of the time" is undetectable until
  it matters. Point at the three code checks.
- **Weakening the verifier when it rejects.** The instinct is to relax the check. The
  answer is a better prompt, a lower temperature, or a bigger model.
- **Fixed-size chunking.** Then a citation lands mid-clause and a reviewer cannot use it.
- **Crossing document boundaries in a chunk.** Catch this immediately; a chunk spanning
  two documents cannot be cited at all.
- **Forgetting that the embedder is a leak point.** Ask the room, mid-lab: *"if your chat
  model is local and your embedder is `text-embedding-3-large`, where did the documents
  go?"* Half of them have not thought about it. That is the Module 5 hand-off.
- **Skipping unanswerable questions in the eval set.** Then a 0% refusal rate looks like
  high recall. Roughly 20% of an eval set should be unanswerable.
- **Logging the answer but not the retrieved context.** Half the prompt is retrieved text.
  Without `retrieval.jsonl` nothing can be replayed, and Lab 05's bundle will fail to
  verify.

### Debrief Q&A

- *Why RRF and not a weighted score sum?* RRF needs no score normalization across
  incomparable scales (BM25 vs cosine), is robust, and is one line. `RRF_K = 60` is the
  conventional constant; it damps the influence of any single list's top position.
- *Is 220 tokens the right chunk size?* It is a defensible default for citation precision.
  Bigger chunks retrieve better and cite worse. It is a trade, and it belongs in the
  manifest either way.
- *Can we skip the lexical half?* Not in legal work. Bates numbers, defined terms and
  exact quotes are what lexical search is for, and it is the explainable half.
- *What about "lost in the middle"?* Real. Put the strongest chunk first — `build_prompt`
  already emits them in fused-score order.
- *Is the attribution extension worth doing?* It is the most interesting unsolved problem
  in this course. Strong students should take it.

### What good looks like

A student has a passing citation chain they can click through to a character offset in a
real document; has seen the verifier reject something and can say which of the three
checks fired and why; found the injection and reported it rather than obeying it; has an
eval result including a refusal rate; and can state the four leak points —
**OCR, embeddings, chat, logs** — without looking.

---
