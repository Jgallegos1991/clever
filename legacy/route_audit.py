#!/usr/bin/env python3
"""
tools/route_audit.py - Enumerate Flask routes for Clever.

Why: Provide a quick diagnostic of all registered endpoints, their methods,
     and handler names to support auditing and automated documentation.
Where: Run from repository root (`python3 tools/route_audit.py`).
How: Imports `app`, iterates the Flask url_map, and prints a sorted table.
"""

from __future__ import annotations

import sys
from pathlib import Path


def load_app():
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from app import app  # Deferred import to respect app initialization

    return app


def build_route_table(app) -> list[list[str]]:
    rows: list[list[str]] = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: (str(r.rule), sorted(r.methods))):
        methods = ", ".join(sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"}))
        rows.append([rule.rule, methods or "-", rule.endpoint])
    return rows


def main() -> None:
    app = load_app()
    rows = build_route_table(app)
    headers = ("Route", "Methods", "Endpoint")
    col_widths = [len(h) for h in headers]
    for route, methods, endpoint in rows:
        col_widths[0] = max(col_widths[0], len(route))
        col_widths[1] = max(col_widths[1], len(methods))
        col_widths[2] = max(col_widths[2], len(endpoint))

    def fmt_row(values: tuple[str, str, str]) -> str:
        return (
            f"{values[0]:<{col_widths[0]}}  "
            f"{values[1]:<{col_widths[1]}}  "
            f"{values[2]:<{col_widths[2]}}"
        )

    print(fmt_row(headers))
    print(" ".join("-" * w for w in col_widths))
    for route, methods, endpoint in rows:
        print(fmt_row((route, methods, endpoint)))


if __name__ == "__main__":
    main()
