"""Generate the dense H2 dataset and two-route offline audio study."""

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from qiskit_nature_molecular_v1.dissociation_sonification import (
    DissociationConfig,
    build_dense_dataset,
    export_study,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an unquantized H2 dissociation study")
    parser.add_argument("--points", type=int, default=61)
    parser.add_argument("--duration", type=float, default=36.0)
    parser.add_argument("--output", type=Path, default=Path("outputs/qiskit_nature_h2_dissociation_v1"))
    args = parser.parse_args()
    dataset = build_dense_dataset(DissociationConfig(num_points=args.points, duration_seconds=args.duration))
    for name, path in export_study(dataset, args.output).items():
        print(name, path)


if __name__ == "__main__":
    main()

