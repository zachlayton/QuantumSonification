from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class CircuitDiagnosticsView:
    """Publish detailed circuit and entanglement diagnostics."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        circuit_state = frame.metadata.get("circuit_state")
        if not isinstance(circuit_state, dict):
            return

        single_entropy = frame.observables.get("single_qubit_entropy", {})
        if not isinstance(single_entropy, dict):
            single_entropy = {}

        for qubit in range(4):
            value = float(single_entropy.get(qubit, 0.0))
            osc.send_message(f"/qmw/circuit/q{qubit}_entropy", value)
            osc.send_message(f"/qmw/qubit/{qubit}/entropy", value)

        osc.send_message(
            "/qmw/qubit/mean_entropy",
            float(frame.observables.get("mean_single_entropy", 0.0)),
        )

        for key, address in (
            ("entropy_spread", "/qmw/circuit/entropy_spread"),
            ("entropy_centroid", "/qmw/circuit/entropy_centroid"),
            ("entropy_centroid_norm", "/qmw/circuit/entropy_centroid_norm"),
            ("entropy_motion", "/qmw/circuit/entropy_motion"),
            ("entropy_motion_mean", "/qmw/circuit/entropy_motion_mean"),
        ):
            osc.send_message(address, float(circuit_state.get(key, 0.0)))

        osc.send_message(
            "/qmw/circuit/entropy_motion_vector",
            [
                float(value)
                for value in circuit_state.get(
                    "entropy_motion_vector",
                    [0.0, 0.0, 0.0, 0.0],
                )
            ],
        )
        osc.send_message(
            "/qmw/circuit/entropy_dominant_qubit",
            int(circuit_state.get("entropy_dominant_qubit", 0)),
        )
        osc.send_message("/qmw/circuit/coherence", float(circuit_state.get("coherence", 0.0)))
        osc.send_message("/qmw/circuit/purity", float(circuit_state.get("purity", 0.0)))
        osc.send_message("/qmw/circuit/entropy", float(circuit_state.get("entropy", 0.0)))
        osc.send_message("/qmw/circuit/column", int(circuit_state.get("column", 0)))

        pilot = circuit_state.get("pilot", {})
        osc.send_message("/qmw/circuit/pilot_node", int(self._pilot_value(pilot, "node", 0)))
        osc.send_message(
            "/qmw/circuit/pilot_velocity",
            float(self._pilot_value(pilot, "velocity", 0.0)),
        )
        osc.send_message(
            "/qmw/circuit/phase_gradient",
            float(self._pilot_value(pilot, "phase_gradient", 0.0)),
        )
        osc.send_message(
            "/qmw/circuit/branch_entropy",
            float(self._pilot_value(pilot, "branch_entropy", 0.0)),
        )

        osc.send_message("/qmw/circuit/gate_applied", int(circuit_state.get("gate_applied", 0)))
        osc.send_message("/qmw/circuit/delta_rho", float(circuit_state.get("gate_delta_rho", 0.0)))
        osc.send_message("/qmw/circuit/last_column", int(circuit_state.get("last_gate_column", -1)))
        osc.send_message(
            "/qmw/circuit/last_delta_rho",
            float(circuit_state.get("last_gate_delta_rho", 0.0)),
        )
        osc.send_message("/qmw/circuit/gate_energy", float(circuit_state.get("gate_energy", 0.0)))
        osc.send_message("/qmw/circuit/event_count", int(circuit_state.get("gate_event_count", 0)))

        for key, address in (
            ("entropy_spread", "/qmw/entanglement/entropy_spread"),
            ("entropy_centroid", "/qmw/entanglement/entropy_centroid"),
            ("entropy_centroid_norm", "/qmw/entanglement/entropy_centroid_norm"),
            ("entropy_motion", "/qmw/entanglement/entropy_motion"),
            ("entropy_motion_mean", "/qmw/entanglement/entropy_motion_mean"),
        ):
            osc.send_message(address, float(frame.observables.get(key, 0.0)))

        osc.send_message(
            "/qmw/entanglement/entropy_motion_vector",
            [
                float(value)
                for value in frame.observables.get(
                    "entropy_motion_vector",
                    [0.0, 0.0, 0.0, 0.0],
                )
            ],
        )
        osc.send_message(
            "/qmw/entanglement/entropy_dominant_qubit",
            int(frame.observables.get("entropy_dominant_qubit", 0)),
        )

        bipartition = frame.observables.get("bipartition_entropy", {})
        if not isinstance(bipartition, dict):
            bipartition = {}

        osc.send_message(
            "/qmw/entanglement/partition_01_vs_23",
            float(bipartition.get("01_vs_23", 0.0)),
        )
        osc.send_message(
            "/qmw/entanglement/partition_02_vs_13",
            float(bipartition.get("02_vs_13", 0.0)),
        )
        osc.send_message(
            "/qmw/entanglement/partition_03_vs_12",
            float(bipartition.get("03_vs_12", 0.0)),
        )
        osc.send_message(
            "/qmw/entanglement/mean_bipartition",
            float(frame.observables.get("entanglement", 0.0)),
        )

    @staticmethod
    def _pilot_value(pilot: Any, name: str, default: Any) -> Any:
        if isinstance(pilot, dict):
            return pilot.get(name, default)
        return getattr(pilot, name, default)
