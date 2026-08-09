from __future__ import annotations

import math
import unittest

import networkx as nx

from procedural_notation_v1.geometry_graph import (
    build_dodecahedron_graph,
    build_quantized_cycle_graph,
    build_regular_polygon_graph,
    build_tetrahedron_graph,
)


class RegularPolygonGraphTests(unittest.TestCase):
    def test_octagon_has_expected_cycle_structure(self) -> None:
        graph = build_regular_polygon_graph()

        self.assertEqual(graph.number_of_nodes(), 8)
        self.assertEqual(graph.number_of_edges(), 8)
        self.assertTrue(nx.is_connected(graph))
        self.assertEqual(dict(graph.degree()), {node: 2 for node in range(8)})

    def test_geometry_is_embedded_and_weighted(self) -> None:
        radius = 2.5
        graph = build_regular_polygon_graph(sides=5, radius=radius)
        expected_edge_length = 2.0 * radius * math.sin(math.pi / 5.0)

        for _, data in graph.nodes(data=True):
            x, y = data["position"]
            self.assertAlmostEqual(math.hypot(x, y), radius)
            self.assertTrue(0.0 <= data["angle"] < math.tau)

        for _, _, data in graph.edges(data=True):
            self.assertAlmostEqual(data["distance"], expected_edge_length)

    def test_same_parameters_produce_same_graph(self) -> None:
        first = build_regular_polygon_graph(sides=7, radius=1.75, phase=0.25)
        second = build_regular_polygon_graph(sides=7, radius=1.75, phase=0.25)

        self.assertEqual(dict(first.nodes(data=True)), dict(second.nodes(data=True)))
        self.assertEqual(dict(first.edges), dict(second.edges))

    def test_invalid_parameters_are_rejected(self) -> None:
        invalid_arguments = (
            {"sides": 2},
            {"sides": 3.5},
            {"radius": 0.0},
            {"radius": math.inf},
            {"phase": math.nan},
        )

        for arguments in invalid_arguments:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    build_regular_polygon_graph(**arguments)


class QuantizedCycleGraphTests(unittest.TestCase):
    def test_default_graph_has_24_quarter_tone_nodes(self) -> None:
        graph = build_quantized_cycle_graph()

        self.assertEqual(graph.number_of_nodes(), 24)
        self.assertEqual(graph.number_of_edges(), 24)
        self.assertEqual(graph.graph["pitch_system"], "24-EDO")
        self.assertEqual(graph.graph["cents_per_pitch_step"], 50.0)
        self.assertEqual(graph.nodes[0]["pitch_space"], 60.0)
        self.assertEqual(graph.nodes[1]["pitch_space"], 60.5)
        self.assertEqual(graph.nodes[23]["pitch_space"], 71.5)

    def test_default_rhythm_tick_is_a_32nd_note(self) -> None:
        graph = build_quantized_cycle_graph()

        self.assertEqual(graph.graph["rhythm_subdivisions_per_quarter"], 8)
        self.assertEqual(graph.graph["rhythm_note_value"], 32)
        self.assertEqual(graph.graph["quarter_length_per_tick"], 0.125)
        self.assertEqual(graph.nodes[7]["onset_tick"], 7)
        self.assertEqual(graph.nodes[7]["duration_ticks"], 1)
        self.assertEqual(graph.nodes[7]["quarter_length"], 0.125)

    def test_topology_and_quantization_are_independent(self) -> None:
        graph = build_quantized_cycle_graph(
            node_count=32,
            pitch_divisions=24,
            rhythm_subdivisions=8,
        )

        self.assertEqual(graph.number_of_nodes(), 32)
        self.assertEqual(graph.nodes[24]["pitch_step"], 0)
        self.assertEqual(graph.nodes[31]["onset_tick"], 31)

    def test_invalid_quantization_is_rejected(self) -> None:
        for arguments in (
            {"node_count": 2},
            {"pitch_divisions": 0},
            {"rhythm_subdivisions": 0},
            {"root_pitch_space": math.nan},
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    build_quantized_cycle_graph(**arguments)


class TetrahedronGraphTests(unittest.TestCase):
    def test_tetrahedron_is_complete_graph_on_four_vertices(self) -> None:
        graph = build_tetrahedron_graph()

        self.assertEqual(graph.number_of_nodes(), 4)
        self.assertEqual(graph.number_of_edges(), 6)
        self.assertTrue(nx.is_isomorphic(graph, nx.complete_graph(4)))
        self.assertEqual(graph.graph["dimension"], 3)

    def test_vertices_and_edges_are_geometrically_regular(self) -> None:
        radius = 2.5
        graph = build_tetrahedron_graph(radius=radius)
        expected_edge_length = radius * math.sqrt(8.0 / 3.0)

        positions = [data["position"] for _, data in graph.nodes(data=True)]
        for x, y, z in positions:
            self.assertAlmostEqual(math.sqrt(x * x + y * y + z * z), radius)
        for coordinate in range(3):
            self.assertAlmostEqual(sum(point[coordinate] for point in positions), 0.0)
        for _, _, data in graph.edges(data=True):
            self.assertAlmostEqual(data["distance"], expected_edge_length)

    def test_invalid_radius_is_rejected(self) -> None:
        for radius in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    build_tetrahedron_graph(radius)


class DodecahedronGraphTests(unittest.TestCase):
    def test_dodecahedron_has_expected_topology(self) -> None:
        graph = build_dodecahedron_graph()

        self.assertEqual(graph.number_of_nodes(), 20)
        self.assertEqual(graph.number_of_edges(), 30)
        self.assertTrue(nx.is_isomorphic(graph, nx.dodecahedral_graph()))
        self.assertEqual(set(dict(graph.degree()).values()), {3})

    def test_dodecahedron_is_regular_in_three_dimensions(self) -> None:
        radius = 1.75
        graph = build_dodecahedron_graph(radius)

        for _, data in graph.nodes(data=True):
            x, y, z = data["position"]
            self.assertAlmostEqual(math.sqrt(x * x + y * y + z * z), radius)
        edge_lengths = [data["distance"] for _, _, data in graph.edges(data=True)]
        self.assertTrue(all(math.isclose(length, edge_lengths[0]) for length in edge_lengths))

    def test_invalid_dodecahedron_radius_is_rejected(self) -> None:
        for radius in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    build_dodecahedron_graph(radius)


if __name__ == "__main__":
    unittest.main()
