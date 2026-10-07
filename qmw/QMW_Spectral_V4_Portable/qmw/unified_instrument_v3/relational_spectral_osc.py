"""Atomic OSC publication for Unified Instrument V3 relational spectral control."""

from __future__ import annotations

from typing import Any, Iterable

from .frames import MODE_COUNT, RelationalSpectralControlFrame


QMW_RELATIONAL_SPECTRAL_OSC_ROOT = "/qmw/unified/v3/relational_spectral"
QMW_RELATIONAL_SPECTRAL_OSC_SCHEMA = "qmw.unified.relational_spectral.osc.v1"
QMW_RELATIONAL_SPECTRAL_OSC_PORT = 17881


class RelationalSpectralOSCPublisher:
    """Publish one bounded, complete control transaction per graph revision."""

    def __init__(self, clients: Iterable[Any] = ()) -> None:
        self.clients = tuple(clients)
        if not self.clients or any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("at least one OSC client with send_message is required.")
        self._last_revision = -1

    @classmethod
    def from_udp(
        cls,
        *,
        host: str = "127.0.0.1",
        port: int = QMW_RELATIONAL_SPECTRAL_OSC_PORT,
    ) -> "RelationalSpectralOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(self, frame: RelationalSpectralControlFrame) -> list[tuple[str, list[Any]]]:
        if not isinstance(frame, RelationalSpectralControlFrame):
            raise ValueError("frame must be a RelationalSpectralControlFrame.")
        revision = frame.revision
        messages: list[tuple[str, list[Any]]] = [
            (f"{QMW_RELATIONAL_SPECTRAL_OSC_ROOT}/frame/begin", [
                revision,
                frame.time,
                QMW_RELATIONAL_SPECTRAL_OSC_SCHEMA,
                MODE_COUNT,
                len(frame.graph_band_energy),
            ]),
            (f"{QMW_RELATIONAL_SPECTRAL_OSC_ROOT}/scalars", [
                revision,
                frame.bridge_strength,
                frame.segmentation,
                frame.global_connectivity,
                frame.relational_tension,
            ]),
        ]
        messages.extend(
            (f"{QMW_RELATIONAL_SPECTRAL_OSC_ROOT}/band", [revision, index, float(value)])
            for index, value in enumerate(frame.graph_band_energy)
        )
        messages.extend(
            (f"{QMW_RELATIONAL_SPECTRAL_OSC_ROOT}/mode", [
                revision,
                index,
                float(frame.excitation_gain[index]),
                float(frame.decay_scale[index]),
                float(frame.brightness[index]),
            ])
            for index in range(MODE_COUNT)
        )
        messages.append((f"{QMW_RELATIONAL_SPECTRAL_OSC_ROOT}/frame/end", [revision]))
        return messages

    def publish(self, frame: RelationalSpectralControlFrame) -> int | None:
        if frame.revision <= self._last_revision:
            return None
        for address, payload in self.messages(frame):
            for client in self.clients:
                client.send_message(address, payload)
        self._last_revision = frame.revision
        return frame.revision


__all__ = [
    "QMW_RELATIONAL_SPECTRAL_OSC_PORT",
    "QMW_RELATIONAL_SPECTRAL_OSC_ROOT",
    "QMW_RELATIONAL_SPECTRAL_OSC_SCHEMA",
    "RelationalSpectralOSCPublisher",
]
