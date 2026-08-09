#!/usr/bin/env python3
"""Write the sixteen-clock Ligeti-form score as MIDI and MusicXML."""

from __future__ import annotations

import argparse
from pathlib import Path

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .history_state import prepare_floquet_history_state
from .ligeti_history_export import (
    LigetiClockConfig,
    build_ligeti_clock_score,
    write_ligeti_clock_score,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("output/entangled_history_clock16_v1/step5_ligeti_export"),
    )
    parser.add_argument("--rhythm-word", default="10101")
    parser.add_argument("--interval-ms", type=float, default=150.0)
    parser.add_argument("--hit-budget", type=int, default=48)
    args = parser.parse_args(argv)

    history = prepare_floquet_history_state(
        FloquetTimeCrystal16(),
        computational_basis_state(0),
    )
    config = LigetiClockConfig(
        rhythm_word=str(args.rhythm_word),
        reference_interval_ms=float(args.interval_ms),
        hit_budget=int(args.hit_budget),
    )
    score = build_ligeti_clock_score(history, config)
    paths = write_ligeti_clock_score(score, args.output_directory)
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
