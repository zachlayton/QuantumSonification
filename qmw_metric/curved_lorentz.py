"""Trajectory dynamics through the shared effective field."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import LorentzConfig
from .frames import MetricFieldFrame, TrajectoryFrame
from .grid import Grid2D, RealArray


@dataclass(frozen=True)
class ParticleState:
    position: RealArray
    velocity: RealArray
    mass: float = 1.0
    charge: float = 1.0

    def __post_init__(self) -> None:
        position = np.asarray(self.position, dtype=np.float64).copy()
        velocity = np.asarray(self.velocity, dtype=np.float64).copy()
        if position.shape != (2,) or velocity.shape != (2,):
            raise ValueError("position and velocity must have shape (2,)")
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        position.setflags(write=False)
        velocity.setflags(write=False)
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "velocity", velocity)


class CurvedLorentzEngine:
    """Independently gated slope, circulation, and conformal-geodesic terms."""

    def __init__(self, grid: Grid2D, config: LorentzConfig = LorentzConfig()):
        self.grid = grid
        self.config = config

    def force_components(
        self, particle: ParticleState, field: MetricFieldFrame
    ) -> dict[str, RealArray]:
        grad_phi = np.asarray(self.grid.sample(field.grad_potential, particle.position))
        magnetic = float(self.grid.sample(field.vorticity, particle.position))
        vx, vy = particle.velocity
        slope = -particle.charge * grad_phi
        circulation = particle.charge * np.array((vy * magnetic, -vx * magnetic))
        christoffel = np.asarray(
            self.grid.sample(field.christoffel, particle.position), dtype=np.float64
        )
        geodesic_acceleration = -np.einsum(
            "ijk,j,k->i", christoffel, particle.velocity, particle.velocity
        )
        return {
            "slope": slope,
            "circulation": circulation,
            "geodesic": particle.mass * geodesic_acceleration,
        }

    def force(self, particle: ParticleState, field: MetricFieldFrame) -> RealArray:
        terms = self.force_components(particle, field)
        result = np.zeros(2, dtype=np.float64)
        if self.config.topography_mode in ("explicit_force", "hybrid"):
            result += self.config.slope_gain * terms["slope"]
        if self.config.circulation_enabled:
            result += self.config.circulation_gain * terms["circulation"]
        if self.config.topography_mode in ("geodesic", "hybrid"):
            result += self.config.geodesic_gain * terms["geodesic"]
        return result

    def acceleration(self, particle: ParticleState, field: MetricFieldFrame) -> RealArray:
        return self.force(particle, field) / particle.mass

    def step(
        self,
        particle: ParticleState,
        field: MetricFieldFrame,
        dt: float,
        time: float | None = None,
    ) -> tuple[ParticleState, TrajectoryFrame]:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        # Kick-drift-kick.  The second force uses the half-step velocity for the
        # optional velocity-dependent circulation and geodesic terms.
        initial_force = self.force(particle, field)
        half_velocity = particle.velocity + 0.5 * dt * initial_force / particle.mass
        position = self.grid.wrap_position(particle.position + dt * half_velocity)
        midpoint = ParticleState(position, half_velocity, particle.mass, particle.charge)
        force = self.force(midpoint, field)
        velocity = half_velocity + 0.5 * dt * force / particle.mass
        next_particle = ParticleState(position, velocity, particle.mass, particle.charge)
        potential = particle.charge * float(self.grid.sample(field.potential, position))
        frame = TrajectoryFrame(
            time=field.time + dt if time is None else float(time),
            position=position,
            velocity=velocity,
            force=force,
            kinetic_energy=0.5 * particle.mass * float(np.dot(velocity, velocity)),
            potential_energy=potential,
            work_rate=float(np.dot(force, velocity)),
        )
        return next_particle, frame
