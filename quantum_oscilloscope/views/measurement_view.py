from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class MeasurementView:
    """Publish basis-measurement and circuit readout state."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        circuit_state = frame.metadata.get("circuit_state")
        if not isinstance(circuit_state, dict):
            return

        osc.send_message(
            "/qmw/circuit/populations",
            [float(value) for value in circuit_state.get("populations", [0.0] * 16)],
        )
        osc.send_message("/qmw/circuit/qasm", str(circuit_state.get("qasm", "")))
        osc.send_message(
            "/qmw/circuit/basis_labels",
            [
                str(value)
                for value in circuit_state.get(
                    "basis_labels",
                    [format(index, "04b") for index in range(16)],
                )
            ],
        )
        osc.send_message(
            "/qmw/circuit/phase_reference",
            int(circuit_state.get("phase_reference", 0)),
        )
        osc.send_message(
            "/qmw/circuit/basis_phases",
            [float(value) for value in circuit_state.get("basis_phases", [0.0] * 16)],
        )
        osc.send_message(
            "/qmw/circuit/phase_quality",
            [float(value) for value in circuit_state.get("phase_quality", [0.0] * 16)],
        )

