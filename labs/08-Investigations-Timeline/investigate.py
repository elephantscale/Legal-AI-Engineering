#!/usr/bin/env python3
"""investigate.py — Lab 08: entities, threads, timelines, lineage (Module 9).

    python3 investigate.py entities --work ../work
    python3 investigate.py resolve  --work ../work
    python3 investigate.py threads  --work ../work
    python3 investigate.py timeline --work ../work --pair aray,jdoe
    python3 investigate.py diff     --work ../work --group ND-0001
    python3 investigate.py leads    --work ../work

Investigation differs from review in one way that changes all the engineering: **review
asks what a document says; investigation asks what the documents, together, imply** —
including what is missing. A gap in a conversation is a finding. A referenced document
that is not in the collection is a finding. Neither contains a keyword, so neither can be
found by search. They are structural queries.

Everything here reads Lab 01's catalog and text store. Nothing here needs a model: the
gazetteer path is deterministic and runs offline. The LLM path (`--llm`) adds recall on
entities the gazetteer does not know, and every entity it returns still carries a source
span, because an entity you cannot point at in a document is not evidence.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import llm  # noqa: E402


# --------------------------------------------------------------------------- loading
def load_catalog(work: Path) -> list[dict]:
    p = work / "catalog.jsonl"
    if not p.exists():
        raise SystemExit(f"no catalog at {p} — run Lab 01 first")
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]


def doc_text(work: Path, doc_id: str) -> str:
    p = work / "text" / f"{doc_id}.txt"
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


# ----------------------------------------------------------------- 1. entities + spans
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MONEY_RE = re.compile(r"\$\s?[\d,]+(?:\.\d{2})?(?:\s?(?:million|billion))?", re.I)
DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
    r"|\d{1,2}/\d{1,2}/\d{2,4})\b")
CLAUSE_RE = re.compile(
    r"(?:\b(?:§|Section|Sec\.|Art\.|Article)\s?\d+(?:\.\d+)*"
    # ...and the bare form, which is how contracts actually number clauses:
    # "7.3 INDEMNIFICATION CAP." at the start of a line. Requiring the § sigil is the
    # kind of plausible-looking regex that silently misses the clause you care about.
    r"|(?m:^\s*\d+\.\d+(?=\s+[A-Z]))"
    r"|(?m:^\s*\d+\.(?=\s+[A-Z]{3})))", re.I)
ORG_SUFFIX = r"(?:Inc|Inc\.|LLC|L\.L\.C\.|Ltd|Ltd\.|Corp|Corp\.|Corporation|Systems|Industries|LLP|PLLC)"
ORG_RE = re.compile(rf"\b([A-Z][A-Za-z&.\-]+(?:\s+[A-Z][A-Za-z&.\-]+)*\s+{ORG_SUFFIX})\b")


@dataclass
class Entity:
    doc_id: str
    kind: str          # PERSON | ORG | EMAIL | MONEY | DATE | CLAUSE
    surface: str       # exactly as it appears in the source field
    start: int         # character offsets INTO `field` (see below)
    end: int
    source: str        # gazetteer | pattern | llm
    confidence: float
    # Which text the offsets index. "body" means text/<doc_id>.txt; anything else is a
    # catalog metadata field, e.g. "metadata.from". Both are checkable, which is the
    # only property that matters: an entity whose locator you cannot resolve is a claim,
    # not evidence. Header participants are most of the people in a mail corpus and they
    # never appear in the body, so a body-only extractor finds almost no one.
    field: str = "body"

    def row(self) -> dict:
        return self.__dict__


def header_items(m: dict) -> list[tuple[str, str]]:
    """(field_name, raw_value) for every participant slot in a message's headers."""
    out = []
    for f in ("from", "to", "cc", "bcc"):
        v = m.get(f)
        for item in (v if isinstance(v, list) else [v] if v else []):
            if item:
                out.append((f"metadata.{f}", item))
    return out


def build_gazetteer(cat: list[dict]) -> dict[str, tuple[str, float]]:
    """Known custodians, plus every name form that appears in a header.

    A gazetteer is not a fallback for a weak model. In a matter you ALWAYS have one: the
    custodian list, the party names, the counsel of record. Those entities are the ones
    whose misidentification is most expensive, so they get the deterministic path and the
    model gets the long tail.

    The forms matter. People sign emails "Anita", are addressed as "Anita", and appear in
    headers as "Anita Ray <a.ray@…>". A gazetteer holding only the full form finds nobody
    in a message body. So we add the bare first and last names too — at **lower
    confidence**, because "Anita" in running text is genuinely ambiguous and pretending
    otherwise is how an investigation tool starts putting words in the wrong mouth.
    """
    gaz: dict[str, tuple[str, float]] = {}
    for d in cat:
        m = d.get("metadata") or {}
        for _field, item in header_items(m):
            name = re.sub(r"<[^>]*>", "", item).strip(' "')
            addr = EMAIL_RE.search(item)
            if name and " " in name:
                gaz[name] = ("PERSON", 1.0)
                parts = [p for p in name.split() if len(p) > 2 and p[0].isupper()]
                for p in parts:
                    gaz.setdefault(p, ("PERSON", 0.55))
            if addr:
                gaz[addr.group(0)] = ("EMAIL", 1.0)
                local = addr.group(0).split("@")[0]
                if len(local) > 2:
                    gaz.setdefault(local, ("PERSON", 0.5))
        if d.get("custodian"):
            gaz.setdefault(d["custodian"], ("PERSON", 0.8))
    return gaz


def extract_patterns(doc_id: str, text: str) -> list[Entity]:
    out: list[Entity] = []
    for rx, kind in ((EMAIL_RE, "EMAIL"), (MONEY_RE, "MONEY"),
                     (DATE_RE, "DATE"), (CLAUSE_RE, "CLAUSE"), (ORG_RE, "ORG")):
        for m in rx.finditer(text):
            out.append(Entity(doc_id, kind, m.group(0), m.start(), m.end(),
                              "pattern", 0.95))
    return out


def extract_gazetteer(doc_id: str, text: str,
                      gaz: dict[str, tuple[str, float]],
                      field: str = "body") -> list[Entity]:
    out: list[Entity] = []
    for surface, (kind, conf) in gaz.items():
        if len(surface) < 3:
            continue
        # word-boundary match: "Ray" must not fire inside "Rayburn", and a bare first
        # name is exactly the case where a substring match invents a person.
        for m in re.finditer(rf"(?<![\w.@]){re.escape(surface)}(?![\w@])", text):
            out.append(Entity(doc_id, kind, m.group(0), m.start(), m.end(),
                              "gazetteer", conf, field))
    return out


def extract_headers(doc_id: str, meta: dict,
                    gaz: dict[str, tuple[str, float]]) -> list[Entity]:
    """Participants, from the headers, with offsets into the header value itself."""
    out: list[Entity] = []
    for fieldname, raw in header_items(meta):
        for m in EMAIL_RE.finditer(raw):
            out.append(Entity(doc_id, "EMAIL", m.group(0), m.start(), m.end(),
                              "gazetteer", 1.0, fieldname))
        name = re.sub(r"<[^>]*>", "", raw).strip(' "')
        if name and " " in name:
            pos = raw.find(name)
            out.append(Entity(doc_id, "PERSON", name, pos, pos + len(name),
                              "gazetteer", 1.0, fieldname))
    return out


LLM_ENTITY_SYSTEM = """You extract named entities from legal documents for an investigation.

Return ONLY a JSON array. Each element: {"kind": "...", "surface": "..."}
kind is one of PERSON, ORG, LOCATION, PRODUCT.
surface MUST be copied character-for-character from the document. Do not normalize,
expand, correct spelling, or infer. If you cannot copy it exactly, omit it.
Return [] if there are none. No prose, no markdown fence."""


def extract_llm(doc_id: str, text: str) -> list[Entity]:
    """LLM entities, verified back against the text.

    The verification is the whole reason this is usable. A model that returns an entity
    we cannot find in the document has either normalized it ("Hollerith Inc." for
    "Hollerith Industries, Inc.") or invented it. Both are dropped. An entity without a
    span is a claim; an entity with a span is evidence.
    """
    raw = llm.chat(LLM_ENTITY_SYSTEM, text[:6000], temperature=0.0)
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out: list[Entity] = []
    for it in items if isinstance(items, list) else []:
        surface = str(it.get("surface", "")).strip()
        kind = str(it.get("kind", "")).strip().upper()
        if not surface or kind not in {"PERSON", "ORG", "LOCATION", "PRODUCT"}:
            continue
        pos = text.find(surface)
        if pos < 0:
            continue                      # unverifiable -> dropped, silently and on purpose
        out.append(Entity(doc_id, kind, surface, pos, pos + len(surface), "llm", 0.7))
    return out


def cmd_entities(work: Path, use_llm: bool, limit: int) -> int:
    cat = load_catalog(work)
    gaz = build_gazetteer(cat)
    print(f"\n  gazetteer : {len(gaz)} known surfaces from headers and custodians")
    ents: list[Entity] = []
    dropped = 0
    docs = cat[:limit] if limit else cat
    for i, d in enumerate(docs, 1):
        text = doc_text(work, d["doc_id"])
        if not text:
            continue
        ents += extract_patterns(d["doc_id"], text)
        ents += extract_gazetteer(d["doc_id"], text, gaz)
        ents += extract_headers(d["doc_id"], d.get("metadata") or {}, gaz)
        if use_llm and llm.available():
            before = len(ents)
            ents += extract_llm(d["doc_id"], text)
            dropped += 0 if len(ents) > before else 0
        if i % 200 == 0:
            print(f"  {i}/{len(docs)}", end="\r", flush=True)

    # de-overlap: keep the most trustworthy source for identical spans
    rank = {"gazetteer": 3, "pattern": 2, "llm": 1}
    best: dict[tuple, Entity] = {}
    for e in ents:
        k = (e.doc_id, e.field, e.start, e.end)
        if k not in best or rank[e.source] > rank[best[k].source]:
            best[k] = e
    rows = [e.row() for e in sorted(best.values(),
                                    key=lambda e: (e.doc_id, e.field, e.start))]
    write_jsonl(work / "entities.jsonl", rows)

    by_kind: dict[str, int] = defaultdict(int)
    by_src: dict[str, int] = defaultdict(int)
    for r in rows:
        by_kind[r["kind"]] += 1
        by_src[r["source"]] += 1
    print(f"\n  entities  : {len(rows)} with verified spans")
    for k, n in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print(f"      {k:<10} {n}")
    print(f"  by source : " + ", ".join(f"{k}={n}" for k, n in sorted(by_src.items())))
    body = sum(1 for r in rows if r["field"] == "body")
    low = sum(1 for r in rows if r["confidence"] < 0.6)
    print(f"  by locator: body={body}, headers={len(rows) - body}")
    print(f"  low confidence (<0.6): {low} — bare first names and address local-parts")
    print(f"\n  wrote {work / 'entities.jsonl'}")
    print("\n  Every row has doc_id + field + start + end. Open one and check it:")
    print("  field 'body' means text/<doc_id>.txt; 'metadata.cc' means that header")
    print("  value in catalog.jsonl. An entity you cannot point at is not evidence.")
    return 0


# ------------------------------------------------------------- 2. resolution + merge log
def normalize_person(surface: str) -> str:
    s = surface.lower().strip(' ."')
    s = re.sub(r"\s+", " ", s)
    return s


def cmd_resolve(work: Path) -> int:
    """Resolve surfaces to canonical identities, and LOG every merge with its evidence.

    Entity resolution is where investigation tooling quietly becomes an ethics problem.
    Merging "M. Chen" into "Mei Chen" is almost certainly right. Merging two different
    people who share a surname puts words in someone's mouth, and because the merge is
    invisible downstream, nobody ever checks it. So: no merge without recorded evidence,
    and the merge log ships with the findings.
    """
    p = work / "entities.jsonl"
    if not p.exists():
        raise SystemExit("run `entities` first")
    ents = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]

    # address -> the display names seen with it, from the headers (strong evidence)
    cat = load_catalog(work)
    addr_names: dict[str, set[str]] = defaultdict(set)
    for d in cat:
        m = d.get("metadata") or {}
        for fieldname in ("from", "to", "cc", "bcc"):
            v = m.get(fieldname)
            for item in (v if isinstance(v, list) else [v] if v else []):
                addr = EMAIL_RE.search(item or "")
                name = re.sub(r"<[^>]*>", "", item or "").strip(' "')
                if addr and name and " " in name:
                    addr_names[addr.group(0).lower()].add(name)

    canon: dict[str, str] = {}
    merges: list[dict] = []
    for addr, names in sorted(addr_names.items()):
        primary = sorted(names, key=len)[-1]
        canon[addr] = primary
        for n in sorted(names):
            canon[normalize_person(n)] = primary
            if normalize_person(n) != normalize_person(primary):
                merges.append({
                    "canonical": primary, "merged": n, "confidence": 0.99,
                    "evidence": f"appears in a header with {addr}",
                    "basis": "same-address", "reviewed_by": None})
        # initial + surname, e.g. "M. Chen" -> "Mei Chen": a HEURISTIC, flagged lower
        parts = primary.split()
        if len(parts) >= 2:
            variant = f"{parts[0][0]}. {parts[-1]}"
            if normalize_person(variant) not in canon:
                canon[normalize_person(variant)] = primary
                merges.append({
                    "canonical": primary, "merged": variant, "confidence": 0.60,
                    "evidence": "initial + surname pattern only; no address co-occurrence",
                    "basis": "heuristic", "reviewed_by": None})

    write_jsonl(work / "merge_log.jsonl", merges)
    resolved = 0
    for e in ents:
        if e["kind"] in ("PERSON", "EMAIL"):
            c = canon.get(normalize_person(e["surface"])) or \
                canon.get(e["surface"].lower())
            if c:
                e["canonical"] = c
                resolved += 1
    write_jsonl(work / "entities.jsonl", ents)

    strong = sum(1 for m in merges if m["basis"] == "same-address")
    weak = sum(1 for m in merges if m["basis"] == "heuristic")
    print(f"\n  canonical identities : {len(set(canon.values()))}")
    print(f"  entity rows resolved : {resolved}")
    print(f"  merges logged        : {len(merges)}  "
          f"({strong} same-address, {weak} heuristic)")
    print(f"\n  wrote {work / 'merge_log.jsonl'}")
    print("\n  Read the heuristic merges. Each one has confidence 0.60 and "
          "reviewed_by: null.\n  In a real matter a human clears those before any "
          "finding rests on them —\n  which is why the field exists and why it starts "
          "empty.")
    return 0


# -------------------------------------------------------------- 3. thread reconstruction
@dataclass
class Node:
    doc_id: str
    message_id: str
    parent: str | None
    subject: str
    sent: str
    frm: str
    to: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)


def build_threads(cat: list[dict]) -> tuple[dict[str, Node], dict[str, list[str]]]:
    nodes: dict[str, Node] = {}
    for d in cat:
        m = d.get("metadata") or {}
        mid = m.get("message_id")
        if not mid:
            continue
        rraw = m.get("references") or []
        refs = rraw.split() if isinstance(rraw, str) else list(rraw)
        parent = m.get("in_reply_to") or (refs[-1] if refs else None)
        nodes[mid] = Node(d["doc_id"], mid, parent, m.get("subject", ""),
                          m.get("sent_utc", ""), m.get("from", ""),
                          m.get("to") or [], m.get("cc") or [])
    for n in nodes.values():
        if n.parent and n.parent in nodes:
            nodes[n.parent].children.append(n.message_id)
    roots: dict[str, list[str]] = defaultdict(list)
    for n in nodes.values():
        r, seen = n.message_id, set()
        while nodes[r].parent in nodes and r not in seen:
            seen.add(r)
            r = nodes[r].parent
        roots[r].append(n.message_id)
    return nodes, roots


def addrs(items: list[str]) -> set[str]:
    out = set()
    for i in items:
        m = EMAIL_RE.search(i or "")
        if m:
            out.add(m.group(0).lower())
    return out


def cmd_threads(work: Path) -> int:
    cat = load_catalog(work)
    nodes, roots = build_threads(cat)
    threads = sorted(roots.items(), key=lambda kv: -len(kv[1]))

    rows, dropped_rows = [], []
    for root, members in threads:
        ms = sorted((nodes[m] for m in members), key=lambda n: n.sent)
        # the INCLUSIVE set: messages whose recipient set is not a subset of a later
        # message in the same thread. Reviewing only these covers the whole text of the
        # conversation, which is how review volume gets cut by half honestly.
        inclusive = []
        for i, n in enumerate(ms):
            people = addrs([n.frm]) | addrs(n.to) | addrs(n.cc)
            covered = any(people <= (addrs([l.frm]) | addrs(l.to) | addrs(l.cc))
                          for l in ms[i + 1:])
            if not covered:
                inclusive.append(n)
        for i in range(1, len(ms)):
            lost = addrs(ms[i - 1].cc) - (addrs(ms[i].cc) | addrs(ms[i].to))
            if lost:
                dropped_rows.append({
                    "thread_root": root, "doc_id": ms[i].doc_id,
                    "sent_utc": ms[i].sent, "subject": ms[i].subject,
                    "dropped": sorted(lost), "from": ms[i].frm,
                    "finding": "recipient removed mid-thread",
                    "why_it_matters": "a conversation that narrows is a conversation "
                                      "somebody wanted narrowed; check what is said "
                                      "after the drop"})
        rows.append({"thread_root": root, "subject": ms[0].subject if ms else "",
                     "messages": len(ms), "inclusive": len(inclusive),
                     "span": [ms[0].sent, ms[-1].sent] if ms else None,
                     "doc_ids": [n.doc_id for n in ms],
                     "inclusive_doc_ids": [n.doc_id for n in inclusive]})

    write_jsonl(work / "threads.jsonl", rows)
    write_jsonl(work / "dropped_recipients.jsonl", dropped_rows)
    tot = sum(r["messages"] for r in rows)
    inc = sum(r["inclusive"] for r in rows)
    multi = [r for r in rows if r["messages"] > 1]
    m_tot = sum(r["messages"] for r in multi)
    m_inc = sum(r["inclusive"] for r in multi)
    print(f"\n  threads   : {len(rows)}  messages {tot}")
    print(f"  of those  : {len(multi)} thread(s) with more than one message "
          f"({m_tot} messages)")
    print(f"  inclusive : {inc} of {tot} overall "
          f"({inc / tot:.0%}) — the set you must read to see all the text")
    if m_tot:
        print(f"              {m_inc} of {m_tot} ({m_inc / m_tot:.0%}) within the "
              f"multi-message threads")
    print("\n  Be honest about that first percentage: this corpus is mostly "
          "single-message\n  filler, so inclusive review saves almost nothing here. On "
          "a real custodian\n  mailbox it removes 30-50% of the reading. The MECHANISM "
          "is what you are\n  checking today, not the saving.\n")
    print(f"  deepest threads:")
    for r in sorted(multi, key=lambda r: -r["messages"])[:5]:
        print(f"      {r['messages']} msgs ({r['inclusive']} inclusive)  "
              f"{r['subject'][:58]}")
    print(f"\n  dropped-Cc events : {len(dropped_rows)}")
    for r in dropped_rows[:5]:
        print(f"      {r['doc_id']}  {r['sent_utc']}  lost "
              f"{', '.join(r['dropped'])}\n          subject: {r['subject'][:62]}")
    print(f"\n  wrote {work / 'threads.jsonl'}, {work / 'dropped_recipients.jsonl'}")
    print("\n  'Inclusive' is a review-volume argument AND a defensibility risk: the")
    print("  non-inclusive messages still have distinct metadata and distinct")
    print("  attachments. Suppress them from READING, never from the catalog.")
    return 0


# ------------------------------------------------------------------ 4. timeline + gaps
# How much longer than normal is a gap? Both numbers are policy, not statistics, so they
# are named and visible rather than buried in an expression.
GAP_MULTIPLE = 5.0      # five times the surrounding cadence
GAP_FLOOR_DAYS = 7.0    # and never flag less than a week, however chatty the thread


def parse_ts(s: str) -> datetime | None:
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return None


def cmd_timeline(work: Path, pair: str | None, gap_sigma: float,
                 responsive: bool, terms: str | None, thread: str | None) -> int:
    """A cited chronology, plus the gaps — the finding that is an absence.

    Scope matters more than any parameter here. A chronology of *everything* a pair of
    custodians sent is not a chronology, it is a mailbox: the filler drowns the signal
    and no gap is ever visible, because somebody always sent something. An investigator
    builds the timeline of an ISSUE. So scope it — by the responsive set from Lab 05, by
    terms, or both — and say in the output what the scope was, because the gaps you find
    are a property of the scope.
    """
    cat = load_catalog(work)
    nodes, roots = build_threads(cat)
    msgs = [n for n in nodes.values() if parse_ts(n.sent)]
    msgs.sort(key=lambda n: n.sent)

    # --thread is the scope that finds a gap in a CONVERSATION, which is the gap that
    # means something. A flat chronology of a mailbox has no gaps: somebody always sent
    # something about something else.
    thread_ids: set[str] | None = None
    if thread:
        t = thread.lower()
        match_roots = {r for r, members in roots.items()
                       if any(t in (nodes[m].subject or "").lower()
                              or t == nodes[m].doc_id.lower() for m in members)}
        if not match_roots:
            print(f"\n  no thread matches {thread!r}. Try a subject fragment, or run "
                  f"`threads`\n  and pick one of the deepest.")
            return 1
        thread_ids = {nodes[m].doc_id for r in match_roots for m in roots[r]}

    want = None
    if pair:
        want = {p.strip().lower() for p in pair.split(",")}

    def who(n: Node) -> set[str]:
        s = {a.split("@")[0].lower() for a in addrs([n.frm]) | addrs(n.to) | addrs(n.cc)}
        return {x.replace(".", "") for x in s} | s

    keep_ids: set[str] | None = None
    scope_notes = []
    if responsive:
        dp = work / "decisions.jsonl"
        if not dp.exists():
            raise SystemExit("--responsive needs Lab 05's decisions.jsonl")
        keep_ids = {json.loads(l)["doc_id"] for l in dp.open(encoding="utf-8")
                    if l.strip() and json.loads(l)["decision"] == "responsive"}
        scope_notes.append(f"responsive set from Lab 05 ({len(keep_ids)} documents)")
    term_list = [t.strip().lower() for t in (terms or "").split(",") if t.strip()]
    if term_list:
        scope_notes.append("terms " + ", ".join(repr(t) for t in term_list))
    if pair:
        scope_notes.append(f"participants {pair}")
    if thread_ids is not None:
        scope_notes.append(f"thread matching {thread!r} ({len(thread_ids)} messages)")

    def in_scope(n: Node) -> bool:
        if thread_ids is not None and n.doc_id not in thread_ids:
            return False
        if want and not want <= who(n):
            return False
        if keep_ids is not None and n.doc_id not in keep_ids:
            return False
        if term_list:
            hay = (n.subject + " " + doc_text(work, n.doc_id)).lower()
            if not any(t in hay for t in term_list):
                return False
        return True

    selected = [n for n in msgs if in_scope(n)]
    if not selected:
        print(f"\n  no messages match pair {pair!r}. Known local-parts:")
        print("    " + ", ".join(sorted({a.split('@')[0] for n in msgs
                                         for a in addrs([n.frm])})[:12]))
        return 1

    # The baseline is per-scope, not global: "39 days" means nothing until you know that
    # this conversation otherwise moves in hours.
    deltas = [(parse_ts(b.sent) - parse_ts(a.sent)).total_seconds() / 86400
              for a, b in zip(selected, selected[1:])]

    def median(xs: list[float]) -> float:
        if not xs:
            return 0.0
        ys = sorted(xs)
        n = len(ys)
        return ys[n // 2] if n % 2 else (ys[n // 2 - 1] + ys[n // 2]) / 2

    # LEAVE-ONE-OUT baseline. Scoring a gap against a baseline that includes the gap is
    # how a real finding hides: in a three-message thread that ran for an hour and then
    # went quiet for 39 days, the 39 days IS the median, so a naive threshold reports
    # nothing. Each interval is judged against the median of the others.
    def is_gap(i: int) -> tuple[bool, float]:
        others = deltas[:i] + deltas[i + 1:]
        base = median(others) if others else median(deltas)
        t = max(base * GAP_MULTIPLE, GAP_FLOOR_DAYS)
        return deltas[i] > t, t

    med = median(deltas)
    mean = sum(deltas) / len(deltas) if deltas else 0.0
    sd = ((sum((d - mean) ** 2 for d in deltas) / len(deltas)) ** 0.5) if deltas else 0.0
    thresh = max(med * GAP_MULTIPLE, mean + gap_sigma * sd, GAP_FLOOR_DAYS)

    lines = [f"# Timeline — {pair or 'all custodians'}", "",
             "**Scope:** " + ("; ".join(scope_notes) if scope_notes
                              else "every message in the collection") +
             f" → {len(selected)} message(s).", "",
             f"Baseline for this selection: median gap **{med:.1f} days**, "
             f"mean {mean:.1f}. A gap is flagged above **{thresh:.1f} days**.", "",
             "A gap is a property of the scope. Widen the scope and it may close; that "
             "does not make it uninteresting, it makes it a question about *this* "
             "conversation.", "",
             "| date (UTC) | from | subject | doc_id |", "|---|---|---|---|"]
    gaps = []
    for i, n in enumerate(selected):
        name = re.sub(r"<[^>]*>", "", n.frm).strip(' "') or n.frm
        subj = n.subject.replace("|", "/")[:58]
        lines.append(f"| {n.sent[:10]} | {name} | {subj} | `{n.doc_id}` |")
        if i:
            flagged, t = is_gap(i - 1)
            if flagged:
                prev = selected[i - 1]
                others = deltas[:i - 1] + deltas[i:]
                g = {"days": round(deltas[i - 1], 1),
                     "between": [prev.doc_id, n.doc_id],
                     "from_date": prev.sent[:10], "to_date": n.sent[:10],
                     "baseline_median_days": round(median(others) if others else med, 1),
                     "threshold_days": round(t, 1),
                     "next_subject": n.subject}
                gaps.append(g)
                lines.append(f"| | | **▲ GAP {g['days']} days** — the rest of this "
                             f"selection runs at {g['baseline_median_days']} days; "
                             f"nothing between {g['from_date']} and {g['to_date']} | |")

    lines += ["", "## Gaps", ""]
    if gaps:
        for g in gaps:
            lines.append(
                f"- **{g['days']} days** between `{g['between'][0]}` "
                f"({g['from_date']}) and `{g['between'][1]}` ({g['to_date']}). "
                f"Leave-one-out baseline {g['baseline_median_days']} days, so the "
                f"threshold here was {g['threshold_days']} days. "
                f"The conversation resumes with: *{g['next_subject'][:70]}*")
        lines += ["",
                  "A gap is a question, not a conclusion. It has three innocent "
                  "explanations — they moved to phone or chat, the custodian was on "
                  "leave, or the collection is incomplete — and one that is not. "
                  "Which it is, is a collection question you ask next, not an "
                  "inference you publish."]
    else:
        lines.append("- none above the threshold for this selection.")

    (work / "timeline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_jsonl(work / "timeline_gaps.jsonl", gaps)
    print(f"\n  scope     : " + ("; ".join(scope_notes) if scope_notes
                                   else "every message in the collection"))
    print(f"  rows      : {len(selected)}   median interval {med:.1f} days")
    print(f"  gaps      : {len(gaps)}  (each judged against a leave-one-out baseline, "
          f"floor {GAP_FLOOR_DAYS:g} days)")
    for g in gaps:
        print(f"      {g['days']:>6.1f} days  {g['from_date']} -> {g['to_date']}  "
              f"(baseline {g['baseline_median_days']}, threshold "
              f"{g['threshold_days']})")
        print(f"               resumes with: {g['next_subject'][:58]}")
    print(f"\n  wrote {work / 'timeline.md'}, {work / 'timeline_gaps.jsonl'}")
    print("\n  Every row cites a doc_id. A timeline without citations is a story.")
    return 0


# ------------------------------------------------------------------- 5. lineage + diff
def cmd_diff(work: Path, group: str | None) -> int:
    """Diff the versions inside a near-duplicate group. Find the clause that vanished."""
    cat = load_catalog(work)
    groups: dict[str, list[dict]] = defaultdict(list)
    for d in cat:
        g = (d.get("dedupe") or {}).get("near_dupe_group")
        if g:
            groups[g].append(d)
    multi = {g: ds for g, ds in groups.items() if len(ds) > 1}
    if not group:
        print(f"\n  near-duplicate groups with >1 member: {len(multi)}\n")
        for g, ds in sorted(multi.items())[:15]:
            print(f"    {g}  ({len(ds)})")
            for d in ds[:4]:
                print(f"        {d['doc_id']}  {d['source_path'][-62:]}")
        print("\n  pick one:  --group ND-0001")
        return 0
    if group not in groups:
        raise SystemExit(f"no group {group!r}")

    members = groups[group]

    # Collapse exact text duplicates FIRST. A near-dupe group spans custodians, so the
    # same draft appears several times; diffing path-sorted members then produces a
    # meaningless A->B->A chain. One row per distinct text, each listing every custodian
    # who held it — which is also the possession fact you must not destroy.
    by_text: dict[str, dict] = {}
    for d in members:
        k = d.get("text_sha256") or d["doc_id"]
        rec = by_text.setdefault(k, {"doc": d, "copies": []})
        rec["copies"].append(d)
        if d["source_path"] < rec["doc"]["source_path"]:
            rec["doc"] = d

    def version_key(d: dict) -> tuple:
        """Draft order where the filename says it; otherwise path order. A filename is a
        weak signal and this is a presentation detail — the diff content is the finding,
        not the arrow direction."""
        name = Path(d["source_path"]).name.lower()
        m = re.search(r"draft\s*(\d+)", name)
        if m:
            return (0, int(m.group(1)), name)
        if "execut" in name or "final" in name or "signed" in name:
            return (1, 0, name)
        return (0, 99, name)

    uniq = sorted(by_text.values(), key=lambda r: version_key(r["doc"]))
    ds = [r["doc"] for r in uniq]
    print(f"\n  group {group}: {len(members)} documents, "
          f"{len(ds)} distinct text(s)")
    for r in uniq:
        d = r["doc"]
        held = sorted({c.get("custodian") or "?" for c in r["copies"]})
        print(f"    {d['doc_id']}  {d['source_path']}")
        if len(r["copies"]) > 1:
            print(f"        ({len(r['copies'])} identical copies, held by "
                  f"{', '.join(held)})")
    findings = []
    for a, b in zip(ds, ds[1:]):
        ta = doc_text(work, a["doc_id"]).splitlines()
        tb = doc_text(work, b["doc_id"]).splitlines()
        diff = list(difflib.unified_diff(ta, tb, lineterm="",
                                         fromfile=a["doc_id"], tofile=b["doc_id"]))
        removed = [l[1:].strip() for l in diff
                   if l.startswith("-") and not l.startswith("---") and l[1:].strip()]
        added = [l[1:].strip() for l in diff
                 if l.startswith("+") and not l.startswith("+++") and l[1:].strip()]
        print(f"\n  --- {a['doc_id']} -> {b['doc_id']} "
              f"({len(removed)} removed, {len(added)} added)")
        for l in removed[:6]:
            print(f"      - {l[:92]}")
        for l in added[:6]:
            print(f"      + {l[:92]}")
        # a removed clause reference is the finding shape that matters in contracts
        for l in removed:
            c = CLAUSE_RE.search(l)
            money = MONEY_RE.search(l)
            if c or money:
                findings.append({
                    "group": group, "from": a["doc_id"], "to": b["doc_id"],
                    "removed_text": l[:300],
                    "clause": c.group(0) if c else None,
                    "amount": money.group(0) if money else None,
                    "finding": "substantive text removed between versions"})
    write_jsonl(work / "lineage_findings.jsonl", findings)
    print(f"\n  substantive removals: {len(findings)}")
    for f in findings[:6]:
        print(f"      {f['from']} -> {f['to']}  "
              f"{f['clause'] or ''} {f['amount'] or ''}".rstrip())
        print(f"          {f['removed_text'][:88]}")
    print(f"\n  wrote {work / 'lineage_findings.jsonl'}")
    print("\n  Near-duplicate grouping is a REVIEW-EFFICIENCY tool and a FINDINGS tool.")
    print("  Teams use the first and forget the second. The clause that disappeared")
    print("  between draft and execution is the thing you were hired to find.")
    return 0


# ----------------------------------------------------------------- 6. collection leads
REFERENCE_RE = re.compile(
    r"\b(?:attached|attaching|enclosed|per the|see the|as set out in|referenced in|"
    r"pursuant to)\s+(?:the\s+)?([a-z][a-z \-]{2,38}?)\b(?=[\s,.;:]|$)", re.I)
NAMED_DOC_RE = re.compile(
    r"\b((?:side|cover|engagement|comfort|retention)\s+letter"
    r"|(?:board|audit|committee)\s+(?:minutes|memo|memorandum|deck)"
    r"|redline|term\s+sheet|schedule\s+[A-Z0-9]|exhibit\s+[A-Z0-9]|appendix\s+[A-Z0-9])\b",
    re.I)


def cmd_leads(work: Path) -> int:
    """Documents referenced in the collection but absent from it.

    The highest-value output of an investigation is often a list of documents you do not
    have. Search cannot produce it: the thing you are looking for contains no keyword
    because it contains nothing — it is not there.
    """
    cat = load_catalog(work)
    have_names = {Path(d["source_path"]).name.lower() for d in cat}
    have_text = {d["doc_id"]: None for d in cat}
    leads: dict[str, dict] = {}

    for d in cat:
        text = doc_text(work, d["doc_id"])
        if not text:
            continue
        for m in NAMED_DOC_RE.finditer(text):
            phrase = re.sub(r"\s+", " ", m.group(1)).strip().lower()
            lo, hi = max(0, m.start() - 90), min(len(text), m.end() + 90)
            # is there a file in the collection whose name plausibly matches?
            stub = phrase.replace(" ", "_")
            present = any(stub in n or phrase.replace(" ", "") in n.replace("_", "")
                          for n in have_names)
            rec = leads.setdefault(phrase, {
                "referenced_as": phrase, "mentions": 0, "present_in_collection": present,
                "examples": []})
            rec["mentions"] += 1
            rec["present_in_collection"] = rec["present_in_collection"] or present
            if len(rec["examples"]) < 4:
                rec["examples"].append({
                    "doc_id": d["doc_id"], "custodian": d.get("custodian"),
                    "sent_utc": (d.get("metadata") or {}).get("sent_utc"),
                    "quote": re.sub(r"\s+", " ", text[lo:hi]).strip(),
                    "char_span": [m.start(), m.end()]})

    missing = sorted((r for r in leads.values() if not r["present_in_collection"]),
                     key=lambda r: -r["mentions"])
    for r in missing:
        r["finding"] = "referenced but absent — collection lead"
        r["next_step"] = ("ask the producing party for this document by name, citing the "
                          "quotes below; or confirm it was withheld and on what basis")
    write_jsonl(work / "collection_leads.jsonl", missing)

    # the load file is the other source of leads, and Lab 01 already found those
    man = work / "manifest.json"
    from_loadfile = []
    if man.exists():
        lf = (json.loads(man.read_text()).get("load_file") or {})
        from_loadfile = lf.get("in_load_file_not_collected") or []

    print(f"\n  named-document references found : {len(leads)}")
    print(f"  referenced but ABSENT            : {len(missing)}\n")
    for r in missing[:8]:
        print(f"    {r['referenced_as']!r} — {r['mentions']} mention(s)")
        for ex in r["examples"][:2]:
            print(f"        {ex['doc_id']} ({ex['custodian']}, "
                  f"{(ex['sent_utc'] or '')[:10]}): …{ex['quote'][:84]}…")
    if from_loadfile:
        print(f"\n  plus {len(from_loadfile)} row(s) from the producer's LOAD FILE with "
              f"no native:")
        for r in from_loadfile:
            print(f"    {r.get('begbates')}–{r.get('endbates')}  "
                  f"{r.get('native_path')}  (custodian {r.get('custodian')})")
    print(f"\n  wrote {work / 'collection_leads.jsonl'}")
    print("\n  Two independent routes to the same lead — the text says it exists, and")
    print("  the producer's own load file lists it — is the strongest version of this")
    print("  finding. One route is a question. Two is a letter to opposing counsel.")
    return 0


# ------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("entities", "resolve", "threads", "timeline", "diff", "leads"):
        s = sub.add_parser(name)
        s.add_argument("--work", default="../work")
        if name == "entities":
            s.add_argument("--llm", action="store_true",
                           help="add LLM entities (verified against the text)")
            s.add_argument("--limit", type=int, default=0,
                           help="first N documents only (for a fast demo)")
        if name == "timeline":
            s.add_argument("--pair", help="comma-separated local-parts, e.g. aray,jdoe")
            s.add_argument("--gap-sigma", type=float, default=2.5)
            s.add_argument("--responsive", action="store_true",
                           help="scope to Lab 05's responsive set (recommended)")
            s.add_argument("--terms",
                           help="comma-separated terms a message must contain")
            s.add_argument("--thread",
                           help="scope to one conversation: a subject fragment or a "
                                "doc_id (this is where conversation gaps show up)")
        if name == "diff":
            s.add_argument("--group", help="near-dupe group id, e.g. ND-0001")
    args = ap.parse_args()
    work = Path(args.work).resolve()

    if args.cmd == "entities":
        return cmd_entities(work, args.llm, args.limit)
    if args.cmd == "resolve":
        return cmd_resolve(work)
    if args.cmd == "threads":
        return cmd_threads(work)
    if args.cmd == "timeline":
        return cmd_timeline(work, args.pair, args.gap_sigma, args.responsive,
                            args.terms, args.thread)
    if args.cmd == "diff":
        return cmd_diff(work, args.group)
    if args.cmd == "leads":
        return cmd_leads(work)
    return 2


if __name__ == "__main__":
    sys.exit(main())
