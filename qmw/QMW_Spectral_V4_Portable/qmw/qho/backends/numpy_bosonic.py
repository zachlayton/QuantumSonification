"""Scientifically authoritative dense NumPy/SciPy backend."""

from __future__ import annotations

import numpy as np

from ..evolution import (
    LindbladEnvironment,
    evolve_density,
    evolve_lindblad,
    oscillator_collapse_operators,
)
from ..model import OscillatorModel, OscillatorSpec
from ..observables import frame_from_density
from ..schema import OscillatorFrame
from ..states import density_matrix


class NumPyBosonicBackend:
    def __init__(self, spec: OscillatorSpec | None = None) -> None:
        self.model = OscillatorModel.from_spec(spec)

    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
        include_wigner: bool = False,
        environment: LindbladEnvironment | None = None,
    ) -> OscillatorFrame:
        rho = density_matrix(state)
        resolved_environment = environment or LindbladEnvironment()
        if resolved_environment.is_closed:
            evolved = evolve_density(
                rho,
                self.model.operators.hamiltonian,
                time,
                hbar=self.model.spec.hbar,
            )
            evolution_kind = "unitary"
        else:
            collapse = oscillator_collapse_operators(
                self.model.operators.annihilation,
                self.model.operators.number,
                resolved_environment,
            )
            evolved = evolve_lindblad(
                rho,
                self.model.operators.hamiltonian,
                time,
                collapse,
                hbar=self.model.spec.hbar,
            )
            evolution_kind = "lindblad_gksl"
        return frame_from_density(
            evolved,
            self.model,
            time=time,
            backend="numpy_bosonic",
            backend_metadata={
                "authoritative": True,
                "representation": "truncated_fock_basis",
                "dimension": self.model.spec.dimension,
                "evolution": evolution_kind,
                "environment": resolved_environment.to_dict(),
            },
            include_rho=include_rho,
            include_wigner=include_wigner,
        )


__all__ = ["NumPyBosonicBackend"]
