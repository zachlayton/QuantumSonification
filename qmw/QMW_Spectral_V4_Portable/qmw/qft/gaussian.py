"""Gaussian states and exact symplectic evolution for the free scalar field."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import ScalarFieldModel


@dataclass(frozen=True)
class GaussianFieldState:
    """First moments and symmetrized covariance in ``(phi..., pi...)`` order."""

    mean: np.ndarray
    covariance: np.ndarray

    def validated(self, model: ScalarFieldModel, tolerance: float = 1e-9) -> "GaussianFieldState":
        mean = np.asarray(self.mean, dtype=float)
        covariance = np.asarray(self.covariance, dtype=float)
        dimension = model.phase_space_dimension
        if mean.shape != (dimension,) or covariance.shape != (dimension, dimension):
            raise ValueError("Gaussian state shape does not match field model")
        if not np.isfinite(mean).all() or not np.isfinite(covariance).all():
            raise ValueError("Gaussian state contains non-finite values")
        symmetry_error = float(np.linalg.norm(covariance - covariance.T))
        if symmetry_error > tolerance:
            raise ValueError("Gaussian covariance must be symmetric")
        covariance = 0.5 * (covariance + covariance.T)
        uncertainty = covariance + 0.5j * model.spec.hbar * model.symplectic_form
        if float(np.min(np.linalg.eigvalsh(uncertainty))) < -tolerance:
            raise ValueError("Gaussian covariance violates the uncertainty relation")
        return GaussianFieldState(mean.copy(), covariance.copy())


def _mode_covariance(
    model: ScalarFieldModel, thermal_factors: np.ndarray
) -> np.ndarray:
    frequencies = model.frequencies
    vectors = model.mode_vectors
    hbar = model.spec.hbar
    q_variances = 0.5 * hbar * thermal_factors / frequencies
    p_variances = 0.5 * hbar * thermal_factors * frequencies
    phi = (vectors * q_variances) @ vectors.T
    pi = (vectors * p_variances) @ vectors.T
    zero = np.zeros_like(phi)
    return np.block([[phi, zero], [zero, pi]])


def vacuum_state(model: ScalarFieldModel) -> GaussianFieldState:
    factors = np.ones(model.spec.sites, dtype=float)
    return GaussianFieldState(
        mean=np.zeros(model.phase_space_dimension, dtype=float),
        covariance=_mode_covariance(model, factors),
    ).validated(model)


def thermal_state(model: ScalarFieldModel, temperature: float) -> GaussianFieldState:
    temperature = float(temperature)
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("temperature must be finite and positive")
    arguments = model.spec.hbar * model.frequencies / (2.0 * temperature)
    factors = 1.0 / np.tanh(arguments)
    return GaussianFieldState(
        mean=np.zeros(model.phase_space_dimension, dtype=float),
        covariance=_mode_covariance(model, factors),
    ).validated(model)


def coherent_mode_state(
    model: ScalarFieldModel, amplitudes: np.ndarray
) -> GaussianFieldState:
    """Prepare coherent amplitudes in NumPy's deterministic normal-mode basis."""

    alpha = np.asarray(amplitudes, dtype=np.complex128)
    if alpha.shape != (model.spec.sites,) or not np.isfinite(alpha).all():
        raise ValueError("one finite coherent amplitude is required per mode")
    hbar = model.spec.hbar
    mode_phi = np.sqrt(2.0 * hbar / model.frequencies) * alpha.real
    mode_pi = np.sqrt(2.0 * hbar * model.frequencies) * alpha.imag
    mean = np.concatenate(
        [model.mode_vectors @ mode_phi, model.mode_vectors @ mode_pi]
    )
    vacuum = vacuum_state(model)
    return GaussianFieldState(mean, vacuum.covariance.copy()).validated(model)


def localized_displacement_state(
    model: ScalarFieldModel,
    *,
    mean_phi: np.ndarray | None = None,
    mean_pi: np.ndarray | None = None,
) -> GaussianFieldState:
    sites = model.spec.sites
    phi = np.zeros(sites) if mean_phi is None else np.asarray(mean_phi, dtype=float)
    pi = np.zeros(sites) if mean_pi is None else np.asarray(mean_pi, dtype=float)
    if phi.shape != (sites,) or pi.shape != (sites,):
        raise ValueError("localized means require one value per lattice site")
    vacuum = vacuum_state(model)
    return GaussianFieldState(
        np.concatenate([phi, pi]), vacuum.covariance.copy()
    ).validated(model)


def squeezed_mode_state(
    model: ScalarFieldModel, squeezing: np.ndarray
) -> GaussianFieldState:
    """Product squeezed vacuum in the deterministic normal-mode basis.

    The convention is ``z_k = r_k exp(i theta_k)`` with dimensionless modal
    quadrature covariance
    ``V_xx = hbar/2 (cosh(2r)-cos(theta)sinh(2r))``.
    """

    values = np.asarray(squeezing, dtype=np.complex128)
    if values.shape != (model.spec.sites,) or not np.isfinite(values).all():
        raise ValueError("one finite squeezing parameter is required per mode")
    magnitude = np.abs(values)
    angle = np.angle(values)
    cosh = np.cosh(2.0 * magnitude)
    sinh = np.sinh(2.0 * magnitude)
    hbar = model.spec.hbar
    modal_phi = 0.5 * hbar * (cosh - np.cos(angle) * sinh) / model.frequencies
    modal_pi = 0.5 * hbar * (cosh + np.cos(angle) * sinh) * model.frequencies
    modal_cross = -0.5 * hbar * np.sin(angle) * sinh
    vectors = model.mode_vectors
    phi = (vectors * modal_phi) @ vectors.T
    pi = (vectors * modal_pi) @ vectors.T
    cross = (vectors * modal_cross) @ vectors.T
    covariance = np.block([[phi, cross], [cross.T, pi]])
    return GaussianFieldState(
        np.zeros(model.phase_space_dimension), covariance
    ).validated(model, tolerance=2e-8)


def bogoliubov_coefficients(
    squeezing: np.ndarray | complex,
) -> tuple[np.ndarray, np.ndarray]:
    """Return constrained ``(mu, nu)`` for ``S† a S = mu a + nu a†``.

    With ``z = r exp(i theta)``, this convention has
    ``mu = cosh(r)`` and ``nu = -exp(i theta) sinh(r)``.  It therefore
    satisfies ``|mu|² - |nu|² = 1`` by construction.
    """

    values = np.asarray(squeezing, dtype=np.complex128)
    if not np.isfinite(values).all():
        raise ValueError("squeezing parameters must be finite")
    magnitude = np.abs(values)
    angle = np.angle(values)
    mu = np.cosh(magnitude).astype(np.complex128)
    nu = -np.exp(1j * angle) * np.sinh(magnitude)
    return mu, nu


def symplectic_evolution(model: ScalarFieldModel, time: float) -> np.ndarray:
    time = float(time)
    if not np.isfinite(time):
        raise ValueError("time must be finite")
    vectors = model.mode_vectors
    frequencies = model.frequencies
    cosine = (vectors * np.cos(frequencies * time)) @ vectors.T
    sine_over_frequency = (
        vectors * (np.sin(frequencies * time) / frequencies)
    ) @ vectors.T
    minus_frequency_sine = (
        vectors * (-frequencies * np.sin(frequencies * time))
    ) @ vectors.T
    return np.block(
        [[cosine, sine_over_frequency], [minus_frequency_sine, cosine]]
    )


def evolve_gaussian(
    state: GaussianFieldState, model: ScalarFieldModel, time: float
) -> GaussianFieldState:
    initial = state.validated(model)
    evolution = symplectic_evolution(model, time)
    return GaussianFieldState(
        mean=evolution @ initial.mean,
        covariance=evolution @ initial.covariance @ evolution.T,
    ).validated(model, tolerance=2e-8)


__all__ = [
    "GaussianFieldState",
    "bogoliubov_coefficients",
    "coherent_mode_state",
    "evolve_gaussian",
    "localized_displacement_state",
    "squeezed_mode_state",
    "symplectic_evolution",
    "thermal_state",
    "vacuum_state",
]
