#!/usr/bin/env python3
"""
Managed IPFS snapshot automation for Clever.

Why: Preserve offline redundancy by snapshotting key artifacts to IPFS so Jay
can restore Clever’s knowledge graph even if local storage fails.
Where: Runs from maintenance scripts or direct CLI invocations when generating
daily snapshots inside `logs/codex_diagnostics/`.
How: Reads `config/ipfs_config.json`, pins configured paths, and logs the
resulting CIDs while capturing diagnostics about pinning status.

File Usage:
    - `tools/ipfs_snapshot_manager.py`: primary CLI utility for IPFS snapshots.
    - `automation workflows`: import helpers when chaining snapshot + backup.
Connects to:
    - `logs/codex_diagnostics/`: receives CID tracking JSON logs.
    - `config/ipfs_config.json`: declares snapshot targets and gateway settings.
    - Local IPFS daemon: invoked via subprocess call to `ipfs`.

This utility pins configured artifact sets to the local IPFS node, captures the
resulting CIDs, and records a diagnostic artifact under logs/codex_diagnostics/.
Remote pinning hooks are scaffolded for future extension; for now the tool
records whether the necessary credentials are available.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "ipfs_config.json"
DIAGNOSTIC_DIR = REPO_ROOT / "logs" / "codex_diagnostics"
LAST_CID_PATH = REPO_ROOT / "logs" / "self_reflection_reports" / "last_ipfs_cids.json"

DEFAULT_CONFIG = {
    "gateway": "http://127.0.0.1:8081",
    "pin_sets": [
        {
            "name": "core_artifacts",
            "enabled": True,
            "recursive": False,
            "paths": [
                "CLEVER_MANIFEST.md",
                "Clever_Cognitive_Map.dot",
            ],
        },
        {
            "name": "self_reflection_reports",
            "enabled": True,
            "recursive": True,
            "paths": [
                "logs/self_reflection_reports",
            ],
        },
        {
            "name": "sync_packages",
            "enabled": False,
            "recursive": True,
            "paths": [
                "Clever_Sync",
            ],
        },
    ],
    "remote_pinners": [
        # Example entry:
        # {
        #     "name": "pinata",
        #     "type": "pinata",
        #     "api_key_env": "PINATA_JWT",
        #     "enabled": False
        # }
    ],
}


def load_config() -> Dict[str, object]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid IPFS config JSON: {exc}") from exc
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    return DEFAULT_CONFIG.copy()


def check_command(cmd: Iterable[str]) -> Tuple[bool, Optional[str]]:
    try:
        subprocess.run(
            list(cmd),
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True, None
    except FileNotFoundError:
        return False, "command_not_found"
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="ignore").strip()
        return False, stderr or exc.stdout.decode("utf-8", errors="ignore").strip()


def ensure_ipfs_ready() -> Dict[str, object]:
    status: Dict[str, object] = {
        "ipfs_available": False,
        "daemon_available": False,
        "warnings": [],
    }

    available, detail = check_command(["ipfs", "--version"])
    if not available:
        status["warnings"].append(f"ipfs_cli_unavailable: {detail}")
        return status

    status["ipfs_available"] = True
    daemon_ok, detail = check_command(["ipfs", "id"])
    if not daemon_ok:
        status["warnings"].append(f"ipfs_daemon_unreachable: {detail}")
        return status

    status["daemon_available"] = True
    return status


def normalize_paths(paths: Iterable[str]) -> List[Path]:
    normalized = []
    for raw in paths:
        if not raw:
            continue
        normalized.append((REPO_ROOT / raw).resolve())
    return normalized


def pin_path(path: Path, recursive: bool) -> Tuple[str, Dict[str, object]]:
    if not path.exists():
        return "missing", {
            "path": str(path),
            "status": "missing",
            "message": "Path does not exist",
        }

    cmd = ["ipfs", "add", "-Q"]
    if path.is_dir():
        cmd.append("-r")
        if not recursive:
            # ipfs requires -r for directories; note that recursion was disabled.
            status_message = "Directory pin forced recursive due to IPFS requirements"
        else:
            status_message = None
    else:
        status_message = None

    cmd.append(str(path))

    try:
        result = subprocess.check_output(cmd, cwd=REPO_ROOT)
    except FileNotFoundError:
        return "error", {
            "path": str(path),
            "status": "error",
            "message": "ipfs command not found during pin",
        }
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="ignore").strip() if exc.stderr else ""
        return "error", {
            "path": str(path),
            "status": "error",
            "message": stderr or "ipfs add failed",
        }

    cid = result.decode("utf-8").strip()
    data = {
        "path": str(path),
        "status": "pinned",
        "cid": cid,
    }
    if status_message:
        data["message"] = status_message
    return "pinned", data


def merge_cid_record(new_entries: List[Dict[str, object]]) -> None:
    if not new_entries:
        return

    existing: Dict[str, str] = {}
    if LAST_CID_PATH.exists():
        try:
            existing = json.loads(LAST_CID_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    for entry in new_entries:
        cid = entry.get("cid")
        name = Path(entry.get("path", "")).name
        if cid and name:
            existing[name] = cid

    LAST_CID_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAST_CID_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def evaluate_remote_pinners(config: Dict[str, object]) -> List[Dict[str, object]]:
    remotes: List[Dict[str, object]] = []
    for item in config.get("remote_pinners", []) or []:
        if not isinstance(item, dict):
            continue
        enabled = item.get("enabled", True)
        env_var = item.get("api_key_env")
        token_present = bool(env_var and os.environ.get(str(env_var), "").strip())
        remotes.append(
            {
                "name": item.get("name", "unnamed"),
                "type": item.get("type", "custom"),
                "enabled": bool(enabled),
                "credentials_present": token_present,
                "status": "pending_implementation",
            }
        )
    return remotes


def run() -> int:
    config = load_config()
    timestamp = datetime.now(timezone.utc)
    ipfs_status = ensure_ipfs_ready()

    diagnostic: Dict[str, object] = {
        "timestamp": timestamp.isoformat(),
        "gateway": config.get("gateway"),
        "ipfs_status": ipfs_status,
        "pin_sets": [],
        "remote_pinners": evaluate_remote_pinners(config),
        "warnings": [],
    }

    overall_new_entries: List[Dict[str, object]] = []
    pin_sets = config.get("pin_sets", [])

    if not ipfs_status.get("daemon_available"):
        diagnostic["warnings"].extend(ipfs_status.get("warnings", []))
    else:
        for set_config in pin_sets:
            if not isinstance(set_config, dict):
                continue
            if not set_config.get("enabled", True):
                diagnostic["pin_sets"].append(
                    {
                        "name": set_config.get("name", "unnamed"),
                        "status": "skipped",
                        "reason": "disabled",
                    }
                )
                continue

            name = set_config.get("name", "unnamed")
            recursive = bool(set_config.get("recursive", False))
            paths = normalize_paths(set_config.get("paths", []))
            set_entries: List[Dict[str, object]] = []

            for path in paths:
                _, entry = pin_path(path, recursive)
                set_entries.append(entry)
                if entry.get("status") == "pinned":
                    overall_new_entries.append(entry)

            diagnostic["pin_sets"].append(
                {
                    "name": name,
                    "recursive": recursive,
                    "entries": set_entries,
                }
            )

    merge_cid_record(overall_new_entries)

    DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)
    log_path = DIAGNOSTIC_DIR / f"ipfs_snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    log_path.write_text(json.dumps(diagnostic, indent=2), encoding="utf-8")

    pinned_count = sum(1 for entry in overall_new_entries if entry.get("status") == "pinned")
    missing_count = sum(
        1
        for set_result in diagnostic["pin_sets"]
        for entry in set_result.get("entries", [])
        if entry.get("status") == "missing"
    )
    failed_count = sum(
        1
        for set_result in diagnostic["pin_sets"]
        for entry in set_result.get("entries", [])
        if entry.get("status") == "error"
    )

    print(f"[IPFS snapshot] pinned={pinned_count} missing={missing_count} failed={failed_count}")
    print(f"Diagnostic log: {log_path.relative_to(REPO_ROOT)}")

    if not ipfs_status.get("daemon_available"):
        print("Warning: IPFS daemon unavailable; no snapshots completed.")
        return 1
    if failed_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
