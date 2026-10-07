#!/bin/bash
# V2 reuses the complete V1 session and adds bounded sealed-frame receivers.
set -eu

QFT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$QFT_ROOT/../.." && pwd -P)"
export QMW_RESONATOR_SC_FILE="$REPO_ROOT/Quantum_Resonant_Membrane_v1/supercollider/QMWUnifiedInstrumentResonatorV2.scd"
export QMW_SEALED_FRAME_SOURCE=1
exec "$QFT_ROOT/StartQMWUnifiedResonantInstrumentV1.command" "$@"
