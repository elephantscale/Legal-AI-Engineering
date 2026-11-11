# Lab 05 — Local Model + Egress Proof

**Module:** 5 — Privacy, Privilege, and Local Serving
**Duration:** 75 minutes
**Difficulty:** Intermediate

---

## Goal

Run yesterday's RAG end to end on a **local** model and produce the artifact that answers
*"where did that document go?"* — an `attestation.json` with the connection log, the model
pins, the claim, and **its own stated limits**.

Then measure, honestly, what going local cost you in quality.

> "We configured it to be local" is a statement about intent.
> "Here is the connection log for the run" is a statement about fact.

## Files in this lab

```
05-Local-Model-Egress-Proof/
  README.md          <- you are here
  requirements.txt   <- nothing to install
  local_proof.py     <- observe / prove / tripwire / compare
```

The guard and the attestation writer live in `../common/egress.py`. Read it — it is 250
lines and it is the whole module.

## Prerequisites

- Labs 02–04 complete (`../work/chunks.jsonl` and `../work/vectors.jsonl` exist)
- **Ollama running**, for the lab as intended:
  ```sh
  ollama serve &
  ollama pull qwen3:8b
  ollama pull nomic-embed-text
  curl http://localhost:11434/v1/models        # the "is it alive" check
  ```
- No Ollama? Every step still runs on the offline stub and the attestation is still real.

## Steps

### 1. Observe before you enforce

```sh
python3 local_proof.py observe --work ../work
```

Nothing is blocked. Everything is recorded. This is step one on any system you did not
build yourself, and teams are routinely surprised by the answer.

Read the `by peer` table. Every row marked `*** EXTERNAL ***` is a decision somebody made
and probably does not remember making.

### 2. Count the four leak points

Open `ai_components()` in `local_proof.py`. Four entries, and that is not an accident:

| # | Component | The mistake |
|---|---|---|
| 1 | `ocr_extraction` | a cloud OCR API leaks the raw page before the LLM ever sees it |
| 2 | `embeddings` | a cloud embedding call ships the full chunk text |
| 3 | `chat` | the one everybody remembers |
| 4 | `telemetry_and_logs` | prompts in your APM; documents in your stack traces |

Your posture is set by the **leakiest** stage. Localizing #3 alone buys you nothing.

Now say all four out loud. You will be asked them in the defense round.

### 3. Enforce and attest

```sh
python3 local_proof.py prove --work ../work
cat ../work/attestation.json | python3 -m json.tool
```

Read the whole artifact, field by field. Then read **`scope_and_limits`** and understand
why it is there:

- the guard is **in-process** — it covers this Python process, not subprocesses, not other
  host processes, not anything below the runtime
- it covers **a time window**, not continuous operation
- a **DNS lookup** is itself a disclosure, and is counted
- enforcement in production belongs to a **firewall** or an `internal: true` network; the
  guard demonstrates the control and produces the record

Overclaiming is the fastest way to lose a defensibility argument. Naming your limits is
what makes the artifact credible.

### 4. Trip the wire

```sh
python3 local_proof.py tripwire --work ../work
```

Four deliberate leaks — a hosted model API, a SaaS log aggregator, a cloud OCR endpoint,
and a bare IP with no DNS — all blocked, all logged. And loopback, allowed.

Note that the blocked attempts appear **in the attestation**. An attestation that hides
the attempts is worth nothing; one that records them is evidence the control is live.

### 5. Measure what local cost you

```sh
python3 local_proof.py compare --work ../work
```

With no API key set it reports local only — which is the right default for a legal course.
To run the actual comparison against the **synthetic** corpus:

```sh
export LEGAL_AI_MODE=cloud
export LEGAL_AI_BASE_URL=https://api.openai.com/v1
export LEGAL_AI_API_KEY=sk-...
python3 local_proof.py compare --work ../work
unset LEGAL_AI_API_KEY LEGAL_AI_MODE
```

Read `how_to_read_this` in `../work/local-vs-cloud.json`. `verifier_pass` is a floor, not
a quality score. `non_loopback_connections` is the column that decides whether you are
allowed to use the row at all.

**If local loses, say so.** That is what a validation pass looks like. The honest moves
are a bigger VRAM tier, a larger model, better chunking, or documenting the delta and the
mitigation. Hiding it is not on the list.

### 6. The belt-and-suspenders demo (worth 30 seconds of your life)

```sh
nmcli radio wifi off        # Linux;  macOS: turn off Wi-Fi;  or pull the cable
python3 local_proof.py prove --work ../work
nmcli radio wifi on
```

Your legal-AI system answering questions about documents with the network physically off
is the most persuasive thirty seconds you will ever have in a client meeting.

## Deliverable

1. `../work/attestation.json` — `non_loopback_connections: 0`, with the model pins and
   the stated limits
2. `../work/attestation-tripwire.json` — proof the control is live, with the blocked
   attempts recorded
3. `../work/local-vs-cloud.json` — a one-page comparison with real numbers
4. One written sentence naming a limit of your own claim that an opposing expert could
   otherwise raise first

## Exercises

1. **Leak on purpose, from inside the pipeline.** Add `urllib.request.urlopen("https://example.com")`
   to `_run_rag`. Run `prove`. Find the log line. Remove it.
2. **Point the embedder at a cloud endpoint** and keep the chat model local. Run `prove`.
   Watch it get blocked, and explain to your neighbour exactly which document text would
   have left.
3. **Switch policy to `deny-lan`** (`export LEGAL_AI_EGRESS=deny-lan`). When is that the
   right policy, and what does it cost you in the claim you can make?
4. **Tamper with the artifact.** Edit a number in `attestation.json`, then recompute the
   hash over the document without `artifact_sha256`. Show that the tampering is
   detectable — and that this is why the artifact hashes itself.
5. **Pin the model properly.** If `weights_sha256` is `null`, find out why
   (`curl localhost:11434/api/show -d '{"model":"qwen3:8b"}'`). An unpinnable model is a
   **legal auto-fail** in Module 7.

## Troubleshooting

- **`no chunks at ../work`** — Lab 04's `chunk` and `embed` first.
- **`EGRESS BLOCKED` during `prove` and you did not expect it** — good. That is the lab
  working. Read the destination in the message; it is one of the four leak points.
- **`weights_sha256: null`** — the runtime did not expose a digest, or you are on the
  offline stub. The attestation says so rather than guessing; see exercise 5.
- **Ollama on a non-default port or host** — `export LEGAL_AI_BASE_URL=http://127.0.0.1:PORT/v1`.
  If Ollama is on another machine, you need `deny-lan` and you must say so in the claim.
- **`compare` skips cloud** — no `LEGAL_AI_API_KEY`. That is intentional.
- **The tripwire "connects" to loopback** — that means something is listening on 11434,
  i.e. Ollama is up. The guard allowed it, which is correct.

## Review Questions

1. Your chat model is local and your embedder is hosted. What exactly left the building?
2. Name the four leak points, in order.
3. What does `non_loopback_connections: 0` actually prove, and what does it not?
4. A vendor offers a zero-retention contractual guarantee. Which level of the "private"
   spectrum is that, and what evidence can you produce for it?
5. Why is reproducibility (Module 6) a *second*, independent argument for local inference?

---

## Teacher's Playbook

### Worked model answer

With Ollama up, `prove` should report `non_loopback_connections: 0` with a few hundred
loopback attempts to `127.0.0.1:11434` — one per chat call and one per embedding call.
`tripwire` should report **4 blocked, 4 non-loopback, 0 connected**, with loopback allowed.

The attestation's `ai_components` should show all four components `local: true`, and
`weights_sha256` populated from `/api/show` when Ollama is the runtime.

### Live-demo script (about 12 minutes)

1. `observe` first, on purpose. *"We changed nothing. We just watched."* If anyone in the
   room has an APM SDK in their own stack, ask what they think `observe` would print
   there. The silence is the lesson.
2. `prove`. Show the artifact on screen. Scroll to **`scope_and_limits`** and read all
   five aloud. *"An expert witness will say every one of these. I would rather say them
   first."* This slide-free moment is the heart of the course's credibility argument.
3. `tripwire`. Four blocks, including the **log aggregator** and the **cloud OCR**.
   *"Nobody forgets the model. Everybody forgets these two."*
4. **The cable.** Turn off Wi-Fi on the projector machine and run `prove` again. It still
   answers questions about the documents. Hold the silence for a beat.
5. `compare`, if you have a key. Put both rows up. Then point at the `egress` column:
   *"The cloud row might be better. It is also the row that is not available to you."*

### Common mistakes + fixes

- **Enforcing before observing.** Things break, nobody learns anything, and the student
  never finds out what their pipeline was actually doing.
- **Localizing only the chat model.** The single most common real-world error. Exercise 2
  makes it concrete; make everyone do it.
- **Overclaiming.** Watch for "provably private" and "no data ever leaves" in students'
  writing. Correct it to the narrow, true claim. This is a professional-habit correction,
  not a pedantic one.
- **Treating the monitor as the control.** A monitor sees; a firewall prevents. Ship both.
  `internal: true` in Module 7 is the enforcement half.
- **Being embarrassed by a bad local score.** The honest comparison *is* the deliverable.
  Say out loud that a measured accuracy delta is what makes the switch defensible — the
  compliance case is the *why*, the measurement is the *how*.
- **Forgetting the model download is itself an outbound call.** Pull once, verify the
  hash, go offline. It is a supply-chain event, not a document leak — and it belongs in
  SAIS-100's Model & Supply Chain category.

### Debrief Q&A

- *Could a determined process bypass this guard?* Yes — it is in-process and it says so.
  Real enforcement is a firewall rule or an isolated network. The guard's job is the
  **record**, and the record is the artifact nobody else in legal AI is producing.
- *Is a DNS lookup really a disclosure?* Yes: the resolver learns what you looked up and
  when. In a matter where the existence of an inquiry is sensitive, that is not trivial.
- *What about hosted zero-retention tiers?* Legitimate, substantial, and adequate for a
  lot of work. The argument is not that hosted AI is illegitimate — it is that for
  privileged and regulated material the cheapest way to satisfy a long checklist is to
  make the checklist not apply.
- *How would I attest continuously, not per-run?* A long-lived monitor writing a signed,
  append-only log, with the per-matter window extracted on demand. That is a product, and
  a good one.

### What good looks like

A student has an `attestation.json` with zero non-loopback connections **and can state
three limits of their own claim without being prompted**; has a tripwire artifact showing
blocked attempts recorded rather than hidden; has an honest local-vs-something comparison;
and can recite the four leak points — **OCR, embeddings, chat, logs**.

The sentence you are listening for: *"I can prove no document content left this host from
this process during this window — and here is what that does not cover."*

---
