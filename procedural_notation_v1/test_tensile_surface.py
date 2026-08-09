from __future__ import annotations

from collections import Counter
import contextlib
import io
import unittest

from music21 import converter, note

from procedural_notation_v1.generate_tensile_saddle_canon_score import main as generate_score
from procedural_notation_v1.tensile_surface_canon import build_tensile_saddle_32_voice_canon
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


class TensileSaddleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = build_tensile_saddle_mesh()
        cls.canon = build_tensile_saddle_32_voice_canon(cls.surface)

    def test_surface_is_a_harmonic_four_anchor_cable_net(self) -> None:
        self.assertEqual(self.surface.number_of_nodes(), 256)
        self.assertEqual(self.surface.number_of_edges(), 480)
        self.assertEqual(
            sum(data["anchor"] for _, data in self.surface.nodes(data=True)),
            4,
        )
        self.assertLess(
            max(abs(data["algebraic_residual"]) for _, data in self.surface.nodes(data=True)),
            1e-10,
        )
        for row in range(1, 15):
            for column in range(1, 15):
                center = self.surface.nodes[row, column]["position"][2]
                neighbor_mean = sum(
                    self.surface.nodes[node_id]["position"][2]
                    for node_id in self.surface.neighbors((row, column))
                ) / 4.0
                self.assertAlmostEqual(center, neighbor_mean)

    def test_warp_and_weft_lines_form_32_reflecting_voices(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.canon.nodes(data=True))

        self.assertEqual(len(voice_counts), 32)
        self.assertEqual(set(voice_counts.values()), {64})
        self.assertEqual(
            Counter(data["voice_family"] for _, data in self.canon.nodes(data=True)),
            {"warp": 1024, "weft": 1024},
        )
        self.assertEqual(
            {data["reflection_direction"] for _, data in self.canon.nodes(data=True)},
            {-1, 1},
        )

    def test_canon_has_interleaved_entries_and_moderate_augmentation(self) -> None:
        data = [item for _, item in self.canon.nodes(data=True)]

        self.assertEqual({item["canon_entry_index"] for item in data}, set(range(32)))
        self.assertEqual({item["mensuration_factor"] for item in data}, {1, 2})
        self.assertEqual({item["base_duration_ticks"] for item in data}, {1, 2, 3})
        self.assertEqual({item["duration_ticks"] for item in data}, {1, 2, 3, 4, 6})
        self.assertEqual({item["internal_rest_ticks"] for item in data}, {0, 1, 2, 4})

    def test_musicxml_contains_complete_tensile_canon(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        self.assertEqual(
            {
                sum(
                    item.tie is None or item.tie.type == "start"
                    for item in part.recurse().getElementsByClass(note.Note)
                )
                for part in score.parts
            },
            {64},
        )
        self.assertGreater(len(score.parts[0].getElementsByClass("Measure")), 5)


if __name__ == "__main__":
    unittest.main()
