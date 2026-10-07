"""Reproducible command-line probe for the QMW scalar field V3."""

from __future__ import annotations

import argparse
import json

import numpy as np

from .backends.gaussian import GaussianScalarFieldBackend
from .gaussian import (
    coherent_mode_state,
    localized_displacement_state,
    squeezed_mode_state,
    thermal_state,
    vacuum_state,
)
from .model import ScalarFieldModel, ScalarFieldSpec


def main() -> None:
    parser = argparse.ArgumentParser(description="QMW V3 free scalar-field probe")
    parser.add_argument("--sites", type=int, default=8)
    parser.add_argument("--mass", type=float, default=0.6)
    parser.add_argument("--time", type=float, default=1.5)
    parser.add_argument(
        "--state",
        choices=("vacuum", "localized", "coherent", "squeezed", "thermal"),
        default="localized",
    )
    args = parser.parse_args()
    spec = ScalarFieldSpec(sites=args.sites, mass=args.mass)
    model = ScalarFieldModel.from_spec(spec)
    if args.state == "vacuum":
        state = vacuum_state(model)
    elif args.state == "localized":
        field = np.zeros(spec.sites)
        field[spec.sites // 2] = 1.0
        state = localized_displacement_state(model, mean_phi=field)
    elif args.state == "coherent":
        amplitudes = np.zeros(spec.sites, dtype=complex)
        amplitudes[0] = 0.8
        state = coherent_mode_state(model, amplitudes)
    elif args.state == "squeezed":
        squeezing = np.zeros(spec.sites, dtype=complex)
        squeezing[0] = 0.5
        state = squeezed_mode_state(model, squeezing)
    else:
        state = thermal_state(model, temperature=0.8)
    frame = GaussianScalarFieldBackend(spec).run(state, time=args.time)
    print(
        json.dumps(
            {
                "schema": "qmw.scalar_field_probe.v3",
                "state": args.state,
                "time": frame.time,
                "frequencies": frame.frequencies.tolist(),
                "mean_phi": frame.mean_phi.tolist(),
                "mean_pi": frame.mean_pi.tolist(),
                "mode_occupations": frame.mode_occupations.tolist(),
                "local_energy_density": frame.local_energy_density.tolist(),
                "mean_energy": frame.mean_energy,
                "purity": frame.purity,
                "backend": frame.backend,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
