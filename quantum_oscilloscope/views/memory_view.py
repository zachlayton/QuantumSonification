from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class MemoryView:
    """Publish quantum-memory summary observables."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        memory = frame.metadata.get("memory", {})
        if not isinstance(memory, dict):
            return

        osc.send_message("/qmw/memory/size", int(memory.get("size", 0)))
        osc.send_message("/qmw/memory/purity", float(memory.get("purity", 0.0)))
        osc.send_message("/qmw/memory/coherence", float(memory.get("coherence", 0.0)))

