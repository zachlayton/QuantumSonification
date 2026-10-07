"""Numerical diagnostics for Hilbert-current observations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hilbert_current import continuity_residual, current_matrix, hermitian_matrix


@dataclass(frozen=True)
class HilbertDiagnostics:
    trace: float
    purity: float
    minimum_eigenvalue: float
    hermiticity_error: float
    current_antisymmetry_error: float
    continuity_linf: float


def diagnose_hilbert_transport(rho: object, hamiltonian: object, *, hbar: float = 1.0) -> HilbertDiagnostics:
    density = hermitian_matrix("rho", rho)
    generator = hermitian_matrix("hamiltonian", hamiltonian)
    if density.shape != generator.shape:
        raise ValueError("rho and hamiltonian must share a shape.")
    current = current_matrix(density, generator, hbar=hbar)
    residual = continuity_residual(density, generator, hbar=hbar)
    return HilbertDiagnostics(
        trace=float(np.trace(density).real),
        purity=float(np.trace(density @ density).real),
        minimum_eigenvalue=float(np.min(np.linalg.eigvalsh(density))),
        hermiticity_error=float(np.max(np.abs(density - density.conj().T))),
        current_antisymmetry_error=float(np.max(np.abs(current + current.T))),
        continuity_linf=float(np.max(np.abs(residual))),
    )


__all__ = ["HilbertDiagnostics", "diagnose_hilbert_transport"]
