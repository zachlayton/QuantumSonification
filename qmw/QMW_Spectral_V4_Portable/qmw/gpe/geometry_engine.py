"""Geometry-to-potential generation for periodic two-dimensional GPE fields.

This module turns declared spatial geometry into a real scalar potential
``V(x, y)``.  It neither evolves ``psi`` nor performs flow, event, OSC, or
sound work.  Its arrays are directly accepted by ``qmw.qmw_gpe.GPEEngine``.

Grid convention: a field has shape ``(len(x), len(y))`` and uses
``np.meshgrid(x, y, indexing='ij')``.  Obstacles remain ordinary finite
potential barriers; they are not boundary conditions or acoustic resonators.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np


Array = np.ndarray


def _axis(name: str, values: Any) -> Array:
    axis = np.asarray(values, dtype=float)
    if axis.ndim != 1 or axis.size < 2 or not np.all(np.isfinite(axis)) or np.any(np.diff(axis) <= 0.0):
        raise ValueError(f"{name} must be a finite, strictly increasing one-dimensional coordinate array.")
    return np.array(axis, copy=True)


def _finite(name: str, value: float, *, positive: bool = False, nonnegative: bool = False) -> float:
    value = float(value)
    valid = value > 0.0 if positive else (value >= 0.0 if nonnegative else True)
    if not math.isfinite(value) or not valid:
        qualifier = "finite"
        if positive:
            qualifier += " and greater than zero"
        elif nonnegative:
            qualifier += " and nonnegative"
        raise ValueError(f"{name} must be {qualifier}.")
    return value


@dataclass(frozen=True)
class GeometryPotential2D:
    """A spatial potential derived from declared geometry, not a field state."""

    x: Array
    y: Array
    potential: Array
    kind: str
    provenance: str = "geometry_derived_gpe_external_potential"


@dataclass(frozen=True)
class GeometryEigenbasis2D:
    """Geometry-aligned spatial eigenfunctions supplied to the modal layer.

    This records the basis and optional linear eigenvalues without claiming
    that an arbitrary potential has been solved here.  A geometry, spectral,
    or finite-element provider may create the modes; this engine verifies they
    are aligned to its spatial grid before GPE modal analysis uses them.
    """

    x: Array
    y: Array
    modes: Array
    eigenvalues: Array | None
    provenance: str = "geometry_aligned_gpe_eigenbasis"


class GeometryPotentialEngine2D:
    """Create and combine analytic or rasterized terrain potentials on one grid."""

    def __init__(self, x: Sequence[float] | Array, y: Sequence[float] | Array) -> None:
        self.x = _axis("x", x)
        self.y = _axis("y", y)
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing="ij")
        self.shape = self.X.shape

    def harmonic_bowl(
        self,
        omega: float,
        *,
        center: tuple[float, float] = (0.0, 0.0),
    ) -> GeometryPotential2D:
        """Return ``V = 1/2 omega^2 ((x-x0)^2 + (y-y0)^2)``."""

        frequency = _finite("omega", omega, nonnegative=True)
        x0, y0 = (_finite("center[0]", center[0]), _finite("center[1]", center[1]))
        potential = 0.5 * frequency**2 * ((self.X - x0) ** 2 + (self.Y - y0) ** 2)
        return self._frame(potential, "harmonic_bowl")

    def ring(
        self,
        alpha: float,
        radius: float,
        *,
        center: tuple[float, float] = (0.0, 0.0),
    ) -> GeometryPotential2D:
        """Return the radial ring terrain ``V = alpha (r-r0)^2``."""

        strength = _finite("alpha", alpha, nonnegative=True)
        target_radius = _finite("radius", radius, nonnegative=True)
        x0, y0 = (_finite("center[0]", center[0]), _finite("center[1]", center[1]))
        radial_distance = np.hypot(self.X - x0, self.Y - y0)
        return self._frame(strength * (radial_distance - target_radius) ** 2, "ring")

    def double_well_x(self, a: float, b: float) -> GeometryPotential2D:
        """Return an x-directed double well ``V = a (x^2-b^2)^2`` across y."""

        coefficient = _finite("a", a, nonnegative=True)
        separation = _finite("b", b, nonnegative=True)
        return self._frame(coefficient * (self.X**2 - separation**2) ** 2, "double_well_x")

    def obstacles(
        self,
        mask: Any,
        height: float,
        *,
        background: float = 0.0,
    ) -> GeometryPotential2D:
        """Rasterize a boolean/fractional obstacle mask as a finite barrier.

        A value of one receives ``background + height``; fractional masks
        interpolate linearly.  Finite barriers preserve the periodic solver's
        semantics and do not silently introduce hard-wall boundaries.
        """

        raster = np.asarray(mask, dtype=float)
        if raster.shape != self.shape or not np.all(np.isfinite(raster)) or np.any(raster < 0.0) or np.any(raster > 1.0):
            raise ValueError("mask must be finite, lie in [0, 1], and match the geometry grid.")
        barrier = _finite("height", height, nonnegative=True)
        base = _finite("background", background)
        return self._frame(base + barrier * raster, "rasterized_obstacles")

    def compose(self, *potentials: GeometryPotential2D | Array | float) -> GeometryPotential2D:
        """Add geometry-derived potential components on this engine's grid."""

        if not potentials:
            raise ValueError("compose requires at least one potential component.")
        result = np.zeros(self.shape, dtype=float)
        for component in potentials:
            values = component.potential if isinstance(component, GeometryPotential2D) else component
            array = np.asarray(values, dtype=float)
            if array.ndim == 0:
                array = np.full(self.shape, float(array), dtype=float)
            if array.shape != self.shape or not np.all(np.isfinite(array)):
                raise ValueError("each potential component must be finite and match the geometry grid.")
            result += array
        return self._frame(result, "composed_geometry")

    def bind_eigenbasis(
        self,
        modes: Any,
        *,
        eigenvalues: Any | None = None,
    ) -> GeometryEigenbasis2D:
        """Bind caller-supplied geometric eigenfunctions to this exact grid."""

        basis = np.asarray(modes, dtype=np.complex128)
        if basis.ndim != 3 or basis.shape[0] < 1 or basis.shape[1:] != self.shape or not np.all(np.isfinite(basis)):
            raise ValueError("modes must be finite with shape (mode_count, len(x), len(y)).")
        values: Array | None = None
        if eigenvalues is not None:
            values = np.asarray(eigenvalues, dtype=float)
            if values.shape != (basis.shape[0],) or not np.all(np.isfinite(values)):
                raise ValueError("eigenvalues must be finite with one value per mode.")
            values = np.array(values, copy=True)
        return GeometryEigenbasis2D(
            x=np.array(self.x, copy=True), y=np.array(self.y, copy=True),
            modes=np.array(basis, copy=True), eigenvalues=values,
        )

    def _frame(self, potential: Array, kind: str) -> GeometryPotential2D:
        return GeometryPotential2D(
            x=np.array(self.x, copy=True), y=np.array(self.y, copy=True),
            potential=np.array(potential, dtype=float, copy=True), kind=kind,
        )


__all__ = ["GeometryEigenbasis2D", "GeometryPotential2D", "GeometryPotentialEngine2D"]
