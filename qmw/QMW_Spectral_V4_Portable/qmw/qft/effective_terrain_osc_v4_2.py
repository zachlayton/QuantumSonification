"""Density-matrix effective terrain observer and OSC publisher for QFT V4.2.

This is an attached mesoscopic observer.  The supplied density matrix remains
authoritative: the terrain evolves only its own generalized coordinates and
never writes back into ``rho`` or the QFT scalar-field source.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from qmw.qmw_lagrangian_terrain import (
    DensityLagrangianTerrain,
    LagrangianTerrainFrame,
)
from qmw.qmw_probability_flow import (
    EffectiveTerrainFlowFrame,
    FluxEventState,
    emit_flux_events,
    flow_from_lagrangian_terrain,
)


SCHEMA = "qmw.effective_lagrangian_terrain.osc.v1"
SOURCE_SCHEMA = "qmw.density_matrix.v2"
OSC_ROOT = "/qmw/qft/v4_2/effective_terrain"
OUTPUT_PORT = 17863


class EffectiveTerrainPublisher:
    """Publish atomic terrain and membrane-flow frames for GUI/audio adapters."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.revision = 0

    def publish(
        self,
        terrain: LagrangianTerrainFrame,
        flow: EffectiveTerrainFlowFrame,
        *,
        source_revision: int,
        provider: str,
    ) -> int:
        if flow.current_kind != "effective_terrain":
            raise ValueError("effective-terrain publisher requires effective terrain flow")
        self.revision += 1
        revision = self.revision
        dimension = int(terrain.q.size)
        max_flux = max(
            (boundary.magnitude for boundary in flow.boundary_fluxes),
            default=0.0,
        )
        self.client.send_message(
            f"{OSC_ROOT}/frame/begin",
            [
                revision,
                int(source_revision),
                terrain.time,
                SCHEMA,
                SOURCE_SCHEMA,
                str(provider),
                terrain.basis,
                flow.current_kind,
            ],
        )
        self.client.send_message(f"{OSC_ROOT}/available", [revision, 1])
        self.client.send_message(f"{OSC_ROOT}/dimension", [revision, dimension])
        for name, values in (
            ("populations", terrain.populations),
            ("q", terrain.q),
            ("qdot", terrain.qdot),
            ("mass", terrain.mass),
            ("frequency", terrain.frequency),
        ):
            self.client.send_message(
                f"{OSC_ROOT}/{name}",
                [revision, *np.asarray(values, dtype=float).tolist()],
            )
        for boundary in flow.boundary_fluxes:
            self.client.send_message(
                f"{OSC_ROOT}/boundary",
                [
                    revision,
                    boundary.boundary,
                    boundary.source_region,
                    boundary.destination_region,
                    boundary.direction,
                    boundary.signed_flux,
                    boundary.magnitude,
                    float("nan") if boundary.phase is None else boundary.phase,
                    boundary.current_kind,
                ],
            )
        for event in flow.crossings:
            self.client.send_message(
                f"{OSC_ROOT}/event",
                [
                    revision,
                    event.source_region,
                    event.destination_region,
                    event.boundary,
                    event.direction,
                    event.magnitude,
                    float("nan") if event.phase is None else event.phase,
                    event.current_kind,
                ],
            )
        self.client.send_message(
            f"{OSC_ROOT}/global",
            [
                revision,
                terrain.purity,
                terrain.lagrangian,
                terrain.kinetic_energy,
                terrain.potential_energy,
                terrain.total_energy,
                terrain.damping_power,
                flow.flow_energy,
                flow.coherence_flow,
                max_flux,
                len(flow.crossings),
            ],
        )
        self.client.send_message(f"{OSC_ROOT}/frame/end", revision)
        return revision


class DensityTerrainObserver:
    """Turn successive authoritative ``rho`` frames into published terrain flow."""

    def __init__(
        self,
        publisher: EffectiveTerrainPublisher,
        *,
        event_threshold: float = 0.005,
    ) -> None:
        if not math.isfinite(event_threshold) or event_threshold <= 0.0:
            raise ValueError("event_threshold must be finite and positive")
        self.publisher = publisher
        self.event_threshold = float(event_threshold)
        self.terrain = DensityLagrangianTerrain()
        self.events = FluxEventState()
        self._source_time: float | None = None

    def reset(self) -> None:
        """Begin a new attached trajectory without carrying mesoscopic state."""

        self.terrain.reset()
        self.events = FluxEventState()
        self._source_time = None

    def observe(
        self,
        rho: Any,
        *,
        time: float,
        dt: float,
        source_revision: int,
        provider: str,
    ) -> tuple[LagrangianTerrainFrame, EffectiveTerrainFlowFrame, int]:
        logical_time = float(time)
        step_dt = float(dt)
        if self._source_time is not None and logical_time <= self._source_time:
            # An authoritative QFT state/time reset begins a new trajectory.
            # Do not integrate the mesoscopic terrain across that discontinuity
            # or emit crossings inherited from the previous run.
            self.reset()
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
        return terrain, flow, revision


__all__ = [
    "DensityTerrainObserver",
    "EffectiveTerrainPublisher",
    "OSC_ROOT",
    "OUTPUT_PORT",
    "SCHEMA",
    "SOURCE_SCHEMA",
]
