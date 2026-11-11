#!/usr/bin/env python3
"""audit.py — Lab 12: a verified SAIS-100 governance audit (Module 12).

    python3 audit.py artifacts --work ../work          # the nine, present or missing
    python3 audit.py audit     --work ../work          # verified score, evidence cited
    python3 audit.py findings  --work ../work          # the one-page report
    python3 audit.py delta     --work ../work          # after you apply a fix

The difference between this and Lab 07's `sais100.py` is one word: **verified**.

Lab 07 scored your own system from your own artifacts, and it trusted them. An auditor
does not. Here every sub-score must cite evidence that an auditor can independently
open — a path, a line number, a test result, a log sample — and the audit **re-runs the
checks it can** rather than reading a conclusion someone else wrote.

Three rules this file enforces:

  1. **"We're careful" scores 0.** No evidence, no points. A control nobody can show you
     is indistinguishable from one that does not exist.
  2. **Evidence must be independently resolvable.** Not "see attestation.json" but
     "attestation.json:egress_policy == 'default-deny; loopback only'", so the auditor
     checks the claim rather than the citation.
  3. **A check that could not run is not a pass.** It is recorded as UNVERIFIED, which is
     different from 0 and different from 3, and it is the row an honest report leads with.

Swap systems with another pair if you can. Auditing somebody else's system is far more
instructive than auditing your own, and it is what the job actually looks like.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
sys.path.insert(0, str(LABS / "07-Score-and-Package"))
import sais100  # noqa: E402  the scorer under audit — we re-check it, we do not trust it

WEIGHTS = sais100.WEIGHTS
ANCHORS = sais100.ANCHORS


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ====================================================== the nine governance artifacts
NINE = [
    {"n": 1, "name": "Written AI use policy",
     "what": "what is allowed, by whom, with what data",
     "source": "the organization — NOT your pipeline",
     "paths": ["AI-USE-POLICY.md", "docs/ai-use-policy.md", "../AI-USE-POLICY.md"],
     "emitted_by_system": False},
    {"n": 2, "name": "System description",
     "what": "data flows, every hop, every component",
     "source": "your architecture doc; the attestation's ai_components is a start",
     "paths": ["SYSTEM-DESCRIPTION.md", "attestation.json"],
     "emitted_by_system": True},
    {"n": 3, "name": "Egress attestation per matter",
     "what": "what the system could and did reach",
     "source": "Module 5 / Lab 05",
     "paths": ["attestation.json"], "emitted_by_system": True},
    {"n": 4, "name": "Validation protocol, pre-registered, plus results",
     "what": "the thresholds, fixed before the run, and what was measured",
     "source": "Module 6 / Lab 06",
     "paths": ["validation-protocol.md", "metrics.json"], "emitted_by_system": True},
    {"n": 5, "name": "Reproducibility bundle that replays",
     "what": "someone else re-runs the review and gets the same determinations",
     "source": "Module 6 / Lab 06",
     "paths": ["bundle-path.txt"], "emitted_by_system": True},
    {"n": 6, "name": "Audit trail per matter",
     "what": "prompts, retrieved context, decisions, overrides",
     "source": "Modules 6-7",
     "paths": ["rag-log.jsonl", "decisions.jsonl"], "emitted_by_system": True},
    {"n": 7, "name": "Model inventory (an AI SBOM)",
     "what": "name, version, hash, quantization, provenance",
     "source": "Module 7",
     "paths": ["bundle:manifest.json"], "emitted_by_system": True},
    {"n": 8, "name": "Access-control and ethical-wall evidence",
     "what": "a test that matter A cannot reach matter B, not a policy saying so",
     "source": "your deployment",
     "paths": ["ETHICAL-WALL-TEST.md", "matter-isolation-test.json"],
     "emitted_by_system": False},
    {"n": 9, "name": "Incident and exception records",
     "what": "including the processing exception list",
     "source": "Modules 2, 7",
     "paths": ["exceptions.jsonl"], "emitted_by_system": True},
]


def resolve(work: Path, spec: str) -> Path | None:
    if spec.startswith("bundle:"):
        ptr = work / "bundle-path.txt"
        if not ptr.exists():
            return None
        b = Path(ptr.read_text().strip())
        p = b / spec.split(":", 1)[1]
        return p if p.exists() else None
    p = (work / spec).resolve()
    return p if p.exists() else None


def cmd_artifacts(work: Path) -> int:
    print(f"\n  THE NINE GOVERNANCE ARTIFACTS — {work}\n")
    present, missing = [], []
    for a in NINE:
        hit = next((resolve(work, s) for s in a["paths"]
                    if resolve(work, s) is not None), None)
        (present if hit else missing).append(a)
        mark = "PRESENT" if hit else "MISSING"
        print(f"  [{mark:<7}] {a['n']}. {a['name']}")
        print(f"             {a['what']}")
        if hit:
            try:
                rel = hit.relative_to(work)
            except ValueError:
                rel = hit
            print(f"             -> {rel}")
        else:
            print(f"             -> none of: {', '.join(a['paths'])}")
            print(f"             gap: {a['source']}")
    rows = [{"n": a["n"], "name": a["name"],
             "present": a in present,
             "emitted_by_system": a["emitted_by_system"],
             "gap": None if a in present else a["source"]} for a in NINE]
    (work / "audit-artifacts.json").write_text(
        json.dumps({"at": now(), "present": len(present), "missing": len(missing),
                    "artifacts": rows}, indent=2) + "\n")
    print(f"\n  present: {len(present)}/9    missing: {len(missing)}/9")
    sys_missing = [a for a in missing if a["emitted_by_system"]]
    org_missing = [a for a in missing if not a["emitted_by_system"]]
    if sys_missing:
        print(f"\n  Missing and YOUR SYSTEM SHOULD EMIT IT ({len(sys_missing)}):")
        for a in sys_missing:
            print(f"      {a['n']}. {a['name']}  <- {a['source']}")
    if org_missing:
        print(f"\n  Missing and it is an ORGANIZATIONAL document, not a program output "
              f"({len(org_missing)}):")
        for a in org_missing:
            print(f"      {a['n']}. {a['name']}")
        print("\n  Do not fake these by generating a file. #1 is a policy somebody with")
        print("  authority signs, and #8 is a TEST you run against a real second matter.")
        print("  An audit that accepts a generated policy document has taught the")
        print("  organization that generating documents is how you pass audits.")
    print(f"\n  The reframe that matters: {sum(1 for a in NINE if a['emitted_by_system'])}"
          f" of the nine are files your SYSTEM EMITS, not documents somebody writes")
    print("  afterwards. Build them as outputs and an audit is a morning. Write them")
    print("  afterwards and it is a quarter.")
    print(f"\n  wrote {work / 'audit-artifacts.json'}")
    return 0


# ================================================================ independent re-checks
@dataclass
class Check:
    """One independently re-run verification, with its command and its result."""
    cid: str
    question: str
    how: str
    passed: bool | None          # None = could not run
    evidence: list[str] = field(default_factory=list)
    note: str = ""

    def row(self) -> dict:
        return {"id": self.cid, "question": self.question, "method": self.how,
                "result": "PASS" if self.passed else
                          ("UNVERIFIED" if self.passed is None else "FAIL"),
                "evidence": self.evidence, "note": self.note}


def recheck_bundle_replays(work: Path) -> Check:
    """Do not read `certified: true`. Re-run the verification."""
    ptr = work / "bundle-path.txt"
    if not ptr.exists():
        return Check("V1", "Does the reproducibility bundle actually replay?",
                     "re-run defensible_review.py verify --replay", None,
                     note="no bundle — nothing to verify")
    cmd = [sys.executable, "defensible_review.py", "verify", "--work", str(work),
           "--corpus", str(LABS / "assets" / "corpus"), "--replay"]
    try:
        r = subprocess.run(cmd, cwd=LABS / "06-Defensible-Review",
                           capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.SubprocessError) as e:
        return Check("V1", "Does the reproducibility bundle actually replay?",
                     " ".join(cmd[1:]), None, note=f"could not run: {e}")
    out = r.stdout or ""
    m = re.search(r'"certified":\s*(true|false)', out)
    mm = re.search(r'"matched":\s*(\d+)', out)
    md = re.search(r'"differed":\s*(\d+)', out)
    ok = bool(m and m.group(1) == "true")
    return Check("V1", "Does the reproducibility bundle actually replay?",
                 "re-ran `defensible_review.py verify --replay` in this audit", ok,
                 [f"exit {r.returncode}",
                  f"replayed: matched={mm.group(1) if mm else '?'} "
                  f"differed={md.group(1) if md else '?'}",
                  f"certified={m.group(1) if m else 'unknown'}"],
                 note="" if ok else "the bundle does not certify; read the findings list "
                                    "in the verify output")


def recheck_egress_enforced(work: Path) -> Check:
    """An attestation is a claim. Re-run the tripwire and see the control fire."""
    cmd = [sys.executable, "local_proof.py", "tripwire", "--work", str(work)]
    try:
        r = subprocess.run(cmd, cwd=LABS / "05-Local-Model-Egress-Proof",
                           capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        return Check("V2", "Does the egress control actually block?",
                     " ".join(cmd[1:]), None, note=f"could not run: {e}")
    trip = work / "attestation-tripwire.json"
    if not trip.exists():
        return Check("V2", "Does the egress control actually block?",
                     " ".join(cmd[1:]), None, note="tripwire produced no attestation")
    d = json.loads(trip.read_text())
    blocked = d.get("blocked_attempts", 0)
    trip_policy = d.get("egress_policy", "")
    # TWO questions, and conflating them is a real audit error.
    #
    #   capability    — CAN the control block? (re-run the tripwire)
    #   configuration — IS it on, in the run that produced the work? (read the run's
    #                   own attestation, not the tripwire's)
    #
    # A system whose guard works perfectly but which ran in observe-only mode passes the
    # first and fails the second, and the second is the one the matter was processed
    # under. Scoring it on capability alone is how an auditor certifies a system that
    # was, in fact, unprotected while it handled the documents.
    capability = blocked > 0 and "default-deny" in trip_policy.lower()
    run_att = work / "attestation.json"
    run_policy = (json.loads(run_att.read_text()).get("egress_policy", "")
                  if run_att.exists() else "")
    configured = "default-deny" in run_policy.lower()
    ok = capability and configured
    ev = [f"CAPABILITY: attestation-tripwire.json:egress_policy == {trip_policy!r}",
          f"CAPABILITY: attestation-tripwire.json:blocked_attempts == {blocked}",
          "DNS resolution counted as an attempted disclosure",
          f"CONFIGURATION: attestation.json:egress_policy == {run_policy!r}"]
    if capability and not configured:
        note = ("The guard WORKS but was not ENFORCING for the run that produced this "
                "work directory: the tripwire blocks, while the run's own attestation "
                "records an observe-only policy. The documents were processed without "
                "the control on. Capability is not configuration.")
    elif not capability:
        note = ("The monitor did not block anything on re-check — the guard is not "
                "installed, or the policy is observe-only.")
    else:
        note = ""
    return Check("V2", "Is egress enforced — both capable and configured?",
                 "re-ran `local_proof.py tripwire` for capability, and read the run's "
                 "own attestation for configuration", ok, ev, note=note)


def recheck_protocol_predates(work: Path) -> Check:
    """Was the threshold fixed before the run, or is that just asserted?"""
    proto = work / "validation-protocol.md"
    if not proto.exists():
        return Check("V3", "Was the validation protocol fixed before classification?",
                     "compare protocol hash to the bundle manifest", None,
                     note="no protocol on disk")
    live = hashlib.sha256(proto.read_bytes()).hexdigest()
    ptr = work / "bundle-path.txt"
    recorded = None
    if ptr.exists():
        man = Path(ptr.read_text().strip()) / "manifest.json"
        if man.exists():
            m = json.loads(man.read_text())
            recorded = ((m.get("validation") or {}).get("protocol_sha256")
                        or (m.get("protocol") or {}).get("sha256"))
    if not recorded:
        return Check("V3", "Was the validation protocol fixed before classification?",
                     "compare protocol hash to the bundle manifest", None,
                     [f"protocol on disk: sha256 {live[:16]}…"],
                     note="the bundle records no protocol hash, so the protocol cannot "
                          "be shown to predate the run. This is UNVERIFIED, not a fail: "
                          "it may well have, and there is no evidence either way.")
    ok = recorded == live
    # The tool-level control is also worth checking: does `protocol` refuse to overwrite?
    src = (LABS / "06-Defensible-Review" / "defensible_review.py")
    refuses = "--force" in src.read_text() and "refuses to overwrite" in src.read_text() \
        if src.exists() else False
    return Check("V3", "Was the validation protocol fixed before classification?",
                 "compared the on-disk protocol hash to the hash recorded in the "
                 "bundle manifest", ok,
                 [f"on disk: {live[:16]}…", f"in manifest: {str(recorded)[:16]}…",
                  f"tool refuses to overwrite without --force: {refuses}"],
                 note="" if ok else "the protocol on disk is NOT the one the bundle "
                                    "recorded — it was edited after the run, which is "
                                    "the single most damaging finding in this list")


def recheck_exceptions_triaged(work: Path) -> Check:
    exc = work / "exceptions.jsonl"
    if not exc.exists():
        return Check("V4", "Are processing exceptions recorded and triaged?",
                     "read exceptions.jsonl and the ingest gate record", None,
                     note="no exception list — which is itself a finding: a run with "
                          "zero exceptions over a messy corpus means they were dropped")
    rows = [json.loads(l) for l in exc.open(encoding="utf-8") if l.strip()]
    with_next = [r for r in rows if (r.get("next_step") or "").strip()]
    gate = work / "_state" / "gate-ingest.json"
    approved = json.loads(gate.read_text()).get("approved_by") if gate.exists() else None
    ok = bool(rows) and len(with_next) == len(rows) and bool(approved)
    return Check("V4", "Are processing exceptions recorded and triaged?",
                 "counted exceptions, checked each has a next step, checked for a "
                 "recorded human review", ok,
                 [f"exceptions.jsonl: {len(rows)} row(s)",
                  f"with a next_step: {len(with_next)}/{len(rows)}",
                  f"_state/gate-ingest.json approved_by: {approved!r}"],
                 note="" if ok else "exceptions exist but no human review is on record; "
                                    "a silently dropped document is the classic "
                                    "defensibility hole")


def recheck_matter_isolation(work: Path) -> Check:
    """The one the legal overlay cares most about — and the hardest to evidence."""
    cat = work / "catalog.jsonl"
    if not cat.exists():
        return Check("V5", "Is matter isolation enforced, not merely conventional?",
                     "inspect catalog matters; look for an isolation test", None,
                     note="no catalog")
    matters = set()
    for line in cat.open(encoding="utf-8"):
        if line.strip():
            d = json.loads(line)
            if d.get("matter"):
                matters.add(d["matter"])
    test = next((resolve(work, s) for s in
                 ("matter-isolation-test.json", "ETHICAL-WALL-TEST.md")
                 if resolve(work, s)), None)
    if len(matters) > 1:
        return Check("V5", "Is matter isolation enforced, not merely conventional?",
                     "counted distinct matters in the catalog", False,
                     [f"catalog.jsonl contains {len(matters)} matters: "
                      f"{sorted(matters)}"],
                     note="AUTO-FAIL: documents from different matters share one index")
    if test:
        return Check("V5", "Is matter isolation enforced, not merely conventional?",
                     "found an isolation test artifact and confirmed a single matter "
                     "in the catalog", True,
                     [f"single matter: {sorted(matters)}",
                      f"isolation test: {test.name}"])
    return Check("V5", "Is matter isolation enforced, not merely conventional?",
                 "counted matters; looked for an isolation test artifact", None,
                 [f"single matter in the catalog: {sorted(matters) or 'none recorded'}",
                  "no matter-isolation test artifact found"],
                 note="UNVERIFIED, and deliberately not a pass. One matter in one index "
                      "is a convention. The evidence an auditor needs is a TEST: query "
                      "matter A's index for a document only present in matter B and "
                      "assert zero hits. Until that test exists there is nothing to "
                      "verify.")


def recheck_citations_enforced(work: Path) -> Check:
    """Is the citation verifier real code, and does it reject when it should?"""
    cmd = [sys.executable, "legal_rag.py", "ask", "--work", str(work),
           "-q", "What is the indemnification cap in the MSA?", "--break-citations"]
    try:
        r = subprocess.run(cmd, cwd=LABS / "04-Legal-RAG-Citations",
                           capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.SubprocessError) as e:
        return Check("V6", "Does the citation verifier reject a bad answer?",
                     " ".join(cmd[1:]), None, note=f"could not run: {e}")
    out = (r.stdout or "") + (r.stderr or "")
    rejected = "REJECT" in out.upper()
    return Check("V6", "Does the citation verifier reject a bad answer?",
                 "re-ran `legal_rag.py ask --break-citations`, which deliberately "
                 "corrupts the answer, and checked that the verifier caught it",
                 rejected,
                 [f"exit {r.returncode}",
                  f"verifier reported a rejection: {rejected}"],
                 note="" if rejected else "the verifier did not reject a deliberately "
                                          "sabotaged answer — the control is decorative")


RECHECKS = [recheck_bundle_replays, recheck_egress_enforced, recheck_protocol_predates,
            recheck_exceptions_triaged, recheck_matter_isolation,
            recheck_citations_enforced]


# ========================================================================== the audit
def cmd_audit(work: Path, skip_rechecks: bool) -> int:
    print(f"\n  VERIFIED SAIS-100 AUDIT — {work}")
    print(f"  auditor re-runs the checks it can; it does not read conclusions.\n")

    checks: list[Check] = []
    if skip_rechecks:
        print("  (--no-rechecks: scoring from artifacts only. An audit that skips the")
        print("   re-checks is a review, not an audit. Say which one you did.)\n")
    else:
        for fn in RECHECKS:
            print(f"  running {fn.__name__.replace('recheck_', '')} …",
                  end=" ", flush=True)
            c = fn(work)
            checks.append(c)
            print(c.row()["result"])

    # The self-score, which we now treat as a CLAIM to be corroborated.
    claimed = sais100.build_score(work)

    # Adjust: a category cannot score above what the re-checks support.
    adjustments = []
    verified = json.loads(json.dumps(claimed))   # deep copy
    CHECK_TO_Q = {"V1": ("governance", "G2"), "V2": ("data_security", "D1"),
                  "V3": ("governance", "G1"), "V4": ("detection_monitoring", "T2"),
                  "V5": ("data_security", "D2"), "V6": ("prompt_security", "P2")}
    for c in checks:
        cat, qid = CHECK_TO_Q[c.cid]
        q = next(q for q in verified["categories"][cat]["questions"] if q["id"] == qid)
        if c.passed is False and q["score"] > 1:
            adjustments.append({"question": qid, "from": q["score"], "to": 1,
                                "because": f"{c.cid} FAILED on re-check: {c.note}"})
            q["score"] = 1
        elif c.passed is None and q["score"] > 2:
            adjustments.append({"question": qid, "from": q["score"], "to": 2,
                                "because": f"{c.cid} could not be verified: {c.note}"})
            q["score"] = 2
        q["verified_by"] = c.row()

    total = 0
    for cat, c in verified["categories"].items():
        raw = sum(q["score"] for q in c["questions"])
        c["raw"] = raw
        c["score"] = round(raw / 9 * WEIGHTS[cat])
        total += c["score"]
    verified["total"] = total
    verified["verdict"] = sais100.verdict(total)
    verified["audit"] = {
        "kind": "verified" if not skip_rechecks else "self-assessment (NOT an audit)",
        "at": now(), "rechecks": [c.row() for c in checks],
        "adjustments": adjustments,
        "claimed_total": claimed["total"],
        "verified_total": total,
    }
    verified["final"] = ("DO NOT DEPLOY — legal auto-fail"
                         if verified["legal_auto_fails"] else verified["verdict"])

    print(f"\n  {'category':<24}{'claimed':>9}{'verified':>10}{'Δ':>5}")
    print("  " + "-" * 48)
    for cat in WEIGHTS:
        a, b = claimed["categories"][cat]["score"], verified["categories"][cat]["score"]
        d = b - a
        print(f"  {cat.replace('_', ' '):<24}{a:>9}{b:>10}"
              f"{(('+' if d > 0 else '') + str(d)) if d else '·':>5}")
    print("  " + "-" * 48)
    d = total - claimed["total"]
    print(f"  {'TOTAL':<24}{claimed['total']:>9}{total:>10}"
          f"{(('+' if d > 0 else '') + str(d)) if d else '·':>5}")
    print(f"\n  verified verdict: {verified['final']}")

    if adjustments:
        print(f"\n  ADJUSTMENTS ({len(adjustments)})\n")
        for a in adjustments:
            print(f"    {a['question']}: {a['from']} -> {a['to']}")
            print(f"        {a['because']}")
    unver = [c for c in checks if c.passed is None]
    if unver:
        print(f"\n  UNVERIFIED ({len(unver)}) — not a pass and not a zero\n")
        for c in unver:
            print(f"    {c.cid}  {c.question}")
            print(f"        {c.note}")

    print(f"\n  LEGAL AUTO-FAILS: {len(verified['legal_auto_fails'])}")
    for f in verified["legal_auto_fails"]:
        print(f"    {f['id']}  {f['condition']}")

    out = work / "sais100-verified.json"
    out.write_text(json.dumps(verified, indent=2) + "\n")
    print(f"\n  wrote {out}")
    print("\n  Note the direction of the delta. A verified audit almost never scores")
    print("  HIGHER than the self-assessment, and when it does, the self-assessment")
    print("  was being modest about evidence it actually had.")
    return 0


# ======================================================================== the findings
EFFORT = {
    "D1": ("Enforce egress instead of observing it", "1 hour",
           "Run with LEGAL_AI_EGRESS=deny and re-attest. The code is already there."),
    "D2": ("Write a matter-isolation test", "half a day",
           "Create a second matter, index it separately, query A for a B-only document, "
           "assert zero hits. Commit the test. This is artifact #8."),
    "D3": ("Hash the corpus at ingest and record it", "1 hour", ""),
    "P1": ("Fence retrieved context and detect instruction-shaped text", "2 hours", ""),
    "P2": ("Add the citation verifier to the ask path", "half a day", ""),
    "P3": ("Log every rendered prompt into the bundle", "2 hours", ""),
    "A1": ("Record a human approval at the production gate", "15 minutes",
           "Run the approve command. The gate already exists and refuses without it."),
    "A2": ("Route privilege and low-confidence calls to a human", "2 hours", ""),
    "A3": ("Log every stage and make the bundle replay", "half a day", ""),
    "M1": ("Pin the model by hash and quantization", "1 hour",
           "Read the digest from the runtime's /api/show and record it in the manifest."),
    "M2": ("Hash-pin dependencies and reference the image by digest", "half a day",
           "pip --require-hashes, and docker inspect for the base image digest."),
    "M3": ("Pin the embedding model, dimension and chunking; freeze the index",
           "2 hours", ""),
    "T1": ("Run the tripwire so the monitor is shown to fire", "15 minutes",
           "One command. It is the cheapest point on this whole list."),
    "T2": ("Triage the exception list and record who reviewed it", "1 hour",
           "The gate command exists; somebody has to actually read the list first."),
    "T3": ("Measure elusion on the discard pile", "half a day",
           "Recall alone does not tell you what you missed."),
    "G1": ("Write the protocol first and hash it into the bundle", "1 hour", ""),
    "G2": ("Make the bundle verify, with replay", "half a day", ""),
    "G3": ("State the limits of every claim", "1 hour",
           "The cheapest defensibility control there is, and the most often skipped."),
}
EFFORT_ORDER = {"15 minutes": 0, "1 hour": 1, "2 hours": 2, "half a day": 3}


def cmd_findings(work: Path) -> int:
    p = work / "sais100-verified.json"
    if not p.exists():
        raise SystemExit("run `audit` first")
    v = json.loads(p.read_text())
    arts = work / "audit-artifacts.json"
    nine = json.loads(arts.read_text()) if arts.exists() else None

    gaps = []
    for cat, c in v["categories"].items():
        for q in c["questions"]:
            if q["score"] < 3:
                name, effort, how = EFFORT.get(q["id"], (q["gap_to_next_level"], "?", ""))
                # points available = (3 - score) scaled by the category weight
                points = round((3 - q["score"]) / 9 * WEIGHTS[cat], 1)
                gaps.append({"id": q["id"], "category": cat, "score": q["score"],
                             "points_available": points, "fix": name,
                             "effort": effort, "how": how,
                             "gap": q["gap_to_next_level"]})
    # cheapest first, then by points — "value per hour", which is what a client asks for
    gaps.sort(key=lambda g: (EFFORT_ORDER.get(g["effort"], 9), -g["points_available"]))

    lines = [
        f"# Governance audit findings — {v.get('mode', 'local')} deployment", "",
        f"**Audited:** {v['audit']['at']}  ",
        f"**Audit kind:** {v['audit']['kind']}  ",
        f"**Self-assessed score:** {v['audit']['claimed_total']}/100  ",
        f"**Verified score:** {v['total']}/100 "
        f"(score band: {v['verdict']})  ",
        f"**Final:** {v['final']}", "",
        ("> The score band and the final verdict differ because an auto-fail is a "
         "condition, not a deduction. Quote the Final line, never the score alone."
         if v["legal_auto_fails"] else
         "> Score band and final verdict agree: no auto-fail conditions are present."),
        "",
        "## Verdict", "",
    ]
    if v["legal_auto_fails"]:
        lines.append(f"**DO NOT DEPLOY.** {len(v['legal_auto_fails'])} legal auto-fail "
                     f"condition(s) are present. The score is not the verdict:")
        for f in v["legal_auto_fails"]:
            lines.append(f"- **{f['id']}** — {f['condition']}. {f['why']}")
    else:
        lines.append(f"No legal auto-fail conditions. Verified score {v['total']}/100 "
                     f"({v['verdict']}).")
    lines.append("")

    lines += ["## What was re-checked, not taken on trust", "",
              "| check | question | result |", "|---|---|---|"]
    for c in v["audit"]["rechecks"]:
        lines.append(f"| {c['id']} | {c['question']} | **{c['result']}** |")
    lines.append("")
    unver = [c for c in v["audit"]["rechecks"] if c["result"] == "UNVERIFIED"]
    if unver:
        lines += ["### Unverified — neither a pass nor a zero", ""]
        for c in unver:
            lines.append(f"- **{c['id']}** — {c['note']}")
        lines.append("")
    if v["audit"]["adjustments"]:
        lines += ["### Score adjustments made by this audit", ""]
        for a in v["audit"]["adjustments"]:
            lines.append(f"- `{a['question']}` {a['from']} → {a['to']}: {a['because']}")
        lines.append("")

    if nine:
        lines += [f"## The nine governance artifacts — {nine['present']}/9 present", "",
                  "| # | artifact | status | gap |", "|---|---|---|---|"]
        for a in nine["artifacts"]:
            lines.append(f"| {a['n']} | {a['name']} | "
                         f"{'present' if a['present'] else '**missing**'} | "
                         f"{a['gap'] or '—'} |")
        lines.append("")

    lines += ["## The three highest-value fixes", "",
              "Ordered by effort, then by points available. This is the order a client "
              "will ask for.", ""]
    for g in gaps[:3]:
        lines += [f"### {g['fix']}", "",
                  f"- **Effort:** {g['effort']}",
                  f"- **Points available:** {g['points_available']} "
                  f"({g['category'].replace('_', ' ')}, question `{g['id']}`, "
                  f"currently {g['score']}/3)",
                  f"- **Why it is open:** {g['gap']}"]
        if g["how"]:
            lines.append(f"- **How:** {g['how']}")
        lines.append("")

    if len(gaps) > 3:
        lines += ["## Everything else that is open", "",
                  "| question | score | points | effort | fix |", "|---|---|---|---|---|"]
        for g in gaps[3:]:
            lines.append(f"| `{g['id']}` | {g['score']}/3 | {g['points_available']} | "
                         f"{g['effort']} | {g['fix']} |")
        lines.append("")

    lines += ["## Gaps consciously carried", "",
              "*Fill this in yourself. Not every gap gets closed, and the professional "
              "judgment is in knowing which ones you are carrying and being able to say "
              "why. An audit report with an empty section here is incomplete.*", "",
              "| gap | why we are carrying it | revisit when |", "|---|---|---|",
              "|  |  |  |", ""]

    out = work / "audit-findings.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n  self-assessed : {v['audit']['claimed_total']}/100")
    print(f"  verified      : {v['total']}/100 — {v['final']}")
    print(f"  open questions: {len(gaps)}")
    print(f"\n  cheapest three fixes:")
    for g in gaps[:3]:
        print(f"      {g['effort']:<12} +{g['points_available']:<5} {g['fix']}")
    print(f"\n  wrote {out}")
    print("\n  Open the report and fill in 'Gaps consciously carried'. That section is")
    print("  the one a senior engineer is paid for, and the tool cannot write it.")
    return 0


def cmd_delta(work: Path) -> int:
    base = work / "sais100-verified-baseline.json"
    cur = work / "sais100-verified.json"
    if not cur.exists():
        raise SystemExit("run `audit` first")
    if not base.exists():
        base.write_text(cur.read_text())
        print(f"\n  saved baseline -> {base}")
        print("  Now apply ONE fix, re-run `audit`, and run `delta` again.")
        return 0
    b, c = json.loads(base.read_text()), json.loads(cur.read_text())
    print(f"\n  {'category':<24}{'before':>8}{'after':>7}{'Δ':>5}")
    print("  " + "-" * 44)
    for cat in WEIGHTS:
        bb, aa = b["categories"][cat]["score"], c["categories"][cat]["score"]
        d = aa - bb
        print(f"  {cat.replace('_', ' '):<24}{bb:>8}{aa:>7}"
              f"{(('+' if d > 0 else '') + str(d)) if d else '·':>5}")
    print("  " + "-" * 44)
    d = c["total"] - b["total"]
    print(f"  {'TOTAL':<24}{b['total']:>8}{c['total']:>7}"
          f"{(('+' if d > 0 else '') + str(d)) if d else '·':>5}")
    print(f"\n  {b['final']}  ->  {c['final']}")
    moved = []
    for cat in WEIGHTS:
        for qb, qc in zip(b["categories"][cat]["questions"],
                          c["categories"][cat]["questions"]):
            if qb["score"] != qc["score"]:
                moved.append((qc["id"], qb["score"], qc["score"]))
    if moved:
        print(f"\n  questions that moved:")
        for qid, x, y in moved:
            print(f"      {qid}: {x} -> {y}")
    else:
        print("\n  Nothing moved. Either the fix did not land, or it was not a fix the")
        print("  rubric measures — and the second case is worth more thought than the")
        print("  first.")
    (work / "audit-delta.json").write_text(json.dumps({
        "before": b["total"], "after": c["total"], "delta": d,
        "before_final": b["final"], "after_final": c["final"],
        "questions_moved": [{"id": q, "from": x, "to": y} for q, x, y in moved],
    }, indent=2) + "\n")
    print(f"\n  wrote {work / 'audit-delta.json'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("artifacts", "audit", "findings", "delta"):
        s = sub.add_parser(name)
        s.add_argument("--work", default="../work")
        if name == "audit":
            s.add_argument("--no-rechecks", action="store_true",
                           help="score from artifacts only (then it is not an audit)")
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if not work.is_dir():
        raise SystemExit(f"no work directory at {work}\n"
                         f"Run the Lab 07 pipeline first:\n"
                         f"  cd ../07-Score-and-Package && python3 run_matter.py "
                         f"--work {work}")
    if args.cmd == "artifacts":
        return cmd_artifacts(work)
    if args.cmd == "audit":
        return cmd_audit(work, args.no_rechecks)
    if args.cmd == "findings":
        return cmd_findings(work)
    if args.cmd == "delta":
        return cmd_delta(work)
    return 2


if __name__ == "__main__":
    sys.exit(main())
