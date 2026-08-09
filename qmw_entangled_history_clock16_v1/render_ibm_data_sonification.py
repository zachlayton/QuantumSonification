#!/usr/bin/env python3
"""Render the archived IBM 64-position history-clock shot records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .diagnostics import analyze_history
from .history_state import prepare_floquet_history_state
from .ibm_data_sonification import (
    IBMDataSonificationConfig,
    render_ibm_data,
    write_ibm_data_sonification,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args(argv)

    archive = json.loads(args.archive.read_text())
    history = prepare_floquet_history_state(
        FloquetTimeCrystal16(),
        computational_basis_state(0),
        clock_qubits=6,
    )
    ideal_fourier = analyze_history(history).clock_fourier_probabilities
    config = IBMDataSonificationConfig()
    render = render_ibm_data(
        archive["shot_sequences"],
        ideal_fourier,
        config,
    )
    paths = write_ibm_data_sonification(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
