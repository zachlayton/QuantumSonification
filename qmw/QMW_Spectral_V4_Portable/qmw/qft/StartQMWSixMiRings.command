#!/bin/bash
# Deliberately small performance session: QRM + resonant interaction + six
# bounded MiRings voices.  It excludes the V2/V3 observer stack so listening
# is not competing with relational, temporal, modal, and geometry updates.
set -eu

QFT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$QFT_ROOT/../.." && pwd -P)"

export QMW_RESONATOR_SC_FILE="$REPO_ROOT/Quantum_Resonant_Membrane_v1/supercollider/QMWUnifiedResonantInstrumentV1.scd"
export QMW_SIMPLE_SIX_MIRINGS=1
export QMW_SEALED_FRAME_SOURCE=0
export QMW_RELATIONAL_SPECTRAL_PORT=0
export QMW_TEMPORAL_MEMORY_PORT=0
export QMW_TEMPORAL_MEMORY_CONTROL_PORT=0
export QMW_HARMONIC_MEMORY_INTERFERENCE=0
export QMW_HARMONIC_MEMORY_DEVELOPMENT_PORT=0
export QMW_INTERACTION_RATE_HZ=4
export QMW_QHO_RATE_HZ=4

exec "$QFT_ROOT/StartQMWUnifiedResonantInstrumentV1.command" "$@"
