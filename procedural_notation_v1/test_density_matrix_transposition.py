from __future__ import annotations

from collections import defaultdict
import contextlib
import io
import unittest

from music21 import converter, note

from procedural_notation_v1.density_matrix_canon import build_density_matrix_cable_net_canon
from procedural_notation_v1.density_matrix_field import (
    build_density_matrix_snapshots,
    weighted_z_expectation,
)
from procedural_notation_v1.generate_density_matrix_transposition_score import (
    main as generate_score,
)
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


class DensityMatrixTranspositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshots = build_density_matrix_snapshots()
        surface = build_tensile_saddle_mesh()
        cls.fixed = build_density_matrix_cable_net_canon(
            surface,
            cls.snapshots,
            transpose_collections=False,
        )
        cls.transposed = build_density_matrix_cable_net_canon(
            surface,
            cls.snapshots,
            transpose_collections=True,
        )

    def test_snapshot_transposition_comes_from_weighted_z_observable(self) -> None:
        expected = tuple(round(weighted_z_expectation(density)) for density in self.snapshots)

        self.assertEqual(expected, (9, 6, 5, 6))
        self.assertEqual(self.transposed.graph["snapshot_transpositions"], expected)

    def test_transposition_changes_pitch_without_changing_density_or_rhythm(self) -> None:
        self.assertEqual(set(self.fixed.nodes), set(self.transposed.nodes))
        changed_pitch_count = 0
        for event_id in self.fixed.nodes:
            fixed = self.fixed.nodes[event_id]
            transposed = self.transposed.nodes[event_id]
            self.assertEqual(fixed["onset_tick"], transposed["onset_tick"])
            self.assertEqual(fixed["duration_ticks"], transposed["duration_ticks"])
            if fixed["pitch"] != transposed["pitch"]:
                changed_pitch_count += 1

        self.assertGreater(changed_pitch_count, self.transposed.number_of_nodes() * 0.65)

    def test_conjugate_phase_creates_opposing_local_transpositions(self) -> None:
        values_by_element = defaultdict(dict)
        for _, data in self.transposed.nodes(data=True):
            key = (
                data["snapshot_index"],
                data["matrix_row"],
                data["matrix_column"],
            )
            values_by_element[key][data["voice_family"]] = data[
                "coherence_transposition_semitones"
            ]

        paired = [values for values in values_by_element.values() if len(values) == 2]
        self.assertTrue(
            all(values["ket"] == -values["bra"] for values in paired)
        )
        pitch_classes = {
            data["transposed_pitch_class"]
            for _, data in self.transposed.nodes(data=True)
        }
        self.assertGreaterEqual(len(pitch_classes), 10)

    def test_musicxml_preserves_32_transposed_parts(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        self.assertTrue(
            all(part.recurse().getElementsByClass(note.Note) for part in score.parts)
        )


if __name__ == "__main__":
    unittest.main()
