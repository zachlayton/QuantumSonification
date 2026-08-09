"""Compose an H2-derived resonant chamber study."""

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from qiskit_nature_molecular_v1.dissociation_sonification import export_spectral_chamber_study


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the H2 spectral chamber composition")
    parser.add_argument(
        "--descriptor",
        type=Path,
        default=Path("outputs/qiskit_nature_h2_dissociation_v1/h2_dissociation_features.json"),
    )
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/qiskit_nature_h2_spectral_chamber_v4")
    )
    args = parser.parse_args()
    with args.descriptor.open(encoding="utf-8") as handle:
        dataset = json.load(handle)
    for name, path in export_spectral_chamber_study(dataset, args.output, args.sample_rate).items():
        print(name, path)


if __name__ == "__main__":
    main()

