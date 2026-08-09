from __future__ import annotations

from collections import defaultdict
import contextlib
import io
import unittest

from music21 import converter, note, pitch

from procedural_notation_v1.density_matrix_canon import (
    DEFAULT_FIXED_TRANSPOSITIONS,
    build_density_matrix_cable_net_canon,
)
from procedural_notation_v1.density_matrix_field import build_density_matrix_snapshots
from procedural_notation_v1.generate_density_matrix_fixed_transpositions_score import (
    FIXED_TRANSPOSITION_TIMES,
    main as generate_score,
)
from procedural_notation_v1.surface_mesh_graph import TORUS_HEXATONIC_SET
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


class DensityMatrixFixedTranspositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshots = build_density_matrix_snapshots(FIXED_TRANSPOSITION_TIMES)
        surface = build_tensile_saddle_mesh()
        cls.fixed_pitch = build_density_matrix_cable_net_canon(
            surface,
            cls.snapshots,
            fixed_set_transpositions=DEFAULT_FIXED_TRANSPOSITIONS,
        )
        cls.untransposed = build_density_matrix_cable_net_canon(
            surface,
            cls.snapshots,
        )

    def test_all_five_transpositions_are_global_snapshot_states(self) -> None:
        self.assertEqual(
            set(self.fixed_pitch.graph["snapshot_transpositions"]),
            set(DEFAULT_FIXED_TRANSPOSITIONS),
        )
        transpositions_by_snapshot = defaultdict(set)
        for _, data in self.fixed_pitch.nodes(data=True):
            transpositions_by_snapshot[data["snapshot_index"]].add(
                data["total_transposition_semitones"]
            )

        self.assertEqual(set(transpositions_by_snapshot), set(range(5)))
        self.assertTrue(all(len(values) == 1 for values in transpositions_by_snapshot.values()))
        self.assertEqual(
            {data["coherence_transposition_semitones"] for _, data in self.fixed_pitch.nodes(data=True)},
            {0},
        )

    def test_each_snapshot_stays_inside_one_transposed_hexatonic_set(self) -> None:
        expected_pitch_classes = {}
        for transposition in DEFAULT_FIXED_TRANSPOSITIONS:
            expected_pitch_classes[transposition] = {
                pitch.Pitch(name).transpose(transposition).pitchClass
                for name in TORUS_HEXATONIC_SET
            }

        for snapshot_index, transposition in enumerate(
            self.fixed_pitch.graph["snapshot_transpositions"]
        ):
            sounding_pitch_classes = {
                int(data["pitch_space"]) % 12
                for _, data in self.fixed_pitch.nodes(data=True)
                if data["snapshot_index"] == snapshot_index
            }
            self.assertLessEqual(
                sounding_pitch_classes,
                expected_pitch_classes[transposition],
            )

    def test_fixed_transposition_leaves_density_and_rhythm_unchanged(self) -> None:
        self.assertEqual(set(self.fixed_pitch.nodes), set(self.untransposed.nodes))
        for event_id in self.fixed_pitch.nodes:
            fixed = self.fixed_pitch.nodes[event_id]
            original = self.untransposed.nodes[event_id]
            self.assertEqual(fixed["onset_tick"], original["onset_tick"])
            self.assertEqual(fixed["duration_ticks"], original["duration_ticks"])

    def test_musicxml_preserves_five_transposition_form(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        self.assertTrue(
            all(part.recurse().getElementsByClass(note.Note) for part in score.parts)
        )


if __name__ == "__main__":
    unittest.main()
