"""Read-only four-qubit connected-correlation geometry observer for V3.

This module observes one sealed :class:`~qmw.quantum.dynamics.QuantumFrame`.
It never evolves or mutates ``rho``.  The distance, graph, and tetrahedral
embedding are explicitly declared derived-model operations, not physical
spacetime reconstruction or Loop Quantum Gravity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from qmw.quantum.dynamics import QuantumFrame
from qmw.quantum.pauli_basis import pauli_matrix

from .frames import QUBIT_COUNT, RELATIONAL_EDGE_PAIRS, RelationalGeometryFrame


_AXES = ("X", "Y", "Z")


@dataclass(frozen=True)
class RelationalGeometryConfig:
    """Declared numerical policy for the V3 relational geometry observer.

    ``strength_reference`` sets the dimensionless scale of the monotone map
    ``w = strength / (strength_reference + strength)``.  Link distance is
    ``maximum_distance - (maximum_distance - minimum_distance) * w``: strong
    connected correlation means shorter distance, with no singularity.
    """

    minimum_distance: float = 0.35
    maximum_distance: float = 2.0
    strength_reference: float = 1.0
    embedding_tolerance: float = 1.0e-8
    node_ids: tuple[str, ...] = ("q0", "q1", "q2", "q3")

    def __post_init__(self) -> None:
        values = (float(self.minimum_distance), float(self.maximum_distance), float(self.strength_reference), float(self.embedding_tolerance))
        if not all(math.isfinite(value) for value in values):
            raise ValueError("relational geometry configuration values must be finite.")
        if not 0.0 < values[0] < values[1]:
            raise ValueError("minimum_distance must be positive and less than maximum_distance.")
        if values[2] <= 0.0 or values[3] <= 0.0:
            raise ValueError("strength_reference and embedding_tolerance must be positive.")
        if len(self.node_ids) != QUBIT_COUNT or len(set(self.node_ids)) != QUBIT_COUNT or any(not str(value) for value in self.node_ids):
            raise ValueError("node_ids must contain four unique nonempty identifiers.")


def _expectation(frame: QuantumFrame, label: str) -> float:
    value = complex(np.trace(frame.rho @ pauli_matrix(label)))
    if abs(value.imag) > 1.0e-9:
        raise ValueError("a Hermitian Pauli expectation was unexpectedly complex.")
    return float(value.real)


def _single_label(qubit: int, axis: str) -> str:
    labels = ["I"] * QUBIT_COUNT
    labels[qubit] = axis
    return "".join(labels)


def _pair_label(left: int, right: int, left_axis: str, right_axis: str) -> str:
    labels = ["I"] * QUBIT_COUNT
    labels[left], labels[right] = left_axis, right_axis
    return "".join(labels)


def connected_pauli_correlation_tensors(frame: QuantumFrame) -> np.ndarray:
    """Return canonical six connected 3x3 pair-correlation tensors.

    This is a read-only observable of the supplied native four-qubit density
    matrix.  It does not use raw local phase as a geometry coordinate.
    """

    if not isinstance(frame, QuantumFrame):
        raise TypeError("frame must be a sealed QuantumFrame.")
    if frame.hamiltonian.dimension != 16 or frame.rho.shape != (16, 16):
        raise ValueError("V3 relational geometry requires a native four-qubit QuantumFrame; no padding is permitted.")
    local = np.array([[_expectation(frame, _single_label(qubit, axis)) for axis in _AXES] for qubit in range(QUBIT_COUNT)])
    tensors = np.empty((len(RELATIONAL_EDGE_PAIRS), 3, 3), dtype=float)
    for edge, (left, right) in enumerate(RELATIONAL_EDGE_PAIRS):
        for row, left_axis in enumerate(_AXES):
            for column, right_axis in enumerate(_AXES):
                tensors[edge, row, column] = (
                    _expectation(frame, _pair_label(left, right, left_axis, right_axis))
                    - (local[left, row] * local[right, column])
                )
    tensors.flags.writeable = False
    return tensors


def _distances_from_strength(strength: np.ndarray, config: RelationalGeometryConfig) -> tuple[np.ndarray, np.ndarray]:
    weights = strength / (float(config.strength_reference) + strength)
    lengths = float(config.maximum_distance) - ((float(config.maximum_distance) - float(config.minimum_distance)) * weights)
    adjacency = np.zeros((QUBIT_COUNT, QUBIT_COUNT), dtype=float)
    distances = np.zeros((QUBIT_COUNT, QUBIT_COUNT), dtype=float)
    for weight, length, (left, right) in zip(weights, lengths, RELATIONAL_EDGE_PAIRS):
        adjacency[left, right] = adjacency[right, left] = weight
        distances[left, right] = distances[right, left] = length
    return adjacency, distances


def _best_fit_embedding(distances: np.ndarray) -> np.ndarray:
    """Return a deterministic centred 3-D classical-MDS best fit."""

    count = distances.shape[0]
    centre = np.eye(count) - (np.ones((count, count)) / count)
    gram = -0.5 * centre @ (distances * distances) @ centre
    values, vectors = np.linalg.eigh((gram + gram.T) * 0.5)
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    positive = np.maximum(values[:3], 0.0)
    return vectors[:, :3] * np.sqrt(positive)


def _tetrahedral_embedding(distances: np.ndarray, tolerance: float) -> tuple[np.ndarray, bool, tuple[str, ...]]:
    """Embed the ordered tetrahedron, reporting invalid metrics without coercion."""

    d01, d02, d03 = distances[0, 1], distances[0, 2], distances[0, 3]
    d12, d13, d23 = distances[1, 2], distances[1, 3], distances[2, 3]
    x2 = ((d02 * d02) + (d01 * d01) - (d12 * d12)) / (2.0 * d01)
    y2_squared = (d02 * d02) - (x2 * x2)
    if y2_squared < -tolerance:
        return _best_fit_embedding(distances), False, ("tetrahedron_not_realizable: first face violates triangle inequality",)
    y2 = math.sqrt(max(0.0, y2_squared))
    if y2 <= tolerance:
        return _best_fit_embedding(distances), False, ("tetrahedron_not_realizable: first face is degenerate",)
    x3 = ((d03 * d03) + (d01 * d01) - (d13 * d13)) / (2.0 * d01)
    y3 = (((d03 * d03) - (d23 * d23) + (d02 * d02)) / 2.0 - (x2 * x3)) / y2
    z3_squared = (d03 * d03) - (x3 * x3) - (y3 * y3)
    if z3_squared < -tolerance:
        return _best_fit_embedding(distances), False, ("tetrahedron_not_realizable: Cayley-Menger volume is negative",)
    vertices = np.array(((0.0, 0.0, 0.0), (d01, 0.0, 0.0), (x2, y2, 0.0), (x3, y3, math.sqrt(max(0.0, z3_squared)))))
    residual = float(np.max(np.abs(np.linalg.norm(vertices[:, None, :] - vertices[None, :, :], axis=-1) - distances)))
    if residual > tolerance:
        return _best_fit_embedding(distances), False, (f"tetrahedron_not_realizable: embedding residual {residual:.3e}",)
    return vertices, True, ()


def _face_areas_and_volume(vertices: np.ndarray) -> tuple[np.ndarray, float]:
    areas = np.empty(QUBIT_COUNT, dtype=float)
    for omitted in range(QUBIT_COUNT):
        indices = [index for index in range(QUBIT_COUNT) if index != omitted]
        first, second, third = vertices[indices]
        areas[omitted] = 0.5 * np.linalg.norm(np.cross(second - first, third - first))
    volume = abs(float(np.linalg.det(np.stack((vertices[1] - vertices[0], vertices[2] - vertices[0], vertices[3] - vertices[0]))))) / 6.0
    return areas, volume


def observe_relational_geometry(
    frame: QuantumFrame,
    *,
    config: RelationalGeometryConfig | None = None,
) -> RelationalGeometryFrame:
    """Observe one immutable V3 relational geometry from a sealed frame."""

    cfg = config or RelationalGeometryConfig()
    tensors = connected_pauli_correlation_tensors(frame)
    strength = np.linalg.norm(tensors, axis=(1, 2))
    adjacency, distances = _distances_from_strength(strength, cfg)
    vertices, embedding_valid, diagnostics = _tetrahedral_embedding(distances, cfg.embedding_tolerance)
    areas, volume = _face_areas_and_volume(vertices)
    laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    return RelationalGeometryFrame(
        revision=frame.frame_index,
        time=frame.time,
        quantum_revision=frame.frame_index,
        node_ids=cfg.node_ids,
        edge_pairs=RELATIONAL_EDGE_PAIRS,
        connected_correlation_tensors=tensors,
        link_strength=strength,
        adjacency=adjacency,
        distances=distances,
        vertices=vertices,
        face_area=areas,
        volume=volume,
        laplacian=laplacian,
        eigenvalues=np.maximum(eigenvalues, 0.0),
        eigenvectors=eigenvectors,
        embedding_valid=embedding_valid,
        diagnostics=diagnostics,
    )


__all__ = [
    "RelationalGeometryConfig", "connected_pauli_correlation_tensors",
    "observe_relational_geometry",
]
