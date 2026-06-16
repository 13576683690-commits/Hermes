#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/macgy/Desktop/Codex-Hermes"
if [ -x "$REPO_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="${PYTHON_BIN:-$REPO_DIR/.venv/bin/python}"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/evolution-publish.log"
PAGE_PATH="evolution-tracking/index.html"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting evolution archive publish"

  "$PYTHON_BIN" "$REPO_DIR/evolution-tracking/update_evolution.py"

  if git diff --quiet -- "$PAGE_PATH" && ! git ls-files --others --exclude-standard -- "$PAGE_PATH" | grep -q .; then
    echo "No evolution archive changes to publish."
    exit 0
  fi

  git add "$PAGE_PATH"
  git commit -m "Update evolution archive"
  git push origin main

  echo "Evolution archive published."
} 2>&1 | tee -a "$LOG_FILE"
