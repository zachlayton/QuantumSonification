"""Uniform periodic two-dimensional grid and shared sampling convention."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class Grid2D:
    x: RealArray
    y: RealArray
    dx: float
    dy: float
    boundary: str = "periodic"

    def __post_init__(self) -> None:
        x = np.asarray(self.x, dtype=np.float64).copy()
        y = np.asarray(self.y, dtype=np.float64).copy()
        if x.ndim != 1 or y.ndim != 1 or x.size < 4 or y.size < 4:
            raise ValueError("x and y must be one-dimensional with at least four points")
        if self.boundary != "periodic":
            raise ValueError("the v1 solvers currently require periodic boundaries")
        if self.dx <= 0.0 or self.dy <= 0.0:
            raise ValueError("dx and dy must be positive")
        x.setflags(write=False)
        y.setflags(write=False)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    @classmethod
    def periodic(
        cls,
        shape: tuple[int, int] = (32, 32),
        extent: tuple[float, float, float, float] = (-1.0, 1.0, -1.0, 1.0),
    ) -> "Grid2D":
        ny, nx = shape
        xmin, xmax, ymin, ymax = extent
        if xmax <= xmin or ymax <= ymin:
            raise ValueError("extent maxima must exceed minima")
        x = np.linspace(xmin, xmax, nx, endpoint=False, dtype=np.float64)
        y = np.linspace(ymin, ymax, ny, endpoint=False, dtype=np.float64)
        return cls(x=x, y=y, dx=(xmax - xmin) / nx, dy=(ymax - ymin) / ny)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.y.size, self.x.size)

    @property
    def cell_area(self) -> float:
        return self.dx * self.dy

    @property
    def extent(self) -> tuple[float, float, float, float]:
        return (self.x[0], self.x[0] + self.x.size * self.dx,
                self.y[0], self.y[0] + self.y.size * self.dy)

    def mesh(self) -> tuple[RealArray, RealArray]:
        return np.meshgrid(self.x, self.y, indexing="xy")

    def fractional_index(self, position: RealArray) -> tuple[float, float]:
        """Map physical ``[x, y]`` to wrapped fractional array indices."""
        value = np.asarray(position, dtype=np.float64)
        if value.shape != (2,):
            raise ValueError("position must have shape (2,)")
        ix = ((value[0] - self.x[0]) / self.dx) % self.x.size
        iy = ((value[1] - self.y[0]) / self.dy) % self.y.size
        return float(ix), float(iy)

    def sample(self, field: RealArray, position: RealArray) -> np.ndarray:
        """Periodic bilinear sampling; leading component axes are preserved."""
        values = np.asarray(field, dtype=np.float64)
        if values.shape[-2:] != self.shape:
            raise ValueError(f"field must end in grid shape {self.shape}")
        ix, iy = self.fractional_index(position)
        x0, y0 = int(np.floor(ix)), int(np.floor(iy))
        x1, y1 = (x0 + 1) % self.x.size, (y0 + 1) % self.y.size
        tx, ty = ix - x0, iy - y0
        return (
            (1.0 - tx) * (1.0 - ty) * values[..., y0, x0]
            + tx * (1.0 - ty) * values[..., y0, x1]
            + (1.0 - tx) * ty * values[..., y1, x0]
            + tx * ty * values[..., y1, x1]
        )

    def wrap_position(self, position: RealArray) -> RealArray:
        xmin, xmax, ymin, ymax = self.extent
        value = np.asarray(position, dtype=np.float64).copy()
        value[0] = xmin + (value[0] - xmin) % (xmax - xmin)
        value[1] = ymin + (value[1] - ymin) % (ymax - ymin)
        return value
