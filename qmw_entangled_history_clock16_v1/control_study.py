"""Coherent, dephased, shuffled, and sequential history controls.

The controls distinguish a quantum history state from classical reordering and
from an incoherent clock-labelled ensemble.  They are read-only constructions:
no control performs a clock measurement or mutates the canonical QMW state.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class HistoryControlStudy:
    """Four matched representations of the same set of system moments."""

    sequential_order: np.ndarray
    shuffled_order: np.ndarray
    sequential_states: np.ndarray = field(repr=False)
    shuffled_states: np.ndarray = field(repr=False)
    sequential_densities: np.ndarray = field(repr=False)
    shuffled_densities: np.ndarray = field(repr=False)
    coherent_joint_density: np.ndarray = field(repr=False)
    incoherent_joint_density: np.ndarray = field(repr=False)
    coherent_reduced_clock: np.ndarray = field(repr=False)
    incoherent_reduced_clock: np.ndarray = field(repr=False)
    coherent_reduced_system: np.ndarray = field(repr=False)
    incoherent_reduced_system: np.ndarray = field(repr=False)
    sequential_adjacent_distances: np.ndarray
    shuffled_adjacent_distances: np.ndarray
    coherent_joint_purity: float
    incoherent_joint_purity: float
    coherent_temporal_block_coherence: float
    incoherent_temporal_block_coherence: float
    reduced_system_difference: float
    shuffle_seed: int
    protocol_kind: str = "page_wootters_matched_history_controls"


def clock_dephase_joint_density(history: DiscreteHistoryState) -> np.ndarray:
    """Delete all off-diagonal clock blocks while preserving each moment."""

    blocks = history.branch_blocks()
    clock_states = history.clock_states
    system_dimension = history.system_dimension
    joint = np.zeros(
        (history.joint_dimension, history.joint_dimension),
        dtype=np.complex128,
    )
    for clock_index, block in enumerate(blocks):
        start = clock_index * system_dimension
        joint[
            start : start + system_dimension,
            start : start + system_dimension,
        ] = np.outer(block, block.conj())
    trace = float(np.trace(joint).real)
    if abs(trace - 1.0) > 1e-10:
        raise RuntimeError(f"clock-dephased joint trace is {trace}, expected 1")
    return joint


def reduced_states_from_joint(
    joint_density: np.ndarray,
    *,
    clock_states: int,
    system_dimension: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (clock, system) partial traces for clock-major joint indexing."""

    clock_count = int(clock_states)
    system_size = int(system_dimension)
    joint_size = clock_count * system_size
    density = np.asarray(joint_density, dtype=np.complex128)
    if density.shape != (joint_size, joint_size):
        raise ValueError(
            f"joint_density must have shape {(joint_size, joint_size)}"
        )
    tensor = density.reshape(
        clock_count,
        system_size,
        clock_count,
        system_size,
    )
    clock = np.trace(tensor, axis1=1, axis2=3)
    system = np.trace(tensor, axis1=0, axis2=2)
    return clock, system


def temporal_block_coherence(
    joint_density: np.ndarray,
    *,
    clock_states: int,
    system_dimension: int,
) -> float:
    """Normalized sum of Frobenius norms of off-diagonal clock blocks.

    For the equally weighted pure history prepared by this package, the value
    is one before clock dephasing and zero afterward.  This witnesses retained
    cross-time blocks; it is distinct from system--time entanglement ``E_2``.
    """

    clock_count = int(clock_states)
    system_size = int(system_dimension)
    if clock_count <= 1:
        return 0.0
    joint_size = clock_count * system_size
    density = np.asarray(joint_density, dtype=np.complex128)
    if density.shape != (joint_size, joint_size):
        raise ValueError(
            f"joint_density must have shape {(joint_size, joint_size)}"
        )
    tensor = density.reshape(
        clock_count,
        system_size,
        clock_count,
        system_size,
    )
    total = 0.0
    for left in range(clock_count):
        for right in range(clock_count):
            if left != right:
                total += float(np.linalg.norm(tensor[left, :, right, :]))
    return total / float(clock_count - 1)


def adjacent_pure_state_distances(states: np.ndarray) -> np.ndarray:
    """Trace distance between each adjacent pair in an ordered pure trajectory."""

    values = np.asarray(states, dtype=np.complex128)
    if values.ndim != 2 or values.shape[0] < 2:
        raise ValueError("states must contain at least two state vectors")
    overlaps = np.sum(values[:-1].conj() * values[1:], axis=1)
    return np.sqrt(np.clip(1.0 - np.abs(overlaps) ** 2, 0.0, 1.0))


def build_control_study(
    history: DiscreteHistoryState,
    *,
    shuffle_seed: int = 23,
) -> HistoryControlStudy:
    """Build four matched controls from one prepared coherent history state."""

    sequential_order = np.arange(history.clock_states, dtype=int)
    shuffled_order = np.random.default_rng(int(shuffle_seed)).permutation(
        sequential_order
    )
    sequential_states = history.conditional_states()
    sequential_densities = history.conditional_densities()
    shuffled_states = sequential_states[shuffled_order].copy()
    shuffled_densities = sequential_densities[shuffled_order].copy()

    coherent = history.density_matrix()
    incoherent = clock_dephase_joint_density(history)
    coherent_clock, coherent_system = reduced_states_from_joint(
        coherent,
        clock_states=history.clock_states,
        system_dimension=history.system_dimension,
    )
    incoherent_clock, incoherent_system = reduced_states_from_joint(
        incoherent,
        clock_states=history.clock_states,
        system_dimension=history.system_dimension,
    )
    coherent_purity = float(np.trace(coherent @ coherent).real)
    incoherent_purity = float(np.trace(incoherent @ incoherent).real)

    return HistoryControlStudy(
        sequential_order=sequential_order,
        shuffled_order=shuffled_order,
        sequential_states=sequential_states,
        shuffled_states=shuffled_states,
        sequential_densities=sequential_densities,
        shuffled_densities=shuffled_densities,
        coherent_joint_density=coherent,
        incoherent_joint_density=incoherent,
        coherent_reduced_clock=coherent_clock,
        incoherent_reduced_clock=incoherent_clock,
        coherent_reduced_system=coherent_system,
        incoherent_reduced_system=incoherent_system,
        sequential_adjacent_distances=adjacent_pure_state_distances(
            sequential_states
        ),
        shuffled_adjacent_distances=adjacent_pure_state_distances(
            shuffled_states
        ),
        coherent_joint_purity=coherent_purity,
        incoherent_joint_purity=incoherent_purity,
        coherent_temporal_block_coherence=temporal_block_coherence(
            coherent,
            clock_states=history.clock_states,
            system_dimension=history.system_dimension,
        ),
        incoherent_temporal_block_coherence=temporal_block_coherence(
            incoherent,
            clock_states=history.clock_states,
            system_dimension=history.system_dimension,
        ),
        reduced_system_difference=float(
            np.linalg.norm(coherent_system - incoherent_system)
        ),
        shuffle_seed=int(shuffle_seed),
    )
