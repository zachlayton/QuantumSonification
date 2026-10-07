"""Geometry-native modal membrane driven by density terrain and flux."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .flow import FieldBus, FlowFrame
from .geometry import MembraneGeometry
from .numerics import stability_diagnostics
from .terrain import TerrainFrame


Array = np.ndarray


@dataclass(frozen=True)
class MembraneConfig:
    population_mass_depth: float = 0.8
    population_tension_depth: float = 0.7
    coherence_coupling_depth: float = 1.6
    damping_floor: float = 0.025
    coherence_loss_damping: float = 0.22
    field_frequency_depth: float = 1.0
    field_coupling_depth: float = 0.7
    event_impulse_gain: float = 12.0
    motion_output_gain: float = 9.0
    velocity_output_gain: float = 0.8
    max_substep: float = 1.0 / 480.0
    stability_safety: float = 0.8


@dataclass(frozen=True)
class CrossingModalForce:
    source: int
    destination: int
    direction: int
    magnitude: float
    phase: float
    contact_vertex: int
    contact_position: Array
    persistence: int
    transported_probability: float
    modal_weights: Array
    current_kind: str


@dataclass(frozen=True)
class MembraneFrame:
    time: float
    modal_amplitudes: Array
    modal_velocities: Array
    audible_amplitudes: Array
    frequency_ratios: Array
    modal_mass: Array
    modal_stiffness: Array
    modal_damping: Array
    force: Array
    event_impulse: Array
    injected_energy: float
    kinetic_energy: float
    potential_energy: float
    total_energy: float
    lagrangian: float
    omega_max: float
    stability_dt_limit: float
    effective_dt_cap: float
    substeps: int
    actual_substep: float
    crossings: tuple[CrossingModalForce, ...]
    provenance: str = "geometry_native_effective_membrane"


class ResonantMembrane:
    def __init__(
        self,
        geometry: MembraneGeometry,
        config: MembraneConfig | None = None,
    ) -> None:
        self.geometry = geometry
        self.config = config or MembraneConfig()
        count = geometry.mode_shapes.shape[1]
        self.amplitude = np.zeros(count, dtype=float)
        self.velocity = np.zeros(count, dtype=float)

    def reset(self) -> None:
        self.amplitude.fill(0.0)
        self.velocity.fill(0.0)

    def _matrices(
        self,
        terrain: TerrainFrame,
        field: FieldBus,
    ) -> tuple[Array, Array, Array]:
        geometry = self.geometry
        phi = geometry.mode_shapes
        regional_field = np.clip(0.65 * terrain.populations + 0.35 * terrain.q, 0.0, 1.5)
        vertex_mass = geometry.vertex_area * (
            1.0 + self.config.population_mass_depth * regional_field[geometry.regions]
        )
        vertex_stiffness = np.zeros_like(geometry.stiffness)
        for left, right in geometry.edges:
            region_left = int(geometry.regions[left])
            region_right = int(geometry.regions[right])
            distance = float(np.linalg.norm(geometry.vertices[left] - geometry.vertices[right]))
            weight = (
                1.0
                + self.config.population_tension_depth
                * 0.5
                * (regional_field[region_left] + regional_field[region_right])
                + self.config.coherence_coupling_depth
                * terrain.coherence[region_left, region_right]
            ) / max(distance, 1.0e-9)
            vertex_stiffness[left, left] += weight
            vertex_stiffness[right, right] += weight
            vertex_stiffness[left, right] -= weight
            vertex_stiffness[right, left] -= weight
        vertex_stiffness += 0.04 * np.diag(vertex_mass)
        modal_mass = phi.T @ (vertex_mass[:, None] * phi)
        modal_stiffness = phi.T @ vertex_stiffness @ phi
        frequency_scale = np.clip(
            1.0
            + self.config.field_frequency_depth
            * field.modal_frequency_offset_fraction,
            0.55,
            1.65,
        )
        scale_matrix = np.diag(frequency_scale)
        modal_stiffness = scale_matrix @ modal_stiffness @ scale_matrix
        coupling_laplacian = (
            np.diag(np.sum(field.intermodal_coupling, axis=1))
            - field.intermodal_coupling
        )
        stiffness_reference = max(
            float(np.median(np.diag(modal_stiffness))), 1.0e-9
        )
        modal_stiffness += (
            self.config.field_coupling_depth
            * stiffness_reference
            * coupling_laplacian
        )
        dimension = terrain.populations.size
        normalized_coherence = float(np.sum(terrain.coherence)) / max(1, dimension - 1)
        coherence_loss = 1.0 - float(np.clip(normalized_coherence, 0.0, 1.0))
        diagonal_mass = np.maximum(np.diag(modal_mass), 1.0e-9)
        diagonal_stiffness = np.maximum(np.diag(modal_stiffness), 1.0e-9)
        terrain_damping_ratio = (
            self.config.damping_floor
            + self.config.coherence_loss_damping * coherence_loss
        )
        damping_ratio = np.clip(
            0.35 * terrain_damping_ratio + 0.65 * field.modal_damping_ratio,
            self.config.damping_floor,
            0.5,
        )
        modal_damping = np.diag(
            2.0 * damping_ratio * np.sqrt(diagonal_mass * diagonal_stiffness)
        )
        return modal_mass, modal_stiffness, modal_damping

    def step(
        self,
        terrain: TerrainFrame,
        flow: FlowFrame,
        *,
        dt: float,
    ) -> MembraneFrame:
        dt = float(dt)
        if not math.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        phi = self.geometry.mode_shapes
        modal_mass, modal_stiffness, modal_damping = self._matrices(
            terrain, flow.field_bus
        )
        force = np.zeros_like(self.amplitude)
        event_impulse = np.zeros_like(self.amplitude)
        crossing_forces: list[CrossingModalForce] = []
        for crossing in flow.event_bus.crossings:
            weights = phi[crossing.contact_vertex].copy()
            peak = float(np.max(np.abs(weights)))
            if peak > 1.0e-12:
                weights /= peak
            weights *= 0.15 + 0.85 * flow.field_bus.modal_susceptibility
            event_impulse += (
                self.config.event_impulse_gain
                * crossing.transported_probability
                * (0.35 + math.sqrt(min(crossing.magnitude, 2.0)))
                * weights
            )
            crossing_forces.append(
                CrossingModalForce(
                    source=crossing.source,
                    destination=crossing.destination,
                    direction=crossing.direction,
                    magnitude=crossing.magnitude,
                    phase=crossing.phase,
                    contact_vertex=crossing.contact_vertex,
                    contact_position=self.geometry.vertices[crossing.contact_vertex].copy(),
                    persistence=crossing.persistence,
                    transported_probability=crossing.transported_probability,
                    modal_weights=weights,
                    current_kind=crossing.current_kind,
                )
            )
        stability = stability_diagnostics(
            modal_mass,
            modal_stiffness,
            modal_damping,
            dt=dt,
            max_substep=self.config.max_substep,
            safety=self.config.stability_safety,
        )
        kinetic_before_injection = 0.5 * float(
            self.velocity @ modal_mass @ self.velocity
        )
        if np.any(np.abs(event_impulse) > 0.0):
            if float(np.dot(self.velocity, event_impulse)) < 0.0:
                event_impulse *= -1.0
            self.velocity += np.linalg.solve(modal_mass, event_impulse)
        kinetic_after_injection = 0.5 * float(
            self.velocity @ modal_mass @ self.velocity
        )
        injected_energy = max(0.0, kinetic_after_injection - kinetic_before_injection)
        if dt > 0.0:
            h = stability.actual_substep
            for _ in range(stability.substeps):
                rhs = force - modal_damping @ self.velocity - modal_stiffness @ self.amplitude
                acceleration = np.linalg.solve(modal_mass, rhs)
                self.velocity += h * acceleration
                self.amplitude += h * self.velocity
        diagonal_mass = np.maximum(np.diag(modal_mass), 1.0e-9)
        diagonal_stiffness = np.maximum(np.diag(modal_stiffness), 1.0e-9)
        frequencies = np.sqrt(diagonal_stiffness / diagonal_mass)
        ratios = frequencies / max(float(frequencies[0]), 1.0e-9)
        audible = np.tanh(
            self.config.motion_output_gain * self.amplitude
            + self.config.velocity_output_gain * self.velocity
        )
        kinetic = 0.5 * float(self.velocity @ modal_mass @ self.velocity)
        potential = 0.5 * float(self.amplitude @ modal_stiffness @ self.amplitude)
        return MembraneFrame(
            time=terrain.time,
            modal_amplitudes=self.amplitude.copy(),
            modal_velocities=self.velocity.copy(),
            audible_amplitudes=audible,
            frequency_ratios=ratios,
            modal_mass=modal_mass,
            modal_stiffness=modal_stiffness,
            modal_damping=modal_damping,
            force=force,
            event_impulse=event_impulse,
            injected_energy=injected_energy,
            kinetic_energy=kinetic,
            potential_energy=potential,
            total_energy=kinetic + potential,
            lagrangian=kinetic - potential,
            omega_max=stability.omega_max,
            stability_dt_limit=stability.spectral_dt_limit,
            effective_dt_cap=stability.effective_dt_cap,
            substeps=stability.substeps,
            actual_substep=stability.actual_substep,
            crossings=tuple(crossing_forces),
        )


__all__ = [
    "CrossingModalForce",
    "MembraneConfig",
    "MembraneFrame",
    "ResonantMembrane",
]
