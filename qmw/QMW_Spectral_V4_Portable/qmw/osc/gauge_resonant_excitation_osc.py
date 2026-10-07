"""Atomic OSC publication for downstream gauge-resonant excitation controls."""

from __future__ import annotations

from typing import Any, Iterable

from qmw.mappings.gauge_flow_to_resonance import GaugeResonantExcitationFrame


SCHEMA = "qmw.gauge_resonant_excitation.osc.v1"
OSC_ROOT = "/qmw/gauge/v1/resonant_excitation"
OUTPUT_PORT = 17875


class GaugeResonantExcitationOSCPublisher:
    """Publish complete excitation transactions without altering their source frame."""

    def __init__(self, clients: Iterable[Any] = ()) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.revision = 0

    @classmethod
    def from_udp(
        cls,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> "GaugeResonantExcitationOSCPublisher":
        """Create a publisher for the dedicated opt-in SuperCollider port."""
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(self, frame: GaugeResonantExcitationFrame) -> list[tuple[str, list[Any]]]:
        """Return one revisioned begin/node/edge/end OSC transaction."""
        if not isinstance(frame, GaugeResonantExcitationFrame):
            raise TypeError("frame must be a GaugeResonantExcitationFrame.")
        revision = self.revision
        node_count = int(frame.node_sustained_excitation.size)
        messages: list[tuple[str, list[Any]]] = [
            (
                f"{OSC_ROOT}/frame/begin",
                [
                    revision,
                    float(frame.time),
                    SCHEMA,
                    str(frame.source),
                    node_count,
                    len(frame.directed_routes),
                    int(frame.current_derivative_available),
                    str(frame.frequency_policy),
                ],
            )
        ]
        for node, (sustain, release) in enumerate(
            zip(frame.node_sustained_excitation, frame.node_energy_release)
        ):
            messages.append((
                f"{OSC_ROOT}/node",
                [revision, node, float(sustain), float(release)],
            ))
        for route in frame.directed_routes:
            messages.append((
                f"{OSC_ROOT}/edge",
                [
                    revision,
                    route.edge_index,
                    -1 if route.source_node is None else route.source_node,
                    -1 if route.destination_node is None else route.destination_node,
                    route.signed_current,
                    route.sustained_transport,
                    route.transient_strength,
                ],
            ))
        messages.append((f"{OSC_ROOT}/frame/end", [revision]))
        return messages

    def publish(self, frame: GaugeResonantExcitationFrame) -> int:
        """Send an atomic descriptor transaction and return its revision."""
        revision = self.revision
        for address, payload in self.messages(frame):
            for client in self.clients:
                client.send_message(address, payload)
        self.revision += 1
        return revision


__all__ = [
    "GaugeResonantExcitationOSCPublisher",
    "OSC_ROOT",
    "OUTPUT_PORT",
    "SCHEMA",
]
