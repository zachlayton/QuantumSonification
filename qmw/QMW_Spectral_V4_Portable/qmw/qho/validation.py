"""Cross-backend validation before any hardware execution."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .backends.numpy_bosonic import NumPyBosonicBackend
from .backends.qiskit_aer import QiskitAerEncodedBackend
from .model import OscillatorSpec
from .schema import OscillatorFrame


@dataclass(frozen=True)
class CrossBackendValidation:
    passed: bool
    population_max_abs_error: float
    moment_max_abs_error: float
    rho_trace_distance: float
    reference: OscillatorFrame
    encoded: OscillatorFrame
    atol: float

    def summary(self) -> dict[str, float | bool]:
        return {
            "passed": self.passed,
            "population_max_abs_error": self.population_max_abs_error,
            "moment_max_abs_error": self.moment_max_abs_error,
            "rho_trace_distance": self.rho_trace_distance,
            "atol": self.atol,
        }


def _trace_distance(a: np.ndarray, b: np.ndarray) -> float:
    difference = 0.5 * ((a - b) + (a - b).conj().T)
    return 0.5 * float(np.sum(np.abs(np.linalg.eigvalsh(difference))))


def validate_reference_against_aer(
    state: np.ndarray,
    *,
    spec: OscillatorSpec | None = None,
    time: float = 0.0,
    atol: float = 1e-9,
) -> CrossBackendValidation:
    """Require exact local agreement before considering hardware execution."""

    reference = NumPyBosonicBackend(spec).run(state, time=time, include_rho=True)
    encoded = QiskitAerEncodedBackend(spec).run(state, time=time, include_rho=True)
    population_error = float(
        np.max(np.abs(reference.populations - encoded.populations))
    )
    moment_pairs = [
        (reference.mean_n, encoded.mean_n),
        (reference.mean_energy, encoded.mean_energy),
        (reference.x, encoded.x),
        (reference.p, encoded.p),
        (reference.var_x, encoded.var_x),
        (reference.var_p, encoded.var_p),
    ]
    moment_error = max(abs(a - b) for a, b in moment_pairs)
    if reference.rho is None or encoded.rho is None:
        raise RuntimeError("validation backends did not return density matrices")
    trace_distance = _trace_distance(reference.rho, encoded.rho)
    passed = max(population_error, moment_error, trace_distance) <= atol
    return CrossBackendValidation(
        passed=passed,
        population_max_abs_error=population_error,
        moment_max_abs_error=moment_error,
        rho_trace_distance=trace_distance,
        reference=reference,
        encoded=encoded,
        atol=atol,
    )


__all__ = ["CrossBackendValidation", "validate_reference_against_aer"]
