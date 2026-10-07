"""Effective regional Lagrangian terrain read from authoritative ``rho``."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .numerics import stability_diagnostics


Array = np.ndarray


@dataclass(frozen=True)
class TerrainConfig:
    mass_floor: float = 0.35
    population_mass: float = 0.9
    frequency_floor: float = 0.7
    population_frequency: float = 0.9
    coherence_coupling: float = 2.2
    phase_force: float = 0.45
    damping: float = 0.32
    max_substep: float = 1.0 / 240.0
    stability_safety: float = 0.8


@dataclass(frozen=True)
class TerrainFrame:
    time: float
    dt: float
    populations: Array
    coherence: Array
    phase: Array
    mass: Array
    frequency: Array
    coupling: Array
    permeability: Array
    q: Array
    qdot: Array
    kinetic_energy: float
    potential_energy: float
    lagrangian: float
    omega_max: float
    stability_dt_limit: float
    effective_dt_cap: float
    substeps: int
    actual_substep: float
    provenance: str = "effective_mesoscopic_terrain"


class DensityTerrain:
    def __init__(self, config: TerrainConfig | None = None) -> None:
        self.config = config or TerrainConfig()
        self.q: Array | None = None
        self.qdot: Array | None = None

    def reset(self) -> None:
        self.q = None
        self.qdot = None

    def step(self, rho: Array, *, time: float, dt: float) -> TerrainFrame:
        rho = np.asarray(rho, dtype=np.complex128)
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
            raise ValueError("rho must be square")
        if not np.allclose(rho, rho.conj().T, atol=1.0e-9):
            raise ValueError("rho must be Hermitian")
        dt = float(dt)
        if not math.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        populations = np.maximum(np.real(np.diag(rho)), 0.0)
        coherence = np.abs(rho)
        phase = np.angle(rho)
        np.fill_diagonal(coherence, 0.0)
        mass = self.config.mass_floor + self.config.population_mass * populations
        frequency = self.config.frequency_floor + self.config.population_frequency * populations
        coupling = self.config.coherence_coupling * coherence
        coupling = 0.5 * (coupling + coupling.T)
        permeability = np.clip(0.05 + coherence * (0.5 + 0.5 * np.cos(phase)), 0.0, 1.0)
        np.fill_diagonal(permeability, 0.0)
        orientation = self.config.phase_force * np.sum(coherence * np.sin(phase), axis=1)
        if self.q is None or self.q.shape != populations.shape:
            self.q = populations.copy()
            self.qdot = np.zeros_like(populations)
        stiffness = mass * frequency**2
        coupling_laplacian = np.diag(np.sum(coupling, axis=1)) - coupling
        stiffness_matrix = np.diag(stiffness) + coupling_laplacian
        damping_matrix = np.diag(self.config.damping * mass)
        stability = stability_diagnostics(
            mass,
            stiffness_matrix,
            damping_matrix,
            dt=dt,
            max_substep=self.config.max_substep,
            safety=self.config.stability_safety,
        )
        if dt > 0.0:
            h = stability.actual_substep
            for _ in range(stability.substeps):
                force = (
                    -stiffness * (self.q - populations)
                    - coupling_laplacian @ self.q
                    + orientation
                    - self.config.damping * mass * self.qdot
                )
                self.qdot += h * force / mass
                self.q += h * self.qdot
        difference = self.q[:, None] - self.q[None, :]
        kinetic = 0.5 * float(np.sum(mass * self.qdot**2))
        potential = (
            0.5 * float(np.sum(stiffness * (self.q - populations) ** 2))
            + 0.25 * float(np.sum(coupling * difference**2))
            - float(np.dot(orientation, self.q))
        )
        return TerrainFrame(
            time=float(time), dt=dt, populations=populations.copy(),
            coherence=coherence.copy(), phase=phase.copy(), mass=mass,
            frequency=frequency, coupling=coupling, permeability=permeability,
            q=self.q.copy(), qdot=self.qdot.copy(), kinetic_energy=kinetic,
            potential_energy=potential, lagrangian=kinetic - potential,
            omega_max=stability.omega_max,
            stability_dt_limit=stability.spectral_dt_limit,
            effective_dt_cap=stability.effective_dt_cap,
            substeps=stability.substeps,
            actual_substep=stability.actual_substep,
        )


__all__ = ["DensityTerrain", "TerrainConfig", "TerrainFrame"]
