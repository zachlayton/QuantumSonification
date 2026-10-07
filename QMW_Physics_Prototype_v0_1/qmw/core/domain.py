from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import numpy as np


@dataclass(frozen=True)
class Domain:
    kind: Literal["space_1d", "basis_index", "time_history", "mode_index", "graph"]
    shape: tuple[int, ...]
    coordinates: np.ndarray | None = None
    spacing: tuple[float, ...] | None = None
    boundary: str = "none"
    coordinate_unit: str = "dimensionless"

    def __post_init__(self):
        if not self.shape or any(not isinstance(n, int) or n <= 0 for n in self.shape):
            raise ValueError("Domain shape must contain positive integers")
        if self.spacing is not None and (len(self.spacing) != len(self.shape) or
                not all(np.isfinite(d) and d > 0 for d in self.spacing)):
            raise ValueError("Spacing must be positive, finite and match dimensions")
        if self.kind == "space_1d":
            if len(self.shape) != 1 or self.spacing is None or self.coordinates is None:
                raise ValueError("1-D space requires coordinates and spacing")
            x = np.asarray(self.coordinates, dtype=float)
            if x.shape != self.shape or not np.isfinite(x).all():
                raise ValueError("Coordinates do not match domain")
            if x.size > 1 and not np.allclose(np.diff(x), self.spacing[0]):
                raise ValueError("This prototype requires a uniform spatial grid")
            x = x.copy(); x.setflags(write=False)
            object.__setattr__(self, "coordinates", x)

    @classmethod
    def periodic(cls, n: int = 2048, length: float = 64.0) -> "Domain":
        if isinstance(n, bool) or not isinstance(n, int) or n < 16:
            raise ValueError("Spatial resolution must be an integer >= 16")
        if not np.isfinite(length) or length <= 0:
            raise ValueError("Length must be finite and positive")
        dx = length / n
        return cls("space_1d", (n,), np.arange(n)*dx-length/2,
                   (dx,), "periodic", "scaled length")

    @classmethod
    def basis(cls, n: int) -> "Domain":
        return cls("basis_index", (n,))

    @property
    def size(self) -> int:
        return int(np.prod(self.shape))

    @property
    def weights(self) -> np.ndarray:
        return np.full(self.shape, float(np.prod(self.spacing)) if self.kind == "space_1d" else 1.0)

    @property
    def length(self) -> float:
        self.require_periodic_space()
        return self.shape[0] * self.spacing[0]

    def integrate(self, values: np.ndarray):
        a = np.asarray(values)
        if a.shape != self.shape:
            raise ValueError("Integrand shape does not match domain")
        return np.sum(self.weights * a)

    def require_periodic_space(self):
        if self.kind != "space_1d" or self.boundary != "periodic":
            raise ValueError("Spatial derivatives require a periodic spatial domain")
