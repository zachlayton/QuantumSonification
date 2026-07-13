from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class TrajectoryView:
    """Publish quantum-trajectory observables."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        osc.send_message(
            "/qmw/trajectory/speed",
            float(frame.observables.get("trajectory_speed", 0.0)),
        )
        osc.send_message(
            "/qmw/trajectory/acceleration",
            float(frame.observables.get("trajectory_acceleration", 0.0)),
        )
        osc.send_message(
            "/qmw/trajectory/direction_change",
            float(frame.observables.get("trajectory_direction_change", 0.0)),
        )

