"""Explicit domain metadata for QMW arrays.

A 2048-sample array can be psi(x), psi(t), a spectrum, or graph vertices. Those
are not interchangeable, so every field carries a Domain and operations that
only make sense in space (gradients, fluxes) check it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

DomainKind = Literal["space_1d", "space_2d", "space_3d", "graph", "time_history", "mode_index", "spectrum"]
Boundary = Literal["dirichlet", "periodic"]
SPATIAL_KINDS = ("space_1d", "space_2d", "space_3d")


@dataclass(frozen=True)
class Domain:
    kind: DomainKind
    shape: tuple[int, ...]
    coordinates: np.ndarray | None = None
    spacing: tuple[float, ...] | None = None
    boundary: Boundary | None = None
    units: str = ""

    @property
    def is_spatial(self) -> bool:
        return self.kind in SPATIAL_KINDS

    def require_spatial(self, operation: str) -> None:
        if not self.is_spatial:
            raise TypeError(f"{operation} needs a spatial domain, not {self.kind!r}")

    @classmethod
    def line(cls, n: int, x_min: float, x_max: float, boundary: Boundary = "dirichlet") -> "Domain":
        """Uniform 1-D grid. Dirichlet grids exclude the two wall points (psi = 0 there);
        periodic grids exclude the duplicate end point."""
        if boundary == "dirichlet":
            dx = (x_max - x_min) / (n + 1)
            x = x_min + dx * np.arange(1, n + 1)
        elif boundary == "periodic":
            dx = (x_max - x_min) / n
            x = x_min + dx * np.arange(n)
        else:
            raise ValueError(f"unknown boundary {boundary!r}")
        x.setflags(write=False)
        return cls("space_1d", (n,), x, (dx,), boundary)

    @property
    def dx(self) -> float:
        self.require_spatial("dx")
        assert self.spacing is not None
        return self.spacing[0]
