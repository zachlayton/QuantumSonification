"""Apple-silicon MLX backend with complex64 storage and lazy frame evaluation."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import mlx.core as mx
except ImportError as exc:  # pragma: no cover - depends on host
    raise ImportError("MLX backend requires the optional 'mlx' package") from exc

from qmw_density_backend import DensityBackend


class MLXDensityBackend(DensityBackend):
    name = "mlx"
    complex_dtype = mx.complex64

    def __init__(self) -> None:
        if not hasattr(mx, "linalg"):
            raise RuntimeError("installed MLX lacks linear algebra support")

    def array(self, value: Any, dtype: Any | None = None) -> Any:
        return mx.array(value, dtype=dtype)

    def zeros(self, shape: tuple[int, ...], dtype: Any | None = None) -> Any:
        return mx.zeros(shape, dtype=dtype or self.complex_dtype)

    def eye(self, size: int, dtype: Any | None = None) -> Any:
        return mx.eye(size, dtype=dtype or self.complex_dtype)

    def kron(self, left: Any, right: Any) -> Any:
        return mx.kron(left, right)

    def matmul(self, left: Any, right: Any) -> Any:
        return mx.matmul(left, right)

    def trace(self, value: Any) -> Any:
        return mx.trace(value)

    def eigvalsh(self, value: Any) -> Any:
        return mx.linalg.eigvalsh(value)

    def eigh(self, value: Any) -> tuple[Any, Any]:
        return mx.linalg.eigh(value)

    def conjugate_transpose(self, value: Any) -> Any:
        return mx.conjugate(mx.transpose(value))

    def evaluate(self, *values: Any) -> None:
        if values:
            mx.eval(*values)

    def to_numpy(self, value: Any) -> np.ndarray:
        mx.eval(value)
        return np.asarray(value)
