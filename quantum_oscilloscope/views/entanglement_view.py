from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class EntanglementView:
    """Publish global scalar density/entanglement observables."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        for key, address in (
            ("purity", "/qmw/purity"),
            ("entropy", "/qmw/entropy"),
            ("coherence", "/qmw/coherence"),
            ("entanglement", "/qmw/entanglement"),
        ):
            if key in frame.observables:
                osc.send_message(address, float(frame.observables[key]))

