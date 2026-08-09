from __future__ import annotations

import unittest

import networkx as nx
from music21 import converter, note

from procedural_notation_v1 import build_dodecahedron_graph
from procedural_notation_v1.dodecahedron_score import (
    apply_dodecahedron_mapping,
    apply_polyphonic_dodecahedron_mapping,
)
from procedural_notation_v1.generate_dodecahedron_score import main as generate_score
from procedural_notation_v1.generate_dodecahedron_polyphonic_score import (
    main as generate_polyphonic_score,
)


class DodecahedronScoreTests(unittest.TestCase):
    def test_geometry_controls_pitch_onset_and_duration(self) -> None:
        graph = apply_dodecahedron_mapping(build_dodecahedron_graph())
        data = [node_data for _, node_data in graph.nodes(data=True)]
        onsets = sorted(node_data["onset_tick"] for node_data in data)

        self.assertEqual(len(onsets), 20)
        self.assertEqual(len(set(onsets)), 20)
        self.assertTrue(all(right - left >= 2 for left, right in zip(onsets, onsets[1:])))
        self.assertTrue(any(node_data["pitch_space"] % 1 == 0.5 for node_data in data))
        self.assertTrue(any(node_data["duration_ticks"] > 1 for node_data in data))
        self.assertTrue(
            any(
                node_data["onset_tick"] // 32
                != (node_data["onset_tick"] + node_data["duration_ticks"] - 1) // 32
                for node_data in data
            )
        )

    def test_musicxml_contains_four_measures_rests_and_ties(self) -> None:
        score = converter.parse(generate_score())
        part = score.parts[0]
        measures = list(part.getElementsByClass("Measure"))
        notes = list(part.recurse().getElementsByClass(note.Note))
        rests = list(part.recurse().getElementsByClass(note.Rest))
        tie_types = [item.tie.type for item in notes if item.tie is not None]

        self.assertEqual(len(measures), 4)
        self.assertTrue(all(float(measure.duration.quarterLength) == 4.0 for measure in measures))
        self.assertGreater(len(rests), 0)
        self.assertIn("start", tie_types)
        self.assertIn("stop", tie_types)
        self.assertEqual(sum(bool(item.lyrics) for item in notes), 20)


class PolyphonicDodecahedronScoreTests(unittest.TestCase):
    def test_rotations_create_three_complete_overlapping_voices(self) -> None:
        graph = apply_polyphonic_dodecahedron_mapping(build_dodecahedron_graph())
        voices = {data["voice"] for _, data in graph.nodes(data=True)}

        self.assertEqual(voices, {0, 1, 2})
        self.assertEqual(graph.number_of_nodes(), 60)
        self.assertEqual(graph.number_of_edges(), 90)
        self.assertTrue(all(graph.nodes[start]["voice"] == graph.nodes[end]["voice"] for start, end in graph.edges))
        for voice in voices:
            voice_graph = graph.subgraph(
                node_id for node_id, data in graph.nodes(data=True) if data["voice"] == voice
            )
            self.assertTrue(nx.is_isomorphic(voice_graph, nx.dodecahedral_graph()))
        self.assertTrue(all(data["pitch_space"] % 1 == 0 for _, data in graph.nodes(data=True)))
        self.assertEqual(graph.graph["voice_degree_rotations"], (0, 1, 2))
        expected_names = ({"C", "D", "E", "G", "A"},) * 3
        for voice in voices:
            self.assertEqual(
                {
                    note.Note(data["pitch"]).pitch.name
                    for _, data in graph.nodes(data=True)
                    if data["voice"] == voice
                },
                expected_names[voice],
            )

        for voice in voices:
            degree_counts = {
                degree: sum(
                    data["voice"] == voice and data["pentatonic_degree"] == degree
                    for _, data in graph.nodes(data=True)
                )
                for degree in range(5)
            }
            self.assertEqual(degree_counts, {degree: 4 for degree in range(5)})
            for face in graph.graph["pentagonal_faces"]:
                self.assertEqual(
                    {graph.nodes[(voice, source_vertex)]["pentatonic_degree"] for source_vertex in face},
                    set(range(5)),
                )
                self.assertEqual(
                    {graph.nodes[(voice, source_vertex)]["sounding_degree"] for source_vertex in face},
                    set(range(5)),
                )
            for degree in range(5):
                self.assertEqual(
                    {
                        data["octave_layer"]
                        for _, data in graph.nodes(data=True)
                        if data["voice"] == voice and data["pentatonic_degree"] == degree
                    },
                    {0, 1, 2, 3},
                )
        for _, data in graph.nodes(data=True):
            self.assertEqual(
                data["pitch_space"],
                36
                + 12 * data["octave_layer"]
                + (0, 2, 4, 7, 9)[data["sounding_degree"]],
            )

        starts = []
        intervals_by_voice: dict[int, list[tuple[int, int]]] = {}
        for voice in sorted(voices):
            intervals = sorted(
                (data["onset_tick"], data["onset_tick"] + data["duration_ticks"])
                for _, data in graph.nodes(data=True)
                if data["voice"] == voice
            )
            starts.append(intervals[0][0])
            intervals_by_voice[voice] = intervals
            self.assertTrue(
                all(left_end <= right_start for (_, left_end), (right_start, _) in zip(intervals, intervals[1:]))
            )
        self.assertEqual(len(set(starts)), 3)
        self.assertTrue(
            any(
                max(left_start, right_start) < min(left_end, right_end)
                for left_voice in range(3)
                for right_voice in range(left_voice + 1, 3)
                for left_start, left_end in intervals_by_voice[left_voice]
                for right_start, right_end in intervals_by_voice[right_voice]
            )
        )

    def test_polyphonic_musicxml_has_three_six_measure_parts(self) -> None:
        score = converter.parse(generate_polyphonic_score())

        self.assertEqual(len(score.parts), 3)
        self.assertTrue(
            all(len(part.getElementsByClass("Measure")) == 6 for part in score.parts)
        )
        notes = list(score.recurse().getElementsByClass(note.Note))
        rests = list(score.recurse().getElementsByClass(note.Rest))
        tie_types = [item.tie.type for item in notes if item.tie is not None]
        self.assertEqual(sum(bool(item.lyrics) for item in notes), 60)
        self.assertGreater(len(rests), 0)
        self.assertIn("start", tie_types)
        self.assertIn("stop", tie_types)


if __name__ == "__main__":
    unittest.main()
