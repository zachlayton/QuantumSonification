"""State preparation for two truncated bosonic modes."""

from __future__ import annotations

import numpy as np

from .states import coherent_state, density_matrix, fock_state


def product_state(state_a: np.ndarray, state_b: np.ndarray) -> np.ndarray:
    """Return a tensor-product ket when possible, otherwise a density matrix."""

    value_a = np.asarray(state_a, dtype=np.complex128)
    value_b = np.asarray(state_b, dtype=np.complex128)
    if value_a.ndim == 1 and value_b.ndim == 1:
        norm_a = np.linalg.norm(value_a)
        norm_b = np.linalg.norm(value_b)
        if norm_a == 0.0 or norm_b == 0.0:
            raise ValueError("product-state factors must have nonzero norm")
        return np.kron(value_a / norm_a, value_b / norm_b)
    return np.kron(density_matrix(value_a), density_matrix(value_b))


def product_fock_state(
    n_a: int,
    n_b: int,
    dimension_a: int = 4,
    dimension_b: int = 4,
) -> np.ndarray:
    return product_state(
        fock_state(n_a, dimension_a),
        fock_state(n_b, dimension_b),
    )


def product_coherent_state(
    alpha_a: complex,
    alpha_b: complex,
    dimension_a: int = 4,
    dimension_b: int = 4,
) -> np.ndarray:
    return product_state(
        coherent_state(alpha_a, dimension_a),
        coherent_state(alpha_b, dimension_b),
    )


__all__ = ["product_coherent_state", "product_fock_state", "product_state"]
