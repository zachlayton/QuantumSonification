#!/usr/bin/env python3
"""Render the first deterministic GHZ -> GRW -> resonator experiment."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from density.grw_ghz_sonification_experiment_v1 import render_ghz_experiment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/grw_ghz_sonification_v1.wav"))
    parser.add_argument("--qubit", type=int, choices=range(4), default=2)
    parser.add_argument("--outcome", type=int, choices=(0, 1), default=0)
    parser.add_argument("--strength", type=float, default=0.94)
    args = parser.parse_args()
    path, frame = render_ghz_experiment(
        args.output,
        qubit=args.qubit,
        outcome=args.outcome,
        strength=args.strength,
    )
    print(f"Rendered: {path}")
    print(
        "GRW event: "
        f"branch={frame.branch}, "
        f"excitation={frame.excitation_amplitude:.4f}, "
        f"bandwidth={frame.bandwidth:.3f}, "
        f"grains={frame.grain_structure:.3f}, "
        f"orientation={frame.orientation}, "
        f"Pauli={frame.dominant_pauli}"
    )


if __name__ == "__main__":
    main()
