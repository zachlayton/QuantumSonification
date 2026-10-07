#!/bin/sh
set -eu

PACKAGE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN="${QRM_PYTHON:-$PACKAGE_ROOT/.venv/bin/python}"
DEFAULT_SCLANG="/Applications/SuperCollider.app/Contents/MacOS/sclang"
SCLANG_BIN="${QRM_SCLANG:-$DEFAULT_SCLANG}"
SCLANG_CONFIG="${QRM_SCLANG_CONFIG:-}"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Python environment not found. Run Install.command first." >&2
    exit 1
fi
if [ ! -x "$SCLANG_BIN" ]; then
    SCLANG_BIN="$(command -v sclang || true)"
fi
if [ -z "$SCLANG_BIN" ] || [ ! -x "$SCLANG_BIN" ]; then
    echo "SuperCollider sclang was not found. Install SuperCollider or set QRM_SCLANG." >&2
    exit 1
fi
if [ -z "$SCLANG_CONFIG" ] && [ "$SCLANG_BIN" = "$DEFAULT_SCLANG" ]; then
    SCLANG_CONFIG="$PACKAGE_ROOT/supercollider/sclang_core_macos.yaml"
fi

cd "$PACKAGE_ROOT"
"$PYTHON_BIN" -u run_backend.py &
BACKEND_PID=$!
cleanup() {
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM
sleep 0.8
if [ -n "$SCLANG_CONFIG" ]; then
    XDG_CONFIG_HOME="${QRM_SC_CONFIG_HOME:-$PACKAGE_ROOT/supercollider}"
    export XDG_CONFIG_HOME
    "$SCLANG_BIN" -a -l "$SCLANG_CONFIG" "$PACKAGE_ROOT/supercollider/QuantumResonantMembraneV1.scd"
else
    "$SCLANG_BIN" "$PACKAGE_ROOT/supercollider/QuantumResonantMembraneV1.scd"
fi
