from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class BohmView:
    """Publish Bohmian pilot-wave diagnostics."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        bohm = frame.metadata.get("bohm", {})
        if not isinstance(bohm, dict):
            return

        values = {
            "/qmw/bohm/x": float(bohm.get("x", 0.0)),
            "/qmw/bohm/velocity": float(bohm.get("velocity", 0.0)),
            "/qmw/bohm/speed": float(bohm.get("speed", 0.0)),
            "/qmw/bohm/phase": float(bohm.get("phase", 0.0)),
            "/qmw/bohm/density": float(bohm.get("density", 0.0)),
            "/qmw/bohm/node_proximity": float(bohm.get("node_proximity", 0.0)),
            "/qmw/bohm/curvature": float(bohm.get("curvature", 0.0)),
            "/qmw/bohm/field_velocity": float(bohm.get("field_velocity", 0.0)),
            "/qmw/bohm/position": float(bohm.get("x", 0.0)),
            "/qmw/bohm/local_density": float(bohm.get("density", 0.0)),
            "/qmw/bohm/field_curvature": float(bohm.get("curvature", 0.0)),
        }

        for address, value in values.items():
            osc.send_message(address, value)
            visual_osc.send_message(address, value)
