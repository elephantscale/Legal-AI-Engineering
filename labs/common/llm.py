"""llm.py — the only place in these labs that talks to a model.

Three modes, chosen by environment. Local is the default, because in legal work local is
the default.

    LEGAL_AI_MODE=local    (default)  Ollama (or any OpenAI-compatible server) on localhost
    LEGAL_AI_MODE=offline             no model at all; deterministic stand-ins
    LEGAL_AI_MODE=cloud               a hosted provider — the CONTRAST CASE, used in Lab 04
                                      to measure what you give up, never the happy path

Environment:
    LEGAL_AI_BASE_URL   default http://localhost:11434/v1
    LEGAL_AI_MODEL      default qwen3:8b
    LEGAL_AI_EMBED      default nomic-embed-text
    LEGAL_AI_API_KEY    only used when LEGAL_AI_MODE=cloud

Why an offline mode exists: no lab in this course may be blocked on a download. The
offline embedder is a hashed character-n-gram vectorizer — real, deterministic, and
genuinely worse than a trained model, which is itself the lesson. The offline chat
"model" is an extractive stub that quotes and cites its context; it is good enough to
exercise a citation verifier and honest enough not to pretend to reason.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Iterable, Sequence

MODE = os.environ.get("LEGAL_AI_MODE", "local").lower()
BASE_URL = os.environ.get("LEGAL_AI_BASE_URL", "http://localhost:11434/v1").rstrip("/")
CHAT_MODEL = os.environ.get("LEGAL_AI_MODEL", "qwen3:8b")
EMBED_MODEL = os.environ.get("LEGAL_AI_EMBED", "nomic-embed-text")
API_KEY = os.environ.get("LEGAL_AI_API_KEY", "not-needed")
OFFLINE_DIM = 512

_warned: set[str] = set()


def _warn_once(key: str, msg: str) -> None:
    if key not in _warned:
        _warned.add(key)
        print(f"[llm] {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- info
@dataclass
class ModelInfo:
    """Everything the reproducibility manifest needs to know about the AI layer."""
    mode: str
    chat_endpoint: str
    chat_model: str
    embed_model: str
    embed_dim: int | None = None
    runtime: str | None = None
    weights_sha256: str | None = None
    quantization: str | None = None
    decoding: dict = field(default_factory=lambda: {"temperature": 0, "seed": 42})
    local: bool = True

    def as_dict(self) -> dict:
        return asdict(self)


def model_info() -> ModelInfo:
    """Describe the AI layer for the manifest and the attestation.

    Note what this does NOT do: invent a weights hash. If we cannot read one from the
    runtime, the field stays None and the manifest says so. A reproducibility artifact
    that guesses is worse than one that admits a gap.
    """
    if MODE == "offline":
        # The offline stand-ins are code, not weights — so the thing that determines
        # their behavior, and therefore the thing you pin, is the SOURCE. Hashing this
        # file is a genuine pin: change the stub and the hash changes, exactly as a model
        # bump changes a weights digest. The principle generalizes: pin whatever actually
        # decides the output, and name what you pinned.
        return ModelInfo(mode="offline", chat_endpoint="none",
                         chat_model="offline-extractive-stub",
                         embed_model=f"offline-hashing-{OFFLINE_DIM}",
                         embed_dim=OFFLINE_DIM, runtime="builtin (stdlib)",
                         weights_sha256=_source_sha256(),
                         quantization="n/a (deterministic code, not weights)",
                         local=True)
    if MODE == "cloud":
        return ModelInfo(mode="cloud", chat_endpoint=BASE_URL, chat_model=CHAT_MODEL,
                         embed_model=EMBED_MODEL, runtime="hosted (not pinnable)",
                         local=False)
    info = ModelInfo(mode="local", chat_endpoint=BASE_URL, chat_model=CHAT_MODEL,
                     embed_model=EMBED_MODEL, local=True)
    tags = _ollama_show(CHAT_MODEL)
    if tags:
        info.runtime = f"ollama {tags.get('_server_version', '?')}"
        info.weights_sha256 = tags.get("digest")
        info.quantization = tags.get("quantization_level")
    return info


def _source_sha256() -> str:
    """SHA-256 of this module's source — the pin for the offline stand-ins."""
    try:
        return hashlib.sha256(__file__ and open(__file__, "rb").read()).hexdigest()
    except OSError:
        return "unavailable"


def _ollama_show(model: str) -> dict | None:
    """Ask Ollama for the model digest + quantization. Best effort; None on failure."""
    root = BASE_URL[:-3] if BASE_URL.endswith("/v1") else BASE_URL
    try:
        req = urllib.request.Request(
            f"{root}/api/show", data=json.dumps({"model": model}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = json.loads(r.read())
    except Exception:
        return None
    details = body.get("details", {}) or {}
    digest = (body.get("digest") or "").replace("sha256:", "") or None
    out = {"quantization_level": details.get("quantization_level"), "digest": digest}
    try:
        with urllib.request.urlopen(f"{root}/api/version", timeout=5) as r:
            out["_server_version"] = json.loads(r.read()).get("version", "?")
    except Exception:
        out["_server_version"] = "?"
    return out


def available() -> bool:
    """Is the configured endpoint actually there? Labs use this to pick a mode."""
    if MODE == "offline":
        return True
    try:
        req = urllib.request.Request(f"{BASE_URL}/models",
                                     headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


# --------------------------------------------------------------------------- chat
def chat(system: str, user: str, *, temperature: float = 0.0, seed: int = 42,
         max_tokens: int = 1024) -> str:
    """One chat completion. Temperature 0 and a fixed seed, always, on purpose.

    Greedy decoding is what makes a review reproducible (Module 6). If you find
    yourself wanting temperature > 0 in a legal pipeline, write down why.
    """
    if MODE == "offline":
        return _offline_chat(system, user)
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.loads(r.read())
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, OSError, KeyError) as e:
        _warn_once("chat-fallback",
                   f"chat endpoint unavailable ({e}); falling back to the offline stub. "
                   f"Start Ollama for the real thing: `ollama serve && ollama pull {CHAT_MODEL}`")
        return _offline_chat(system, user)


_CTX_RE = re.compile(r"^\[(\d+)\]\s", re.M)


def _offline_chat(system: str, user: str) -> str:
    """A deterministic extractive stand-in.

    It finds the numbered context block, scores each passage by overlap with the question,
    and answers by quoting the best passage with its [n] marker. It cannot reason. It can
    exercise a citation verifier, which is what the labs need it for.
    """
    blocks = _split_numbered_context(user)
    question = _extract_question(user)
    if not blocks:
        return "Not found in the provided documents."
    qterms = set(_tokens(question))
    scored = sorted(
        ((len(qterms & set(_tokens(txt))), n, txt) for n, txt in blocks),
        reverse=True)
    best_score, best_n, best_txt = scored[0]
    if best_score < 2:
        return "Not found in the provided documents."
    sentences = [s.strip() for s in re.split(r"(?<=[.;])\s+", best_txt) if s.strip()]
    sentences.sort(key=lambda s: len(qterms & set(_tokens(s))), reverse=True)
    # cite EVERY sentence, not just the last one: the citation rules in the lab's system
    # prompt are absolute, and a stand-in that ignores them teaches the wrong habit
    out = []
    for sent in sentences[:2]:
        sent = re.sub(r"\s+", " ", sent).strip()
        if not sent:
            continue
        out.append(sent if sent.endswith(f"[{best_n}]") else f"{sent} [{best_n}]")
    return " ".join(out)[:700] or "Not found in the provided documents."


def _split_numbered_context(user: str) -> list[tuple[int, str]]:
    m = re.search(r"<context>(.*?)</context>", user, re.S)
    body = m.group(1) if m else user
    parts = _CTX_RE.split(body)
    out: list[tuple[int, str]] = []
    for i in range(1, len(parts) - 1, 2):
        try:
            n = int(parts[i])
        except ValueError:
            continue
        block = parts[i + 1]
        # the first line of each block is our provenance header
        # ("DOC-000417 | §7.3 | chars 10-900 | custodian=jdoe"), not document text.
        # Quoting it back would be a fabricated quotation.
        head, _, rest = block.partition("\n")
        text = rest if "|" in head and "chars" in head else block
        out.append((n, text.strip()))
    return out


def _extract_question(user: str) -> str:
    m = re.search(r"(?:Question|QUESTION):\s*(.+)", user)
    if m:
        return m.group(1)
    return user.rsplit("</context>", 1)[-1]


def _tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9']+", s.lower()) if len(t) > 2]


# ----------------------------------------------------------------------- embeddings
def embed(texts: Sequence[str]) -> list[list[float]]:
    """Embed a batch. Returns unit-normalized vectors.

    Reminder from Module 4: the dimension is part of your index. Change the model and you
    re-ingest the corpus — you cannot mix dimensions in one collection.
    """
    if MODE == "offline":
        return [_offline_embed(t) for t in texts]
    out: list[list[float]] = []
    for t in texts:
        payload = {"model": EMBED_MODEL, "input": t}
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/embeddings", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {API_KEY}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read())
            out.append(_normalize(body["data"][0]["embedding"]))
        except (urllib.error.URLError, OSError, KeyError) as e:
            _warn_once("embed-fallback",
                       f"embedding endpoint unavailable ({e}); using the offline hashing "
                       f"embedder. Retrieval quality WILL be worse — that is the lesson, "
                       f"not a bug. `ollama pull {EMBED_MODEL}` for the real thing.")
            out.append(_offline_embed(t))
    return out


def _offline_embed(text: str, dim: int = OFFLINE_DIM) -> list[float]:
    """Hashed character-4-gram + word unigram vectorizer. Deterministic, no download.

    This is a real technique (the hashing trick) and a weak one. It survives OCR noise
    reasonably well, which is why it is not useless here, and it has no idea that
    'indemnify' and 'hold harmless' are related, which is why a trained embedder wins.
    """
    vec = [0.0] * dim
    s = re.sub(r"\s+", " ", text.lower())
    grams: list[str] = [s[i:i + 4] for i in range(max(0, len(s) - 3))]
    grams += _tokens(s)
    for g in grams:
        h = hashlib.blake2b(g.encode(), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        sign = 1.0 if h[4] & 1 else -1.0
        vec[idx] += sign
    return _normalize(vec)


def _normalize(v: Iterable[float]) -> list[float]:
    v = list(v)
    norm = sum(x * x for x in v) ** 0.5
    return [x / norm for x in v] if norm else v


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


# ----------------------------------------------------------------------------- cli
if __name__ == "__main__":
    info = model_info()
    print(json.dumps(info.as_dict(), indent=2))
    print(f"endpoint reachable: {available()}")
    if not info.local:
        print("\n!! MODE=cloud. Document text will leave this machine. "
              "This mode exists for the Lab 04 comparison only.")
