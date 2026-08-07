from __future__ import annotations

"""Repository configuration (CI-safe defaults).

Why:
    CI and the diagnostics drift checker (legacy/diagnostics_check.py) expect a
    repo-root config.py to exist. Without it, GitHub Actions fails with
    FileNotFoundError.

Where:
    - Read by legacy/diagnostics_check.py (expects DB_PATH definition).
    - Imported/used by application code as needed.

How:
    Provide non-secret defaults and allow environment-variable overrides.
    This keeps local dev flexible and makes CI deterministic.
"""

import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent

# Single canonical SQLite DB location (required by diagnostics_check.py)
DB_PATH = os.environ.get("CLEVER_DB_PATH", str(ROOT_DIR / "clever.db"))

# General runtime config (optional)
ENV = os.environ.get("ENV", "ci")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Secrets should come from environment variables; keep None by default.
OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
