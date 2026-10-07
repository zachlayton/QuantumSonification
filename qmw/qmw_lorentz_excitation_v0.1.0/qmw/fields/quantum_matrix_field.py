"""Validated 16 x 16 complex matrix field and spatial sampling helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


FIELD_SHAPE = (16, 16)


def _positive_pair(value: ArrayLike, *, name: str) -> tuple[float, float]:
    pair = np.asarray(value, dtype=float)
    if pair.shape != (2,) or not np.all(np.isfinite(pair)):
        raise ValueError(f"{name} must contain exactly two finite values")
    if np.any(pair <= 0.0):
        raise ValueError(f"{name} values must be positive")
    return float(pair[0]), float(pair[1])


def _finite_pair(value: ArrayLike, *, name: str) -> tuple[float, float]:
    pair = np.asarray(value, dtype=float)
    if pair.shape != (2,) or not np.all(np.isfinite(pair)):
        raise ValueError(f"{name} must contain exactly two finite values")
    return float(pair[0]), float(pair[1])


@dataclass(frozen=True, slots=True)
class QuantumMatrixField:
    """A complex QMW matrix interpreted as a sampled two-dimensional field.

    ``values[y, x]`` follows NumPy's row-major convention. ``origin`` and
    ``spacing`` are ordered as ``(x, y)``.
    """

    values: NDArray[np.complexfloating]
    spacing: tuple[float, float] = (1.0, 1.0)
    origin: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self) -> None:
        raw = np.asarray(self.values)
        if raw.shape != FIELD_SHAPE:
            raise ValueError(
                f"matrix field must have shape {FIELD_SHAPE}, got {raw.shape}"
            )
        if not np.iscomplexobj(raw):
            raise TypeError("matrix field values must use a complex dtype")
        values = np.asarray(raw, dtype=np.complex128)
        if not np.all(np.isfinite(values.real)) or not np.all(
            np.isfinite(values.imag)
        ):
            raise ValueError("matrix field values must be finite")

        object.__setattr__(self, "values", values.copy())
        object.__setattr__(
            self, "spacing", _positive_pair(self.spacing, name="spacing")
        )
        object.__setattr__(self, "origin", _finite_pair(self.origin, name="origin"))

    @property
    def magnitude(self) -> NDArray[np.float64]:
        """Return the complex magnitude without exposing mutable state."""

        return np.abs(self.values)

    @property
    def phase(self) -> NDArray[np.float64]:
        """Return wrapped phase in radians in the interval [-pi, pi]."""

        return np.angle(self.values)

    @property
    def bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Physical ``((x_min, x_max), (y_min, y_max))`` bounds."""

        dx, dy = self.spacing
        ox, oy = self.origin
        return ((ox, ox + (FIELD_SHAPE[1] - 1) * dx), (oy, oy + (FIELD_SHAPE[0] - 1) * dy))

    def grid_indices(
        self, position: ArrayLike, *, clip: bool = True
    ) -> tuple[float, float, bool]:
        """Convert a physical position to fractional ``(x_index, y_index)``.

        Returns the indices and whether the original point was inside bounds.
        """

        point = np.asarray(position, dtype=float)
        if point.shape not in {(2,), (3,)} or not np.all(np.isfinite(point)):
            raise ValueError("position must contain two or three finite values")
        ox, oy = self.origin
        dx, dy = self.spacing
        x_index = (float(point[0]) - ox) / dx
        y_index = (float(point[1]) - oy) / dy
        in_bounds = 0.0 <= x_index <= 15.0 and 0.0 <= y_index <= 15.0
        if not in_bounds and not clip:
            raise ValueError("position lies outside the matrix field")
        if clip:
            x_index = float(np.clip(x_index, 0.0, 15.0))
            y_index = float(np.clip(y_index, 0.0, 15.0))
        return x_index, y_index, in_bounds

    def clipped_position(self, position: ArrayLike) -> NDArray[np.float64]:
        """Return the sampled physical position as a three-component vector."""

        x_index, y_index, _ = self.grid_indices(position, clip=True)
        ox, oy = self.origin
        dx, dy = self.spacing
        point = np.asarray(position, dtype=float)
        z = float(point[2]) if point.shape == (3,) else 0.0
        return np.array([ox + x_index * dx, oy + y_index * dy, z], dtype=float)

    def sample(self, grid: ArrayLike, position: ArrayLike) -> NDArray[np.float64] | float:
        """Bilinearly sample a scalar or vector grid at ``position``.

        The first two grid dimensions must be 16 x 16. Any trailing dimension
        is preserved, so the same routine samples scalar and vector fields.
        Positions beyond the boundary are clamped to the nearest field point.
        """

        samples = np.asarray(grid)
        if samples.shape[:2] != FIELD_SHAPE:
            raise ValueError(
                f"sample grid must start with shape {FIELD_SHAPE}, got {samples.shape}"
            )
        x, y, _ = self.grid_indices(position, clip=True)
        x0, y0 = int(np.floor(x)), int(np.floor(y))
        x1, y1 = min(x0 + 1, 15), min(y0 + 1, 15)
        tx, ty = x - x0, y - y0

        top = (1.0 - tx) * samples[y0, x0] + tx * samples[y0, x1]
        bottom = (1.0 - tx) * samples[y1, x0] + tx * samples[y1, x1]
        result = (1.0 - ty) * top + ty * bottom
        if np.ndim(result) == 0:
            return float(result)
        return np.asarray(result, dtype=float)

