#!/usr/bin/env python3
"""
self_introspect.py
Continuous local introspection engine for Clever.

Purpose:
    Gives Clever real-time self-awareness by running the local_codex scanner
    in a background thread during normal operation. All analysis logs are
    written to system_self_introspection.log for later reflection and evolution.

When active:
    - Scans Clever’s codebase every 10 minutes.
    - Hashes each file and counts lines.
    - Logs summaries without touching runtime behavior.

Connects to:
    - codex/local_codex.py  →  Provides scan_directory() for structural analysis
    - app.py                →  Starts background thread via start_background_loop()
"""

import datetime
import json
import os
import threading
import time
from pathlib import Path

try:
    from codex.local_codex import scan_directory
except Exception as e:
    print(f"[Self-Introspect] Warning: codex.local_codex unavailable → {e}")
    scan_directory = None

LOG_PATH = Path(__file__).resolve().parent / "system_self_introspection.log"
SCAN_INTERVAL = 600  # seconds (10 min)


def _log(entry: dict):
    """Append one JSON entry to Clever’s introspection log."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    record = {"timestamp": ts, **entry}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_cycle():
    """Perform a single introspection scan."""
    if not scan_directory:
        return
    base = os.environ.get("CLEVER_HOME", str(Path(__file__).resolve().parent))
    results = scan_directory(base)
    total = len(results)
    changed = [r["file"] for r in results if r.get("hash")]
    _log({"total_files": total, "scanned": len(changed)})
    print(f"[Self-Introspect] ✅ Scanned {total} files — log updated.")


def start_background_loop():
    """Spawn an autonomous background loop for continuous self-analysis."""

    def loop():
        while True:
            try:
                run_cycle()
            except Exception as e:
                print(f"[Self-Introspect] Error: {e}")
            time.sleep(SCAN_INTERVAL)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print("[Self-Introspect] Background loop started.")
    return t


if __name__ == "__main__":
    run_cycle()
