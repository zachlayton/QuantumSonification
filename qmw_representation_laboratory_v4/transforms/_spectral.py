"""Deterministic eigenspace helpers shared by spectral transforms."""

from __future__ import annotations

import numpy as np


def canonicalize_eigenspaces(
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    *,
    tolerance: float = 1e-9,
) -> np.ndarray:
    vectors = np.asarray(eigenvectors, dtype=complex)
    result = np.zeros_like(vectors)
    dimension = vectors.shape[0]
    start = 0
    while start < len(eigenvalues):
        stop = start + 1
        while (
            stop < len(eigenvalues)
            and abs(eigenvalues[stop] - eigenvalues[start]) <= tolerance
        ):
            stop += 1
        width = stop - start
        if width == 1:
            result[:, start] = vectors[:, start]
        else:
            projector = (
                vectors[:, start:stop] @ vectors[:, start:stop].conj().T
            )
            selected: list[np.ndarray] = []
            for coordinate in range(dimension):
                candidate = np.array(projector[:, coordinate], copy=True)
                for previous in selected:
                    candidate -= previous * np.vdot(previous, candidate)
                norm = float(np.linalg.norm(candidate))
                if norm > tolerance:
                    selected.append(candidate / norm)
                if len(selected) == width:
                    break
            if len(selected) != width:
                raise ValueError("could not stabilize a degenerate eigenspace")
            result[:, start:stop] = np.column_stack(selected)
        start = stop
    for column in range(result.shape[1]):
        pivot = int(np.argmax(np.abs(result[:, column])))
        if abs(result[pivot, column]) > 0.0:
            result[:, column] *= np.exp(
                -1j * np.angle(result[pivot, column])
            )
    return result


def eigenbasis(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    vectors = canonicalize_eigenspaces(eigenvalues, eigenvectors)
    return np.asarray(eigenvalues, dtype=float), vectors
