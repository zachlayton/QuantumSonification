"""Thermodynamics for a homogeneous, nonrelativistic 3D ideal quantum gas.

The physical control is the phase-space density D = n * lambda_T**3.  Internal
degeneracy ``g`` is kept explicit, so fugacity is determined by D/g.  The
functions use the conventional complete Bose/Fermi integrals

    I_s(z) = 1/Gamma(s) integral_0^infinity x**(s-1)/(z**-1 exp(x) +/- 1) dx.

The plus sign is fermionic and the minus sign is bosonic.  For bosons, the
excited gas saturates at D/g = zeta(3/2); additional particles enter the
zero-momentum condensate and contribute no ideal-gas pressure.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import gamma, zeta


PLANCK = 6.626_070_15e-34
BOLTZMANN = 1.380_649e-23
ATOMIC_MASS = 1.660_539_068_92e-27
BOSE_CRITICAL_REDUCED_DENSITY = float(zeta(1.5, 1.0))


def thermal_de_broglie_wavelength(mass_kg: float, temperature_k: float) -> float:
    """Return lambda_T = h/sqrt(2*pi*m*k_B*T) in metres."""

    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive")
    return PLANCK / math.sqrt(2.0 * math.pi * mass_kg * BOLTZMANN * temperature_k)


def phase_space_density(number_density_m3: float, mass_kg: float, temperature_k: float) -> float:
    """Return the dimensionless degeneracy control D = n*lambda_T**3."""

    if number_density_m3 < 0.0:
        raise ValueError("number_density_m3 cannot be negative")
    wavelength = thermal_de_broglie_wavelength(mass_kg, temperature_k)
    return number_density_m3 * wavelength**3


def _occupation(x: float, log_fugacity: float, statistics: str) -> float:
    shifted = x - log_fugacity
    if statistics == "fermi":
        if shifted > 45.0:
            return math.exp(-shifted)
        if shifted < -45.0:
            return 1.0
        return 1.0 / (math.exp(shifted) + 1.0)
    if shifted > 45.0:
        return math.exp(-shifted)
    return 1.0 / math.expm1(shifted)


def quantum_integral(order: float, log_fugacity: float, statistics: str) -> float:
    """Evaluate the normalized complete Bose or Fermi integral I_order(z)."""

    if statistics not in {"fermi", "bose"}:
        raise ValueError("statistics must be 'fermi' or 'bose'")
    if order <= 1.0:
        raise ValueError("this implementation requires order > 1")
    if statistics == "bose" and log_fugacity > 0.0:
        raise ValueError("boson fugacity cannot exceed one")

    # x=u**2 removes the integrable Bose singularity at x=0 when z=1.
    def integrand(u: float) -> float:
        if u == 0.0:
            if statistics == "bose" and log_fugacity == 0.0 and order == 1.5:
                return 2.0
            return 0.0
        x = u * u
        return 2.0 * u ** (2.0 * order - 1.0) * _occupation(x, log_fugacity, statistics)

    upper = max(48.0, log_fugacity + 48.0)
    value, _ = quad(integrand, 0.0, math.sqrt(upper), epsabs=2e-11, epsrel=2e-10, limit=300)
    return float(value / gamma(order))


def _solve_log_fugacity(reduced_density: float, statistics: str) -> float:
    if reduced_density <= 0.0:
        return -math.inf
    if statistics == "bose":
        if reduced_density >= BOSE_CRITICAL_REDUCED_DENSITY:
            return 0.0
        return float(
            brentq(
                lambda log_z: quantum_integral(1.5, log_z, "bose") - reduced_density,
                -50.0,
                -1e-12,
                xtol=2e-12,
            )
        )

    lower = -50.0
    upper = max(4.0, (1.5 * reduced_density) ** (2.0 / 3.0) + 4.0)
    while quantum_integral(1.5, upper, "fermi") < reduced_density:
        upper *= 2.0
    return float(
        brentq(
            lambda log_z: quantum_integral(1.5, log_z, "fermi") - reduced_density,
            lower,
            upper,
            xtol=2e-12,
        )
    )


@dataclass(frozen=True)
class QuantumGasState:
    statistics: str
    phase_space_density: float
    internal_degeneracy: int
    log_fugacity: float
    pressure_ratio: float
    condensate_fraction: float

    @property
    def fugacity(self) -> float:
        if self.log_fugacity == -math.inf:
            return 0.0
        if self.log_fugacity > 709.0:
            return math.inf
        return math.exp(self.log_fugacity)

    @property
    def quantum_pressure_sign(self) -> int:
        """Sign of P-P_classical: +1 fermions, -1 bosons, 0 at D=0."""

        if self.phase_space_density == 0.0:
            return 0
        return 1 if self.statistics == "fermi" else -1

    def mean_occupation(self, reduced_energy: float) -> float:
        """Mean occupation of one state at x = epsilon/(k_B*T)."""

        if reduced_energy < 0.0:
            raise ValueError("reduced_energy cannot be negative")
        if not math.isfinite(self.log_fugacity):
            return 0.0
        if self.statistics == "bose" and self.log_fugacity == 0.0 and reduced_energy == 0.0:
            return math.inf
        return _occupation(reduced_energy, self.log_fugacity, self.statistics)

    def sample_detected_occupation(
        self,
        reduced_energy: float,
        rng: object,
        *,
        detection_efficiency: float = 1.0,
    ) -> int:
        """Sample one detector window from the Fermi/Bose occupation law.

        Bernoulli and geometric distributions are preserved under independent
        detection loss, with their means multiplied by the efficiency.
        ``rng`` may be ``random.Random`` or a NumPy generator.
        """

        if not 0.0 <= detection_efficiency <= 1.0:
            raise ValueError("detection_efficiency must lie in [0,1]")
        mean = detection_efficiency * self.mean_occupation(reduced_energy)
        random_value = float(rng.random())
        if self.statistics == "fermi":
            return int(random_value < mean)
        if mean <= 0.0:
            return 0
        if not math.isfinite(mean):
            raise ValueError("sample the condensate separately from its macroscopic fraction")
        ratio = mean / (1.0 + mean)
        return int(math.log1p(-random_value) / math.log(ratio))

    def pressure_pa(self, number_density_m3: float, temperature_k: float) -> float:
        if number_density_m3 < 0.0 or temperature_k <= 0.0:
            raise ValueError("density must be nonnegative and temperature positive")
        return self.pressure_ratio * number_density_m3 * BOLTZMANN * temperature_k

    def spectral_particle_weights(self, energy_centres: np.ndarray) -> np.ndarray:
        """Normalize 3D energy-shell particle populations for sonification."""

        energies = np.asarray(energy_centres, dtype=float)
        if energies.ndim != 1 or np.any(energies <= 0.0):
            raise ValueError("energy centres must be a positive one-dimensional array")
        occupations = np.array([self.mean_occupation(float(x)) for x in energies])
        shell_particles = np.sqrt(energies) * occupations
        total = float(np.sum(shell_particles))
        if total <= 0.0:
            return np.zeros_like(shell_particles)
        return shell_particles / total


def quantum_gas_state(
    phase_density: float,
    statistics: str,
    *,
    internal_degeneracy: int = 1,
) -> QuantumGasState:
    """Solve fugacity, condensate fraction, and P/(n*k_B*T) from D."""

    if phase_density < 0.0:
        raise ValueError("phase_density cannot be negative")
    if statistics not in {"fermi", "bose"}:
        raise ValueError("statistics must be 'fermi' or 'bose'")
    if internal_degeneracy < 1:
        raise ValueError("internal_degeneracy must be at least one")
    if phase_density == 0.0:
        return QuantumGasState(statistics, 0.0, internal_degeneracy, -math.inf, 1.0, 0.0)

    reduced = phase_density / internal_degeneracy
    log_z = _solve_log_fugacity(reduced, statistics)
    if statistics == "bose" and reduced >= BOSE_CRITICAL_REDUCED_DENSITY:
        condensate_fraction = 1.0 - BOSE_CRITICAL_REDUCED_DENSITY / reduced
        pressure_ratio = float(zeta(2.5, 1.0)) / reduced
    else:
        condensate_fraction = 0.0
        pressure_ratio = quantum_integral(2.5, log_z, statistics) / reduced
    return QuantumGasState(
        statistics=statistics,
        phase_space_density=float(phase_density),
        internal_degeneracy=int(internal_degeneracy),
        log_fugacity=log_z,
        pressure_ratio=float(pressure_ratio),
        condensate_fraction=float(condensate_fraction),
    )


def compare_statistics(phase_density: float, *, internal_degeneracy: int = 1) -> dict[str, QuantumGasState]:
    """Return fermion and boson states at the same n*lambda_T**3."""

    return {
        name: quantum_gas_state(phase_density, name, internal_degeneracy=internal_degeneracy)
        for name in ("fermi", "bose")
    }


def state_from_physical_controls(
    number_density_m3: float,
    temperature_k: float,
    mass_amu: float,
    statistics: str,
    *,
    internal_degeneracy: int = 1,
) -> QuantumGasState:
    """Convenience bridge from laboratory controls to the dimensionless state."""

    if mass_amu <= 0.0:
        raise ValueError("mass_amu must be positive")
    density = phase_space_density(number_density_m3, mass_amu * ATOMIC_MASS, temperature_k)
    return quantum_gas_state(density, statistics, internal_degeneracy=internal_degeneracy)
