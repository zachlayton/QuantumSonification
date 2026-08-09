#!/usr/bin/env python3
"""Render the paper-faithful 64-position Schmidt-mode rhythm."""

from __future__ import annotations

import argparse
from pathlib import Path

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .history_state import prepare_floquet_history_state
from .schmidt_sonification import (
    SchmidtRhythmConfig,
    render_schmidt_rhythm,
    write_schmidt_rhythm,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("output/entangled_history_clock64_v1/schmidt_rhythm"),
    )
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--interval-ms", type=float, default=62.0)
    parser.add_argument("--interval-ms-end", type=float, default=43.0)
    args = parser.parse_args(argv)

    history = prepare_floquet_history_state(
        FloquetTimeCrystal16(),
        computational_basis_state(0),
        clock_qubits=6,
    )
    config = SchmidtRhythmConfig(
        sample_rate=int(args.sample_rate),
        duration_seconds=float(args.duration),
        clock_interval_ms_start=float(args.interval_ms),
        clock_interval_ms_end=float(args.interval_ms_end),
    )
    render = render_schmidt_rhythm(history, config)
    paths = write_schmidt_rhythm(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
