"""Backend contract for the dynamic I Ching density oracle."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class DensityBackend(ABC):
    """Small array seam shared by the NumPy and MLX implementations."""

    name: str
    complex_dtype: Any

    @abstractmethod
    def array(self, value: Any, dtype: Any | None = None) -> Any: ...

    @abstractmethod
    def zeros(self, shape: tuple[int, ...], dtype: Any | None = None) -> Any: ...

    @abstractmethod
    def eye(self, size: int, dtype: Any | None = None) -> Any: ...

    @abstractmethod
    def kron(self, left: Any, right: Any) -> Any: ...

    @abstractmethod
    def matmul(self, left: Any, right: Any) -> Any: ...

    @abstractmethod
    def trace(self, value: Any) -> Any: ...

    @abstractmethod
    def eigvalsh(self, value: Any) -> Any: ...

    @abstractmethod
    def eigh(self, value: Any) -> tuple[Any, Any]: ...

    @abstractmethod
    def conjugate_transpose(self, value: Any) -> Any: ...

    @abstractmethod
    def evaluate(self, *values: Any) -> None: ...

    @abstractmethod
    def to_numpy(self, value: Any) -> Any: ...

    def synchronize_frame(self, values: Iterable[Any]) -> None:
        """Materialize one complete diagnostic frame (one MLX eval barrier)."""
        self.evaluate(*tuple(values))


def create_backend(name: str, *, allow_fallback: bool = True) -> DensityBackend:
    normalized = name.lower()
    if normalized == "numpy":
        from qmw_density_backend_numpy import NumPyDensityBackend

        return NumPyDensityBackend()
    if normalized == "mlx":
        try:
            from qmw_density_backend_mlx import MLXDensityBackend

            return MLXDensityBackend()
        except (ImportError, RuntimeError):
            if not allow_fallback:
                raise
            from qmw_density_backend_numpy import NumPyDensityBackend

            backend = NumPyDensityBackend()
            backend.requested_name = "mlx"  # type: ignore[attr-defined]
            backend.fallback_reason = "MLX is unavailable; using NumPy"  # type: ignore[attr-defined]
            return backend
    raise ValueError(f"unknown density backend: {name!r}")
