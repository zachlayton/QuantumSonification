#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=/workspace/enneads
VENV_DIR="$PROJECT_DIR/venv"
RAVE_CONFIG_DIR="$VENV_DIR/lib/python3.11/site-packages/rave/configs"
CHECKPOINT_ROOT="$PROJECT_DIR/runs/enneads_be81ca5504"

export MPLCONFIGDIR="$PROJECT_DIR/.cache/matplotlib"
export NUMBA_CACHE_DIR="$PROJECT_DIR/.cache/numba"
export PYTHONUNBUFFERED=1

mkdir -p "$PROJECT_DIR/runs" "$MPLCONFIGDIR" "$NUMBA_CACHE_DIR"
cd "$PROJECT_DIR"

TRAIN_ARGS=(
  --config "$RAVE_CONFIG_DIR/v2.gin"
  --db_path "$PROJECT_DIR/dataset"
  --out_path "$PROJECT_DIR/runs"
  --name enneads
  --channels 1
  --augment "$RAVE_CONFIG_DIR/augmentations/mute.gin"
  --augment "$RAVE_CONFIG_DIR/augmentations/gain.gin"
  --gpu 0
  --workers 4
  --max_steps 1500000
  --val_every 10000
  --save_every 100000
  --noprogress
)

LATEST_CHECKPOINT=""
if [[ -d "$CHECKPOINT_ROOT" ]]; then
  LATEST_CHECKPOINT="$(find "$CHECKPOINT_ROOT" -type f -name '*.ckpt' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)"
fi

if [[ -n "$LATEST_CHECKPOINT" ]]; then
  echo "Resuming RAVE from $LATEST_CHECKPOINT"
  TRAIN_ARGS+=(--ckpt "$LATEST_CHECKPOINT")
fi

exec "$VENV_DIR/bin/rave" train "${TRAIN_ARGS[@]}"
