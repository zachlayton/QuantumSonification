#!/bin/bash
set -eu

PACKAGE_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
PYTHON_BIN="${QMW_PYTHON:-python3}"

"$PYTHON_BIN" -m venv "$PACKAGE_ROOT/.venv"
"$PACKAGE_ROOT/.venv/bin/python" -m pip install --upgrade pip
"$PACKAGE_ROOT/.venv/bin/python" -m pip install -r "$PACKAGE_ROOT/requirements.txt"
echo "QMW Spectral V4 Portable environment ready: $PACKAGE_ROOT/.venv"
