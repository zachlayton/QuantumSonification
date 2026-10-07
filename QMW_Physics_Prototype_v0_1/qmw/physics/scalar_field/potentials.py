"""U(s) = m² s/2 - a s²/4 + b s³/6, s=|phi|²."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PolynomialPotential:
    mass_squared: float = 1.0
    attraction: float = 1.0
    repulsion: float = 1.0

    def __post_init__(self):
        if not np.isfinite([self.mass_squared, self.attraction, self.repulsion]).all():
            raise ValueError("Scalar potential coefficients must be finite")
        if self.mass_squared < 0 or self.attraction < 0 or self.repulsion < 0:
            raise ValueError("This scalar demo uses nonnegative m², attraction, and repulsion")
        if self.attraction > 0 and self.repulsion == 0:
            raise ValueError("Attractive quartic potential requires positive sextic stabilization")

    def energy_s(self, s: np.ndarray) -> np.ndarray:
        s = np.asarray(s)
        return .5*self.mass_squared*s - .25*self.attraction*s**2 + (self.repulsion/6)*s**3

    def energy(self, phi: np.ndarray) -> np.ndarray:
        return self.energy_s(np.abs(phi)**2)

    def derivative_s(self, s: np.ndarray) -> np.ndarray:
        s = np.asarray(s)
        return .5*self.mass_squared - .5*self.attraction*s + .5*self.repulsion*s**2

    def force(self, phi: np.ndarray) -> np.ndarray:
        return -2*self.derivative_s(np.abs(phi)**2)*phi

    def curvature_bound(self, phi: np.ndarray) -> float:
        """Conservative magnitude bound on both real-component force Jacobian eigenvalues.

        Tangential curvature: m²-a*s+b*s²; radial: m²-3a*s+5b*s².
        The absolute-sum bound deliberately errs toward a smaller accepted timestep.
        """
        maximum_s = float(np.max(np.abs(phi)**2))
        return self.mass_squared + 3*self.attraction*maximum_s + 5*self.repulsion*maximum_s**2
