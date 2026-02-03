#!/usr/bin/env bash
set -euo pipefail

# Run the FastAPI backend using a Python >=3.9 interpreter.
# Prefers the local `.venv` if present.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN=""
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="python3.11"
elif command -v python3.10 >/dev/null 2>&1; then
  PYTHON_BIN="python3.10"
elif command -v python3.9 >/dev/null 2>&1; then
  PYTHON_BIN="python3.9"
else
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 9):
    raise SystemExit(
        f"Python >=3.9 is required (found {sys.version.split()[0]}). "
        "Run: bash scripts/setup_server_venv.sh"
    )
PY

export PYTHONPATH="${PYTHONPATH:-}:."

exec "$PYTHON_BIN" "src/server/main.py" "$@"

