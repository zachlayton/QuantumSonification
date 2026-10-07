"""Atomic OSC transport for admitted-event harmonic-memory development frames."""

from __future__ import annotations

from typing import Any, Iterable

from .development import HarmonicMemoryDevelopmentFrame


QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT = "/qmw/harmonic_memory_development/v1"
QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_SCHEMA = "qmw.harmonic_memory_development.osc.v1"
QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_PORT = 17886


class HarmonicMemoryDevelopmentOSCPublisher:
    """Publish one complete frame for each explicitly admitted memory event."""

    def __init__(self, clients: Iterable[Any] = ()) -> None:
        self.clients = tuple(clients)
        if not self.clients or any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("at least one OSC client with send_message is required.")
        self._last_revision = 0

    @classmethod
    def from_udp(
        cls, *, host: str = "127.0.0.1", port: int = QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_PORT,
    ) -> "HarmonicMemoryDevelopmentOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(self, frame: HarmonicMemoryDevelopmentFrame) -> list[tuple[str, list[Any]]]:
        if not isinstance(frame, HarmonicMemoryDevelopmentFrame):
            raise TypeError("frame must be a HarmonicMemoryDevelopmentFrame.")
        revision, series = frame.revision, frame.series
        messages: list[tuple[str, list[Any]]] = [
            (f"{QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT}/frame/begin", [
                revision, frame.source_revision, frame.time,
                QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_SCHEMA, series.event_index,
            ]),
            (f"{QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT}/series", [
                revision, series.injection, series.harmonic, series.harmonic2,
                series.euler_sum, series.residual, series.event_write,
                series.persistence, series.topology_index, series.recursion_index,
                series.instability, series.euler_exponent,
            ]),
        ]
        messages.extend(
            (f"{QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT}/node", [
                revision, index, float(frame.node_population[index]),
                float(frame.event_injection[index]), float(frame.self_persistence[index]),
                float(frame.delay_seconds[index]),
            ])
            for index in range(4)
        )
        messages.append((f"{QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT}/frame/end", [revision]))
        return messages

    def publish(self, frame: HarmonicMemoryDevelopmentFrame) -> int | None:
        if not isinstance(frame, HarmonicMemoryDevelopmentFrame):
            raise TypeError("frame must be a HarmonicMemoryDevelopmentFrame.")
        if frame.revision <= self._last_revision:
            return None
        for address, payload in self.messages(frame):
            for client in self.clients:
                client.send_message(address, payload)
        self._last_revision = frame.revision
        return frame.revision


__all__ = [
    "HarmonicMemoryDevelopmentOSCPublisher",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_PORT",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_SCHEMA",
]
