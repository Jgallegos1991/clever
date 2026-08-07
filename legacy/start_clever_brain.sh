#!/bin/bash
# Clever Auto-Start Script
# Makes Clever the default AI system on this Chromebook

set -euo pipefail

CLEVER_DIR="/home/jgallegos1991/Clever"
VENV_ACTIVATE="$CLEVER_DIR/.venv/bin/activate"
LOG_DIR="$CLEVER_DIR/logs/autostart"
mkdir -p "$LOG_DIR"

echo "🚀 Starting Clever as Chromebook AI Brain..."
cd "$CLEVER_DIR"

if [ -f "$VENV_ACTIVATE" ]; then
    echo "⚡ Activating virtual environment..."
    # shellcheck disable=SC1090
    source "$VENV_ACTIVATE"
else
    echo "❌ Virtual environment not found at $VENV_ACTIVATE"
    exit 1
fi

# Ensure voice + clever features stay enabled unless explicitly disabled upstream
export CLEVER_VOICE_ENABLED="${CLEVER_VOICE_ENABLED:-1}"
export VOICE_OK="${VOICE_OK:-1}"
export FLASK_ENV=production
export FLASK_DEBUG=0
export PYTHONPATH="$CLEVER_DIR:${PYTHONPATH:-}"

timestamp() {
    date -u '+%Y-%m-%dT%H:%M:%SZ'
}

log_status() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_DIR/autostart.log"
}

log_status "Initializing Clever auto-boot stack..."

# Start main Clever application
python app.py >> "$LOG_DIR/clever_app.log" 2>&1 &
CLEVER_PID=$!
log_status "Clever Flask app started (PID $CLEVER_PID)"

# Start voice system
python clever_voice_takeover.py >> "$LOG_DIR/clever_voice.log" 2>&1 &
VOICE_PID=$!
log_status "Voice engine started (PID $VOICE_PID)"

# Start always-on monitor
python clever_always_running.py --daemon >> "$LOG_DIR/clever_daemon.log" 2>&1 &
DAEMON_PID=$!
log_status "Always-running monitor started (PID $DAEMON_PID)"

# Save PIDs for management
echo "$CLEVER_PID" > /tmp/clever_main.pid
echo "$VOICE_PID" > /tmp/clever_voice.pid
echo "$DAEMON_PID" > /tmp/clever_daemon.pid

log_status "✅ Clever AI brain stack online at http://localhost:5000"
log_status "🗣️ Voice activation ready — Jay can say 'IT'S TIME!'"

# Keep script running to maintain services
wait
