#!/usr/bin/env bash
set -euo pipefail

# Offline-friendly Piper installer for Clever
# Why: Maintain digital sovereignty by installing from local files only
# Where: Places piper binary under repo bin/ and models under models/piper/
# How: Copy from user-provided local paths, chmod +x binary, update voice_profile.local.json

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BIN_DIR="$ROOT_DIR/bin"
MODEL_DIR="$ROOT_DIR/models/piper"
CFG_DIR="$ROOT_DIR/config"

usage() {
  echo "Usage: $0 /path/to/piper_binary /path/to/model.onnx /path/to/model.json" >&2
  exit 1
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 3 ]]; then
  usage
fi

SRC_BIN="$1"
SRC_ONNX="$2"
SRC_JSON="$3"

if [[ ! -f "$SRC_BIN" || ! -f "$SRC_ONNX" || ! -f "$SRC_JSON" ]]; then
  echo "Error: One or more source files do not exist" >&2
  usage
fi

mkdir -p "$BIN_DIR" "$MODEL_DIR" "$CFG_DIR"

cp -f "$SRC_BIN" "$BIN_DIR/piper"
chmod +x "$BIN_DIR/piper"

MODEL_NAME=$(basename "$SRC_ONNX")
CFG_NAME=$(basename "$SRC_JSON")

cp -f "$SRC_ONNX" "$MODEL_DIR/$MODEL_NAME"
cp -f "$SRC_JSON" "$MODEL_DIR/$CFG_NAME"

cat > "$CFG_DIR/voice_profile.local.json" <<EOF
{
  "engine": "piper",
  "model": "$MODEL_DIR/$MODEL_NAME",
  "config": "$MODEL_DIR/$CFG_NAME",
  "speed": 0.90,
  "pitch": 0.94,
  "humor_level": 0.30,
  "style": "GeminiWarm"
}
EOF

echo "✅ Installed piper locally: $BIN_DIR/piper"
echo "✅ Model: $MODEL_DIR/$MODEL_NAME"
echo "✅ Config: $MODEL_DIR/$CFG_NAME"
echo "Tip: add to PATH for current session: export PATH=\"$BIN_DIR:\$PATH\""