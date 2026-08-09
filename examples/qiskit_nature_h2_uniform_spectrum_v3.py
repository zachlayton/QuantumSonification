"""Render every computed H2 excitation through one uniform frequency downshift."""

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from qiskit_nature_molecular_v1.dissociation_sonification import export_uniform_downshift_study


def main() -> None:
    parser = argparse.ArgumentParser(description="Uniformly downshift the complete computed H2 spectrum")
    parser.add_argument(
        "--descriptor",
        type=Path,
        default=Path("outputs/qiskit_nature_h2_dissociation_v1/h2_dissociation_features.json"),
    )
    parser.add_argument("--sample-rate", type=int, default=96_000)
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/qiskit_nature_h2_uniform_spectrum_v3")
    )
    args = parser.parse_args()
    with args.descriptor.open(encoding="utf-8") as handle:
        dataset = json.load(handle)
    for name, path in export_uniform_downshift_study(dataset, args.output, args.sample_rate).items():
        print(name, path)


if __name__ == "__main__":
    main()

