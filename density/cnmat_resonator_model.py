"""Translate a finite density operator into a CNMAT ``resonators~`` model.

CNMAT represents a resonant body as a flat sequence of
``frequency, gain, decay`` triples.  This module keeps the translation free of
OSC and Max concerns so the numerical contract can be tested independently.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CNMATDensityResonatorFrame:
    """One complete density-derived resonator model."""

    frequencies_hz: np.ndarray
    gains: np.ndarray
    decays_seconds: np.ndarray
    phases_radians: np.ndarray
    dimension: int

    @property
    def resonance_count(self) -> int:
        return self.dimension * self.dimension

    def triples(self) -> np.ndarray:
        """Return ``(frequency, gain, decay)`` rows in matrix row order."""
        return np.column_stack(
            (self.frequencies_hz, self.gains, self.decays_seconds)
        )

    def flat_triples(self) -> list[float]:
        """Return the flat list accepted by CNMAT ``resonators~``."""
        return self.triples().reshape(-1).astype(float).tolist()

    def triple_rows(self) -> list[list[float]]:
        """Split the model into one bounded OSC payload per matrix row."""
        return [
            row.reshape(-1).astype(float).tolist()
            for row in self.triples().reshape(self.dimension, self.dimension, 3)
        ]


def density_matrix_to_cnmat_resonators(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    *,
    minimum_frequency_hz: float = 30.0,
    maximum_frequency_hz: float = 8_000.0,
    diagonal_anchor_hz: float = 36.0,
    total_gain: float = 0.42,
    minimum_decay_seconds: float = 0.08,
    maximum_decay_seconds: float = 6.0,
) -> CNMATDensityResonatorFrame:
    """Build a quantum resonant body from ``rho`` and its Hamiltonian.

    ``rho`` is rotated into the Hamiltonian eigenbasis.  Each ordered matrix
    relation becomes one resonance: Hamiltonian energy difference controls
    frequency, relation magnitude controls gain, and stronger relations ring
    longer.  Diagonal relations have zero transition frequency, so they use a
    low chromatic anchor ladder instead of being collapsed to DC.
    """
    matrix = np.asarray(rho, dtype=np.complex128)
    operator = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("rho must be a square matrix")
    if operator.shape != matrix.shape:
        raise ValueError("hamiltonian must have the same shape as rho")
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(operator)):
        raise ValueError("rho and hamiltonian must contain only finite values")
    if minimum_frequency_hz <= 0 or maximum_frequency_hz <= minimum_frequency_hz:
        raise ValueError("frequency bounds must be positive and increasing")
    if diagonal_anchor_hz <= 0:
        raise ValueError("diagonal_anchor_hz must be positive")
    if total_gain < 0:
        raise ValueError("total_gain must be non-negative")
    if minimum_decay_seconds <= 0 or maximum_decay_seconds < minimum_decay_seconds:
        raise ValueError("decay bounds must be positive and increasing")

    # Numerical evolution can accumulate tiny anti-Hermitian residuals.
    matrix = 0.5 * (matrix + matrix.conj().T)
    operator = 0.5 * (operator + operator.conj().T)
    energies, energy_vectors = np.linalg.eigh(operator)
    energy_rho = energy_vectors.conj().T @ matrix @ energy_vectors

    dimension = matrix.shape[0]
    magnitudes = np.abs(energy_rho)
    phases = np.angle(energy_rho).reshape(-1)

    gaps = np.abs(energies[:, None] - energies[None, :])
    largest_gap = float(np.max(gaps))
    if largest_gap > 1.0e-12:
        frequencies = gaps * (maximum_frequency_hz / largest_gap)
        frequencies = np.clip(
            frequencies, minimum_frequency_hz, maximum_frequency_hz
        )
    else:
        frequencies = np.full_like(gaps, minimum_frequency_hz, dtype=np.float64)

    diagonal = np.arange(dimension)
    anchors = diagonal_anchor_hz * np.power(2.0, diagonal / 12.0)
    frequencies[diagonal, diagonal] = np.clip(
        anchors, minimum_frequency_hz, maximum_frequency_hz
    )

    # L2 normalization gives a bounded aggregate model without changing the
    # relative magnitude of density relations.
    magnitude_norm = float(np.linalg.norm(magnitudes.reshape(-1)))
    gains = (
        magnitudes * (total_gain / magnitude_norm)
        if magnitude_norm > 1.0e-15
        else np.zeros_like(magnitudes)
    )

    peak = float(np.max(magnitudes))
    relative = magnitudes / peak if peak > 1.0e-15 else np.zeros_like(magnitudes)
    trace = float(np.real(np.trace(matrix)))
    normalized = matrix / trace if abs(trace) > 1.0e-15 else matrix
    purity = float(np.clip(np.real(np.trace(normalized @ normalized)), 0.0, 1.0))
    decay_shape = np.power(relative, 0.35)
    decays = minimum_decay_seconds + decay_shape * (
        maximum_decay_seconds - minimum_decay_seconds
    )
    decays *= 0.72 + 0.28 * purity
    decays = np.clip(decays, minimum_decay_seconds, maximum_decay_seconds)

    return CNMATDensityResonatorFrame(
        frequencies_hz=frequencies.reshape(-1).astype(np.float64),
        gains=gains.reshape(-1).astype(np.float64),
        decays_seconds=decays.reshape(-1).astype(np.float64),
        phases_radians=phases.astype(np.float64),
        dimension=dimension,
    )
