#!/usr/bin/env python3
"""Render a rank-expanded, randomized-basis 64-position history clock."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from qmw_temporal_crystal16_v1 import FloquetIsingConfig, FloquetTimeCrystal16

from .history_state import prepare_floquet_history_state
from .randomized_clock_sonification import (
    RandomizedClockConfig,
    render_randomized_clock,
    write_randomized_clock,
)


BLOCH_POLAR_ANGLES = (0.37, 0.83, 1.21, 1.67)
BLOCH_AZIMUTH_ANGLES = (0.20, 1.10, 2.00, 2.70)


def tilted_product_state() -> np.ndarray:
    state = np.asarray([1.0 + 0.0j])
    for polar, azimuth in zip(BLOCH_POLAR_ANGLES, BLOCH_AZIMUTH_ANGLES):
        qubit = np.asarray([
            np.cos(0.5 * polar),
            np.exp(1j * azimuth) * np.sin(0.5 * polar),
        ])
        state = np.kron(state, qubit)
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("output/entangled_history_clock64_v1/randomized_clock"),
    )
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--duration", type=float, default=12.0)
    parser.add_argument("--seed", type=int, default=64021)
    args = parser.parse_args(argv)

    model = FloquetTimeCrystal16(FloquetIsingConfig(
        pulse_error=0.05,
        transverse_fields=(0.07, -0.11, 0.13, -0.17),
    ))
    history = prepare_floquet_history_state(
        model,
        tilted_product_state(),
        clock_qubits=6,
    )
    config = RandomizedClockConfig(
        sample_rate=int(args.sample_rate),
        duration_seconds=float(args.duration),
        seed=int(args.seed),
    )
    render = render_randomized_clock(history, config)
    paths = write_randomized_clock(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
