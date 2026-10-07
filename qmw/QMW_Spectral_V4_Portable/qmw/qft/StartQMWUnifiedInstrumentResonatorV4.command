#!/bin/bash
# V4 is an opt-in spectral source layer over a complete V3 runtime.  The V3
# checkout stays separate: no existing V3 sources are copied into this branch.
set -eu

QFT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$QFT_ROOT/../.." && pwd -P)"
DEFAULT_V3_ROOT="$REPO_ROOT/worktrees/qmw-v3-runtime"
if [ ! -d "$DEFAULT_V3_ROOT" ]; then
    DEFAULT_V3_ROOT="$REPO_ROOT"
fi
V3_ROOT="${QMW_V3_ROOT:-$DEFAULT_V3_ROOT}"
V3_LAUNCHER="$V3_ROOT/qmw/qft/StartQMWUnifiedResonantInstrumentV1.command"
V3_SC_FILE="$V3_ROOT/Quantum_Resonant_Membrane_v1/supercollider/QMWUnifiedInstrumentResonatorV3.scd"
BOOTSTRAP_FILE="$REPO_ROOT/supercollider/qmw_spectral_v4_v3_bootstrap.scd"
BRIDGE_FILE="$REPO_ROOT/supercollider/qmw_spectral_v4_v3_fx_bridge.scd"

for REQUIRED in "$V3_LAUNCHER" "$V3_SC_FILE" "$BOOTSTRAP_FILE" "$BRIDGE_FILE"; do
    if [ ! -f "$REQUIRED" ]; then
        echo "QMW V4 launcher cannot start: missing $REQUIRED" >&2
        echo "This spectral checkout has no complete V3 runtime. Set QMW_V3_ROOT" >&2
        echo "to a V3 checkout; no stashed work has been restored automatically." >&2
        exit 1
    fi
done

if [ ! -x "$V3_LAUNCHER" ]; then
    echo "QMW V4 launcher cannot start: V3 launcher is not executable: $V3_LAUNCHER" >&2
    exit 1
fi

export QMW_V3_SC_FILE="$V3_SC_FILE"
export QMW_V4_SPECTRAL_BRIDGE_FILE="$BRIDGE_FILE"
export QMW_RESONATOR_SC_FILE="$BOOTSTRAP_FILE"
# Dense V4 performance default; explicit performer settings still win.
export QMW_PLUCK_THRESHOLD="${QMW_PLUCK_THRESHOLD:-0.005}"

if [ "${QMW_LAUNCH_DRY_RUN:-0}" = "1" ]; then
    echo "QMW Unified Instrument Resonator V4 launch plan is valid."
    echo "  V3 runtime:  $V3_ROOT"
    echo "  V4 bridge:   $BRIDGE_FILE"
    echo "  V4 OSC:      /qmw/v4/spectral/frame on UDP 7404"
    echo "  initial mix: dry=0, fx-send=0"
    exit 0
fi

exec "$V3_LAUNCHER" "$@"
