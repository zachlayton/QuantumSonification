"""Translate a finite density operator into a harmonic wavetable.

The mapping mirrors the QMW QFT spectral synthesizer: sixteen complex spectral
coefficients render one normalized 256-sample table. Populations determine
harmonic amplitudes, while coherence relative to the strongest occupied
energy-basis state supplies deterministic relative phases.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DensitySpectralWavetableFrame:
    """One complete density-derived harmonic wavetable."""

    samples: np.ndarray
    harmonic_amplitudes: np.ndarray
    harmonic_phases: np.ndarray
    reference_index: int

    @property
    def sample_count(self) -> int:
        return int(self.samples.size)

    @property
    def harmonic_count(self) -> int:
        return int(self.harmonic_amplitudes.size)


def density_matrix_to_spectral_wavetable(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    *,
    sample_count: int = 256,
    peak_amplitude: float = 0.95,
    spectral_tilt: float = 0.35,
    coherence_phase_threshold: float = 1.0e-5,
) -> DensitySpectralWavetableFrame:
    """Render an energy-basis density matrix as a periodic harmonic table.

    For a pure state, ``rho[k, reference]`` recovers each state's phase
    relative to the strongest occupied state. For a mixed or incoherent state,
    harmonics without meaningful reference coherence receive zero phase. The
    representation is a sonification mapping, not a reconstruction of a
    unique state vector from a mixed density operator.
    """

    matrix = np.asarray(rho, dtype=np.complex128)
    operator = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("rho must be a square matrix")
    if operator.shape != matrix.shape:
        raise ValueError("hamiltonian must have the same shape as rho")
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(operator)):
        raise ValueError("rho and hamiltonian must contain only finite values")
    if int(sample_count) < 16:
        raise ValueError("sample_count must be at least 16")
    if not 0.0 < float(peak_amplitude) <= 1.0:
        raise ValueError("peak_amplitude must be in (0, 1]")
    if float(spectral_tilt) < 0.0:
        raise ValueError("spectral_tilt must be nonnegative")

    matrix = 0.5 * (matrix + matrix.conj().T)
    trace = float(np.real(np.trace(matrix)))
    if abs(trace) <= 1.0e-15:
        raise ValueError("rho must have nonzero trace")
    matrix = matrix / trace
    operator = 0.5 * (operator + operator.conj().T)

    _, energy_vectors = np.linalg.eigh(operator)
    energy_rho = energy_vectors.conj().T @ matrix @ energy_vectors
    populations = np.clip(np.real(np.diag(energy_rho)), 0.0, None)
    population_total = float(np.sum(populations))
    if population_total <= 1.0e-15:
        raise ValueError("rho has no positive energy-basis population")
    populations /= population_total

    reference = int(np.argmax(populations))
    reference_population = float(populations[reference])
    amplitudes = np.sqrt(populations)
    phases = np.zeros(matrix.shape[0], dtype=np.float64)
    for index, population in enumerate(populations):
        coherence_bound = np.sqrt(float(population) * reference_population)
        if coherence_bound <= 1.0e-15:
            continue
        relation = complex(energy_rho[index, reference])
        normalized_coherence = abs(relation) / coherence_bound
        if normalized_coherence >= float(coherence_phase_threshold):
            phases[index] = float(np.angle(relation))

    count = int(sample_count)
    phase_axis = 2.0 * np.pi * np.arange(count, dtype=np.float64) / count
    table = np.zeros(count, dtype=np.float64)
    for index, (amplitude, phase) in enumerate(zip(amplitudes, phases)):
        harmonic = index + 1
        weight = float(amplitude) / (harmonic ** float(spectral_tilt))
        table += weight * np.sin(harmonic * phase_axis + float(phase))

    table -= float(np.mean(table))
    peak = float(np.max(np.abs(table)))
    if peak > 1.0e-15:
        table *= float(peak_amplitude) / peak
    table = np.clip(table, -float(peak_amplitude), float(peak_amplitude))

    return DensitySpectralWavetableFrame(
        samples=table.astype(np.float64),
        harmonic_amplitudes=amplitudes.astype(np.float64),
        harmonic_phases=phases,
        reference_index=reference,
    )
