#!/usr/bin/env python3
"""ingest_reference.py — the worked answer to Lab 01's four TODOs.

Read your own attempt first. Then read this, and argue with it.

It subclasses `Ingester` from `ingest.py` and overrides exactly the four methods the lab
leaves open, so the diff between "starter" and "done" is the lesson:

    TODO 1  ocr_image              — local OCR, no network
    TODO 2  apply_dedupe           — a documented policy, not a cleanup
    TODO 3  group_near_duplicates  — MinHash shingling; GROUP, don't suppress
    TODO 4  reconcile_load_file    — read .dat/.opt and find what is missing

Run it exactly like the starter:

    python3 ingest_reference.py --corpus ../assets/corpus --out ../work
    python3 ingest_reference.py --corpus ../assets/corpus --out ../work --reocr
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest import MATTER, Ingester, read_dat, read_opt   # noqa: E402

SHINGLE = 5          # words per shingle
SKETCH = 128         # MinHash sketch size


class ReferenceIngester(Ingester):

    # ---------------------------------------------------------------- TODO 1
    def ocr_image(self, data: bytes) -> tuple[str, str]:
        """Local OCR via the tesseract CLI. No network — Module 2, rule 2.

        Note what we return on failure: empty text and an engine string saying so, which
        makes the caller log a processing *exception* rather than silently produce a
        document with no text. A blank scan and a failed OCR look identical in the
        output and must not look identical in the record.
        """
        if self._ocr_engine == "none":
            return "", "ocr-unavailable"
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as fh:
                fh.write(data)
                tmp = fh.name
            proc = subprocess.run(
                ["tesseract", tmp, "stdout", "--psm", "3"],
                capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                return "", "ocr-failed"
            return proc.stdout, self._ocr_engine
        except (OSError, subprocess.SubprocessError):
            return "", "ocr-failed"
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass

    # ---------------------------------------------------------------- TODO 2
    def apply_dedupe(self) -> None:
        """Apply the policy and write down what it did.

        The three policies differ in one thing: the key. That is the whole
        implementation. The *consequence* is what matters:

          global         cheapest; collapses six custodians' copies into one, which
                         destroys the fact that six people had the document
          per-custodian  keeps possession, costs more review
          none           suppresses nothing; you will review the same document N times

        Possession is frequently more probative than content. "Who had the memo" is a
        question you cannot answer after a global dedupe.
        """
        policy = self.dedupe_policy
        seen: dict[tuple, str] = {}
        counts = {"unique": 0, "duplicate": 0}
        for d in self.docs:
            if policy == "none":
                key = (d.doc_id,)
            elif policy == "global":
                key = (d.native_sha256,)
            else:                                     # per-custodian
                key = (d.custodian, d.native_sha256)
            first = seen.get(key)
            if first is None:
                seen[key] = d.doc_id
                d.dedupe = {"policy": policy, "status": "unique",
                            "duplicate_of": None, "key": "|".join(map(str, key))[:80]}
                counts["unique"] += 1
            else:
                d.dedupe = {"policy": policy, "status": "duplicate",
                            "duplicate_of": first,
                            "key": "|".join(map(str, key))[:80]}
                counts["duplicate"] += 1
        self.dedupe_counts = counts

    # ---------------------------------------------------------------- TODO 3
    def group_near_duplicates(self, threshold: float = 0.80) -> None:
        """MinHash shingling, then union-find. Grouping only — nothing is suppressed.

        Why group and not suppress: v1 and v7 of a contract differ in exactly the clause
        that matters. The 6% *is* the finding (Module 9). A near-dupe group is an
        instruction to a reviewer: read these together and diff them.
        """
        sketches: dict[str, set[int]] = {}
        for d in self.docs:
            sk = _minhash(d.text)
            if sk:
                sketches[d.doc_id] = sk

        parent: dict[str, str] = {k: k for k in sketches}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        # O(n^2) on purpose: it is readable, and it is fine at lab scale. At production
        # scale you band the sketches (LSH) instead — same similarity, sublinear pairs.
        ids = sorted(sketches)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                sa, sb = sketches[a], sketches[b]
                inter = len(sa & sb)
                if inter and inter / len(sa | sb) >= threshold:
                    union(a, b)

        groups: dict[str, list[str]] = {}
        for doc_id in ids:
            groups.setdefault(find(doc_id), []).append(doc_id)

        gid = 0
        assigned: dict[str, str] = {}
        for members in groups.values():
            if len(members) < 2:
                continue
            gid += 1
            label = f"ND-{gid:04d}"
            for m in members:
                assigned[m] = label
        for d in self.docs:
            d.dedupe["near_dupe_group"] = assigned.get(d.doc_id)
        self.near_dupe_groups = gid

    # ---------------------------------------------------------------- TODO 4
    def reconcile_load_file(self) -> dict:
        """Read the .dat / .opt pair and reconcile it against what we actually found.

        The reconciliation is the point, not the parsing. A row in the producer's load
        file with no corresponding native in the collection is a **collection lead** —
        a document that exists, is listed, and was not given to you. Report it.
        """
        prod = self.corpus / "production"
        dat_files = sorted(prod.glob("*.dat"))
        opt_files = sorted(prod.glob("*.opt"))
        if not dat_files:
            return {"status": "no load file found", "load_file_rows": 0}

        rows: list[dict] = []
        for f in dat_files:
            rows.extend(read_dat(f))
        pages: list[dict] = []
        for f in opt_files:
            pages.extend(read_opt(f))

        # index what we collected by basename, which is all a load file gives us
        collected: dict[str, list[str]] = {}
        for d in self.docs:
            collected.setdefault(Path(d.source_path).name.lower(), []).append(d.doc_id)
        for e in self.exceptions:
            collected.setdefault(Path(e.source_path).name.lower(), []).append(e.doc_id)

        matched, missing = [], []
        for r in rows:
            native = (r.get("NATIVE_PATH") or "").replace("\\", "/")
            base = Path(native).name.lower()
            hit = collected.get(base)
            entry = {"begbates": r.get("BEGBATES"), "endbates": r.get("ENDBATES"),
                     "custodian": r.get("CUSTODIAN"), "native_path": native,
                     "matched_doc_ids": hit or []}
            (matched if hit else missing).append(entry)

        images_present = {p.name.lower()
                          for p in (prod / "IMAGES").rglob("*") if p.is_file()}
        pages_missing = [p["page_id"] for p in pages
                         if Path(p["path"].replace("\\", "/")).name.lower()
                         not in images_present]

        out = {
            "dat_files": [f.name for f in dat_files],
            "opt_files": [f.name for f in opt_files],
            "load_file_rows": len(rows),
            "matched": len(matched),
            "in_load_file_not_collected": missing,
            "opt_pages": len(pages),
            "opt_documents": sum(1 for p in pages if p["doc_start"]),
            "opt_pages_with_no_image_file": pages_missing,
            "delimiters": {"field": "\\x14 (ASCII 20)", "quote": "\\xfe (ASCII 254)",
                           "encoding_used": "cp1252 (sniffed: no BOM present)"},
        }
        if missing:
            out["COLLECTION_LEAD"] = (
                f"{len(missing)} row(s) are listed in the producer's load file with no "
                f"corresponding native in the collection. Report this to counsel: these "
                f"documents exist and were not produced to you. "
                f"({', '.join(m['native_path'] for m in missing)})")
        return out


def _minhash(text: str, shingle: int = SHINGLE, sketch: int = SKETCH) -> set[int]:
    """The N smallest 64-bit hashes of the document's word shingles."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    if len(words) < shingle:
        return set()
    hashes = set()
    for i in range(len(words) - shingle + 1):
        gram = " ".join(words[i:i + shingle])
        hashes.add(int.from_bytes(
            hashlib.blake2b(gram.encode(), digest_size=8).digest(), "big"))
    return set(sorted(hashes)[:sketch])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default="../assets/corpus")
    ap.add_argument("--out", default="../work")
    ap.add_argument("--dedupe", choices=["none", "global", "per-custodian"],
                    default="per-custodian")
    ap.add_argument("--matter", default=MATTER,
                    help="matter id stamped on every record (default: %(default)s)")
    ap.add_argument("--nd-threshold", type=float, default=0.60,
                    help="near-duplicate similarity threshold (default 0.60)")
    ap.add_argument("--reocr", action="store_true")
    ap.add_argument("--tika-url", default=os.environ.get("TIKA_URL"))
    args = ap.parse_args()

    corpus = Path(args.corpus).resolve()
    if not corpus.exists():
        print(f"error: corpus not found at {corpus}\n"
              f"generate it first:  python3 ../assets/make_corpus.py", file=sys.stderr)
        return 2

    ing = ReferenceIngester(corpus, Path(args.out).resolve(), dedupe=args.dedupe,
                            reocr=args.reocr, tika_url=args.tika_url,
                            matter=args.matter)
    for p in sorted(corpus.rglob("*.ocr.txt")):
        ing.ocr_sidecars[p.relative_to(corpus).as_posix()[:-len(".ocr.txt")]] = \
            p.read_text(encoding="utf-8", errors="replace")
    ing.walk()
    ing.apply_dedupe()
    ing.group_near_duplicates(args.nd_threshold)
    manifest = ing.write()

    lf = manifest["load_file"]
    print(f"\ningested   : {manifest['counts']['documents']} documents")
    print(f"exceptions : {manifest['counts']['exceptions']}  <- look at these")
    print(f"dedupe     : {args.dedupe}  "
          f"unique={ing.dedupe_counts['unique']} duplicate={ing.dedupe_counts['duplicate']}")
    print(f"near-dupes : {ing.near_dupe_groups} group(s)")
    print(f"ocr        : {manifest['policies']['ocr']} (engine: {ing._ocr_engine})")
    print(f"load file  : {lf.get('load_file_rows')} rows, {lf.get('matched')} matched, "
          f"{len(lf.get('in_load_file_not_collected', []))} missing")
    if lf.get("COLLECTION_LEAD"):
        print(f"\n  !! {lf['COLLECTION_LEAD']}")
    print(f"\nwrote {args.out}/catalog.jsonl, exceptions.jsonl, manifest.json")
    print(f"\n{manifest['honesty_check']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
