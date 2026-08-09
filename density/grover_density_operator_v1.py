"""Grover-style amplitude amplification acting directly on density matrices.

The module keeps the phase-one Qiskit basis convention: an ``n``-bit label is
written ``|q[n-1] ... q[0]>`` and converts directly to its integer index.

Each complete iteration is ordered as:

    oracle -> diffusion -> Hamiltonian evolution -> decoherence -> metrics

The partial oracle is the continuous unitary ``exp(-i*pi*strength*P)``, where
``P`` projects onto all marked states. It is identity at strength zero and the
ordinary Grover phase reflection at strength one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np


BasisState = int | str
HamiltonianSource = np.ndarray | Callable[[int, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class DecoherenceConfig:
    """Continuous local noise rates in inverse units of ``time_step``."""

    dephasing_rate: float = 0.0
    amplitude_damping_rate: float = 0.0
    depolarizing_rate: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("dephasing_rate", self.dephasing_rate),
            ("amplitude_damping_rate", self.amplitude_damping_rate),
            ("depolarizing_rate", self.depolarizing_rate),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")


@dataclass(frozen=True)
class GroverDensityMetrics:
    iteration: int
    marked_probability: float
    purity: float
    coherence_l1: float
    von_neumann_entropy: float
    trace: float
    minimum_eigenvalue: float


@dataclass(frozen=True)
class GroverDensityResult:
    n_qubits: int
    marked_indices: tuple[int, ...]
    oracle_strength: float
    time_step: float
    states: tuple[np.ndarray, ...]
    metrics: tuple[GroverDensityMetrics, ...]

    @property
    def final_rho(self) -> np.ndarray:
        return self.states[-1]

    @property
    def final_metrics(self) -> GroverDensityMetrics:
        return self.metrics[-1]


def basis_index(state: BasisState, n_qubits: int) -> int:
    """Validate a basis-state label and return its integer index."""
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, int) or n_qubits < 1:
        raise ValueError("n_qubits must be a positive integer")
    dimension = 1 << n_qubits
    if isinstance(state, bool):
        raise TypeError("basis states must be integers or binary strings")
    if isinstance(state, int):
        index = state
    elif isinstance(state, str):
        if len(state) != n_qubits or any(bit not in "01" for bit in state):
            raise ValueError(
                f"binary state labels must contain exactly {n_qubits} bits"
            )
        index = int(state, 2)
    else:
        raise TypeError("basis states must be integers or binary strings")
    if not 0 <= index < dimension:
        raise ValueError(f"basis-state index must be in [0, {dimension})")
    return index


def marked_indices(
    marked_states: BasisState | Iterable[BasisState], n_qubits: int
) -> tuple[int, ...]:
    if isinstance(marked_states, (int, str)) and not isinstance(marked_states, bool):
        raw: Sequence[BasisState] = (marked_states,)
    else:
        try:
            raw = tuple(marked_states)  # type: ignore[arg-type]
        except TypeError as exc:
            raise TypeError("marked_states must be a state or iterable of states") from exc
    indices = tuple(sorted({basis_index(state, n_qubits) for state in raw}))
    if not indices:
        raise ValueError("at least one marked state is required")
    if len(indices) == 1 << n_qubits:
        raise ValueError("at least one state must remain unmarked")
    return indices


def marked_projector(
    n_qubits: int, marked_states: BasisState | Iterable[BasisState]
) -> np.ndarray:
    """Return P = sum(|marked><marked|) for one or more marked states."""
    indices = marked_indices(marked_states, n_qubits)
    projector = np.zeros((1 << n_qubits, 1 << n_qubits), dtype=np.complex128)
    projector[indices, indices] = 1.0
    return projector


def oracle_operator(
    n_qubits: int,
    marked_states: BasisState | Iterable[BasisState],
    strength: float = 1.0,
) -> np.ndarray:
    """Return exp(-i*pi*strength*P), a continuous phase oracle."""
    if not math.isfinite(strength) or not 0.0 <= strength <= 1.0:
        raise ValueError("oracle strength must be finite and in [0, 1]")
    projector = marked_projector(n_qubits, marked_states)
    phase = np.exp(-1j * math.pi * strength)
    return np.eye(projector.shape[0], dtype=np.complex128) + (phase - 1.0) * projector


def diffusion_operator(n_qubits: int) -> np.ndarray:
    """Return the standard Grover reflection D = 2|s><s| - I."""
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, int) or n_qubits < 1:
        raise ValueError("n_qubits must be a positive integer")
    dimension = 1 << n_qubits
    uniform = np.full(dimension, 1.0 / math.sqrt(dimension), dtype=np.complex128)
    return 2.0 * np.outer(uniform, uniform.conj()) - np.eye(
        dimension, dtype=np.complex128
    )


def uniform_density(n_qubits: int) -> np.ndarray:
    """Return |s><s|, the standard Grover initial density matrix."""
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, int) or n_qubits < 1:
        raise ValueError("n_qubits must be a positive integer")
    dimension = 1 << n_qubits
    uniform = np.full(dimension, 1.0 / math.sqrt(dimension), dtype=np.complex128)
    return np.outer(uniform, uniform.conj())


def normalize_density(rho: np.ndarray, *, atol: float = 1e-10) -> np.ndarray:
    """Validate, Hermitize, and trace-normalize a density matrix."""
    state = np.asarray(rho, dtype=np.complex128)
    if state.ndim == 1:
        norm = float(np.linalg.norm(state))
        if norm <= atol:
            raise ValueError("statevector has zero norm")
        ket = state / norm
        state = np.outer(ket, ket.conj())
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("rho must be a square matrix or a statevector")
    dimension = state.shape[0]
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("rho dimension must be a power of two")
    if not np.all(np.isfinite(state)):
        raise ValueError("rho must contain only finite values")
    if not np.allclose(state, state.conj().T, atol=atol, rtol=0.0):
        raise ValueError("rho must be Hermitian")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= atol:
        raise ValueError("rho must have positive trace")
    state = state / trace
    minimum = float(np.min(np.linalg.eigvalsh(state)).real)
    if minimum < -atol:
        raise ValueError(f"rho must be positive semidefinite (minimum={minimum:.3e})")
    return state


def unitary_evolution(hamiltonian: np.ndarray, time_step: float) -> np.ndarray:
    """Return exp(-i H dt) for a finite Hermitian Hamiltonian."""
    matrix = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Hamiltonian must be square")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("Hamiltonian must contain only finite values")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-10, rtol=0.0):
        raise ValueError("Hamiltonian must be Hermitian")
    if not math.isfinite(time_step) or time_step < 0.0:
        raise ValueError("time_step must be finite and non-negative")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    phases = np.exp(-1j * eigenvalues * time_step)
    return (eigenvectors * phases) @ eigenvectors.conj().T


def _local_operator(operator: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Embed an operator with q0 as the least-significant basis bit."""
    if not 0 <= qubit < n_qubits:
        raise ValueError("qubit lies outside the register")
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(2, dtype=np.complex128)
    for tensor_qubit in reversed(range(n_qubits)):
        result = np.kron(result, operator if tensor_qubit == qubit else identity)
    return result


def apply_kraus_channel(
    rho: np.ndarray, kraus_operators: Sequence[np.ndarray], qubit: int, n_qubits: int
) -> np.ndarray:
    """Apply a trace-preserving single-qubit channel to one register qubit."""
    local = tuple(np.asarray(operator, dtype=np.complex128) for operator in kraus_operators)
    if not local or any(operator.shape != (2, 2) for operator in local):
        raise ValueError("local Kraus operators must be non-empty 2x2 matrices")
    completeness = sum(operator.conj().T @ operator for operator in local)
    if not np.allclose(completeness, np.eye(2), atol=1e-10):
        raise ValueError("Kraus operators must be trace preserving")
    output = np.zeros_like(rho, dtype=np.complex128)
    for operator in local:
        full = _local_operator(operator, qubit, n_qubits)
        output += full @ rho @ full.conj().T
    return normalize_density(output)


def apply_continuous_decoherence(
    rho: np.ndarray,
    config: DecoherenceConfig,
    time_step: float,
    n_qubits: int,
) -> np.ndarray:
    """Apply local Markovian channels using p(dt) = 1 - exp(-rate*dt)."""
    if not math.isfinite(time_step) or time_step < 0.0:
        raise ValueError("time_step must be finite and non-negative")
    state = normalize_density(rho)
    if state.shape != (1 << n_qubits, 1 << n_qubits):
        raise ValueError("rho dimension does not match n_qubits")
    identity = np.eye(2, dtype=np.complex128)
    pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    pauli_y = np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)
    pauli_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)

    dephasing_retention = math.exp(-config.dephasing_rate * time_step)
    dephasing_flip = 0.5 * (1.0 - dephasing_retention)
    dephasing = (
        math.sqrt(1.0 - dephasing_flip) * identity,
        math.sqrt(dephasing_flip) * pauli_z,
    )

    damping = 1.0 - math.exp(-config.amplitude_damping_rate * time_step)
    amplitude_damping = (
        np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - damping)]], dtype=np.complex128),
        np.array([[0.0, math.sqrt(damping)], [0.0, 0.0]], dtype=np.complex128),
    )

    depolarized_fraction = 1.0 - math.exp(-config.depolarizing_rate * time_step)
    depolarizing = (
        math.sqrt(1.0 - 0.75 * depolarized_fraction) * identity,
        math.sqrt(0.25 * depolarized_fraction) * pauli_x,
        math.sqrt(0.25 * depolarized_fraction) * pauli_y,
        math.sqrt(0.25 * depolarized_fraction) * pauli_z,
    )

    for qubit in range(n_qubits):
        if config.dephasing_rate > 0.0:
            state = apply_kraus_channel(state, dephasing, qubit, n_qubits)
        if config.amplitude_damping_rate > 0.0:
            state = apply_kraus_channel(state, amplitude_damping, qubit, n_qubits)
        if config.depolarizing_rate > 0.0:
            state = apply_kraus_channel(state, depolarizing, qubit, n_qubits)
    return state


def density_metrics(
    rho: np.ndarray,
    marked: np.ndarray,
    iteration: int,
) -> GroverDensityMetrics:
    """Measure amplification, purity, l1 coherence, entropy, and validity."""
    state = normalize_density(rho)
    diagonal = np.diag(np.diag(state))
    eigenvalues = np.linalg.eigvalsh(state).real
    entropy_values = np.clip(eigenvalues, 0.0, 1.0)
    nonzero = entropy_values[entropy_values > 1e-15]
    return GroverDensityMetrics(
        iteration=int(iteration),
        marked_probability=float(np.trace(marked @ state).real),
        purity=float(np.trace(state @ state).real),
        coherence_l1=float(np.sum(np.abs(state - diagonal))),
        von_neumann_entropy=float(-np.sum(nonzero * np.log2(nonzero))),
        trace=float(np.trace(state).real),
        minimum_eigenvalue=float(np.min(eigenvalues)),
    )


def _hamiltonian_at(
    source: HamiltonianSource, iteration: int, rho: np.ndarray
) -> np.ndarray:
    value = source(iteration, rho.copy()) if callable(source) else source
    return np.asarray(value, dtype=np.complex128)


def run_density_grover(
    n_qubits: int,
    marked_states: BasisState | Iterable[BasisState],
    iterations: int,
    *,
    initial_rho: np.ndarray | None = None,
    oracle_strength: float = 1.0,
    decoherence: DecoherenceConfig | None = None,
    hamiltonian: HamiltonianSource | None = None,
    time_step: float = 1.0,
) -> GroverDensityResult:
    """Apply Grover reflections and optional open-system evolution to ``rho``."""
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 0:
        raise ValueError("iterations must be a non-negative integer")
    if not math.isfinite(time_step) or time_step < 0.0:
        raise ValueError("time_step must be finite and non-negative")
    indices = marked_indices(marked_states, n_qubits)
    projector = marked_projector(n_qubits, indices)
    oracle = oracle_operator(n_qubits, indices, oracle_strength)
    diffusion = diffusion_operator(n_qubits)
    rho = uniform_density(n_qubits) if initial_rho is None else normalize_density(initial_rho)
    dimension = 1 << n_qubits
    if rho.shape != (dimension, dimension):
        raise ValueError("initial_rho dimension does not match n_qubits")
    noise = decoherence or DecoherenceConfig()

    states = [rho.copy()]
    history = [density_metrics(rho, projector, 0)]
    for iteration in range(1, iterations + 1):
        rho = oracle @ rho @ oracle.conj().T
        rho = diffusion @ rho @ diffusion.conj().T
        if hamiltonian is not None and time_step > 0.0:
            h_matrix = _hamiltonian_at(hamiltonian, iteration, rho)
            if h_matrix.shape != (dimension, dimension):
                raise ValueError("Hamiltonian dimension does not match n_qubits")
            evolution = unitary_evolution(h_matrix, time_step)
            rho = evolution @ rho @ evolution.conj().T
        if time_step > 0.0:
            rho = apply_continuous_decoherence(rho, noise, time_step, n_qubits)
        rho = normalize_density(rho)
        states.append(rho.copy())
        history.append(density_metrics(rho, projector, iteration))

    return GroverDensityResult(
        n_qubits=n_qubits,
        marked_indices=indices,
        oracle_strength=float(oracle_strength),
        time_step=float(time_step),
        states=tuple(states),
        metrics=tuple(history),
    )


class GroverDensityOperator:
    """Reusable configuration wrapper around :func:`run_density_grover`."""

    def __init__(
        self,
        n_qubits: int,
        marked_states: BasisState | Iterable[BasisState],
        *,
        oracle_strength: float = 1.0,
        decoherence: DecoherenceConfig | None = None,
        hamiltonian: HamiltonianSource | None = None,
        time_step: float = 1.0,
    ) -> None:
        self.n_qubits = n_qubits
        self.marked_states = marked_indices(marked_states, n_qubits)
        self.oracle_strength = oracle_strength
        self.decoherence = decoherence or DecoherenceConfig()
        self.hamiltonian = hamiltonian
        self.time_step = time_step

    def run(self, rho: np.ndarray | None, iterations: int) -> GroverDensityResult:
        return run_density_grover(
            self.n_qubits,
            self.marked_states,
            iterations,
            initial_rho=rho,
            oracle_strength=self.oracle_strength,
            decoherence=self.decoherence,
            hamiltonian=self.hamiltonian,
            time_step=self.time_step,
        )
