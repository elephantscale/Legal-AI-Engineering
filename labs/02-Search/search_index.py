#!/usr/bin/env python3
"""search_index.py — Lab 02: the eDiscovery search index (Module 3).

Builds a dual-field full-text index over Lab 01's catalog and runs real eDiscovery-style
searches: phrase, proximity, wildcard, boolean, fuzzy, with custodian and date filters,
family-aware results, and a hit report.

    python3 search_index.py build   --work ../work
    python3 search_index.py search  --work ../work -q '"material adverse change"'
    python3 search_index.py search  --work ../work -q 'indemnification' --fuzzy
    python3 search_index.py search  --work ../work -q 'restatement' \
                                    --custodian jdoe,aray --from 2026-02-01 --to 2026-06-30
    python3 search_index.py hitreport --work ../work --terms terms.txt

Why SQLite FTS5 and not Solr: FTS5 is the same primitive — an inverted index with BM25
ranking — and it installs in zero seconds, so this lab is never blocked. Production
eDiscovery runs Lucene/Solr (that is what FreeEed uses). What you learn here transfers
directly; what changes is the ops, not the ideas.

Two fields, on purpose (Module 3):
    text_analyzed   stemmed, lowercased, stopword-aware  -> recall
    text_keyword    untouched                            -> exact names, Bates, defined terms
Searching only the first loses `shall` vs `may`. Searching only the second loses
`terminate` vs `termination`. Legal search needs both.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# Legal-aware stopword list: the usual English list MINUS the words that carry
# obligations. "Lessee shall not" and "Lessee may not" are different contracts.
LEGAL_KEEP = {"shall", "may", "must", "will", "not", "no", "nor", "any", "all",
              "without", "except", "unless", "including"}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
    "has", "have", "he", "her", "his", "i", "if", "in", "into", "is", "it", "its",
    "of", "on", "or", "our", "re", "she", "that", "the", "their", "them", "there",
    "these", "they", "this", "to", "was", "we", "were", "what", "when", "which",
    "who", "with", "you", "your",
} - LEGAL_KEEP


def stem(word: str) -> str:
    """A deliberately crude suffix stripper.

    Crude is the point: you can read it, so you can predict what it will and will not
    match. A black-box stemmer that silently mangles defined terms is worse than a simple
    one you understand. Note it never touches words under 5 characters, which protects
    most defined terms and all Bates prefixes.
    """
    if len(word) < 5:
        return word
    for suf in ("ications", "ication", "ingly", "ments", "ment", "ions", "ion",
                "ing", "ies", "ied", "ers", "er", "ed", "es", "s"):
        if word.endswith(suf) and len(word) - len(suf) >= 4:
            base = word[: -len(suf)]
            return base + "y" if suf in ("ies", "ied") else base
    return word


def analyze(text: str) -> str:
    """Index-time AND query-time analysis. The same function, always.

    The classic bug in legal search is stemming one side only, then wondering why
    `clause` misses `clauses`. One function, called from both paths, makes it impossible.
    """
    toks = re.findall(r"[a-z0-9][a-z0-9'\-\.]*", text.lower())
    return " ".join(stem(t) for t in toks if t not in STOPWORDS)


# ------------------------------------------------------------------------------ build
SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog (
    doc_id        TEXT PRIMARY KEY,
    parent_id     TEXT,
    family_id     TEXT,
    custodian     TEXT,
    source_path   TEXT,
    media_type    TEXT,
    extracted_by  TEXT,
    sent_utc      TEXT,
    tz_offset     TEXT,
    subject       TEXT,
    mail_from     TEXT,
    mail_to       TEXT,
    dedupe_status TEXT,
    nd_group      TEXT,
    text_chars    INTEGER
);
CREATE INDEX IF NOT EXISTS ix_custodian ON catalog(custodian);
CREATE INDEX IF NOT EXISTS ix_sent      ON catalog(sent_utc);
CREATE INDEX IF NOT EXISTS ix_family    ON catalog(family_id);

CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(
    doc_id UNINDEXED,
    text_analyzed,
    text_keyword,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""


def build(work: Path) -> dict:
    catalog = work / "catalog.jsonl"
    if not catalog.exists():
        raise SystemExit(f"no catalog at {catalog} — run Lab 01 first")
    db_path = work / "index.sqlite"
    db_path.unlink(missing_ok=True)
    db = sqlite3.connect(db_path)
    db.executescript(SCHEMA)

    rows = 0
    for line in catalog.open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        md = r.get("metadata") or {}
        txt_file = work / "text" / f"{r['doc_id']}.txt"
        text = txt_file.read_text(encoding="utf-8") if txt_file.exists() else ""
        db.execute(
            "INSERT INTO catalog VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["doc_id"], r.get("parent_id"), r.get("family_id"), r.get("custodian"),
             r.get("source_path"), r.get("media_type"), r.get("extracted_by"),
             md.get("sent_utc"), md.get("tz_offset"), md.get("subject"),
             md.get("from"), json.dumps(md.get("to") or []),
             (r.get("dedupe") or {}).get("status"),
             (r.get("dedupe") or {}).get("near_dupe_group"), r.get("text_chars", 0)))
        searchable = "\n".join(filter(None, [md.get("subject"), text]))
        db.execute("INSERT INTO fts (doc_id, text_analyzed, text_keyword) VALUES (?,?,?)",
                   (r["doc_id"], analyze(searchable), searchable.lower()))
        rows += 1
    db.commit()

    # the index is a meaningful fraction of the text it indexes - budget for it
    text_bytes = sum(f.stat().st_size for f in (work / "text").glob("*.txt")) \
        if (work / "text").exists() else 0
    stats = {
        "documents_indexed": rows,
        "index_bytes": db_path.stat().st_size,
        "text_bytes": text_bytes,
        "index_overhead": f"{db_path.stat().st_size / text_bytes:.0%}" if text_bytes else "n/a",
        "analyzer": {"stopwords": len(STOPWORDS),
                     "legal_terms_kept": sorted(LEGAL_KEEP),
                     "note": "index-time and query-time analysis use the same function"},
    }
    db.close()
    (work / "index-manifest.json").write_text(json.dumps(stats, indent=2) + "\n")
    return stats


# ----------------------------------------------------------------------------- search
def _lit(token: str) -> str:
    """Wrap a token as an FTS5 string literal.

    Legal text is full of `7.3`, `11.2`, `W/10` and `HOLL0000001` — tokens whose
    punctuation is FTS5 syntax. Quoting every operand is the difference between a working
    search box and a `fts5: syntax error` in front of a client.
    """
    return '"' + token.replace('"', '""') + '"'


def _and_terms(analyzed: str) -> str:
    toks = [t for t in analyzed.split() if t]
    return " ".join(_lit(t) for t in toks)


def to_fts_query(q: str, *, fuzzy: bool = False) -> tuple[str, str]:
    """Translate a lawyer's query into an FTS5 MATCH expression.

    Supported, because these are what actually get run:
        "exact phrase"            -> phrase search on the keyword field
        NEAR(a b, 10) / a W/10 b  -> proximity
        terminat*                 -> prefix / truncation
        AND OR NOT                -> boolean
    Returns (match_expression, which_field).
    """
    q = q.strip()
    # W/n is how lawyers write proximity; FTS5 spells it NEAR(...)
    m = re.match(r'^\s*(\S+)\s+W/(\d+)\s+(\S+)\s*$', q, re.I)
    if m:
        a, n, b = m.group(1), m.group(2), m.group(3)
        return (f'NEAR({_and_terms(analyze(a))} {_and_terms(analyze(b))}, {n})',
                "text_analyzed")
    if q.startswith('"') and q.endswith('"'):
        return q, "text_keyword"          # phrase: never stem, never reorder
    if "*" in q:
        # truncation on the raw text field: quote the stem, keep the trailing *
        parts = [(_lit(t[:-1]) + "*") if t.endswith("*") else _lit(t)
                 for t in q.lower().split() if t]
        return " ".join(parts), "text_keyword"
    if re.search(r"\b(AND|OR|NOT|NEAR)\b", q):
        # boolean: analyze the operands, keep the operators
        parts = re.split(r"\b(AND|OR|NOT|NEAR)\b", q)
        out = []
        for p in parts:
            if p.strip() in ("AND", "OR", "NOT", "NEAR"):
                out.append(p.strip())
            elif p.strip():
                out.append(_and_terms(analyze(p)))
        return " ".join(out), "text_analyzed"
    if fuzzy:
        # FTS5 has no edit distance. Prefix-matching the stem is the cheap, honest
        # approximation, and we say so in the search log rather than pretending.
        base = analyze(q)
        return (" OR ".join(_lit(t[:max(4, len(t) - 2)]) + "*" for t in base.split()),
                "text_analyzed")
    return _and_terms(analyze(q)), "text_analyzed"


def search(work: Path, q: str, *, custodians: list[str] | None = None,
           date_from: str | None = None, date_to: str | None = None,
           fuzzy: bool = False, limit: int = 25, families: bool = True) -> dict:
    db = sqlite3.connect(work / "index.sqlite")
    db.row_factory = sqlite3.Row
    match, field = to_fts_query(q, fuzzy=fuzzy)

    where, params = [f"fts.{field} MATCH ?"], [match]
    if custodians:
        where.append(f"c.custodian IN ({','.join('?' * len(custodians))})")
        params += custodians
    if date_from:
        where.append("(c.sent_utc IS NULL OR c.sent_utc >= ?)")
        params.append(date_from)
    if date_to:
        where.append("(c.sent_utc IS NULL OR c.sent_utc <= ?)")
        params.append(date_to + "T23:59:59Z")

    sql = f"""
        SELECT c.doc_id, c.custodian, c.family_id, c.subject, c.source_path,
               c.sent_utc, c.extracted_by, c.dedupe_status, c.nd_group,
               bm25(fts) AS score
          FROM fts JOIN catalog c ON c.doc_id = fts.doc_id
         WHERE {' AND '.join(where)}
         ORDER BY score
         LIMIT ?
    """
    hits = [dict(r) for r in db.execute(sql, params + [limit])]

    # Family-aware results: a hit surfaces its whole family, not an orphan page.
    # If the parent email is responsive, the attachments generally go out with it.
    family_rows: list[dict] = []
    if families and hits:
        fams = sorted({h["family_id"] for h in hits if h["family_id"]})
        if fams:
            fsql = (f"SELECT doc_id, custodian, family_id, subject, source_path "
                    f"FROM catalog WHERE family_id IN ({','.join('?' * len(fams))}) "
                    f"ORDER BY family_id, doc_id")
            family_rows = [dict(r) for r in db.execute(fsql, fams)]

    # The OCR honesty check from Module 3: never report a clean negative on OCR'd text.
    ocr_total = db.execute(
        "SELECT COUNT(*) FROM catalog WHERE extracted_by LIKE '%ocr%' "
        "OR extracted_by LIKE 'tesseract%'").fetchone()[0]
    db.close()

    result = {
        "query": q,
        "fts_match": match,
        "field": field,
        "fuzzy": fuzzy,
        "filters": {"custodians": custodians, "date_from": date_from,
                    "date_to": date_to},
        "hit_count": len(hits),
        "hits": hits,
        "family_count": len({h["family_id"] for h in hits if h["family_id"]}),
        "family_documents": family_rows,
        "ocr_caveat": (
            f"{ocr_total} document(s) in this index were produced by OCR. "
            f"Keyword search over OCR'd text is exact and OCR is not: a reported zero "
            f"is a claim about the index, not about the world. Re-run with --fuzzy, and "
            f"disclose this caveat in any search report."
            if ocr_total else None),
    }
    if fuzzy:
        result["fuzzy_note"] = (
            "FTS5 has no edit distance. --fuzzy prefix-matches a shortened stem, which "
            "approximates it. State the method in your search log; do not call it "
            "'fuzzy matching' without saying what you actually ran.")
    return result


# ------------------------------------------------------------------------- hit report
def hit_report(work: Path, terms: list[str]) -> dict:
    """term -> document count -> family count.

    This table, not the documents, is frequently the deliverable. Search terms get
    *negotiated*: one side proposes, the other runs them and says "that term alone pulls
    340,000 documents, it is overbroad." Your system has to produce this on demand.
    """
    rows = []
    for t in terms:
        r = search(work, t, limit=100000, families=True)
        rows.append({"term": t, "fts_match": r["fts_match"], "field": r["field"],
                     "documents": r["hit_count"], "families": r["family_count"]})
    rows.sort(key=lambda x: -x["documents"])
    return {"report": rows,
            "total_terms": len(rows),
            "note": "Document count and FAMILY count both matter: families are what "
                    "actually get reviewed and produced."}


# ------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build the index from Lab 01's catalog")
    b.add_argument("--work", default="../work")

    s = sub.add_parser("search", help="run one query")
    s.add_argument("--work", default="../work")
    s.add_argument("-q", "--query", required=True)
    s.add_argument("--custodian", help="comma-separated list")
    s.add_argument("--from", dest="date_from", help="YYYY-MM-DD")
    s.add_argument("--to", dest="date_to", help="YYYY-MM-DD")
    s.add_argument("--fuzzy", action="store_true")
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--json", action="store_true", help="full JSON, for your search log")

    h = sub.add_parser("hitreport", help="term -> document count -> family count")
    h.add_argument("--work", default="../work")
    h.add_argument("--terms", default="terms.txt")

    args = ap.parse_args()
    work = Path(args.work).resolve()

    if args.cmd == "build":
        stats = build(work)
        print(json.dumps(stats, indent=2))
        print(f"\nindex: {work / 'index.sqlite'}")
        return 0

    if args.cmd == "search":
        res = search(work, args.query,
                     custodians=args.custodian.split(",") if args.custodian else None,
                     date_from=args.date_from, date_to=args.date_to,
                     fuzzy=args.fuzzy, limit=args.limit)
        if args.json:
            print(json.dumps(res, indent=2))
            return 0
        print(f"\nquery      : {res['query']}")
        print(f"fts match  : {res['fts_match']}   (field: {res['field']})")
        print(f"filters    : {json.dumps(res['filters'])}")
        print(f"hits       : {res['hit_count']} documents in {res['family_count']} families\n")
        for h2 in res["hits"]:
            subj = (h2["subject"] or Path(h2["source_path"]).name)[:58]
            print(f"  {h2['doc_id']}  {h2['custodian']:<8} {h2['sent_utc'] or '-':<21} "
                  f"{subj}")
            if h2["extracted_by"] and "tesseract" in (h2["extracted_by"] or ""):
                print(f"              ^ OCR'd text (engine {h2['extracted_by']})")
        if res["ocr_caveat"]:
            print(f"\n  ! {res['ocr_caveat']}")
        if res.get("fuzzy_note"):
            print(f"\n  ! {res['fuzzy_note']}")
        return 0

    if args.cmd == "hitreport":
        tf = Path(args.terms)
        if not tf.is_absolute():
            tf = Path(__file__).parent / args.terms
        terms = [ln.strip() for ln in tf.read_text().splitlines()
                 if ln.strip() and not ln.startswith("#")]
        rep = hit_report(work, terms)
        print(f"\n{'term':<42} {'docs':>6} {'families':>9}")
        print("-" * 60)
        for r in rep["report"]:
            print(f"{r['term'][:42]:<42} {r['documents']:>6} {r['families']:>9}")
        out = work / "hit-report.json"
        out.write_text(json.dumps(rep, indent=2) + "\n")
        print(f"\n{rep['note']}\nwrote {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
