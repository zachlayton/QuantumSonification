#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "QMW launcher: Python was not found: $PYTHON_BIN" >&2
    echo "Install Python 3 or set PYTHON_BIN to the Python executable to use." >&2
    exit 1
fi

if ! "$PYTHON_BIN" -c "import numpy" >/dev/null 2>&1; then
    echo "QMW launcher: NumPy is required by this package." >&2
    echo "Install it with: $PYTHON_BIN -m pip install numpy" >&2
    exit 1
fi

export PYTHONPATH="$PACKAGE_DIR${PYTHONPATH:+:$PYTHONPATH}"

echo "Starting QMW QuantumFrame granular OSC stream..."
echo "Default destination: 127.0.0.1:7405"
echo "Press Ctrl-C to stop."

exec "$PYTHON_BIN" "$PACKAGE_DIR/examples/stream_xy_grains.py" "$@"
