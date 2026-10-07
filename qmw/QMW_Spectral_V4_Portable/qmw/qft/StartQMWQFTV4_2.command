#!/bin/bash
set -eu

QFT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$QFT_ROOT/../.." && pwd -P)"
SUPPORT_ROOT="$REPO_ROOT"
if [ ! -f "$SUPPORT_ROOT/density/density_matrix_engine.py" ]; then
    SUPPORT_ROOT="$(cd "$REPO_ROOT/../.." && pwd -P)"
fi
if [ ! -f "$SUPPORT_ROOT/density/density_matrix_engine.py" ]; then
    echo "QMW V4.2 cannot find density/density_matrix_engine.py." >&2
    exit 1
fi
PYTHON_BIN="${QMW_PYTHON:-$(command -v python3 || true)}"
SCLANG_BIN="${QMW_SCLANG:-/Applications/SuperCollider.app/Contents/MacOS/sclang}"
SC_FILE="$REPO_ROOT/supercollider/qmw_scalar_field_observer_v4_2.scd"
ENGINE_SCRIPT="$SUPPORT_ROOT/quantumsonification_engine.py"
QHO_RATE_HZ="${QMW_QHO_RATE_HZ:-15}"
BLOCH_RATE_HZ="${QMW_BLOCH_RATE_HZ:-20}"
BLOCH_SC_PORT="${QMW_BLOCH_SC_PORT:-17832}"
NUMBA_CACHE_ROOT="${QMW_NUMBA_CACHE_DIR:-/private/tmp/qmw_v42_numba_cache}"

if [ ! -f "$ENGINE_SCRIPT" ]; then
    echo "QMW V4.2 cannot find quantumsonification_engine.py." >&2
    exit 1
fi
if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    echo "QMW V4.2 cannot find an executable Python. Set QMW_PYTHON explicitly." >&2
    exit 1
fi

case "$QHO_RATE_HZ" in
    ''|*[!0-9]*)
        echo "QMW_QHO_RATE_HZ must be an integer in [1, 60]." >&2
        exit 1
        ;;
esac
if [ "$QHO_RATE_HZ" -lt 1 ] || [ "$QHO_RATE_HZ" -gt 60 ]; then
    echo "QMW_QHO_RATE_HZ must be an integer in [1, 60]." >&2
    exit 1
fi

case "$BLOCH_RATE_HZ" in
    ''|*[!0-9]*)
        echo "QMW_BLOCH_RATE_HZ must be an integer in [1, 60]." >&2
        exit 1
        ;;
esac
if [ "$BLOCH_RATE_HZ" -lt 1 ] || [ "$BLOCH_RATE_HZ" -gt 60 ]; then
    echo "QMW_BLOCH_RATE_HZ must be an integer in [1, 60]." >&2
    exit 1
fi

case "$BLOCH_SC_PORT" in
    ''|*[!0-9]*)
        echo "QMW_BLOCH_SC_PORT must be an integer in [1024, 65535]." >&2
        exit 1
        ;;
esac
if [ "$BLOCH_SC_PORT" -lt 1024 ] || [ "$BLOCH_SC_PORT" -gt 65535 ]; then
    echo "QMW_BLOCH_SC_PORT must be an integer in [1024, 65535]." >&2
    exit 1
fi

if [ "${QMW_LAUNCH_DRY_RUN:-0}" = "1" ]; then
    echo "QMW V4.2 launch plan is valid."
    echo "  scalar field / control:      17860 / 17861"
    echo "  probability + terrain:      17863"
    echo "  QHO Parseval / control:      17830 / 17831 at ${QHO_RATE_HZ} Hz"
    echo "  four-qubit engine/control:   full profile / 7402"
    echo "  Bloch full-engine mirror:    ${BLOCH_SC_PORT} at ${BLOCH_RATE_HZ} Hz"
    echo "  plucks + Bloch voice:        outputs 1-2"
    echo "  field + overtone:            outputs 3-4"
    echo "  SuperCollider:              $SC_FILE"
    exit 0
fi

cd "$REPO_ROOT"

PORT_CONFLICT=0
for PORT in 7402 17830 17831 17860 17861 17863 "$BLOCH_SC_PORT"; do
    PORT_OWNERS="$(lsof -nP -iUDP:"$PORT" 2>/dev/null || true)"
    if [ -n "$PORT_OWNERS" ]; then
        echo "QMW V4.2 cannot start: UDP port $PORT is already in use."
        echo "$PORT_OWNERS"
        PORT_CONFLICT=1
    fi
done
if [ "$PORT_CONFLICT" -ne 0 ]; then
    echo "Stop the previous QMW V4.2 Python/SuperCollider session, then run this launcher again."
    echo "The read-only inspector on UDP 17866 may remain open."
    exit 1
fi

FIELD_PID=""
QHO_PID=""
ENGINE_PID=""
cleanup() {
    for PID in "$ENGINE_PID" "$QHO_PID" "$FIELD_PID"; do
        case "$PID" in
            ''|*[!0-9]*) continue ;;
        esac
        kill "$PID" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

mkdir -p "$NUMBA_CACHE_ROOT"

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$REPO_ROOT:$SUPPORT_ROOT" \
    "$PYTHON_BIN" -u -m qmw.qft.live_flow_osc_v4_2 --monitor-port 17864 &
FIELD_PID=$!
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$REPO_ROOT" \
    "$PYTHON_BIN" -u -m qmw.qho.live_osc \
    --output-port 17830 --control-port 17831 --rate-hz "$QHO_RATE_HZ" &
QHO_PID=$!
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$REPO_ROOT:$SUPPORT_ROOT:$SUPPORT_ROOT/qmw" \
NUMBA_CACHE_DIR="$NUMBA_CACHE_ROOT" \
    "$PYTHON_BIN" -u "$ENGINE_SCRIPT" \
    --implementation=resonator_v9 \
    --osc-profile=full \
    --diagnostics-hz "$BLOCH_RATE_HZ" \
    --sc-osc-port "$BLOCH_SC_PORT" &
ENGINE_PID=$!
sleep 5
if ! kill -0 "$FIELD_PID" 2>/dev/null \
    || ! kill -0 "$QHO_PID" 2>/dev/null \
    || ! kill -0 "$ENGINE_PID" 2>/dev/null; then
    wait "$FIELD_PID" 2>/dev/null || true
    wait "$QHO_PID" 2>/dev/null || true
    wait "$ENGINE_PID" 2>/dev/null || true
    echo "QMW V4.2 field, QHO, or four-qubit source exited during startup; SuperCollider was not launched."
    exit 1
fi
echo "Bloch voice input: canonical full engine is mirrored on UDP $BLOCH_SC_PORT"
QMW_BLOCH_SC_PORT="$BLOCH_SC_PORT" "$SCLANG_BIN" "$SC_FILE"
