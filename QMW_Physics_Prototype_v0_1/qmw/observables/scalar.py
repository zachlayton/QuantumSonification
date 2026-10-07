"""Energetics and U(1) charge of a classical complex scalar field."""
from __future__ import annotations

from typing import Protocol
import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import ObservableData, StateData
from qmw.core.operators import derivative, laplacian
from .schrodinger import _real_grid


class ScalarPotential(Protocol):
    def energy(self, phi: np.ndarray) -> np.ndarray:
        """Return U(s) at s=|phi|², accepting the complex field."""
        ...

    def derivative_s(self, s: np.ndarray) -> np.ndarray:
        """Return the real radial derivative dU/ds."""
        ...


def scalar_observables(
    state: StateData,
    domain: Domain,
    potential: ScalarPotential,
) -> ObservableData:
    """Observe L=½|π|²−½|∂ₓφ|²−U(|φ|²), with π=∂ₜφ.

    With this explicit ½ convention the PDE force is −2U'(s)φ. Charge is
    q=Im(φ*π) and its spatial current is −Im(φ*∂ₓφ). Scalar-field intensity is
    not a normalized probability, so probability and norm channels remain None.
    Rates hold potential parameters fixed; external changes require work ledgers.
    """
    domain.require_periodic_space()
    state.validate(domain)
    if state.phi is None or state.pi is None:
        raise ValueError("Scalar observables require phi and pi")

    phi = np.asarray(state.phi, dtype=complex)
    pi = np.asarray(state.pi, dtype=complex)
    radial_squared = np.abs(phi)**2
    U = _real_grid(potential.energy(phi), domain, "Scalar potential energy")
    U_prime = _real_grid(potential.derivative_s(radial_squared), domain,
                         "Scalar potential derivative")
    phi_x = derivative(phi, domain)
    pi_x = derivative(pi, domain)
    pi_t = laplacian(phi, domain) - 2.0 * U_prime * phi

    kinetic = 0.5 * np.abs(pi)**2
    gradient = 0.5 * np.abs(phi_x)**2
    energy = kinetic + gradient + U
    flux = -np.real(np.conj(pi) * phi_x)
    charge = np.imag(np.conj(phi) * pi)
    charge_current = -np.imag(np.conj(phi) * phi_x)
    charge_rate = np.imag(np.conj(phi) * pi_t)
    energy_rate = (np.real(np.conj(pi) * pi_t)
                   + np.real(np.conj(phi_x) * pi_x)
                   + 2.0 * U_prime * np.real(np.conj(phi) * pi))

    return ObservableData(
        phase=np.angle(phi),
        kinetic_energy_density=kinetic,
        gradient_energy_density=gradient,
        potential_energy_density=U,
        total_energy_density=energy,
        energy_flux=flux,
        charge_density=charge,
        charge_current=charge_current,
        energy_rate=energy_rate,
        charge_rate=charge_rate,
        total_energy=float(domain.integrate(energy)),
        total_charge=float(domain.integrate(charge)),
        expectations={
            "temporal_energy": float(domain.integrate(kinetic)),
            "gradient_energy": float(domain.integrate(gradient)),
            "potential_energy": float(domain.integrate(U)),
            "field_intensity_integral": float(domain.integrate(radial_squared)),
        },
    )
