"""Immutable polarization frame shared by viewers, OSC, and sonifiers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .jones import JonesState
from .poincare import PoincareState
from .polarization_density_matrix import PolarizationDensityMatrix
from .stokes import StokesParameters


def _readonly_vector(value: np.ndarray) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64).copy()
    if result.shape != (3,) or not np.all(np.isfinite(result)):
        raise ValueError("field vectors must be finite three-component arrays")
    result.setflags(write=False)
    return result


@dataclass(frozen=True, slots=True)
class PolarizationFrame:
    """One authoritative state snapshot; downstream layers do no physics."""

    time: float
    z: float
    carrier_phase: float
    electric_field: np.ndarray
    magnetic_field: np.ndarray
    jones: JonesState
    stokes: StokesParameters
    poincare: PoincareState
    density: PolarizationDensityMatrix

    def __post_init__(self) -> None:
        object.__setattr__(self, "electric_field", _readonly_vector(self.electric_field))
        object.__setattr__(self, "magnetic_field", _readonly_vector(self.magnetic_field))

    @property
    def relative_phase(self) -> float:
        return self.jones.relative_phase

    @property
    def energy_proxy(self) -> float:
        """Jones intensity; absolute SI energy needs the chosen field units."""

        return self.jones.intensity


__all__ = ["PolarizationFrame"]
