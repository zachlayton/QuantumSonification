#!/usr/bin/env python3
"""Render the granular entangled-history proof of concept."""

from __future__ import annotations

import argparse
from pathlib import Path

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .granular_sonification import (
    GranularHistoryConfig,
    render_granular_history,
    write_granular_history,
)
from .history_state import prepare_floquet_history_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("output/entangled_history_clock16_v1/step5_granular"),
    )
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--rhythm-word", default="10101")
    parser.add_argument("--interval-ms", type=float, default=140.0)
    parser.add_argument("--interval-ms-end", type=float, default=110.0)
    args = parser.parse_args(argv)

    history = prepare_floquet_history_state(
        FloquetTimeCrystal16(),
        computational_basis_state(0),
    )
    config = GranularHistoryConfig(
        sample_rate=int(args.sample_rate),
        duration_seconds=float(args.duration),
        rhythm_word=str(args.rhythm_word),
        clock_interval_ms_start=float(args.interval_ms),
        clock_interval_ms_end=float(args.interval_ms_end),
        seed=int(args.seed),
    )
    render = render_granular_history(history, config)
    paths = write_granular_history(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
