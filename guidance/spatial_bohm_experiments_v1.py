"""Command-line validation experiments for the spatial Bohm engine."""

from __future__ import annotations

import argparse
import json

import numpy as np

from .schrodinger_pilot_1d_v2 import SchrodingerPilot1D
from .schrodinger_pilot_2d_v1 import SchrodingerPilot2D
from .schrodinger_pilot_3d_v1 import SchrodingerPilot3D
from .two_particle_pilot_1d_v1 import TwoParticlePilot1D


EXPERIMENTS = (
    "1d_gaussian",
    "2d_gaussian",
    "2d_vortex",
    "2d_oscillator",
    "2d_double_slit",
    "two_particle_nonlocal",
    "3d_gaussian",
    "3d_hydrogen_m1",
)


def run_experiment(name: str, *, steps: int = 50, dt: float = 0.01, seed: int = 23) -> dict:
    if steps < 0 or dt < 0.0:
        raise ValueError("steps and dt must be non-negative")
    if name == "1d_gaussian":
        pilot = SchrodingerPilot1D.free_gaussian(n_points=256)
        pilot.seed_trajectories(512, seed=seed)
        for _ in range(steps):
            pilot.step(dt)
        snapshot = pilot.snapshot()
        return {
            "experiment": name,
            "coordinate_semantics": pilot.coordinate_semantics,
            "time": snapshot.time,
            "norm": snapshot.norm,
            "expectation_x": snapshot.expectation_x,
            "uncertainty_x": snapshot.uncertainty_x,
            "trajectory_mean": float(np.mean(pilot.trajectory_positions)),
        }

    if name.startswith("2d_"):
        if name == "2d_gaussian":
            pilot = SchrodingerPilot2D.gaussian(grid_shape=96)
        elif name == "2d_vortex":
            pilot = SchrodingerPilot2D.vortex(grid_shape=96)
        elif name == "2d_oscillator":
            pilot = SchrodingerPilot2D.harmonic_ground(grid_shape=96)
        else:
            pilot = SchrodingerPilot2D.double_slit(
                emerging=True, grid_shape=(128, 96)
            )
        pilot.seed_trajectories(512, seed=seed)
        for _ in range(steps):
            pilot.step(dt)
        snapshot = pilot.snapshot()
        result = {
            "experiment": name,
            "coordinate_semantics": pilot.coordinate_semantics,
            "time": snapshot.time,
            "norm": snapshot.norm,
            "expectation_position": snapshot.expectation_position,
            "spread": snapshot.spread,
            "valid_fraction": snapshot.valid_fraction,
        }
        if name == "2d_vortex":
            result["phase_winding"] = pilot.phase_winding(2.0)
            result["circulation"] = pilot.circulation(2.0)
        return result

    if name == "two_particle_nonlocal":
        pilot = TwoParticlePilot1D.entangled(n_points=96)
        pilot.seed_configurations(512, seed=seed)
        response = pilot.nonlocal_response(
            fixed_x1=0.5, x2_values=np.array([-1.0, 0.0, 1.0])
        )
        for _ in range(steps):
            pilot.step(dt)
        snapshot = pilot.snapshot()
        return {
            "experiment": name,
            "coordinate_semantics": pilot.coordinate_semantics,
            "time": snapshot.time,
            "norm": snapshot.norm,
            "covariance": snapshot.covariance,
            "v1_at_x2_minus_zero_plus": response.tolist(),
        }

    if name == "3d_gaussian":
        pilot = SchrodingerPilot3D.gaussian(grid_shape=32)
    elif name == "3d_hydrogen_m1":
        pilot = SchrodingerPilot3D.hydrogenic(
            grid_shape=32, states=((2, 1, 1, 1.0 + 0.0j),)
        )
    else:
        raise ValueError(f"unknown experiment {name!r}")
    pilot.seed_trajectories(256, seed=seed)
    for _ in range(steps):
        pilot.step(dt)
    snapshot = pilot.snapshot()
    result = {
        "experiment": name,
        "coordinate_semantics": pilot.coordinate_semantics,
        "state_family": snapshot.state_family,
        "time": snapshot.time,
        "norm": snapshot.norm,
        "expectation_position": snapshot.expectation_position,
        "rms_radius": snapshot.rms_radius,
        "valid_fraction": snapshot.valid_fraction,
    }
    if name == "3d_hydrogen_m1":
        result["spherical_velocity_at_3_0_0"] = pilot.spherical_velocity_components(
            np.array([[3.0, 0.0, 0.0]])
        )[0].tolist()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=EXPERIMENTS)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()
    print(
        json.dumps(
            run_experiment(args.experiment, steps=args.steps, dt=args.dt, seed=args.seed),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

