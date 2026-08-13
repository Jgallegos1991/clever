"""tools/diagnostics_check.py - Diagnostics Consistency Checker

Why: Provide a lightweight, offline-safe validation that key architectural
assertions documented in `docs/copilot_diagnostics.md` are still true in the
current working tree (offline guard present, single DB reference, diagnostics
file exists). This acts as an early drift detector before deeper CI.
Where: Invoked by `tests/test_diagnostics.py` and `make diagnostics`; wired
into CI to gate on architectural invariants before the full test suite.
How: Performs static text scans instead of importing the whole app (avoids
side effects). Reads selective files and searches for required tokens.

Connects to:
    - app.py: Verifies `offline_guard.enable()` invocation
    - config/__init__.py: Ensures single `DB_PATH` definition in the canonical config package
    - docs/copilot_diagnostics.md: Confirms existence + required headers
    - tests/test_diagnostics.py: Test that loads and calls main()
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAIL = False


def fail(msg: str) -> None:
    """Register failure (no immediate exit to aggregate results).

    Why: Aggregate multiple drift signals for better developer feedback.
    Where: Used across each validation step in this script.
    How: Sets module-global FAIL flag and prints prefixed line.
    """
    global FAIL
    FAIL = True
    print(f"[DRIFT] {msg}")


def check_offline_guard() -> None:
    """Confirm app.py contains the offline guard enablement call.

    Why: Ensures Jay's digital sovereignty guarantee (no external calls) is
    enforced at runtime startup and has not been accidentally removed.
    Where: Validates app.py, which is the Flask entry point.
    How: Simple substring search; offline, no imports.
    """
    app_py = (ROOT / "app.py").read_text(encoding="utf-8", errors="ignore")
    if "offline_guard.enable()" not in app_py:
        fail("offline_guard.enable() missing in app.py")
    else:
        print("[OK] offline guard present")


def check_single_db() -> None:
    """Validate a single DB_PATH assignment referencing clever.db.

    Why: Enforces the single-database rule so Clever's memory stays coherent
    and no shadow databases are accidentally created.
    Where: Validates config/__init__.py, the canonical configuration package entry point.
    How: Scans config/__init__.py for lines matching DB_PATH assignment and verifies
    exactly one exists and that it references clever.db.
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


def check_diagnostics_doc() -> None:
    """Verify the copilot diagnostics document exists with required sections.

    Why: Ensures the living alignment document is present and maintains the
    expected structure so AI agents can orient themselves.
    Where: Checks docs/copilot_diagnostics.md.
    How: Existence check + required header substring scan.
    """
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


def main() -> None:
    """Run all diagnostics checks and exit non-zero on any drift.

    Why: Single entry point for test runner and Makefile target.
    Where: Called by tests/test_diagnostics.py and `make diagnostics`.
    How: Runs each check sequentially; exits 1 if any drift was registered.
    """
    check_offline_guard()
    check_single_db()
    check_diagnostics_doc()
    if FAIL:
        print("\n❌ Diagnostics drift detected")
        sys.exit(1)
    print("\n✅ Diagnostics checks passed")


if __name__ == "__main__":  # pragma: no cover - direct CLI entry
    main()
