from __future__ import annotations

from collections import Counter, defaultdict
import contextlib
import io
import statistics
import unittest

from music21 import converter, note

from procedural_notation_v1.generate_quartic_torus_curvature_canon_score import (
    main as generate_score,
)
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_motion import build_torus_32_voice_rotating_mesh


class TorusCurvatureCanonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
        cls.canon = build_torus_32_voice_rotating_mesh(
            cls.surface,
            rotations=4,
            curvature_motion=True,
        )

    def test_curvature_accelerates_outer_surface_and_decelerates_inner_surface(self) -> None:
        positive_ratios = []
        negative_ratios = []
        for _, data in self.canon.nodes(data=True):
            ratio = data["elongation_ticks"] / (
                data["base_elongation_ticks"] * data["mensuration_factor"]
            )
            if data["normalized_curvature"] > 0.2:
                positive_ratios.append(ratio)
            elif data["normalized_curvature"] < -0.2:
                negative_ratios.append(ratio)

        self.assertLess(
            statistics.mean(positive_ratios),
            statistics.mean(negative_ratios),
        )
        self.assertEqual(
            {data["curvature_rest_units"] for _, data in self.canon.nodes(data=True)},
            {0, 1},
        )

    def test_meridian_voices_accelerate_and_decelerate_during_each_orbit(self) -> None:
        scales_by_voice_orbit = defaultdict(set)
        for _, data in self.canon.nodes(data=True):
            if data["voice_family"] == "meridian":
                scales_by_voice_orbit[(data["voice"], data["orbit_index"])].add(
                    round(data["curvature_time_scale"], 4)
                )

        self.assertTrue(all(len(scales) >= 5 for scales in scales_by_voice_orbit.values()))

    def test_canon_form_and_pitch_events_are_preserved(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.canon.nodes(data=True))

        self.assertEqual(len(voice_counts), 32)
        self.assertEqual(set(voice_counts.values()), {64})
        self.assertEqual(
            {data["canon_entry_index"] for _, data in self.canon.nodes(data=True)},
            set(range(32)),
        )

    def test_musicxml_contains_complete_curvature_canon(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        attack_counts = {
            sum(
                item.tie is None or item.tie.type == "start"
                for item in part.recurse().getElementsByClass(note.Note)
            )
            for part in score.parts
        }
        self.assertEqual(attack_counts, {64})
        self.assertGreater(len(score.parts[0].getElementsByClass("Measure")), 10)


if __name__ == "__main__":
    unittest.main()
