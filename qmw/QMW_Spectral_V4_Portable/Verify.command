#!/bin/bash
set -eu

PACKAGE_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
SUPPORT_ROOT="$PACKAGE_ROOT"
if [ ! -d "$SUPPORT_ROOT/quantum_chladni_synth_v1" ]; then
    SUPPORT_ROOT="$(cd "$PACKAGE_ROOT/../.." && pwd -P)"
fi
PYTHON_BIN="${QMW_PYTHON:-$PACKAGE_ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
    echo "Missing Python environment: run ./Install.command or set QMW_PYTHON." >&2
    exit 1
fi

cd "$PACKAGE_ROOT"
PYTHONPATH="$PACKAGE_ROOT:$SUPPORT_ROOT" "$PYTHON_BIN" -m unittest \
    tests.test_resonant_recording \
    tests.test_quantum_spectrum \
    tests.test_qho_chebyshev_membrane_v1 \
    tests.test_qho_parseval_modes_v1 \
    tests.test_qft_v42_parseval_overtone_bank \
    tests.test_qft_v42_bloch_spatial_voice \
    tests.test_qft_v42b_audio_bus_mixer \
    tests.test_qft_v42b_sophie_germain \
    tests.test_portable_unified_imports \
    tests.test_spectral_v4_sonification \
    tests.test_spectral_v4_supercollider_bridge
bash -n qmw/qft/StartQMWUnifiedInstrumentResonatorV4.command
bash -n qmw/qft/StartQMWQFTV4_2.command
bash -n qmw/qft/StartQMWQFTV4_2b.command
echo "QMW Spectral V4 Portable verification passed."
