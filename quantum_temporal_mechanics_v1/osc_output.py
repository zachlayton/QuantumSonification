"""OSC publishing for the operational temporal-mechanics model."""

from __future__ import annotations

from typing import Any

import numpy as np

from .core import DurationEstimate, EventTimeEstimate, QuantumTemporalMechanics, TemporalDiagnostics


class TemporalMechanicsOSCPublisher:
    ROOT = "/qmw/temporal-mechanics/v1"

    def __init__(self, host: str = "127.0.0.1", port: int = 7443, client: Any = None) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, port)
        self.client = client

    def publish_frame(
        self,
        frame: int,
        mechanics: QuantumTemporalMechanics,
        tick: int,
        events: tuple[tuple[np.ndarray, EventTimeEstimate], ...],
        duration: DurationEstimate,
        diagnostics: TemporalDiagnostics,
    ) -> None:
        root = self.ROOT
        reading = mechanics.reading(tick)
        rho = reading.conditional_state
        populations = np.clip(np.diag(rho).real, 0.0, 1.0)
        purity = float(np.trace(rho @ rho).real)

        self.client.send_message(f"{root}/frame/begin", frame)
        self.client.send_message(
            f"{root}/clock",
            [reading.tick, reading.phase, reading.coordinate, reading.probability],
        )
        self.client.send_message(f"{root}/state/populations", populations.tolist())
        self.client.send_message(f"{root}/state/purity", purity)
        for effect, estimate in events:
            likelihood = float(np.clip(np.trace(effect @ rho).real, 0.0, 1.0))
            self.client.send_message(
                f"{root}/event",
                [estimate.label, likelihood, estimate.probability, estimate.mean_phase, estimate.concentration],
            )
        self.client.send_message(
            f"{root}/duration",
            [duration.first, duration.second, duration.forward_ticks, duration.duration, duration.confidence],
        )
        self.client.send_message(
            f"{root}/diagnostics",
            [
                diagnostics.mean_transition_fidelity,
                diagnostics.closure_fidelity,
                diagnostics.clock_entropy_bits,
                diagnostics.clock_effect_completeness_error,
            ],
        )
        self.client.send_message(f"{root}/frame/end", frame)
