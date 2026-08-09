"""Gauge-covariant wavefunction instruments."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import Mapping, Optional

import numpy as np

from excitation.wavefunction_sources_v1 import WavefunctionFrame, _frame_from_psi


class AharonovBohmRingSource:
    """Charged quantum rotor threaded by magnetic flux.

    ``flux_ratio`` is alpha = q Phi / h, equivalently Phi / Phi_0 with the
    charge sign included.  Energies and mechanical current depend on m-alpha,
    while the magnetic field can vanish everywhere on the particle's ring.
    """

    def __init__(
        self,
        *,
        n_points: int = 256,
        flux_ratio: float = 0.35,
        coefficients: Optional[Mapping[int, complex]] = None,
        hbar: float = 1.0,
        moment_of_inertia: float = 1.0,
    ) -> None:
        if n_points < 8:
            raise ValueError("n_points must be at least 8")
        if moment_of_inertia <= 0.0:
            raise ValueError("moment_of_inertia must be positive")
        self.coordinates = (np.linspace(0.0, 2.0 * math.pi, n_points, endpoint=False),)
        self.spacing = (2.0 * math.pi / n_points,)
        self.flux_ratio = float(flux_ratio)
        self.coefficients = dict(coefficients or {-1: 0.55, 0: 1.0, 2: 0.45j})
        norm = math.sqrt(sum(abs(value) ** 2 for value in self.coefficients.values()))
        if norm <= 1e-15:
            raise ValueError("at least one angular-momentum coefficient must be nonzero")
        self.coefficients = {key: complex(value) / norm for key, value in self.coefficients.items()}
        self.hbar = float(hbar)
        self.moment_of_inertia = float(moment_of_inertia)
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt
        phi = self.coordinates[0]
        psi = np.zeros_like(phi, dtype=np.complex128)
        for angular_momentum, coefficient in self.coefficients.items():
            mechanical_index = angular_momentum - self.flux_ratio
            energy = self.hbar**2 * mechanical_index**2 / (2.0 * self.moment_of_inertia)
            basis = np.exp(1j * angular_momentum * phi) / math.sqrt(2.0 * math.pi)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)

        raw = _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=np.zeros_like(phi),
            time=self.time,
            source="aharonov_bohm_effect",
            hbar=self.hbar,
            mass=self.moment_of_inertia,
            metadata={},
        )
        mode_numbers = np.fft.fftfreq(phi.size, d=1.0 / phi.size)
        derivative = np.fft.ifft(1j * mode_numbers * np.fft.fft(psi))
        mechanical_derivative = -1j * derivative - self.flux_ratio * psi
        current = (
            self.hbar
            / self.moment_of_inertia
            * np.real(np.conj(psi) * mechanical_derivative)
        )
        energy_density = (
            self.hbar**2
            / (2.0 * self.moment_of_inertia)
            * np.abs(mechanical_derivative) ** 2
        )
        energy = float(np.sum(energy_density) * self.spacing[0])
        current_strength = float(np.sum(np.abs(current)) * self.spacing[0])
        mechanical_momentum = float(
            self.hbar
            * np.sum(np.real(np.conj(psi) * mechanical_derivative))
            * self.spacing[0]
        )
        descriptor = replace(
            raw.descriptor,
            energy=energy / (energy + 1.0),
            current=current_strength / (current_strength + 1.0),
            momentum=(mechanical_momentum,),
        )
        return replace(
            raw,
            probability_current=(current,),
            energy_density=energy_density,
            descriptor=descriptor,
            metadata={
                "flux_ratio": self.flux_ratio,
                "holonomy_phase": 2.0 * math.pi * self.flux_ratio,
                "angular_momenta": tuple(sorted(self.coefficients)),
                "mechanical_angular_momentum": mechanical_momentum,
                "persistent_current": float(np.sum(current) * self.spacing[0]),
                "expectation_energy": energy,
            },
        )

    def descriptor(self, dt: float):
        return self.frame(dt).descriptor


__all__ = ["AharonovBohmRingSource"]
