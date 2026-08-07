#!/usr/bin/env bash
set -e
SESSION="clever"
cd "$HOME/Clever"
source .venv/bin/activate
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" "python voice_daemon.py"
  echo "Started Clever voice daemon in tmux session '$SESSION'."
else
  echo "Clever already running in session '$SESSION'."
fi
