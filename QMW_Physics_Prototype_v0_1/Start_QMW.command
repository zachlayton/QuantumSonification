#!/bin/bash
set -e
QMW_PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$QMW_PROJECT_DIR"
# Reuse a healthy inspector rather than create a second physics owner.
if python3 -c '
import json, sys, urllib.request, webbrowser
try:
    with urllib.request.urlopen("http://127.0.0.1:8767/api/state", timeout=1) as response:
        state = json.load(response)
    if state.get("physics", {}).get("schema_version") != "qmw.physics/0.1":
        sys.exit(1)
    print("Opening the running QMW inspector at http://127.0.0.1:8767")
    webbrowser.open("http://127.0.0.1:8767/")
except Exception:
    sys.exit(1)
'; then
    exit 0
fi
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
exec .venv/bin/python -m qmw serve --port 8767 --open
