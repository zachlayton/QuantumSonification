"""Atomic OSC sidecar for QMW Unified Quantum Instrument snapshots."""

from __future__ import annotations

import errno
import math
from typing import Any

import numpy as np

from .envelope import PerformanceSnapshot, StateKind
from .bodies import FourQubitDensityState, HilbertIQFrame


SCHEMA = "qmw.performance.osc.v1"
OSC_ROOT = "/qmw/performance/v1"
OUTPUT_PORT = 17866

_TRANSIENT_SEND_ERRORS = {errno.EAGAIN, errno.EWOULDBLOCK, errno.ENOBUFS}
_SCALAR_CHANNELS = (
    ("site-phi", "mean_phi"),
    ("site-pi", "mean_pi"),
    ("site-energy", "local_energy_density"),
    ("mode-occupations", "mode_occupations"),
    ("mode-frequencies", "frequencies"),
)


def _finite_lane_values(payload: object, attribute: str, lanes: int, label: str) -> list[float]:
    values = np.asarray(getattr(payload, attribute), dtype=float)
    if values.shape != (lanes,) or not np.all(np.isfinite(values)):
        raise ValueError(f"{label} must contain {lanes} finite values")
    return values.tolist()


class PerformanceSnapshotPublisher:
    """Publish an inspector snapshot without changing its native source stream."""

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
        self.dropped_packets = 0

    def _send(self, suffix: str, values: Any) -> None:
        try:
            self.client.send_message(f"{OSC_ROOT}/{suffix}", values)
        except OSError as exc:
            if exc.errno not in _TRANSIENT_SEND_ERRORS:
                raise
            self.dropped_packets += 1

    def publish(
        self,
        snapshot: PerformanceSnapshot,
        *,
        logical_audio_lanes: int,
        gauge_phase: Any | None = None,
    ) -> int:
        header = snapshot.state.header
        stream = snapshot.event_stream
        lanes = int(logical_audio_lanes)
        if lanes < 1:
            raise ValueError("logical_audio_lanes must be positive")
        if (header.source_id, header.source_revision) != (
            stream.source_id,
            stream.source_revision,
        ):
            raise ValueError("state and events must share a source revision")

        revision = header.source_revision
        observers = tuple(snapshot.state.observers.values())
        capabilities = tuple(sorted(header.capabilities))
        self._send(
            "snapshot/begin",
            [
                revision,
                header.source_id,
                header.logical_time,
                SCHEMA,
                len(observers),
                len(stream.events),
                len(capabilities),
                lanes,
            ],
        )
        self._send(
            "state",
            [
                revision,
                header.state_kind.value,
                header.native_schema,
                header.time_domain,
                header.authority.value,
                header.confidence,
                int(header.complete),
            ],
        )
        self._send(
            "basis",
            [
                revision,
                header.basis.name,
                ",".join(str(value) for value in header.basis.shape),
                header.basis.semantics,
                header.basis.ordering,
            ],
        )
        self._send("capabilities", [revision, *capabilities])
        for observer in observers:
            self._send(
                "observer",
                [
                    revision,
                    observer.name,
                    observer.native_schema,
                    observer.authority.value,
                    -1 if observer.source_revision is None else observer.source_revision,
                ],
            )
        self._send("audio/lanes", [revision, lanes])

        if header.state_kind is StateKind.SCALAR_FIELD:
            for suffix, attribute in _SCALAR_CHANNELS:
                values = np.asarray(getattr(snapshot.state.payload, attribute), dtype=float)
                if values.shape != (lanes,) or not np.all(np.isfinite(values)):
                    raise ValueError(
                        f"ScalarField {attribute} must contain {lanes} finite values"
                    )
                self._send(f"scalar/{suffix}", [revision, *values.tolist()])
        elif header.state_kind is StateKind.DENSITY_STATE:
            if not isinstance(snapshot.state.payload, FourQubitDensityState):
                raise ValueError("DensityState inspector payload must be FourQubitDensityState")
            payload = snapshot.state.payload
            self._send(
                "density/populations",
                [revision, *_finite_lane_values(payload, "populations", lanes, "DensityState populations")],
            )
            self._send("density/metrics", [revision, payload.purity, payload.coherence_l1])
        elif header.state_kind is StateKind.HILBERT_IQ:
            if not isinstance(snapshot.state.payload, HilbertIQFrame):
                raise ValueError("HilbertIQ inspector payload must be HilbertIQFrame")
            payload = snapshot.state.payload
            self._send(
                "hilbert/in_phase",
                [revision, *_finite_lane_values(payload, "in_phase", lanes, "Hilbert I/Q in_phase")],
            )
            self._send(
                "hilbert/quadrature",
                [revision, *_finite_lane_values(payload, "quadrature", lanes, "Hilbert I/Q quadrature")],
            )

        for event in stream.events:
            self._send(
                "event",
                [
                    revision,
                    event.event_id,
                    event.event_type,
                    event.logical_time,
                    event.time_domain,
                    -1 if event.lane is None else event.lane,
                    event.authority.value,
                ],
            )
        self._send("snapshot/end", [revision, len(stream.events)])
        if gauge_phase is not None:
            if not math.isclose(float(gauge_phase.time), float(header.logical_time), rel_tol=0.0, abs_tol=1.0e-9):
                raise ValueError("gauge_phase time must match the performance snapshot logical_time.")
            from .gauge_phase_osc import GaugePerformerPhaseOSCPublisher

            GaugePerformerPhaseOSCPublisher(self.client).publish(gauge_phase, source_revision=revision)
        return revision


__all__ = [
    "OSC_ROOT",
    "OUTPUT_PORT",
    "PerformanceSnapshotPublisher",
    "SCHEMA",
]
