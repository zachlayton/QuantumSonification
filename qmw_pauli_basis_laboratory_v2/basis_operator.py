"""Common representation interface for the QMW Pauli Basis Laboratory.

The canonical quantum material is a density matrix ``rho``.  A
``BasisOperator`` changes its coordinates according to the laboratory
convention

    rho' = U rho U†

It does not evolve or collapse the physical state.  The companion observable
methods make the passive-coordinate semantics explicit:

* ``transform_observable`` carries the same physical observable into the new
  coordinates.
* ``pullback_observable`` explains what a fixed observable in the new
  coordinates measures in the canonical coordinates.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


DEFAULT_TOLERANCE = 1e-10


def square_matrix(value: Any, *, name: str) -> np.ndarray:
    """Return ``value`` as a finite complex square matrix."""
    matrix = np.asarray(value, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if matrix.shape[0] == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} contains a non-finite value")
    return matrix


def validate_density_matrix(
    rho: Any,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> np.ndarray:
    """Validate and return a normalized, positive-semidefinite density matrix."""
    matrix = square_matrix(rho, name="rho")
    if not np.allclose(matrix, matrix.conj().T, atol=tolerance, rtol=0.0):
        raise ValueError("rho must be Hermitian")
    trace = complex(np.trace(matrix))
    if abs(trace.imag) > tolerance or not np.isclose(
        trace.real, 1.0, atol=tolerance, rtol=0.0
    ):
        raise ValueError("rho must have trace 1")
    minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(matrix)))
    if minimum_eigenvalue < -tolerance:
        raise ValueError("rho must be positive semidefinite")
    return matrix


def validate_unitary(
    unitary: Any,
    dimension: int,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> np.ndarray:
    """Validate a basis transform matrix for a requested Hilbert dimension."""
    matrix = square_matrix(unitary, name="basis unitary")
    if matrix.shape != (dimension, dimension):
        raise ValueError(
            "basis unitary has shape "
            f"{matrix.shape}; expected {(dimension, dimension)}"
        )
    identity = np.eye(dimension, dtype=complex)
    if not np.allclose(
        matrix @ matrix.conj().T,
        identity,
        atol=tolerance,
        rtol=0.0,
    ):
        raise ValueError("basis unitary must satisfy U U† = I")
    return matrix


class BasisOperator(ABC):
    """Abstract coordinate transform over density matrices and observables."""

    name: str
    description: str

    @abstractmethod
    def unitary(self, dimension: int) -> np.ndarray:
        """Return ``U`` for a Hilbert space of ``dimension``."""

    def checked_unitary(self, dimension: int) -> np.ndarray:
        return validate_unitary(self.unitary(dimension), dimension)

    def transform(self, rho: Any) -> np.ndarray:
        """Return the representation ``U rho U†``."""
        density = validate_density_matrix(rho)
        unitary = self.checked_unitary(density.shape[0])
        transformed = unitary @ density @ unitary.conj().T
        # Remove roundoff asymmetry while preserving the explicit convention.
        return (transformed + transformed.conj().T) / 2.0

    def transform_observable(self, observable: Any) -> np.ndarray:
        """Carry the same physical observable into the new coordinates."""
        matrix = square_matrix(observable, name="observable")
        unitary = self.checked_unitary(matrix.shape[0])
        return unitary @ matrix @ unitary.conj().T

    def pullback_observable(self, observable: Any) -> np.ndarray:
        """Express a fixed new-coordinate observable in canonical coordinates."""
        matrix = square_matrix(observable, name="observable")
        unitary = self.checked_unitary(matrix.shape[0])
        return unitary.conj().T @ matrix @ unitary

    def metadata(self, dimension: int) -> dict[str, Any]:
        """Return JSON-friendly identity data for menus, logs, and archives."""
        self.checked_unitary(dimension)
        return {
            "name": self.name,
            "description": self.description,
            "dimension": int(dimension),
            "convention": "rho_prime = U rho U_dagger",
        }
