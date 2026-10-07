"""Atomic OSC publication of the canonical 20-mode modal geometry frame."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from .frames import MODE_COUNT
from .modal_geometry import ModalGeometryFrame


QMW_MODAL_GEOMETRY_OSC_ROOT = "/qmw/modal"
QMW_MODAL_GEOMETRY_OSC_SCHEMA = "qmw.modal_geometry.osc.v1"
QMW_MODAL_GEOMETRY_OSC_PORT = 17882


class ModalGeometryOSCPublisher:
    """Publish exactly one complete geometry transaction for each frame ID."""

    def __init__(self, clients: Iterable[Any] = ()) -> None:
        self.clients = tuple(clients)
        if not self.clients or any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("at least one OSC client with send_message is required")
        self._last_frame_id = -1

    @classmethod
    def from_udp(
        cls,
        *,
        host: str = "127.0.0.1",
        port: int = QMW_MODAL_GEOMETRY_OSC_PORT,
    ) -> "ModalGeometryOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(self, frame: ModalGeometryFrame) -> list[tuple[str, list[Any]]]:
        if not isinstance(frame, ModalGeometryFrame):
            raise TypeError("frame must be a ModalGeometryFrame")
        frame_id = frame.frame_id
        # The engine keeps its source of truth as frequencies/tuning ratios;
        # recover f0 from that same frame instead of maintaining a duplicate
        # tuning parameter in the transport adapter.
        reference_hz = float(frame.frequency_hz[0] / frame.ratios[0])
        edge_indices = np.argwhere(np.triu(frame.adjacency, 1) > 0.0)
        edge_payload: list[Any] = [frame_id, int(len(edge_indices))]
        for left, right in edge_indices:
            edge_payload.extend((int(left), int(right), float(frame.adjacency[left, right])))
        return [
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/frame/begin", [
                frame_id, frame.time, QMW_MODAL_GEOMETRY_OSC_SCHEMA,
                MODE_COUNT, reference_hz,
            ]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/freqs", [frame_id, *map(float, frame.frequency_hz)]),
            # Keep the reference-relative geometry factor distinct from the
            # combined Scala frequency dictionary. A live source can multiply
            # its own dynamic ratios by geometry**amount without replacement.
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/geometry_ratios", [frame_id, *map(float, frame.geometry_ratio)]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/q", [frame_id, *map(float, frame.quality_factor)]),
            # The eigenvectors are the mode shapes.  Frequency/Q alone are
            # insufficient for a source-position -> modal-bank -> receiver
            # transfer calculation, so this is part of the canonical frame.
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/eigenvectors", [
                frame_id, *map(float, frame.eigenvectors.reshape(-1))
            ]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/xyz", [frame_id, *map(float, frame.spectral_xyz.reshape(-1))]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/eigenvalues", [frame_id, *map(float, frame.eigenvalues)]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/edges", edge_payload),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/connectivity", [
                frame_id, frame.algebraic_connectivity, frame.connected_components,
                frame.spectral_energy,
            ]),
            (f"{QMW_MODAL_GEOMETRY_OSC_ROOT}/frame/end", [frame_id]),
        ]

    def publish(self, frame: ModalGeometryFrame) -> int | None:
        if frame.frame_id <= self._last_frame_id:
            return None
        for address, payload in self.messages(frame):
            for client in self.clients:
                client.send_message(address, payload)
        self._last_frame_id = frame.frame_id
        return frame.frame_id


__all__ = [
    "ModalGeometryOSCPublisher",
    "QMW_MODAL_GEOMETRY_OSC_PORT",
    "QMW_MODAL_GEOMETRY_OSC_ROOT",
    "QMW_MODAL_GEOMETRY_OSC_SCHEMA",
]
