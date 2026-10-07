"""Bounded atomic OSC projection of a MeasurementFrame; never sends rho or P."""

from __future__ import annotations

import numpy as np

from .engine import MeasurementFrame
from .performance import MeasurementPerformanceState


MEASUREMENT_OSC_ROOT = "/qmw/measure/v1"
MEASUREMENT_OSC_SCHEMA = "qmw.projective_measurement.osc.v1"
# 17874 is the Feynman-composer control receiver and 17875 is the gauge
# resonant-excitation receiver.  Projective observations have their own port.
MEASUREMENT_OSC_PORT = 17876


class MeasurementOSCPublisher:
    def __init__(self, client: object | None = None, *, host: str = "127.0.0.1", port: int = MEASUREMENT_OSC_PORT) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient
            client = SimpleUDPClient(host, int(port))
        if not hasattr(client, "send_message"):
            raise ValueError("OSC client must expose send_message().")
        self.client = client

    def publish(
        self,
        frame: MeasurementFrame,
        *,
        performance: MeasurementPerformanceState | None = None,
        primary_holonomy: float = 0.0,
    ) -> int:
        if not isinstance(frame, MeasurementFrame):
            raise ValueError("publish requires a MeasurementFrame.")
        revision = int(frame.revision)
        self.client.send_message(
            f"{MEASUREMENT_OSC_ROOT}/frame/begin",
            [revision, frame.time, MEASUREMENT_OSC_SCHEMA, frame.bank_id, len(frame.names), int(frame.complete)],
        )
        for index, name in enumerate(frame.names):
            self.client.send_message(
                f"{MEASUREMENT_OSC_ROOT}/channel",
                [revision, index, name, float(frame.probabilities[index]),
                 float(frame.state_current[index]), float(frame.aperture_current[index]),
                 float(frame.total_current[index])],
            )
        if performance is not None:
            self.client.send_message(
                f"{MEASUREMENT_OSC_ROOT}/configuration",
                [revision, performance.bank_mode, performance.pauli_label,
                 performance.aperture_mode, float(performance.aperture_rate),
                 float(performance.gauge_flux), float(primary_holonomy)],
            )
        self.client.send_message(
            f"{MEASUREMENT_OSC_ROOT}/summary",
            [revision, float(frame.shannon_entropy), int(np.argmax(frame.probabilities))],
        )
        self.client.send_message(f"{MEASUREMENT_OSC_ROOT}/frame/end", revision)
        return revision


__all__ = [
    "MEASUREMENT_OSC_PORT", "MEASUREMENT_OSC_ROOT", "MEASUREMENT_OSC_SCHEMA",
    "MeasurementOSCPublisher",
]
