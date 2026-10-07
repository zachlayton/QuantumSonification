"""Canonical computational, Pauli, and geometric projector banks."""

from __future__ import annotations

import numpy as np

from qmw.quantum.pauli_basis import pauli_matrix
from .projector import ProjectorBank, ProjectorSpec


def computational_projector_bank(dimension: int = 16) -> ProjectorBank:
    if int(dimension) != dimension or dimension < 2:
        raise ValueError("dimension must be an integer of at least two.")
    width = max(1, int(np.ceil(np.log2(dimension))))
    projectors = []
    for index in range(int(dimension)):
        matrix = np.zeros((dimension, dimension), dtype=np.complex128)
        matrix[index, index] = 1.0
        projectors.append(ProjectorSpec(
            name=f"|{index:0{width}b}><{index:0{width}b}|",
            matrix=matrix, family="computational", rank=1,
            metadata={"basis_index": index},
        ))
    return ProjectorBank(
        f"computational_{dimension}", projectors, complete=True, orthogonal=True,
    )


def pauli_projector_bank(label: str) -> ProjectorBank:
    observable = pauli_matrix(label.upper())
    identity = np.eye(observable.shape[0], dtype=np.complex128)
    normalized = label.upper()
    return ProjectorBank(
        f"pauli_{normalized}",
        (
            ProjectorSpec(f"{normalized}+", (identity + observable) * 0.5, "pauli", metadata={"eigenvalue": 1}),
            ProjectorSpec(f"{normalized}-", (identity - observable) * 0.5, "pauli", metadata={"eigenvalue": -1}),
        ),
        complete=True, orthogonal=True,
    )


def pauli_eigenbasis_projector_bank(label: str) -> ProjectorBank:
    """Return a deterministic rank-one PVM refining a Pauli +/- measurement."""

    normalized = label.upper()
    observable = pauli_matrix(normalized)
    root_two = np.sqrt(2.0)
    local_bases = {
        "I": np.eye(2, dtype=np.complex128),
        "Z": np.eye(2, dtype=np.complex128),
        "X": np.array(((1.0, 1.0), (1.0, -1.0)), dtype=np.complex128) / root_two,
        "Y": np.array(((1.0, 1.0), (1.0j, -1.0j)), dtype=np.complex128) / root_two,
    }
    basis = np.ones((1, 1), dtype=np.complex128)
    for symbol in normalized:
        basis = np.kron(basis, local_bases[symbol])
    eigenvalues = np.asarray([
        np.real(basis[:, index].conj() @ observable @ basis[:, index])
        for index in range(basis.shape[1])
    ])
    bank = transform_projector_bank(
        computational_projector_bank(observable.shape[0]), basis,
        identifier=f"pauli_eigenbasis_{normalized}",
    )
    projectors = tuple(ProjectorSpec(
        name=f"{normalized}:{index:02d}:{'+' if eigenvalues[index] > 0 else '-'}",
        matrix=item.matrix, family="pauli_eigenbasis", rank=1,
        metadata={"observable": normalized, "eigenvalue": int(np.sign(eigenvalues[index]))},
    ) for index, item in enumerate(bank.projectors))
    return ProjectorBank(bank.identifier, projectors, complete=True, orthogonal=True)


def hypercube_geometry_projector_bank(qubits: int = 4) -> ProjectorBank:
    """Rank-one PVM for the Walsh modes of the declared Q_n state graph."""

    if int(qubits) != qubits or qubits < 1:
        raise ValueError("qubits must be a positive integer.")
    single = np.array(((1.0, 1.0), (1.0, -1.0))) / np.sqrt(2.0)
    basis = single
    for _ in range(int(qubits) - 1):
        basis = np.kron(basis, single)
    bank = geometry_projector_bank(basis, identifier=f"hypercube_q{int(qubits)}_walsh_geometry")
    projectors = tuple(ProjectorSpec(
        name=f"Q{int(qubits)}:Walsh:{index:02d}", matrix=item.matrix,
        family="configuration_graph_geometry", rank=1,
        metadata={"geometry": f"{int(qubits)}-hypercube", "walsh_mode": index},
    ) for index, item in enumerate(bank.projectors))
    return ProjectorBank(bank.identifier, projectors, complete=True, orthogonal=True)


def _unitary(values: object, dimension: int | None = None) -> np.ndarray:
    unitary = np.asarray(values, dtype=np.complex128)
    if unitary.ndim != 2 or unitary.shape[0] != unitary.shape[1] or not np.all(np.isfinite(unitary)):
        raise ValueError("basis must be a finite square unitary matrix.")
    if dimension is not None and unitary.shape != (dimension, dimension):
        raise ValueError("basis unitary has the wrong dimension.")
    if not np.allclose(unitary.conj().T @ unitary, np.eye(unitary.shape[0]), rtol=0.0, atol=1.0e-9):
        raise ValueError("basis must be unitary.")
    return unitary


def transform_projector_bank(bank: ProjectorBank, unitary: object, *, identifier: str | None = None) -> ProjectorBank:
    basis = _unitary(unitary, bank.dimension)
    transformed = tuple(ProjectorSpec(
        item.name,
        basis @ item.matrix @ basis.conj().T,
        item.family,
        item.rank,
        item.metadata,
    ) for item in bank.projectors)
    return ProjectorBank(identifier or bank.identifier, transformed, bank.complete, bank.orthogonal)


def geometry_projector_bank(basis: object, *, identifier: str = "geometry_modes") -> ProjectorBank:
    unitary = _unitary(basis)
    return transform_projector_bank(
        computational_projector_bank(unitary.shape[0]), unitary, identifier=identifier,
    )


__all__ = [
    "computational_projector_bank", "geometry_projector_bank",
    "hypercube_geometry_projector_bank", "pauli_eigenbasis_projector_bank",
    "pauli_projector_bank", "transform_projector_bank",
]
