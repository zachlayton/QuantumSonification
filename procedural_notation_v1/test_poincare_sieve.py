from __future__ import annotations

from collections import Counter
import contextlib
import io
import unittest

import networkx as nx
import numpy as np
from music21 import articulations, converter, dynamics, note

from procedural_notation_v1.generate_poincare_sieve_score import main as generate_score
from procedural_notation_v1.poincare_disk_graph import (
    build_poincare_disk_graph,
    poincare_distance,
)
from procedural_notation_v1.poincare_sieve_canon import build_poincare_sieve_canon
from procedural_notation_v1.xenakis_sieve import (
    DEFAULT_PARENT_PITCH_CLASSES,
    modular_pitch_sieve,
    pitch_digit,
)


class PoincareSieveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.disk = build_poincare_disk_graph()
        cls.canon = build_poincare_sieve_canon(cls.disk)

    def test_disk_has_hyperbolically_expanding_rings(self) -> None:
        self.assertEqual(self.disk.number_of_nodes(), 49)
        self.assertTrue(nx.is_connected(self.disk))
        self.assertTrue(nx.check_planarity(self.disk)[0])
        self.assertEqual(
            Counter(data["ring_index"] for _, data in self.disk.nodes(data=True)),
            {0: 1, 1: 8, 2: 16, 3: 24},
        )
        for ring_index, expected_radius in enumerate((0.0, 0.8, 1.6, 2.4)):
            node_id = (ring_index, 0)
            self.assertAlmostEqual(
                poincare_distance((0.0, 0.0), self.disk.nodes[node_id]["position"]),
                expected_radius,
            )

    def test_modular_sieve_is_larger_than_previous_fixed_collections(self) -> None:
        sieve = modular_pitch_sieve()

        self.assertEqual(len(DEFAULT_PARENT_PITCH_CLASSES), 10)
        self.assertEqual(len(sieve), 19)
        self.assertEqual(sieve[0], 36)
        self.assertEqual(sieve[-1], 94)
        parent_lattice = [
            midi_pitch
            for midi_pitch in range(36, 97)
            if midi_pitch % 12 in DEFAULT_PARENT_PITCH_CLASSES
        ]
        lattice_indices = {midi_pitch: index for index, midi_pitch in enumerate(parent_lattice)}
        self.assertTrue(
            all(
                lattice_indices[midi_pitch] % 7 in (0, 2)
                or lattice_indices[midi_pitch] % 9 == 1
                for midi_pitch in sieve
            )
        )
        self.assertEqual(
            {midi_pitch % 12 for midi_pitch in sieve},
            set(DEFAULT_PARENT_PITCH_CLASSES),
        )
        self.assertEqual({pitch_digit(midi_pitch) for midi_pitch in sieve}, set(range(10)))

    def test_eight_voices_rotate_through_every_ray_and_dilate_outward(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.canon.nodes(data=True))

        self.assertEqual(len(voice_counts), 8)
        self.assertEqual(set(voice_counts.values()), {56})
        self.assertEqual(
            {data["duration_dilation"] for _, data in self.canon.nodes(data=True)},
            {1, 2, 3, 4},
        )
        sectors_by_voice = {}
        for voice in voice_counts:
            sectors_by_voice[voice] = {
                data["sector"]
                for _, data in self.canon.nodes(data=True)
                if data["voice"] == voice
            }
        self.assertTrue(all(sectors == set(range(8)) for sectors in sectors_by_voice.values()))
        self.assertEqual(
            {data["pitch_digit"] for _, data in self.canon.nodes(data=True)},
            set(range(10)),
        )

    def test_quantum_density_field_creates_dynamic_contrast_and_accents(self) -> None:
        self.assertEqual(self.canon.graph["quantum_dynamic_snapshot_count"], 8)
        self.assertEqual(
            {data["dynamic_level"] for _, data in self.canon.nodes(data=True)},
            {"ppp", "pp", "p", "mp", "mf", "f", "ff"},
        )
        self.assertEqual(self.canon.graph["quantum_dynamic_mark_count"], 100)
        self.assertEqual(
            self.canon.graph["quantum_accent_counts"],
            {"accent": 50, "strong-accent": 27},
        )
        self.assertTrue(
            all(
                0.0 <= data["quantum_intensity"] <= 1.0
                for _, data in self.canon.nodes(data=True)
            )
        )

    def test_weighted_laplacian_eigenfield_is_valid(self) -> None:
        node_order = list(self.disk.graph["node_order"])
        adjacency = nx.to_numpy_array(self.disk, nodelist=node_order, weight="coupling")
        laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
        field = np.asarray([self.disk.nodes[node_id]["field_value"] for node_id in node_order])

        self.assertTrue(
            np.allclose(laplacian @ field, self.disk.graph["eigenvalue"] * field)
        )

    def test_musicxml_contains_eight_complete_hyperbolic_rays(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 8)
        self.assertEqual(
            {
                sum(
                    item.tie is None or item.tie.type == "start"
                    for item in part.recurse().getElementsByClass(note.Note)
                )
                for part in score.parts
            },
            {56},
        )
        self.assertEqual(
            sum(len(part.recurse().getElementsByClass(dynamics.Dynamic)) for part in score.parts),
            100,
        )
        notated_accents = [
            articulation
            for part in score.parts
            for musical_note in part.recurse().getElementsByClass(note.Note)
            for articulation in musical_note.articulations
            if isinstance(articulation, (articulations.Accent, articulations.StrongAccent))
        ]
        self.assertEqual(len(notated_accents), 77)


if __name__ == "__main__":
    unittest.main()
