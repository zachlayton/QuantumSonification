"""Diagnostics for coherent discrete clock--system history states.

The quantities in this module are read-only functions of a prepared history.
They do not measure, collapse, sample, or mutate either subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .history_state import DiscreteHistoryState


def qft_matrix(dimension: int) -> np.ndarray:
    """Return the unitary forward QFT with exp(-2 pi i m t / N)."""

    size = int(dimension)
    if size <= 0:
        raise ValueError("dimension must be positive")
    modes = np.arange(size, dtype=float)[:, np.newaxis]
    times = np.arange(size, dtype=float)[np.newaxis, :]
    return np.exp(-2j * np.pi * modes * times / size) / np.sqrt(size)


@dataclass(frozen=True)
class HistoryDiagnostics:
    """Reduced states and finite-history dynamical diagnostics."""

    clock_density: np.ndarray = field(repr=False)
    system_average_density: np.ndarray = field(repr=False)
    clock_fourier_density: np.ndarray = field(repr=False)
    clock_fourier_probabilities: np.ndarray
    clock_schmidt_eigenvalues: np.ndarray
    clock_schmidt_modes: np.ndarray = field(repr=False)
    loschmidt_echoes: np.ndarray
    clock_purity: float
    system_average_purity: float
    system_time_linear_entropy: float
    discrete_loschmidt_echo_average: float
    effective_schmidt_rank: int
    schmidt_participation_number: float
    schmidt_von_neumann_entropy_bits: float
    clock_states: int
    protocol_kind: str = "page_wootters_history_diagnostics"

    @property
    def dominant_clock_fourier_mode(self) -> int:
        return int(np.argmax(self.clock_fourier_probabilities))


def reduced_clock_density(history: DiscreteHistoryState) -> np.ndarray:
    """Trace out the system: rho_C[t,t'] = <psi(t')|psi(t)> / N."""

    blocks = history.branch_blocks()
    density = blocks @ blocks.conj().T
    return 0.5 * (density + density.conj().T)


def reduced_system_density(history: DiscreteHistoryState) -> np.ndarray:
    """Trace out the clock, yielding the finite temporal-average state."""

    blocks = history.branch_blocks()
    density = np.einsum("ti,tj->ij", blocks, blocks.conj(), optimize=True)
    return 0.5 * (density + density.conj().T)


def discrete_loschmidt_echoes(history: DiscreteHistoryState) -> np.ndarray:
    """Return |<psi_0|psi(t)>|^2 for all represented clock values."""

    states = history.conditional_states()
    overlaps = states @ history.initial_state.conj()
    return np.asarray(np.abs(overlaps) ** 2, dtype=float)


def deterministic_density_eigendecomposition(
    density: np.ndarray,
    *,
    tolerance: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray]:
    """Return deterministic eigenvalues and row eigenmodes of a density.

    Equal weights do not define unique eigenvectors.  Within each degenerate
    eigenspace we diagonalize the computational-position operator, then
    remove each mode's arbitrary global phase.  This makes downstream
    sonification reproducible without changing the density operator.
    """

    threshold = float(tolerance)
    if threshold <= 0.0:
        raise ValueError("tolerance must be positive")
    matrix = np.asarray(density, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("density must be square")
    if np.max(np.abs(matrix - matrix.conj().T)) > 1e-9:
        raise ValueError("density must be Hermitian")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order].real, 0.0, None)
    eigenvectors = eigenvectors[:, order]

    start = 0
    positions = np.arange(matrix.shape[0], dtype=float)
    while start < eigenvalues.size:
        stop = start + 1
        scale = max(1.0, float(eigenvalues[start]))
        while (
            stop < eigenvalues.size
            and abs(float(eigenvalues[stop] - eigenvalues[start]))
            <= threshold * scale
        ):
            stop += 1
        if stop - start > 1:
            subspace = eigenvectors[:, start:stop]
            projected_position = (
                subspace.conj().T @ (positions[:, np.newaxis] * subspace)
            )
            projected_position = 0.5 * (
                projected_position + projected_position.conj().T
            )
            position_values, rotation = np.linalg.eigh(projected_position)
            eigenvectors[:, start:stop] = (
                subspace @ rotation[:, np.argsort(position_values)]
            )
        start = stop

    for column in range(eigenvectors.shape[1]):
        mode = eigenvectors[:, column]
        magnitudes = np.abs(mode)
        maximum = float(np.max(magnitudes))
        candidates = np.flatnonzero(
            magnitudes >= maximum * (1.0 - 100.0 * threshold)
        )
        anchor = int(candidates[0])
        if abs(mode[anchor]) > threshold:
            eigenvectors[:, column] *= np.exp(-1j * np.angle(mode[anchor]))

    return eigenvalues, eigenvectors.T.copy()


def clock_schmidt_decomposition(
    history: DiscreteHistoryState,
    *,
    tolerance: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray]:
    """Return clock Schmidt weights and deterministic temporal modes."""

    return deterministic_density_eigendecomposition(
        reduced_clock_density(history),
        tolerance=tolerance,
    )


def analyze_history(history: DiscreteHistoryState) -> HistoryDiagnostics:
    """Calculate reduced-state, entanglement, echo, and clock-QFT metrics."""

    clock_density = reduced_clock_density(history)
    system_density = reduced_system_density(history)

    clock_trace = float(np.trace(clock_density).real)
    system_trace = float(np.trace(system_density).real)
    if abs(clock_trace - 1.0) > 1e-10:
        raise RuntimeError(f"reduced clock trace is {clock_trace}, expected 1")
    if abs(system_trace - 1.0) > 1e-10:
        raise RuntimeError(f"reduced system trace is {system_trace}, expected 1")

    clock_purity = float(np.trace(clock_density @ clock_density).real)
    system_purity = float(np.trace(system_density @ system_density).real)
    if abs(clock_purity - system_purity) > 1e-9:
        raise RuntimeError(
            "pure history requires equal reduced purities; "
            f"clock={clock_purity}, system={system_purity}"
        )
    linear_entropy = float(np.clip(1.0 - clock_purity, 0.0, 1.0))

    fourier = qft_matrix(history.clock_states)
    fourier_density = fourier @ clock_density @ fourier.conj().T
    fourier_density = 0.5 * (fourier_density + fourier_density.conj().T)
    fourier_probabilities = np.clip(
        np.diag(fourier_density).real,
        0.0,
        None,
    )
    fourier_total = float(fourier_probabilities.sum())
    if fourier_total <= 1e-15:
        raise RuntimeError("clock Fourier probabilities have zero total weight")
    fourier_probabilities /= fourier_total

    echoes = discrete_loschmidt_echoes(history)
    schmidt_eigenvalues, schmidt_modes = clock_schmidt_decomposition(history)
    schmidt_threshold = max(1e-12, 1e-10 * float(schmidt_eigenvalues[0]))
    effective_rank = int(np.count_nonzero(
        schmidt_eigenvalues > schmidt_threshold
    ))
    participation_number = float(1.0 / clock_purity)
    positive_weights = schmidt_eigenvalues[
        schmidt_eigenvalues > schmidt_threshold
    ]
    von_neumann_entropy = float(-np.sum(
        positive_weights * np.log2(positive_weights)
    ))
    return HistoryDiagnostics(
        clock_density=clock_density,
        system_average_density=system_density,
        clock_fourier_density=fourier_density,
        clock_fourier_probabilities=fourier_probabilities,
        clock_schmidt_eigenvalues=schmidt_eigenvalues,
        clock_schmidt_modes=schmidt_modes,
        loschmidt_echoes=echoes,
        clock_purity=clock_purity,
        system_average_purity=system_purity,
        system_time_linear_entropy=linear_entropy,
        discrete_loschmidt_echo_average=float(np.mean(echoes)),
        effective_schmidt_rank=effective_rank,
        schmidt_participation_number=participation_number,
        schmidt_von_neumann_entropy_bits=von_neumann_entropy,
        clock_states=history.clock_states,
    )
