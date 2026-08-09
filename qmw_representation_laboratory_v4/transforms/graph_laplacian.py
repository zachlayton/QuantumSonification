from typing import Any

import numpy as np

from ..core import TransformContext, UnitaryOperator, square_matrix
from ._spectral import eigenbasis


class GraphLaplacianBasis(UnitaryOperator):
    name = "graph_laplacian"
    description = "Graph-frequency basis ordered by Laplacian eigenvalue."

    def __init__(
        self,
        adjacency: Any,
        *,
        normalized: bool = False,
        graph_name: str = "custom",
    ) -> None:
        value = square_matrix(adjacency, name="adjacency")
        if np.max(np.abs(value.imag)) > 1e-10:
            raise ValueError("adjacency must be real")
        matrix = np.asarray(value.real, dtype=float)
        if not np.allclose(matrix, matrix.T, atol=1e-10, rtol=0.0):
            raise ValueError("adjacency must be symmetric")
        if np.any(matrix < -1e-10):
            raise ValueError("adjacency weights must be non-negative")
        if not np.allclose(np.diag(matrix), 0.0, atol=1e-10, rtol=0.0):
            raise ValueError("adjacency diagonal must be zero")
        matrix = np.maximum(matrix, 0.0)
        degrees = np.sum(matrix, axis=1)
        self.normalized = bool(normalized)
        self.graph_name = str(graph_name)
        if normalized:
            inverse = np.zeros_like(degrees)
            connected = degrees > 1e-12
            inverse[connected] = 1.0 / np.sqrt(degrees[connected])
            laplacian = np.eye(len(degrees)) - (
                inverse[:, None] * matrix * inverse[None, :]
            )
            laplacian[~connected, :] = 0.0
            laplacian[:, ~connected] = 0.0
        else:
            laplacian = np.diag(degrees) - matrix
        self._eigenvalues, vectors = eigenbasis(laplacian)
        self._adjacency = matrix
        self._laplacian = laplacian
        self._unitary = vectors.conj().T

    @property
    def adjacency(self) -> np.ndarray:
        return np.array(self._adjacency, copy=True)

    @property
    def laplacian(self) -> np.ndarray:
        return np.array(self._laplacian, copy=True)

    @property
    def eigenvalues(self) -> np.ndarray:
        return np.array(self._eigenvalues, copy=True)

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if self._unitary.shape != (dimension, dimension):
            raise ValueError(
                f"graph has {self._unitary.shape[0]} nodes, but the density "
                f"dimension is {dimension}"
            )
        return np.array(self._unitary, copy=True)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        zero_modes = int(np.count_nonzero(np.abs(self._eigenvalues) <= 1e-10))
        gap = max(0.0, float(self._eigenvalues[1])) if dimension > 1 else 0.0
        metadata.update(
            graph_name=self.graph_name,
            node_count=int(self._adjacency.shape[0]),
            edge_count=int(np.count_nonzero(self._adjacency) // 2),
            normalized=self.normalized,
            connected_components=zero_modes,
            spectral_gap=gap,
            eigenvalues=self._eigenvalues.tolist(),
        )
        return metadata


def path_graph_adjacency(node_count: int) -> np.ndarray:
    if node_count <= 0:
        raise ValueError("node_count must be positive")
    result = np.zeros((node_count, node_count), dtype=float)
    for node in range(node_count - 1):
        result[node, node + 1] = result[node + 1, node] = 1.0
    return result


def cycle_graph_adjacency(node_count: int) -> np.ndarray:
    if node_count < 3:
        raise ValueError("cycle graph requires at least three nodes")
    result = path_graph_adjacency(node_count)
    result[0, -1] = result[-1, 0] = 1.0
    return result


def complete_graph_adjacency(node_count: int) -> np.ndarray:
    if node_count <= 0:
        raise ValueError("node_count must be positive")
    return np.ones((node_count, node_count)) - np.eye(node_count)
