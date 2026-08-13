"""NumPy correctness-reference backend."""

from __future__ import annotations

from typing import Any

import numpy as np

from qmw_density_backend import DensityBackend


class NumPyDensityBackend(DensityBackend):
    name = "numpy"
    complex_dtype = np.complex128

    def array(self, value: Any, dtype: Any | None = None) -> np.ndarray:
        return np.asarray(value, dtype=dtype)

    def zeros(self, shape: tuple[int, ...], dtype: Any | None = None) -> np.ndarray:
        return np.zeros(shape, dtype=dtype or self.complex_dtype)

    def eye(self, size: int, dtype: Any | None = None) -> np.ndarray:
        return np.eye(size, dtype=dtype or self.complex_dtype)

    def kron(self, left: Any, right: Any) -> np.ndarray:
        return np.kron(left, right)

    def matmul(self, left: Any, right: Any) -> np.ndarray:
        return np.matmul(left, right)

    def trace(self, value: Any) -> Any:
        return np.trace(value)

    def eigvalsh(self, value: Any) -> np.ndarray:
        return np.linalg.eigvalsh(value)

    def eigh(self, value: Any) -> tuple[np.ndarray, np.ndarray]:
        return np.linalg.eigh(value)

    def conjugate_transpose(self, value: Any) -> np.ndarray:
        return np.asarray(value).conj().T

    def evaluate(self, *values: Any) -> None:
        return None

    def to_numpy(self, value: Any) -> np.ndarray:
        return np.asarray(value)
