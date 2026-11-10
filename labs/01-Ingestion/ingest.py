#!/usr/bin/env python3
"""ingest.py — Lab 01: the ingestion pipeline (Module 2).

Walk a messy legal collection, extract text, OCR the scans, hash the natives, apply a
*documented* dedupe policy, group near-duplicates, reconcile against the load file, and
emit the catalog every later lab reads.

    python3 ingest.py --corpus ../assets/corpus --out ../work
    python3 ingest.py --corpus ../assets/corpus --out ../work --dedupe global
    python3 ingest.py --corpus ../assets/corpus --out ../work --reocr

Outputs (into --out):
    catalog.jsonl      one row per document. The contract with Labs 02-07.
    exceptions.jsonl   every document that did NOT process, and why. First-class output.
    manifest.json      what ran, with what policy, over what input.

Three rules this file obeys, because the engine it mirrors obeys them (Module 2):
    1. Never modify the source.          -> everything is opened read-only
    2. No outbound network calls.        -> nothing here resolves a hostname
    3. Log everything, append-only.      -> catalog + exceptions are append-only JSONL

The deliberate gaps, for you to fill:
    * TODO 1 — OCR the image-only scans
    * TODO 2 — choose and apply the dedupe policy
    * TODO 3 — group near-duplicates
    * TODO 4 — reconcile the load file against what you actually found
Each TODO has a reference implementation in `ingest_reference.py`. Read yours first.
"""
from __future__ import annotations

import argparse
import csv
import email
import email.policy
import hashlib
import io
import json
import mailbox
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterator

MATTER = "SYNTHETIC-DEMO-01"
TEXT_TYPES = {".txt", ".md", ".log", ".ocr"}
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- records
@dataclass
class Doc:
    doc_id: str
    # The matter id is on EVERY record, not just the manifest. Matters at one firm are
    # separated by ethical walls, and a document whose row does not say which matter it
    # belongs to cannot be proven to be on the right side of that wall. SAIS-100's legal
    # overlay scores this (D2), and mixing matters is an auto-fail.
    matter: str
    parent_id: str | None
    family_id: str
    custodian: str
    source_path: str
    native_sha256: str
    native_bytes: int
    media_type: str
    extracted_by: str
    text: str = ""
    text_sha256: str = ""
    text_chars: int = 0
    metadata: dict = field(default_factory=dict)
    dedupe: dict = field(default_factory=dict)
    exceptions: list = field(default_factory=list)

    def row(self) -> dict:
        d = asdict(self)
        d.pop("text")                      # text lives in the text store, not the catalog
        return d


@dataclass
class Exception_:
    doc_id: str
    matter: str
    source_path: str
    custodian: str
    reason: str
    tried: str
    next_step: str

    def row(self) -> dict:
        return asdict(self)


# ------------------------------------------------------------------------- the walker
class Ingester:
    """Walks the collection tree. Depth-unlimited, because legal data is recursive."""

    def __init__(self, corpus: Path, out: Path, *, dedupe: str, reocr: bool,
                 tika_url: str | None, matter: str = MATTER):
        self.corpus = corpus
        self.out = out
        self.matter = matter
        self.dedupe_policy = dedupe
        self.reocr = reocr
        self.tika_url = tika_url
        self.docs: list[Doc] = []
        self.exceptions: list[Exception_] = []
        self._n = 0
        self._ocr_engine = self._detect_ocr()
        self.text_dir = out / "text"
        self.ocr_sidecars: dict[str, str] = {}   # source_path -> sidecar text

    # ---- ids -----------------------------------------------------------------
    def next_doc_id(self) -> str:
        self._n += 1
        return f"DOC-{self._n:06d}"

    # ---- OCR -----------------------------------------------------------------
    def _detect_ocr(self) -> str:
        if shutil.which("tesseract"):
            try:
                v = subprocess.run(["tesseract", "--version"], capture_output=True,
                                   text=True, timeout=10).stdout.splitlines()[0]
                return v.strip().replace(" ", "-").lower()
            except (OSError, subprocess.SubprocessError, IndexError):
                pass
        return "none"

    def ocr_image(self, data: bytes) -> tuple[str, str]:
        """OCR an image. Returns (text, engine). Local only — rule 2.

        TODO 1: implement this.
          - write `data` to a temp file
          - run `tesseract <file> stdout` (local, no network)
          - return the text and the engine string (self._ocr_engine)
          - on any failure, return ("", "ocr-failed") so the caller logs an exception
        """
        return "", "TODO-1-not-implemented"

    # ---- extraction ----------------------------------------------------------
    def extract(self, name: str, data: bytes) -> tuple[str, str, list[str]]:
        """Return (text, extracted_by, problems). Dispatch on extension, then sniff."""
        ext = Path(name).suffix.lower()
        problems: list[str] = []

        if not data:
            return "", "none", ["zero-byte file"]

        if ext in TEXT_TYPES or ext == ".csv":
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1", errors="replace")
                problems.append("non-utf8 bytes; decoded as latin-1")
            if ext == ".csv":
                # keep CSV readable as text, headers included (a row without its
                # header is noise - Module 4)
                try:
                    rdr = list(csv.reader(io.StringIO(text)))
                    if rdr:
                        head = rdr[0]
                        text = "\n".join(
                            " | ".join(f"{h}={v}" for h, v in zip(head, r))
                            for r in rdr[1:]) or text
                except csv.Error:
                    problems.append("csv parse failed; kept raw text")
            return text, "builtin-text", problems

        if ext in IMAGE_TYPES:
            if self.reocr:
                text, engine = self.ocr_image(data)
                if not text.strip():
                    problems.append("OCR produced no text")
                return text, engine, problems
            return "", "deferred-to-sidecar", problems

        if ext == ".pdf":
            text, engine, probs = self._extract_pdf(data)
            return text, engine, problems + probs

        if ext in (".docx", ".xlsx", ".pptx"):
            text, engine, probs = self._extract_ooxml(data)
            return text, engine, problems + probs

        if self.tika_url:
            text, engine, probs = self._extract_tika(name, data)
            return text, engine, problems + probs

        return "", "unsupported", [f"no handler for '{ext or 'no extension'}'"]

    def _extract_pdf(self, data: bytes) -> tuple[str, str, list[str]]:
        """Text layer first; OCR only if there is none (Module 2's decision ladder)."""
        try:
            from pypdf import PdfReader
        except ImportError:
            return "", "unsupported", ["pypdf not installed (pip install pypdf)"]
        try:
            rdr = PdfReader(io.BytesIO(data))
            text = "\n".join((p.extract_text() or "") for p in rdr.pages)
        except Exception as e:                      # a hostile parser, as promised
            return "", "pypdf-failed", [f"pdf parse failed: {type(e).__name__}"]
        if text.strip():
            return text, "pypdf", []
        return "", "pdf-image-only", ["PDF has no text layer; needs OCR"]

    def _extract_ooxml(self, data: bytes) -> tuple[str, str, list[str]]:
        """Pull the shared strings / document text straight out of the OOXML zip."""
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            return "", "ooxml-failed", ["not a valid OOXML container (truncated?)"]
        parts = [n for n in z.namelist()
                 if n.endswith(".xml") and ("document" in n or "sharedStrings" in n
                                            or "slide" in n or "sheet" in n)]
        chunks = []
        for n in parts:
            try:
                xml = z.read(n).decode("utf-8", errors="replace")
            except KeyError:
                continue
            chunks.append(re.sub(r"<[^>]+>", " ", xml))
        text = re.sub(r"\s+", " ", " ".join(chunks)).strip()
        return text, "builtin-ooxml", [] if text else ["no text found in OOXML parts"]

    def _extract_tika(self, name: str, data: bytes) -> tuple[str, str, list[str]]:
        """Optional: a local tika-server. Treat it as hostile — timeout and move on."""
        import urllib.request
        try:
            req = urllib.request.Request(
                f"{self.tika_url.rstrip('/')}/tika", data=data, method="PUT",
                headers={"Accept": "text/plain"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace"), "tika-server", []
        except Exception as e:
            return "", "tika-failed", [f"tika error: {type(e).__name__}"]

    # ---- the tree ------------------------------------------------------------
    def walk(self) -> None:
        for path in sorted(self.corpus.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(self.corpus).as_posix()
            if rel.startswith("_groundtruth/"):
                continue                       # labels are not evidence
            if rel.startswith("production/"):
                continue                       # handled by the load-file reconciliation
            data = path.read_bytes()           # rule 1: read-only
            self.handle(rel, data, parent_id=None, family_id=None,
                        custodian=self.custodian_of(rel))

    @staticmethod
    def custodian_of(path: str) -> str:
        m = re.search(r"custodian_([a-z0-9]+)", path)
        if m:
            return m.group(1)
        if path.startswith("exceptions_src/"):
            return "unknown"
        return "unknown"

    def handle(self, display_path: str, data: bytes, *, parent_id: str | None,
               family_id: str | None, custodian: str) -> None:
        name = display_path.rsplit("/", 1)[-1]
        ext = Path(name).suffix.lower()

        # --- containers recurse, they are not documents -----------------------
        if ext == ".zip":
            self.handle_zip(display_path, data, parent_id, family_id, custodian)
            return
        if ext in (".mbox",):
            self.handle_mbox(display_path, data, custodian)
            return
        if ext == ".eml":
            self.handle_message(display_path, email.message_from_bytes(
                data, policy=email.policy.default), parent_id, family_id, custodian)
            return
        # the vendor's OCR sidecar is not a document; it is the text of its sibling
        if name.endswith(".ocr.txt"):
            self.ocr_sidecars[display_path[:-len(".ocr.txt")]] = \
                data.decode("utf-8", errors="replace")
            return

        self.emit(display_path, data, parent_id=parent_id, family_id=family_id,
                  custodian=custodian)

    def handle_zip(self, display_path: str, data: bytes, parent_id: str | None,
                   family_id: str | None, custodian: str) -> None:
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            self.except_(display_path, custodian, "corrupt zip container",
                         "zipfile.ZipFile", "re-request the container from the producer")
            return
        for info in sorted(z.infolist(), key=lambda i: i.filename):
            if info.is_dir():
                continue
            inner = f"{display_path}/{info.filename}"
            try:
                payload = z.read(info)
            except RuntimeError as e:          # password-protected
                self.except_(inner, self.custodian_of(inner) or custodian,
                             "encrypted / password-protected", f"zipfile.read: {e}",
                             "ask the producer for the password; do not guess")
                continue
            except (zipfile.BadZipFile, OSError) as e:
                self.except_(inner, custodian, "unreadable zip member",
                             f"{type(e).__name__}", "re-request from the producer")
                continue
            self.handle(inner, payload, parent_id=parent_id, family_id=family_id,
                        custodian=self.custodian_of(inner) or custodian)

    def handle_mbox(self, display_path: str, data: bytes, custodian: str) -> None:
        with tempfile.NamedTemporaryFile(suffix=".mbox", delete=False) as fh:
            fh.write(data)
            tmp = fh.name
        try:
            box = mailbox.mbox(tmp)
            for i, raw in enumerate(box, 1):
                msg = email.message_from_string(raw.as_string(),
                                                policy=email.policy.default)
                self.handle_message(f"{display_path}/#{i:05d}", msg,
                                    None, None, custodian)
        finally:
            os.unlink(tmp)

    def handle_message(self, display_path: str, msg: EmailMessage,
                       parent_id: str | None, family_id: str | None,
                       custodian: str) -> None:
        """A message is a document AND a container. Its family is itself + attachments."""
        body_parts: list[str] = []
        attachments: list[tuple[str, bytes | EmailMessage, str]] = []
        # NOTE: do NOT use msg.walk() here. walk() descends *into* a message/rfc822
        # part, so a nested message's attachments would be attributed to the outer
        # message as well as to the inner one — double-counting them and putting them
        # in the wrong family. Walk this message's own parts and stop at a nested
        # message, which we then recurse into deliberately, one level at a time.
        for part in _own_parts(msg):
            fname = part.get_filename()
            ctype = part.get_content_type()
            if ctype == "message/rfc822":
                inner = part.get_payload(0) if part.is_multipart() else \
                    email.message_from_string(str(part.get_payload()),
                                              policy=email.policy.default)
                attachments.append((fname or "attached-message.eml", inner, ctype))
            elif fname:
                attachments.append((fname, part.get_payload(decode=True) or b"", ctype))
            elif ctype == "text/plain":
                body_parts.append(part.get_content())

        headers = self.message_metadata(msg)
        body = "\n".join(body_parts)
        raw = msg.as_bytes()
        doc_id = self.emit(display_path, raw, parent_id=parent_id,
                           family_id=family_id, custodian=custodian,
                           override_text=body, extracted_by="builtin-email",
                           extra_metadata=headers,
                           media_type="message/rfc822")
        fam = family_id or f"FAM-{doc_id.split('-')[1]}"
        if doc_id:
            # retro-fix the family id on the parent we just emitted
            self.docs[-1].family_id = fam
        for fname, payload, ctype in attachments:
            child_path = f"{display_path}/{fname}"
            if isinstance(payload, (EmailMessage, email.message.Message)):
                self.handle_message(child_path, payload, parent_id=doc_id,
                                    family_id=fam, custodian=custodian)
            else:
                self.handle(child_path, payload, parent_id=doc_id, family_id=fam,
                            custodian=custodian)

    @staticmethod
    def message_metadata(msg: EmailMessage) -> dict:
        """Store UTC AND the original offset. Timezone bugs break chronologies."""
        md: dict = {}
        raw_date = msg.get("Date")
        if raw_date:
            try:
                dt = parsedate_to_datetime(raw_date)
                md["sent_utc"] = dt.astimezone(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ")
                off = dt.utcoffset()
                if off is not None:
                    total = int(off.total_seconds())
                    sign = "+" if total >= 0 else "-"
                    md["tz_offset"] = f"{sign}{abs(total)//3600:02d}:{abs(total)%3600//60:02d}"
            except (TypeError, ValueError):
                md["sent_raw"] = raw_date
                md["date_problem"] = "unparseable Date header"
        for h, key in (("From", "from"), ("Subject", "subject"),
                       ("Message-ID", "message_id"), ("In-Reply-To", "in_reply_to")):
            if msg.get(h):
                md[key] = _unfold(msg.get(h))
        for h, key in (("To", "to"), ("Cc", "cc"), ("Bcc", "bcc")):
            if msg.get(h):
                md[key] = [a.strip() for a in _unfold(msg.get(h)).split(",") if a.strip()]
        if msg.get("References"):
            md["references"] = _unfold(msg.get("References")).split()
        return md

    # ---- emit ----------------------------------------------------------------
    def emit(self, display_path: str, data: bytes, *, parent_id: str | None,
             family_id: str | None, custodian: str,
             override_text: str | None = None, extracted_by: str | None = None,
             extra_metadata: dict | None = None,
             media_type: str | None = None) -> str | None:
        name = display_path.rsplit("/", 1)[-1]
        if override_text is None:
            text, engine, problems = self.extract(name, data)
        else:
            text, engine, problems = override_text, extracted_by or "builtin", []

        # image with no re-OCR: adopt the producer's OCR sidecar if we have one
        if not text and Path(name).suffix.lower() in IMAGE_TYPES:
            key = display_path.rsplit(".", 1)[0]
            sidecar = self.ocr_sidecars.get(key)
            if sidecar:
                text, engine = sidecar, "producer-ocr-sidecar"
                problems = [p for p in problems if "OCR produced no text" not in p]

        doc_id = self.next_doc_id()
        if not text.strip():
            reason = problems[0] if problems else "no extractable text"
            self.except_(display_path, custodian, reason,
                         f"extractor={engine}",
                         "OCR, convert, or route to a human — do not drop silently",
                         doc_id=doc_id)
            return None

        doc = Doc(
            doc_id=doc_id,
            matter=self.matter,
            parent_id=parent_id,
            family_id=family_id or f"FAM-{doc_id.split('-')[1]}",
            custodian=custodian,
            source_path=display_path,
            native_sha256=hashlib.sha256(data).hexdigest(),
            native_bytes=len(data),
            media_type=media_type or guess_media_type(name),
            extracted_by=engine,
            text=text,
            text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            text_chars=len(text),
            metadata=extra_metadata or {},
            exceptions=problems,
        )
        self.docs.append(doc)
        return doc_id

    def except_(self, path: str, custodian: str, reason: str, tried: str,
                next_step: str, doc_id: str | None = None) -> None:
        self.exceptions.append(Exception_(
            doc_id=doc_id or self.next_doc_id(), matter=self.matter,
            source_path=path,
            custodian=custodian, reason=reason, tried=tried, next_step=next_step))

    # ---- dedupe --------------------------------------------------------------
    def apply_dedupe(self) -> None:
        """TODO 2: apply the dedupe policy. It is a DOCUMENTED DECISION, not a cleanup.

        Policies:
          "none"          every document is unique; nothing suppressed
          "global"        one copy of a hash across the whole corpus (cheapest; destroys
                          the fact that N custodians each had the document)
          "per-custodian" one copy per (custodian, hash) — keeps possession

        Set, on every doc:
            doc.dedupe = {"policy": <policy>, "status": "unique"|"duplicate",
                          "duplicate_of": <doc_id or None>}

        Possession is evidence. Which policy you choose changes your document count, and
        you will be asked which one you used and why.
        """
        for d in self.docs:
            d.dedupe = {"policy": self.dedupe_policy, "status": "unique",
                        "duplicate_of": None,
                        "TODO": "TODO 2 not implemented"}

    # ---- near-duplicates -----------------------------------------------------
    def group_near_duplicates(self, threshold: float = 0.80) -> None:
        """TODO 3: group near-duplicates. GROUP them; do not suppress them.

        Suggested approach (all stdlib):
          - shingle each doc's text into overlapping word 5-grams
          - hash each shingle, keep the N smallest hashes (a MinHash sketch)
          - Jaccard-estimate pairwise similarity from the sketches
          - union-find the pairs above `threshold` into ND-#### groups
          - write the group id into doc.dedupe["near_dupe_group"]

        v1 and v7 of a contract differ in exactly the clause that matters. Nobody cares
        that two documents are 94% similar; everybody cares about the 6%.
        """
        for d in self.docs:
            d.dedupe.setdefault("near_dupe_group", None)

    # ---- load file -----------------------------------------------------------
    def reconcile_load_file(self) -> dict:
        """TODO 4: read production/VOL001.dat + .opt and reconcile.

        The .dat is delimited by \\x14 and quoted with \\xfe (ASCII 20 / 254), because
        commas and quotes appear in legal text. The .opt maps PAGES to documents; a "Y"
        in the 4th field marks the first page of a document.

        Produce, and return:
          {"load_file_rows": N,
           "matched": [...],              rows whose NATIVE_PATH we found in the collection
           "in_load_file_not_collected": [...],   <- a COLLECTION LEAD. Report it.
           "collected_not_in_load_file": N,
           "opt_pages": N, "opt_documents": N}

        One row in the shipped corpus is deliberately listed in the load file and absent
        from the collection. Finding it is the point of this TODO.
        """
        return {"TODO": "TODO 4 not implemented"}

    # ---- write ---------------------------------------------------------------
    def write(self) -> dict:
        self.out.mkdir(parents=True, exist_ok=True)
        self.text_dir.mkdir(parents=True, exist_ok=True)
        with (self.out / "catalog.jsonl").open("w", encoding="utf-8") as fh:
            for d in self.docs:
                (self.text_dir / f"{d.doc_id}.txt").write_text(d.text, encoding="utf-8")
                fh.write(json.dumps(d.row(), ensure_ascii=False) + "\n")
        with (self.out / "exceptions.jsonl").open("w", encoding="utf-8") as fh:
            for e in self.exceptions:
                fh.write(json.dumps(e.row(), ensure_ascii=False) + "\n")

        by_custodian: dict[str, int] = {}
        for d in self.docs:
            by_custodian[d.custodian] = by_custodian.get(d.custodian, 0) + 1
        manifest = {
            "stage": "01-ingestion",
            "matter": MATTER,
            "run_at": now(),
            "corpus_root": str(self.corpus),
            "policies": {
                "dedupe": self.dedupe_policy,
                "ocr": "re-OCR locally" if self.reocr else "accept producer OCR sidecar",
                "ocr_engine": self._ocr_engine,
                "tika": self.tika_url or "not used (builtin extractors only)",
                "forensic": ["sources opened read-only",
                             "no outbound network calls during processing",
                             "append-only catalog and exception log"],
            },
            "counts": {
                "documents": len(self.docs),
                "exceptions": len(self.exceptions),
                "by_custodian": by_custodian,
                "by_extractor": _tally(d.extracted_by for d in self.docs),
                "by_media_type": _tally(d.media_type for d in self.docs),
            },
            "load_file": self.reconcile_load_file(),
            "honesty_check": (
                f"{len(self.docs)} documents processed; {len(self.exceptions)} did not. "
                f"Both numbers belong in any statement about this collection."),
        }
        (self.out / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return manifest


def _unfold(value: object) -> str:
    """Normalize a header value.

    Long headers are FOLDED across lines, so a raw `str()` of a Message-ID can come back
    as `"\n <abc@host>"`. Anything that later matches on a Message-ID — thread
    reconstruction (Lab 08), ground-truth resolution (Lab 05) — silently fails on that
    leading whitespace. Unfold once, here, at the single point where headers enter the
    catalog.
    """
    return re.sub(r"\s+", " ", str(value)).strip()


def _own_parts(msg: EmailMessage) -> Iterator[EmailMessage]:
    """Yield this message's leaf parts WITHOUT descending into a nested message.

    `EmailMessage.walk()` recurses through message/rfc822 parts. For legal ingestion
    that is wrong: an attachment of an attached message belongs to the inner message's
    family, not the outer one's.
    """
    if not msg.is_multipart():
        yield msg
        return
    for part in msg.iter_parts():
        ctype = part.get_content_type()
        if ctype == "message/rfc822":
            yield part                       # a boundary: the caller recurses
        elif part.get_content_maintype() == "multipart":
            yield from _own_parts(part)
        else:
            yield part


def _tally(items) -> dict:
    out: dict[str, int] = {}
    for i in items:
        out[i] = out.get(i, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def guess_media_type(name: str) -> str:
    import mimetypes
    t, _ = mimetypes.guess_type(name)
    return t or "application/octet-stream"


# -------------------------------------------------------------------------- loadfile
def read_dat(path: Path) -> list[dict]:
    """Read a Concordance-style .dat: \\x14 delimited, \\xfe quoted.

    Encoding is not a detail here. Load files arrive cp1252 (most often), UTF-16LE with a
    BOM (Relativity exports), or occasionally UTF-8. Decode a cp1252 file as UTF-8 and the
    \xfe quote character becomes an invalid byte; decode UTF-16 as cp1252 and every field
    gains a NUL. Sniff the BOM, then fall back to cp1252 — and say in your manifest which
    you used, because the answer changes what the fields contain.
    """
    raw_bytes = path.read_bytes()
    if raw_bytes[:2] in (b"\xff\xfe", b"\xfe\xff"):
        raw = raw_bytes.decode("utf-16")
    elif raw_bytes[:3] == b"\xef\xbb\xbf":
        raw = raw_bytes[3:].decode("utf-8")
    else:
        raw = raw_bytes.decode("cp1252", errors="replace")
    rows = [ln for ln in raw.replace("\r\n", "\n").split("\n") if ln.strip()]
    def fields(line: str) -> list[str]:
        return [f.strip("\xfe") for f in line.split("\x14")]
    header = fields(rows[0])
    return [dict(zip(header, fields(r))) for r in rows[1:]]


def read_opt(path: Path) -> list[dict]:
    """Read an Opticon .opt: one row per PAGE; 'Y' in field 4 starts a new document."""
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        f = (line.split(",") + [""] * 7)[:7]
        out.append({"page_id": f[0], "volume": f[1], "path": f[2],
                    "doc_start": f[3].upper() == "Y", "page_count": f[6]})
    return out


# ------------------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default="../assets/corpus")
    ap.add_argument("--out", default="../work")
    ap.add_argument("--dedupe", choices=["none", "global", "per-custodian"],
                    default="per-custodian",
                    help="a LEGAL decision, recorded in the manifest (default: per-custodian)")
    ap.add_argument("--matter", default=MATTER,
                    help="matter id stamped on every record (default: %(default)s)")
    ap.add_argument("--nd-threshold", type=float, default=0.60,
                    help="near-duplicate similarity threshold (default 0.60). This is a "
                         "real decision: too high and an edited contract no longer "
                         "groups with its own drafts.")
    ap.add_argument("--reocr", action="store_true",
                    help="re-OCR scans locally instead of accepting the producer's sidecar")
    ap.add_argument("--tika-url", default=os.environ.get("TIKA_URL"),
                    help="optional local tika-server, e.g. http://localhost:9998")
    args = ap.parse_args()

    corpus = Path(args.corpus).resolve()
    if not corpus.exists():
        print(f"error: corpus not found at {corpus}\n"
              f"generate it first:  python3 ../assets/make_corpus.py", file=sys.stderr)
        return 2

    ing = Ingester(corpus, Path(args.out).resolve(), dedupe=args.dedupe,
                   reocr=args.reocr, tika_url=args.tika_url, matter=args.matter)
    # two passes: sidecars first, so an image can adopt its producer OCR text
    for p in sorted(corpus.rglob("*.ocr.txt")):
        ing.ocr_sidecars[p.relative_to(corpus).as_posix()[:-len(".ocr.txt")]] = \
            p.read_text(encoding="utf-8", errors="replace")
    ing.walk()
    ing.apply_dedupe()
    ing.group_near_duplicates(args.nd_threshold)
    manifest = ing.write()

    print(f"\ningested  : {manifest['counts']['documents']} documents")
    print(f"exceptions: {manifest['counts']['exceptions']}  <- look at these")
    print(f"dedupe    : {args.dedupe}")
    print(f"ocr       : {manifest['policies']['ocr']} (engine: {ing._ocr_engine})")
    print(f"\nby extractor: {json.dumps(manifest['counts']['by_extractor'])}")
    print(f"\nwrote {args.out}/catalog.jsonl, exceptions.jsonl, manifest.json")
    print(f"\n{manifest['honesty_check']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
