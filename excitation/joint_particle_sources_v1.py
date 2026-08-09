"""Joint-state instruments for identical particles in one spatial dimension."""

from __future__ import annotations

import math
from typing import Literal

import numpy as np

from excitation.quantum_frames_v1 import JointWavefunctionFrame


class IdenticalParticles1DSource:
    """Two free particles with exact bosonic or fermionic exchange symmetry."""

    def __init__(
        self,
        *,
        statistics: Literal["boson", "fermion"] = "boson",
        n_points: int = 96,
        extent: float = 16.0,
        center_a: float = -1.2,
        center_b: float = 1.2,
        momentum_a: float = 1.1,
        momentum_b: float = -1.1,
        sigma: float = 1.1,
        hbar: float = 1.0,
        mass: float = 1.0,
    ) -> None:
        if statistics not in ("boson", "fermion"):
            raise ValueError("statistics must be boson or fermion")
        if n_points < 8 or extent <= 0.0 or sigma <= 0.0 or mass <= 0.0:
            raise ValueError("invalid grid or particle parameters")
        self.statistics = statistics
        self.coordinates = np.linspace(-extent / 2.0, extent / 2.0, n_points, endpoint=False)
        self.spacing = float(self.coordinates[1] - self.coordinates[0])
        self.hbar = float(hbar)
        self.mass = float(mass)
        self._parameters = (center_a, center_b, momentum_a, momentum_b, sigma)
        self._initial_a = self._gaussian(center_a, momentum_a, sigma)
        self._initial_b = self._gaussian(center_b, momentum_b, sigma)
        self.orbital_a = self._initial_a.copy()
        self.orbital_b = self._initial_b.copy()
        wave_numbers = 2.0 * math.pi * np.fft.fftfreq(n_points, d=self.spacing)
        self.kinetic_energy = self.hbar**2 * wave_numbers**2 / (2.0 * self.mass)
        self.time = 0.0

    def _gaussian(self, center: float, momentum: float, sigma: float) -> np.ndarray:
        orbital = np.exp(-((self.coordinates - center) ** 2) / (4.0 * sigma**2))
        orbital = orbital * np.exp(1j * momentum * self.coordinates / self.hbar)
        norm = math.sqrt(float(np.sum(np.abs(orbital) ** 2) * self.spacing))
        return np.asarray(orbital / norm, dtype=np.complex128)

    def reset(self) -> None:
        self.orbital_a = self._initial_a.copy()
        self.orbital_b = self._initial_b.copy()
        self.time = 0.0

    def _propagate(self, orbital: np.ndarray, dt: float) -> np.ndarray:
        phase = np.exp(-1j * self.kinetic_energy * dt / self.hbar)
        result = np.fft.ifft(np.fft.fft(orbital) * phase)
        norm = math.sqrt(float(np.sum(np.abs(result) ** 2) * self.spacing))
        return result / norm

    def frame(self, dt: float = 0.0) -> JointWavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            self.orbital_a = self._propagate(self.orbital_a, dt)
            self.orbital_b = self._propagate(self.orbital_b, dt)
            self.time += dt
        direct = np.outer(self.orbital_a, self.orbital_b)
        exchanged = np.outer(self.orbital_b, self.orbital_a)
        psi = direct + exchanged if self.statistics == "boson" else direct - exchanged
        measure = self.spacing**2
        norm = math.sqrt(max(float(np.sum(np.abs(psi) ** 2) * measure), 1e-30))
        psi = psi / norm
        probability = np.abs(psi) ** 2
        marginal_a = np.sum(probability, axis=1) * self.spacing
        marginal_b = np.sum(probability, axis=0) * self.spacing
        swap = float(np.sum(np.conj(psi) * psi.T).real * measure)
        coincidence = float(np.sum(np.diag(probability)) * measure)
        reduced_a = psi @ psi.conj().T * self.spacing
        one_body_purity = float(np.sum(np.abs(reduced_a) ** 2) * measure)
        overlap = complex(np.vdot(self.orbital_a, self.orbital_b) * self.spacing)
        return JointWavefunctionFrame(
            psi=psi,
            probability=probability,
            coordinates=(self.coordinates, self.coordinates),
            marginal_a=marginal_a,
            marginal_b=marginal_b,
            exchange_symmetry=self.statistics,
            swap_expectation=swap,
            coincidence_probability=coincidence,
            one_body_purity=one_body_purity,
            time=self.time,
            norm=float(np.sum(probability) * measure),
            source="identical_particles_fermion_boson",
            metadata={
                "orbital_overlap_real": overlap.real,
                "orbital_overlap_imag": overlap.imag,
                "grid_points": self.coordinates.size,
                "extent": float(self.coordinates[-1] - self.coordinates[0] + self.spacing),
                "parameters": self._parameters,
            },
        )


__all__ = ["IdenticalParticles1DSource"]
