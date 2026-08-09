from __future__ import annotations

import math
import random
import unittest

from pauli_statistical_grainflow_v1.statistical_model import (
    StatisticsClass,
    accessible_modes,
    dimensionless_entropy,
    microstate_count,
    sample_configuration,
)


class StatisticalModelTests(unittest.TestCase):
    def test_microstate_counts(self) -> None:
        self.assertEqual(microstate_count("fermion", 6, 2), 15)
        self.assertEqual(microstate_count("boson", 6, 2), 21)
        self.assertEqual(microstate_count("classical", 6, 2), 36)

    def test_closed_fermion_shell_is_unique_and_zero_entropy(self) -> None:
        self.assertEqual(microstate_count("fermion", 6, 6), 1)
        self.assertEqual(dimensionless_entropy("fermion", 6, 6), 0.0)

    def test_fermion_overfill_has_no_allowed_microstate(self) -> None:
        self.assertEqual(microstate_count("fermion", 4, 5), 0)
        self.assertEqual(dimensionless_entropy("fermion", 4, 5), float("-inf"))

    def test_energy_shell_selects_and_has_closest_fallback(self) -> None:
        self.assertEqual(accessible_modes(1.0, 0.0, 0.1), (1, 4))
        self.assertEqual(accessible_modes(1.0, 10.0, 0.1), (5,))

    def test_fermion_sampling_never_double_occupies(self) -> None:
        configuration = sample_configuration(
            StatisticsClass.FERMION,
            tuple(range(6)),
            5,
            rng=random.Random(4),
        )
        self.assertEqual(sum(configuration), 5)
        self.assertLessEqual(max(configuration), 1)

    def test_boson_sampling_preserves_particle_number_and_can_bunch(self) -> None:
        configuration = sample_configuration(
            StatisticsClass.BOSON,
            (2,),
            7,
            rng=random.Random(1),
        )
        self.assertEqual(configuration[2], 7)
        self.assertEqual(sum(configuration), 7)


if __name__ == "__main__":
    unittest.main()
