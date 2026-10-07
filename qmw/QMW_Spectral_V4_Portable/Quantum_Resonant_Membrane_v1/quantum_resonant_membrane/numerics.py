"""Runtime spectral stability bounds for effective second-order systems."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class StabilityDiagnostics:
    omega_max: float
    damping_rate_max: float
    spectral_dt_limit: float
    effective_dt_cap: float
    substeps: int
    actual_substep: float


def _as_mass_matrix(mass: Array) -> Array:
    matrix = np.asarray(mass, dtype=float)
    if matrix.ndim == 1:
        matrix = np.diag(matrix)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("mass must be a vector or square matrix")
    return 0.5 * (matrix + matrix.T)


def _mass_normalized(matrix: Array, cholesky: Array) -> Array:
    """Return L^-1 matrix L^-T for mass M = L L^T."""
    first = np.linalg.solve(cholesky, np.asarray(matrix, dtype=float))
    normalized = np.linalg.solve(cholesky, first.T).T
    return 0.5 * (normalized + normalized.T)


def stability_diagnostics(
    mass: Array,
    stiffness: Array,
    damping: Array,
    *,
    dt: float,
    max_substep: float,
    safety: float = 0.8,
) -> StabilityDiagnostics:
    """Choose substeps from generalized modal and damping spectral rates.

    Semi-implicit Euler is stable for an undamped oscillator below
    ``h * omega = 2``.  The same explicit update requires a damping-rate bound.
    We apply ``safety`` to both limits, then retain ``max_substep`` as a user
    resolution ceiling rather than treating it as the stability argument.
    """
    dt = float(dt)
    max_substep = float(max_substep)
    safety = float(safety)
    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("dt must be finite and nonnegative")
    if not math.isfinite(max_substep) or max_substep <= 0.0:
        raise ValueError("max_substep must be finite and positive")
    if not math.isfinite(safety) or not 0.0 < safety < 1.0:
        raise ValueError("safety must lie strictly between zero and one")
    mass_matrix = _as_mass_matrix(mass)
    stiffness_matrix = np.asarray(stiffness, dtype=float)
    damping_matrix = np.asarray(damping, dtype=float)
    if stiffness_matrix.shape != mass_matrix.shape or damping_matrix.shape != mass_matrix.shape:
        raise ValueError("mass, stiffness, and damping dimensions must match")
    cholesky = np.linalg.cholesky(mass_matrix)
    normalized_stiffness = _mass_normalized(stiffness_matrix, cholesky)
    normalized_damping = _mass_normalized(damping_matrix, cholesky)
    lambda_max = max(0.0, float(np.max(np.linalg.eigvalsh(normalized_stiffness))))
    damping_rate_max = max(
        0.0, float(np.max(np.linalg.eigvalsh(normalized_damping)))
    )
    omega_max = math.sqrt(lambda_max)
    oscillator_limit = math.inf if omega_max <= 1.0e-15 else 2.0 * safety / omega_max
    damping_limit = (
        math.inf
        if damping_rate_max <= 1.0e-15
        else 2.0 * safety / damping_rate_max
    )
    spectral_limit = min(oscillator_limit, damping_limit)
    if not math.isfinite(spectral_limit):
        spectral_limit = max_substep
    effective_cap = min(max_substep, spectral_limit)
    substeps = 0 if dt == 0.0 else max(1, int(math.ceil(dt / effective_cap)))
    actual = 0.0 if substeps == 0 else dt / substeps
    return StabilityDiagnostics(
        omega_max=omega_max,
        damping_rate_max=damping_rate_max,
        spectral_dt_limit=spectral_limit,
        effective_dt_cap=effective_cap,
        substeps=substeps,
        actual_substep=actual,
    )


__all__ = ["StabilityDiagnostics", "stability_diagnostics"]
