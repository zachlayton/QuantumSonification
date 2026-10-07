"""A partition of the simulation domain, distinct from the musical voice count."""
import numpy as np
from qmw.core import Domain, PhysicsFrame, RegionalData
from qmw.core.operators import derivative
from ._validation import require_count, require_frame_domain, real_values, require_density_matrix


class RegionProjector:
    """Integrate observables over contiguous regions including quadrature.

    For periodic space, incoming flux is the integral of minus the *same*
    spectral divergence used by the observer. Basis-index bins aggregate
    populations; they never acquire an invented spatial current.
    """

    def __init__(self, domain: Domain, count: int = 16):
        if domain.kind not in ("space_1d", "basis_index"):
            raise ValueError("Region projection requires space_1d or basis_index")
        if domain.kind == "space_1d":
            domain.require_periodic_space()
        if len(domain.shape) != 1:
            raise ValueError("Region projection requires a one-dimensional sample array")
        require_count(count, domain.size)
        self.domain = domain
        self.count = count
        self.masks = np.zeros((count, domain.size), dtype=float)
        for index, points in enumerate(np.array_split(np.arange(domain.size), count)):
            self.masks[index, points] = 1.0
        self.masks.setflags(write=False)
        self._weighted_masks = self.masks * domain.weights[None, :]
        self._weighted_masks.setflags(write=False)
        coordinates = (domain.coordinates if domain.kind == "space_1d"
                       else np.arange(domain.size, dtype=float))
        self.centers = (self._weighted_masks @ coordinates) / self._weighted_masks.sum(axis=1)
        self.centers.setflags(write=False)
        self.projection_id = f"{domain.kind}-partition-{count}"

    def _integral(self, values, quantity: str):
        if values is None:
            return None
        return self._weighted_masks @ real_values(values, self.domain.shape, quantity)

    def _incoming_flux(self, values, quantity: str):
        if values is None or self.domain.kind != "space_1d":
            return None
        flux = real_values(values, self.domain.shape, quantity)
        return -(self._weighted_masks @ derivative(flux, self.domain))

    def project(self, frame: PhysicsFrame) -> RegionalData:
        require_frame_domain(frame, self.domain)
        obs = frame.observables
        probability = obs.probability_density
        if probability is None and frame.state.psi is not None:
            probability = np.abs(frame.state.psi) ** 2
        if probability is None and frame.state.rho is not None:
            if self.domain.kind != "basis_index":
                raise ValueError("Regional rho populations require a declared basis_index domain")
            rho = require_density_matrix(frame.state.rho, self.domain.size)
            probability = np.diag(rho).real
        return RegionalData(
            centers=self.centers.copy(),
            probability=self._integral(probability, "probability density/populations"),
            energy=self._integral(obs.total_energy_density, "energy density"),
            charge=self._integral(obs.charge_density, "charge density"),
            incoming_probability_flux=self._incoming_flux(obs.probability_current, "probability current"),
            incoming_energy_flux=self._incoming_flux(obs.energy_flux, "energy flux"),
            incoming_charge_flux=self._incoming_flux(obs.charge_current, "charge current"),
            projection_id=self.projection_id,
        )
