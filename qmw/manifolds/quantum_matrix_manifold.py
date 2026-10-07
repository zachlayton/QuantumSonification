"""First-class 4-qubit Quantum Matrix Manifold."""

from __future__ import annotations

from typing import Any, Optional, Sequence

import numpy as np

from qmw.fields.quantum_matrix_field import QuantumMatrixField
from qmw.frames.manifold_frame import ManifoldFrame
from qmw.manifolds.basis_path import BasisPath
from qmw.manifolds.interpolation_types import InterpolationType
from qmw.manifolds.manifold_gradient import ManifoldGradient
from qmw.manifolds.manifold_sampler import BoundaryMode, ManifoldSampler
from qmw.transforms.manifold_spectral_transform import (
    ManifoldSpectralTransform,
    SpectralTransformType,
)


N_QUBITS = 4
DIMENSION = 2**N_QUBITS
BUFFER_SIZE = DIMENSION**2


def _matrix16(name: str, matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    if value.shape != (DIMENSION, DIMENSION):
        raise ValueError(
            f"{name} must have shape {(DIMENSION, DIMENSION)} for four qubits, "
            f"got {value.shape}"
        )
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} contains non-finite values")
    return value.copy()


def _vector16(name: str, values: np.ndarray, *, real: bool = False) -> np.ndarray:
    dtype = float if real else np.complex128
    value = np.asarray(values, dtype=dtype)
    if value.shape != (DIMENSION,):
        raise ValueError(f"{name} must have shape {(DIMENSION,)}, got {value.shape}")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} contains non-finite values")
    return value.copy()


def _hermiticity_error(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix - matrix.conj().T, ord="fro"))


class QuantumMatrixManifold:
    """Continuous field ``M(m, n, eta)`` for a four-qubit QMW system.

    Calling the constructor directly selects basis interpolation. Use the named
    constructors for state, eigenvalue, or eigenvector interpolation so the
    mathematical meaning is explicit at the call site.
    """

    def __init__(
        self,
        matrix: np.ndarray,
        source_basis: np.ndarray,
        target_basis: np.ndarray,
        *,
        source_basis_name: str = "source",
        target_basis_name: str = "target",
        branch_shifts: Optional[Sequence[int]] = None,
        sampler_boundary: BoundaryMode | str = BoundaryMode.CLAMP,
    ) -> None:
        self._interpolation_type = InterpolationType.BASIS
        self._matrix = _matrix16("matrix", matrix)
        self._basis_path = BasisPath(
            _matrix16("source_basis", source_basis),
            _matrix16("target_basis", target_basis),
            branch_shifts=branch_shifts,
        )
        self._source_matrix = None
        self._target_matrix = None
        self._source_eigenvalues = None
        self._target_eigenvalues = None
        self._fixed_eigenvectors = None
        self._eigenvalues = None
        self._source_basis_name = str(source_basis_name)
        self._target_basis_name = str(target_basis_name)
        self._sampler = ManifoldSampler(sampler_boundary)
        self._spectral = ManifoldSpectralTransform()

    @classmethod
    def _empty(
        cls,
        interpolation_type: InterpolationType,
        source_basis_name: str,
        target_basis_name: str,
        sampler_boundary: BoundaryMode | str,
    ) -> "QuantumMatrixManifold":
        instance = cls.__new__(cls)
        instance._interpolation_type = interpolation_type
        instance._matrix = None
        instance._basis_path = None
        instance._source_matrix = None
        instance._target_matrix = None
        instance._source_eigenvalues = None
        instance._target_eigenvalues = None
        instance._fixed_eigenvectors = None
        instance._eigenvalues = None
        instance._source_basis_name = str(source_basis_name)
        instance._target_basis_name = str(target_basis_name)
        instance._sampler = ManifoldSampler(sampler_boundary)
        instance._spectral = ManifoldSpectralTransform()
        return instance

    @classmethod
    def from_state_endpoints(
        cls,
        source_matrix: np.ndarray,
        target_matrix: np.ndarray,
        *,
        source_name: str = "source_state",
        target_name: str = "target_state",
        sampler_boundary: BoundaryMode | str = BoundaryMode.CLAMP,
    ) -> "QuantumMatrixManifold":
        """Affinely mix two states: ``(1-eta) M0 + eta M1``.

        This is not a basis change. Trace is preserved only when endpoint traces
        agree; eigenvalues generally vary. Positive semidefiniteness is
        preserved when both endpoints are positive semidefinite.
        """
        instance = cls._empty(
            InterpolationType.STATE, source_name, target_name, sampler_boundary
        )
        instance._source_matrix = _matrix16("source_matrix", source_matrix)
        instance._target_matrix = _matrix16("target_matrix", target_matrix)
        return instance

    @classmethod
    def from_eigenvalue_endpoints(
        cls,
        source_eigenvalues: np.ndarray,
        target_eigenvalues: np.ndarray,
        eigenvectors: np.ndarray,
        *,
        basis_name: str = "fixed_eigenbasis",
        sampler_boundary: BoundaryMode | str = BoundaryMode.CLAMP,
    ) -> "QuantumMatrixManifold":
        """Interpolate ordered real eigenvalues in one fixed eigenbasis."""
        instance = cls._empty(
            InterpolationType.EIGENVALUES,
            basis_name,
            basis_name,
            sampler_boundary,
        )
        instance._source_eigenvalues = _vector16(
            "source_eigenvalues", source_eigenvalues, real=True
        )
        instance._target_eigenvalues = _vector16(
            "target_eigenvalues", target_eigenvalues, real=True
        )
        fixed = _matrix16("eigenvectors", eigenvectors)
        error = np.linalg.norm(fixed.conj().T @ fixed - np.eye(DIMENSION), ord="fro")
        if error > 1e-9:
            raise ValueError(f"eigenvectors must be unitary, error {error:.3e}")
        instance._fixed_eigenvectors = fixed
        return instance

    @classmethod
    def from_eigenvector_path(
        cls,
        eigenvalues: np.ndarray,
        source_eigenvectors: np.ndarray,
        target_eigenvectors: np.ndarray,
        *,
        source_name: str = "source_eigenvectors",
        target_name: str = "target_eigenvectors",
        branch_shifts: Optional[Sequence[int]] = None,
        sampler_boundary: BoundaryMode | str = BoundaryMode.CLAMP,
    ) -> "QuantumMatrixManifold":
        """Reconstruct a fixed real spectrum in a moving eigenframe.

        ``M(eta) = V(eta) diag(eigenvalues) V(eta)^dagger``. This differs from
        basis interpolation, which re-expresses one fixed laboratory operator
        as ``U(eta)^dagger M U(eta)``.
        """
        instance = cls._empty(
            InterpolationType.EIGENVECTORS,
            source_name,
            target_name,
            sampler_boundary,
        )
        instance._eigenvalues = _vector16("eigenvalues", eigenvalues, real=True)
        instance._basis_path = BasisPath(
            _matrix16("source_eigenvectors", source_eigenvectors),
            _matrix16("target_eigenvectors", target_eigenvectors),
            branch_shifts=branch_shifts,
        )
        return instance

    @staticmethod
    def _eta(eta: float) -> float:
        value = float(eta)
        if not np.isfinite(value) or value < 0.0 or value > 1.0:
            raise ValueError(f"eta must be finite and in [0, 1], got {eta!r}")
        return value

    @property
    def interpolation_type(self) -> InterpolationType:
        return self._interpolation_type

    @property
    def dimension(self) -> int:
        return DIMENSION

    @property
    def buffer_size(self) -> int:
        return BUFFER_SIZE

    @property
    def basis_path(self) -> BasisPath | None:
        return self._basis_path

    def matrix_at(self, eta: float) -> np.ndarray:
        value = self._eta(eta)
        kind = self._interpolation_type

        if kind is InterpolationType.BASIS:
            assert self._basis_path is not None and self._matrix is not None
            unitary = self._basis_path.unitary_at(value)
            result = unitary.conj().T @ self._matrix @ unitary
        elif kind is InterpolationType.STATE:
            assert self._source_matrix is not None and self._target_matrix is not None
            if value == 0.0:
                return self._source_matrix.copy()
            if value == 1.0:
                return self._target_matrix.copy()
            result = (1.0 - value) * self._source_matrix + value * self._target_matrix
        elif kind is InterpolationType.EIGENVALUES:
            assert self._source_eigenvalues is not None
            assert self._target_eigenvalues is not None
            assert self._fixed_eigenvectors is not None
            eigenvalues = (
                (1.0 - value) * self._source_eigenvalues
                + value * self._target_eigenvalues
            )
            result = (
                self._fixed_eigenvectors
                @ np.diag(eigenvalues)
                @ self._fixed_eigenvectors.conj().T
            )
        else:
            assert self._basis_path is not None and self._eigenvalues is not None
            eigenvectors = self._basis_path.unitary_at(value)
            result = eigenvectors @ np.diag(self._eigenvalues) @ eigenvectors.conj().T
        return np.array(result, dtype=np.complex128, copy=True)

    def derivative_at(self, eta: float) -> np.ndarray:
        """Return the analytic matrix derivative ``dM/deta``."""
        value = self._eta(eta)
        kind = self._interpolation_type

        if kind is InterpolationType.BASIS:
            assert self._basis_path is not None
            current = self.matrix_at(value)
            generator = self._basis_path.generator
            result = current @ generator - generator @ current
        elif kind is InterpolationType.STATE:
            assert self._source_matrix is not None and self._target_matrix is not None
            result = self._target_matrix - self._source_matrix
        elif kind is InterpolationType.EIGENVALUES:
            assert self._source_eigenvalues is not None
            assert self._target_eigenvalues is not None
            assert self._fixed_eigenvectors is not None
            delta = self._target_eigenvalues - self._source_eigenvalues
            result = (
                self._fixed_eigenvectors
                @ np.diag(delta)
                @ self._fixed_eigenvectors.conj().T
            )
        else:
            assert self._basis_path is not None and self._eigenvalues is not None
            vectors = self._basis_path.unitary_at(value)
            derivative = self._basis_path.derivative_at(value)
            diagonal = np.diag(self._eigenvalues)
            result = (
                derivative @ diagonal @ vectors.conj().T
                + vectors @ diagonal @ derivative.conj().T
            )
        return np.array(result, dtype=np.complex128, copy=True)

    def field_at(self, eta: float) -> QuantumMatrixField:
        return QuantumMatrixField(
            self.matrix_at(eta),
            eta=float(eta),
            metadata={"interpolation_type": self._interpolation_type.value},
        )

    def sample(self, m: float, n: float, eta: float) -> complex:
        return self._sampler.sample(self.matrix_at(eta), m, n)

    def gradient(self, m: float, n: float, eta: float) -> ManifoldGradient:
        matrix = self.matrix_at(eta)
        gradient_m, gradient_n = self._sampler.spatial_gradient(matrix, m, n)
        gradient_eta = self._sampler.sample(self.derivative_at(eta), m, n)
        return ManifoldGradient(m=gradient_m, n=gradient_n, eta=gradient_eta)

    def flatten_at(self, eta: float) -> np.ndarray:
        return QuantumMatrixField.flatten(self.matrix_at(eta))

    @staticmethod
    def flatten(matrix: np.ndarray) -> np.ndarray:
        value = _matrix16("matrix", matrix)
        return QuantumMatrixField.flatten(value)

    @staticmethod
    def unflatten(buffer: np.ndarray) -> np.ndarray:
        return QuantumMatrixField.unflatten(buffer, dimension=DIMENSION).astype(
            np.complex128, copy=False
        )

    def magnitude_at(self, eta: float) -> np.ndarray:
        return np.abs(self.matrix_at(eta))

    def phase_at(self, eta: float) -> np.ndarray:
        return np.angle(self.matrix_at(eta))

    def spectrum_at(
        self,
        eta: float,
        kind: SpectralTransformType | str = SpectralTransformType.FFT2,
    ) -> np.ndarray:
        return self._spectral.transform(self.matrix_at(eta), kind=kind)

    def diagnostics_at(self, eta: float) -> dict[str, Any]:
        matrix = self.matrix_at(eta)
        trace = np.trace(matrix)
        diagnostics: dict[str, Any] = {
            "interpolation_type": self._interpolation_type.value,
            "dimension": DIMENSION,
            "buffer_size": BUFFER_SIZE,
            "trace_real": float(trace.real),
            "trace_imag": float(trace.imag),
            "hermiticity_error": _hermiticity_error(matrix),
            "frobenius_norm": float(np.linalg.norm(matrix, ord="fro")),
        }
        if self._basis_path is not None:
            diagnostics["basis_path"] = self._basis_path.diagnostics.as_dict()
            diagnostics["path_at_eta"] = dict(self._basis_path.diagnostics_at(eta))
        return diagnostics

    def frame_at(
        self,
        eta: float,
        *,
        spectrum_kind: SpectralTransformType | str = SpectralTransformType.FFT2,
    ) -> ManifoldFrame:
        value = self._eta(eta)
        matrix = self.matrix_at(value)
        gradient_m, gradient_n = np.gradient(matrix, axis=(0, 1), edge_order=2)
        gradient_eta = self.derivative_at(value)
        return ManifoldFrame(
            eta=value,
            matrix=matrix,
            magnitude=np.abs(matrix),
            phase=np.angle(matrix),
            buffer_256=QuantumMatrixField.flatten(matrix),
            spectrum=self._spectral.transform(matrix, kind=spectrum_kind),
            gradient_m=gradient_m,
            gradient_n=gradient_n,
            gradient_eta=gradient_eta,
            source_basis_name=self._source_basis_name,
            target_basis_name=self._target_basis_name,
            diagnostics=self.diagnostics_at(value),
        )

