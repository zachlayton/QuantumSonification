"""Atomic bounded OSC transport for :class:`QMW44QuantumFrame`."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .qmw_4_4_frame import QMW44QuantumFrame

if TYPE_CHECKING:
    from qmw.performance.four_qubit_preparation import FourQubitPreparationState


QMW44_QUANTUM_OSC_ROOT = "/qmw/4_4/quantum"
QMW44_QUANTUM_OSC_SCHEMA = "qmw.4_4.quantum_frame.osc.v1"
QMW44_QUANTUM_OSC_PORT = 17873


class QMW44QuantumOSCPublisher:
    """Publish a complete frame transaction; never publish rho or H."""

    def __init__(
        self,
        client: object | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = QMW44_QUANTUM_OSC_PORT,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        if not hasattr(client, "send_message"):
            raise ValueError("OSC client must expose send_message().")
        self.client = client

    def publish(
        self,
        frame: QMW44QuantumFrame,
        *,
        preparation: "FourQubitPreparationState | None" = None,
    ) -> int:
        if not isinstance(frame, QMW44QuantumFrame):
            raise ValueError("publish requires a QMW44QuantumFrame.")
        revision = int(frame.revision)
        self.client.send_message(
            f"{QMW44_QUANTUM_OSC_ROOT}/frame/begin",
            [
                revision, float(frame.time), QMW44_QUANTUM_OSC_SCHEMA,
                16, len(frame.current_edges), len(frame.pauli_activity),
                len(frame.current_events),
            ],
        )
        for index, population in enumerate(frame.populations):
            self.client.send_message(
                f"{QMW44_QUANTUM_OSC_ROOT}/population",
                [revision, index, float(population)],
            )
        if preparation is not None:
            self.client.send_message(
                f"{QMW44_QUANTUM_OSC_ROOT}/preparation",
                [
                    revision, preparation.mode, preparation.localized_index,
                    preparation.coherent_theta, preparation.coherent_phase,
                    preparation.squeeze_magnitude, preparation.squeeze_phase,
                    preparation.temperature, preparation.revision,
                ],
            )
        for index, edge in enumerate(frame.current_edges):
            self.client.send_message(
                f"{QMW44_QUANTUM_OSC_ROOT}/current_edge",
                [
                    revision, index, edge.source, edge.destination,
                    float(edge.magnitude), edge.dominant_pauli or "",
                    float(edge.dominant_contribution),
                ],
            )
        for index, activity in enumerate(frame.pauli_activity):
            self.client.send_message(
                f"{QMW44_QUANTUM_OSC_ROOT}/pauli",
                [
                    revision, index, activity.label, activity.weight,
                    float(activity.expectation), float(activity.derivative),
                    float(activity.h_coefficient), float(activity.transport_activity),
                    float(activity.score),
                ],
            )
        diagnostics = frame.diagnostics
        self.client.send_message(
            f"{QMW44_QUANTUM_OSC_ROOT}/diagnostics",
            [
                revision, diagnostics.trace, diagnostics.purity,
                diagnostics.minimum_eigenvalue, diagnostics.hermiticity_error,
                diagnostics.current_antisymmetry_error,
                diagnostics.continuity_linf,
            ],
        )
        for index, event in enumerate(frame.current_events):
            has_phase = event.phase is not None and math.isfinite(float(event.phase))
            self.client.send_message(
                f"{QMW44_QUANTUM_OSC_ROOT}/event",
                [
                    revision, index, event.domain, event.source,
                    event.destination, float(event.magnitude),
                    float(event.phase) if has_phase else 0.0, int(has_phase),
                    event.provenance,
                ],
            )
        self.client.send_message(f"{QMW44_QUANTUM_OSC_ROOT}/frame/end", revision)
        return revision


__all__ = [
    "QMW44_QUANTUM_OSC_PORT", "QMW44_QUANTUM_OSC_ROOT",
    "QMW44_QUANTUM_OSC_SCHEMA", "QMW44QuantumOSCPublisher",
]
