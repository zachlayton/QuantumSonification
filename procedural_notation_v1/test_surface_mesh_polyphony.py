from __future__ import annotations

import unittest

from music21 import converter, note

from procedural_notation_v1.generate_quartic_torus_polyphonic_score import (
    main as generate_score,
)
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_polyphony import build_torus_dual_cycle_polyphony


class TorusDualCyclePolyphonyTests(unittest.TestCase):
    def test_each_voice_covers_every_mesh_vertex_once(self) -> None:
        polyphony = build_torus_dual_cycle_polyphony(build_quartic_torus_mesh())
        voice_counts = {
            voice: sum(data["voice"] == voice for _, data in polyphony.nodes(data=True))
            for voice in polyphony.graph["voices"]
        }

        self.assertEqual(voice_counts, {"major_cycle": 96, "minor_cycle": 96})
        for voice in polyphony.graph["voices"]:
            source_vertices = {
                data["source_vertex"]
                for _, data in polyphony.nodes(data=True)
                if data["voice"] == voice
            }
            self.assertEqual(len(source_vertices), 96)

    def test_coordinate_cycles_have_distinct_collections_and_phrase_counts(self) -> None:
        polyphony = build_torus_dual_cycle_polyphony(build_quartic_torus_mesh())

        self.assertEqual(polyphony.graph["major_cycle_pitch_collection"], ("C", "D", "E", "F#", "G", "A"))
        self.assertEqual(polyphony.graph["minor_cycle_pitch_collection"], ("C", "D", "E", "G", "A"))
        self.assertEqual(len(polyphony.graph["major_cycle_rests"]), 8)
        self.assertEqual(len(polyphony.graph["minor_cycle_rests"]), 12)
        self.assertEqual(sum(polyphony.graph["major_cycle_rests"]), 24)
        self.assertEqual(sum(polyphony.graph["minor_cycle_rests"]), 24)

    def test_musicxml_contains_two_complete_simultaneous_voices(self) -> None:
        score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 2)
        self.assertEqual([len(part.getElementsByClass("Measure")) for part in score.parts], [5, 5])
        self.assertEqual(
            [len(part.recurse().getElementsByClass(note.Note)) for part in score.parts],
            [96, 96],
        )
        self.assertEqual(
            [sum(rest.quarterLength for rest in part.recurse().getElementsByClass(note.Rest)) for part in score.parts],
            [3.0, 3.0],
        )


if __name__ == "__main__":
    unittest.main()
