#!/bin/bash
# V3 reuses the complete V2 session and adds read-only relational-Laplacian
# shaping plus an optional independent temporal-memory delay sidecar.
set -eu

QFT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$QFT_ROOT/../.." && pwd -P)"
export QMW_RESONATOR_SC_FILE="$REPO_ROOT/Quantum_Resonant_Membrane_v1/supercollider/QMWUnifiedInstrumentResonatorV3.scd"
export QMW_SEALED_FRAME_SOURCE=1
export QMW_RELATIONAL_SPECTRAL_PORT="${QMW_RELATIONAL_SPECTRAL_PORT:-17881}"
export QMW_TEMPORAL_MEMORY_PORT="${QMW_TEMPORAL_MEMORY_PORT:-17884}"
export QMW_TEMPORAL_MEMORY_CONTROL_PORT="${QMW_TEMPORAL_MEMORY_CONTROL_PORT:-17885}"
export QMW_HARMONIC_MEMORY_INTERFERENCE="${QMW_HARMONIC_MEMORY_INTERFERENCE:-0}"
export QMW_HARMONIC_MEMORY_DEVELOPMENT_PORT="${QMW_HARMONIC_MEMORY_DEVELOPMENT_PORT:-0}"
exec "$QFT_ROOT/StartQMWUnifiedResonantInstrumentV1.command" "$@"
