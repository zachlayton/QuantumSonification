#!/bin/bash
set -eu

PACKAGE_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
exec "$PACKAGE_ROOT/qmw/qft/StartQMWUnifiedInstrumentResonatorV4.command" "$@"
