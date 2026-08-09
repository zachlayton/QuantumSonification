#!/bin/zsh
set -eu

COMPONENT_ROOT="${0:A:h}"
PYTHON_BIN="/Users/zlayton/miniconda3/envs/music/bin/python"
SCLANG_BIN="/Applications/SuperCollider.app/Contents/MacOS/sclang"
SC_FILE="$COMPONENT_ROOT/supercollider/qmw_qiskit_compare_instrument_v1.scd"
PY_FILE="$COMPONENT_ROOT/examples/run_realtime_comparison.py"

"$SCLANG_BIN" "$SC_FILE" &
SC_PID=$!
trap 'kill "$SC_PID" 2>/dev/null || true' EXIT INT TERM
sleep 3
cd "$COMPONENT_ROOT"
PYTHONPATH="$COMPONENT_ROOT:$COMPONENT_ROOT/.." \
    "$PYTHON_BIN" -u "$PY_FILE" --route aer_noisy --period-seconds 0.4
