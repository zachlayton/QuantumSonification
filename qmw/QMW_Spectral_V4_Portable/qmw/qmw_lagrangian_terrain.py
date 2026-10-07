"""Effective mesoscopic Lagrangian terrain derived from a density matrix.

The density matrix remains authoritative.  This module reads ``rho`` and
constructs a basis-declared resonant terrain for observation, flow
interpretation, OSC, and sound adapters.  It does not update ``rho`` and does
not claim that its generalized coordinates are quantum state variables.

Mapping:

* diagonal populations -> equilibrium, inertia, and local resonance,
* coherence magnitudes -> symmetric coupling and membrane permeability,
* coherence phases -> antisymmetric orientation force.

Damping is an explicit mesoscopic Rayleigh term outside the conservative
Lagrangian.  The frame reports it separately.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np


Array = np.ndarray


def _positive(name: str, value: float, *, allow_zero: bool = False) -> float:
    value = float(value)
    valid = value >= 0.0 if allow_zero else value > 0.0
    if not math.isfinite(value) or not valid:
        qualifier = "nonnegative" if allow_zero else "greater than zero"
        raise ValueError(f"{name} must be finite and {qualifier}.")
    return value


@dataclass(frozen=True)
class LagrangianTerrainConfig:
    """Bounded mapping and integration parameters for the effective terrain."""

    mass_floor: float = 0.25
    population_inertia: float = 0.75
    frequency_floor: float = 0.8
    population_frequency: float = 0.8
    coupling_scale: float = 2.0
    phase_bias_scale: float = 0.5
    permeability_floor: float = 0.05
    coherence_permeability: float = 0.95
    damping: float = 0.35
    max_substep: float = 1.0 / 240.0
    density_tolerance: float = 1.0e-9

    def __post_init__(self) -> None:
        for name in (
            "mass_floor", "frequency_floor", "max_substep", "density_tolerance"
        ):
            _positive(name, getattr(self, name))
        for name in (
            "population_inertia", "population_frequency", "coupling_scale",
            "phase_bias_scale", "permeability_floor", "coherence_permeability",
            "damping",
        ):
            _positive(name, getattr(self, name), allow_zero=True)
        if self.permeability_floor > 1.0:
            raise ValueError("permeability_floor must not exceed one.")


@dataclass(frozen=True)
class LagrangianTerrainFrame:
    """One read-only effective terrain observation and mesoscopic state."""

    time: float
    dt: float
    density_matrix: Array
    populations: Array
    coherence_magnitude: Array
    coherence_phase: Array
    equilibrium: Array
    mass: Array
    frequency: Array
    coupling: Array
    permeability: Array
    phase_force: Array
    q: Array
    qdot: Array
    kinetic_energy: float
    local_potential_energy: float
    coupling_potential_energy: float
    phase_potential_energy: float
    potential_energy: float
    total_energy: float
    lagrangian: float
    damping_power: float
    purity: float
    basis: str = "density_matrix_basis"
    provenance: str = "effective_mesoscopic_terrain"


def _density_matrix(values: Any, tolerance: float) -> Array:
    rho = np.asarray(values, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] == 0:
        raise ValueError("rho must be a nonempty square density matrix.")
    if not np.all(np.isfinite(rho.real)) or not np.all(np.isfinite(rho.imag)):
        raise ValueError("rho must contain only finite values.")
    if not np.allclose(rho, np.conj(rho.T), rtol=tolerance, atol=tolerance):
        raise ValueError("rho must be Hermitian within density_tolerance.")
    trace = complex(np.trace(rho))
    if abs(trace.imag) > tolerance or abs(trace.real - 1.0) > tolerance:
        raise ValueError("rho must have unit trace within density_tolerance.")
    eigenvalues = np.linalg.eigvalsh(rho)
    if float(np.min(eigenvalues)) < -tolerance:
        raise ValueError("rho must be positive semidefinite within density_tolerance.")
    return np.array(rho, dtype=np.complex128, copy=True)


def _terrain_parameters(
    rho: Array, config: LagrangianTerrainConfig
) -> tuple[Array, Array, Array, Array, Array, Array, Array, Array]:
    populations = np.maximum(np.real(np.diag(rho)), 0.0)
    coherence_magnitude = np.abs(rho)
    coherence_phase = np.angle(rho)
    off_diagonal = coherence_magnitude.copy()
    np.fill_diagonal(off_diagonal, 0.0)

    mass = config.mass_floor + config.population_inertia * populations
    frequency = config.frequency_floor + config.population_frequency * populations
    coupling = config.coupling_scale * off_diagonal
    coupling = 0.5 * (coupling + coupling.T)
    phase_alignment = 0.5 * (1.0 + np.cos(coherence_phase))
    permeability = np.clip(
        config.permeability_floor
        + config.coherence_permeability * off_diagonal * phase_alignment,
        0.0,
        1.0,
    )
    permeability = 0.5 * (permeability + permeability.T)
    np.fill_diagonal(permeability, 0.0)

    # Hermiticity makes sin(phi_ij) antisymmetric, hence this orientation
    # force sums to zero across the complete basis graph.
    phase_force = config.phase_bias_scale * np.sum(
        off_diagonal * np.sin(coherence_phase), axis=1
    )
    return (
        populations,
        coherence_magnitude,
        coherence_phase,
        mass,
        frequency,
        coupling,
        permeability,
        phase_force,
    )


class DensityLagrangianTerrain:
    """Stateful mesoscopic terrain driven by successive authoritative ``rho`` frames."""

    def __init__(self, config: LagrangianTerrainConfig | None = None) -> None:
        self.config = config or LagrangianTerrainConfig()
        self._q: Array | None = None
        self._qdot: Array | None = None
        self._time: float | None = None

    def reset(self) -> None:
        self._q = None
        self._qdot = None
        self._time = None

    def step(
        self, rho: Any, *, time: float, dt: float | None = None
    ) -> LagrangianTerrainFrame:
        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite.")
        matrix = _density_matrix(rho, self.config.density_tolerance)
        (
            populations,
            coherence_magnitude,
            coherence_phase,
            mass,
            frequency,
            coupling,
            permeability,
            phase_force,
        ) = _terrain_parameters(matrix, self.config)

        if dt is None:
            dt_value = 0.0 if self._time is None else logical_time - self._time
        else:
            dt_value = float(dt)
        if not math.isfinite(dt_value) or dt_value < 0.0:
            raise ValueError("dt must be finite and nonnegative.")
        if self._time is not None and logical_time <= self._time:
            raise ValueError("time must increase between terrain frames.")

        if self._q is None or self._q.shape != populations.shape:
            q = populations.copy()
            qdot = np.zeros_like(populations)
        else:
            q = self._q.copy()
            qdot = self._qdot.copy()

        stiffness = mass * frequency**2
        laplacian = np.diag(np.sum(coupling, axis=1)) - coupling
        if dt_value > 0.0:
            substeps = max(1, int(math.ceil(dt_value / self.config.max_substep)))
            step_size = dt_value / substeps
            for _ in range(substeps):
                force = (
                    -stiffness * (q - populations)
                    - laplacian @ q
                    + phase_force
                    - self.config.damping * mass * qdot
                )
                qdot += step_size * (force / mass)
                q += step_size * qdot

        difference = q[:, None] - q[None, :]
        kinetic = 0.5 * float(np.sum(mass * qdot**2))
        local_potential = 0.5 * float(np.sum(stiffness * (q - populations) ** 2))
        coupling_potential = 0.25 * float(np.sum(coupling * difference**2))
        phase_potential = -float(np.dot(phase_force, q))
        potential = local_potential + coupling_potential + phase_potential
        damping_power = float(np.sum(self.config.damping * mass * qdot**2))

        self._q = q.copy()
        self._qdot = qdot.copy()
        self._time = logical_time
        return LagrangianTerrainFrame(
            time=logical_time,
            dt=dt_value,
            density_matrix=matrix,
            populations=populations.copy(),
            coherence_magnitude=coherence_magnitude.copy(),
            coherence_phase=coherence_phase.copy(),
            equilibrium=populations.copy(),
            mass=mass.copy(),
            frequency=frequency.copy(),
            coupling=coupling.copy(),
            permeability=permeability.copy(),
            phase_force=phase_force.copy(),
            q=q.copy(),
            qdot=qdot.copy(),
            kinetic_energy=kinetic,
            local_potential_energy=local_potential,
            coupling_potential_energy=coupling_potential,
            phase_potential_energy=phase_potential,
            potential_energy=potential,
            total_energy=kinetic + potential,
            lagrangian=kinetic - potential,
            damping_power=damping_power,
            purity=float(np.real(np.trace(matrix @ matrix))),
        )


__all__ = [
    "DensityLagrangianTerrain",
    "LagrangianTerrainConfig",
    "LagrangianTerrainFrame",
]
