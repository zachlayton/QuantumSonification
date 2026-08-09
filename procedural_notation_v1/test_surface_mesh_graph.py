from __future__ import annotations

import unittest

import networkx as nx
from music21 import converter, note
import numpy as np

from procedural_notation_v1.generate_quartic_torus_score import main as generate_score
from procedural_notation_v1.surface_mesh_graph import (
    TORUS_HEXATONIC_SET,
    apply_torus_hexatonic_mapping,
    build_quartic_torus_mesh,
)


class QuarticTorusMeshTests(unittest.TestCase):
    def test_mesh_has_torus_topology_and_lies_on_quartic(self) -> None:
        graph = build_quartic_torus_mesh()

        self.assertEqual(graph.number_of_nodes(), 96)
        self.assertEqual(graph.number_of_edges(), 192)
        self.assertTrue(nx.is_connected(graph))
        self.assertEqual(set(dict(graph.degree()).values()), {4})
        self.assertEqual(graph.graph["euler_characteristic"], 0)
        self.assertLess(
            max(abs(data["implicit_residual"]) for _, data in graph.nodes(data=True)),
            1e-10,
        )

    def test_mesh_eigenfield_satisfies_weighted_laplacian_equation(self) -> None:
        graph = build_quartic_torus_mesh()
        node_order = list(graph.graph["node_order"])
        adjacency = nx.to_numpy_array(graph, nodelist=node_order, weight="coupling")
        laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
        field = np.asarray([graph.nodes[node_id]["field_value"] for node_id in node_order])

        self.assertTrue(
            np.allclose(laplacian @ field, graph.graph["eigenvalue"] * field)
        )

    def test_coordinates_control_pitch_rotation_register_and_rests(self) -> None:
        graph = apply_torus_hexatonic_mapping(build_quartic_torus_mesh())
        path = graph.graph["traversal_path"]

        self.assertEqual(len(path), 96)
        self.assertTrue(all(graph.has_edge(start, end) for start, end in zip(path, path[1:])))
        self.assertEqual(graph.graph["pitch_collection"], TORUS_HEXATONIC_SET)
        self.assertEqual(graph.graph["ring_rest_ticks"], (1, 2, 3, 4, 5, 4, 3, 2))
        self.assertEqual(graph.graph["total_ticks"], 120)
        self.assertEqual(
            {graph.nodes[node_id]["octave_displacement"] for node_id in path},
            {-1, 0, 1},
        )

    def test_musicxml_round_trip_preserves_surface_form(self) -> None:
        score = converter.parse(generate_score())
        part = score.parts[0]
        notes = list(part.recurse().getElementsByClass(note.Note))
        rests = list(part.recurse().getElementsByClass(note.Rest))

        self.assertEqual(len(part.getElementsByClass("Measure")), 5)
        self.assertEqual(len(notes), 96)
        self.assertEqual(sum(item.quarterLength for item in rests), 3.0)
        self.assertTrue(all(item.tie is None for item in notes))


if __name__ == "__main__":
    unittest.main()
