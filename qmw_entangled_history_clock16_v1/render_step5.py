#!/usr/bin/env python3
"""Render the default Floquet entangled-history proof-of-concept WAV files."""

from __future__ import annotations

import argparse
from pathlib import Path

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .history_state import prepare_floquet_history_state
from .sonification import (
    HistorySonificationConfig,
    render_history_audio,
    write_history_audio,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("output/entangled_history_clock16_v1/step5"),
    )
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--step-duration", type=float, default=0.5)
    parser.add_argument("--initial-basis", type=int, default=0)
    args = parser.parse_args(argv)

    model = FloquetTimeCrystal16()
    initial = computational_basis_state(int(args.initial_basis))
    history = prepare_floquet_history_state(model, initial)
    config = HistorySonificationConfig(
        sample_rate=int(args.sample_rate),
        step_duration_seconds=float(args.step_duration),
    )
    render = render_history_audio(history, config)
    paths = write_history_audio(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
