"""Unitary-preserving paths between matrix bases."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional, Sequence

import numpy as np
from scipy.linalg import expm, schur

from qmw.manifolds.interpolation_types import BranchConvention


def _frobenius_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def _unitarity_error(matrix: np.ndarray) -> float:
    identity = np.eye(matrix.shape[0], dtype=np.complex128)
    return _frobenius_norm(matrix.conj().T @ matrix - identity)


def _validate_square(name: str, matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be a square matrix, got {value.shape}")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} contains non-finite values")
    return value.copy()


@dataclass(frozen=True)
class BasisPathDiagnostics:
    dimension: int
    source_unitarity_error: float
    target_unitarity_error: float
    relative_unitarity_error: float
    schur_off_diagonal_norm: float
    generator_skew_hermitian_error: float
    endpoint_error: float
    minimum_branch_cut_distance: float
    near_branch_cut_count: int
    branch_convention: str
    phase_min: float
    phase_max: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class BasisPath:
    """Geodesic-like unitary path ``U0 exp(eta K)``.

    The relative unitary is reduced with a complex Schur decomposition. Its
    phases define a skew-Hermitian logarithm without applying a general-purpose
    logarithm to an almost-unitary matrix. Eigenvalues close to -1 remain a
    genuine branch choice; diagnostics expose that condition and integer
    ``branch_shifts`` allow an explicit alternative path.
    """

    def __init__(
        self,
        source_basis: np.ndarray,
        target_basis: np.ndarray,
        *,
        branch_shifts: Optional[Sequence[int]] = None,
        unitarity_tolerance: float = 1e-9,
        endpoint_tolerance: float = 1e-8,
        branch_cut_tolerance: float = 1e-7,
    ) -> None:
        source = _validate_square("source_basis", source_basis)
        target = _validate_square("target_basis", target_basis)
        if source.shape != target.shape:
            raise ValueError(
                f"basis shapes must agree, got {source.shape} and {target.shape}"
            )

        source_error = _unitarity_error(source)
        target_error = _unitarity_error(target)
        if source_error > unitarity_tolerance:
            raise ValueError(
                f"source_basis is not unitary: Frobenius error {source_error:.3e}"
            )
        if target_error > unitarity_tolerance:
            raise ValueError(
                f"target_basis is not unitary: Frobenius error {target_error:.3e}"
            )

        relative = source.conj().T @ target
        relative_error = _unitarity_error(relative)
        triangular, schur_vectors = schur(relative, output="complex")
        diagonal = np.diag(triangular)
        magnitudes = np.abs(diagonal)
        if np.any(magnitudes < 1e-14):
            raise ValueError("relative unitary has a numerically zero Schur eigenvalue")
        eigenvalues = diagonal / magnitudes

        phases = np.angle(eigenvalues)
        # Make the exact negative-real case deterministic: choose +pi, not -pi.
        phases = np.where(
            np.isclose(phases, -np.pi, atol=branch_cut_tolerance, rtol=0.0),
            np.pi,
            phases,
        )
        if branch_shifts is None:
            shifts = np.zeros(source.shape[0], dtype=int)
            convention = BranchConvention.PRINCIPAL
        else:
            shifts = np.asarray(branch_shifts)
            if shifts.shape != (source.shape[0],):
                raise ValueError(
                    f"branch_shifts must have shape {(source.shape[0],)}, got {shifts.shape}"
                )
            if not np.issubdtype(shifts.dtype, np.integer):
                if not np.all(np.equal(shifts, np.round(shifts))):
                    raise ValueError("branch_shifts must contain integers")
                shifts = np.round(shifts).astype(int)
            else:
                shifts = shifts.astype(int, copy=True)
            convention = BranchConvention.EXPLICIT_SHIFTS

        selected_phases = phases + 2.0 * np.pi * shifts
        generator = schur_vectors @ np.diag(1j * selected_phases) @ schur_vectors.conj().T
        # Remove only roundoff-scale Hermitian leakage.
        generator = 0.5 * (generator - generator.conj().T)

        schur_offdiag = _frobenius_norm(
            triangular - np.diag(np.diag(triangular))
        )
        generator_error = _frobenius_norm(generator + generator.conj().T)
        reconstructed_target = source @ expm(generator)
        endpoint_error = _frobenius_norm(reconstructed_target - target)
        if endpoint_error > endpoint_tolerance:
            raise ValueError(
                "unitary path does not close at target within tolerance: "
                f"error {endpoint_error:.3e}; relative Schur off-diagonal "
                f"norm {schur_offdiag:.3e}"
            )

        branch_distance = np.abs(np.pi - np.abs(phases))
        self._source = source
        self._target = target
        self._generator = generator
        self._principal_phases = phases.copy()
        self._selected_phases = selected_phases.copy()
        self._branch_shifts = shifts.copy()
        self._diagnostics = BasisPathDiagnostics(
            dimension=source.shape[0],
            source_unitarity_error=source_error,
            target_unitarity_error=target_error,
            relative_unitarity_error=relative_error,
            schur_off_diagonal_norm=schur_offdiag,
            generator_skew_hermitian_error=generator_error,
            endpoint_error=endpoint_error,
            minimum_branch_cut_distance=float(np.min(branch_distance)),
            near_branch_cut_count=int(np.count_nonzero(branch_distance <= branch_cut_tolerance)),
            branch_convention=convention.value,
            phase_min=float(np.min(selected_phases)),
            phase_max=float(np.max(selected_phases)),
        )

    @staticmethod
    def _validate_eta(eta: float) -> float:
        value = float(eta)
        if not np.isfinite(value) or value < 0.0 or value > 1.0:
            raise ValueError(f"eta must be finite and in [0, 1], got {eta!r}")
        return value

    @property
    def dimension(self) -> int:
        return self._source.shape[0]

    @property
    def generator(self) -> np.ndarray:
        return self._generator.copy()

    @property
    def principal_phases(self) -> np.ndarray:
        return self._principal_phases.copy()

    @property
    def selected_phases(self) -> np.ndarray:
        return self._selected_phases.copy()

    @property
    def branch_shifts(self) -> np.ndarray:
        return self._branch_shifts.copy()

    @property
    def diagnostics(self) -> BasisPathDiagnostics:
        return self._diagnostics

    def unitary_at(self, eta: float) -> np.ndarray:
        value = self._validate_eta(eta)
        # Exact endpoint copies make the public endpoint contract unambiguous.
        if value == 0.0:
            return self._source.copy()
        if value == 1.0:
            return self._target.copy()
        return self._source @ expm(value * self._generator)

    def derivative_at(self, eta: float) -> np.ndarray:
        unitary = self.unitary_at(eta)
        return unitary @ self._generator

    def diagnostics_at(self, eta: float) -> Mapping[str, float]:
        unitary = self.unitary_at(eta)
        return {
            "eta": float(eta),
            "unitarity_error": _unitarity_error(unitary),
            "endpoint_error": self._diagnostics.endpoint_error,
            "near_branch_cut_count": float(self._diagnostics.near_branch_cut_count),
        }

