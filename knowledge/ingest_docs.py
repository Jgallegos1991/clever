#!/usr/bin/env python3
# ingest_docs.py — Jay-only, offline knowledge indexer for Clever (Synaptic Hub)
# Source: ~/Clever/knowledge/*.{docx,pdf,md,txt}  ->  ~/.clever/knowledge/index.jsonl

"""
Offline knowledge ingestion utility for Clever's private vault.

Why: Keep Jay's local knowledge corpus synchronized with Clever's indexed
memory without touching external services.
Where: Run manually or via cron on Jay's device whenever new documents land in
`~/Clever/knowledge`.
How: Scans supported files, normalizes text, chunks content, and writes an
append-only JSONL index consumed by the knowledge engine.

File Usage:
    - `ingest_docs.py`: executed directly for one-off ingestion runs.
    - Automation scripts under `tools/`: import helper functions for batch jobs.
Connects to:
    - `knowledge_base.py`: reads generated JSONL entries during ingestion.
    - `Clever_Sync/` and `Clever_Learn/`: upstream sources mirrored here.
"""

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime

VAULT_DIR = os.path.expanduser("~/Clever/knowledge")
OUT_DIR = os.path.expanduser("~/.clever/knowledge")
OUT_FILE = os.path.join(OUT_DIR, "index.jsonl")


# ---------- helpers ----------
def ensure_dirs():
    os.makedirs(VAULT_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def clean_text(s: str) -> str:
    s = s.replace("\r", "")
    s = re.sub(r"\u0000", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def chunk_text(s: str, target_chars=1200, overlap=150):
    # simple semantic-ish chunker: split on paragraphs, then merge up to target length
    paras = [p.strip() for p in re.split(r"\n\s*\n", s) if p.strip()]
    chunks, buf = [], []
    size = 0
    for p in paras:
        if size + len(p) + 1 > target_chars and buf:
            joined = "\n\n".join(buf).strip()
            chunks.append(joined)
            if overlap > 0 and chunks:
                tail = joined[-overlap:]
                buf = [tail, p]
                size = len(tail) + len(p) + 1
            else:
                buf, size = [p], len(p)
        else:
            buf.append(p)
            size += len(p) + 1
    if buf:
        chunks.append("\n\n".join(buf).strip())
    return chunks


# ---------- readers (offline) ----------
def read_txt(path):
    return pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")


def read_md(path):
    return read_txt(path)


def read_docx(path):
    # No internet, so avoid heavy deps. Try python-docx if available, else fallback via text extraction call if present.
    try:
        import docx

        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        # fallback: use `wvText` or `antiword` if user installed; otherwise give minimal notice
        for cmd in (["docx2txt", path, "-"], ["wvText", path, "-"], ["antiword", path]):
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(
                    "utf-8", "ignore"
                )
                return out
            except Exception:
                pass
        # Dead-simple fallback: no parse
        return ""


def read_pdf(path):
    # Try pdftotext if available
    for cmd in (["pdftotext", "-layout", path, "-"], ["pdftotext", path, "-"]):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
            return out
        except Exception:
            pass
    # minimal pure-python fallback using PyPDF2 if installed
    try:
        import PyPDF2

        text = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception:
        return ""


READERS = {
    ".txt": read_txt,
    ".md": read_md,
    ".docx": read_docx,
    ".pdf": read_pdf,
}


def read_file(path):
    ext = pathlib.Path(path).suffix.lower()
    fn = READERS.get(ext)
    if not fn:
        return ""
    return fn(path)


# ---------- main ingest ----------
def iter_files():
    if not os.path.isdir(VAULT_DIR):
        return
    for root, _, files in os.walk(VAULT_DIR):
        for f in files:
            p = os.path.join(root, f)
            if pathlib.Path(p).suffix.lower() in READERS:
                yield p


def record_for(path, text):
    stat = os.stat(path)
    meta = {
        "path": path,
        "title": pathlib.Path(path).stem,
        "mtime": int(stat.st_mtime),
        "size": stat.st_size,
        "indexed_at": int(time.time()),
    }
    body = clean_text(text)
    chunks = chunk_text(body)
    base_id = sha256(f"{path}:{stat.st_mtime}:{stat.st_size}")
    rows = []
    for i, ch in enumerate(chunks):
        rows.append(
            {
                "id": f"{base_id}-{i:04d}",
                "doc_id": base_id,
                "chunk_index": i,
                "title": meta["title"],
                "text": ch,
                "meta": meta,
            }
        )
    return rows


def main():
    ensure_dirs()
    # Build fresh index each run; append is possible but full rebuild is simple & safe
    tmp = OUT_FILE + ".tmp"
    total, docs = 0, 0
    with open(tmp, "w", encoding="utf-8") as w:
        for path in sorted(iter_files()):
            raw = read_file(path)
            if not raw.strip():
                continue
            docs += 1
            for row in record_for(path, raw):
                w.write(json.dumps(row, ensure_ascii=False) + "\n")
                total += 1
    os.replace(tmp, OUT_FILE)
    print(f"Indexed {docs} docs into {OUT_FILE} with {total} chunks.")


if __name__ == "__main__":
    main()
