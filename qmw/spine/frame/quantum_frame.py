"""QuantumFrame: one complete, synchronized quantum instant.

Every downstream consumer (flow, geometry, sound, GUI) reads the same sealed
frame instead of separately re-deriving rho, H, or observables -- that is
what prevents the timing mismatch where one component sees rho(t) and
another sees a separately updated Bloch state from rho(t - dt).

Publication happens only after the frame is complete: build_frame() computes
every derived quantity from one rho snapshot, validates it, and returns an
immutable QuantumFrame. Nothing downstream mutates it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from qmw.spine.quantum.evolution import commutator_norm, unitary_velocity
from qmw.spine.quantum.hamiltonian import Hamiltonian
from qmw.spine.quantum.pauli import all_pauli_labels, decompose
from qmw.spine.quantum.state import StateDiagnostics, validate_density_matrix, von_neumann_entropy

GENERATOR_VERSION = "qmw-spine-v1"


@dataclass(frozen=True)
class QuantumFrame:
    frame_id: int
    state_epoch: int
    t: float
    dt: float
    basis_id: str
    generator_version: str
    n_qubits: int

    rho: np.ndarray
    hamiltonian_matrix: np.ndarray
    rho_dot_unitary: np.ndarray
    rho_dot_dissipative: np.ndarray | None

    diagnostics: StateDiagnostics
    pauli: dict[str, float]
    pauli_velocity: dict[str, float]
    commutator_norm: float
    energy: float
    entropy: float

    projector_id: str | None = None
    event_discontinuity: dict[str, Any] | None = None
    source: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rho.setflags(write=False)
        self.hamiltonian_matrix.setflags(write=False)
        self.rho_dot_unitary.setflags(write=False)
        if self.rho_dot_dissipative is not None:
            self.rho_dot_dissipative.setflags(write=False)

    @property
    def purity(self) -> float:
        return self.diagnostics.purity


def build_frame(
    t: float,
    dt: float,
    rho: np.ndarray,
    hamiltonian: Hamiltonian,
    frame_id: int,
    state_epoch: int,
    basis_id: str = "computational",
    projector_id: str | None = None,
    pauli_labels: tuple[str, ...] | None = None,
    dissipator: Any = None,
    event_discontinuity: dict[str, Any] | None = None,
    source: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> QuantumFrame:
    """Freeze one rho snapshot into a sealed QuantumFrame. Raises StateInvariantError if rho is invalid."""
    diagnostics = validate_density_matrix(rho)
    H = hamiltonian.matrix(t)
    rho_dot_unitary = unitary_velocity(H, rho)
    rho_dot_dissipative = dissipator(rho) if dissipator is not None else None

    labels = pauli_labels if pauli_labels is not None else all_pauli_labels(hamiltonian.n_qubits)
    pauli = decompose(rho, labels)
    pauli_velocity = decompose(rho_dot_unitary, labels)

    return QuantumFrame(
        frame_id=frame_id,
        state_epoch=state_epoch,
        t=t,
        dt=dt,
        basis_id=basis_id,
        generator_version=GENERATOR_VERSION,
        n_qubits=hamiltonian.n_qubits,
        rho=np.array(rho, copy=True),
        hamiltonian_matrix=H,
        rho_dot_unitary=rho_dot_unitary,
        rho_dot_dissipative=rho_dot_dissipative,
        diagnostics=diagnostics,
        pauli=pauli,
        pauli_velocity=pauli_velocity,
        commutator_norm=commutator_norm(H, rho),
        energy=float(np.trace(H @ rho).real),
        entropy=von_neumann_entropy(rho),
        projector_id=projector_id,
        event_discontinuity=event_discontinuity,
        source=source or {},
        metadata=metadata or {},
    )
