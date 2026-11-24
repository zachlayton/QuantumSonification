"""Fine field -> R regions (default 16), via a projection matrix W (R x N).

    E_i = sum_n W_in E_n dx

The windows form a partition of unity (sum_i W_in = 1 for every n), so regional
totals always add up to the field totals. `overlap` > 0 gives raised-cosine
crossfades between neighbouring regions; 0 gives hard bins.

Regional inflows come from the divergence of the flux observables, so
d/dt P_i = probability_inflow_i holds exactly for the Schrödinger link currents.
"""
from __future__ import annotations

import numpy as np

from qmw.core.domain import Domain
from qmw.core.field_frame import ObservableData, RegionalData
from qmw.core.module_spec import ModuleSpec, PortSpec

SPEC = ModuleSpec(
    "region_projector", "Region projector",
    r"E_i = \int w_i(x)\,\mathcal{E}(x)\,dx,\qquad \sum_i w_i(x) = 1",
    (PortSpec("field observables", "densities on the fine grid"),),
    (PortSpec("regions", "regional probability, energy, inflows, centroids"),))


class RegionProjector:
    spec = SPEC

    def __init__(self, domain: Domain, regions: int = 16, overlap: float = 0.5,
                 x_min: float | None = None, x_max: float | None = None):
        domain.require_spatial("RegionProjector")
        self.domain, self.regions = domain, regions
        x = domain.coordinates
        lo = x[0] if x_min is None else x_min
        hi = x[-1] if x_max is None else x_max
        self.boundaries = np.linspace(lo, hi, regions + 1)
        half = 0.5 * overlap * (hi - lo) / regions

        def step(b):
            if half <= 0:
                return (x >= b).astype(float)
            t = np.clip((x - (b - half)) / (2 * half), 0, 1)
            return 0.5 - 0.5 * np.cos(np.pi * t)

        s = [np.ones_like(x)] + [step(b) for b in self.boundaries[1:-1]] + [np.zeros_like(x)]
        self.W = np.array([s[i] - s[i + 1] for i in range(regions)])
        self.centres = 0.5 * (self.boundaries[:-1] + self.boundaries[1:])

    def _div_links(self, links):
        dx = self.domain.dx
        return (links - np.roll(links, 1)) / dx if self.domain.boundary == "periodic" else np.diff(links) / dx

    def project(self, obs: ObservableData, sink_density: np.ndarray | None = None) -> RegionalData:
        dx, W, x = self.domain.dx, self.W, self.domain.coordinates
        P = W @ (obs.probability_density * dx)
        inflow_p = None
        if obs.probability_current_edges is not None:
            dp = -self._div_links(obs.probability_current_edges)
            if sink_density is not None:
                dp = dp - sink_density
            inflow_p = W @ (dp * dx)
        inflow_e = None
        if obs.energy_flux is not None:
            S = obs.energy_flux
            divS = ((np.roll(S, -1) - np.roll(S, 1)) / (2 * dx) if self.domain.boundary == "periodic"
                    else np.gradient(S, dx))
            inflow_e = -(W @ (divS * dx))
        wr = W @ (obs.probability_density * x * dx)
        cent = np.where(P > 1e-300, wr / np.maximum(P, 1e-300), self.centres)
        return RegionalData(
            probability=P,
            energy=W @ (obs.total_energy_density * dx),
            kinetic_energy=W @ (obs.kinetic_energy_density * dx),
            potential_energy=W @ (obs.potential_energy_density * dx),
            probability_inflow=inflow_p, energy_inflow=inflow_e, centroids=cent)
