#!/usr/bin/env bash
set -euo pipefail

# Synthesizes a short utterance to a WAV file using piper and the repo's voice_profile.json
# Usage:
#   bin/test_piper.sh "Your text here" /tmp/output.wav [model.onnx] [config.json]
#   PIPER_MODEL=/path/to/model.onnx PIPER_CONFIG=/path/to/config.json bin/test_piper.sh "text" /tmp/out.wav
# Notes:
#   - If config/voice_profile.local.json exists, it overrides config/voice_profile.json
# Defaults:
#   text = "Piper voice check. Hello, Jay."
#   out  = ./out.wav (repo root)

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MODEL_JSON="$ROOT_DIR/config/voice_profile.json"
LOCAL_JSON="$ROOT_DIR/config/voice_profile.local.json"
if [[ -f "$LOCAL_JSON" ]]; then MODEL_JSON="$LOCAL_JSON"; fi

TEXT="${1:-Piper voice check. Hello, Jay.}"
OUT_WAV="${2:-$ROOT_DIR/out.wav}"

# Prefer system piper, fall back to repo-local binary if present
if command -v piper >/dev/null 2>&1; then
  PIPER_BIN="piper"
elif [[ -x "$ROOT_DIR/bin/piper" ]]; then
  PIPER_BIN="$ROOT_DIR/bin/piper"
else
  echo "Error: piper not found on PATH and no repo-local binary at $ROOT_DIR/bin/piper" >&2
  exit 1
fi

if [[ ! -f "$MODEL_JSON" ]]; then
  echo "voice_profile.json not found: $MODEL_JSON" >&2
  exit 1
fi

read -r MODEL CFG SPEED < <(python3 - <<PY
import json
from pathlib import Path
p=Path("$MODEL_JSON")
try:
    d=json.loads(p.read_text())
    print(d.get('model',''), d.get('config',''), d.get('speed',0.91))
except Exception:
    print('', '', 0.91)
PY
)

# Allow overrides via positional args 3/4 or env vars PIPER_MODEL/PIPER_CONFIG
ARG_MODEL="${3:-}"
ARG_CFG="${4:-}"
if [[ -n "${PIPER_MODEL:-}" ]]; then MODEL="$PIPER_MODEL"; fi
if [[ -n "${PIPER_CONFIG:-}" ]]; then CFG="$PIPER_CONFIG"; fi
if [[ -n "$ARG_MODEL" ]]; then MODEL="$ARG_MODEL"; fi
if [[ -n "$ARG_CFG" ]]; then CFG="$ARG_CFG"; fi

if [[ -z "$MODEL" || -z "$CFG" ]]; then
  echo "Missing model/config. Either populate config/voice_profile.json or pass MODEL/CFG overrides:" >&2
  echo "  bin/test_piper.sh \"text\" /tmp/out.wav /path/to/model.onnx /path/to/config.json" >&2
  echo "  PIPER_MODEL=/path/to/model.onnx PIPER_CONFIG=/path/to/config.json bin/test_piper.sh \"text\" /tmp/out.wav" >&2
  exit 2
fi

MODEL_PATH="$ROOT_DIR/$MODEL"
CFG_PATH="$ROOT_DIR/$CFG"
# If MODEL/CFG are absolute paths, use as-is
if [[ "$MODEL" = /* ]]; then MODEL_PATH="$MODEL"; fi
if [[ "$CFG" = /* ]]; then CFG_PATH="$CFG"; fi
if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Model file not found: $MODEL_PATH" >&2
  echo "Tip: Supply a different path via arg 3 or PIPER_MODEL env var." >&2
  exit 2
fi
if [[ ! -f "$CFG_PATH" ]]; then
  echo "Config file not found: $CFG_PATH" >&2
  echo "Tip: Supply a different path via arg 4 or PIPER_CONFIG env var." >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT_WAV")"
echo "🔊 Synthesizing via piper..."
echo "   model: $MODEL_PATH"
echo "   config: $CFG_PATH"
echo "   length_scale(speed): $SPEED"

"$PIPER_BIN" --model "$MODEL_PATH" --config "$CFG_PATH" \
  --length_scale "$SPEED" --noise_scale 0.5 -f "$OUT_WAV" <<< "$TEXT"

if [[ -f "$OUT_WAV" ]]; then
  SZ=$(stat -c%s "$OUT_WAV" 2>/dev/null || wc -c < "$OUT_WAV")
  echo "✅ Wrote: $OUT_WAV ($SZ bytes)"
  exit 0
else
  echo "Failed to produce $OUT_WAV" >&2
  exit 1
fi
