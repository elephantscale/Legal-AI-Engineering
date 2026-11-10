"""bundle.py — the defensible case snapshot (Module 6).

A reproducibility bundle is a directory you could hand to opposing counsel so they can
re-run your review and get the same determinations. This module writes one, and verifies
one.

    from bundle import Bundle
    b = Bundle("case-snapshot-SYNTHETIC-DEMO-01", matter="SYNTHETIC-DEMO-01")
    b.pin_model(model_info())
    b.pin_corpus("work/catalog.jsonl")
    b.log_query(query, chunks, prompt, answer)      # one row per model call
    b.log_decision(doc_id, "responsive", rationale, citations)
    b.write_manifest()
    print(b.verify())                                # replay and certify

The two directories teams always omit, and this module therefore makes mandatory:

  runs/<run-id>/retrieval.jsonl    the chunk set per query. Half the prompt is retrieved
                                   text; without it you cannot replay anything.
  validation/protocol.md           written BEFORE the run. Without it, your acceptance
                                   threshold was chosen after you saw the result.

Determinism, stated honestly (and repeated inside VERIFY.md):

  * Default claim = **same determinations**. Greedy decoding (temperature 0) plus a pinned
    model, runtime and captured prompts makes this robust in practice.
  * **Bit-exact** replay is a separate, stronger claim. GPU inference is not bit-exact
    because parallel floating-point reduction order varies; for bit-exact archival replay
    you run the verify pass on a deterministic backend (CPU, fixed config).
  * Do not promise the second while delivering the first.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

BUNDLE_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_sha(cwd: str | Path | None = None) -> str | None:
    """Your own glue code is part of the pipeline. Pin it too."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd or os.getcwd(),
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    return obj


class Bundle:
    """Write and verify a defensible case snapshot."""

    def __init__(self, root: str | Path, *, matter: str, run_id: str | None = None):
        self.root = Path(root)
        self.matter = matter
        self.run_id = run_id or f"run-{_now().replace(':', '').replace('-', '')}"
        self.started = _now()
        self.pins: dict[str, Any] = {}
        self._queries = 0
        self._decisions = 0
        for d in ("corpus", f"runs/{self.run_id}/prompts", "validation"):
            (self.root / d).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ paths
    @property
    def run_dir(self) -> Path:
        return self.root / "runs" / self.run_id

    # ------------------------------------------------------------------- pins
    def pin_model(self, info: Any) -> None:
        d = _jsonable(info)
        if isinstance(d, dict) and not d.get("weights_sha256"):
            d["weights_sha256_note"] = (
                "NOT AVAILABLE. The runtime did not expose a weights digest, or the "
                "model is hosted and cannot be pinned. A review run against an "
                "unpinnable model is not reproducible — see the legal auto-fail in "
                "course-materials/sais-100-legal-overlay.md.")
        self.pins["model"] = d

    def pin_embeddings(self, *, model: str, dim: int | None, chunk_tokens: int,
                       overlap: float, strategy: str) -> None:
        self.pins["embeddings"] = {
            "model": model, "dim": dim, "chunk_tokens": chunk_tokens,
            "chunk_overlap": overlap, "chunking_strategy": strategy,
            "note": "Changing the embedding model changes the vector dimension and "
                    "forces a full re-ingest. It is a pinned part of the pipeline.",
        }

    def pin_corpus(self, catalog_path: str | Path,
                   exceptions_path: str | Path | None = None) -> None:
        catalog_path = Path(catalog_path)
        dest = self.root / "corpus" / "catalog.jsonl"
        dest.write_bytes(catalog_path.read_bytes())
        n = sum(1 for _ in dest.open(encoding="utf-8") if _.strip())
        entry = {"catalog_sha256": sha256_file(dest), "document_count": n}
        if exceptions_path and Path(exceptions_path).exists():
            edest = self.root / "corpus" / "exceptions.jsonl"
            edest.write_bytes(Path(exceptions_path).read_bytes())
            entry["exceptions_sha256"] = sha256_file(edest)
            entry["exception_count"] = sum(
                1 for _ in edest.open(encoding="utf-8") if _.strip())
        else:
            entry["exception_count"] = None
            entry["exceptions_note"] = (
                "NO EXCEPTION LIST. 'We processed N documents' is not a true statement "
                "unless you can also say what happened to the rest.")
        self.pins["corpus"] = entry

    def pin_index(self, index_path: str | Path | None, *, frozen: bool) -> None:
        self.pins["index"] = {
            "path": str(index_path) if index_path else None,
            "sha256": sha256_file(index_path) if index_path and
            Path(index_path).is_file() else None,
            "frozen": frozen,
            "note": "Retrieval must be replayable: either freeze the index or capture "
                    "the retrieved set per query (we do both).",
        }

    def pin_software(self, repo_root: str | Path | None = None) -> None:
        self.pins["software"] = {
            "git_sha": git_sha(repo_root),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "built_at": _now(),
        }

    # ------------------------------------------------------------------- logs
    def log_query(self, *, query: str, chunks: Iterable[dict], prompt: str,
                  answer: str, citations: Iterable[str] | None = None,
                  extra: dict | None = None) -> str:
        """Record one model call completely enough to replay it."""
        qid = f"q{self._queries:06d}"
        self._queries += 1
        (self.run_dir / "prompts" / f"{qid}.txt").write_text(prompt, encoding="utf-8")
        chunk_rows = [
            {"rank": i, "chunk_id": c.get("chunk_id"), "doc_id": c.get("doc_id"),
             "char_start": c.get("char_start"), "char_end": c.get("char_end"),
             "score": c.get("score"), "text_sha256": sha256_text(c.get("text", ""))}
            for i, c in enumerate(chunks, 1)
        ]
        self._append(self.run_dir / "retrieval.jsonl",
                     {"qid": qid, "query": query, "retrieved": chunk_rows})
        row = {"qid": qid, "query": query, "answer": answer,
               "citations": list(citations or []),
               "prompt_sha256": sha256_text(prompt),
               "prompt_path": f"runs/{self.run_id}/prompts/{qid}.txt",
               "answer_sha256": sha256_text(answer), "at": _now()}
        if extra:
            row.update(extra)
        self._append(self.run_dir / "responses.jsonl", row)
        return qid

    def log_decision(self, *, doc_id: str, decision: str, rationale: str = "",
                     citations: Iterable[str] | None = None,
                     confidence: float | None = None, reviewed_by: str | None = None,
                     override: str | None = None, qid: str | None = None) -> None:
        """One row per coding decision. Append-only. This file is your witness."""
        self._decisions += 1
        self._append(self.root / "decisions.jsonl", {
            "doc_id": doc_id, "decision": decision, "confidence": confidence,
            "rationale": rationale, "citations": list(citations or []),
            "qid": qid, "reviewed_by": reviewed_by, "override": override,
            "at": _now(),
        })

    def log_step(self, row: dict) -> None:
        """One row per agent step (Module 10). Same bundle, same schema family."""
        self._append(self.run_dir / "steps.jsonl", {**row, "at": _now()})

    @staticmethod
    def _append(path: Path, row: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    # -------------------------------------------------------------- validation
    def write_protocol(self, text: str) -> Path:
        """Write validation/protocol.md. Call this BEFORE you classify anything."""
        p = self.root / "validation" / "protocol.md"
        p.write_text(text, encoding="utf-8")
        return p

    def attach_validation(self, *, ground_truth: dict[str, bool], metrics: dict,
                          seed: int) -> None:
        gt = self.root / "validation" / "ground_truth.jsonl"
        with gt.open("w", encoding="utf-8") as fh:
            for doc_id, responsive in sorted(ground_truth.items()):
                fh.write(json.dumps({"doc_id": doc_id, "responsive": responsive,
                                      "source": "blind human review (synthetic)"}) + "\n")
        (self.root / "validation" / "metrics.json").write_text(
            json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        proto = self.root / "validation" / "protocol.md"
        self.pins["validation"] = {
            "sample_seed": seed,
            "ground_truth_sha256": sha256_file(gt),
            "protocol_sha256": sha256_file(proto) if proto.exists() else None,
            "protocol_note": None if proto.exists() else
            "NO PRE-REGISTERED PROTOCOL. The acceptance threshold cannot be shown to "
            "have been chosen before the result was known.",
        }

    def attach_attestation(self, path: str | Path) -> None:
        src = Path(path)
        if src.exists():
            (self.root / "attestation.json").write_bytes(src.read_bytes())
            self.pins["attestation_sha256"] = sha256_file(self.root / "attestation.json")

    # ---------------------------------------------------------------- manifest
    def write_manifest(self, *, claim: str = "same determinations") -> Path:
        manifest = {
            "bundle_version": BUNDLE_VERSION,
            "matter": self.matter,
            "run_id": self.run_id,
            "window": {"start": self.started, "end": _now()},
            "reproducibility_claim": claim,
            "claim_meaning": {
                "same determinations":
                    "Replaying this bundle yields the same coding decisions. Achieved by "
                    "greedy decoding (temperature 0), a pinned model/runtime, and the "
                    "captured prompt + retrieved context for every call.",
                "bit-exact":
                    "Replaying yields token-identical output. Requires a deterministic "
                    "backend; GPU inference is not bit-exact.",
            }[claim],
            "counts": {"queries": self._queries, "decisions": self._decisions},
            **self.pins,
        }
        p = self.root / "manifest.json"
        p.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (self.root / "VERIFY.md").write_text(
            VERIFY_MD.format(matter=self.matter, run_id=self.run_id, claim=claim),
            encoding="utf-8")
        return p

    # ------------------------------------------------------------------ verify
    def verify(self, *, replay=None) -> dict:
        """Check the bundle is complete and internally consistent.

        With `replay` (a callable taking the saved prompt text and returning an answer)
        it also re-runs every logged query and diffs the output — the actual
        "hand it to opposing counsel" proof.
        """
        findings: list[str] = []
        required = [
            ("manifest.json", "the pins"),
            ("corpus/catalog.jsonl", "the documents"),
            (f"runs/{self.run_id}/responses.jsonl", "what the model said"),
            (f"runs/{self.run_id}/retrieval.jsonl", "what the model saw"),
        ]
        for rel, why in required:
            if not (self.root / rel).exists():
                findings.append(f"MISSING {rel} ({why})")

        recommended = [
            ("corpus/exceptions.jsonl", "what did not process"),
            ("validation/protocol.md", "the pre-registered protocol"),
            ("validation/metrics.json", "the measured numbers"),
            ("attestation.json", "the egress claim"),
            ("decisions.jsonl", "the coding decisions"),
        ]
        for rel, why in recommended:
            if not (self.root / rel).exists():
                findings.append(f"INCOMPLETE {rel} ({why})")

        man_path = self.root / "manifest.json"
        manifest = json.loads(man_path.read_text()) if man_path.exists() else {}
        cat = self.root / "corpus" / "catalog.jsonl"
        if cat.exists() and manifest.get("corpus", {}).get("catalog_sha256"):
            if sha256_file(cat) != manifest["corpus"]["catalog_sha256"]:
                findings.append("TAMPER corpus/catalog.jsonl does not match its hash")
        if not (manifest.get("model") or {}).get("weights_sha256"):
            findings.append(
                "UNPINNED model has no weights hash — this review is not reproducible "
                "(legal auto-fail)")

        replayed = {"attempted": 0, "matched": 0, "differed": 0}
        if replay is not None:
            resp = self.run_dir / "responses.jsonl"
            if resp.exists():
                for line in resp.open(encoding="utf-8"):
                    row = json.loads(line)
                    prompt_file = self.root / row["prompt_path"]
                    if not prompt_file.exists():
                        findings.append(f"MISSING prompt {row['prompt_path']}")
                        continue
                    replayed["attempted"] += 1
                    got = replay(prompt_file.read_text(encoding="utf-8"))
                    if sha256_text(got) == row["answer_sha256"]:
                        replayed["matched"] += 1
                    else:
                        replayed["differed"] += 1

        ok = not any(f.startswith(("MISSING", "TAMPER", "UNPINNED")) for f in findings)
        result = {
            "bundle": str(self.root),
            "verified_at": _now(),
            "certified": ok and replayed["differed"] == 0,
            "complete": not findings,
            "findings": findings,
            "replay": replayed if replay is not None else "not attempted",
            "claim": manifest.get("reproducibility_claim"),
        }
        # The verification is itself an artifact. A bundle that says "I was checked, on
        # this date, by this code, and here is what was wrong" is worth more than one
        # that was checked and forgot.
        (self.root / "verification.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result


VERIFY_MD = """# VERIFY — {matter}

This bundle is a **defensible case snapshot**. It contains everything needed to re-run the
review recorded in `runs/{run_id}/` and compare the result.

## The claim

**{claim}.** See `manifest.json` → `claim_meaning` for exactly what that promises.

Read that carefully. "Same determinations" means replaying this bundle produces the same
coding decisions. It does **not** promise token-identical output: GPU inference is not
bit-exact, because the order of parallel floating-point reductions varies. For bit-exact
replay, run the verify pass on a deterministic backend (CPU, fixed configuration).

## How to re-run it

1. Install the pinned model named in `manifest.json` → `model`, and check its
   `weights_sha256` against what you installed. If the hash does not match, stop: you are
   not running the same model.
2. Confirm the runtime engine and version in `manifest.json` → `model.runtime`.
3. For each row in `runs/{run_id}/responses.jsonl`:
   - read the saved prompt at `prompt_path` (this is the **rendered** prompt, including
     the retrieved context — not a template)
   - send it with the decoding parameters in `manifest.json` → `model.decoding`
     (temperature 0, fixed seed)
   - compare the determination to the recorded `answer`
4. `runs/{run_id}/retrieval.jsonl` records which chunks were retrieved for each query, by
   id, offsets, and text hash — so you can confirm the model saw what we say it saw.

## What "match" means

* **Certified match** — every replayed query produced the same determination.
* **Differences** — report them. A difference is information, not a failure to hide. The
  usual causes are a different quantization of the same model, a different runtime
  version, or a non-deterministic backend.

## What this bundle does NOT claim

* It does not claim the determinations are *correct*. Correctness is addressed by
  `validation/metrics.json` — recall, elusion and precision against a blind sample.
* It does not claim no data ever left the host outside the attested window. See
  `attestation.json` → `scope_and_limits`.
"""


# ----------------------------------------------------------------------------- demo
if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        b = Bundle(Path(td) / "case-snapshot-DEMO", matter="DEMO")
        cat = Path(td) / "catalog.jsonl"
        cat.write_text('{"doc_id":"DOC-1"}\n{"doc_id":"DOC-2"}\n')
        b.pin_corpus(cat)
        b.pin_model({"chat_model": "qwen3:8b", "weights_sha256": None})
        b.pin_software()
        b.log_query(query="what is the cap?", chunks=[{"chunk_id": "c1", "doc_id": "DOC-1",
                                                       "text": "cap is $2,000,000"}],
                    prompt="<context>\n[1] cap is $2,000,000\n</context>\nQuestion: what is the cap?",
                    answer="The cap is $2,000,000 [1]", citations=["DOC-1#c1"])
        b.log_decision(doc_id="DOC-1", decision="responsive", rationale="cap [1]",
                       citations=["DOC-1#c1"])
        b.write_manifest()
        print(json.dumps(b.verify(), indent=2))
        print("\nreplay with a stub that returns the recorded answer:")
        print(json.dumps(b.verify(replay=lambda p: "The cap is $2,000,000 [1]"), indent=2))
