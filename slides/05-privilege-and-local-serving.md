# Module 5 — Privacy, Privilege, and Local Serving: The Privilege Trap

Elephant Scale

---

## Day 2 Starts With the Harder Question

Yesterday you built a system that works.

Today you make it one you can **defend**.

> **"Where did that document go?"**

By lunch you will have a signed artifact that answers it: a run of your own system, with a
monitor attesting that **zero** external connections occurred.

Notes:

Put the two-risks slide from Module 1 back up before this one. Day 2 is the half of the
course that nobody else teaches, and the half that students will actually be paid for.

---

## Where the Data Actually Goes

You send a prompt to a hosted model. Name every hop:

```text
your app
  -> TLS to the provider's edge (their CDN, their region)
    -> their gateway / load balancer      [logged]
      -> their inference cluster           [the prompt, in RAM, in plaintext]
        -> abuse-and-safety classifiers    [a second system reads it]
          -> retention store               [30 days is a common default]
            -> possibly human review        [abuse workflows]
    -> your observability vendor            [you forgot about this one]
    -> your error tracker                   [prompt in the stack trace]
```

* The inference call is the hop everyone thinks about. The **last two** are the ones that
  actually surprise people.
* Your APM/tracing SDK, your error reporter, and your log aggregator may each be shipping
  prompt text — i.e. document text — to a third party you never evaluated.

> You did not make one disclosure decision. You made **six**, and you only remember one.

Notes:

This is the slide that connects back to the Module 1 whiteboard exercise where people drew
the logs hop. Make them count the hops in their own stack out loud.

The abuse-classifier hop deserves a beat: for legitimate safety reasons, providers run a
second model over inputs and outputs, and some have a human-review path. That is a separate
system, with separate access, reading privileged material.

---

## Privilege, For Engineers

* **Attorney–client privilege** protects confidential communications between a client and
  their lawyer made for the purpose of legal advice
* **Work product** protects material prepared **in anticipation of litigation**
* Both are **conditional**: they depend on confidentiality being *maintained*
* Disclosure to a third party can **waive** the protection — and once waived, the material
  may be fair game, and the waiver can extend to related material
* Separately, a lawyer owes a **duty of technological competence** — in most US
  jurisdictions, an explicit ethical duty to understand the tech they use

> There is no incident response for privilege. The protection either held, or it didn't.

Notes:

Engineers model confidentiality as a control that can fail and be remediated. Privilege is
closer to a one-way valve: the question is not "was it secure," it is "was confidentiality
maintained," and a third-party disclosure is the exact thing that answers "no."

Say plainly: this is a course for engineers and none of this is legal advice. The point is
that your *architecture* is now a variable in someone else's privilege analysis, and you
should know it.

---

## Morgan v. V2X, Inc. — What a Court Actually Said

**No. 25-cv-01991 (D. Colo., Mar. 30, 2026)** — Magistrate Judge Dominguez Braswell. An
employment case with a self-represented plaintiff. The first widely-read federal decision on
AI tools in discovery.

What the court held:

* **Work-product protection applies** to a party's use of an AI tool in preparing for
  litigation — Rule 26(b)(3) is broad
* **Using ChatGPT did not, by itself, waive** that protection — waiver requires disclosure
  *to an adversary* or in a manner likely to reach one
* **But the identity of the AI tool is not protected** — the plaintiff was ordered to
  disclose **which AI tools** were used with confidential materials
* **The protective order was amended**: confidential discovery material may go into an AI
  tool only if the provider meets specified contractual safeguards — which, the court noted,
  will for now **exclude most mainstream free and low-cost AI tools**

> The headline for a builder: **the tool you chose is discoverable, and the protective order
> may dictate which tools are allowed at all.**

Notes:

Be precise about what this case is and isn't. It is a magistrate judge's order in one
district, involving a pro se litigant — the court expressly reasoned that a pro se party is
"simultaneously the party and the advocate," which limits how far it generalizes. It is not
a circuit holding, and commentary across firms differs on how broadly it applies.

What is not in dispute is the direction of travel, and it is the part that matters for
architecture: courts are beginning to (a) require disclosure of which AI tool touched
confidential material, and (b) condition AI use on the provider's contractual terms. Both
are easier to satisfy if the answer is "a model running on our own hardware, pinned to this
hash, and here is the attestation."

Cite it accurately and resist the urge to oversell it. The audience in a legal-tech room may
know this case better than you do.

---

## The "Private" Spectrum

From weakest to strongest. Know which one you are actually selling.

| Level | What you have | What you can prove |
|---|---|---|
| 1. **Consumer AI** | Terms of service | Nothing. Often trained on. |
| 2. **Enterprise tier** | "We don't train on your data" | A contract |
| 3. **Zero-retention / BAA / DPA** | Contractual non-retention | A contract, plus an audit report |
| 4. **Dedicated / VPC endpoint** | Their model, your network boundary | A contract + an architecture diagram |
| 5. **Gov cloud (FedRAMP + CJIS addendum)** | An authorized boundary | An authorization package |
| 6. **Local model, your hardware** | The weights are on your disk | **A network log showing zero egress** |
| 7. **Air-gapped** | No network at all | The absence of a cable |

* Levels 2–5 are **contractual** privacy. Levels 6–7 are **physical** privacy.
* A contract is a promise plus a remedy. It is not a mechanism.

> Contractual privacy asks you to trust a counterparty. Physical privacy asks you to trust
> a **packet capture.** Only one of those is evidence.

Notes:

This is the most commercially useful slide in the course — it is a sales tool as much as an
architecture tool. Students will recognize their own vendor conversations in rows 2 and 3.

Be fair to the hosted providers: levels 3–5 are real, substantial, and adequate for a great
deal of work. The argument is not that hosted AI is illegitimate. It is that for privileged
and regulated material, the cheapest way to satisfy a long compliance checklist is to make
the checklist not apply.

---

## Why Local Is Court-Defensible

The structural argument, in four sentences:

1. **No third-party disclosure** → nothing to waive, no vendor to bind, no addendum to
   negotiate, no provider personnel to screen
2. **The compliance surface shrinks to your own controls** — which you already operate for
   the case-management system holding the same documents
3. **You can prove it** — a monitor can show zero outbound connections for a run; that is a
   clean artifact for an auditor or a court
4. **You can pin it** — you cannot pin somebody else's hosted model; it is silently replaced.
   Local weights + a hash = a reproducible review (Module 6)

* Under CJIS, the hosted path means: FedRAMP boundary, signed Security Addendum, personnel
  screening with fingerprint checks, FIPS-validated crypto, data residency, MFA, full audit.
  The local path means: the controls you already run.

> For regulated records, the cheapest route to "strict compliance" is usually to **stop
> sending the data out at all.**

Notes:

This is FreeEed's actual compliance thesis and it is drawn from `docs/local-ai-cjis-briefing.md`.
CJIS is the strictest, most explicit regime, which makes it a useful worst case — but the
underlying logic (no third-party disclosure, no vendor to bind, nothing to waive) is general
and applies to ordinary civil matters just as well.

Point 4 is the one legal buyers have not internalized yet. Say it twice.

---

# Part 2 — Serving a Model Locally

---

## OpenAI-Compatible Is the Whole Trick

Going local is a **config change**, not a rewrite — because everything speaks the same API
shape.

```python
from openai import OpenAI

# cloud
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4.1"

# local — same SDK, same calls, same response objects
client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")
MODEL  = "qwen3:14b"
```

* `base_url` + model name. That is the diff.
* Keep it a **toggle**, driven by config, so you can A/B local vs. cloud on the same corpus
  and *measure* the quality delta rather than guessing at it

> Design your code so "local" is a config value, and the privacy decision stops being an
> architecture migration.

Notes:

This mirrors exactly how FreeEed's AI layer is built: two chokepoints (`get_llm()` and
`embedding_function`), both pointed by config. That is why "go local" is a config change for
them and a rewrite for teams that scattered `openai.ChatCompletion` calls through the
codebase.

Practical tip to give: centralize your model client in one module on day one, even if you
only ever use one provider.

---

## Ollama vs. vLLM

| | **Ollama** | **vLLM** |
|---|---|---|
| Footprint | Laptop / workstation | GPU server |
| Install | one binary, `ollama pull qwen3:14b` | Python + CUDA |
| Throughput | single-user | high, batched, concurrent |
| API | OpenAI-compatible `/v1` + embeddings | OpenAI-compatible `/v1` |
| Use for | dev, desktop product, demos, this class | production batch & multi-user |

* **One code path, config-scaled:** desktop → Ollama; server → vLLM. The application cannot
  tell the difference.
* Also in this family: llama.cpp (embedded, no server), TGI, LM Studio (GUI).

```sh
ollama pull qwen3:8b
ollama pull nomic-embed-text
curl http://localhost:11434/v1/models
```

Notes:

Have students run those three commands before the lab. The `curl` is the "is it alive" check
and it is also the moment they realize a local model is just an HTTP service on a port.

---

## Picking a Local Model: Pin It to Your VRAM

| Tier (VRAM) | Chat / RAG | Note |
|---|---|---|
| Entry — 16 GB | **Qwen3 8B** or **Llama 3.1 8B** (Q4/Q5) | Good instruction-following + citation behavior |
| Recommended — 24 GB | **Qwen3 14B** or **Gemma 3 12B** | Best quality-per-VRAM at the 4090 tier |
| Business — 48 GB | **Qwen3 32B** or **Mistral Small 3.x** | Approaches hosted quality |
| Server — 48–80 GB | **Llama 3.3 70B** / **Qwen3 72B** (Q4) | "As good as cloud for most tasks" |

* **Structured extraction** (fill known fields): a mid-size instruct model with reliable JSON
  output is enough. Temperature 0, validate against the schema. Don't reach for 70B.
* **Embeddings:** `nomic-embed-text` (768) or `mxbai-embed-large` (1024)
* **Pin the model and the quantization.** They are part of the validated pipeline — a model
  bump is a code change and needs re-validation.

> Quantization is a quality decision, not just a memory decision. Q4 is usually fine for
> RAG; validate it, don't assume it.

Notes:

These are FreeEed's current pinned defaults mapped to hardware tiers — say they rev fast and
should be treated as a snapshot, not a permanent list.

The honest caveat students need: a local open-weight model will not automatically match the
largest hosted models on messy real-world documents. The professional move is a validation
pass — run both against a labeled sample and measure field-level precision and recall. The
compliance case is the *why*; a measured accuracy delta is what makes the switch defensible.

---

# Part 3 — Proving It

---

## Belief Is Not Evidence

You configured `base_url` to localhost. Can you prove nothing left?

Three layers, and you need all three:

1. **Enforce** — network policy blocks outbound traffic from the AI process. The local model
   and local OCR need no internet. Default-deny, allow loopback.
2. **Observe** — monitor the process's connections for the duration of the run and record
   every one
3. **Attest** — emit a signed artifact: run id, time window, process, **every** connection
   observed, and the explicit claim *zero non-loopback connections*

* Belt-and-suspenders demo: **run the whole thing with the network physically off.** It is
  the most persuasive thirty seconds in any client meeting.

> "We configured it to be local" is a statement about intent.
> "Here is the connection log for the run" is a statement about fact.

Notes:

Build order matters and it is worth stating: start with observability (prove what the current
system actually does — teams are routinely surprised), then enforce, then package the
attestation as a first-class product output. Teams that enforce first break things and learn
nothing.

---

## The Four Leak Points (Count Them Every Time)

```text
   document  ->  [1] OCR / extraction  ->  [2] embeddings  ->  [3] the chat model
                                                                      |
                                                              [4] logs, traces, errors
```

1. **OCR / extraction** — a cloud document-intelligence API leaks the raw page
2. **Embeddings** — a cloud embedding call ships the full chunk text
3. **The chat model** — the one everybody remembers
4. **Logs and telemetry** — prompts in your APM, documents in your stack traces

* Your posture is set by the **leakiest** stage. Localizing [3] alone buys you nothing.

> Four stages. Audit all four, every time, by name. Most "private AI" architectures
> localize one.

Notes:

This is the course's most reusable checklist and it has now appeared in Modules 2, 4, and 5.
That repetition is deliberate. Make them recite the four.

Add the fifth if the room is sharp enough: the **model download itself**. Pulling weights is
an outbound call — do it once, verify the hash, then run offline. It is not a leak of document
data, but it is a supply-chain event, and it belongs in the SAIS-100 Model & Supply Chain
category.

---

## The Attestation Artifact

```json
{
  "attestation_version": "1.0",
  "run_id": "run-2026-11-09T14:02:11Z-7f3a",
  "matter": "SYNTHETIC-DEMO-01",
  "window": { "start": "2026-11-09T14:02:11Z", "end": "2026-11-09T14:19:48Z" },
  "host": { "os": "Linux 6.8.0", "hostname_sha256": "c41d..." },
  "ai_components": {
    "chat":       { "endpoint": "http://127.0.0.1:11434/v1", "model": "qwen3:14b",
                    "weights_sha256": "9ab3...", "runtime": "ollama 0.5.4" },
    "embeddings": { "endpoint": "http://127.0.0.1:11434/v1", "model": "nomic-embed-text",
                    "dim": 768 },
    "ocr":        { "engine": "tesseract", "version": "5.3.4", "local": true }
  },
  "egress_policy": "default-deny; loopback only",
  "connections_observed": [
    { "peer": "127.0.0.1:11434", "proto": "tcp", "count": 412, "loopback": true }
  ],
  "non_loopback_connections": 0,
  "documents_processed": 1184,
  "claim": "No document content left this host during the window above.",
  "produced_by": "egress_attest 1.0",
  "artifact_sha256": "e7c1..."
}
```

> This is the deliverable. Not a slide, not a policy document — **a file, with a hash, from
> a run that happened.**

Notes:

Walk the fields. The ones students leave out and shouldn't: `weights_sha256` (ties the
attestation to Module 6's reproducibility bundle), `egress_policy` (states what was enforced,
not just what was observed), and `artifact_sha256` (makes the attestation itself tamper-evident).

Be scrupulous about the limits of the claim: this attests to *observed connections from the
monitored process tree during the window*. It does not prove the absence of a kernel-level
exfiltration path, and you should say so rather than let an expert say it for you. Honest
scope is what makes the artifact credible.

---

## Honest Limits of the Claim

Say these before someone else does:

* The monitor observes **the processes it monitors.** Scope it explicitly and say so.
* It covers **a time window.** Continuous monitoring is a different, stronger claim.
* A **DNS lookup** is itself a disclosure (that you looked something up, and when) —
  count it.
* **Model download** is an outbound call. Do it once, verify the hash, then go offline.
* **Enforcement beats observation.** A monitor sees; a firewall prevents. Ship both.
* Local inference on a GPU is **not bit-deterministic** — that is a Module 6 problem, and
  we will not pretend otherwise.

> Overclaiming is the fastest way to lose a defensibility argument. Name your limits and
> you keep your credibility.

Notes:

Dwell here. The commercial temptation in this space is to oversell "provably private," and an
expert witness will dismantle it in one question. A narrower claim, precisely stated, with an
artifact behind it, beats a broad claim with a brochure behind it — every time.

This slide is also what distinguishes an Elephant Scale course from vendor training. Say so.

---

## Lab 05 — Local Model + Egress Proof

Run yesterday's RAG end to end on a **local** model, and prove nothing left:

* Point the client at Ollama; re-run the Lab 04 eval set
* Install an **in-process egress guard**: default-deny sockets, loopback allowed, every
  attempt recorded
* Run the **monitor**; attempt a deliberate outbound call and watch it get blocked **and
  logged**
* Emit `attestation.json` with the connection log, model hash, and the claim
* **Compare local vs. cloud** on the same eval set and record the quality delta honestly

**Deliverable:** `attestation.json` + a one-page local-vs-cloud comparison with real numbers.

> Optional and worth it: pull the network cable (or `nmcli radio wifi off`) and run it again.

Notes:

Budget 75 minutes. The deliberate-blocked-call step is the one that makes the lesson physical
— students see their own code get stopped, with a log line naming the destination.

Insist on the honest comparison. Some students will find the local model clearly worse on
their eval set. That is the correct, valuable outcome and it is what a real validation pass
looks like. The answer is not to hide it; it is to size the hardware, pick a bigger tier, or
document the delta and the mitigation.

---

## ▶ LAB BREAK — Lab 05

Debrief: **"Read me your `non_loopback_connections` number. Now read me your quality
delta."**

Notes:

Two numbers, in that order, from four or five students. The first should be 0 for everyone.
The second will vary, and the variation is the honest conversation about hardware tiers and
model selection that no vendor will have with them.
