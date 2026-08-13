"""Diagnostics Consistency Checker

Why: Provide a lightweight, offline-safe validation that key architectural
assertions documented in `docs/copilot_diagnostics.md` are still true in the
current working tree (offline guard present, single DB reference, diagnostics
file exists). This acts as an early drift detector before deeper CI.
Where: Legacy copy retained for historical compatibility. The canonical checker
lives in `tools/diagnostics_check.py`.
How: Performs static text scans instead of importing the whole app (avoids
side effects). Reads selective files and searches for required tokens.

Connects to:
    - app.py: Verifies `offline_guard.enable()` invocation
    - config/__init__.py: Ensures single `DB_PATH` definition in the canonical config package
    - docs/copilot_diagnostics.md: Confirms existence + required headers
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAIL = False


def fail(msg: str):
    """Register failure (no immediate exit to aggregate results).

    Why: Aggregate multiple drift signals for better developer feedback.
    Where: Used across each validation step in this script.
    How: Sets module-global FAIL flag and prints prefixed line.
    """
    global FAIL
    FAIL = True
    print(f"[DRIFT] {msg}")


def check_offline_guard():
    app_py = (ROOT / "app.py").read_text(encoding="utf-8", errors="ignore")
    if "offline_guard.enable()" not in app_py:
        fail("offline_guard.enable() missing in app.py")
    else:
        print("[OK] offline guard present")


def check_single_db():
    """Validate a single DB_PATH assignment referencing clever.db.

    Why: Enforces the single-database rule so Clever's memory stays coherent
    and no shadow databases are accidentally created.
    Where: Validates config/__init__.py, the canonical configuration package entry point.
    How: Scans config/__init__.py for lines starting with 'DB_PATH' (ignoring leading
    whitespace) and counts them; validates 'clever.db' substring is present on
    that line. Avoids executing code or AST parsing to remain trivial & offline.
    """
    config_text = (ROOT / "config" / "__init__.py").read_text(encoding="utf-8", errors="ignore").splitlines()
    db_lines = [ln for ln in config_text if re.match(r"^\s*DB_PATH\s*=", ln)]
    if not db_lines:
        fail("DB_PATH not defined in config/__init__.py")
        return
    if len(db_lines) > 1:
        fail("Multiple DB_PATH assignments detected")
    line = db_lines[0]
    if "clever.db" not in line:
        fail("DB_PATH does not reference clever.db")
    if not FAIL:
        print("[OK] single DB_PATH referencing clever.db")


def check_diagnostics_doc():
    doc_path = ROOT / "docs" / "copilot_diagnostics.md"
    if not doc_path.exists():
        fail("Missing docs/copilot_diagnostics.md")
        return
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    required_headers = [
        "# Copilot Diagnostics & Alignment Report",
        "## Unbreakable Rules Compliance",
        "## UI Vision Alignment",
    ]
    for h in required_headers:
        if h not in text:
            fail(f"Missing diagnostics section: {h}")
    if not FAIL:
        print("[OK] diagnostics document structure intact")


def main():
    check_offline_guard()
    check_single_db()
    check_diagnostics_doc()
    if FAIL:
        print("\n❌ Diagnostics drift detected")
        sys.exit(1)
    print("\n✅ Diagnostics checks passed")


if __name__ == "__main__":  # pragma: no cover - direct CLI entry
    main()
