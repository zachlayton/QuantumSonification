from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from music21 import converter, meter, note

from procedural_notation_v1 import (
    apply_pitch_mapping,
    build_regular_polygon_graph,
    build_score,
    write_musicxml,
)
from procedural_notation_v1.generate_tetrahedron_score import main as generate_tetrahedron_score


class NotationTests(unittest.TestCase):
    def test_default_mapping_assigns_c_major_octave(self) -> None:
        graph = apply_pitch_mapping(build_regular_polygon_graph())

        self.assertEqual(
            [graph.nodes[node_id]["pitch"] for node_id in graph.nodes],
            ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
        )

    def test_score_has_two_measures_and_eight_notes(self) -> None:
        graph = apply_pitch_mapping(build_regular_polygon_graph())
        score = build_score(graph)

        part = score.parts[0]
        self.assertEqual(len(part.getElementsByClass("Measure")), 2)
        self.assertEqual(
            [item.pitch.nameWithOctave for item in part.recurse().getElementsByClass(note.Note)],
            ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
        )
        self.assertEqual(part.recurse().getElementsByClass(meter.TimeSignature).first().ratioString, "4/4")

    def test_musicxml_round_trip_preserves_notes(self) -> None:
        graph = apply_pitch_mapping(build_regular_polygon_graph())
        score = build_score(graph)

        with tempfile.TemporaryDirectory() as directory:
            path = write_musicxml(score, Path(directory) / "score.musicxml")
            reparsed = converter.parse(path)

        pitches = [
            item.pitch.nameWithOctave
            for item in reparsed.parts[0].recurse().getElementsByClass(note.Note)
        ]
        self.assertEqual(pitches, ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"])

    def test_mapping_requires_one_pitch_per_node(self) -> None:
        graph = build_regular_polygon_graph()
        with self.assertRaises(ValueError):
            apply_pitch_mapping(graph, ("C4", "D4"))

    def test_tetrahedron_musicxml_round_trip(self) -> None:
        path = generate_tetrahedron_score()
        reparsed = converter.parse(path)

        part = reparsed.parts[0]
        pitches = [
            item.pitch.nameWithOctave
            for item in part.recurse().getElementsByClass(note.Note)
        ]
        durations = [
            float(item.quarterLength)
            for item in part.recurse().getElementsByClass(note.Note)
        ]
        self.assertEqual(pitches, ["C4", "E4", "C5", "G#4"])
        self.assertEqual(durations, [0.125, 0.125, 0.125, 0.125])
        self.assertEqual(
            part.recurse().getElementsByClass(meter.TimeSignature).first().ratioString,
            "1/8",
        )


if __name__ == "__main__":
    unittest.main()
