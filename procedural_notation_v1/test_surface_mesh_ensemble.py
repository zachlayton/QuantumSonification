from __future__ import annotations

from collections import Counter, defaultdict
import unittest

from music21 import converter, note

from procedural_notation_v1.generate_quartic_torus_32_voice_score import (
    main as generate_score,
)
from procedural_notation_v1.surface_mesh_ensemble import build_torus_32_voice_mesh
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh


class Torus32VoiceMeshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
        cls.ensemble = build_torus_32_voice_mesh(cls.surface)

    def test_ensemble_contains_32_complete_coordinate_lines(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.ensemble.nodes(data=True))

        self.assertEqual(len(voice_counts), 32)
        self.assertEqual(set(voice_counts.values()), {16})
        self.assertEqual(self.ensemble.number_of_nodes(), 512)
        self.assertEqual(
            Counter(data["voice_family"] for _, data in self.ensemble.nodes(data=True)),
            {"ring": 256, "meridian": 256},
        )

    def test_every_vertex_is_a_simultaneous_two_voice_intersection(self) -> None:
        events_by_vertex = defaultdict(list)
        for _, data in self.ensemble.nodes(data=True):
            events_by_vertex[data["source_vertex"]].append(data)

        self.assertEqual(set(events_by_vertex), set(self.surface.nodes))
        for events in events_by_vertex.values():
            self.assertEqual(len(events), 2)
            self.assertEqual({event["voice_family"] for event in events}, {"ring", "meridian"})
            self.assertEqual(len({event["onset_tick"] for event in events}), 1)

    def test_octave_registration_is_derived_from_surface_coordinates(self) -> None:
        displacements = {
            data["octave_displacement"] for _, data in self.ensemble.nodes(data=True)
        }
        errors = [
            abs(data["pitch_space"] - data["register_target"])
            for _, data in self.ensemble.nodes(data=True)
        ]

        self.assertGreaterEqual(len(displacements), 5)
        self.assertLessEqual(max(errors), 6.0)

    def test_musicxml_contains_32_independent_parts(self) -> None:
        score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        self.assertEqual(
            {len(part.getElementsByClass("Measure")) for part in score.parts},
            {1},
        )
        self.assertEqual(
            {len(part.recurse().getElementsByClass(note.Note)) for part in score.parts},
            {16},
        )
        self.assertEqual(
            {
                sum(rest.quarterLength for rest in part.recurse().getElementsByClass(note.Rest))
                for part in score.parts
            },
            {2.0},
        )


if __name__ == "__main__":
    unittest.main()
