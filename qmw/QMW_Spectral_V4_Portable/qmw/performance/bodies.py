"""Explicit native payloads for the non-scalar performance inspector bodies.

These small value objects make the payload contract checkable without changing
the source that supplied it.  In particular, a density matrix is never
silently converted into I/Q: a mixed density state has no unique wavefunction
or global phase.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


_FOUR_QUBIT_DIMENSION = 16


@dataclass(frozen=True)
class FourQubitDensityState:
    """One authoritative or measured 16 by 16 four-qubit density state."""

    rho: np.ndarray

    def __post_init__(self) -> None:
        matrix = np.asarray(self.rho, dtype=np.complex128)
        if matrix.shape != (_FOUR_QUBIT_DIMENSION, _FOUR_QUBIT_DIMENSION):
            raise ValueError("four-qubit DensityState requires a 16x16 rho.")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("four-qubit DensityState rho must be finite.")
        if not np.allclose(matrix, matrix.conj().T, atol=1.0e-9, rtol=0.0):
            raise ValueError("four-qubit DensityState rho must be Hermitian.")
        trace = complex(np.trace(matrix))
        if abs(trace.imag) > 1.0e-9 or not math.isclose(trace.real, 1.0, abs_tol=1.0e-8):
            raise ValueError("four-qubit DensityState rho must have unit trace.")
        if float(np.min(np.linalg.eigvalsh(matrix))) < -1.0e-9:
            raise ValueError("four-qubit DensityState rho must be positive semidefinite.")
        object.__setattr__(self, "rho", np.array(matrix, copy=True))

    @property
    def populations(self) -> np.ndarray:
        return np.array(np.real(np.diag(self.rho)), copy=True)

    @property
    def purity(self) -> float:
        return float(np.real(np.trace(self.rho @ self.rho)))

    @property
    def coherence_l1(self) -> float:
        """Basis-dependent off-diagonal L1 coherence, explicitly labeled as such."""

        return float(np.sum(np.abs(self.rho)) - np.sum(np.abs(np.diag(self.rho))))


@dataclass(frozen=True)
class HilbertIQFrame:
    """Explicit computational-basis I/Q observation, not a density projection."""

    in_phase: np.ndarray
    quadrature: np.ndarray

    def __post_init__(self) -> None:
        in_phase = np.asarray(self.in_phase, dtype=float)
        quadrature = np.asarray(self.quadrature, dtype=float)
        expected = (_FOUR_QUBIT_DIMENSION,)
        if in_phase.shape != expected or quadrature.shape != expected:
            raise ValueError("Hilbert I/Q requires sixteen in-phase and quadrature values.")
        if not np.all(np.isfinite(in_phase)) or not np.all(np.isfinite(quadrature)):
            raise ValueError("Hilbert I/Q values must be finite.")
        object.__setattr__(self, "in_phase", np.array(in_phase, copy=True))
        object.__setattr__(self, "quadrature", np.array(quadrature, copy=True))

    @property
    def magnitude(self) -> np.ndarray:
        return np.hypot(self.in_phase, self.quadrature)

    @property
    def phase(self) -> np.ndarray:
        return np.arctan2(self.quadrature, self.in_phase)


__all__ = ["FourQubitDensityState", "HilbertIQFrame"]
