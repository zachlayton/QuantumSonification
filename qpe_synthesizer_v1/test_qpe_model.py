from __future__ import annotations

import unittest

import numpy as np

from qpe_synthesizer_v1.qpe_model import (
    conditional_eigenstate_probabilities,
    Eigenstate,
    mixture_distribution,
    phase_distribution,
    phase_to_frequency,
    run_qpe,
)


class QPEModelTests(unittest.TestCase):
    def test_exact_binary_phase_is_deterministic(self) -> None:
        distribution = phase_distribution(5 / 8, 3)
        self.assertAlmostEqual(float(distribution[5]), 1.0, places=14)
        self.assertAlmostEqual(float(np.sum(distribution)), 1.0, places=14)

    def test_nonrepresentable_phase_has_normalized_dirichlet_lobes(self) -> None:
        distribution = phase_distribution(0.31, 5)
        self.assertAlmostEqual(float(np.sum(distribution)), 1.0, places=14)
        self.assertEqual(int(np.argmax(distribution)), round(0.31 * 32))
        self.assertGreater(float(distribution[10]), float(distribution[9]))

    def test_phase_wrap_is_periodic(self) -> None:
        np.testing.assert_allclose(
            phase_distribution(-0.17, 6), phase_distribution(0.83, 6), atol=1e-14
        )

    def test_mixture_uses_born_weights(self) -> None:
        states = [Eigenstate(0.25, 1.0, "A"), Eigenstate(0.75, 2.0, "B")]
        distribution = mixture_distribution(states, 2)
        self.assertAlmostEqual(float(distribution[1]), 0.2, places=14)
        self.assertAlmostEqual(float(distribution[3]), 0.8, places=14)

    def test_phase_measurement_conditions_unresolved_eigenstates(self) -> None:
        states = [Eigenstate(0.300, 1.0, "A"), Eigenstate(0.309, 1.0, "B")]
        coarse = conditional_eigenstate_probabilities(states, 3, 2)
        fine_outcome = round(0.300 * 256)
        fine = conditional_eigenstate_probabilities(states, 8, fine_outcome)
        self.assertAlmostEqual(float(np.sum(coarse)), 1.0)
        self.assertGreater(float(np.min(coarse)), 0.1)
        self.assertGreater(float(fine[0]), float(coarse[0]))

    def test_shots_collapse_with_born_frequencies(self) -> None:
        rng = np.random.default_rng(20260718)
        states = [Eigenstate(0.125, 0.5, "dim"), Eigenstate(0.625, np.sqrt(0.75), "bright")]
        shots = [run_qpe(states, 3, rng) for _ in range(20_000)]
        bright = sum(shot.eigenstate_index == 1 for shot in shots) / len(shots)
        self.assertAlmostEqual(bright, 0.75, delta=0.015)
        self.assertTrue(all(shot.measured_phase == shot.exact_phase for shot in shots))

    def test_more_bits_reduce_expected_circular_error(self) -> None:
        phase = 0.30123
        errors = []
        for bits in (3, 8):
            distribution = phase_distribution(phase, bits)
            grid = np.arange(1 << bits) / (1 << bits)
            circular = np.abs((grid - phase + 0.5) % 1.0 - 0.5)
            errors.append(float(np.sum(distribution * circular)))
        self.assertLess(errors[1], errors[0])

    def test_frequency_mapping_is_octave_exponential(self) -> None:
        self.assertAlmostEqual(phase_to_frequency(0.0, root_hz=55, span_octaves=4), 55.0)
        self.assertAlmostEqual(phase_to_frequency(0.5, root_hz=55, span_octaves=4), 220.0)


if __name__ == "__main__":
    unittest.main()
