#!/usr/bin/env bash
set -e
SESSION="clever"
if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "Stopped Clever voice daemon."
else
  echo "No running Clever session."
fi
