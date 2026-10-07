"""Bounded OSC transport for read-only QHO configuration-flow observations.

Only compact regional and threshold-event descriptors cross UDP.  The spatial
grid, density matrix, Hamiltonian, and sampled ``n(x)``/``j(x)`` arrays remain
inside the scientific process.
"""

from __future__ import annotations

import math
from time import monotonic
from typing import Any, Callable, Iterable

import numpy as np

from qmw.quantum.qho_configuration import QHOConfigurationFrame


QMW_QHO_CONFIGURATION_OSC_ROOT = "/qmw/qho_configuration/v1"
QMW_QHO_CONFIGURATION_OSC_SCHEMA = "qmw.qho_configuration.osc.v1"
QMW_QHO_CONFIGURATION_OSC_PORT = 17879


class QHOConfigurationOSCPublisher:
    """Publish atomic, bounded regional flux/event observations without a queue."""

    def __init__(
        self,
        clients: Iterable[object] = (),
        *,
        region_limit: int = 16,
        event_limit: int = 16,
        minimum_interval_seconds: float = 1.0 / 60.0,
        monotonic_clock: Callable[[], float] = monotonic,
    ) -> None:
        for name, value in (("region_limit", region_limit), ("event_limit", event_limit)):
            if int(value) != value or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        interval = float(minimum_interval_seconds)
        if not math.isfinite(interval) or interval < 0.0 or not callable(monotonic_clock):
            raise ValueError("minimum interval must be finite/nonnegative and monotonic_clock callable.")
        self.clients = tuple(client for client in clients if client is not None)
        if any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("OSC clients must expose send_message(address, payload).")
        self.region_limit = int(region_limit)
        self.event_limit = int(event_limit)
        self.minimum_interval_seconds = interval
        self._clock = monotonic_clock
        self._last_revision = -1
        self._last_published_at: float | None = None
        self.dropped_stale_frames = 0
        self.dropped_rate_frames = 0

    @classmethod
    def from_udp(
        cls, host: str = "127.0.0.1", port: int = QMW_QHO_CONFIGURATION_OSC_PORT, **kwargs: Any,
    ) -> "QHOConfigurationOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),), **kwargs)

    def reset_revision_gate(self) -> None:
        self._last_revision = -1
        self._last_published_at = None

    def messages(self, frame: QHOConfigurationFrame) -> list[tuple[str, list[Any]]]:
        if not isinstance(frame, QHOConfigurationFrame):
            raise TypeError("publish requires QHOConfigurationFrame.")
        revision = -1 if frame.source_frame_index is None else int(frame.source_frame_index)
        # A raw QHO observation has no source QuantumFrame revision, so derive
        # a deterministic nonnegative sequence from the observer time only at
        # the caller boundary. Live V2 uses sealed-frame observations.
        if revision < 0:
            raise ValueError("OSC publication requires a QHOConfigurationFrame sourced from QuantumFrame.")
        regions = tuple(range(min(frame.flow.region_population.size, self.region_limit)))
        events = tuple(frame.events[: self.event_limit])
        return [
            (f"{QMW_QHO_CONFIGURATION_OSC_ROOT}/frame/begin", [
                revision, float(frame.time), QMW_QHO_CONFIGURATION_OSC_SCHEMA,
                len(regions), len(events),
            ]),
            (f"{QMW_QHO_CONFIGURATION_OSC_ROOT}/summary", [
                revision, float(frame.projected_probability), float(frame.continuity_linf),
                float(np.max(np.abs(frame.current), initial=0.0)),
                float(np.max(np.abs(frame.density_rate_unitary), initial=0.0)),
                float(np.max(np.abs(frame.density_rate_dissipative), initial=0.0)),
            ]),
            *[
                (f"{QMW_QHO_CONFIGURATION_OSC_ROOT}/region", [
                    revision, index, float(frame.flow.region_population[index]),
                    float(frame.flow.region_flux[index]),
                ])
                for index in regions
            ],
            *[
                (f"{QMW_QHO_CONFIGURATION_OSC_ROOT}/event", [
                    revision, index, int(event.source_region), int(event.destination_region),
                    int(event.direction), float(event.magnitude),
                ])
                for index, event in enumerate(events)
            ],
            (f"{QMW_QHO_CONFIGURATION_OSC_ROOT}/frame/end", [revision, len(regions), len(events)]),
        ]

    def publish(self, frame: QHOConfigurationFrame) -> int | None:
        if not isinstance(frame, QHOConfigurationFrame):
            raise TypeError("publish requires QHOConfigurationFrame.")
        revision = -1 if frame.source_frame_index is None else int(frame.source_frame_index)
        if revision <= self._last_revision:
            self.dropped_stale_frames += 1
            return None
        now = float(self._clock())
        if not math.isfinite(now):
            raise ValueError("monotonic_clock must return a finite value.")
        if self._last_published_at is not None and now - self._last_published_at < self.minimum_interval_seconds:
            self.dropped_rate_frames += 1
            return None
        transaction = self.messages(frame)
        for address, payload in transaction:
            for client in self.clients:
                client.send_message(address, payload)
        self._last_revision = revision
        self._last_published_at = now
        return revision


__all__ = [
    "QHOConfigurationOSCPublisher", "QMW_QHO_CONFIGURATION_OSC_PORT",
    "QMW_QHO_CONFIGURATION_OSC_ROOT", "QMW_QHO_CONFIGURATION_OSC_SCHEMA",
]
