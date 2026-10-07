"""V4.2 OSC sidecar for an explicitly attached probability-flow provider.

The V4 scalar-field source does not itself claim this probability-current
payload. V4.2 publishes a separate compatible wavefunction/density-graph
excitation world, time-aligned to the V4 source revision, so consumers can use
the shared ``FlowFrame`` contract without conflating it with V4.1 lattice-energy
transport.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qmw.qmw_probability_flow import FlowFrame

from .live_osc_v4 import SCHEMA as QFT_SOURCE_SCHEMA


SCHEMA = "qmw.probability_flow.osc.v1"
OSC_ROOT = "/qmw/qft/v4_2/probability_flow"
OUTPUT_PORT = 17863


class ProbabilityFlowPublisher:
    """Revisioned, atomic publisher for a generic shared probability-flow frame."""

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
        frame: FlowFrame,
        *,
        source_revision: int,
        provider: str,
    ) -> int:
        self.revision += 1
        revision = self.revision
        self.client.send_message(
            f"{OSC_ROOT}/frame/begin",
            [
                revision,
                int(source_revision),
                frame.time,
                SCHEMA,
                QFT_SOURCE_SCHEMA,
                str(provider),
                frame.representation,
            ],
        )
        self.client.send_message(
            f"{OSC_ROOT}/region/count",
            [revision, int(frame.region_population.size)],
        )
        if frame.coordinates is not None:
            self.client.send_message(
                f"{OSC_ROOT}/basis/continuous_1d",
                [revision, int(frame.density.size)],
            )
            phase = frame.phase if frame.phase is not None else np.zeros_like(frame.density)
            gradient = (
                frame.phase_gradient
                if frame.phase_gradient is not None
                else np.zeros_like(frame.density)
            )
            for index in range(frame.density.size):
                self.client.send_message(
                    f"{OSC_ROOT}/sample",
                    [
                        revision,
                        index,
                        frame.coordinates[index],
                        frame.density[index],
                        phase[index],
                        gradient[index],
                        frame.current[index],
                        frame.divergence[index],
                        int(frame.region_index[index]),
                    ],
                )
        elif frame.edge_indices is not None:
            self.client.send_message(
                f"{OSC_ROOT}/basis/density_graph",
                [revision, int(frame.density.size), int(frame.current.size)],
            )
            for edge, current in zip(frame.edge_indices, frame.current):
                self.client.send_message(
                    f"{OSC_ROOT}/edge",
                    [revision, int(edge[0]), int(edge[1]), current],
                )
            for node, density in enumerate(frame.density):
                self.client.send_message(
                    f"{OSC_ROOT}/node",
                    [revision, node, density, frame.divergence[node], int(frame.region_index[node])],
                )
        for region, (population, flux) in enumerate(zip(frame.region_population, frame.region_flux)):
            self.client.send_message(
                f"{OSC_ROOT}/region",
                [revision, region, population, flux],
            )
        for boundary in frame.boundary_fluxes:
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
                ],
            )
        for event in frame.crossings:
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
                ],
            )
        self.client.send_message(
            f"{OSC_ROOT}/global",
            [
                revision,
                frame.total_probability,
                frame.flow_energy,
                frame.circulation,
                frame.coherence_flow,
                -1.0 if frame.continuity_linf is None else frame.continuity_linf,
            ],
        )
        self.client.send_message(f"{OSC_ROOT}/frame/end", revision)
        return revision


__all__ = ["OSC_ROOT", "OUTPUT_PORT", "ProbabilityFlowPublisher", "SCHEMA"]
