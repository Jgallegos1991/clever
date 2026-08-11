#!/bin/bash
# Clever AI Independent Startup Script
# This starts Clever without VS Code interference!

VOICE_MODE=1
LOG_SYNC_PID=""
APP_PID=""
LOG_SYNC_AUTOSTART="${CLEVER_LOG_SYNC_AUTOSTART:-1}"
LOG_SYNC_INTERVAL_MINUTES="${CLEVER_LOG_SYNC_INTERVAL_MINUTES:-180}"

if [[ -n "${CLEVER_VOICE_AUTO_START:-}" ]]; then
    case "${CLEVER_VOICE_AUTO_START,,}" in
        0|false|no|off) VOICE_MODE=0 ;;
        *) VOICE_MODE=1 ;;
    esac
fi

APP_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --with-voice)
            VOICE_MODE=1
            ;;
        --no-voice)
            VOICE_MODE=0
            ;;
        --voice=*)
            value="${1#*=}"
            case "${value,,}" in
                0|false|no|off) VOICE_MODE=0 ;;
                *) VOICE_MODE=1 ;;
            esac
            ;;
        *)
            APP_ARGS+=("$1")
            ;;
    esac
    shift
done

set -- "${APP_ARGS[@]}"

should_start_log_sync() {
    local value="${LOG_SYNC_AUTOSTART,,}"
    case "$value" in
        0|false|no|off|"") return 1 ;;
        *) return 0 ;;
    esac
}

start_log_sync_service() {
    if ! should_start_log_sync; then
        echo "🗂 Log sync service auto-start disabled (set CLEVER_LOG_SYNC_AUTOSTART=1 to enable)."
        return
    fi

    if ! command -v rclone >/dev/null 2>&1; then
        echo "⚠️  rclone not available; skipping log sync service start."
        return
    fi

    mkdir -p logs/codex_diagnostics
    echo "🗂 Starting log sync service (interval: ${LOG_SYNC_INTERVAL_MINUTES} minute(s))..."
    python tools/log_sync_service.py --interval-minutes "${LOG_SYNC_INTERVAL_MINUTES}" >> logs/codex_diagnostics/log_sync_service.out 2>&1 &
    LOG_SYNC_PID=$!
}

cleanup() {
    if [[ -n "${LOG_SYNC_PID}" ]]; then
        if kill -0 "${LOG_SYNC_PID}" >/dev/null 2>&1; then
            echo ""
            echo "🗂 Stopping log sync service..."
            kill "${LOG_SYNC_PID}" >/dev/null 2>&1 || true
            wait "${LOG_SYNC_PID}" 2>/dev/null || true
        fi
    fi
    if [[ $VOICE_MODE -eq 1 && -n "${APP_PID}" ]]; then
        if kill -0 "${APP_PID}" >/dev/null 2>&1; then
            echo ""
            echo "🔇 Stopping Clever Flask service..."
            kill "${APP_PID}" >/dev/null 2>&1 || true
            wait "${APP_PID}" 2>/dev/null || true
        fi
    fi
}

trap cleanup EXIT INT TERM

echo "🧠 STARTING CLEVER AI - JAY'S DIGITAL BRAIN EXTENSION"
echo "=================================================="
if [[ $VOICE_MODE -eq 1 ]]; then
    echo "🎙 Voice interaction: ENABLED (use --no-voice to disable)"
else
    echo "🤫 Voice interaction: DISABLED (use --with-voice to enable)"
fi
echo ""

# Resolve repository root from this script's canonical runtime home.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEVER_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$CLEVER_DIR"

echo "⚡ Activating Clever's environment..."
source .venv/bin/activate

if ! python -c "import flask" >/dev/null 2>&1; then
    echo "❌ Flask not available inside the Clever virtual environment."
    echo "   Run: source .venv/bin/activate && pip install -r requirements.txt"
    echo "   (Voice launch aborted.)"
    exit 1
fi

if pgrep -f "code" > /dev/null; then
    echo "⚠️  WARNING: VS Code is still running and may interfere with Clever!"
    echo "   Consider closing VS Code for optimal Clever performance."
    echo ""
fi

echo "📊 System Status Before Clever Startup:"
echo "   Memory Available: $(free -h | awk 'NR==2{printf "%.1fGB", $7/1024/1024}')"
echo "   CPU Load: $(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')"
echo ""

echo "🚀 Launching Clever AI..."
echo "   - Persona Engine: Authentic Jay-specific personality"
echo "   - Memory System: Remembers everything"
echo "   - Evolution Engine: Continuous learning"
echo "   - File Intelligence: Complete system awareness"
echo "   - Holographic UI: Particle interface"
echo ""

start_log_sync_service

export FLASK_ENV=production
export FLASK_DEBUG=0
export PYTHONPATH="$CLEVER_DIR:$PYTHONPATH"

echo "✨ CLEVER IS STARTING UP..."
echo "   Access at: http://localhost:5000"
echo "   Tailscale: http://penguin:5000"
echo ""
echo "Press Ctrl+C to stop Clever when you're done"
echo "=================================================="

if [[ $VOICE_MODE -eq 1 ]]; then
    echo "🎙 Voice interaction enabled – launching Flask app in background."
    python app.py &
    APP_PID=$!

    sleep 2
    echo "🗣️  Starting Clever voice loop. Say 'Hey Clever' or type 'quit' to exit."
    python interface/clever_voice_loop.py "$@"
    voice_status=$?

    if [[ $voice_status -ne 0 ]]; then
        echo "⚠️  Voice loop exited with status ${voice_status}. Keeping Clever running without voice."
        echo "🤫 Voice interaction disabled; Clever continues in text/UI mode. Press Ctrl+C to stop."
        wait "${APP_PID}"
        exit 0
    fi

    echo "🔇 Voice loop ended gracefully. Shutting down Clever."
    exit 0
fi

python app.py "$@"

echo ""
echo "🧠 Clever AI shutdown complete. See you next time, Jay!"
