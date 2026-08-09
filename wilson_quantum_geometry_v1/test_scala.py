from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .scala import (
    analyze_scala_constant_structure,
    format_scl,
    load_scl,
    parse_scl,
    project_ratio_index_to_scala,
    project_ratio_to_scala,
    save_scl,
    scala_scale_from_ratios,
)


class ScalaScaleTests(unittest.TestCase):
    def test_parse_ratios_integers_cents_and_comments(self) -> None:
        scale = parse_scl(
            "! demo.scl\nDemo scale\n4\n! degrees\n16/15 comment\n203.910\n3\n2/1\n"
        )
        self.assertEqual(scale.description, "Demo scale")
        self.assertEqual(scale.size, 4)
        self.assertAlmostEqual(scale.ratios[0], 16 / 15)
        self.assertAlmostEqual(scale.ratios[1], 2 ** (203.910 / 1200))
        self.assertEqual(scale.ratios[2:], (3.0, 2.0))

    def test_format_and_file_roundtrip(self) -> None:
        scale = scala_scale_from_ratios(
            (1.0, 5 / 4, 3 / 2, 2.0),
            description="QMW test",
        )
        self.assertIn("5/4", format_scl(scale))
        with tempfile.TemporaryDirectory() as directory:
            path = save_scl(Path(directory) / "roundtrip", scale)
            self.assertEqual(path.suffix, ".scl")
            self.assertEqual(load_scl(path), scale)

    def test_harmonic_ratio_projects_to_nearest_scale_degree(self) -> None:
        scale = scala_scale_from_ratios(
            (1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2.0),
            description="seven limit",
        )
        self.assertAlmostEqual(project_ratio_to_scala(1.49, scale), 3 / 2)
        self.assertEqual(
            scale.pitch_classes[project_ratio_index_to_scala(1.49, scale)],
            3 / 2,
        )

    def test_constant_structure_analysis_finds_step_count_collision(self) -> None:
        constant = scala_scale_from_ratios(
            (1.0, 9 / 8, 4 / 3, 3 / 2, 27 / 16, 2.0),
            description="Pythagorean pentatonic",
        )
        inconsistent = scala_scale_from_ratios(
            (1.0, 9 / 8, 5 / 4, 3 / 2, 15 / 8, 2.0),
            description="inconsistent",
        )
        self.assertTrue(analyze_scala_constant_structure(constant).is_constant_structure)
        report = analyze_scala_constant_structure(inconsistent)
        self.assertFalse(report.is_constant_structure)
        self.assertGreater(report.conflicting_class_count, 0)


if __name__ == "__main__":
    unittest.main()
