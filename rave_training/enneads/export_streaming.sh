#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /absolute/path/to/completed/rave/run" >&2
  exit 2
fi

RUN_DIR="$1"
if [[ ! -d "$RUN_DIR" ]]; then
  echo "Run directory does not exist: $RUN_DIR" >&2
  exit 1
fi

rave export --run "$RUN_DIR" --streaming

