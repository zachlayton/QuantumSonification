from __future__ import annotations

import unittest

import numpy as np
from types import SimpleNamespace

try:
    from qiskit import QuantumCircuit, qasm2
except ImportError:  # system Python does not carry the music/Qiskit runtime
    QuantumCircuit = None
    qasm2 = None

from qmw.recursive_wilson import BasisFlow, RecursiveWilsonEngine
from wilson_quantum_geometry_v1 import scala_scale_from_ratios
from examples.qmw_complete_cps_flow_v5 import (
    CompleteCPSFlowMaxHost,
    MODULATION_CC_MAP,
    MPE_MEMBER_CHANNELS,
    TUNING_MODES,
    diamond_ratio,
    mos_morph_projection,
    probability_current_velocity,
    state_modulation_metrics,
)


@unittest.skipIf(QuantumCircuit is None, "Qiskit is required")
class CompleteCPSStateSemanticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RecursiveWilsonEngine()

    def support(self) -> list[int]:
        return np.flatnonzero(np.abs(self.engine.state.data) > 1e-9).tolist()

    def test_probability_current_velocity_has_clear_local_dynamic_contrast(self) -> None:
        weak = probability_current_velocity(0.05, 0.5)
        medium = probability_current_velocity(0.2, 0.5)
        strong = probability_current_velocity(0.5, 0.5)

        self.assertLess(weak, medium)
        self.assertLess(medium, strong)
        self.assertGreaterEqual(strong - weak, 55)
        self.assertGreater(
            probability_current_velocity(0.5, 0.5),
            probability_current_velocity(0.05, 0.05),
        )

    def test_mos_progress_moves_wilson_ratio_between_scale_tree_grids(self) -> None:
        from wilson_quantum_geometry_v1 import MOSScaleTreeNavigator

        navigator = MOSScaleTreeNavigator(4 / 3, (1, 2))
        navigator.begin((3, 7))
        source_ratio, source_activation = mos_morph_projection(7 / 5, navigator.frame())
        navigator.set_progress(0.5)
        middle_ratio, middle_activation = mos_morph_projection(7 / 5, navigator.frame())
        navigator.set_progress(1.0)
        target_ratio, target_activation = mos_morph_projection(7 / 5, navigator.frame())

        self.assertNotAlmostEqual(source_ratio, target_ratio)
        self.assertNotAlmostEqual(middle_ratio, source_ratio)
        self.assertNotAlmostEqual(middle_ratio, target_ratio)
        self.assertAlmostEqual(source_activation, 1.0)
        self.assertGreater(middle_activation, 0.0)
        self.assertAlmostEqual(target_activation, 1.0)

    def test_full_four_by_four_diamond_uses_every_basis_state(self) -> None:
        factors = (1, 3, 5, 7)
        ratios = [diamond_ratio(basis, factors) for basis in range(16)]

        self.assertEqual(len(ratios), 16)
        self.assertEqual([ratios[index] for index in (0, 5, 10, 15)], [1.0] * 4)
        self.assertNotEqual(ratios[1], ratios[4])
        self.assertEqual(TUNING_MODES, ("cps", "diamond", "mos", "scala", "equal"))

    def test_tuning_modes_change_pitch_without_changing_basis_identity(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        host.mos_navigator.begin((2, 5))
        host.mos_navigator.set_progress(1.0)
        host.scala_scale = scala_scale_from_ratios(
            (1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2.0),
            description="test scale",
        )
        results = {}
        for mode in TUNING_MODES:
            host.tuning_mode = mode
            payload = host._basis_note_payload(
                generation=0,
                role=4,
                basis=12,
                partner=12,
                velocity=100,
                duration_ms=100,
                strength=1.0,
                theta=0.0,
                beta=0.0,
                phase=0.0,
                channel=2,
            )
            results[mode] = (payload[2], payload[3], payload[10])

        self.assertTrue(all(result[0] == 12 for result in results.values()))
        self.assertEqual(results["equal"][2], 8192)
        self.assertGreaterEqual(len(set(results.values())), 3)

    def test_note_payload_appends_exact_ratio_and_frequency_for_supercollider(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        payload = host._basis_note_payload(
            generation=0,
            role=1,
            basis=0b0011,
            partner=0,
            velocity=96,
            duration_ms=180,
            strength=0.5,
            theta=0.0,
            beta=0.0,
            phase=0.0,
            channel=2,
        )
        self.assertEqual(len(payload), 16)
        self.assertAlmostEqual(payload[14], 3 / 2)
        expected_pitch = 36 + 24 + 12 * np.log2(3 / 2)
        self.assertAlmostEqual(payload[15], 440 * 2 ** ((expected_pitch - 69) / 12))
        host.tuning_mode = "equal"
        equal_payload = host._basis_note_payload(
            generation=0,
            role=1,
            basis=0b0011,
            partner=0,
            velocity=96,
            duration_ms=180,
            strength=0.5,
            theta=0.0,
            beta=0.0,
            phase=0.0,
            channel=2,
        )
        self.assertAlmostEqual(equal_payload[15], 440 * 2 ** ((equal_payload[3] - 69) / 12))

    def test_scala_geometry_packet_is_atomic_and_maps_all_sixteen_states(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        host.scala_scale = scala_scale_from_ratios(
            (1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2.0),
            description="geometry test",
        )
        packets = []
        host._send = lambda address, payload: packets.append((address, payload))
        host.visual_client = SimpleNamespace(send_message=lambda *_args: None)
        host._publish_scala_geometry()

        self.assertTrue(packets[0][0].endswith("/scala/begin"))
        self.assertTrue(packets[-1][0].endswith("/scala/end"))
        assignments = [payload for address, payload in packets if address.endswith("/assignment")]
        degrees = [payload for address, payload in packets if address.endswith("/degree")]
        structure = [
            payload for address, payload in packets if address.endswith("/constant-structure")
        ]
        self.assertEqual(len(assignments), 16)
        self.assertEqual(len(degrees), len(host.scala_scale.pitch_classes))
        self.assertEqual(len(structure), 1)
        self.assertEqual(structure[0][0], packets[0][1][0])
        self.assertEqual({payload[1] for payload in assignments}, set(range(16)))

    def test_empty_bell_and_ghz_have_distinct_basis_support(self) -> None:
        self.engine.clear_circuit()
        self.assertEqual(self.support(), [0])

        bell = QuantumCircuit(4)
        bell.h(0)
        bell.cx(0, 1)
        self.engine.load_qasm2(qasm2.dumps(bell))
        self.assertEqual(self.support(), [0, 3])

        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)
        self.engine.load_qasm2(qasm2.dumps(ghz))
        self.assertEqual(self.support(), [0, 15])

    def test_programmer_qasm_does_not_inherit_hidden_probe(self) -> None:
        bell = QuantumCircuit(4)
        bell.h(0)
        bell.cx(0, 1)
        self.engine.load_qasm2(qasm2.dumps(bell))
        self.assertNotIn(self.engine.probe_basis, self.support())

    def test_max_temperature_has_pascal_grade_multiplicities(self) -> None:
        self.engine.configure(temperature=2.0)
        weights = self.engine._complete_cps_weights()
        grade_weights = [
            sum(weights[basis] for basis in range(16) if basis.bit_count() == grade)
            for grade in range(5)
        ]
        np.testing.assert_allclose(
            grade_weights,
            np.asarray([1, 4, 6, 4, 1], dtype=float) / 16.0,
        )

    def test_global_modulation_lanes_are_normalized_and_distinguish_entanglement(self) -> None:
        basis = QuantumCircuit(4)
        bell = QuantumCircuit(4)
        bell.h(0)
        bell.cx(0, 1)
        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)

        from qiskit.quantum_info import Statevector

        basis_metrics = state_modulation_metrics(Statevector.from_instruction(basis))
        bell_metrics = state_modulation_metrics(Statevector.from_instruction(bell))
        ghz_metrics = state_modulation_metrics(Statevector.from_instruction(ghz), flow_strength=0.7)
        self.assertEqual(tuple(MODULATION_CC_MAP.values()), tuple(range(20, 28)))
        self.assertTrue(all(0.0 <= value <= 1.0 for values in (basis_metrics, bell_metrics, ghz_metrics) for value in values))
        self.assertAlmostEqual(basis_metrics[2], 0.0)
        self.assertAlmostEqual(bell_metrics[2], 0.5)
        self.assertAlmostEqual(ghz_metrics[2], 1.0)
        self.assertAlmostEqual(ghz_metrics[7], 0.7)

    def test_pascal_scheduler_uses_h_at_a_pole_and_xy_inside_a_grade(self) -> None:
        self.engine.configure(temperature=0.0)
        self.engine.clear_circuit()
        pole_step = self.engine.next_complete_cps()
        self.assertEqual(pole_step.selected_basis, 0)
        self.assertEqual(pole_step.selected_grade, 0)
        self.assertEqual(pole_step.motion, "H")

        self.engine.reset(prepare_probe=True)
        interior_step = self.engine.next_complete_cps()
        self.assertEqual(interior_step.selected_basis, self.engine.probe_basis)
        self.assertEqual(interior_step.selected_grade, 2)
        self.assertEqual(interior_step.motion, "XY")

    def test_bell_and_ghz_publish_distinct_audition_signatures(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        sent: list[tuple[str, list[object]]] = []
        host._send = lambda address, payload: sent.append((address, payload))

        bell = QuantumCircuit(4)
        bell.h(0)
        bell.cx(0, 1)
        host.engine.load_qasm2(qasm2.dumps(bell))
        host._publish_state_signature()
        bell_bases = [payload[2] for _, payload in sent]

        sent.clear()
        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)
        host.engine.load_qasm2(qasm2.dumps(ghz))
        host._publish_state_signature()
        ghz_bases = [payload[2] for _, payload in sent]

        self.assertEqual(bell_bases, [0, 3])
        self.assertEqual(ghz_bases, [0, 15])
        self.assertNotEqual(bell_bases, ghz_bases)
        self.assertEqual(MPE_MEMBER_CHANNELS, tuple(range(2, 17)))

    def test_dynamic_mpe_allocation_preserves_master_and_uses_channel_10(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        channels = []
        for basis in range(16):
            payload = host._basis_note_payload(
                generation=0,
                role=4,
                basis=basis,
                partner=basis,
                velocity=100,
                duration_ms=500,
                strength=1.0,
                theta=0.0,
                beta=0.0,
                phase=0.0,
            )
            channels.append(payload[12])

        self.assertNotIn(1, channels)
        self.assertIn(10, channels)
        self.assertEqual(set(channels), set(range(2, 17)))
        self.assertEqual(len(set(channels[:15])), 15)

    def test_hybrid_recursion_moves_ghz_but_keeps_empty_circuit_silent(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
            full_circuit_generation_limit=0,
        )
        host.visual_client = SimpleNamespace(send_message=lambda *_args: None)
        sent: list[tuple[str, list[object]]] = []
        host._send = lambda address, payload: sent.append((address, payload))

        host.engine.clear_circuit()
        host.circuit_active = False
        host.advance()
        self.assertFalse(any(address.endswith("cps_flow_note") for address, _ in sent))

        sent.clear()
        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)
        host.engine.load_qasm2(qasm2.dumps(ghz))
        host.circuit_active = True
        host.advance()
        self.assertTrue(any(address.endswith("cps_flow_note") for address, _ in sent))

    def test_arrival_only_is_the_default_flow_articulation(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        host.visual_client = SimpleNamespace(send_message=lambda *_args: None)
        sent: list[tuple[str, list[object]]] = []
        host._send = lambda address, payload: sent.append((address, payload))
        host._publish_basis_flows(
            (
                BasisFlow(
                    source_basis_index=0,
                    destination_basis_index=3,
                    probability_flow=0.5,
                    relative_phase=0.0,
                ),
            ),
            generation=1,
            theta=0.5,
            beta=0.0,
        )
        note_payloads = [payload for address, payload in sent if address.endswith("cps_flow_note")]
        self.assertEqual(len(note_payloads), 1)
        self.assertEqual(note_payloads[0][1], 1)  # arrival role
        self.assertEqual(note_payloads[0][2], 3)  # destination basis

    def test_phase4_grade_filter_and_atomic_mos_navigation_packets(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        max_packets: list[tuple[str, list[object]]] = []
        visual_packets: list[tuple[str, list[object]]] = []
        host._send = lambda address, payload: max_packets.append((address, payload))
        host.visual_client = SimpleNamespace(
            send_message=lambda address, payload: visual_packets.append((address, payload))
        )
        host.instrument_grade = 2
        host.mos_navigator.begin((2, 5))
        host.mos_navigator.set_progress(0.5)
        host._publish_navigation()

        addresses = [address for address, _payload in max_packets]
        self.assertEqual(addresses[0], "/qmw/wilson/navigation/frame")
        self.assertEqual(addresses[-1], "/qmw/wilson/navigation/end")
        self.assertEqual(addresses, [address for address, _payload in visual_packets])
        header = max_packets[0][1]
        self.assertEqual(header[1:5], [1, 2, 2, 5])
        self.assertEqual(header[7], 2)
        voice_packets = [payload for address, payload in max_packets if address.endswith("/voice")]
        self.assertEqual([payload[1] for payload in voice_packets], list(range(5)))
        self.assertTrue(host._basis_allowed(3))
        self.assertFalse(host._basis_allowed(1))

    def test_dynamic_hexany_labels_commit_exact_ghz_ratios(self) -> None:
        host = CompleteCPSFlowMaxHost(
            control_port=7593,
            max_port=7594,
            visual_port=7595,
        )
        max_packets: list[tuple[str, list[object]]] = []
        visual_packets: list[tuple[str, list[object]]] = []
        host._send = lambda address, payload: max_packets.append((address, payload))
        host.visual_client = SimpleNamespace(
            send_message=lambda address, payload: visual_packets.append((address, payload))
        )
        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)
        host.engine.load_qasm2(qasm2.dumps(ghz))
        host._retune_from_circuit()

        begin = next(payload for address, payload in visual_packets if address.endswith("/tuning/begin"))
        vertices = [payload for address, payload in visual_packets if address.endswith("/tuning/vertex")]
        end = next(payload for address, payload in visual_packets if address.endswith("/tuning/end"))
        self.assertEqual(begin[4], 6)
        self.assertEqual(len(vertices), 6)
        self.assertEqual(begin[0], end[0])
        by_mask = {payload[2]: payload for payload in vertices}
        self.assertEqual(by_mask[0b0011][3:8], [7, 1, 7, 1, 1])
        self.assertEqual(by_mask[0b0101][3:8], [7, 3, 21, 3, 2])
        self.assertEqual(by_mask[0b1100][3:8], [3, 11, 33, 33, 28])
        self.assertEqual(
            [address for address, _payload in max_packets],
            [address for address, _payload in visual_packets],
        )


if __name__ == "__main__":
    unittest.main()
