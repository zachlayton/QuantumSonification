"""Exact discrete Page--Wootters history states for QMW's 16-state system.

This first reference module prepares only the coherent joint state

    |Psi> = 1/sqrt(N) sum_t |t>_C (U**t |psi_0>)_S.

It deliberately does not measure the clock, mutate the canonical live density
matrix, publish OSC, or introduce stochastic sampling.  Joint basis indexing
matches the existing QMW eight-qubit convention:

    joint_index = system_index + system_dimension * clock_index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log2, sqrt
from typing import Any

import numpy as np


DEFAULT_CLOCK_QUBITS = 4
DEFAULT_CLOCK_STATES = 1 << DEFAULT_CLOCK_QUBITS
DEFAULT_SYSTEM_QUBITS = 4
DEFAULT_SYSTEM_DIMENSION = 1 << DEFAULT_SYSTEM_QUBITS


def _as_state_vector(value: Any, dimension: int) -> np.ndarray:
    state = np.asarray(value, dtype=np.complex128).reshape(-1)
    if state.size != dimension:
        raise ValueError(
            f"initial_state requires {dimension} amplitudes; got {state.size}"
        )
    if not np.isfinite(state).all():
        raise ValueError("initial_state contains non-finite amplitudes")
    norm = float(np.linalg.norm(state))
    if norm <= 1e-15:
        raise ValueError("initial_state must have nonzero norm")
    return state / norm


def _as_unitary(value: Any) -> np.ndarray:
    unitary = np.asarray(value, dtype=np.complex128)
    if unitary.ndim != 2 or unitary.shape[0] != unitary.shape[1]:
        raise ValueError("unitary must be a square matrix")
    if not np.isfinite(unitary).all():
        raise ValueError("unitary contains non-finite values")
    identity = np.eye(unitary.shape[0], dtype=np.complex128)
    error = float(np.max(np.abs(unitary.conj().T @ unitary - identity)))
    if error > 1e-9:
        raise ValueError(f"unitary failed validation: error={error}")
    return unitary


@dataclass(frozen=True)
class DiscreteHistoryState:
    """Pure clock--system history state with clock-major basis ordering."""

    state_vector: np.ndarray = field(repr=False)
    branch_states: np.ndarray = field(repr=False)
    unitary: np.ndarray = field(repr=False)
    initial_state: np.ndarray = field(repr=False)
    clock_qubits: int
    system_qubits: int
    protocol_kind: str = "page_wootters_discrete_history_state"
    basis_ordering: str = "joint_index=system_index+system_dimension*clock_index"

    @property
    def clock_states(self) -> int:
        return 1 << self.clock_qubits

    @property
    def system_dimension(self) -> int:
        return 1 << self.system_qubits

    @property
    def joint_dimension(self) -> int:
        return self.clock_states * self.system_dimension

    def clock_block(self, clock_index: int) -> np.ndarray:
        """Return the unnormalized system block <t|Psi>."""

        index = int(clock_index)
        if not 0 <= index < self.clock_states:
            raise IndexError(
                f"clock_index must be in [0, {self.clock_states - 1}]"
            )
        start = index * self.system_dimension
        return self.state_vector[start : start + self.system_dimension].copy()

    def clock_probability(self, clock_index: int) -> float:
        """Return the Born probability for a computational-basis clock value."""

        block = self.clock_block(clock_index)
        return float(np.vdot(block, block).real)

    def conditional_state(self, clock_index: int) -> np.ndarray:
        """Return the normalized conditional system state for clock value ``t``."""

        block = self.clock_block(clock_index)
        probability = self.clock_probability(clock_index)
        if probability <= 1e-15:
            raise RuntimeError("selected clock branch has zero probability")
        return block / sqrt(probability)

    def conditional_density(self, clock_index: int) -> np.ndarray:
        """Return |psi(t)><psi(t)| without measuring or mutating the history."""

        state = self.conditional_state(clock_index)
        return np.outer(state, state.conj())

    def clock_probabilities(self) -> np.ndarray:
        """Return all computational-basis clock probabilities in clock order."""

        probabilities = np.sum(np.abs(self.branch_blocks()) ** 2, axis=1).real
        return np.asarray(probabilities, dtype=float)

    def branch_blocks(self) -> np.ndarray:
        """Return the N unnormalized blocks <t|Psi> as a defensive copy."""

        return self.state_vector.reshape(
            self.clock_states,
            self.system_dimension,
        ).copy()

    def conditional_states(self) -> np.ndarray:
        """Return all normalized |psi(t)> states in ascending clock order."""

        blocks = self.branch_blocks()
        probabilities = np.sum(np.abs(blocks) ** 2, axis=1).real
        if np.any(probabilities <= 1e-15):
            raise RuntimeError("one or more clock branches have zero probability")
        return blocks / np.sqrt(probabilities)[:, np.newaxis]

    def conditional_densities(self) -> np.ndarray:
        """Return all conditional 16 x 16 pure densities in clock order."""

        states = self.conditional_states()
        return np.einsum("ti,tj->tij", states, states.conj(), optimize=True)

    def density_matrix(self) -> np.ndarray:
        return np.outer(self.state_vector, self.state_vector.conj())


def prepare_discrete_history_state(
    unitary: Any,
    initial_state: Any,
    *,
    clock_qubits: int = DEFAULT_CLOCK_QUBITS,
) -> DiscreteHistoryState:
    """Prepare the exact history state using binary controlled-power semantics.

    For a clock value ``t``, the system branch is assembled from the powers
    ``U**1, U**2, U**4, ...`` selected by the set bits of ``t``.  This mirrors
    the phase-estimation-like history-state circuit without requiring Qiskit.
    """

    count = int(clock_qubits)
    if count <= 0:
        raise ValueError("clock_qubits must be positive")
    clock_states = 1 << count
    operation = _as_unitary(unitary)
    system_dimension = operation.shape[0]
    system_qubits = int(round(log2(system_dimension)))
    if 1 << system_qubits != system_dimension:
        raise ValueError("system dimension must be a power of two")
    initial = _as_state_vector(initial_state, system_dimension)

    controlled_powers = tuple(
        np.linalg.matrix_power(operation, 1 << bit) for bit in range(count)
    )
    branches = np.empty(
        (clock_states, system_dimension),
        dtype=np.complex128,
    )
    for clock_index in range(clock_states):
        branch = initial.copy()
        for bit, power in enumerate(controlled_powers):
            if (clock_index >> bit) & 1:
                branch = power @ branch
        branches[clock_index] = branch

    state_vector = (branches / sqrt(clock_states)).reshape(-1)
    normalization_error = abs(float(np.vdot(state_vector, state_vector).real) - 1.0)
    if normalization_error > 1e-10:
        raise RuntimeError(
            f"history-state normalization failed: error={normalization_error}"
        )
    return DiscreteHistoryState(
        state_vector=state_vector,
        branch_states=branches,
        unitary=operation,
        initial_state=initial,
        clock_qubits=count,
        system_qubits=system_qubits,
    )


def prepare_floquet_history_state(
    floquet_model: Any,
    initial_state: Any,
    *,
    clock_qubits: int = DEFAULT_CLOCK_QUBITS,
) -> DiscreteHistoryState:
    """Prepare a history state from ``FloquetTimeCrystal16.floquet_unitary``."""

    try:
        unitary = floquet_model.floquet_unitary
    except AttributeError as exc:
        raise TypeError("floquet_model must expose floquet_unitary") from exc
    if np.asarray(unitary).shape != (
        DEFAULT_SYSTEM_DIMENSION,
        DEFAULT_SYSTEM_DIMENSION,
    ):
        raise ValueError("QMW Floquet history requires a 16 x 16 system unitary")
    return prepare_discrete_history_state(
        unitary,
        initial_state,
        clock_qubits=clock_qubits,
    )
