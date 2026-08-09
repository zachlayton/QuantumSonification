"""Build and preview the H2 density-wavetable/Wilson-material adapter."""

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from qiskit_nature_molecular_v1.dissociation_sonification import (
    DissociationConfig,
    build_dense_dataset,
    export_qmw_wavetable_wilson_study,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render H2 through existing QMW wavetable/Wilson material")
    parser.add_argument("--points", type=int, default=61)
    parser.add_argument("--output", type=Path, default=Path("outputs/qiskit_nature_h2_qmw_wavetable_wilson_v5"))
    args = parser.parse_args()
    dataset = build_dense_dataset(DissociationConfig(num_points=args.points, duration_seconds=48.0))
    for name, path in export_qmw_wavetable_wilson_study(dataset, args.output).items():
        print(name, path)


if __name__ == "__main__":
    main()
