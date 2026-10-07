"""Authoritative dense NumPy/SciPy backend for two coupled bosonic modes."""

from __future__ import annotations

import numpy as np

from ..coupled_model import CoupledOscillatorModel, CoupledOscillatorSpec
from ..coupled_observables import coupled_frame_from_density
from ..coupled_schema import CoupledOscillatorFrame
from ..evolution import evolve_density
from ..states import density_matrix


class NumPyCoupledOscillatorBackend:
    def __init__(self, spec: CoupledOscillatorSpec | None = None) -> None:
        self.model = CoupledOscillatorModel.from_spec(spec)

    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
    ) -> CoupledOscillatorFrame:
        rho = density_matrix(state)
        if rho.shape != (
            self.model.spec.total_dimension,
            self.model.spec.total_dimension,
        ):
            raise ValueError("state dimension does not match coupled oscillator model")
        evolved = evolve_density(
            rho,
            self.model.operators.hamiltonian,
            time,
            hbar=self.model.spec.hbar,
        )
        return coupled_frame_from_density(
            evolved,
            self.model,
            time=time,
            backend="numpy_coupled_bosonic",
            backend_metadata={
                "authoritative": True,
                "representation": "tensor_product_truncated_fock_basis",
                "basis_order": "|n_a,n_b>",
                "flat_index": "n_a*dimension_b+n_b",
                "dimension_a": self.model.spec.dimension_a,
                "dimension_b": self.model.spec.dimension_b,
                "coupling": self.model.spec.coupling,
                "interaction": "hbar*g*(a_dagger*b+a*b_dagger)",
                "physical_qubit_oscillator_claim": False,
            },
            include_rho=include_rho,
        )


__all__ = ["NumPyCoupledOscillatorBackend"]
