"""Read-only complex modal analysis of a GPE field in a geometric eigenbasis."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from .geometry_engine import GeometryEigenbasis2D
from ..gpe_observables import project_gpe_modes


Array = np.ndarray


@dataclass(frozen=True)
class ModalProjectorConfig:
    """Bounded modal-analysis configuration; 32 modes are provisioned by default."""

    provisioned_modes: int = 32
    orthonormal_tolerance: float = 1.0e-8

    def __post_init__(self) -> None:
        if int(self.provisioned_modes) != self.provisioned_modes or self.provisioned_modes < 1:
            raise ValueError("provisioned_modes must be a positive integer.")
        if not math.isfinite(float(self.orthonormal_tolerance)) or self.orthonormal_tolerance <= 0.0:
            raise ValueError("orthonormal_tolerance must be finite and greater than zero.")


@dataclass(frozen=True)
class GPEModalFrame:
    """Complex modal amplitudes of a field, with no acoustic interpretation."""

    time: float
    amplitudes: Array
    occupations: Array
    phases: Array
    eigenvalues: Array | None
    total_probability: float
    projected_probability: float
    unprojected_probability: float
    active_modes: int
    provisioned_modes: int
    provenance: str = "gpe_field_projection_into_geometry_eigenbasis"


class GPEModalProjector2D:
    """Project successive GPE fields into an ordered, geometry-aligned basis."""

    def __init__(
        self,
        eigenbasis: GeometryEigenbasis2D,
        config: ModalProjectorConfig | None = None,
    ) -> None:
        self.eigenbasis = eigenbasis
        self.config = config or ModalProjectorConfig()
        self._dx = self._uniform_spacing("x", eigenbasis.x)
        self._dy = self._uniform_spacing("y", eigenbasis.y)
        self.active_modes = min(int(self.config.provisioned_modes), eigenbasis.modes.shape[0])
        self.modes = np.array(eigenbasis.modes[: self.active_modes], copy=True)
        area = self._dx * self._dy
        gram = area * np.einsum("aij,bij->ab", np.conj(self.modes), self.modes)
        if not np.allclose(gram, np.eye(self.active_modes), atol=self.config.orthonormal_tolerance, rtol=self.config.orthonormal_tolerance):
            raise ValueError("geometry eigenmodes must be orthonormal on the declared periodic grid.")
        self.eigenvalues = (
            None if eigenbasis.eigenvalues is None
            else np.array(eigenbasis.eigenvalues[: self.active_modes], copy=True)
        )

    @staticmethod
    def _uniform_spacing(name: str, axis: Array) -> float:
        differences = np.diff(axis)
        if axis.ndim != 1 or axis.size < 2 or np.any(differences <= 0.0):
            raise ValueError(f"eigenbasis {name} coordinates must be strictly increasing.")
        spacing = float(differences[0])
        if not np.allclose(differences, spacing, rtol=1.0e-9, atol=1.0e-12):
            raise ValueError("modal projection requires uniform periodic coordinate axes.")
        return spacing

    def project(self, psi: Any, *, time: float) -> GPEModalFrame:
        """Calculate ``a_n = integral(conj(phi_n) psi)`` without changing ``psi``."""

        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite.")
        field = np.asarray(psi, dtype=np.complex128)
        if field.shape != self.modes.shape[1:] or not np.all(np.isfinite(field)):
            raise ValueError("psi must be finite and match the geometry eigenbasis grid.")
        projection = project_gpe_modes(field, self.modes, spacing=(self._dx, self._dy))
        total_probability = float(np.sum(np.abs(field) ** 2) * self._dx * self._dy)
        projected_probability = float(np.sum(projection.occupations))
        return GPEModalFrame(
            time=logical_time, amplitudes=projection.amplitudes,
            occupations=projection.occupations, phases=projection.phases,
            eigenvalues=None if self.eigenvalues is None else np.array(self.eigenvalues, copy=True),
            total_probability=total_probability, projected_probability=projected_probability,
            unprojected_probability=total_probability - projected_probability,
            active_modes=self.active_modes, provisioned_modes=int(self.config.provisioned_modes),
        )


__all__ = ["GPEModalFrame", "GPEModalProjector2D", "ModalProjectorConfig"]
