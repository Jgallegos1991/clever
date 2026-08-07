#!/usr/bin/env bash
# Weekly self-reflection automation entry point.
# Add to cron (runs every Monday at 3am) with:
#   0 3 * * 1 cd /home/jgallegos1991/Clever && ./tools/self_reflection_update.sh >> logs/self_reflection.log 2>&1

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

PYTHON_EXEC="python3"

if [ -d ".venv" ]; then
  # Activate virtual environment to ensure dependencies like matplotlib are available
  # shellcheck disable=SC1091
  source .venv/bin/activate
  PYTHON_EXEC="python"
fi

if ! command -v "$PYTHON_EXEC" >/dev/null 2>&1; then
  echo "$PYTHON_EXEC not found; cannot regenerate self-reflection artifacts." >&2
  exit 1
fi

if command -v ipfs >/dev/null 2>&1; then
  if ! ipfs id >/dev/null 2>&1; then
    echo "⚠️  IPFS daemon unreachable; snapshots may be skipped."
  fi
fi

"$PYTHON_EXEC" ./tools/self_reflection_update.py

if ! "$PYTHON_EXEC" ./tools/ipfs_snapshot_manager.py; then
  echo "⚠️  IPFS snapshot manager reported issues; review logs/codex_diagnostics/." >&2
fi
