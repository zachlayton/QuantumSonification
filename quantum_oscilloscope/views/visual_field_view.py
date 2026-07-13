from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class VisualFieldView:
    """Publish visual-port field, perturbation, and density delta telemetry."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        density_delta = {
            "/qmw/density/delta_rho/max": float(
                frame.observables.get("density_delta_rho_max", 0.0)
            ),
            "/qmw/density/delta_rho/mean": float(
                frame.observables.get("density_delta_rho_mean", 0.0)
            ),
        }
        for address, value in density_delta.items():
            osc.send_message(address, value)
            visual_osc.send_message(address, value)

        visual = frame.metadata.get("visual", {})
        if not isinstance(visual, dict):
            visual = {}

        for key, address in (
            ("bloch_x", "/qmw/bloch/x"),
            ("bloch_y", "/qmw/bloch/y"),
            ("bloch_z", "/qmw/bloch/z"),
            ("perturbed_bloch_x", "/qmw/bloch/perturbed_x"),
            ("perturbed_bloch_y", "/qmw/bloch/perturbed_y"),
            ("perturbed_bloch_z", "/qmw/bloch/perturbed_z"),
            ("field_strength", "/qmw/visual/field_strength"),
            ("field_acceleration", "/qmw/visual/field_acceleration"),
        ):
            visual_osc.send_message(address, float(visual.get(key, 0.0)))
