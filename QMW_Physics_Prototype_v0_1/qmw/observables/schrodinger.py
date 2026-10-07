"""Local Schrödinger quantities on the same periodic grid as the solver.

Local conservation is a continuum identity. Products can alias on a truncated
Fourier grid, so the conservation stage measures residuals rather than asserting
zero residual for every sampled field. No normalization or clipping occurs here.
"""
from __future__ import annotations

import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import ObservableData, StateData
from qmw.core.operators import derivative, laplacian


def _real_grid(values, domain: Domain, name: str) -> np.ndarray:
    """Accept a real constant or a real grid array, without discarding imaginary data."""
    a = np.asarray(values)
    if np.iscomplexobj(a) and np.any(a.imag != 0):
        raise ValueError(f"{name} must be real")
    if a.ndim == 0:
        a = np.full(domain.shape, float(a.real), dtype=float)
    elif a.shape == domain.shape:
        a = np.asarray(a.real, dtype=float)
    else:
        raise ValueError(f"{name} must be a scalar or match the spatial domain")
    if not np.isfinite(a).all():
        raise ValueError(f"{name} must be finite")
    return a


def schrodinger_observables(
    state: StateData,
    domain: Domain,
    potential,
    hbar: float = 1.0,
    mass: float = 1.0,
) -> ObservableData:
    """Observe ψ(x) for H=−ħ²/(2m)∂ₓ²+V, with controls frozen.

    Spatial integrals include the domain quadrature. ``probability_rate`` and
    ``energy_rate`` are instantaneous derivatives from the PDE, not differences
    between two separately evolved frames. Changes in V or mass belong to the
    runtime's external-work ledger, not the frozen-control continuity equation.
    Phase is a wrapped coordinate and has no physical meaning where |ψ|²=0.
    """
    domain.require_periodic_space()
    state.validate(domain)
    if state.psi is None:
        raise ValueError("Schrödinger observables require a wavefunction")
    if not np.isfinite([hbar, mass]).all() or hbar <= 0 or mass <= 0:
        raise ValueError("hbar and mass must be positive and finite")

    psi = np.asarray(state.psi, dtype=complex)
    V = _real_grid(potential, domain, "Potential")
    psi_x = derivative(psi, domain)
    Hpsi = -(hbar**2 / (2.0 * mass)) * laplacian(psi, domain) + V * psi
    psi_t = -(1j / hbar) * Hpsi
    psi_xt = derivative(psi_t, domain)

    probability = np.abs(psi)**2
    probability_rate = 2.0 * np.real(np.conj(psi) * psi_t)
    current = (hbar / mass) * np.imag(np.conj(psi) * psi_x)
    kinetic = (hbar**2 / (2.0 * mass)) * np.abs(psi_x)**2
    potential_energy = V * probability
    energy = kinetic + potential_energy
    energy_rate = ((hbar**2 / mass) * np.real(np.conj(psi_x) * psi_xt)
                   + V * probability_rate)
    flux = -(hbar**2 / mass) * np.real(np.conj(psi_t) * psi_x)

    return ObservableData(
        probability_density=probability,
        phase=np.angle(psi),
        probability_current=current,
        kinetic_energy_density=kinetic,
        potential_energy_density=potential_energy,
        total_energy_density=energy,
        energy_flux=flux,
        probability_rate=probability_rate,
        energy_rate=energy_rate,
        total_energy=float(domain.integrate(energy)),
        norm=float(domain.integrate(probability)),
        expectations={
            "kinetic_energy": float(domain.integrate(kinetic)),
            "potential_energy": float(domain.integrate(potential_energy)),
            "mean_momentum": float(domain.integrate(
                hbar * np.imag(np.conj(psi) * psi_x))),
        },
    )
