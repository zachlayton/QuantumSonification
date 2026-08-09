"""Command-line H2 sweep generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .h2_sweep import H2SweepConfig, run_h2_sweep


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an exact Qiskit Nature H2 sweep")
    parser.add_argument("--distances", type=float, nargs="+", default=[0.5, 0.735, 1.0, 1.5, 2.0])
    parser.add_argument("--basis", default="sto3g")
    parser.add_argument("--states", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    descriptor = run_h2_sweep(
        H2SweepConfig(tuple(args.distances), basis=args.basis, num_eigenstates=args.states)
    )
    text = json.dumps(descriptor, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()

