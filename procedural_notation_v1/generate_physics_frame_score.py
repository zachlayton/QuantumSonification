"""Reproducible demo or export a captured PhysicsFrame's t/rho NPZ arrays."""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
from qmw.core.physics_frame import PhysicsFrame
from procedural_notation_v1.physics_frame_score import write_physics_frame_score


def example_frame() -> PhysicsFrame:
    """Analytic 2048-sample unitary trajectory, explicitly a simulation fixture."""
    t = np.linspace(0, 6, 2048)
    energies = np.linspace(-1, 1, 16)
    psi = np.exp(-1j * t[:, None] * energies[None, :]) / 4
    rho = np.einsum("ti,tj->tij", psi, psi.conj())
    return PhysicsFrame(t=t, psi=psi, rho=rho,
                        metadata={"source": "analytic diagonal Hamiltonian demo; hbar=1"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="NPZ with t and rho; omitted uses analytic demo")
    parser.add_argument("--output", type=Path, default=Path("physics_frame_canon.musicxml"))
    parser.add_argument("--snapshots", type=int, default=4)
    parser.add_argument("--indices", type=int, nargs="+")
    parser.add_argument("--ticks-per-time-unit", type=float)
    parser.add_argument("--quantization-ticks", type=int, default=1)
    args = parser.parse_args()
    if args.input:
        with np.load(args.input, allow_pickle=False) as data:
            frame = PhysicsFrame(t=data["t"], rho=data["rho"])
    else:
        frame = example_frame()
    print(write_physics_frame_score(
        frame, args.output, snapshot_count=args.snapshots, sample_indices=args.indices,
        ticks_per_time_unit=args.ticks_per_time_unit, quantization_ticks=args.quantization_ticks,
    ))


if __name__ == "__main__":
    main()
