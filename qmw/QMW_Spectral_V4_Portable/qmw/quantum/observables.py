"""Read-only observables derived from authoritative quantum state."""

from __future__ import annotations

import math

import numpy as np

from .hilbert_current import hermitian_matrix
from .pauli_basis import pauli_basis


def pauli_expectation(rho: object, operator: object, *, tolerance: float = 1.0e-9) -> float:
    density = hermitian_matrix("rho", rho, tolerance=tolerance)
    observable = hermitian_matrix("operator", operator, tolerance=tolerance)
    if density.shape != observable.shape:
        raise ValueError("rho and operator must share a shape.")
    result = complex(np.trace(density @ observable))
    if abs(result.imag) > tolerance:
        raise ValueError("Hermitian expectation was unexpectedly complex.")
    return float(result.real)


def observable_derivative(rho: object, hamiltonian: object, observable: object, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> float:
    if not math.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive.")
    density = hermitian_matrix("rho", rho, tolerance=tolerance)
    generator = hermitian_matrix("hamiltonian", hamiltonian, tolerance=tolerance)
    operator = hermitian_matrix("observable", observable, tolerance=tolerance)
    if density.shape != generator.shape or density.shape != operator.shape:
        raise ValueError("rho, hamiltonian, and observable must share a shape.")
    result = complex((1j / hbar) * np.trace(density @ (generator @ operator - operator @ generator)))
    if abs(result.imag) > tolerance:
        raise ValueError("observable derivative was unexpectedly complex.")
    return float(result.real)


def pauli_expectations(rho: object, *, include_identity: bool = False, tolerance: float = 1.0e-9) -> dict[str, float]:
    density = hermitian_matrix("rho", rho, tolerance=tolerance)
    dimension = density.shape[0]
    if dimension & (dimension - 1):
        raise ValueError("rho dimension must be a power of two.")
    return {
        label: pauli_expectation(density, operator, tolerance=tolerance)
        for label, operator in pauli_basis(dimension.bit_length() - 1, include_identity=include_identity)
    }


__all__ = ["observable_derivative", "pauli_expectation", "pauli_expectations"]
