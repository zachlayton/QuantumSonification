"""Cross-backend validation for the QMW scalar field V3."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .backends.exact import (
    ExactTruncatedScalarFieldBackend,
    exact_product_coherent,
)
from .backends.gaussian import GaussianScalarFieldBackend
from .gaussian import coherent_mode_state
from .model import ScalarFieldModel, ScalarFieldSpec


@dataclass(frozen=True)
class ScalarFieldValidationReport:
    sites: int
    cutoff: int
    time: float
    max_mean_phi_error: float
    max_mean_pi_error: float
    max_covariance_error: float
    max_occupation_error: float
    energy_error: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def validate_exact_against_gaussian(
    *,
    spec: ScalarFieldSpec | None = None,
    amplitudes: np.ndarray | None = None,
    cutoff: int = 8,
    time: float = 0.7,
) -> ScalarFieldValidationReport:
    spec = spec or ScalarFieldSpec(sites=2, mass=0.8)
    if amplitudes is None:
        amplitudes = np.linspace(0.08, 0.16, spec.sites).astype(complex)
    alpha = np.asarray(amplitudes, dtype=np.complex128)
    if alpha.shape != (spec.sites,):
        raise ValueError("validation requires one amplitude per field mode")
    model = ScalarFieldModel.from_spec(spec)
    gaussian = GaussianScalarFieldBackend(spec).run(
        coherent_mode_state(model, alpha), time=time
    )
    exact = ExactTruncatedScalarFieldBackend(spec, cutoff=cutoff).run(
        exact_product_coherent(alpha, cutoff), time=time
    )
    covariance_error = max(
        float(np.max(np.abs(exact.covariance_phi - gaussian.covariance_phi))),
        float(np.max(np.abs(exact.covariance_pi - gaussian.covariance_pi))),
        float(
            np.max(
                np.abs(exact.covariance_phi_pi - gaussian.covariance_phi_pi)
            )
        ),
    )
    return ScalarFieldValidationReport(
        sites=spec.sites,
        cutoff=int(cutoff),
        time=float(time),
        max_mean_phi_error=float(
            np.max(np.abs(exact.mean_phi - gaussian.mean_phi))
        ),
        max_mean_pi_error=float(np.max(np.abs(exact.mean_pi - gaussian.mean_pi))),
        max_covariance_error=covariance_error,
        max_occupation_error=float(
            np.max(np.abs(exact.mode_occupations - gaussian.mode_occupations))
        ),
        energy_error=abs(exact.mean_energy - gaussian.mean_energy),
    )


__all__ = ["ScalarFieldValidationReport", "validate_exact_against_gaussian"]
