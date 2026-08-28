"""Density-matrix invariants: Tr(rho)=1, rho hermitian, rho positive semidefinite.

These are hard regression checks (see the spine spec's amendment #27), not
optional diagnostics -- a QuantumFrame that fails them must not be sealed.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class StateInvariantError(ValueError):
    """rho violated a required density-matrix invariant."""


@dataclass(frozen=True)
class StateDiagnostics:
    trace: float
    hermiticity_error: float
    min_eigenvalue: float
    purity: float

    @property
    def is_hermitian(self) -> bool:
        return self.hermiticity_error < 1e-8

    @property
    def is_positive_semidefinite(self) -> bool:
        return self.min_eigenvalue > -1e-8

    @property
    def is_valid(self) -> bool:
        return (
            abs(self.trace - 1.0) < 1e-6
            and self.is_hermitian
            and self.is_positive_semidefinite
        )


def diagnose(rho: np.ndarray) -> StateDiagnostics:
    trace = float(np.trace(rho).real)
    hermiticity_error = float(np.max(np.abs(rho - rho.conj().T)))
    eigenvalues = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    min_eigenvalue = float(eigenvalues.min())
    purity = float(np.trace(rho @ rho).real)
    return StateDiagnostics(trace, hermiticity_error, min_eigenvalue, purity)


def validate_density_matrix(rho: np.ndarray) -> StateDiagnostics:
    diagnostics = diagnose(rho)
    if not diagnostics.is_valid:
        raise StateInvariantError(
            "rho failed density-matrix invariants: "
            f"trace={diagnostics.trace:.6f}, "
            f"hermiticity_error={diagnostics.hermiticity_error:.2e}, "
            f"min_eigenvalue={diagnostics.min_eigenvalue:.2e}"
        )
    return diagnostics


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


def von_neumann_entropy(rho: np.ndarray, eps: float = 1e-12) -> float:
    """S(rho) = -Tr(rho log rho), computed from the eigenvalues; log base 2."""
    eigenvalues = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    eigenvalues = np.clip(eigenvalues.real, eps, None)
    return float(-np.sum(eigenvalues * np.log2(eigenvalues)))
