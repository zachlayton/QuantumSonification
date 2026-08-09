#!/usr/bin/env python3
"""Inspect any v1 wavefunction source and optionally save a complete frame."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np

from excitation.wavefunction_sources_v1 import (
    WAVEFUNCTION_SOURCE_NAMES,
    create_wavefunction_source,
)


def source_parameters(name: str, grid: int | None) -> dict[str, int]:
    if grid is None:
        return {}
    if name == "spherical_harmonic":
        return {"n_theta": grid, "n_phi": 2 * grid}
    if name in ("particle_in_box", "quantum_rotor"):
        return {"n_points": grid}
    return {"grid_shape": grid}


def save_frame(path: Path, frame) -> None:
    payload = {
        "psi_real": frame.psi.real,
        "psi_imag": frame.psi.imag,
        "probability": frame.probability,
        "phase": frame.phase,
        "energy_density": frame.energy_density,
        "time": np.asarray(frame.time),
        "norm": np.asarray(frame.norm),
        "descriptor_json": np.asarray(json.dumps(asdict(frame.descriptor))),
        "metadata_json": np.asarray(json.dumps(dict(frame.metadata), default=str)),
    }
    for index, coordinate in enumerate(frame.coordinates):
        payload[f"coordinate_{index}"] = coordinate
    for index, current in enumerate(frame.probability_current):
        payload[f"current_{index}"] = current
    np.savez_compressed(path, **payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=WAVEFUNCTION_SOURCE_NAMES, default="schrodinger_packet_3d")
    parser.add_argument("--grid", type=int, help="Override grid size (one value per axis).")
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--output", type=Path, help="Optional compressed NPZ frame output.")
    args = parser.parse_args()

    source = create_wavefunction_source(args.source, **source_parameters(args.source, args.grid))
    frame = source.frame(0.0)
    for _ in range(args.steps):
        frame = source.frame(args.dt)

    print(f"source:     {frame.source}")
    print(f"dimension:  {frame.dimension}D")
    print(f"shape:      {frame.psi.shape}")
    print(f"time:       {frame.time:.6f}")
    print(f"norm:       {frame.norm:.12f}")
    print("descriptor:")
    print(json.dumps(asdict(frame.descriptor), indent=2))
    if args.output:
        save_frame(args.output, frame)
        print(f"saved:      {args.output}")


if __name__ == "__main__":
    main()
