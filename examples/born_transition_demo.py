from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from excitation.born_transition import BornTransitionEngine, HYDROGENIC_SPECIES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print lifetime-timed events from the Born transition engine."
    )
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--dt", type=float, default=0.25)
    parser.add_argument(
        "--species",
        choices=tuple(HYDROGENIC_SPECIES),
        default="H-1",
    )
    parser.add_argument(
        "--stochastic",
        action="store_true",
        help="Draw each new transition from its population-weighted probability.",
    )
    parser.add_argument(
        "--mapping",
        choices=("global_ratio", "octave_fold"),
        default="global_ratio",
        help="Use ratio-preserving global scaling or legacy octave folding.",
    )
    args = parser.parse_args()

    engine = BornTransitionEngine(
        species=args.species,
        selection_mode="stochastic" if args.stochastic else "sequential",
        frequency_mapping=args.mapping,
    )
    print(f"species: {args.species}; frequency mapping: {args.mapping}")
    print(
        "event  transition   photon THz  wavelength nm  audio Hz  "
        "probability  duration s  linewidth Hz"
    )
    for event in range(args.steps):
        state = engine.state
        print(
            f"{event:>5}  {state.initial_label:>4}->{state.final_label:<4}  "
            f"{state.photon_frequency_hz / 1.0e12:>10.3f}  "
            f"{state.wavelength_nm:>13.3f}  "
            f"{state.audio_frequency_hz:>8.3f}  "
            f"{state.event_probability:>11.6f}  "
            f"{state.sonic_duration_seconds:>10.3f}  "
            f"{state.sonic_linewidth_hz:>12.6f}"
        )
        engine.step(max(args.dt, state.sonic_duration_seconds))


if __name__ == "__main__":
    main()
