from __future__ import annotations

import itertools
import math
import unittest

import numpy as np

from quantumsonification_foundations_v1.density.graph_density_state_v1 import (
    GraphDensityState,
    TensorLabeling,
    adjacency_from_edges,
    direct_product_adjacency,
    direct_product_density_formula,
    edge_mixture,
    edge_projector,
    graph_density_matrix,
    laplacian_from_adjacency,
    negativity,
    partial_transpose,
    project_density_to_graph_state,
    relabel_density_matrix,
)


class GraphDensityStateTests(unittest.TestCase):
    def test_k2_is_the_pure_edge_state(self) -> None:
        adjacency = adjacency_from_edges(2, [(0, 1)])
        state = GraphDensityState.from_adjacency(adjacency)
        expected = edge_projector(0, 1, 2)
        np.testing.assert_allclose(state.rho_graph, expected, atol=1e-12)
        self.assertAlmostEqual(state.purity, 1.0)
        self.assertAlmostEqual(state.entropy_bits, 0.0)
        self.assertEqual(state.rank, 1)
        self.assertEqual(state.nullity, 1)

    def test_weighted_laplacian_equals_weighted_edge_mixture(self) -> None:
        edges = [(0, 1), (1, 2), (0, 2)]
        weights = np.array([0.5, 2.0, 1.25])
        adjacency = adjacency_from_edges(3, edges, weights)
        state = GraphDensityState.from_adjacency(adjacency)
        expected = edge_mixture(edges, 3, weights)
        np.testing.assert_allclose(state.rho_graph, expected, atol=1e-12)
        self.assertLess(state.metadata["edge_mixture_residual"], 1e-12)

    def test_complete_graph_reaches_graph_state_entropy_bound(self) -> None:
        dimension = 16
        edges = list(itertools.combinations(range(dimension), 2))
        state = GraphDensityState.from_adjacency(
            adjacency_from_edges(dimension, edges)
        )
        self.assertAlmostEqual(state.entropy_bits, math.log2(15), places=11)
        self.assertEqual(state.rank, 15)
        self.assertEqual(state.nullity, 1)

    def test_loops_do_not_change_the_combinatorial_laplacian(self) -> None:
        adjacency = adjacency_from_edges(3, [(0, 1), (1, 2)])
        with_loops = adjacency.copy()
        np.fill_diagonal(with_loops, [3.0, 7.0, 11.0])
        np.testing.assert_allclose(
            laplacian_from_adjacency(adjacency),
            laplacian_from_adjacency(with_loops),
        )

    def test_partial_transpose_detects_bell_entanglement(self) -> None:
        bell = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128) / np.sqrt(2.0)
        rho = np.outer(bell, bell.conj())
        transformed = partial_transpose(rho, (2, 2), 1)
        self.assertAlmostEqual(float(np.min(np.linalg.eigvalsh(transformed))), -0.5)
        self.assertAlmostEqual(negativity(rho, (2, 2), 1), 0.5)

    def test_p4_entanglement_depends_on_vertex_labeling(self) -> None:
        adjacency = adjacency_from_edges(4, [(0, 1), (1, 2), (2, 3)])
        rho = GraphDensityState.from_adjacency(adjacency).rho_graph
        observed = [
            negativity(relabel_density_matrix(rho, order), (2, 2), 1)
            for order in itertools.permutations(range(4))
        ]
        self.assertLess(min(observed), 1e-12)
        self.assertGreater(max(observed), 0.06)

    def test_tensor_labeling_reorders_to_canonical_basis(self) -> None:
        custom_labels = ((0, 0), (1, 0), (0, 1), (1, 1))
        labeling = TensorLabeling((2, 2), custom_labels)
        np.testing.assert_array_equal(
            labeling.canonical_permutation(), np.array([0, 2, 1, 3])
        )
        self.assertEqual(labeling.vertex((1, 0)), 1)
        self.assertEqual(labeling.label(2), (0, 1))

    def test_direct_product_formula_matches_graph_density(self) -> None:
        k2 = adjacency_from_edges(2, [(0, 1)])
        product_adjacency = direct_product_adjacency(k2, k2)
        exact = graph_density_matrix(
            laplacian_from_adjacency(product_adjacency)
        )
        formula = direct_product_density_formula(k2, k2)
        np.testing.assert_allclose(exact, formula, atol=1e-12)
        self.assertLess(negativity(exact, (2, 2), 1), 1e-12)

    def test_direct_product_formula_supports_nonnegative_weights(self) -> None:
        graph_a = adjacency_from_edges(3, [(0, 1), (1, 2)], [0.3, 1.7])
        graph_b = adjacency_from_edges(2, [(0, 1)], [2.5])
        exact = GraphDensityState.from_adjacency(
            direct_product_adjacency(graph_a, graph_b)
        ).rho_graph
        formula = direct_product_density_formula(graph_a, graph_b)
        np.testing.assert_allclose(exact, formula, atol=1e-12)

    def test_projection_recovers_an_existing_graph_state(self) -> None:
        adjacency = adjacency_from_edges(4, [(0, 1), (1, 2), (2, 3)])
        rho = GraphDensityState.from_adjacency(adjacency).rho_graph
        report = project_density_to_graph_state(rho)
        self.assertTrue(report.success, report.message)
        self.assertLess(report.frobenius_error, 2e-6)
        self.assertLess(report.trace_distance, 2e-6)

    def test_projection_exposes_maximally_mixed_state_limitation(self) -> None:
        rho = np.eye(4, dtype=np.complex128) / 4.0
        report = project_density_to_graph_state(rho)
        self.assertTrue(report.success, report.message)
        self.assertGreater(report.frobenius_error, 0.28)
        self.assertAlmostEqual(report.trace_distance, 0.25, places=8)
        self.assertGreaterEqual(report.rank_deficit, 1)

    def test_invalid_negative_adjacency_is_rejected(self) -> None:
        adjacency = np.array([[0.0, -1.0], [-1.0, 0.0]])
        with self.assertRaisesRegex(ValueError, "non-negative"):
            laplacian_from_adjacency(adjacency)

    def test_out_of_range_self_loop_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside dimension"):
            adjacency_from_edges(2, [(5, 5)])

    def test_direct_product_rejects_asymmetric_adjacency(self) -> None:
        asymmetric = np.array([[0.0, 1.0], [0.0, 0.0]])
        valid = adjacency_from_edges(2, [(0, 1)])
        with self.assertRaisesRegex(ValueError, "symmetric"):
            direct_product_adjacency(asymmetric, valid)
        with self.assertRaisesRegex(ValueError, "symmetric"):
            direct_product_density_formula(asymmetric, valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
