"""Read-only reduced-state and correlation observations of sealed frames.

This module is intentionally upstream of state-derived geometry.  It derives
information-theoretic and correlation observables from one immutable
``QuantumFrame`` and does not evolve, project, measure, publish, or sonify the
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np

from qmw.qmw_emergent_geometry import (
    mutual_information,
    pauli_pair_expectation,
    reduced_density_matrix,
    two_qubit_concurrence,
    von_neumann_entropy,
)

from .dynamics import Array, QuantumFrame, _readonly
from .pauli_basis import SINGLE_PAULI


def _real_expectation(rho: Array, operator: Array) -> float:
    value = complex(np.trace(rho @ operator))
    if abs(value.imag) > 1.0e-10:
        raise ValueError("Hermitian observable had unexpectedly complex expectation.")
    return float(value.real)


@dataclass(frozen=True)
class LocalBlochVector:
    """A single-qubit reduced-state view, never the full system state."""

    qubit: int
    reduced_density: Array
    x: float
    y: float
    z: float
    entropy_bits: float

    @property
    def vector(self) -> Array:
        return _readonly((self.x, self.y, self.z), dtype=float)

    @property
    def radius(self) -> float:
        return float(np.linalg.norm(self.vector))


@dataclass(frozen=True)
class PairCorrelationTensor:
    """Measured two-qubit correlation and connected-correlation tensors."""

    left: int
    right: int
    reduced_density: Array
    entropy_bits: float
    mutual_information_bits: float
    concurrence: float
    tensor: Array
    connected_tensor: Array


@dataclass(frozen=True)
class QuantumInformationFrame:
    """One immutable information/correlation branch from a ``QuantumFrame``."""

    revision: int
    time: float
    qubits: int
    global_entropy_bits: float
    global_purity: float
    local_bloch_vectors: tuple[LocalBlochVector, ...]
    pair_correlations: tuple[PairCorrelationTensor, ...]
    reduced_density_matrices: Mapping[tuple[int, ...], Array]
    provenance: str = "read_only_quantum_frame_information_observer_v1"


def observe_quantum_information(frame: QuantumFrame) -> QuantumInformationFrame:
    """Derive reductions, Bloch vectors, tensors, and entanglement diagnostics.

    The input must already be sealed by ``QuantumFrameEngine`` or
    ``QuantumFrame.observe``.  All output arrays are copies marked read-only.
    """

    if not isinstance(frame, QuantumFrame):
        raise ValueError("observe_quantum_information requires a QuantumFrame.")
    qubits = frame.hamiltonian.qubits
    reduced: dict[tuple[int, ...], Array] = {}
    local: list[LocalBlochVector] = []
    for qubit in range(qubits):
        key = (qubit,)
        state = reduced_density_matrix(frame.rho, key)
        reduced[key] = _readonly(state)
        local.append(LocalBlochVector(
            qubit=qubit,
            reduced_density=reduced[key],
            x=_real_expectation(state, SINGLE_PAULI["X"]),
            y=_real_expectation(state, SINGLE_PAULI["Y"]),
            z=_real_expectation(state, SINGLE_PAULI["Z"]),
            entropy_bits=von_neumann_entropy(state),
        ))

    pairs: list[PairCorrelationTensor] = []
    axes = ("X", "Y", "Z")
    for left in range(qubits):
        for right in range(left + 1, qubits):
            key = (left, right)
            state = reduced_density_matrix(frame.rho, key)
            reduced[key] = _readonly(state)
            tensor = np.asarray([
                [pauli_pair_expectation(frame.rho, left, right, first + second) for second in axes]
                for first in axes
            ], dtype=float)
            left_vector = local[left].vector
            right_vector = local[right].vector
            pairs.append(PairCorrelationTensor(
                left=left,
                right=right,
                reduced_density=reduced[key],
                entropy_bits=von_neumann_entropy(state),
                mutual_information_bits=mutual_information(frame.rho, (left,), (right,)),
                concurrence=two_qubit_concurrence(state),
                tensor=_readonly(tensor, dtype=float),
                connected_tensor=_readonly(tensor - np.outer(left_vector, right_vector), dtype=float),
            ))
    return QuantumInformationFrame(
        revision=frame.frame_index,
        time=frame.time,
        qubits=qubits,
        global_entropy_bits=von_neumann_entropy(frame.rho),
        global_purity=frame.purity,
        local_bloch_vectors=tuple(local),
        pair_correlations=tuple(pairs),
        reduced_density_matrices=MappingProxyType(dict(reduced)),
    )


__all__ = [
    "LocalBlochVector", "PairCorrelationTensor", "QuantumInformationFrame",
    "observe_quantum_information",
]
