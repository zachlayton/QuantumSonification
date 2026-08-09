from __future__ import annotations

import math
import unittest
from fractions import Fraction

import numpy as np

from wilson_quantum_geometry_v1 import (
    CombinationProductSet,
    harmonic_distance,
    harmonic_intersection,
    interval_tuneability,
    make_mos,
    pascal_cps_row,
    prime_coordinates,
    scale_tree_position,
    simplest_ratio_within_tolerance,
)
from wilson_quantum_geometry_v1.hexany_study import (
    HexanyStudyConfig,
    build_hamiltonian,
    compose_states,
)


class CombinationProductSetTests(unittest.TestCase):
    def test_pascal_row_catalogs_all_cps_shells_and_complements(self) -> None:
        row = pascal_cps_row(6)
        self.assertEqual([shell.dimension for shell in row], [1, 6, 15, 20, 15, 6, 1])
        self.assertEqual([shell.complement_grade for shell in row], [6, 5, 4, 3, 2, 1, 0])
        self.assertTrue(row[3].is_self_complementary)
        self.assertFalse(row[2].is_self_complementary)

    def test_hexany_is_the_weight_two_four_qubit_shell(self) -> None:
        hexany = CombinationProductSet((1, 3, 5, 7), 2)
        self.assertEqual(hexany.name, "2)4 1-3-5-7")
        self.assertEqual(hexany.dimension, 6)
        self.assertEqual(len(hexany.tones), 6)
        self.assertTrue(all(tone.bitmask.bit_count() == 2 for tone in hexany.tones))
        self.assertEqual(len(hexany.edges()), 12)  # Johnson graph J(4, 2)
        self.assertTrue(all(len(hexany.neighbors(i)) == 4 for i in range(6)))

    def test_self_mirroring_cps_has_reciprocal_complements(self) -> None:
        hexany = CombinationProductSet((1, 3, 5, 7), 2)
        for tone in hexany.tones:
            complement = hexany.tones[tone.complement_index]
            self.assertEqual(complement.complement_index, tone.index)
            self.assertEqual(tone.bitmask ^ complement.bitmask, 0b1111)

    def test_state_projection_preserves_shell_leakage_and_phase(self) -> None:
        hexany = CombinationProductSet((1, 3, 5, 7), 2)
        amplitudes = [0j] * 16
        amplitudes[0b0011] = 0.5
        amplitudes[0b0101] = 0.5j
        amplitudes[0] = math.sqrt(0.5)
        projection = hexany.project_state(amplitudes)
        self.assertAlmostEqual(projection.shell_probability, 0.5)
        selected = {item.tone.bitmask: item for item in projection.tones}
        self.assertAlmostEqual(selected[0b0011].conditional_probability, 0.5)
        self.assertAlmostEqual(selected[0b0101].conditional_probability, 0.5)
        self.assertAlmostEqual(abs(selected[0b0101].relative_phase), math.pi / 2)

    def test_perceptual_edges_keep_tenney_distance_separate(self) -> None:
        hexany = CombinationProductSet((1, 3, 5, 7), 2)
        edges = hexany.perceptual_edges()
        self.assertEqual(len(edges), 12)
        for edge in edges:
            self.assertAlmostEqual(
                edge.harmonic_distance,
                harmonic_distance(Fraction(edge.interval_numerator, edge.interval_denominator)),
            )


class MOSTests(unittest.TestCase):
    def test_fourth_generator_reproduces_wilsons_mos_sequence(self) -> None:
        sizes = [
            size
            for size in range(2, 30)
            if make_mos(4 / 3, size).is_moment_of_symmetry
        ]
        self.assertEqual(sizes, [2, 3, 5, 7, 12, 17, 29])
        scale = make_mos(4 / 3, 7)
        self.assertEqual(scale.scale_type, Fraction(3, 7))
        self.assertEqual(len(scale.step_sizes), 2)

    def test_scale_tree_yields_keyboard_coordinates(self) -> None:
        position = scale_tree_position(4, 7)
        self.assertEqual(position.ancestors, (
            Fraction(1, 1),
            Fraction(1, 2),
            Fraction(2, 3),
            Fraction(3, 5),
            Fraction(4, 7),
        ))
        self.assertEqual(position.generator_coordinates, (1, 3))
        self.assertEqual(position.period_coordinates, (2, 5))


class TenneyHarmonicSpaceTests(unittest.TestCase):
    def test_prime_coordinates_and_octave_projection(self) -> None:
        self.assertEqual(prime_coordinates(Fraction(45, 28)), ((2, -2), (3, 2), (5, 1), (7, -1)))
        self.assertEqual(
            prime_coordinates(Fraction(45, 28), collapse_octaves=True),
            ((3, 2), (5, 1), (7, -1)),
        )

    def test_harmonic_distance_is_city_block_prime_distance(self) -> None:
        self.assertAlmostEqual(harmonic_distance(Fraction(3, 2)), math.log2(6))
        self.assertAlmostEqual(
            harmonic_distance(Fraction(5, 4), Fraction(3, 2)),
            math.log2(30),
        )

    def test_tolerance_selects_simplest_available_identity(self) -> None:
        equal_tempered_fifth = 2 ** (7 / 12)
        self.assertEqual(
            simplest_ratio_within_tolerance(equal_tempered_fifth, 2.0),
            Fraction(3, 2),
        )

    def test_intersection_and_tuneability_are_register_aware(self) -> None:
        self.assertAlmostEqual(harmonic_intersection(Fraction(3, 2)), 2 / 3)
        natural_seventh = interval_tuneability(Fraction(7, 4), 220.0)
        self.assertTrue(natural_seventh.tuneable)
        self.assertEqual(natural_seventh.periodicity_pitch, 55.0)
        self.assertEqual(natural_seventh.least_common_partial, 1540.0)
        high_natural_seventh = interval_tuneability(Fraction(7, 4), 1000.0)
        self.assertFalse(high_natural_seventh.tuneable)
        self.assertIn("common_partial_above_bound", high_natural_seventh.failures)


class HexanyStudyTests(unittest.TestCase):
    def test_walk_is_hermitian_normalized_and_stays_in_shell(self) -> None:
        cps = CombinationProductSet((1, 3, 5, 7), 2)
        hamiltonian = build_hamiltonian(cps)
        self.assertTrue(np.allclose(hamiltonian, hamiltonian.T.conj()))
        result = compose_states(
            HexanyStudyConfig(duration_seconds=0.3, control_rate=30)
        )
        np.testing.assert_allclose(
            np.sum(np.abs(result.states) ** 2, axis=1),
            1.0,
            atol=1e-12,
        )
        self.assertTrue(0 <= result.measurement_tone < cps.dimension)


if __name__ == "__main__":
    unittest.main()
