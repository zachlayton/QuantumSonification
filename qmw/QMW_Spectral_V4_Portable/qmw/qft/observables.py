"""Auditable observables for finite-lattice Gaussian scalar fields."""

from __future__ import annotations

import numpy as np

from .gaussian import GaussianFieldState
from .model import ScalarFieldModel
from .schema import ScalarFieldFrame


def _expected_squared_difference(
    mean: np.ndarray, covariance: np.ndarray, left: int, right: int
) -> float:
    mean_difference = mean[left] - mean[right]
    variance = (
        covariance[left, left]
        + covariance[right, right]
        - 2.0 * covariance[left, right]
    )
    return float(mean_difference**2 + variance)


def gaussian_purity(state: GaussianFieldState, model: ScalarFieldModel) -> float:
    covariance = state.validated(model).covariance
    sign, log_determinant = np.linalg.slogdet(covariance)
    if sign <= 0.0:
        raise ValueError("Gaussian covariance must have positive determinant")
    log_purity = model.spec.sites * np.log(model.spec.hbar / 2.0)
    log_purity -= 0.5 * log_determinant
    return float(np.clip(np.exp(log_purity), 0.0, 1.0))


def frame_from_gaussian(
    state: GaussianFieldState,
    model: ScalarFieldModel,
    *,
    time: float,
    backend: str,
    backend_metadata: dict[str, object] | None = None,
) -> ScalarFieldFrame:
    value = state.validated(model)
    sites = model.spec.sites
    mean_phi = value.mean[:sites]
    mean_pi = value.mean[sites:]
    covariance_phi = value.covariance[:sites, :sites]
    covariance_pi = value.covariance[sites:, sites:]
    covariance_phi_pi = value.covariance[:sites, sites:]

    vectors = model.mode_vectors
    mode_phi = vectors.T @ mean_phi
    mode_pi = vectors.T @ mean_pi
    mode_covariance_phi = vectors.T @ covariance_phi @ vectors
    mode_covariance_pi = vectors.T @ covariance_pi @ vectors
    occupations = (
        model.frequencies
        * (mode_phi**2 + np.diag(mode_covariance_phi))
        + (mode_pi**2 + np.diag(mode_covariance_pi)) / model.frequencies
    ) / (2.0 * model.spec.hbar) - 0.5
    occupations = np.maximum(occupations, 0.0)

    expected_pi_squared = mean_pi**2 + np.diag(covariance_pi)
    expected_phi_squared = mean_phi**2 + np.diag(covariance_phi)
    gradient_scale = (
        model.spec.propagation_speed / model.spec.lattice_spacing
    ) ** 2
    local_energy = np.empty(sites, dtype=float)
    for site in range(sites):
        left = (site - 1) % sites
        right = (site + 1) % sites
        left_bond = _expected_squared_difference(
            mean_phi, covariance_phi, site, left
        )
        right_bond = _expected_squared_difference(
            mean_phi, covariance_phi, right, site
        )
        local_energy[site] = (
            0.5 * expected_pi_squared[site]
            + 0.5 * model.spec.mass**2 * expected_phi_squared[site]
            + 0.25 * gradient_scale * (left_bond + right_bond)
        )

    mean_energy = 0.5 * (
        float(mean_pi @ mean_pi)
        + float(np.trace(covariance_pi))
        + float(mean_phi @ model.stiffness @ mean_phi)
        + float(np.trace(model.stiffness @ covariance_phi))
    )
    return ScalarFieldFrame(
        time=float(time),
        sites=sites,
        mean_phi=mean_phi.copy(),
        mean_pi=mean_pi.copy(),
        covariance_phi=covariance_phi.copy(),
        covariance_pi=covariance_pi.copy(),
        covariance_phi_pi=covariance_phi_pi.copy(),
        frequencies=model.frequencies.copy(),
        mode_occupations=occupations,
        local_energy_density=local_energy,
        mean_energy=mean_energy,
        purity=gaussian_purity(value, model),
        backend=backend,
        backend_metadata=dict(backend_metadata or {}),
    )


__all__ = ["frame_from_gaussian", "gaussian_purity"]
