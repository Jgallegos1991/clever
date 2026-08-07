#!/usr/bin/env python3
"""
local_codex.py
Offline reasoning and code-introspection engine for Clever.

This replaces any remote Codex or OpenAI dependency.
It parses Python files, extracts structural info, runs
simple static analysis, and produces natural-language
summaries and refactor hints.
"""

import ast
import difflib
import hashlib
import os
import re
from pathlib import Path
from textwrap import shorten


def summarize_file(path: str) -> dict:
    text = Path(path).read_text(errors="ignore")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return {"file": path, "error": f"SyntaxError: {e}"}
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    doc = ast.get_docstring(tree) or "No module docstring."
    hashval = hashlib.sha1(text.encode()).hexdigest()[:10]
    return {
        "file": path,
        "hash": hashval,
        "functions": funcs,
        "classes": classes,
        "doc": shorten(doc, 300),
        "line_count": len(text.splitlines()),
    }


def diff_summary(a_path, b_path):
    a = Path(a_path).read_text(errors="ignore").splitlines()
    b = Path(b_path).read_text(errors="ignore").splitlines()
    diff = list(difflib.unified_diff(a, b, lineterm=""))
    changed = [l for l in diff if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    return f"{len(changed)} changed lines detected between {a_path} and {b_path}."


def scan_directory(base=".", pattern=r".*\.py$"):
    summaries = []
    for root, _, files in os.walk(base):
        for f in files:
            if re.match(pattern, f):
                summaries.append(summarize_file(os.path.join(root, f)))
    return summaries


def print_summary(summary):
    print(f"\nFile: {summary['file']}")
    print(f"Hash: {summary['hash']}  Lines: {summary['line_count']}")
    print(f"Classes: {', '.join(summary['classes']) or '—'}")
    print(f"Functions: {', '.join(summary['functions']) or '—'}")
    print(f"Docstring: {summary['doc']}")


def main():
    base = os.environ.get("CLEVER_HOME", str(Path(__file__).resolve().parent.parent))
    print(f"[Local Codex] Scanning {base}")
    results = scan_directory(base)
    for s in results[:10]:
        print_summary(s)
    print(f"\nAnalyzed {len(results)} Python files total.")


if __name__ == "__main__":
    main()
