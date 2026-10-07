"""Closed harmonic lattice mechanics and immutable phonon analysis frames.

This module implements a scalar-displacement harmonic lattice.  Its authority
is a caller-supplied real symmetric positive-semidefinite dynamical matrix
``D`` with equation of motion ``x_ddot + D x = 0``.  It does not infer a
lattice from a density matrix, turn diagnostic activity into scattering, or
claim a quantum phonon population from classical phase-space coordinates.

``PhononLatticeEngine.from_couplings`` is the explicit graph-spring adapter:
nonnegative symmetric pair couplings ``C`` and onsite stiffness ``k`` produce
``D = diag(sum_j C_ij) - C + diag(k)``.  More general finite-element or
mass-weighted geometry solvers can supply their own ``D`` directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import numpy as np


Array = np.ndarray


def _readonly_real(value: object, name: str) -> Array:
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise ValueError(f"{name} must be real")
    result = np.array(raw, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def dynamical_matrix_from_couplings(
    couplings: object,
    *,
    onsite: object = 0.0,
    tolerance: float = 1.0e-12,
) -> Array:
    """Build a scalar graph-spring dynamical matrix.

    ``couplings[i, j]`` is the nonnegative pair stiffness between sites.  The
    matrix must be symmetric and have a zero diagonal. ``onsite`` is either a
    nonnegative scalar or one nonnegative pinning stiffness per site.  Unit
    masses (or already mass-normalized coordinates) are assumed.
    """

    tol = float(tolerance)
    if not np.isfinite(tol) or tol <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    raw = np.asarray(couplings)
    if np.iscomplexobj(raw):
        raise ValueError("couplings must be real")
    matrix = np.array(raw, dtype=np.float64, copy=True)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 1:
        raise ValueError("couplings must be a nonempty square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("couplings must be finite")
    scale = max(float(np.max(np.abs(matrix))), np.finfo(float).tiny)
    if np.linalg.norm(matrix - matrix.T, ord="fro") > tol * scale * matrix.shape[0]:
        raise ValueError("couplings must be symmetric")
    if np.any(matrix < -tol * scale):
        raise ValueError("couplings must be nonnegative")
    if np.any(np.abs(np.diag(matrix)) > tol * scale):
        raise ValueError("couplings diagonal must be zero; use onsite stiffness")
    # Preserve exact caller values except for roundoff-scale negative zeros.
    matrix[matrix < 0.0] = 0.0

    onsite_raw = np.asarray(onsite)
    if np.iscomplexobj(onsite_raw):
        raise ValueError("onsite stiffness must be real")
    onsite_values = np.asarray(onsite_raw, dtype=np.float64)
    if onsite_values.ndim == 0:
        onsite_values = np.full(matrix.shape[0], float(onsite_values))
    else:
        onsite_values = np.array(onsite_values, dtype=np.float64, copy=True).reshape(-1)
    if onsite_values.shape != (matrix.shape[0],):
        raise ValueError("onsite stiffness must be scalar or one value per site")
    if not np.all(np.isfinite(onsite_values)) or np.any(onsite_values < 0.0):
        raise ValueError("onsite stiffness must be finite and nonnegative")

    result = np.diag(np.sum(matrix, axis=1) + onsite_values) - matrix
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class PhononFrame:
    """One immutable harmonic-lattice state and its modal decomposition.

    Frequencies are angular frequencies in the source time unit. Mode shapes
    are Euclidean-orthonormal columns. Energy arrays contain one value per
    mode and obey ``2 E_j = Qdot_j**2 + omega_j**2 Q_j**2`` for unit mass.

    ``energy_current[i, j]`` is positive for instantaneous energy flow from
    site ``i`` to site ``j`` under the symmetric local-energy partition. It is
    antisymmetric and ``d local_energy_i / dt = -sum_j current[i, j]``.

    Ratios with a zero denominator are explicitly undefined (NaN). A zero-mode
    phase is only the finite convention ``atan2(-Qdot, omega*Q)`` and must not
    be interpreted as an oscillator phase. Occupations and scattering events
    remain caller-owned optional data; the closed classical engine invents
    neither.
    """

    displacement: Array
    velocity: Array
    dynamical_matrix: Array

    frequencies: Array
    mode_shapes: Array
    modal_positions: Array
    modal_velocities: Array
    modal_phases: Array

    kinetic_energy: Array
    potential_energy: Array
    modal_energy: Array

    frequency_ratios: Array
    recurrence_errors: Array
    occupations: Array | None
    energy_current: Array
    scattering_events: tuple[Any, ...]

    frequency_unit: str = "rad/source_time_unit"
    diagnostics: Mapping[str, object] = field(default_factory=dict)
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        array_names = (
            "displacement",
            "velocity",
            "dynamical_matrix",
            "frequencies",
            "mode_shapes",
            "modal_positions",
            "modal_velocities",
            "modal_phases",
            "kinetic_energy",
            "potential_energy",
            "modal_energy",
            "frequency_ratios",
            "recurrence_errors",
            "energy_current",
        )
        for name in array_names:
            object.__setattr__(self, name, _readonly_real(getattr(self, name), name))
        if self.occupations is not None:
            object.__setattr__(
                self,
                "occupations",
                _readonly_real(self.occupations, "occupations"),
            )
        object.__setattr__(self, "scattering_events", tuple(self.scattering_events))
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))
        object.__setattr__(self, "provenance", tuple(self.provenance))

        n = self.displacement.size
        if self.displacement.shape != (n,) or n < 1:
            raise ValueError("displacement must be a nonempty vector")
        vector_names = (
            "velocity",
            "frequencies",
            "modal_positions",
            "modal_velocities",
            "modal_phases",
            "kinetic_energy",
            "potential_energy",
            "modal_energy",
        )
        for name in vector_names:
            value = getattr(self, name)
            if value.shape != (n,) or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be a finite vector with one value per mode")
        if self.dynamical_matrix.shape != (n, n) or not np.all(np.isfinite(self.dynamical_matrix)):
            raise ValueError("dynamical_matrix must be finite and square")
        if self.mode_shapes.shape != (n, n) or not np.all(np.isfinite(self.mode_shapes)):
            raise ValueError("mode_shapes must be a finite square modal basis")
        for name in ("frequency_ratios", "recurrence_errors", "energy_current"):
            if getattr(self, name).shape != (n, n):
                raise ValueError(f"{name} must have shape {(n, n)}")
        if self.occupations is not None:
            if self.occupations.shape != (n,) or not np.all(np.isfinite(self.occupations)):
                raise ValueError("occupations must be a finite per-mode vector or None")
            if np.any(self.occupations < 0.0):
                raise ValueError("occupations must be nonnegative")
        if not isinstance(self.frequency_unit, str) or not self.frequency_unit.strip():
            raise ValueError("frequency_unit must be a nonempty string")
        if np.any(self.frequencies < 0.0):
            raise ValueError("frequencies must be nonnegative")
        if np.any(self.kinetic_energy < 0.0) or np.any(self.potential_energy < -1e-12):
            raise ValueError("modal kinetic and potential energies must be nonnegative")
        if np.any(self.modal_energy < -1e-12):
            raise ValueError("modal energy must be nonnegative")
        if not np.allclose(
            self.modal_energy,
            self.kinetic_energy + self.potential_energy,
            rtol=1e-11,
            atol=1e-13,
        ):
            raise ValueError("modal energy must equal kinetic plus potential energy")
        if not np.allclose(
            self.mode_shapes.T @ self.mode_shapes,
            np.eye(n),
            rtol=1e-11,
            atol=1e-11,
        ):
            raise ValueError("mode_shapes must be Euclidean orthonormal")
        if not np.allclose(
            self.dynamical_matrix @ self.mode_shapes,
            self.mode_shapes * self.frequencies**2,
            rtol=1e-10,
            atol=1e-11,
        ):
            raise ValueError("mode_shapes and frequencies must diagonalize the dynamical matrix")
        if not np.allclose(self.energy_current + self.energy_current.T, 0.0, atol=1e-12):
            raise ValueError("energy_current must be antisymmetric")
        if np.any(np.isinf(self.frequency_ratios)) or np.any(np.isinf(self.recurrence_errors)):
            raise ValueError("ratio diagnostics may be finite or NaN, never infinite")
        if not np.array_equal(np.isnan(self.frequency_ratios), np.isnan(self.recurrence_errors)):
            raise ValueError("ratio and recurrence undefined masks must agree")

    @property
    def total_energy(self) -> float:
        return float(np.sum(self.modal_energy))


class PhononLatticeEngine:
    """Pure analyzer and exact propagator for ``x_ddot + D x = 0``.

    The engine caches only the immutable eigensystem of ``D``. ``frame`` and
    ``evolve`` are deterministic and do not mutate a running lattice. Exact
    degeneracies retain the eigensolver's arbitrary basis within the degenerate
    subspace; persistent modal identity belongs to a separate subspace tracker.
    """

    def __init__(
        self,
        dynamical_matrix: object,
        *,
        tolerance: float = 1.0e-10,
        absolute_tolerance: float = 1.0e-12,
        ratio_max_denominator: int = 16,
        frequency_unit: str = "rad/source_time_unit",
        provenance: Sequence[str] = (),
    ) -> None:
        self.tolerance = float(tolerance)
        self.absolute_tolerance = float(absolute_tolerance)
        if not np.isfinite(self.tolerance) or self.tolerance <= 0.0:
            raise ValueError("tolerance must be finite and positive")
        if not np.isfinite(self.absolute_tolerance) or self.absolute_tolerance <= 0.0:
            raise ValueError("absolute_tolerance must be finite and positive")
        self.ratio_max_denominator = _positive_integer(
            ratio_max_denominator, "ratio_max_denominator"
        )
        if not isinstance(frequency_unit, str) or not frequency_unit.strip():
            raise ValueError("frequency_unit must be a nonempty string")
        self.frequency_unit = frequency_unit
        self.provenance = tuple(provenance)

        raw = np.asarray(dynamical_matrix)
        if np.iscomplexobj(raw):
            raise ValueError("dynamical_matrix must be real")
        matrix = np.array(raw, dtype=np.float64, copy=True)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 1:
            raise ValueError("dynamical_matrix must be a nonempty square matrix")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("dynamical_matrix must be finite")
        scale = max(float(np.linalg.norm(matrix, ord="fro")), np.finfo(float).tiny)
        symmetry_error = float(np.linalg.norm(matrix - matrix.T, ord="fro"))
        if symmetry_error > self.absolute_tolerance + self.tolerance * scale:
            raise ValueError("dynamical_matrix must be symmetric")

        eigenvalues, mode_shapes = np.linalg.eigh(matrix)
        spectral_scale = max(float(np.max(np.abs(eigenvalues))), np.finfo(float).tiny)
        psd_floor = -(self.absolute_tolerance + self.tolerance * spectral_scale)
        if float(np.min(eigenvalues)) < psd_floor:
            raise ValueError("dynamical_matrix must be positive semidefinite")
        omega_squared = np.maximum(eigenvalues, 0.0)
        frequencies = np.sqrt(omega_squared)
        mode_shapes = self._canonicalize_signs(mode_shapes)

        self._dynamical_matrix = _readonly_real(matrix, "dynamical_matrix")
        self._frequencies = _readonly_real(frequencies, "frequencies")
        self._mode_shapes = _readonly_real(mode_shapes, "mode_shapes")
        self._symmetry_error = symmetry_error
        self._minimum_eigenvalue = float(np.min(eigenvalues))
        self._eigen_residual = float(
            np.linalg.norm(matrix @ mode_shapes - mode_shapes * omega_squared, ord="fro")
        )

    @classmethod
    def from_couplings(
        cls,
        couplings: object,
        *,
        onsite: object = 0.0,
        **engine_options: object,
    ) -> "PhononLatticeEngine":
        matrix = dynamical_matrix_from_couplings(couplings, onsite=onsite)
        return cls(matrix, **engine_options)

    @staticmethod
    def _canonicalize_signs(vectors: Array) -> Array:
        result = np.array(vectors, dtype=np.float64, copy=True)
        for column in range(result.shape[1]):
            pivot = int(np.argmax(np.abs(result[:, column])))
            if result[pivot, column] < 0.0:
                result[:, column] *= -1.0
        return result

    @property
    def dimension(self) -> int:
        return self._dynamical_matrix.shape[0]

    @property
    def dynamical_matrix(self) -> Array:
        return self._dynamical_matrix

    @property
    def frequencies(self) -> Array:
        return self._frequencies

    @property
    def mode_shapes(self) -> Array:
        return self._mode_shapes

    def _state_vector(self, value: object, name: str) -> Array:
        vector = _readonly_real(value, name)
        if vector.shape != (self.dimension,) or not np.all(np.isfinite(vector)):
            raise ValueError(f"{name} must be a finite vector of length {self.dimension}")
        return vector

    def _ratio_diagnostics(self) -> tuple[Array, Array]:
        n = self.dimension
        ratios = np.full((n, n), np.nan, dtype=np.float64)
        errors = np.full((n, n), np.nan, dtype=np.float64)
        zero_floor = np.sqrt(self.absolute_tolerance)
        for numerator_index, numerator in enumerate(self._frequencies):
            for denominator_index, denominator in enumerate(self._frequencies):
                if denominator <= zero_floor:
                    continue
                ratio = float(numerator / denominator)
                candidate = Fraction(ratio).limit_denominator(self.ratio_max_denominator)
                ratios[numerator_index, denominator_index] = ratio
                errors[numerator_index, denominator_index] = abs(
                    ratio - candidate.numerator / candidate.denominator
                )
        return ratios, errors

    def frame(
        self,
        displacement: object,
        velocity: object,
        *,
        occupations: object | None = None,
        scattering_events: Sequence[Any] = (),
    ) -> PhononFrame:
        """Analyze one caller-owned lattice state without advancing it."""

        x = self._state_vector(displacement, "displacement")
        v = self._state_vector(velocity, "velocity")
        q = self._mode_shapes.T @ x
        q_velocity = self._mode_shapes.T @ v
        kinetic = 0.5 * q_velocity**2
        potential = 0.5 * self._frequencies**2 * q**2
        modal_energy = kinetic + potential
        phases = np.arctan2(-q_velocity, self._frequencies * q)
        ratios, recurrence_errors = self._ratio_diagnostics()
        # J_ij is outgoing from i to j. Diagonal/onsite terms cancel exactly.
        energy_current = 0.5 * self._dynamical_matrix * (
            v[:, None] * x[None, :] - x[:, None] * v[None, :]
        )

        occupation_values = None
        if occupations is not None:
            occupation_values = self._state_vector(occupations, "occupations")
            if np.any(occupation_values < 0.0):
                raise ValueError("occupations must be nonnegative")

        diagnostics: Mapping[str, object] = {
            "model": "closed scalar harmonic lattice; unit mass or mass-normalized coordinates",
            "equation": "x_ddot + D x = 0",
            "symmetry_residual_fro": self._symmetry_error,
            "minimum_raw_eigenvalue": self._minimum_eigenvalue,
            "eigen_residual_fro": self._eigen_residual,
            "zero_mode_count": int(np.count_nonzero(self._frequencies <= np.sqrt(self.absolute_tolerance))),
            "ratio_max_denominator": self.ratio_max_denominator,
            "ratio_error": "absolute error |omega_i/omega_j - p/q| for bounded Fraction candidate",
            "occupation_policy": "caller supplied" if occupations is not None else "not inferred",
            "scattering_policy": "caller supplied events; closed engine generates none",
            "degeneracy_policy": "frame-local eigensolver basis; use modal subspace tracking for persistent identity",
        }
        return PhononFrame(
            displacement=x,
            velocity=v,
            dynamical_matrix=self._dynamical_matrix,
            frequencies=self._frequencies,
            mode_shapes=self._mode_shapes,
            modal_positions=q,
            modal_velocities=q_velocity,
            modal_phases=phases,
            kinetic_energy=kinetic,
            potential_energy=potential,
            modal_energy=modal_energy,
            frequency_ratios=ratios,
            recurrence_errors=recurrence_errors,
            occupations=occupation_values,
            energy_current=energy_current,
            scattering_events=tuple(scattering_events),
            frequency_unit=self.frequency_unit,
            diagnostics=diagnostics,
            provenance=self.provenance
            + (
                "qmw.phonon_lattice.v1",
                "D:eigendecomposition; Q=E^T*x; Qdot=E^T*v",
                "energy:0.5*(Qdot^2+omega^2*Q^2)",
            ),
        )

    # Compatibility names for observer-style QMW pipelines.
    analyze = frame
    process = frame

    def evolve(
        self,
        displacement: object,
        velocity: object,
        *,
        time: float,
        occupations: object | None = None,
        scattering_events: Sequence[Any] = (),
    ) -> PhononFrame:
        """Return the exact closed harmonic state after elapsed source time."""

        elapsed = float(time)
        if not np.isfinite(elapsed):
            raise ValueError("time must be finite")
        x0 = self._state_vector(displacement, "displacement")
        v0 = self._state_vector(velocity, "velocity")
        q0 = self._mode_shapes.T @ x0
        qv0 = self._mode_shapes.T @ v0
        q = np.empty(self.dimension, dtype=np.float64)
        q_velocity = np.empty(self.dimension, dtype=np.float64)
        zero_floor = np.sqrt(self.absolute_tolerance)
        moving = self._frequencies > zero_floor
        angles = self._frequencies[moving] * elapsed
        cosines = np.cos(angles)
        sines = np.sin(angles)
        omega = self._frequencies[moving]
        q[moving] = q0[moving] * cosines + qv0[moving] * sines / omega
        q_velocity[moving] = -q0[moving] * omega * sines + qv0[moving] * cosines
        q[~moving] = q0[~moving] + qv0[~moving] * elapsed
        q_velocity[~moving] = qv0[~moving]
        return self.frame(
            self._mode_shapes @ q,
            self._mode_shapes @ q_velocity,
            occupations=occupations,
            scattering_events=scattering_events,
        )

    step = evolve


__all__ = [
    "PhononFrame",
    "PhononLatticeEngine",
    "dynamical_matrix_from_couplings",
]
