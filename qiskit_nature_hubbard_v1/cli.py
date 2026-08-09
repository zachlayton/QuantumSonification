"""Command-line descriptor generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mapping import musical_descriptor
from .model import HubbardConfig, analyze_hubbard


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a validated Fermi-Hubbard descriptor")
    parser.add_argument("--sites", type=int, default=2)
    parser.add_argument("--particles", type=int, default=2)
    parser.add_argument("--hopping", type=float, default=1.0)
    parser.add_argument("--interaction", type=float, default=4.0)
    parser.add_argument("--potential", type=float, default=0.0)
    parser.add_argument("--states", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = HubbardConfig(
        num_sites=args.sites,
        particles=args.particles,
        hopping=args.hopping,
        onsite_interaction=args.interaction,
        onsite_potential=args.potential,
        num_eigenstates=args.states,
    )
    descriptor = musical_descriptor(analyze_hubbard(config))
    text = json.dumps(descriptor, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()

