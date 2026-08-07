"""
tools/clever_doctor.py - Lightweight health check for Clever's runtime environment

Why: Provide a quick, offline-safe command Jay can run (or wire into automation)
     to confirm Clever's core environment variables and filesystem locations are
     aligned with the Synaptic Hub layout before launching services.
Where: Executed manually (`python tools/clever_doctor.py`) or by future startup
       scripts to verify Clever's readiness.
How: Reads key environment variables, validates that expected files/directories
     exist (or will be created safely), and reports concise status codes.

Connects to:
    - config.py: Imports the enhanced configuration to confirm initialization.
    - ~/.bashrc / .env: Relies on exported environment variables for paths.
    - Clever filesystem: Checks database file and sync directories under CLEVER_HOME.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


Status = str  # literal "ok", "warn", "error"


@dataclass(frozen=True)
class CheckResult:
    """Structured result for a single environment or filesystem check."""

    name: str
    status: Status
    detail: str

    def emoji(self) -> str:
        return {"ok": "✅", "warn": "⚠️", "error": "❌"}.get(self.status, "❓")


def _get_env(name: str) -> CheckResult:
    """Validate the presence of an environment variable."""
    value = os.environ.get(name)
    if value:
        return CheckResult(name=name, status="ok", detail=value)
    return CheckResult(name=name, status="error", detail="Missing environment variable")


def _check_path(name: str, raw_value: str, expect_dir: bool) -> CheckResult:
    """Confirm that a path resolves and exists (or is creatable)."""
    if not raw_value:
        return CheckResult(name=name, status="error", detail="Not set")

    path = Path(raw_value).expanduser()
    if expect_dir:
        if path.is_dir():
            return CheckResult(name=name, status="ok", detail=str(path))
        if path.exists():
            return CheckResult(
                name=name,
                status="error",
                detail=f"Exists but is not a directory: {path}",
            )
        parent = path.parent
        detail = f"Missing directory (parent exists: {parent.exists()})"
        return CheckResult(name=name, status="warn", detail=detail)

    # Expecting a file (database)
    if path.is_file():
        return CheckResult(name=name, status="ok", detail=str(path))

    parent = path.parent
    if not parent.exists():
        return CheckResult(
            name=name,
            status="error",
            detail=f"Parent directory does not exist: {parent}",
        )

    return CheckResult(
        name=name,
        status="warn",
        detail=f"File missing (will be created on first run): {path}",
    )


def check_environment() -> Tuple[List[CheckResult], Dict[str, str]]:
    """Gather environment variables and perform path checks."""
    env_keys = [
        "CLEVER_HOME",
        "CLEVER_DB_PATH",
        "CLEVER_SYNC_DIR",
        "CLEVER_SYNAPTIC_DIR",
        "CLEVER_ENVIRONMENT",
        "RCLONE_REMOTE",
        "RCLONE_SRC",
        "RCLONE_DST",
    ]

    results: List[CheckResult] = []
    env_values: Dict[str, str] = {}

    for key in env_keys:
        result = _get_env(key)
        results.append(result)
        if result.status == "ok":
            env_values[key] = os.environ[key]

    # Path-specific validations
    home_result = _check_path("CLEVER_HOME path", env_values.get("CLEVER_HOME", ""), True)
    db_result = _check_path("CLEVER_DB_PATH file", env_values.get("CLEVER_DB_PATH", ""), False)
    sync_result = _check_path("CLEVER_SYNC_DIR", env_values.get("CLEVER_SYNC_DIR", ""), True)
    synaptic_result = _check_path(
        "CLEVER_SYNAPTIC_DIR", env_values.get("CLEVER_SYNAPTIC_DIR", ""), True
    )

    results.extend([home_result, db_result, sync_result, synaptic_result])
    return results, env_values


def check_configuration(env_values: Dict[str, str]) -> CheckResult:
    """Ensure the enhanced config loads with the provided environment."""
    try:
        import config  # noqa: F401  (local import after sys.path adjustment)

        cfg = config.get_enhanced_config()
        detail = (
            f"env={cfg.environment.value}, "
            f"db={cfg.database.path}, "
            f"sync={cfg.paths.sync_dir.name}"
        )
        return CheckResult(name="Enhanced configuration", status="ok", detail=detail)
    except Exception as exc:  # pragma: no cover - defensive
        return CheckResult(
            name="Enhanced configuration",
            status="error",
            detail=f"Failed to load config: {exc}",
        )


def get_doctor_report() -> Dict[str, Any]:
    """Generate the full doctor report with structured results and summary."""
    results, env_values = check_environment()
    results.append(check_configuration(env_values))
    report_results = [asdict(r) for r in results]
    summary = _summarize(results)
    return {
        "results": report_results,
        "summary": summary,
        "generated_ts": time.time(),
        "has_errors": any(r["status"] == "error" for r in report_results),
        "has_warnings": any(r["status"] == "warn" for r in report_results),
    }


def format_text(results: Iterable[CheckResult]) -> str:
    """Build a human-friendly text report."""
    lines = ["🩺  Clever Doctor — Environment Check", "-" * 46]
    for result in results:
        lines.append(f"{result.emoji()} {result.name}: {result.detail}")
    summary = _summarize(results)
    lines.append("-" * 46)
    lines.append(summary)
    return "\n".join(lines)


def _summarize(results: Iterable[CheckResult]) -> str:
    counts = {"ok": 0, "warn": 0, "error": 0}
    for result in results:
        if result.status in counts:
            counts[result.status] += 1
    if counts["error"]:
        return f"❌ {counts['error']} error(s), {counts['warn']} warning(s). Resolve before launch."
    if counts["warn"]:
        return f"⚠️ {counts['warn']} warning(s); launch will recreate missing assets."
    return "✅ All checks passed. Clever is ready to launch."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Clever environment health checks.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON for automation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = get_doctor_report()
    results = [CheckResult(**r) for r in report["results"]]
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_text(results))

    return 1 if report["has_errors"] else 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
