#!/usr/bin/env bash
set -euo pipefail

# Setup a Python >=3.9 virtual environment for the backend.
# This script is intended for macOS/Linux development environments.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pick_python() {
  if command -v python3.12 >/dev/null 2>&1; then echo "python3.12"; return; fi
  if command -v python3.11 >/dev/null 2>&1; then echo "python3.11"; return; fi
  if command -v python3.10 >/dev/null 2>&1; then echo "python3.10"; return; fi
  if command -v python3.9 >/dev/null 2>&1; then echo "python3.9"; return; fi
  echo "python3"
}

PYTHON_BIN="$(pick_python)"

echo "Using Python: $($PYTHON_BIN --version 2>/dev/null || true)"

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 9):
    raise SystemExit(
        f"Python >=3.9 is required (found {sys.version.split()[0]}). "
        "Please install Python 3.9+ and re-run."
    )
PY

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv ".venv"
fi

".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install -r "src/server/requirements.txt"

echo "Backend environment ready."
echo "Next:"
echo "  bash scripts/run_server.sh --reload"

