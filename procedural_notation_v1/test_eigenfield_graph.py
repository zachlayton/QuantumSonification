from __future__ import annotations

import unittest

from music21 import converter, note
import networkx as nx
import numpy as np

from procedural_notation_v1.eigenfield_graph import (
    OCTAVE_DISPLACED_HEXATONIC_LINE,
    apply_eigenfield_line_mapping,
    build_laplacian_eigenfield_graph,
    serpentine_path,
)
from procedural_notation_v1.generate_eigenfield_hexatonic_score import (
    main as generate_hexatonic_score,
)
from procedural_notation_v1.generate_eigenfield_line_score import main as generate_score
from procedural_notation_v1.generate_eigenfield_numerical_phrases_score import (
    main as generate_numerical_phrases_score,
)
from procedural_notation_v1.eigenfield_phrase import build_numerical_phrase_graph


class EigenfieldGraphTests(unittest.TestCase):
    def test_grid_contains_a_valid_laplacian_eigenfield(self) -> None:
        graph = build_laplacian_eigenfield_graph()
        node_order = list(graph.graph["node_order"])
        adjacency = nx.to_numpy_array(graph, nodelist=node_order, weight="coupling", dtype=float)
        laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
        field = np.asarray([graph.nodes[node_id]["field_value"] for node_id in node_order])

        self.assertEqual(graph.number_of_nodes(), 64)
        self.assertEqual(graph.number_of_edges(), 112)
        self.assertTrue(nx.is_connected(graph))
        self.assertTrue(
            np.allclose(laplacian @ field, graph.graph["eigenvalue"] * field)
        )

    def test_serpentine_path_is_connected_and_complete(self) -> None:
        graph = build_laplacian_eigenfield_graph()
        path = serpentine_path(graph)

        self.assertEqual(len(path), 64)
        self.assertEqual(len(set(path)), 64)
        self.assertTrue(all(graph.has_edge(start, end) for start, end in zip(path, path[1:])))

    def test_quantization_creates_repeated_note_line(self) -> None:
        graph = apply_eigenfield_line_mapping(build_laplacian_eigenfield_graph())
        path = graph.graph["traversal_path"]
        pitches = [graph.nodes[node_id]["pitch"] for node_id in path]
        repeated_transitions = sum(left == right for left, right in zip(pitches, pitches[1:]))

        self.assertGreaterEqual(repeated_transitions, 12)
        self.assertGreater(len(set(pitches)), 3)
        self.assertEqual([graph.nodes[node_id]["onset_tick"] for node_id in path], list(range(64)))

    def test_musicxml_has_two_measures_and_rearticulated_repetitions(self) -> None:
        score = converter.parse(generate_score())
        part = score.parts[0]
        notes = list(part.recurse().getElementsByClass(note.Note))

        self.assertEqual(len(part.getElementsByClass("Measure")), 2)
        self.assertEqual(len(notes), 64)
        self.assertTrue(all(item.tie is None for item in notes))
        self.assertTrue(any(left.pitch == right.pitch for left, right in zip(notes, notes[1:])))

    def test_hexatonic_version_uses_octave_displaced_collection(self) -> None:
        graph = apply_eigenfield_line_mapping(
            build_laplacian_eigenfield_graph(),
            pitches=OCTAVE_DISPLACED_HEXATONIC_LINE,
        )
        path = graph.graph["traversal_path"]
        written_pitches = {graph.nodes[node_id]["pitch"] for node_id in path}

        self.assertEqual(written_pitches, set(OCTAVE_DISPLACED_HEXATONIC_LINE))
        self.assertEqual(
            {item.rstrip("0123456789") for item in written_pitches},
            {"C", "D", "E", "F#", "G", "A"},
        )

        score = converter.parse(generate_hexatonic_score())
        notes = list(score.parts[0].recurse().getElementsByClass(note.Note))
        self.assertEqual(len(notes), 64)
        self.assertTrue(any(left.pitch == right.pitch for left, right in zip(notes, notes[1:])))

    def test_numerical_phrases_control_repetitions_and_rests(self) -> None:
        eigenfield = apply_eigenfield_line_mapping(
            build_laplacian_eigenfield_graph(),
            pitches=OCTAVE_DISPLACED_HEXATONIC_LINE,
        )
        phrases = build_numerical_phrase_graph(eigenfield)

        self.assertEqual(phrases.graph["phrase_cells"], (3, 5, 8, 5, 3))
        self.assertEqual(phrases.graph["repetition_cycle"], (1, 2, 3, 5, 3, 2))
        self.assertEqual(phrases.graph["interphrase_rests"], (1, 2, 3, 2))
        self.assertEqual(phrases.number_of_nodes(), 64)
        self.assertEqual(phrases.graph["total_ticks"], 72)

        score = converter.parse(generate_numerical_phrases_score())
        part = score.parts[0]
        notes = list(part.recurse().getElementsByClass(note.Note))
        rests = list(part.recurse().getElementsByClass(note.Rest))
        self.assertEqual(len(part.getElementsByClass("Measure")), 3)
        self.assertEqual(len(notes), 64)
        self.assertEqual(sum(item.quarterLength for item in rests), 1.0)


if __name__ == "__main__":
    unittest.main()
