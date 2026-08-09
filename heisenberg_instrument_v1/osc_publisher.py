"""OSC publication contract for the Heisenberg 16 x 16 transition field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .three_experiments import ExperimentResult
from .transition_matrix import TransitionMatrixFrame


@dataclass
class HeisenbergOSCPublisher:
    client: Any
    root: str = "/qmw/heisenberg"
    revision: int = 0

    def publish_case(
        self,
        result: ExperimentResult,
        frame: TransitionMatrixFrame,
        *,
        active: bool = False,
    ) -> None:
        prefix = f"{self.root}/{result.mode.value}"
        self._publish(prefix, result, frame)
        if active:
            self._publish(f"{self.root}/active", result, frame)

    def _publish(
        self,
        prefix: str,
        result: ExperimentResult,
        frame: TransitionMatrixFrame,
    ) -> None:
        self.revision += 1
        self.client.send_message(f"{prefix}/mode", result.mode.value)
        self.client.send_message(
            f"{prefix}/outcome", -1 if result.outcome is None else result.outcome
        )
        self.client.send_message(
            f"{prefix}/probabilities", list(result.outcome_probabilities)
        )
        self.client.send_message(
            f"{prefix}/disturbance", float(result.measurement_disturbance)
        )
        self.client.send_message(
            f"{prefix}/coherence_before", float(result.coherence_before)
        )
        self.client.send_message(
            f"{prefix}/coherence_after", float(result.coherence_after)
        )

        payloads = frame.osc_payloads()
        self.client.send_message(
            f"{prefix}/matrix/begin", [self.revision, frame.dimension]
        )
        for name in (
            "dimension",
            "magnitude",
            "magnitude_normalized",
            "phase",
            "signed_gap",
            "frequency_hz",
            "pan",
            "real",
            "imag",
            "expectation_real",
            "expectation_imag",
            "reconstruction_error",
            "audio_scale_factor",
        ):
            self.client.send_message(f"{prefix}/matrix/{name}", payloads[name])
        self.client.send_message(f"{prefix}/matrix/end", self.revision)
