from __future__ import annotations

import json
import math
import unittest

import numpy as np

from zx_modular_v1 import (
    PauliGadgetSpec,
    ZXDiagram,
    RewriteOSCVerifier,
    VisualGraphMirror,
    compile_hybrid_max_vcv_plan,
    can_fuse_score_gadgets,
    compile_modular_plan,
    density_frame_from_visual_graph,
    fuse_spiders,
    fuse_score_gadgets,
    get_rule,
    linear_map,
    pauli_expectation,
    pauli_operator,
    pauli_rotation_matrix,
    pauli_score_matrix,
    pauli_strings_commute,
    pauli_weight,
    normalized_state,
    remove_identity_spider,
    rule_catalog,
    verify_visual_pauli_gadget,
    verify_visual_pauli_score,
)
from zx_modular_v1.semantics import HADAMARD
from zx_modular_v1.rack_osc import rack_frame_from_state


def phase_chain(color: str, alpha: float, beta: float) -> ZXDiagram:
    diagram = ZXDiagram(f"{color}_phase_chain")
    diagram.add_boundary("input", "input", 0)
    diagram.add_spider("first", color, alpha)
    diagram.add_spider("second", color, beta)
    diagram.add_boundary("output", "output", 0)
    diagram.connect("e0", "input", "first")
    diagram.connect("e1", "first", "second")
    diagram.connect("e2", "second", "output")
    return diagram


class ZXSemanticsTests(unittest.TestCase):
    def test_zero_phase_z_and_x_spiders_are_identity_maps(self) -> None:
        for color in ("z", "x"):
            with self.subTest(color=color):
                diagram = phase_chain(color, 0.0, 0.0)
                fused = fuse_spiders(diagram, "first", "second").diagram
                np.testing.assert_allclose(linear_map(fused), np.eye(2), atol=1e-12)

    def test_z_phase_is_a_dual_rail_phase_rotation(self) -> None:
        theta = 0.37
        diagram = phase_chain("z", theta, 0.0)
        result = fuse_spiders(diagram, "first", "second").diagram
        expected = np.diag([1.0, np.exp(1j * theta)])
        np.testing.assert_allclose(linear_map(result), expected, atol=1e-12)

    def test_hadamard_wire_has_hadamard_semantics(self) -> None:
        diagram = ZXDiagram("hadamard_wire")
        diagram.add_boundary("input", "input", 0)
        diagram.add_boundary("output", "output", 0)
        diagram.connect("h", "input", "output", kind="hadamard")
        np.testing.assert_allclose(linear_map(diagram), HADAMARD, atol=1e-12)

    def test_zero_phase_z_spider_prepares_a_bell_pair(self) -> None:
        diagram = ZXDiagram("bell_pair")
        diagram.add_spider("z", "z", 0.0)
        diagram.add_boundary("out_0", "output", 0)
        diagram.add_boundary("out_1", "output", 1)
        diagram.connect("e0", "z", "out_0")
        diagram.connect("e1", "z", "out_1")
        expected = np.array([1.0, 0.0, 0.0, 1.0]) / math.sqrt(2.0)
        np.testing.assert_allclose(normalized_state(diagram), expected, atol=1e-12)

    def test_boundary_zero_is_the_least_significant_basis_bit(self) -> None:
        diagram = ZXDiagram("q0_lsb_product_state")
        diagram.add_spider("prepare_q0_one", "x", math.pi)
        diagram.add_spider("prepare_q1_zero", "x", 0.0)
        diagram.add_boundary("out_0", "output", 0)
        diagram.add_boundary("out_1", "output", 1)
        diagram.connect("e0", "prepare_q0_one", "out_0")
        diagram.connect("e1", "prepare_q1_zero", "out_1")
        expected = np.array([0.0, 1.0, 0.0, 0.0])
        np.testing.assert_allclose(normalized_state(diagram), expected, atol=1e-12)


class ZXRewriteTests(unittest.TestCase):
    def test_rule_catalog_covers_core_zx_and_zxh_layers(self) -> None:
        catalog = {item["rule_id"]: item for item in rule_catalog()}
        required = {
            "spider_fusion",
            "identity_removal",
            "pi_copy",
            "state_copy",
            "bialgebra",
            "hopf",
            "local_complementation",
            "pivot",
            "cnot",
            "h_box",
            "absorb",
        }
        self.assertTrue(required.issubset(catalog))
        self.assertEqual(get_rule("cnot").kind, "macro")
        self.assertEqual(get_rule("absorb").calculus, "ZXH")
        self.assertEqual(get_rule("spider_fusion").status, "live_verified")

    def test_spider_fusion_preserves_z_and_x_semantics(self) -> None:
        for color in ("z", "x"):
            with self.subTest(color=color):
                report = fuse_spiders(phase_chain(color, 0.21, -0.82), "first", "second")
                self.assertTrue(report.preserved)
                self.assertLess(report.absolute_error, 1e-12)
                self.assertNotIn("second", report.diagram.nodes)

    def test_identity_removal_preserves_z_and_x_semantics(self) -> None:
        for color in ("z", "x"):
            with self.subTest(color=color):
                diagram = ZXDiagram(f"{color}_identity")
                diagram.add_boundary("input", "input", 0)
                diagram.add_spider("identity", color, 0.0)
                diagram.add_boundary("output", "output", 0)
                diagram.connect("a", "input", "identity")
                diagram.connect("b", "identity", "output")
                report = remove_identity_spider(diagram, "identity")
                self.assertTrue(report.preserved)
                np.testing.assert_allclose(
                    linear_map(report.diagram),
                    np.eye(2),
                    atol=1e-12,
                )

    def test_mixed_color_fusion_is_rejected(self) -> None:
        diagram = ZXDiagram("mixed")
        diagram.add_boundary("input", "input", 0)
        diagram.add_spider("z", "z")
        diagram.add_spider("x", "x")
        diagram.add_boundary("output", "output", 0)
        diagram.connect("a", "input", "z")
        diagram.connect("b", "z", "x")
        diagram.connect("c", "x", "output")
        with self.assertRaisesRegex(ValueError, "same color"):
            fuse_spiders(diagram, "z", "x")

    def test_processing_fusion_is_locally_verified_and_applied(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "Z", 0.3, 0.4, 0.21)
        graph.add_node(3, "Z", 0.6, 0.5, -0.82)
        graph.add_node(4, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        graph.add_edge(3, 4)

        result = graph.verify_and_apply_fusion(
            2,
            3,
            "Z",
            math.remainder(0.21 - 0.82, 2.0 * math.pi),
        )

        self.assertTrue(result.verified)
        self.assertLess(result.absolute_error, 1e-12)
        self.assertNotIn(3, graph.nodes)
        self.assertEqual(len(graph.edges), 2)

    def test_processing_fusion_rejects_wrong_phase(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.3, 0.4, 0.2)
        graph.add_node(2, "Z", 0.6, 0.5, 0.4)
        graph.add_edge(1, 2)

        result = graph.verify_and_apply_fusion(1, 2, "Z", 1.2)

        self.assertFalse(result.verified)
        self.assertIn("fused phase", result.message)
        self.assertIn(2, graph.nodes)

    def test_processing_euler_selection_extracts_exact_one_wire_tensor(
        self,
    ) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "Z", 0.3, 0.5, 0.37)
        graph.add_node(3, "X", 0.6, 0.5, -0.22)
        graph.add_node(4, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        graph.add_edge(3, 4)

        actual = graph.one_qubit_chain_matrix([3, 2])
        hadamard = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
        z = np.diag([1, np.exp(0.37j)])
        x = hadamard @ np.diag([1, np.exp(-0.22j)]) @ hadamard

        np.testing.assert_allclose(actual, x @ z, atol=1e-12)

    def test_processing_euler_selection_rejects_a_branch(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "Z", 0.5, 0.5, 0.37)
        graph.add_node(3, "B", 1.0, 0.4, 0.0)
        graph.add_node(4, "B", 1.0, 0.6, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        graph.add_edge(2, 4)

        with self.assertRaisesRegex(ValueError, "degree two"):
            graph.one_qubit_chain_matrix([2])

    def test_processing_euler_request_is_verified_and_fanned_out(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.graph = VisualGraphMirror()
        verifier.graph.add_node(1, "B", 0.0, 0.5, 0.0)
        verifier.graph.add_node(2, "Z", 0.3, 0.5, 0.37)
        verifier.graph.add_node(3, "X", 0.6, 0.5, -0.22)
        verifier.graph.add_node(4, "B", 1.0, 0.5, 0.0)
        verifier.graph.add_edge(1, 2)
        verifier.graph.add_edge(2, 3)
        verifier.graph.add_edge(3, 4)
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier.tomography_client = Capture()

        verifier._on_euler_request("", 51, 2, 2, 3)

        for target in (
            verifier.client,
            verifier.max_density_client,
            verifier.tomography_client,
        ):
            self.assertEqual(
                target.messages[0][0],
                "/qmw/zx/euler/result",
            )
            payload = target.messages[0][1]
            self.assertEqual(payload[0], 51)
            self.assertEqual(payload[3], "ZXZ")
            self.assertEqual(payload[9], 1)
            self.assertLess(payload[10], 1e-10)

    def test_processing_identity_and_color_change_are_tensor_verified(
        self,
    ) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "Z", 0.5, 0.5, 0.0)
        graph.add_node(3, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)

        identity = graph.apply_selected_rule("identity_removal", [2])
        self.assertTrue(identity.verified)
        self.assertNotIn(2, graph.nodes)
        self.assertEqual(len(graph.edges), 1)

        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "Z", 0.5, 0.5, 0.37)
        graph.add_node(3, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        changed = graph.apply_selected_rule("color_change", [2])
        self.assertTrue(changed.verified)
        self.assertEqual(graph.nodes[2].kind, "X")
        self.assertTrue(
            all(edge.kind == "hadamard" for edge in graph.edges)
        )

    def test_processing_local_complementation_and_pivot_are_verified(
        self,
    ) -> None:
        local = VisualGraphMirror()
        local.add_node(1, "Z", 0.3, 0.5, math.pi / 2.0)
        for qubit in range(3):
            neighbor = qubit + 2
            boundary = qubit + 10
            local.add_node(neighbor, "Z", 0.6, float(qubit), 0.0)
            local.add_node(
                boundary,
                "B",
                0.9,
                float(qubit),
                0.0,
                "output",
                qubit,
            )
            local.add_edge(1, neighbor, "hadamard")
            local.add_edge(neighbor, boundary)

        complemented = local.apply_selected_rule(
            "local_complementation",
            [1],
        )
        self.assertTrue(complemented.verified)
        self.assertLess(complemented.absolute_error, 1e-12)
        self.assertNotIn(1, local.nodes)
        neighbor_edges = {
            frozenset((edge.source, edge.target))
            for edge in local.edges
            if edge.source in {2, 3, 4} and edge.target in {2, 3, 4}
        }
        self.assertEqual(
            neighbor_edges,
            {
                frozenset((2, 3)),
                frozenset((2, 4)),
                frozenset((3, 4)),
            },
        )

        pivot_graph = VisualGraphMirror()
        pivot_graph.add_node(1, "Z", 0.3, 0.4, 0.0)
        pivot_graph.add_node(2, "Z", 0.3, 0.6, 0.0)
        pivot_graph.add_edge(1, 2, "hadamard")
        for qubit in range(4):
            neighbor = qubit + 3
            boundary = qubit + 10
            pivot_graph.add_node(
                neighbor,
                "Z",
                0.6,
                float(qubit),
                0.0,
            )
            pivot_graph.add_node(
                boundary,
                "B",
                0.9,
                float(qubit),
                0.0,
                "output",
                qubit,
            )
            pivot_graph.add_edge(
                1 if qubit < 2 else 2,
                neighbor,
                "hadamard",
            )
            pivot_graph.add_edge(neighbor, boundary)

        pivoted = pivot_graph.apply_selected_rule("pivot", [1, 2])
        self.assertTrue(pivoted.verified)
        self.assertLess(pivoted.absolute_error, 1e-12)
        self.assertNotIn(1, pivot_graph.nodes)
        self.assertNotIn(2, pivot_graph.nodes)

    def test_processing_copy_bialgebra_and_hopf_rules(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "X", 0.2, 0.5, 0.0)
        graph.add_node(2, "Z", 0.5, 0.5, 0.0)
        graph.add_node(3, "B", 0.9, 0.3, 0.0)
        graph.add_node(4, "B", 0.9, 0.7, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        graph.add_edge(2, 4)
        copied = graph.apply_selected_rule("state_copy", [1])
        self.assertTrue(copied.verified)
        self.assertEqual(
            sorted(node.kind for node in graph.nodes.values()),
            ["B", "B", "X", "X"],
        )

        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.4, 0.5, 0.0)
        graph.add_node(2, "X", 0.6, 0.5, 0.0)
        for node_id, x, y, owner in (
            (3, 0.0, 0.3, 1),
            (4, 0.0, 0.7, 1),
            (5, 1.0, 0.3, 2),
            (6, 1.0, 0.7, 2),
        ):
            graph.add_node(node_id, "B", x, y, 0.0)
            graph.add_edge(owner, node_id)
        graph.add_edge(1, 2)
        bialgebra = graph.apply_selected_rule("bialgebra", [1, 2])
        self.assertTrue(bialgebra.verified)
        self.assertEqual(len(graph.nodes), 8)
        self.assertEqual(len(graph.edges), 8)

        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.4, 0.5, 0.0)
        graph.add_node(2, "X", 0.6, 0.5, 0.0)
        graph.add_node(3, "B", 0.0, 0.5, 0.0)
        graph.add_node(4, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 3)
        graph.add_edge(2, 4)
        graph.add_edge(1, 2)
        graph.add_edge(1, 2)
        hopf = graph.apply_selected_rule("hopf", [1, 2])
        self.assertTrue(hopf.verified)
        self.assertEqual(len(graph.edges), 2)
        self.assertAlmostEqual(graph.scalar.real, 0.5)

    def test_processing_pi_copy_and_zxh_absorb(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "B", 0.0, 0.5, 0.0)
        graph.add_node(2, "X", 0.3, 0.5, math.pi)
        graph.add_node(3, "Z", 0.6, 0.5, 0.3)
        graph.add_node(4, "B", 1.0, 0.5, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        graph.add_edge(3, 4)
        copied = graph.apply_selected_rule("pi_copy", [2, 3])
        self.assertTrue(copied.verified)
        self.assertLess(copied.absolute_error, 1e-9)

        graph = VisualGraphMirror()
        graph.add_node(1, "HB", 0.5, 0.5, math.pi)
        graph.add_node(2, "X", 0.2, 0.5, math.pi)
        graph.add_node(3, "B", 1.0, 0.3, 0.0)
        graph.add_node(4, "B", 1.0, 0.7, 0.0)
        graph.add_edge(1, 2)
        graph.add_edge(1, 3)
        graph.add_edge(1, 4)
        absorbed = graph.apply_selected_rule("absorb", [1, 2])
        self.assertTrue(absorbed.verified)
        self.assertNotIn(2, graph.nodes)
        self.assertAlmostEqual(graph.scalar.real, math.sqrt(2.0))

    def test_compact_zxh_topology_is_exact_toffoli_with_ui_scalar(
        self,
    ) -> None:
        from pyzx.tensor import tensorfy

        graph = VisualGraphMirror()
        left: list[int] = []
        right: list[int] = []
        spiders: list[int] = []
        node_id = 1
        for y in (0.25, 0.5, 0.75):
            left.append(node_id)
            graph.add_node(node_id, "B", 0.0, y, 0.0)
            node_id += 1
            spiders.append(node_id)
            graph.add_node(node_id, "Z", 0.5, y, 0.0)
            node_id += 1
            right.append(node_id)
            graph.add_node(node_id, "B", 1.0, y, 0.0)
            node_id += 1

        hadamard_in = node_id
        graph.add_node(hadamard_in, "H", 0.3, 0.75, math.pi)
        node_id += 1
        hadamard_out = node_id
        graph.add_node(hadamard_out, "H", 0.7, 0.75, math.pi)
        node_id += 1
        central_h_box = node_id
        graph.add_node(central_h_box, "HB", 0.65, 0.5, math.pi)

        for wire in range(2):
            graph.add_edge(left[wire], spiders[wire])
            graph.add_edge(spiders[wire], right[wire])
        graph.add_edge(left[2], hadamard_in)
        graph.add_edge(hadamard_in, spiders[2])
        graph.add_edge(spiders[2], hadamard_out)
        graph.add_edge(hadamard_out, right[2])
        for spider in spiders:
            graph.add_edge(spider, central_h_box)
        graph.scalar = 0.5 + 0.0j

        pyzx_graph = graph._to_pyzx()
        pyzx_graph.set_inputs(tuple(left))
        pyzx_graph.set_outputs(tuple(right))
        actual = tensorfy(
            pyzx_graph,
            preserve_scalar=True,
        ).reshape(8, 8)

        expected = np.zeros((8, 8), dtype=np.complex128)
        for basis in range(8):
            bits = [
                (basis >> 2) & 1,
                (basis >> 1) & 1,
                basis & 1,
            ]
            output = list(bits)
            if bits[0] and bits[1]:
                output[2] ^= 1
            output_index = (
                (output[0] << 2) | (output[1] << 1) | output[2]
            )
            expected[output_index, basis] = 1.0

        np.testing.assert_allclose(actual, expected, atol=1e-12)

    def test_four_qubit_discard_zx_produces_a_mixed_density(self) -> None:
        graph = VisualGraphMirror()
        for qubit in range(4):
            graph.add_node(
                qubit + 1,
                "B",
                0.9,
                0.2 + 0.18 * qubit,
                0.0,
                "output",
                qubit,
            )

        graph.add_node(5, "Z", 0.5, 0.2, 0.0)
        graph.add_node(6, "D", 0.5, 0.08, 0.0)
        graph.add_edge(5, 1)
        graph.add_edge(5, 6)
        for qubit in range(1, 4):
            state_id = 6 + qubit
            graph.add_node(
                state_id,
                "X",
                0.5,
                0.2 + 0.18 * qubit,
                0.0,
            )
            graph.add_edge(state_id, qubit + 1)

        frame = density_frame_from_visual_graph(graph, 12)
        self.assertEqual(frame.mode, "discard_cpm_state")
        self.assertAlmostEqual(frame.trace, 1.0)
        self.assertAlmostEqual(frame.purity, 0.5)
        self.assertAlmostEqual(frame.entropy, 1.0)
        self.assertAlmostEqual(frame.rho[0, 0].real, 0.5)
        self.assertAlmostEqual(frame.rho[1, 1].real, 0.5)
        self.assertAlmostEqual(abs(frame.rho[0, 1]), 0.0)

    def test_three_output_green_spider_is_exact_ghz_density(
        self,
    ) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.35, 0.5, 0.0)
        for qubit in range(3):
            output_id = 10 + qubit
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.25 + 0.25 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_edge(1, output_id)

        frame = density_frame_from_visual_graph(graph, 13)

        expected = np.zeros((8, 8), dtype=np.complex128)
        expected[0, 0] = 0.5
        expected[0, 7] = 0.5
        expected[7, 0] = 0.5
        expected[7, 7] = 0.5
        self.assertEqual(frame.mode, "state_preparation")
        self.assertEqual(frame.qubit_count, 3)
        self.assertEqual(frame.rho.shape, (8, 8))
        self.assertAlmostEqual(frame.success_probability, 2.0)
        self.assertAlmostEqual(frame.purity, 1.0)
        self.assertAlmostEqual(frame.entropy, 0.0)
        np.testing.assert_allclose(frame.rho, expected, atol=1e-12)
        for qubit in range(3):
            self.assertAlmostEqual(frame.local_purity[qubit], 0.5)
            self.assertAlmostEqual(frame.local_entropy[qubit], 1.0)
            np.testing.assert_allclose(
                frame.local_bloch[qubit],
                (0.0, 0.0, 0.0),
                atol=1e-12,
            )

    def test_two_output_green_spider_is_exact_bell_density(self) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.35, 0.5, 0.0)
        for qubit in range(2):
            output_id = 10 + qubit
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.35 + 0.3 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_edge(1, output_id)

        frame = density_frame_from_visual_graph(graph, 14)

        expected = np.zeros((4, 4), dtype=np.complex128)
        expected[0, 0] = 0.5
        expected[0, 3] = 0.5
        expected[3, 0] = 0.5
        expected[3, 3] = 0.5
        self.assertEqual(frame.mode, "state_preparation")
        self.assertEqual(frame.qubit_count, 2)
        self.assertEqual(frame.rho.shape, (4, 4))
        np.testing.assert_allclose(frame.rho, expected, atol=1e-12)

    def test_eight_output_green_spider_is_bounded_ghz_density(
        self,
    ) -> None:
        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.35, 0.5, 0.0)
        for qubit in range(8):
            output_id = 10 + qubit
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.1 + 0.1 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_edge(1, output_id)

        frame = density_frame_from_visual_graph(graph, 14)

        self.assertEqual(frame.qubit_count, 8)
        self.assertEqual(frame.rho.shape, (256, 256))
        self.assertAlmostEqual(frame.success_probability, 2.0)
        self.assertAlmostEqual(frame.purity, 1.0)
        self.assertAlmostEqual(frame.entropy, 0.0)
        self.assertAlmostEqual(frame.rho[0, 0].real, 0.5)
        self.assertAlmostEqual(frame.rho[0, 255].real, 0.5)
        self.assertAlmostEqual(frame.rho[255, 0].real, 0.5)
        self.assertAlmostEqual(frame.rho[255, 255].real, 0.5)
        self.assertEqual(np.count_nonzero(np.abs(frame.rho) > 1e-12), 4)
        for qubit in range(8):
            self.assertAlmostEqual(frame.local_purity[qubit], 0.5)
            self.assertAlmostEqual(frame.local_entropy[qubit], 1.0)

    def test_dynamic_density_accepts_a_non_ghz_two_qubit_map(self) -> None:
        graph = VisualGraphMirror()
        for qubit in range(2):
            input_id = 10 + qubit
            gate_id = 20 + qubit
            output_id = 30 + qubit
            graph.add_node(
                input_id,
                "B",
                0.1,
                0.35 + 0.3 * qubit,
                0.0,
                "input",
                qubit,
            )
            graph.add_node(
                gate_id,
                "X" if qubit == 0 else "Z",
                0.5,
                0.35 + 0.3 * qubit,
                math.pi if qubit == 0 else 0.0,
            )
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.35 + 0.3 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_edge(input_id, gate_id)
            graph.add_edge(gate_id, output_id)

        frame = density_frame_from_visual_graph(graph, 15)

        expected = np.zeros((4, 4), dtype=np.complex128)
        expected[1, 1] = 1.0
        self.assertEqual(frame.mode, "map_on_zero")
        self.assertEqual(frame.qubit_count, 2)
        np.testing.assert_allclose(frame.rho, expected, atol=1e-12)

    def test_expanded_qac_bell_ghz_and_weave_presets_match_circuits(
        self,
    ) -> None:
        def build_preset(name: str) -> VisualGraphMirror:
            graph = VisualGraphMirror()
            next_id = 1
            previous: list[int] = []

            def node(kind: str, qubit: int, column: float, phase: float = 0.0):
                nonlocal next_id
                identifier = next_id
                next_id += 1
                graph.add_node(identifier, kind, column, float(qubit), phase)
                return identifier

            for qubit in range(4):
                previous.append(node("X", qubit, 0.0))

            def hadamard(qubit: int, column: float) -> None:
                gate = node("H", qubit, column)
                graph.add_edge(previous[qubit], gate)
                previous[qubit] = gate

            def z_phase(qubit: int, column: float, phase: float) -> None:
                gate = node("Z", qubit, column, phase)
                graph.add_edge(previous[qubit], gate)
                previous[qubit] = gate

            def cnot(control: int, target: int, column: float) -> None:
                control_spider = node("Z", control, column)
                target_spider = node("X", target, column)
                graph.add_edge(previous[control], control_spider)
                graph.add_edge(previous[target], target_spider)
                graph.add_edge(control_spider, target_spider)
                previous[control] = control_spider
                previous[target] = target_spider

            if name == "bell":
                hadamard(0, 1.0)
                cnot(0, 1, 2.0)
            elif name == "ghz":
                hadamard(0, 1.0)
                cnot(0, 1, 2.0)
                cnot(1, 2, 3.0)
                cnot(2, 3, 4.0)
            elif name == "weave":
                for qubit in range(4):
                    hadamard(qubit, 1.0 + qubit)
                cnot(0, 1, 6.0)
                cnot(2, 3, 8.0)
                cnot(1, 2, 11.0)
                z_phase(0, 14.0, math.pi / 4.0)
                z_phase(3, 15.0, math.pi / 2.0)
            else:
                raise AssertionError(name)

            for qubit in range(4):
                output = next_id
                next_id += 1
                graph.add_node(
                    output,
                    "B",
                    16.0,
                    float(qubit),
                    0.0,
                    "output",
                    qubit,
                )
                graph.add_edge(previous[qubit], output)
            return graph

        bell = density_frame_from_visual_graph(build_preset("bell"), 16)
        bell_expected = np.zeros((16, 16), dtype=np.complex128)
        bell_expected[np.ix_([0, 3], [0, 3])] = 0.5
        np.testing.assert_allclose(bell.rho, bell_expected, atol=1e-12)

        ghz = density_frame_from_visual_graph(build_preset("ghz"), 17)
        ghz_expected = np.zeros((16, 16), dtype=np.complex128)
        ghz_expected[np.ix_([0, 15], [0, 15])] = 0.5
        np.testing.assert_allclose(ghz.rho, ghz_expected, atol=1e-12)

        weave = density_frame_from_visual_graph(build_preset("weave"), 18)
        amplitudes = np.asarray(
            [
                np.exp(
                    1j
                    * (
                        (math.pi / 4.0) * (basis & 1)
                        + (math.pi / 2.0) * ((basis >> 3) & 1)
                    )
                )
                / 4.0
                for basis in range(16)
            ],
            dtype=np.complex128,
        )
        weave_expected = np.outer(amplitudes, amplitudes.conj())
        np.testing.assert_allclose(weave.rho, weave_expected, atol=1e-12)

    def test_pdf_swap_and_identity_lab_presets_are_exact_maps(self) -> None:
        from pyzx.tensor import tensorfy

        def begin_map(qubit_count: int):
            graph = VisualGraphMirror()
            next_id = 1
            previous: list[int] = []
            for qubit in range(qubit_count):
                graph.add_node(
                    next_id,
                    "B",
                    0.0,
                    float(qubit),
                    0.0,
                    "input",
                    qubit,
                )
                previous.append(next_id)
                next_id += 1
            return graph, previous, next_id

        def add_node(
            graph: VisualGraphMirror,
            previous: list[int],
            next_id: int,
            kind: str,
            qubit: int,
            column: float,
            phase: float = 0.0,
        ) -> int:
            graph.add_node(next_id, kind, column, float(qubit), phase)
            graph.add_edge(previous[qubit], next_id)
            previous[qubit] = next_id
            if kind == "H":
                graph.scalar /= math.sqrt(2.0)
            return next_id + 1

        def add_cnot(
            graph: VisualGraphMirror,
            previous: list[int],
            next_id: int,
            control: int,
            target: int,
            column: float,
        ) -> int:
            graph.add_node(next_id, "Z", column, float(control), 0.0)
            graph.add_node(next_id + 1, "X", column, float(target), 0.0)
            graph.add_edge(previous[control], next_id)
            graph.add_edge(previous[target], next_id + 1)
            graph.add_edge(next_id, next_id + 1)
            previous[control] = next_id
            previous[target] = next_id + 1
            graph.scalar *= math.sqrt(2.0)
            return next_id + 2

        def finish_map(
            graph: VisualGraphMirror,
            previous: list[int],
            next_id: int,
        ) -> None:
            for qubit, source in enumerate(previous):
                graph.add_node(
                    next_id,
                    "B",
                    20.0,
                    float(qubit),
                    0.0,
                    "output",
                    qubit,
                )
                graph.add_edge(source, next_id)
                next_id += 1

        swap, swap_previous, next_id = begin_map(2)
        next_id = add_cnot(swap, swap_previous, next_id, 0, 1, 1.0)
        next_id = add_cnot(swap, swap_previous, next_id, 1, 0, 2.0)
        next_id = add_cnot(swap, swap_previous, next_id, 0, 1, 3.0)
        finish_map(swap, swap_previous, next_id)
        swap_matrix = np.asarray(
            tensorfy(swap._to_pyzx(), preserve_scalar=True),
            dtype=np.complex128,
        ).reshape(4, 4)
        expected_swap = np.zeros((4, 4), dtype=np.complex128)
        for basis in range(4):
            swapped = ((basis & 1) << 1) | ((basis >> 1) & 1)
            expected_swap[swapped, basis] = 1.0
        np.testing.assert_allclose(swap_matrix, expected_swap, atol=1e-12)

        identity, previous, next_id = begin_map(4)
        next_id = add_node(identity, previous, next_id, "H", 0, 1.0)
        next_id = add_node(identity, previous, next_id, "H", 0, 2.0)
        next_id = add_node(
            identity, previous, next_id, "Z", 1, 1.0, -math.pi / 4.0
        )
        next_id = add_node(
            identity, previous, next_id, "Z", 1, 2.0, math.pi / 4.0
        )
        next_id = add_node(
            identity, previous, next_id, "Z", 2, 1.0, math.pi / 4.0
        )
        next_id = add_node(
            identity, previous, next_id, "Z", 2, 2.0, math.pi / 4.0
        )
        next_id = add_node(
            identity, previous, next_id, "Z", 2, 3.0, -math.pi / 2.0
        )
        next_id = add_cnot(identity, previous, next_id, 2, 3, 4.0)
        next_id = add_cnot(identity, previous, next_id, 2, 3, 5.0)
        finish_map(identity, previous, next_id)
        identity_matrix = np.asarray(
            tensorfy(identity._to_pyzx(), preserve_scalar=True),
            dtype=np.complex128,
        ).reshape(16, 16)
        np.testing.assert_allclose(
            identity_matrix,
            np.eye(16, dtype=np.complex128),
            atol=1e-12,
        )

    def test_pdf_graph_state_presets_match_ring_star_and_complete_graphs(
        self,
    ) -> None:
        topologies = {
            "ring": ((0, 1), (1, 2), (2, 3), (3, 0)),
            "star": ((0, 1), (0, 2), (0, 3)),
            "complete": tuple(
                (left, right)
                for left in range(4)
                for right in range(left + 1, 4)
            ),
        }
        for revision, (name, graph_edges) in enumerate(
            topologies.items(),
            start=30,
        ):
            with self.subTest(topology=name):
                graph = VisualGraphMirror()
                for qubit in range(4):
                    graph.add_node(
                        qubit + 1,
                        "Z",
                        0.4,
                        float(qubit),
                        0.0,
                    )
                    graph.add_node(
                        qubit + 10,
                        "B",
                        0.9,
                        float(qubit),
                        0.0,
                        "output",
                        qubit,
                    )
                    graph.add_edge(qubit + 1, qubit + 10)
                for left, right in graph_edges:
                    graph.add_edge(left + 1, right + 1, "hadamard")

                frame = density_frame_from_visual_graph(graph, revision)
                amplitudes = np.asarray(
                    [
                        (
                            -1.0
                            if sum(
                                ((basis >> left) & 1)
                                * ((basis >> right) & 1)
                                for left, right in graph_edges
                            )
                            % 2
                            else 1.0
                        )
                        / 4.0
                        for basis in range(16)
                    ],
                    dtype=np.complex128,
                )
                expected = np.outer(amplitudes, amplitudes.conj())
                np.testing.assert_allclose(frame.rho, expected, atol=1e-12)

    def test_teleportation_discard_dilation_is_identity_cptp_channel(
        self,
    ) -> None:
        from pyzx.tensor import tensorfy

        graph = VisualGraphMirror()
        next_id = 1
        input_id = next_id
        graph.add_node(input_id, "B", 0.0, 0.0, 0.0, "input", 0)
        previous = [input_id]
        next_id += 1
        for wire in (1, 2):
            graph.add_node(next_id, "X", 0.0, float(wire), 0.0)
            previous.append(next_id)
            next_id += 1

        def hadamard(wire: int, column: float) -> None:
            nonlocal next_id
            graph.add_node(next_id, "H", column, float(wire), 0.0)
            graph.add_edge(previous[wire], next_id)
            previous[wire] = next_id
            next_id += 1
            graph.scalar /= math.sqrt(2.0)

        def cnot(control: int, target: int, column: float) -> None:
            nonlocal next_id
            graph.add_node(next_id, "Z", column, float(control), 0.0)
            graph.add_node(next_id + 1, "X", column, float(target), 0.0)
            graph.add_edge(previous[control], next_id)
            graph.add_edge(previous[target], next_id + 1)
            graph.add_edge(next_id, next_id + 1)
            previous[control] = next_id
            previous[target] = next_id + 1
            next_id += 2
            graph.scalar *= math.sqrt(2.0)

        hadamard(1, 1.0)
        cnot(1, 2, 2.0)
        cnot(0, 1, 3.0)
        hadamard(0, 4.0)
        cnot(1, 2, 5.0)
        hadamard(2, 6.0)
        cnot(0, 2, 7.0)
        hadamard(2, 8.0)

        discard_ids: list[int] = []
        for wire in (0, 1):
            discard = next_id
            next_id += 1
            graph.add_node(
                discard,
                "D",
                9.0,
                float(wire),
                0.0,
                "discard",
                wire,
            )
            graph.add_edge(previous[wire], discard)
            discard_ids.append(discard)
        output_id = next_id
        graph.add_node(output_id, "B", 9.0, 2.0, 0.0, "output", 0)
        graph.add_edge(previous[2], output_id)
        graph.scalar *= 0.5

        preview = density_frame_from_visual_graph(graph, 40)
        self.assertEqual(preview.mode, "discard_cpm_map_on_zero")
        self.assertAlmostEqual(preview.success_probability, 1.0)
        np.testing.assert_allclose(
            preview.rho,
            np.asarray([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128),
            atol=1e-12,
        )

        pyzx_graph = graph._to_pyzx()
        pyzx_graph.set_inputs((input_id,))
        pyzx_graph.set_outputs((output_id, *discard_ids))
        dilation = np.asarray(
            tensorfy(pyzx_graph, preserve_scalar=True),
            dtype=np.complex128,
        ).reshape(2, 4, 2)
        kraus = [dilation[:, environment, :] for environment in range(4)]
        completeness = sum(operator.conj().T @ operator for operator in kraus)
        np.testing.assert_allclose(
            completeness,
            np.eye(2, dtype=np.complex128),
            atol=1e-12,
        )
        for row in range(2):
            for column in range(2):
                basis_operator = np.zeros((2, 2), dtype=np.complex128)
                basis_operator[row, column] = 1.0
                teleported = sum(
                    operator @ basis_operator @ operator.conj().T
                    for operator in kraus
                )
                np.testing.assert_allclose(
                    teleported,
                    basis_operator,
                    atol=1e-12,
                )

    def test_density_commit_uses_existing_atomic_engine_protocol(self) -> None:
        class Capture:
            def __init__(self):
                self.messages = []

            def send_message(self, address, payload):
                self.messages.append((address, payload))

        graph = VisualGraphMirror()
        for qubit in range(4):
            boundary = qubit + 1
            state = qubit + 5
            graph.add_node(
                boundary,
                "B",
                0.9,
                0.2 + 0.18 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_node(
                state,
                "X",
                0.5,
                0.2 + 0.18 * qubit,
                0.0,
            )
            graph.add_edge(state, boundary)
        frame = density_frame_from_visual_graph(graph, 17)

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.density_frame = frame
        verifier.engine_client = Capture()
        verifier.client = Capture()
        verifier.engine_host = "127.0.0.1"
        verifier.engine_port = 7402
        verifier._on_density_commit("", 17)

        addresses = [
            address for address, _payload in verifier.engine_client.messages
        ]
        self.assertEqual(
            addresses,
            [
                "/qmw/state/begin",
                "/qmw/state/rho/real",
                "/qmw/state/rho/imag",
                "/qmw/state/commit",
            ],
        )
        real_payload = verifier.engine_client.messages[1][1]
        imag_payload = verifier.engine_client.messages[2][1]
        self.assertEqual(len(real_payload), 257)
        self.assertEqual(len(imag_payload), 257)

    def test_five_qubit_preview_is_not_committed_to_four_qubit_engine(
        self,
    ) -> None:
        class Capture:
            def __init__(self):
                self.messages = []

            def send_message(self, address, payload):
                self.messages.append((address, payload))

        graph = VisualGraphMirror()
        graph.add_node(1, "Z", 0.35, 0.5, 0.0)
        for qubit in range(5):
            output_id = 10 + qubit
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.1 + 0.16 * qubit,
                0.0,
                "output",
                qubit,
            )
            graph.add_edge(1, output_id)
        frame = density_frame_from_visual_graph(graph, 18)

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.density_frame = frame
        verifier.engine_client = Capture()
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier._on_density_commit("", 18)

        self.assertEqual(verifier.engine_client.messages, [])
        errors = [
            payload
            for address, payload in verifier.client.messages
            if address == "/qmw/zx/density/error"
        ]
        self.assertEqual(len(errors), 1)
        self.assertIn("four-qubit resonator", errors[0])

    def test_density_preview_is_a_bounded_complete_osc_frame(self) -> None:
        graph = VisualGraphMirror()
        for qubit in range(4):
            output_id = 100 + qubit
            state_id = 200 + qubit
            graph.add_node(
                output_id,
                "B",
                0.9,
                0.2 + qubit * 0.2,
                0.0,
                boundary_role="output",
                boundary_index=qubit,
            )
            graph.add_node(state_id, "X", 0.4, 0.2 + qubit * 0.2, 0.0)
            graph.add_edge(state_id, output_id)
        frame = density_frame_from_visual_graph(graph, 23)

        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier._send_density_frame(frame)
        addresses = [address for address, _ in verifier.client.messages]
        self.assertEqual(addresses.count("/qmw/zx/density/row"), 16)
        self.assertEqual(addresses.count("/qmw/zx/density/bloch"), 4)
        self.assertEqual(addresses[0], "/qmw/zx/density/begin")
        self.assertEqual(addresses[-1], "/qmw/zx/density/end")
        row_payload = next(
            payload
            for address, payload in verifier.client.messages
            if address == "/qmw/zx/density/row"
        )
        self.assertEqual(len(row_payload), 34)
        self.assertEqual(
            verifier.max_density_client.messages,
            verifier.client.messages,
        )

    def test_osc_self_loop_is_rejected_without_escaping_handler(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.graph = VisualGraphMirror()
        verifier.graph.add_node(1, "Z", 0.25, 0.5, 0.0)
        verifier.client = Capture()

        verifier._on_edge_add("", 1, 1, "plain")

        self.assertEqual(verifier.graph.edges, [])
        self.assertEqual(
            verifier.client.messages[0][0],
            "/qmw/zx/graph/error",
        )
        self.assertIn(
            "self-loops",
            verifier.client.messages[0][1][0],
        )

    def test_osc_valid_edge_still_reaches_graph_mirror(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.graph = VisualGraphMirror()
        verifier.graph.add_node(1, "Z", 0.25, 0.5, 0.0)
        verifier.graph.add_node(2, "X", 0.75, 0.5, 0.0)
        verifier.client = Capture()

        verifier._on_edge_add("", 1, 2, "plain")

        self.assertEqual(len(verifier.graph.edges), 1)
        self.assertEqual(verifier.client.messages, [])


class PauliGadgetTests(unittest.TestCase):
    @staticmethod
    def visual_gadget(label: str, theta: float) -> VisualGraphMirror:
        graph = VisualGraphMirror()
        next_id = 1
        anchors = []
        hadamards = 0
        for qubit, axis in enumerate(label):
            graph.add_node(next_id, "B", 0, qubit, 0, "input", qubit)
            previous = next_id
            next_id += 1
            if axis == "Y":
                graph.add_node(next_id, "Z", next_id, qubit, -math.pi / 2)
                graph.add_edge(previous, next_id)
                previous = next_id
                next_id += 1
            if axis in {"X", "Y"}:
                graph.add_node(next_id, "H", next_id, qubit, 0)
                graph.add_edge(previous, next_id)
                previous = next_id
                next_id += 1
                hadamards += 2
            if axis != "I":
                graph.add_node(next_id, "Z", next_id, qubit, 0)
                graph.add_edge(previous, next_id)
                anchors.append(next_id)
                previous = next_id
                next_id += 1
            if axis in {"X", "Y"}:
                graph.add_node(next_id, "H", next_id, qubit, 0)
                graph.add_edge(previous, next_id)
                previous = next_id
                next_id += 1
            if axis == "Y":
                graph.add_node(next_id, "Z", next_id, qubit, math.pi / 2)
                graph.add_edge(previous, next_id)
                previous = next_id
                next_id += 1
            graph.add_node(next_id, "B", 99, qubit, 0, "output", qubit)
            graph.add_edge(previous, next_id)
            next_id += 1

        hub = next_id
        graph.add_node(hub, "Z", 50, 5, 0)
        phase = hub + 1
        graph.add_node(phase, "Z", 60, 5, theta)
        for anchor in anchors:
            graph.add_edge(anchor, hub, "hadamard")
        graph.add_edge(hub, phase, "hadamard")
        weight = sum(axis != "I" for axis in label)
        normalization = 2.0 ** (0.5 * (weight - 1 - hadamards))
        graph.scalar = normalization * np.exp(-0.5j * theta)
        return graph

    @staticmethod
    def visual_score(gadgets: list[PauliGadgetSpec]) -> VisualGraphMirror:
        graph = VisualGraphMirror()
        next_id = 1
        previous = []
        for qubit in range(4):
            graph.add_node(next_id, "B", 0, qubit, 0, "input", qubit)
            previous.append(next_id)
            next_id += 1
        scalar = 1.0 + 0.0j
        for score_index, gadget in enumerate(gadgets):
            anchors = []
            hadamards = 0
            for qubit, axis in enumerate(gadget.label):
                if axis == "Y":
                    graph.add_node(
                        next_id,
                        "Z",
                        score_index + 0.1,
                        qubit,
                        -math.pi / 2,
                    )
                    graph.add_edge(previous[qubit], next_id)
                    previous[qubit] = next_id
                    next_id += 1
                if axis in {"X", "Y"}:
                    graph.add_node(
                        next_id,
                        "H",
                        score_index + 0.2,
                        qubit,
                        0,
                    )
                    graph.add_edge(previous[qubit], next_id)
                    previous[qubit] = next_id
                    next_id += 1
                    hadamards += 2
                if axis != "I":
                    graph.add_node(
                        next_id,
                        "Z",
                        score_index + 0.3,
                        qubit,
                        0,
                    )
                    graph.add_edge(previous[qubit], next_id)
                    previous[qubit] = next_id
                    anchors.append(next_id)
                    next_id += 1
                if axis in {"X", "Y"}:
                    graph.add_node(
                        next_id,
                        "H",
                        score_index + 0.4,
                        qubit,
                        0,
                    )
                    graph.add_edge(previous[qubit], next_id)
                    previous[qubit] = next_id
                    next_id += 1
                if axis == "Y":
                    graph.add_node(
                        next_id,
                        "Z",
                        score_index + 0.5,
                        qubit,
                        math.pi / 2,
                    )
                    graph.add_edge(previous[qubit], next_id)
                    previous[qubit] = next_id
                    next_id += 1
            hub = next_id
            graph.add_node(hub, "Z", score_index + 0.3, 5, 0)
            next_id += 1
            phase = next_id
            graph.add_node(
                phase,
                "Z",
                score_index + 0.3,
                6,
                gadget.theta,
            )
            next_id += 1
            for anchor in anchors:
                graph.add_edge(anchor, hub, "hadamard")
            graph.add_edge(hub, phase, "hadamard")
            normalization = 2.0 ** (
                0.5 * (pauli_weight(gadget.label) - 1 - hadamards)
            )
            scalar *= normalization * np.exp(-0.5j * gadget.theta)
        for qubit in range(4):
            graph.add_node(next_id, "B", 99, qubit, 0, "output", qubit)
            graph.add_edge(previous[qubit], next_id)
            next_id += 1
        graph.scalar = scalar
        return graph

    def test_operator_uses_q0_lsb_order(self) -> None:
        operator = pauli_operator("XIII")
        basis_zero = np.zeros(16, dtype=complex)
        basis_zero[0] = 1
        result = operator @ basis_zero
        self.assertEqual(int(np.argmax(np.abs(result))), 1)

    def test_rotation_is_unitary(self) -> None:
        rotation = pauli_rotation_matrix("XYZI", 0.37)
        np.testing.assert_allclose(
            rotation.conj().T @ rotation,
            np.eye(16),
            atol=1e-12,
        )

    def test_pauli_commutation_uses_even_anticommuting_sites(self) -> None:
        self.assertTrue(pauli_strings_commute("XXII", "YYII"))
        self.assertTrue(pauli_strings_commute("XYZI", "XYZI"))
        self.assertFalse(pauli_strings_commute("XIII", "ZIII"))

    def test_score_matrix_preserves_left_to_right_order(self) -> None:
        gadgets = [
            PauliGadgetSpec(1, "XIII", 0.31),
            PauliGadgetSpec(2, "ZIII", -0.27),
        ]
        expected = (
            pauli_rotation_matrix("ZIII", -0.27)
            @ pauli_rotation_matrix("XIII", 0.31)
        )
        np.testing.assert_allclose(pauli_score_matrix(gadgets), expected)

    def test_equal_gadgets_fuse_across_only_commuting_middle(self) -> None:
        commuting = [
            PauliGadgetSpec(1, "XIII", 0.1),
            PauliGadgetSpec(2, "IXII", 0.2),
            PauliGadgetSpec(3, "XIII", 0.3),
        ]
        self.assertTrue(can_fuse_score_gadgets(commuting, 0, 2))
        fused = fuse_score_gadgets(commuting, 0, 2)
        self.assertEqual([g.label for g in fused], ["XIII", "IXII"])
        self.assertAlmostEqual(fused[0].theta, 0.4)
        np.testing.assert_allclose(
            pauli_score_matrix(fused),
            pauli_score_matrix(commuting),
            atol=1e-12,
        )

        blocked = [
            PauliGadgetSpec(1, "XIII", 0.1),
            PauliGadgetSpec(2, "ZIII", 0.2),
            PauliGadgetSpec(3, "XIII", 0.3),
        ]
        self.assertFalse(can_fuse_score_gadgets(blocked, 0, 2))

    def test_expanded_multi_gadget_score_matches_ordered_product(self) -> None:
        gadgets = [
            PauliGadgetSpec(1, "XYZI", math.pi / 8),
            PauliGadgetSpec(2, "ZIII", -math.pi / 4),
            PauliGadgetSpec(3, "IXXY", math.pi / 3),
        ]
        result = verify_visual_pauli_score(
            self.visual_score(gadgets),
            gadgets,
        )
        self.assertTrue(result.verified, result.message)
        self.assertLess(result.absolute_error, 1e-8)

    def test_processing_expansion_is_exactly_verified_by_pyzx(self) -> None:
        for label in ("ZIII", "XIII", "YIII", "ZZII", "XYZI"):
            with self.subTest(label=label):
                graph = self.visual_gadget(label, math.pi / 8)
                result = verify_visual_pauli_gadget(
                    graph,
                    label,
                    math.pi / 8,
                )
                self.assertTrue(result.verified, result.message)
                self.assertLess(result.absolute_error, 1e-8)

    def test_density_expectation_matches_known_pauli_eigenstate(self) -> None:
        ket = np.zeros(16, dtype=complex)
        ket[1] = 1
        rho = np.outer(ket, ket.conj())
        self.assertAlmostEqual(pauli_expectation(rho, "ZIII"), -1.0)
        self.assertAlmostEqual(pauli_expectation(rho, "IZII"), 1.0)

    def test_live_osc_payload_contains_requested_semantics(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        class Frame:
            revision = 42
            rho = np.eye(16, dtype=complex) / 16

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier.active_pauli_label = "XYZI"
        verifier.active_pauli_theta = math.pi / 8
        verifier.active_pauli_verified = True
        verifier._send_active_pauli(Frame())
        address, payload = verifier.client.messages[0]
        self.assertEqual(address, "/qmw/zx/pauli/live")
        self.assertEqual(payload[1:3], ["XYZI", 3])
        self.assertAlmostEqual(payload[3], 0.0)
        self.assertAlmostEqual(payload[4], math.pi / 8)
        self.assertEqual(payload[5], 1)

    def test_score_osc_transaction_verifies_complete_product(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        gadgets = [
            PauliGadgetSpec(7, "XYZI", math.pi / 8),
            PauliGadgetSpec(9, "ZIII", -math.pi / 4),
        ]
        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.graph = self.visual_score(gadgets)
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier.tomography_client = Capture()
        verifier.density_frame = None
        verifier.active_pauli_verified = False
        verifier._on_pauli_score(
            "",
            2,
            7,
            "XYZI",
            math.pi / 8,
            9,
            "ZIII",
            -math.pi / 4,
        )
        self.assertTrue(verifier.pauli_score_verified)
        for target in (
            verifier.client,
            verifier.max_density_client,
            verifier.tomography_client,
        ):
            self.assertEqual(
                target.messages[0][0],
                "/qmw/zx/pauli/score_verified",
            )
            self.assertEqual(target.messages[0][1][1], 1)

    def test_active_gadget_is_fanned_out_only_with_score_verification(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        verifier = RewriteOSCVerifier.__new__(RewriteOSCVerifier)
        verifier.client = Capture()
        verifier.max_density_client = Capture()
        verifier.tomography_client = Capture()
        verifier.density_frame = None
        verifier.pauli_score_verified = True
        verifier._on_pauli_active("", 12, "XYZI", math.pi / 8, 73)

        expected = [12, "XYZI", math.pi / 8, 1]
        for target in (
            verifier.client,
            verifier.max_density_client,
            verifier.tomography_client,
        ):
            self.assertEqual(
                target.messages,
                [("/qmw/zx/pauli/active", expected)],
            )


class ModularCompilerTests(unittest.TestCase):
    def test_plan_contains_exact_modules_cables_and_json(self) -> None:
        diagram = phase_chain("z", math.pi / 4.0, 0.0)
        diagram.edges["e1"] = type(diagram.edges["e1"])(
            "e1",
            "first",
            "second",
            "hadamard",
        )
        plan = compile_modular_plan(diagram)
        self.assertEqual(len(plan.modules), 4)
        self.assertEqual(len(plan.cables), 3)
        self.assertEqual(plan.cables[1].transform, "hadamard")
        spider = next(module for module in plan.modules if module.module_id == "first")
        self.assertEqual(spider.parameters["representation"], "complex_dual_rail_tensor")
        payload = json.loads(plan.to_json())
        self.assertEqual(payload["schema"], "qmw.zx-modular-plan.v1")
        self.assertIn("boundary 0 is LSB", payload["metadata"]["basis_ordering"])
        self.assertEqual(
            payload["metadata"]["vcv_polyphony"]["channels_per_wire"],
            4,
        )

    def test_boundary_must_have_degree_one(self) -> None:
        diagram = ZXDiagram("invalid_boundary")
        diagram.add_boundary("input", "input", 0)
        with self.assertRaisesRegex(ValueError, "degree one"):
            diagram.validate()


class RackControlTests(unittest.TestCase):
    def test_bell_state_maps_to_bounded_oscelot_controls(self) -> None:
        state = np.array([1.0, 0.0, 0.0, 1.0]) / math.sqrt(2.0)
        frame = rack_frame_from_state(
            state,
            phase_radians=math.pi,
            parameter_gradient=-1.0,
        )
        self.assertAlmostEqual(frame.expectation_z0, 0.0)
        self.assertAlmostEqual(frame.population_entropy, 0.5)
        self.assertAlmostEqual(frame.coherence_l1, 1.0 / 3.0)
        self.assertEqual(len(frame.controls), 6)
        self.assertTrue(all(0.0 <= control.value <= 1.0 for control in frame.controls))
        self.assertEqual(
            frame.osc_messages()[0],
            ("/qmw/zx/fader", [1, 0.5]),
        )
        self.assertEqual(
            frame.osc_messages(control_ids={2, 5}),
            [
                ("/qmw/zx/fader", [2, 0.5]),
                ("/qmw/zx/fader", [5, frame.controls[4].value]),
            ],
        )
        self.assertEqual(
            frame.osc_messages(prefix="", control_ids={1}),
            [("/fader", [1, 0.5])],
        )

    def test_hybrid_plan_uses_matching_four_channel_host_wires(self) -> None:
        diagram = phase_chain("z", 0.25, -0.5)
        plan = compile_hybrid_max_vcv_plan(diagram)
        self.assertEqual(plan.to_dict()["schema"], "qmw.zx-hybrid-max-vcv.v1")
        self.assertTrue(plan.revision)
        self.assertTrue(
            all(cable.channels == 4 for cable in plan.max_plan.cables)
        )
        self.assertTrue(
            all(cable.channels == 4 for cable in plan.vcv_plan.cables)
        )
        self.assertEqual(
            plan.synchronization["semantic_authority"],
            "Python / PennyLane / PyZX",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
