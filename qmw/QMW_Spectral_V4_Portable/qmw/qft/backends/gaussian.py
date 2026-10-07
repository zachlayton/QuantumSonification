"""Scalable exact-Gaussian backend for the free scalar field V3."""

from __future__ import annotations

from ..gaussian import GaussianFieldState, evolve_gaussian
from ..model import ScalarFieldModel, ScalarFieldSpec
from ..observables import frame_from_gaussian
from ..schema import ScalarFieldFrame


class GaussianScalarFieldBackend:
    def __init__(self, spec: ScalarFieldSpec | None = None) -> None:
        self.model = ScalarFieldModel.from_spec(spec)

    def run(self, state: GaussianFieldState, *, time: float = 0.0) -> ScalarFieldFrame:
        evolved = evolve_gaussian(state, self.model, time)
        return frame_from_gaussian(
            evolved,
            self.model,
            time=time,
            backend="gaussian_free_scalar",
            backend_metadata={
                "authoritative": True,
                "representation": "lattice_canonical_covariance",
                "phase_space_order": "phi[0:L],pi[0:L]",
                "boundary": self.model.spec.boundary,
                "sites": self.model.spec.sites,
                "lattice_spacing": self.model.spec.lattice_spacing,
                "physical_length": (
                    self.model.spec.sites * self.model.spec.lattice_spacing
                ),
                "interaction": "free_nearest_neighbor_klein_gordon",
                "physical_qubit_field_claim": False,
            },
        )


__all__ = ["GaussianScalarFieldBackend"]
