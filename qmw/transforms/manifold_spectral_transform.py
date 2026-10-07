"""Read-only spectral views of a quantum matrix manifold slice."""

from __future__ import annotations

from enum import Enum

import numpy as np


class SpectralTransformType(str, Enum):
    FFT2 = "fft2"
    QFT_BASIS = "qft_basis"
    EIGENVALUES = "eigenvalues"


def qft_matrix(dimension: int = 16) -> np.ndarray:
    """Return the positive-phase normalized discrete quantum Fourier matrix."""
    n = int(dimension)
    if n <= 0:
        raise ValueError("dimension must be positive")
    indices = np.arange(n)
    return np.exp(2j * np.pi * np.outer(indices, indices) / n) / np.sqrt(n)


class ManifoldSpectralTransform:
    """Pure transforms: inputs are never mutated and outputs never alias them."""

    @staticmethod
    def _matrix(matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=np.complex128)
        if value.ndim != 2 or value.shape[0] != value.shape[1]:
            raise ValueError(f"matrix must be square, got {value.shape}")
        return value

    @classmethod
    def fft2(
        cls, matrix: np.ndarray, *, norm: str = "ortho", shift: bool = False
    ) -> np.ndarray:
        value = cls._matrix(matrix)
        transformed = np.fft.fft2(value, norm=norm)
        if shift:
            transformed = np.fft.fftshift(transformed)
        return np.array(transformed, dtype=np.complex128, copy=True)

    @classmethod
    def qft_basis_view(cls, matrix: np.ndarray) -> np.ndarray:
        """Represent an operator in the QFT basis as ``F^dagger M F``."""
        value = cls._matrix(matrix)
        fourier = qft_matrix(value.shape[0])
        return np.array(fourier.conj().T @ value @ fourier, copy=True)

    @classmethod
    def eigenvalues(cls, matrix: np.ndarray) -> np.ndarray:
        value = cls._matrix(matrix)
        if np.allclose(value, value.conj().T, atol=1e-10, rtol=1e-10):
            return np.linalg.eigvalsh(value).astype(np.complex128)
        return np.linalg.eigvals(value).astype(np.complex128)

    @classmethod
    def transform(
        cls,
        matrix: np.ndarray,
        kind: SpectralTransformType | str = SpectralTransformType.FFT2,
    ) -> np.ndarray:
        transform_type = SpectralTransformType(kind)
        if transform_type is SpectralTransformType.FFT2:
            return cls.fft2(matrix)
        if transform_type is SpectralTransformType.QFT_BASIS:
            return cls.qft_basis_view(matrix)
        return cls.eigenvalues(matrix)

