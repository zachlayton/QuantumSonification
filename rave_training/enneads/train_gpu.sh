#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /absolute/path/to/enneads-project" >&2
  exit 2
fi

PROJECT_DIR="$1"
DATASET_DIR="$PROJECT_DIR/dataset"
RUNS_DIR="$PROJECT_DIR/runs"
RAVE_CONFIG_DIR="$(python -c 'from pathlib import Path; import rave; print(Path(rave.__file__).resolve().parent / "configs")')"

if [[ ! -f "$DATASET_DIR/metadata.yaml" ]]; then
  echo "Missing preprocessed dataset: $DATASET_DIR" >&2
  exit 1
fi

python -c 'import torch; assert torch.cuda.is_available(), "CUDA is not available"; print(torch.cuda.get_device_name(0))'
mkdir -p "$RUNS_DIR"

rave train \
  --config "$RAVE_CONFIG_DIR/v2.gin" \
  --db_path "$DATASET_DIR" \
  --out_path "$RUNS_DIR" \
  --name enneads \
  --channels 1 \
  --augment "$RAVE_CONFIG_DIR/augmentations/mute.gin" \
  --augment "$RAVE_CONFIG_DIR/augmentations/gain.gin" \
  --gpu 0 \
  --workers 4 \
  --max_steps 1500000 \
  --val_every 10000 \
  --save_every 100000 \
  --noprogress
