#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Clever AI – Artifact Sync to Google Drive
#
# This script copies key artifacts (self-reflection, manifests, logs, etc.)
# to a remote folder (default: GDrive:CLEVER_AI) using rclone.
#
# Why: provide a redundant cloud backup in addition to local + IPFS storage.
# -----------------------------------------------------------------------------

set -euo pipefail

# === Configuration ===
REMOTE_NAME="${CLEVER_SYNC_REMOTE:-GDrive}"
REMOTE_PATH="${CLEVER_SYNC_PATH:-CLEVER_AI}"
LOCAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SRC_DIRS=(
  "$LOCAL_ROOT/CLEVER_MANIFEST.md"
  "$LOCAL_ROOT/Clever_Cognitive_Map.dot"
  "$LOCAL_ROOT/CLEVER_ARCHITECTURE_OVERVIEW.md"
  "$LOCAL_ROOT/SELF_REFLECTION_LOG.md"
  "$LOCAL_ROOT/logs"
  "$LOCAL_ROOT/tools"
)

# === Functions ===
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

sync_file_or_dir() {
  local src="$1"
  if [[ -e "$src" ]]; then
    log "→ syncing: $src"
    rclone copy "$src" "${REMOTE_NAME}:${REMOTE_PATH}/" --update --create-empty-src-dirs \
      --fast-list --transfers=4 --checkers=4 --copy-links --progress
  else
    log "⚠️  missing: $src"
  fi
}

# === Execution ===
log "Starting Clever artifact sync to ${REMOTE_NAME}:${REMOTE_PATH}"
for item in "${SRC_DIRS[@]}"; do
  sync_file_or_dir "$item"
done
log "✅ Sync completed."
