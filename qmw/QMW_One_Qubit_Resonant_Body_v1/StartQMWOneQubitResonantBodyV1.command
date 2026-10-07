#!/bin/zsh
set -eu

PACKAGE_DIR="${0:A:h}"
PYTHON_BIN="$PACKAGE_DIR/.venv/bin/python"
SC_BIN="/Applications/SuperCollider.app/Contents/MacOS/sclang"
SC_FILE="$PACKAGE_DIR/supercollider/QMWOneQubitResonantBodyV1.scd"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing $PYTHON_BIN"
  echo "Install once: python3 -m venv '$PACKAGE_DIR/.venv'"
  echo "Then: '$PACKAGE_DIR/.venv/bin/pip' install -r '$PACKAGE_DIR/requirements.txt'"
  exit 1
fi

if [[ ! -x "$SC_BIN" ]]; then
  echo "SuperCollider was not found at $SC_BIN"
  exit 1
fi

cleanup() {
  if [[ -n "${SC_PID:-}" ]]; then
    kill "$SC_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

"$SC_BIN" -D "$SC_FILE" &
SC_PID=$!
cd "$PACKAGE_DIR"
"$PYTHON_BIN" -m qmw_one_qubit.runtime --open-browser
