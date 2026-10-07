"""Adaptive V4.3 diagnostics over the unchanged V4.2 terrain contract.

The density matrix remains authoritative. This module changes only the
mesoscopic terrain integrator and publishes a separate diagnostic capability;
it does not modify rho or the V4 Gaussian scalar field.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from qmw.qmw_lagrangian_terrain import (
    DensityLagrangianTerrain,
    LagrangianTerrainConfig,
    LagrangianTerrainFrame,
    _density_matrix,
    _terrain_parameters,
)
from qmw.qmw_probability_flow import (
    FluxEventState,
    emit_flux_events,
    flow_from_lagrangian_terrain,
)

from .effective_terrain_osc_v4_2 import DensityTerrainObserver


OSC_ROOT = "/qmw/qft/v4_3/membrane"
SCHEMA = "qmw.adaptive_resonant_membrane.osc.v4_3"


@dataclass(frozen=True)
class TerrainStabilityDiagnostics:
    omega_max: float
    spectral_dt_limit: float
    effective_dt_cap: float
    substeps: int
    actual_substep: float


class AdaptiveDensityLagrangianTerrain(DensityLagrangianTerrain):
    """Use runtime mass/stiffness spectra to bound semi-implicit substeps."""

    def __init__(
        self,
        config: LagrangianTerrainConfig | None = None,
        *,
        stability_safety: float = 0.8,
    ) -> None:
        super().__init__(config)
        if not math.isfinite(stability_safety) or not 0.0 < stability_safety < 1.0:
            raise ValueError("stability_safety must lie strictly between zero and one")
        self.stability_safety = float(stability_safety)
        self.last_stability = TerrainStabilityDiagnostics(0.0, math.inf, 0.0, 0, 0.0)

    def step(
        self, rho: Any, *, time: float, dt: float | None = None
    ) -> LagrangianTerrainFrame:
        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite")
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
            raise ValueError("dt must be finite and nonnegative")
        if self._time is not None and logical_time <= self._time:
            raise ValueError("time must increase between terrain frames")

        if self._q is None or self._q.shape != populations.shape:
            q = populations.copy()
            qdot = np.zeros_like(populations)
        else:
            q = self._q.copy()
            qdot = self._qdot.copy()

        stiffness = mass * frequency**2
        laplacian = np.diag(np.sum(coupling, axis=1)) - coupling
        stiffness_matrix = np.diag(stiffness) + laplacian
        inverse_root_mass = np.diag(1.0 / np.sqrt(mass))
        normalized_stiffness = inverse_root_mass @ stiffness_matrix @ inverse_root_mass
        normalized_stiffness = 0.5 * (
            normalized_stiffness + normalized_stiffness.T
        )
        lambda_max = max(0.0, float(np.max(np.linalg.eigvalsh(normalized_stiffness))))
        omega_max = math.sqrt(lambda_max)
        oscillator_limit = (
            math.inf
            if omega_max <= 1.0e-15
            else (2.0 * self.stability_safety) / omega_max
        )
        damping_rate = self.config.damping
        damping_limit = (
            math.inf
            if damping_rate <= 1.0e-15
            else (2.0 * self.stability_safety) / damping_rate
        )
        spectral_limit = min(oscillator_limit, damping_limit)
        effective_cap = min(self.config.max_substep, spectral_limit)
        substeps = (
            0
            if dt_value == 0.0
            else max(1, int(math.ceil(dt_value / effective_cap)))
        )
        actual_substep = 0.0 if substeps == 0 else dt_value / substeps
        self.last_stability = TerrainStabilityDiagnostics(
            omega_max=omega_max,
            spectral_dt_limit=spectral_limit,
            effective_dt_cap=effective_cap,
            substeps=substeps,
            actual_substep=actual_substep,
        )

        for _ in range(substeps):
            force = (
                -stiffness * (q - populations)
                - laplacian @ q
                + phase_force
                - self.config.damping * mass * qdot
            )
            qdot += actual_substep * (force / mass)
            q += actual_substep * qdot

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


class V43DensityTerrainObserver(DensityTerrainObserver):
    """Retain V4.2 publication and add an atomic V4.3 diagnostic stream."""

    def __init__(self, publisher: Any, *, event_threshold: float = 0.005) -> None:
        super().__init__(publisher, event_threshold=event_threshold)
        self.terrain = AdaptiveDensityLagrangianTerrain()

    def observe(
        self,
        rho: Any,
        *,
        time: float,
        dt: float,
        source_revision: int,
        provider: str,
    ):
        logical_time = float(time)
        step_dt = float(dt)
        if self._source_time is not None and logical_time <= self._source_time:
            self.reset()
            self.terrain = AdaptiveDensityLagrangianTerrain()
            step_dt = 0.0
        terrain = self.terrain.step(rho, time=logical_time, dt=step_dt)
        self._source_time = logical_time
        flow = flow_from_lagrangian_terrain(terrain)
        flow, self.events = emit_flux_events(
            flow,
            self.events,
            dt=terrain.dt,
            threshold=self.event_threshold,
        )
        revision = self.publisher.publish(
            terrain,
            flow,
            source_revision=source_revision,
            provider=provider,
        )
        stability = self.terrain.last_stability
        client = self.publisher.client
        client.send_message(
            f"{OSC_ROOT}/frame/begin",
            [revision, int(source_revision), logical_time, SCHEMA],
        )
        client.send_message(f"{OSC_ROOT}/available", [revision, 1])
        client.send_message(
            f"{OSC_ROOT}/rho/real",
            [revision, *terrain.density_matrix.real.ravel().tolist()],
        )
        client.send_message(
            f"{OSC_ROOT}/rho/imag",
            [revision, *terrain.density_matrix.imag.ravel().tolist()],
        )
        client.send_message(
            f"{OSC_ROOT}/stability",
            [
                revision,
                stability.omega_max,
                stability.spectral_dt_limit,
                stability.effective_dt_cap,
                stability.substeps,
                stability.actual_substep,
            ],
        )
        max_flux = max(
            (boundary.magnitude for boundary in flow.boundary_fluxes),
            default=0.0,
        )
        signed_flux = sum(
            boundary.signed_flux for boundary in flow.boundary_fluxes
        )
        total_flux = sum(
            boundary.magnitude for boundary in flow.boundary_fluxes
        )
        client.send_message(
            f"{OSC_ROOT}/flow",
            [
                revision,
                flow.flow_energy,
                flow.coherence_flow,
                max_flux,
                signed_flux,
                len(flow.boundary_fluxes),
                total_flux,
            ],
        )
        client.send_message(f"{OSC_ROOT}/frame/end", revision)
        return terrain, flow, revision


__all__ = [
    "AdaptiveDensityLagrangianTerrain",
    "OSC_ROOT",
    "SCHEMA",
    "TerrainStabilityDiagnostics",
    "V43DensityTerrainObserver",
]
