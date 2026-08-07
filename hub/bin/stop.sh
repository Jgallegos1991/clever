# hub/bin/stop.sh
#!/usr/bin/env bash
set -euo pipefail
pkill -f "python app.py --port 8000" || true
pkill -f "python voice_daemon.py" || true
pkill -f "Synaptic-Hub/hub/bin/start.sh" || true
echo "[hub] stopped."
