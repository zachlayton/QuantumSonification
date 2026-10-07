#!/bin/sh
set -eu

PACKAGE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN="${QRM_PYTHON:-python3}"

cd "$PACKAGE_ROOT"
echo "Creating an isolated Quantum Resonant Membrane environment..."
"$PYTHON_BIN" -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
echo ""
echo "Installed. Run StartQuantumResonantMembrane.command next."
