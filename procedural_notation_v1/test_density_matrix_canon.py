from __future__ import annotations

from collections import Counter, defaultdict
import contextlib
import io
import unittest

from music21 import converter, note
import numpy as np

from procedural_notation_v1.density_matrix_canon import build_density_matrix_cable_net_canon
from procedural_notation_v1.density_matrix_field import (
    build_density_matrix_snapshots,
    density_matrix_purity,
)
from procedural_notation_v1.generate_density_matrix_canon_score import main as generate_score
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


class DensityMatrixCanonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshots = build_density_matrix_snapshots()
        cls.canon = build_density_matrix_cable_net_canon(
            build_tensile_saddle_mesh(),
            cls.snapshots,
        )

    def test_snapshots_are_valid_mixed_four_qubit_density_matrices(self) -> None:
        self.assertEqual(len(self.snapshots), 4)
        for density in self.snapshots:
            self.assertEqual(density.shape, (16, 16))
            self.assertTrue(np.allclose(density, density.conj().T))
            self.assertTrue(np.isclose(np.trace(density), 1.0))
            self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(density))), -1e-10)
            self.assertGreater(density_matrix_purity(density), 1.0 / 16.0)
            self.assertLess(density_matrix_purity(density), 1.0)
        self.assertFalse(np.allclose(self.snapshots[0], self.snapshots[-1]))

    def test_matrix_magnitude_controls_musical_density(self) -> None:
        self.assertLess(
            self.canon.graph["sounding_matrix_events"],
            self.canon.graph["possible_matrix_events"],
        )
        self.assertGreater(self.canon.graph["sounding_matrix_events"], 256)
        snapshot_counts = Counter(
            data["snapshot_index"] for _, data in self.canon.nodes(data=True)
        )
        self.assertGreater(len(set(snapshot_counts.values())), 1)
        self.assertTrue(
            all(
                data["diagonal_population"]
                for _, data in self.canon.nodes(data=True)
                if data["matrix_row"] == data["matrix_column"]
            )
        )

    def test_bra_and_ket_interpret_conjugate_phase_oppositely(self) -> None:
        phases_by_element = defaultdict(dict)
        for _, data in self.canon.nodes(data=True):
            key = (
                data["snapshot_index"],
                data["matrix_row"],
                data["matrix_column"],
            )
            phases_by_element[key][data["voice_family"]] = data["applied_phase"]

        paired = [phases for phases in phases_by_element.values() if len(phases) == 2]
        self.assertGreater(len(paired), 100)
        self.assertTrue(
            all(np.isclose(phases["ket"], -phases["bra"]) for phases in paired)
        )

    def test_musicxml_contains_32_variable_density_parts(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        attack_counts = [
            sum(
                item.tie is None or item.tie.type == "start"
                for item in part.recurse().getElementsByClass(note.Note)
            )
            for part in score.parts
        ]
        self.assertGreater(max(attack_counts), min(attack_counts))
        self.assertTrue(all(count > 0 for count in attack_counts))


if __name__ == "__main__":
    unittest.main()
