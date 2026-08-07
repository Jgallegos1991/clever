# hub/bin/status.sh
#!/usr/bin/env bash
set -euo pipefail
echo "[ps]"
ps aux | egrep "app.py|voice_daemon.py|hub/bin/start.sh" | egrep -v egrep || true
echo
echo "[health]"
curl -sS http://127.0.0.1:8000/health || echo "clever_app: no response"
