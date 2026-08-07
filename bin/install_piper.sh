#!/usr/bin/env bash
set -euo pipefail

# install_piper.sh - Install Piper TTS and a small EN female model (Linux x86_64)
# - Places binary at ./bin/piper
# - Places model at ./models/piper/
# - Updates ./config/voice_profile.json if model paths are missing
# - Verifies by synthesizing a short sample to out.wav

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BIN_DIR="$ROOT_DIR/bin"
MODEL_DIR="$ROOT_DIR/models/piper"
CFG_DIR="$ROOT_DIR/config"
PIPER_BIN="$BIN_DIR/piper"
VOICE_JSON="$CFG_DIR/voice_profile.json"

mkdir -p "$BIN_DIR" "$MODEL_DIR" "$CFG_DIR"

# Detect platform
ARCH=$(uname -m)
OS=$(uname -s)
if [[ "$OS" != "Linux" ]]; then
  echo "This installer currently supports Linux only." >&2
  exit 1
fi
if [[ "$ARCH" != "x86_64" && "$ARCH" != "amd64" ]]; then
  echo "This installer currently targets x86_64/amd64. Detected: $ARCH" >&2
  exit 1
fi

# Piper binary URL (stable release for Linux x86_64)
# Note: URLs may change; adjust if needed.
PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_x86_64.tar.gz"

# Small EN female voice (LJSpeech) - lightweight
MODEL_ONNX="$MODEL_DIR/en_US-amy-medium.onnx"
MODEL_CFG="$MODEL_DIR/en_US-amy-medium.onnx.json"
MODEL_ONNX_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx.gz"
MODEL_CFG_URL="https://raw.githubusercontent.com/rhasspy/piper/v1.2.0/voices/en/en_US-amy-medium.onnx.json"

# Dependencies: curl, tar, gzip, aplay/paplay/play or ffplay for playback test
need() { command -v "$1" >/dev/null 2>&1; }
for cmd in curl tar gzip; do
  if ! need "$cmd"; then echo "Missing dependency: $cmd" >&2; exit 1; fi
done

fetch() {
  # fetch <url> <dest>
  local url="$1" dest="$2"
  if ! curl -fL "$url" -o "$dest"; then
    return 1
  fi
  return 0
}

# Download Piper binary if missing
if [[ ! -x "$PIPER_BIN" ]]; then
  echo "Downloading Piper binary..."
  TMPDIR=$(mktemp -d)
  trap 'rm -rf "$TMPDIR"' EXIT
  if ! fetch "$PIPER_URL" "$TMPDIR/piper.tar.gz"; then
    echo "\n[offline] Could not download Piper. Manual install steps:" >&2
    echo "  1) Place the 'piper' executable at $PIPER_BIN (chmod +x)" >&2
    echo "  2) Place an onnx model + config in $MODEL_DIR" >&2
    echo "  3) Update $VOICE_JSON to point to those files" >&2
    exit 2
  fi
  tar -xzf "$TMPDIR/piper.tar.gz" -C "$TMPDIR"
  # Find extracted piper binary
  EXE=$(find "$TMPDIR" -type f -name piper -executable | head -n 1)
  if [[ -z "$EXE" ]]; then
    echo "Could not find piper executable in archive" >&2
    exit 1
  fi
  cp "$EXE" "$PIPER_BIN"
  chmod +x "$PIPER_BIN"
  echo "Piper installed to $PIPER_BIN"
else
  echo "Piper already present at $PIPER_BIN"
fi

# Download model if missing
if [[ ! -f "$MODEL_ONNX" ]]; then
  echo "Downloading model (onnx)..."
  if ! fetch "$MODEL_ONNX_URL" "$MODEL_ONNX.gz"; then
    echo "\n[offline] Could not download model. Manual install steps:" >&2
    echo "  1) Place a Piper onnx model at: $MODEL_ONNX" >&2
    echo "  2) Place its JSON config at: $MODEL_CFG" >&2
    echo "  3) Re-run this script to patch voice_profile.json and verify" >&2
    exit 2
  fi
  # Verify gzip
  if ! gzip -t "$MODEL_ONNX.gz" 2>/dev/null; then
    echo "Downloaded model is not a valid gzip file. Cleaning up." >&2
    rm -f "$MODEL_ONNX.gz"
    exit 2
  fi
  gzip -d -f "$MODEL_ONNX.gz"
else
  echo "Model ONNX present: $MODEL_ONNX"
fi

if [[ ! -f "$MODEL_CFG" ]]; then
  echo "Downloading model config (json)..."
  if ! fetch "$MODEL_CFG_URL" "$MODEL_CFG"; then
    echo "\n[offline] Could not download model config. Manual install steps:" >&2
    echo "  1) Place the model JSON at: $MODEL_CFG" >&2
    exit 2
  fi
else
  echo "Model config present: $MODEL_CFG"
fi

# Update voice_profile.json if missing or pointing elsewhere
if [[ ! -f "$VOICE_JSON" ]]; then
  cat > "$VOICE_JSON" <<JSON
{
  "engine": "piper",
  "model": "models/piper/$(basename "$MODEL_ONNX")",
  "config": "models/piper/$(basename "$MODEL_CFG")",
  "pitch": 0.94,
  "speed": 0.91,
  "humor_level": 0.30,
  "style": "GeminiWarm"
}
JSON
  echo "Created $VOICE_JSON"
else
  # Patch in-place if keys missing
  # Minimal jq-less edit: replace model/config if file contains default placeholders
  if grep -q 'models/piper/en_US-default.onnx' "$VOICE_JSON"; then
    sed -i "s#models/piper/en_US-default.onnx#models/piper/$(basename "$MODEL_ONNX")#" "$VOICE_JSON"
  fi
  if grep -q 'models/piper/en_US-default.json' "$VOICE_JSON"; then
    sed -i "s#models/piper/en_US-default.json#models/piper/$(basename "$MODEL_CFG")#" "$VOICE_JSON"
  fi
  echo "Updated $VOICE_JSON (if needed)"
fi

# Verify synthesis to out.wav
OUT_WAV="$ROOT_DIR/out.wav"
TEXT="Hello Jay. Piper is ready."

set +e
"$PIPER_BIN" --model "$MODEL_ONNX" --config "$MODEL_CFG" --length_scale 0.91 --noise_scale 0.5 -f "$OUT_WAV" <<< "$TEXT"
RC=$?
set -e
if [[ $RC -ne 0 ]]; then
  echo "Piper synthesis failed (exit $RC)" >&2
  exit $RC
fi

if [[ -f "$OUT_WAV" ]]; then
  SZ=$(stat -c%s "$OUT_WAV" 2>/dev/null || wc -c < "$OUT_WAV")
  echo "Synthesis OK: $OUT_WAV ($SZ bytes)"
else
  echo "No output generated: $OUT_WAV" >&2
  exit 1
fi

echo "Done."
