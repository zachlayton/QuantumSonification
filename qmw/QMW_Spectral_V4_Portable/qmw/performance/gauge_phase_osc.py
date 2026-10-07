"""Atomic read-only OSC transport for the gauge performer-phase view."""

from __future__ import annotations

import errno
import math
from typing import Any

from .gauge_phase_view import GaugePerformerPhaseView
from .osc import OSC_ROOT


SCHEMA = "qmw.gauge.performer_phase.osc.v1"
OSC_ROOT_GAUGE_PHASE = f"{OSC_ROOT}/gauge_phase"
_TRANSIENT_SEND_ERRORS = {errno.EAGAIN, errno.EWOULDBLOCK, errno.ENOBUFS}


class GaugePerformerPhaseOSCPublisher:
    """Publish complete phase views to the existing read-only inspector port."""

    def __init__(self, client: Any | None = None, *, host: str = "127.0.0.1", port: int = 17866) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.dropped_packets = 0

    def _send(self, suffix: str, values: list[Any]) -> None:
        try:
            self.client.send_message(f"{OSC_ROOT_GAUGE_PHASE}/{suffix}", values)
        except OSError as error:
            if error.errno not in _TRANSIENT_SEND_ERRORS:
                raise
            self.dropped_packets += 1

    def publish(self, view: GaugePerformerPhaseView, *, source_revision: int) -> int:
        """Publish one all-or-nothing view linked to a source revision."""

        revision = int(source_revision)
        if revision < 0 or not math.isfinite(float(view.time)):
            raise ValueError("source_revision must be nonnegative and view time must be finite.")
        self._send("begin", [revision, view.time, SCHEMA, len(view.node_raw_phase), len(view.edges), len(view.face_holonomies)])
        self._send("nodes", [revision, *view.node_raw_phase])
        for edge in view.edges:
            self._send(
                "edge",
                [revision, edge.source, edge.destination, edge.raw_phase_difference, edge.connection_phase,
                 edge.covariant_phase_difference, edge.current],
            )
        for name, holonomy in view.face_holonomies.items():
            self._send("face", [revision, name, holonomy])
        self._send("end", [revision])
        return revision


__all__ = ["GaugePerformerPhaseOSCPublisher", "OSC_ROOT_GAUGE_PHASE", "SCHEMA"]
