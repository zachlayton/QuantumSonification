"""OSC event contract and temporal articulation for SPSA probe pairs."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from .spsa_engine import SPSAStep


@dataclass
class SPSAOSCPublisher:
    client: Any
    root: str = "/qmw/spsa"
    sleep: Callable[[float], None] = time.sleep

    def publish(self, step: SPSAStep, gesture_seconds: float = 0.35) -> None:
        """Publish one step, preserving plus/answer/gradient musical timing."""

        probe_pause = max(0.0, gesture_seconds) / 4.0
        self.client.send_message(
            f"{self.root}/step/begin",
            [step.index, len(step.probes), len(step.gradient)],
        )
        self.client.send_message(
            f"{self.root}/theta/before", [step.index, *step.theta_before.tolist()]
        )

        for probe in step.probes:
            self.client.send_message(
                f"{self.root}/probe/begin", [step.index, probe.index]
            )
            self.client.send_message(
                f"{self.root}/probe/delta",
                [step.index, probe.index, *probe.delta.tolist()],
            )
            self.client.send_message(
                f"{self.root}/probe/plus",
                [step.index, probe.index, probe.expectation_plus],
            )
            self.sleep(probe_pause)
            self.client.send_message(
                f"{self.root}/probe/minus",
                [step.index, probe.index, probe.expectation_minus],
            )
            self.sleep(probe_pause)
            self.client.send_message(
                f"{self.root}/probe/gradient",
                [step.index, probe.index, *probe.gradient.tolist()],
            )
            self.client.send_message(
                f"{self.root}/probe/end",
                [step.index, probe.index, probe.difference],
            )
            self.sleep(probe_pause)

        self.client.send_message(
            f"{self.root}/gradient",
            [step.index, step.gradient_norm, *step.gradient.tolist()],
        )
        self.sleep(probe_pause)
        self.client.send_message(
            f"{self.root}/update",
            [
                step.index,
                step.objective_before,
                step.objective_after,
                *step.theta_after.tolist(),
            ],
        )
        self.client.send_message(f"{self.root}/step/end", step.index)
