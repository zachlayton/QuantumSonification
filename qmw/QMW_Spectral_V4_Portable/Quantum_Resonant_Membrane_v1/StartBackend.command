#!/bin/sh
set -eu

PACKAGE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN="${QRM_PYTHON:-$PACKAGE_ROOT/.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Python environment not found. Run Install.command first." >&2
    exit 1
fi
cd "$PACKAGE_ROOT"
exec "$PYTHON_BIN" -u run_backend.py "$@"
