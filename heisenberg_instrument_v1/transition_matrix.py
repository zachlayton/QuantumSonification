"""Build a 16 x 16 Heisenberg transition field from rho, H, and an observable."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class TransitionMatrixFrame:
    dimension: int
    energies: np.ndarray
    rho_energy_basis: np.ndarray
    observable_energy_basis: np.ndarray
    contributions: np.ndarray
    magnitudes: np.ndarray
    normalized_magnitudes: np.ndarray
    phases: np.ndarray
    signed_gaps: np.ndarray
    audio_frequencies_hz: np.ndarray
    pans: np.ndarray
    expectation: complex
    reconstruction_error: float
    audio_scale_factor: float

    def osc_payloads(self) -> dict[str, list[float] | float | int]:
        """Return row-major, OSC-safe arrays for one complete resonator frame."""
        return {
            "dimension": int(self.dimension),
            "magnitude": self.magnitudes.reshape(-1).astype(float).tolist(),
            "magnitude_normalized": (
                self.normalized_magnitudes.reshape(-1).astype(float).tolist()
            ),
            "phase": self.phases.reshape(-1).astype(float).tolist(),
            "signed_gap": self.signed_gaps.reshape(-1).astype(float).tolist(),
            "frequency_hz": (
                self.audio_frequencies_hz.reshape(-1).astype(float).tolist()
            ),
            "pan": self.pans.reshape(-1).astype(float).tolist(),
            "real": self.contributions.real.reshape(-1).astype(float).tolist(),
            "imag": self.contributions.imag.reshape(-1).astype(float).tolist(),
            "expectation_real": float(self.expectation.real),
            "expectation_imag": float(self.expectation.imag),
            "reconstruction_error": float(self.reconstruction_error),
            "audio_scale_factor": float(self.audio_scale_factor),
        }


def _validated_hermitian(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} contains non-finite values")
    if not np.allclose(matrix, matrix.conj().T, atol=1.0e-10):
        raise ValueError(f"{name} must be Hermitian")
    return matrix


def transition_matrix_frame(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    observable: np.ndarray,
    *,
    base_frequency_hz: float = 55.0,
    maximum_frequency_hz: float = 12_000.0,
    diagonal_anchor_hz: float = 27.5,
) -> TransitionMatrixFrame:
    """Construct the relational matrix whose sum reconstructs ``Tr(rho A)``.

    The exact complex contribution in energy-basis cell (m, n) is
    ``rho[m,n] * A[n,m]``. Off-diagonal resonator frequencies preserve the
    ratios of Hamiltonian energy gaps under one global audio scale. Diagonal
    cells have zero physical transition frequency, so they receive a clearly
    separate low-register anchor mapping for audibility.
    """
    density = _validated_hermitian(rho, "rho")
    h = _validated_hermitian(hamiltonian, "hamiltonian")
    a = _validated_hermitian(observable, "observable")
    if h.shape != density.shape or a.shape != density.shape:
        raise ValueError("rho, hamiltonian, and observable must share one shape")
    if not np.isclose(np.trace(density), 1.0, atol=1.0e-10):
        raise ValueError("rho must have trace one")
    if base_frequency_hz <= 0.0 or maximum_frequency_hz <= 0.0:
        raise ValueError("audio frequencies must be positive")
    if maximum_frequency_hz < base_frequency_hz:
        raise ValueError("maximum_frequency_hz must not be below the base")

    energies, energy_vectors = np.linalg.eigh(h)
    rho_e = energy_vectors.conj().T @ density @ energy_vectors
    observable_e = energy_vectors.conj().T @ a @ energy_vectors

    contributions = rho_e * observable_e.T
    expectation = complex(np.trace(density @ a))
    reconstruction_error = float(abs(np.sum(contributions) - expectation))

    magnitudes = np.abs(contributions)
    peak = float(np.max(magnitudes))
    normalized = magnitudes / peak if peak > 1.0e-15 else np.zeros_like(magnitudes)
    phases = np.angle(contributions)

    signed_gaps = energies[:, None] - energies[None, :]
    positive_gaps = np.abs(signed_gaps[np.abs(signed_gaps) > 1.0e-12])
    if positive_gaps.size:
        audio_scale = float(base_frequency_hz / np.min(positive_gaps))
    else:
        audio_scale = 1.0
    audio_frequencies = np.abs(signed_gaps) * audio_scale
    audio_frequencies = np.clip(audio_frequencies, 0.0, maximum_frequency_hz)

    dimension = density.shape[0]
    diagonal = np.arange(dimension)
    # Diagonal entries have no transition frequency. Their low anchor ladder
    # is a declared sonification carrier, not a physical energy gap.
    anchor_ratios = np.power(2.0, diagonal / max(dimension, 1))
    audio_frequencies[diagonal, diagonal] = (
        float(diagonal_anchor_hz) * anchor_ratios
    )

    if dimension == 1:
        pans = np.zeros((1, 1), dtype=np.float64)
    else:
        rows = np.arange(dimension)[:, None]
        columns = np.arange(dimension)[None, :]
        pans = (columns - rows) / float(dimension - 1)

    if not math.isfinite(reconstruction_error):
        raise ValueError("transition reconstruction produced a non-finite result")

    return TransitionMatrixFrame(
        dimension=dimension,
        energies=energies,
        rho_energy_basis=rho_e,
        observable_energy_basis=observable_e,
        contributions=contributions,
        magnitudes=magnitudes,
        normalized_magnitudes=normalized,
        phases=phases,
        signed_gaps=signed_gaps,
        audio_frequencies_hz=audio_frequencies,
        pans=pans,
        expectation=expectation,
        reconstruction_error=reconstruction_error,
        audio_scale_factor=audio_scale,
    )
