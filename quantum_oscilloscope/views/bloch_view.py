from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class BlochView:
    """Publish reduced Bloch vector observables."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        for key, address in (
            ("bloch_x", "/qmw/bloch/x"),
            ("bloch_y", "/qmw/bloch/y"),
            ("bloch_z", "/qmw/bloch/z"),
        ):
            if key in frame.observables:
                osc.send_message(address, float(frame.observables[key]))

