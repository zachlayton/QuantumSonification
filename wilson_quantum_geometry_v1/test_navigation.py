from __future__ import annotations

import unittest
from fractions import Fraction

from wilson_quantum_geometry_v1.navigation import (
    MOSScaleTreeNavigator,
    PascalInstrumentation,
    plan_cps_graph_path,
    validate_constant_structure,
)


class ConstantStructureNavigationTests(unittest.TestCase):
    def test_exact_interval_classes_must_keep_one_step_count(self) -> None:
        pythagorean_pentatonic = (
            Fraction(1),
            Fraction(9, 8),
            Fraction(4, 3),
            Fraction(3, 2),
            Fraction(27, 16),
        )
        report = validate_constant_structure(pythagorean_pentatonic)
        self.assertTrue(report.is_constant_structure)

        inconsistent = (
            Fraction(1),
            Fraction(9, 8),
            Fraction(5, 4),
            Fraction(3, 2),
            Fraction(15, 8),
        )
        failed = validate_constant_structure(inconsistent)
        self.assertFalse(failed.is_constant_structure)
        three_halves = next(
            violation for violation in failed.violations if violation.interval == Fraction(3, 2)
        )
        self.assertEqual(three_halves.step_counts, (2, 3))

    def test_mos_ancestor_descendant_morph_keeps_generator_power_ids(self) -> None:
        navigator = MOSScaleTreeNavigator(4 / 3, (1, 2))
        start = navigator.begin((3, 7))
        self.assertEqual([voice.voice_id for voice in start.voices], list(range(7)))
        self.assertEqual([voice.activation for voice in start.voices[:2]], [1.0, 1.0])
        self.assertEqual([voice.activation for voice in start.voices[2:]], [0.0] * 5)

        middle = navigator.set_progress(0.5)
        self.assertAlmostEqual(middle.active_voice_count, 4.5)
        end = navigator.set_progress(1.0)
        self.assertEqual(navigator.current, Fraction(3, 7))
        self.assertTrue(all(voice.activation == 1.0 for voice in end.voices))
        self.assertEqual(
            [voice.position for voice in start.voices[:2]],
            [voice.position for voice in end.voices[:2]],
        )

    def test_non_mos_scale_tree_position_is_rejected(self) -> None:
        navigator = MOSScaleTreeNavigator(4 / 3, (2, 5))
        with self.assertRaisesRegex(ValueError, "not a MOS position"):
            navigator.begin((3, 8))


class PascalInstrumentationTests(unittest.TestCase):
    def test_eikosany_exposes_paired_dekanies_and_nested_hexanies(self) -> None:
        instrumentation = PascalInstrumentation((1, 3, 5, 7, 11, 13))
        shell = instrumentation.select_grade(3)
        self.assertEqual(shell.dimension, 20)
        eikosany = instrumentation.cps()
        self.assertEqual(eikosany.dimension, 20)
        self.assertTrue(all(tone.complement_index is not None for tone in eikosany.tones))

        subspaces = instrumentation.eikosany_subspaces()
        self.assertEqual(len(subspaces["dekany_2_5"]), 6)
        self.assertEqual(len(subspaces["dekany_3_5"]), 6)
        self.assertEqual(len(subspaces["hexany_2_4"]), 30)
        self.assertTrue(all(item.dimension == 10 for item in subspaces["dekany_2_5"]))
        self.assertTrue(all(item.dimension == 10 for item in subspaces["dekany_3_5"]))
        self.assertTrue(all(item.dimension == 6 for item in subspaces["hexany_2_4"]))
        self.assertEqual(
            len({item.parent_tone_indices for item in subspaces["hexany_2_4"]}),
            30,
        )

    def test_cps_path_timeline_preserves_edges_and_maps_eigenfield_time(self) -> None:
        instrumentation = PascalInstrumentation((1, 3, 5, 7))
        cps = instrumentation.cps(2)
        target = cps.tones[0].complement_index
        self.assertIsNotNone(target)
        timeline = plan_cps_graph_path(
            cps,
            0,
            target,
            total_duration_ms=800,
            eigenfield_values=(0.1, 1.0, 0.5, 0.7, 0.4, 0.2),
        )
        self.assertEqual(timeline.vertex_indices[0], 0)
        self.assertEqual(timeline.vertex_indices[-1], target)
        self.assertAlmostEqual(timeline.events[-1].arrival_ms, 800.0)
        graph_edges = {frozenset(edge) for edge in cps.edges()}
        for left, right in zip(timeline.vertex_indices, timeline.vertex_indices[1:]):
            self.assertIn(frozenset((left, right)), graph_edges)
        self.assertTrue(all(0 <= event.spectral_position < 1 for event in timeline.events))


if __name__ == "__main__":
    unittest.main()
