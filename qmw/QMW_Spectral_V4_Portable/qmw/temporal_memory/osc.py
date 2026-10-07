"""Atomic OSC transport for temporal-memory observer frames."""

from __future__ import annotations

from typing import Any, Iterable

from .engine import TemporalMemoryFrame


QMW_TEMPORAL_MEMORY_OSC_ROOT = "/qmw/temporal_memory/v1"
QMW_TEMPORAL_MEMORY_OSC_SCHEMA = "qmw.temporal_memory.osc.v1"
QMW_TEMPORAL_MEMORY_OSC_PORT = 17884


class TemporalMemoryOSCPublisher:
    """Publish one monotonic, complete control transaction per source revision."""

    def __init__(self, clients: Iterable[Any] = ()) -> None:
        self.clients = tuple(clients)
        if not self.clients or any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("at least one OSC client with send_message is required.")
        self._last_revision = -1

    @classmethod
    def from_udp(
        cls, *, host: str = "127.0.0.1", port: int = QMW_TEMPORAL_MEMORY_OSC_PORT,
    ) -> "TemporalMemoryOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(self, frame: TemporalMemoryFrame) -> list[tuple[str, list[Any]]]:
        if not isinstance(frame, TemporalMemoryFrame):
            raise TypeError("frame must be a TemporalMemoryFrame.")
        revision, count = frame.revision, frame.line_count
        messages: list[tuple[str, list[Any]]] = [
            (f"{QMW_TEMPORAL_MEMORY_OSC_ROOT}/frame/begin", [
                revision, frame.time, QMW_TEMPORAL_MEMORY_OSC_SCHEMA, count,
            ]),
        ]
        messages.extend(
            (f"{QMW_TEMPORAL_MEMORY_OSC_ROOT}/line", [
                revision, index, float(frame.harmonic_weights[index]),
                float(frame.delay_seconds[index]), float(frame.excitation[index]),
                float(frame.persistence[index]), float(frame.relative_phase_cycles[index]),
                float(frame.current_activity[index]),
            ])
            for index in range(count)
        )
        for destination in range(count):
            for source in range(count):
                amount = float(frame.cross_feedback[destination, source])
                if amount > 0.0:
                    messages.append((f"{QMW_TEMPORAL_MEMORY_OSC_ROOT}/cross", [
                        revision, destination, source, amount,
                    ]))
        messages.append((f"{QMW_TEMPORAL_MEMORY_OSC_ROOT}/frame/end", [revision]))
        return messages

    def publish(self, frame: TemporalMemoryFrame) -> int | None:
        if not isinstance(frame, TemporalMemoryFrame):
            raise TypeError("frame must be a TemporalMemoryFrame.")
        if frame.revision <= self._last_revision:
            return None
        for address, payload in self.messages(frame):
            for client in self.clients:
                client.send_message(address, payload)
        self._last_revision = frame.revision
        return frame.revision


__all__ = [
    "QMW_TEMPORAL_MEMORY_OSC_PORT", "QMW_TEMPORAL_MEMORY_OSC_ROOT",
    "QMW_TEMPORAL_MEMORY_OSC_SCHEMA", "TemporalMemoryOSCPublisher",
]
