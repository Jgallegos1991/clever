#!/usr/bin/env python3
"""
tools/log_sync_service.py - Scheduled rclone log synchronization

Why: Keeps Clever's diagnostic and application logs mirrored to the
     Synaptic Hub without manual intervention.
Where: Runs as a lightweight background worker invoked from startup scripts
       or manually for ad-hoc sync operations.
How: Executes `rclone sync` on a configurable interval, recording each run to
     `logs/codex_diagnostics/` for auditability while respecting offline-first
     defaults.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import config

# Default directories (ensures diagnostics path exists)
ROOT_DIR = Path(__file__).resolve().parent.parent
DIAGNOSTICS_DIR = ROOT_DIR / "logs" / "codex_diagnostics"
DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)


def _build_command(
    local_path: Path,
    remote: str,
    remote_path: str,
    extra: str,
    dry_run: bool,
) -> list[str]:
    """Construct the rclone command with safety flags."""
    target = f"{remote}:{remote_path}"
    cmd = ["rclone", "sync", str(local_path), target]
    if extra:
        cmd.extend(shlex.split(extra))
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def _execute(cmd: list[str]) -> Tuple[int, str, str]:
    """Run the rclone command and return (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", "rclone not installed"


def _write_log(
    local_path: Path,
    remote: str,
    remote_path: str,
    return_code: int,
    stdout: str,
    stderr: str,
    duration: float,
    dry_run: bool,
) -> None:
    """Append a structured entry to the codex diagnostics log."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_path = DIAGNOSTICS_DIR / "log_sync_history.log"
    status = "success" if return_code == 0 else "error"
    lines = [
        "=" * 72,
        f"timestamp: {timestamp}",
        f"status: {status}",
        f"return_code: {return_code}",
        f"dry_run: {str(dry_run).lower()}",
        f"duration_sec: {duration:.2f}",
        f"local_path: {local_path}",
        f"remote: {remote}:{remote_path}",
        "stdout:",
        stdout.strip() or "<empty>",
        "stderr:",
        stderr.strip() or "<empty>",
        "",
    ]
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def run_sync(
    local_path: Path,
    remote: str,
    remote_path: str,
    extra: str,
    dry_run: bool = False,
) -> int:
    """Execute a single rclone sync and record the result."""
    start = time.time()
    cmd = _build_command(local_path, remote, remote_path, extra, dry_run)
    rc, stdout, stderr = _execute(cmd)
    duration = time.time() - start
    _write_log(local_path, remote, remote_path, rc, stdout, stderr, duration, dry_run)

    summary = f"[log-sync] rc={rc} duration={duration:.1f}s target={remote}:{remote_path}"
    if rc != 0:
        summary += " ⚠️"
    print(summary)
    if stdout.strip():
        print(stdout.strip())
    if stderr.strip():
        print(stderr.strip(), file=sys.stderr)
    return rc


def should_continue(interval_minutes: int) -> bool:
    """Helper to ensure valid interval."""
    return interval_minutes > 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scheduled rclone sync for Clever logs")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=config.RCLONE_LOGS_INTERVAL_MINUTES,
        help="Minutes between sync runs (default: from configuration)",
    )
    parser.add_argument(
        "--local-path",
        default=config.RCLONE_LOGS_LOCAL,
        help="Local logs directory to sync (default: configuration)",
    )
    parser.add_argument(
        "--remote",
        default=config.RCLONE_LOGS_REMOTE,
        help="rclone remote name (default: configuration)",
    )
    parser.add_argument(
        "--remote-path",
        default=config.RCLONE_LOGS_PATH,
        help="Remote path under the rclone remote (default: configuration)",
    )
    parser.add_argument(
        "--extra-flags",
        default=config.RCLONE_LOGS_EXTRA,
        help="Additional rclone flags (default: configuration)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run rclone with --dry-run for verification",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute a single sync and exit",
    )

    args = parser.parse_args()

    local_path = Path(args.local_path).resolve()
    if not local_path.exists():
        print(f"[log-sync] Local path does not exist: {local_path}", file=sys.stderr)
        return 2

    if not args.remote:
        print(
            "[log-sync] Remote name is required (set RCLONE_LOGS_REMOTE).",
            file=sys.stderr,
        )
        return 2
    if not args.remote_path:
        print(
            "[log-sync] Remote path is required (set RCLONE_LOGS_PATH).",
            file=sys.stderr,
        )
        return 2

    iteration = 0
    while True:
        iteration += 1
        print(f"[log-sync] Starting run #{iteration} (dry_run={args.dry_run})")
        run_sync(local_path, args.remote, args.remote_path, args.extra_flags, args.dry_run)
        if args.once:
            break
        if not should_continue(args.interval_minutes):
            print("[log-sync] Invalid interval; stopping scheduler.", file=sys.stderr)
            break
        sleep_seconds = args.interval_minutes * 60
        try:
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            print("[log-sync] Interrupted; stopping scheduler.")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
