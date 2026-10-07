#!/bin/sh
set -eu

PACKAGE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN="${QRM_PYTHON:-$PACKAGE_ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="${QRM_PYTHON:-python3}"
fi
cd "$PACKAGE_ROOT"
exec "$PYTHON_BIN" scripts/verify_package.py
