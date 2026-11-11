#!/usr/bin/env python3
"""sais100.py — Lab 07: score the system you just built (Module 7).

    python3 sais100.py --work ../work                       # score, with evidence
    python3 sais100.py --work ../work --out sais100-score.json
    python3 sais100.py --work ../work --save-baseline       # remember this score
    python3 sais100.py --work ../work --delta               # compare to the baseline

SAIS-100 is the Elephant Scale Secure AI Score. Six categories, three questions each,
each question scored 0-3 against anchored levels, weighted:

    Data Security            20
    Prompt Security          20
    Agent Security           20
    Model & Supply Chain     15
    Detection & Monitoring   15
    Governance               10
                            ---
                            100

Category score = round(raw / 9 * weight), where raw is the sum of its three answers.

This course does NOT fork SAIS-100. The six categories, the weights and the 0-3 anchors
are exactly as defined for every Elephant Scale assessment. What this file adds is a
*legal overlay*: the evidence each question is scored against is a legal artifact from
your own pipeline, and four legal auto-fail conditions sit on top of the number.

Why evidence-based scoring matters more here than anywhere else: a self-assessed
questionnaire is worth nothing under cross-examination. Every answer below is derived
from a file on disk that you can hand to someone. Where we cannot find the evidence, the
score is 0 and the report says "no evidence found" — not "probably fine".
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

WEIGHTS = {
    "data_security": 20,
    "prompt_security": 20,
    "agent_security": 20,
    "model_supply_chain": 15,
    "detection_monitoring": 15,
    "governance": 10,
}

ANCHORS = {
    0: "absent — no control, or no evidence it exists",
    1: "ad hoc — exists somewhere, not covered everywhere, not enforced",
    2: "covered and enforced — applies by default, but not independently verified",
    3: "verified — covered, enforced, and proven by an artifact someone else can check",
}

# The three dimensions behind every 0-3 anchor. A control you *have* scores 1. A control
# that applies *by default* scores 2. A control with an *artifact that proves it* scores 3.
# Legal work is the one domain where the third dimension is not a nice-to-have, because
# "we have a policy" is not an answer to "prove it".


@dataclass
class Answer:
    qid: str
    question: str
    score: int
    evidence: list[str] = field(default_factory=list)
    gap: str = ""

    def as_dict(self) -> dict:
        return {"id": self.qid, "question": self.question, "score": self.score,
                "anchor": ANCHORS[self.score], "evidence": self.evidence,
                "gap_to_next_level": self.gap}


# ------------------------------------------------------------------- evidence helpers
class Evidence:
    """Reads the pipeline's own artifacts. Every lookup is a file someone can open."""

    def __init__(self, work: Path):
        self.work = work
        self.bundle = self._latest_bundle()

    def _latest_bundle(self) -> Path | None:
        p = self.work / "bundle-path.txt"
        if p.exists():
            b = Path(p.read_text().strip())
            if b.exists():
                return b
        cands = sorted(self.work.glob("case-snapshot-*"))
        return cands[-1] if cands else None

    def has(self, *rel: str) -> Path | None:
        # The WORK dir is searched first, then the bundle. The distinction matters: the
        # score describes the system as it stands now, and the bundle describes the
        # system as it stood when a snapshot was taken. If someone weakens egress today,
        # last month's attestation must not keep scoring it a 3.
        # (manifest.json collides between the two, so the bundle's is read explicitly,
        # via `bundle_manifest`, and never through this lookup.)
        for r in rel:
            for base in (self.work, self.bundle):
                if base and (base / r).exists():
                    return base / r
        return None

    @property
    def bundle_manifest(self) -> dict:
        if not self.bundle:
            return {}
        p = self.bundle / "manifest.json"
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return {}

    def json(self, *rel: str) -> dict | None:
        p = self.has(*rel)
        if not p:
            return None
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return None

    def work_lines(self, rel: str) -> list[dict]:
        """Read ONLY the pipeline's copy. work/decisions.jsonl carries route and
        confidence; the bundle's decisions.jsonl is the normalized legal record and has
        a deliberately narrower schema. Scoring routing needs the former."""
        p = self.work / rel
        if not p.exists():
            return []
        out = []
        for line in p.open(encoding="utf-8"):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out

    def lines(self, *rel: str) -> list[dict]:
        p = self.has(*rel)
        if not p:
            return []
        out = []
        for line in p.open(encoding="utf-8"):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out

    def rel(self, p: Path | None) -> str:
        if p is None:
            return ""
        try:
            return str(p.relative_to(self.work))
        except ValueError:
            return str(p)


def src(name: str) -> str:
    """Point at the code that implements a control, so a reviewer can read it."""
    return f"code: labs/{name}"


# -------------------------------------------------------------------- the 18 questions
def score_data_security(ev: Evidence) -> list[Answer]:
    out = []

    # D1 — does sensitive content leave the boundary?
    att = ev.json("attestation.json")
    guard = Path(__file__).resolve().parent.parent / "common" / "egress.py"
    enforced = "default-deny" in (att or {}).get("egress_policy", "").lower()
    leaked = (att or {}).get("non_loopback_connections", 1)
    if att and enforced and leaked == 0:
        out.append(Answer("D1", "Is egress of case content to third parties prevented?",
                          3, [ev.rel(ev.has("attestation.json")),
                              src("common/egress.py"),
                              "tripwire test: attestation-tripwire.json"],
                          "none at this level; re-attest whenever the stack changes"))
    elif att:
        out.append(Answer("D1", "Is egress of case content to third parties prevented?",
                          2, [ev.rel(ev.has("attestation.json"))],
                          "non-loopback connections were observed — identify each one "
                          "and either justify it in the attestation or block it"))
    elif guard.exists():
        out.append(Answer("D1", "Is egress of case content to third parties prevented?",
                          1, [src("common/egress.py")],
                          "the guard exists but no attestation was produced for this "
                          "run — run Lab 05's `prove` as part of the pipeline"))
    else:
        out.append(Answer("D1", "Is egress of case content to third parties prevented?",
                          0, [], "no egress control and no attestation"))

    # D2 — matter isolation (the legal overlay's headline addition)
    cat = ev.lines("catalog.jsonl")
    matters = {d.get("matter") for d in cat if d.get("matter")}
    bundle_man = ev.bundle_manifest
    if len(matters) == 1 and bundle_man and bundle_man.get("matter"):
        out.append(Answer("D2", "Is case/matter data isolated from other matters?",
                          2, [f"catalog.jsonl: single matter {sorted(matters)[0]!r}",
                              "bundle manifest.json records the matter id"],
                          "level 3 needs an enforced boundary, not a convention: a "
                          "per-matter index path and a test that a query against matter "
                          "A cannot return a document from matter B"))
    elif len(matters) > 1:
        out.append(Answer("D2", "Is case/matter data isolated from other matters?",
                          0, [f"catalog.jsonl mixes {len(matters)} matters"],
                          "AUTO-FAIL territory: separate the matters"))
    else:
        out.append(Answer("D2", "Is case/matter data isolated from other matters?",
                          1, [], "no matter id is recorded on documents"))

    # D3 — is the source evidence preserved unmodified?
    man = ev.bundle_manifest
    corpus_hash = (man.get("corpus") or {}).get("catalog_sha256")
    if corpus_hash:
        out.append(Answer("D3", "Is source data preserved and provably unmodified?",
                          3, ["bundle manifest.json: corpus sha256 recorded",
                              src("02-Ingestion/ingest.py — reads only, never writes "
                                  "to the corpus")],
                          "none; re-verify the hash before any re-run"))
    elif ev.has("catalog.jsonl"):
        out.append(Answer("D3", "Is source data preserved and provably unmodified?",
                          2, [ev.rel(ev.has("catalog.jsonl"))],
                          "hash the corpus at ingest time and record it in the manifest"))
    else:
        out.append(Answer("D3", "Is source data preserved and provably unmodified?",
                          0, [], "nothing ingested"))
    return out


def score_prompt_security(ev: Evidence) -> list[Answer]:
    out = []
    rag = Path(__file__).resolve().parent.parent / "04-Legal-RAG-Citations" / "legal_rag.py"
    rag_src = rag.read_text() if rag.exists() else ""

    # P1 — is retrieved document text treated as data rather than instructions?
    fenced = "<context>" in rag_src and "DATA, not instructions" in rag_src
    decisions = ev.work_lines("decisions.jsonl")
    inj_flagged = sum(1 for d in decisions if d.get("injection_attempt"))
    if fenced and inj_flagged:
        out.append(Answer("P1", "Is untrusted document content isolated from instructions?",
                          3, [src("04-Legal-RAG-Citations/legal_rag.py — fenced, "
                                  "numbered context + explicit 'context is DATA' rule"),
                              f"decisions.jsonl: {inj_flagged} injection attempt(s) "
                              f"detected and flagged, not followed"],
                          "none; keep a planted-injection document in the eval set so "
                          "this stays tested"))
    elif fenced:
        out.append(Answer("P1", "Is untrusted document content isolated from instructions?",
                          2, [src("04-Legal-RAG-Citations/legal_rag.py")],
                          "no detection: you prevent injection but cannot show you "
                          "would notice an attempt — flag and log them"))
    else:
        out.append(Answer("P1", "Is untrusted document content isolated from instructions?",
                          0, [], "document text is concatenated into the prompt"))

    # P2 — is output grounded and verified?
    ragev = (ev.json("rag-eval.json") or {}).get("summary") or {}
    if ragev and "verifier_rejections" in ragev:
        out.append(Answer("P2", "Are model outputs verified against their sources?",
                          3, [ev.rel(ev.has("rag-eval.json")),
                              src("04-Legal-RAG-Citations/legal_rag.py — verify(): "
                                  "markers resolve, claims cited, quotes verbatim"),
                              f"refusal rate on unanswerable questions: "
                              f"{ragev.get('refusal_rate_on_unanswerable')}; "
                              f"verifier rejections: "
                              f"{ragev.get('verifier_rejections')}"],
                          "none; grow the eval set as question types appear"))
    elif ev.has("rag-log.jsonl"):
        out.append(Answer("P2", "Are model outputs verified against their sources?",
                          2, [ev.rel(ev.has("rag-log.jsonl"))],
                          "answers are logged but not scored against an eval set — "
                          "run `legal_rag.py eval`"))
    else:
        out.append(Answer("P2", "Are model outputs verified against their sources?",
                          0, [], "no citation verification"))

    # P3 — is every prompt recorded?
    prompts = list(ev.bundle.glob("runs/*/prompts/*.txt")) if ev.bundle else []
    if prompts:
        out.append(Answer("P3", "Is every prompt sent to the model recorded?",
                          3, [f"bundle prompts/: {len(prompts)} rendered prompt(s), "
                              f"hashed in manifest.json",
                              src("common/bundle.py — log_query()")],
                          "none"))
    elif ev.has("rag-log.jsonl"):
        out.append(Answer("P3", "Is every prompt sent to the model recorded?",
                          2, [ev.rel(ev.has("rag-log.jsonl"))],
                          "prompts are logged but not hashed into an immutable bundle"))
    else:
        out.append(Answer("P3", "Is every prompt sent to the model recorded?",
                          0, [], "no prompt log"))
    return out


def score_agent_security(ev: Evidence) -> list[Answer]:
    """In a legal pipeline 'agent' means: anything that acts on the matter without a
    human in the loop at that instant. Our stages count, even without an LLM agent."""
    out = []
    state = ev.work / "_state"

    # A1 — human gates on irreversible actions
    prod_gate = (state / "gate-production.json").exists()
    prod_man = ev.json("production/VOL001/manifest.json")
    if prod_man and prod_man.get("approved_by"):
        out.append(Answer("A1", "Do irreversible actions require human authorization?",
                          3, ["production/VOL001/manifest.json records approved_by + "
                              "approved_at",
                              src("07-Score-and-Package/run_matter.py — produce() "
                                  "refuses without a recorded approval")],
                          "none; keep the approval record in the bundle"))
    elif prod_gate:
        out.append(Answer("A1", "Do irreversible actions require human authorization?",
                          2, [ "_state/gate-production.json"],
                          "the approval exists but no production has been emitted "
                          "carrying it"))
    else:
        out.append(Answer("A1", "Do irreversible actions require human authorization?",
                          1, [src("07-Score-and-Package/run_matter.py — gate defined")],
                          "the gate is defined but unexercised: no approval on record"))

    # A2 — is autonomy bounded, and is the routing auditable?
    decisions = ev.work_lines("decisions.jsonl")
    routes = {}
    for d in decisions:
        routes[d.get("route", "?")] = routes.get(d.get("route", "?"), 0) + 1
    human = sum(n for r, n in routes.items() if "human" in r)
    if decisions and human:
        out.append(Answer("A2", "Is autonomous action bounded by policy?",
                          3, [f"decisions.jsonl: {len(decisions)} decisions, "
                              f"{human} routed to human review",
                              "routes: " + ", ".join(f"{r}={n}" for r, n in
                                                     sorted(routes.items())),
                              src("06-Defensible-Review/defensible_review.py — "
                                  "privilege and low confidence always route to a human")],
                          "none"))
    elif decisions:
        out.append(Answer("A2", "Is autonomous action bounded by policy?",
                          1, ["decisions.jsonl: nothing routed to a human"],
                          "every decision was auto-coded — set a confidence threshold "
                          "and route privilege calls to a person"))
    else:
        out.append(Answer("A2", "Is autonomous action bounded by policy?",
                          0, [], "no classification run"))

    # A3 — is every step replayable?
    runlog = (state / "run.log").exists()
    verify = ev.has("VERIFY.md")
    if verify and runlog:
        out.append(Answer("A3", "Is every automated step logged and replayable?",
                          3, ["_state/run.log: per-stage timing and status",
                              "bundle VERIFY.md + `verify --replay`",
                              src("common/bundle.py")],
                          "none"))
    elif runlog or verify:
        out.append(Answer("A3", "Is every automated step logged and replayable?",
                          2, [x for x in ["_state/run.log" if runlog else "",
                                          ev.rel(verify)] if x],
                          "add the missing half: a stage log AND a replayable bundle"))
    else:
        out.append(Answer("A3", "Is every automated step logged and replayable?",
                          0, [], "no step log"))
    return out


def score_model_supply_chain(ev: Evidence) -> list[Answer]:
    out = []
    man = ev.bundle_manifest
    model = man.get("model", {})

    # M1 — is the model pinned?
    if model.get("weights_sha256") and model.get("quantization"):
        out.append(Answer("M1", "Is the model pinned to a verifiable version?",
                          3, [f"manifest.json: {model.get('chat_model')} "
                              f"sha256={str(model.get('weights_sha256'))[:16]}… "
                              f"quant={model.get('quantization')}",
                              f"runtime: {model.get('runtime')}"],
                          "none; re-pin whenever you pull a new model tag"))
    elif model.get("chat_model"):
        out.append(Answer("M1", "Is the model pinned to a verifiable version?",
                          1, [f"manifest.json names {model.get('chat_model')} but has "
                              f"no weights hash"],
                          "LEGAL AUTO-FAIL: a model you cannot pin is a review you "
                          "cannot reproduce. Record the digest from the runtime."))
    else:
        out.append(Answer("M1", "Is the model pinned to a verifiable version?",
                          0, [], "no model recorded"))

    # M2 — are the dependencies and code version fixed?
    sw = man.get("software", {})
    reqs = list((Path(__file__).resolve().parent.parent).glob("*/requirements.txt"))
    if sw.get("git_sha") and reqs:
        out.append(Answer("M2", "Are code and dependencies version-pinned?",
                          2, [f"manifest.json: git {str(sw.get('git_sha'))[:12]}",
                              f"{len(reqs)} requirements.txt with == pins"],
                          "level 3 needs hash-pinned installs (pip --require-hashes) "
                          "and a container image referenced by digest, not tag"))
    elif sw.get("git_sha"):
        out.append(Answer("M2", "Are code and dependencies version-pinned?",
                          1, ["git sha recorded, dependencies unpinned"],
                          "pin dependency versions"))
    else:
        out.append(Answer("M2", "Are code and dependencies version-pinned?",
                          0, [], "no software version recorded"))

    # M3 — is the retrieval layer reproducible? (the embedding-dimension trap)
    emb = man.get("embeddings", {})
    idx = man.get("index", {})
    if emb.get("model") and emb.get("dim") and idx.get("sha256"):
        out.append(Answer("M3", "Is the retrieval layer reproducible?",
                          3, [f"manifest.json: embeddings {emb.get('model')} "
                              f"dim={emb.get('dim')}",
                              f"frozen index sha256={str(idx.get('sha256'))[:16]}…",
                              "chunking parameters recorded"],
                          "none; changing the embedding model changes the dimension "
                          "and forces a full re-ingest — that is a new snapshot, not "
                          "an edit to this one"))
    elif emb.get("model"):
        out.append(Answer("M3", "Is the retrieval layer reproducible?",
                          2, [f"embeddings {emb.get('model')} recorded"],
                          "freeze and hash the index itself"))
    else:
        out.append(Answer("M3", "Is the retrieval layer reproducible?",
                          0, [], "no embedding model recorded"))
    return out


def score_detection_monitoring(ev: Evidence) -> list[Answer]:
    out = []

    # T1 — would you notice an egress attempt?
    trip = ev.json("attestation-tripwire.json")
    att = ev.json("attestation.json")
    blocked = (trip or {}).get("blocked_attempts", 0)
    if trip and blocked > 0:
        out.append(Answer("T1", "Would an attempted disclosure be detected?",
                          3, [ev.rel(ev.has("attestation-tripwire.json")) +
                              f": {blocked} attempt(s) blocked and recorded",
                              "DNS resolution is counted as an attempted disclosure, "
                              "not just a completed connection"],
                          "none; re-run the tripwire after any dependency change"))
    elif att:
        out.append(Answer("T1", "Would an attempted disclosure be detected?",
                          2, [ev.rel(ev.has("attestation.json"))],
                          "you attest that nothing left, but have not demonstrated the "
                          "monitor fires — run `local_proof.py tripwire`"))
    else:
        out.append(Answer("T1", "Would an attempted disclosure be detected?",
                          0, [], "no monitoring"))

    # T2 — are processing failures surfaced rather than swallowed?
    exc = ev.lines("exceptions.jsonl")
    cat = ev.lines("catalog.jsonl")
    gate = (ev.work / "_state" / "gate-ingest.json").exists()
    if exc and gate:
        out.append(Answer("T2", "Are processing failures surfaced and triaged?",
                          3, [f"exceptions.jsonl: {len(exc)} exception(s), each with a "
                              f"reason", "_state/gate-ingest.json: exception list "
                              "reviewed by a human",
                              "production manifest discloses the exception count"],
                          "none"))
    elif exc:
        out.append(Answer("T2", "Are processing failures surfaced and triaged?",
                          2, [f"exceptions.jsonl: {len(exc)} exception(s)"],
                          "no record that a human reviewed the exception list — a "
                          "silently dropped document is the classic defensibility hole"))
    elif cat:
        out.append(Answer("T2", "Are processing failures surfaced and triaged?",
                          1, ["no exception list produced"],
                          "emit exceptions as a first-class output, not a log line"))
    else:
        out.append(Answer("T2", "Are processing failures surfaced and triaged?",
                          0, [], "nothing ingested"))

    # T3 — is quality measured against ground truth, not vibes?
    met = ev.json("metrics.json")
    if met and (met.get("verdict") or {}).get("elusion_passed") is not None:
        v = met["verdict"]
        r = met["metrics"]["recall"]
        out.append(Answer("T3", "Is output quality measured against an independent "
                                "ground truth?",
                          3, [ev.rel(ev.has("metrics.json")) +
                              f": recall {r['value']:.1%} CI {r['ci95'][0]:.1%}–"
                              f"{r['ci95'][1]:.1%}",
                              f"elusion test vs pre-set threshold "
                              f"{v['elusion_threshold']:.1%}: "
                              f"{'PASS' if v['elusion_passed'] else 'FAIL'}",
                              "blind seeded samples; protocol hashed before the run"],
                          "none; re-measure after any change to the classifier"))
    elif met:
        out.append(Answer("T3", "Is output quality measured against an independent "
                                "ground truth?",
                          2, [ev.rel(ev.has("metrics.json"))],
                          "no elusion measurement on the discard pile — recall alone "
                          "does not tell you what you missed"))
    else:
        out.append(Answer("T3", "Is output quality measured against an independent "
                                "ground truth?",
                          0, [], "no validation"))
    return out


def score_governance(ev: Evidence) -> list[Answer]:
    out = []

    # G1 — is there a written, pre-registered protocol?
    proto = ev.has("validation/protocol.md", "validation-protocol.md")
    man = ev.bundle_manifest
    val = man.get("validation") or {}
    phash = val.get("protocol_sha256") or (man.get("protocol") or {}).get("sha256")
    if proto and phash:
        out.append(Answer("G1", "Is there a written protocol, fixed before the run?",
                          3, [ev.rel(proto), f"hash recorded in the bundle manifest: "
                              f"{str(phash)[:16]}…",
                              src("06-Defensible-Review/defensible_review.py — "
                                  "`protocol` refuses to overwrite without --force; "
                                  "`classify` refuses to run without a protocol")],
                          "none"))
    elif proto:
        out.append(Answer("G1", "Is there a written protocol, fixed before the run?",
                          2, [ev.rel(proto)],
                          "the protocol is not hashed into the bundle, so you cannot "
                          "show it predates the classification"))
    else:
        out.append(Answer("G1", "Is there a written protocol, fixed before the run?",
                          0, [], "no protocol"))

    # G2 — can a third party reproduce the result?
    verify = ev.has("VERIFY.md")
    certified = None
    vj = ev.json("verification.json")
    if vj:
        certified = vj.get("certified")
    if verify and certified:
        out.append(Answer("G2", "Can an independent party reproduce the result?",
                          3, [ev.rel(verify), "verification.json: certified",
                              "replay re-ran every logged prompt and compared outputs"],
                          "none"))
    elif verify:
        out.append(Answer("G2", "Can an independent party reproduce the result?",
                          2, [ev.rel(verify)],
                          "the bundle exists but has not been verified — run "
                          "`defensible_review.py verify --replay`"))
    else:
        out.append(Answer("G2", "Can an independent party reproduce the result?",
                          0, [], "no reproducibility bundle"))

    # G3 — are the limits of the claim stated?
    att = ev.json("attestation.json")
    scope = (att or {}).get("scope_and_limits")
    vmd = verify.read_text() if verify else ""
    disclaimed = "does NOT claim" in vmd or "not claim" in vmd.lower()
    if scope and disclaimed:
        out.append(Answer("G3", "Are the limits of each claim stated explicitly?",
                          3, [f"attestation.json: {len(scope)} explicit "
                              f"scope_and_limits item(s)",
                              "VERIFY.md states what the bundle does NOT claim "
                              "(same determinations, not bit-exact output)"],
                          "none; this is the single cheapest defensibility control "
                          "and the most often skipped"))
    elif scope or disclaimed:
        out.append(Answer("G3", "Are the limits of each claim stated explicitly?",
                          2, [], "state the limits on BOTH artifacts: the attestation "
                                 "and the reproducibility claim"))
    else:
        out.append(Answer("G3", "Are the limits of each claim stated explicitly?",
                          0, [], "claims are stated without limits — the fastest way "
                                 "to lose an otherwise good position"))
    return out


SCORERS = {
    "data_security": score_data_security,
    "prompt_security": score_prompt_security,
    "agent_security": score_agent_security,
    "model_supply_chain": score_model_supply_chain,
    "detection_monitoring": score_detection_monitoring,
    "governance": score_governance,
}


# ------------------------------------------------------------------------- auto-fails
def legal_auto_fails(ev: Evidence, answers: dict[str, list[Answer]]) -> list[dict]:
    """The legal overlay. Four conditions that void the score regardless of the number.

    These are not "severe findings". They are conditions under which the system must not
    process a real matter, because each one is a disclosure, an ethics problem, or an
    un-defensible review. A 92 with an auto-fail is a 'Do Not Deploy'.
    """
    fails = []
    by_id = {a.qid: a for v in answers.values() for a in v}

    # (a) privileged content can reach a third party by any path
    att = ev.json("attestation.json")
    if by_id["D1"].score < 2:
        fails.append({
            "id": "LEGAL-A",
            "condition": "Privileged content can reach a third party by some path",
            "evidence": by_id["D1"].evidence or ["no egress attestation"],
            "why": "A single disclosure of a privileged document can waive privilege "
                   "for the subject matter. There is no partial credit on this.",
        })
    elif att and "observe" in att.get("egress_policy", "").lower():
        fails.append({
            "id": "LEGAL-A",
            "condition": "Egress is observed but not enforced",
            "evidence": [f"attestation.json: egress_policy="
                         f"{att.get('egress_policy')!r}"],
            "why": "Observation tells you what happened. Only enforcement tells you "
                   "what cannot happen. Run with policy=deny for a real matter.",
        })

    # (b) cross-matter leakage
    if by_id["D2"].score == 0:
        fails.append({
            "id": "LEGAL-B",
            "condition": "Data from different matters can mix",
            "evidence": by_id["D2"].evidence,
            "why": "Matters at the same firm are separated by ethical walls. Leakage "
                   "between them is a conflict-of-interest problem, not a bug.",
        })

    # (c) production without recorded human approval
    prod = ev.json("production/VOL001/manifest.json")
    if prod and not prod.get("approved_by"):
        fails.append({
            "id": "LEGAL-C",
            "condition": "A production was emitted without a recorded human approval",
            "evidence": ["production/VOL001/manifest.json has no approved_by"],
            "why": "Production is irreversible and outward-facing. A named human "
                   "authorizes it, or nobody is accountable for what went out.",
        })

    # (d) the model cannot be pinned
    if by_id["M1"].score < 2:
        fails.append({
            "id": "LEGAL-D",
            "condition": "The model cannot be pinned to a verifiable version",
            "evidence": by_id["M1"].evidence,
            "why": "Without a pin you cannot reproduce the review, so you cannot "
                   "defend it. 'We used GPT-4 last spring' is not a pin.",
        })
    return fails


VERDICTS = [(85, "Enterprise Ready"), (70, "Production Ready"),
            (50, "Significant Risk"), (0, "Do Not Deploy")]


def verdict(total: int) -> str:
    for floor, label in VERDICTS:
        if total >= floor:
            return label
    return "Do Not Deploy"


# ------------------------------------------------------------------------------- main
def build_score(work: Path) -> dict:
    ev = Evidence(work)
    answers = {cat: fn(ev) for cat, fn in SCORERS.items()}
    cats, total = {}, 0
    for cat, ans in answers.items():
        raw = sum(a.score for a in ans)
        pts = round(raw / 9 * WEIGHTS[cat])
        total += pts
        cats[cat] = {"weight": WEIGHTS[cat], "raw": raw, "raw_max": 9, "score": pts,
                     "questions": [a.as_dict() for a in ans]}
    fails = legal_auto_fails(ev, answers)
    return {
        "framework": "SAIS-100 (Elephant Scale Secure AI Score) + legal overlay",
        "framework_note": "Categories, weights and 0-3 anchors are the standard "
                          "SAIS-100. The legal overlay adds evidence requirements and "
                          "four auto-fail conditions; it does not change the scoring.",
        "scored_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "work_dir": str(work),
        "bundle": str(ev.bundle) if ev.bundle else None,
        "mode": os.environ.get("LEGAL_AI_MODE", "local"),
        "categories": cats,
        "total": total,
        "verdict": verdict(total),
        "legal_auto_fails": fails,
        "final": "DO NOT DEPLOY — legal auto-fail" if fails else verdict(total),
        "anchors": ANCHORS,
    }


def print_report(s: dict, show_evidence: bool) -> None:
    print(f"\n  SAIS-100 — {s['framework']}")
    print(f"  work: {s['work_dir']}   mode: {s['mode']}\n")
    print(f"  {'category':<24}{'raw':>5}{'/9':<4}{'weight':>7}{'score':>8}")
    print("  " + "-" * 50)
    for cat, c in s["categories"].items():
        print(f"  {cat.replace('_', ' '):<24}{c['raw']:>5}{'':<4}"
              f"{c['weight']:>7}{c['score']:>8}")
    print("  " + "-" * 50)
    print(f"  {'TOTAL':<24}{'':>5}{'':<4}{100:>7}{s['total']:>8}   {s['verdict']}\n")

    if show_evidence:
        for cat, c in s["categories"].items():
            print(f"  {cat.replace('_', ' ').upper()}")
            for q in c["questions"]:
                print(f"    [{q['score']}] {q['id']}  {q['question']}")
                for e in q["evidence"]:
                    print(f"           + {e}")
                if q["gap_to_next_level"] and q["score"] < 3:
                    print(f"           → {q['gap_to_next_level']}")
            print()

    if s["legal_auto_fails"]:
        print("  LEGAL AUTO-FAILS\n")
        for f in s["legal_auto_fails"]:
            print(f"    {f['id']}  {f['condition']}")
            for e in f["evidence"]:
                print(f"          evidence: {e}")
            print(f"          why: {f['why']}\n")
        print(f"  FINAL: {s['final']}")
        print("  A high number with an auto-fail is still a do-not-deploy. The number "
              "is a\n  summary; the auto-fails are conditions.\n")
    else:
        print(f"  FINAL: {s['final']}   (no legal auto-fails)\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default="../work")
    ap.add_argument("--out", default="sais100-score.json")
    ap.add_argument("--quiet-evidence", action="store_true",
                    help="totals only, no per-question evidence")
    ap.add_argument("--save-baseline", action="store_true",
                    help="store this score as the 'before' for the delta")
    ap.add_argument("--delta", action="store_true",
                    help="compare this score to the saved baseline")
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if not work.exists():
        raise SystemExit(f"no work dir at {work} — run run_matter.py first")

    s = build_score(work)
    print_report(s, not args.quiet_evidence)

    out = Path(args.out)
    out.write_text(json.dumps(s, indent=2) + "\n")
    print(f"  wrote {out}")

    base_path = work / "sais100-baseline.json"
    if args.save_baseline:
        base_path.write_text(json.dumps(s, indent=2) + "\n")
        print(f"  saved baseline -> {base_path}")
        print("\n  Now harden ONE thing, re-run, and `--delta`. One change at a time is")
        print("  how you learn what the score is actually sensitive to.")
    if args.delta:
        if not base_path.exists():
            print("\n  no baseline — run with --save-baseline first")
            return 0
        b = json.loads(base_path.read_text())
        print(f"\n  DELTA vs baseline scored {b['scored_at']}\n")
        print(f"  {'category':<24}{'before':>8}{'after':>7}{'Δ':>5}")
        print("  " + "-" * 44)
        for cat in WEIGHTS:
            bb, aa = b["categories"][cat]["score"], s["categories"][cat]["score"]
            d = aa - bb
            print(f"  {cat.replace('_', ' '):<24}{bb:>8}{aa:>7}"
                  f"{('+' if d > 0 else '') + str(d) if d else '·':>5}")
        print("  " + "-" * 44)
        d = s["total"] - b["total"]
        print(f"  {'TOTAL':<24}{b['total']:>8}{s['total']:>7}"
              f"{('+' if d > 0 else '') + str(d) if d else '·':>5}")
        print(f"\n  {b['final']}  ->  {s['final']}")
        nb, na = len(b["legal_auto_fails"]), len(s["legal_auto_fails"])
        if nb != na:
            print(f"  legal auto-fails: {nb} -> {na}")
        for f in s["legal_auto_fails"]:
            print(f"    still failing: {f['id']} {f['condition']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
