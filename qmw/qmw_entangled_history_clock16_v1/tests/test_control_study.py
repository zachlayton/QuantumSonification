"""Tests for element 4: matched coherent and classical controls."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    build_control_study,
    prepare_floquet_history_state,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class HistoryControlStudyTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16()
        self.history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        self.study = build_control_study(self.history, shuffle_seed=23)

    def test_sequential_control_preserves_clock_order(self):
        np.testing.assert_array_equal(
            self.study.sequential_order,
            np.arange(16),
        )
        np.testing.assert_allclose(
            self.study.sequential_states,
            self.history.conditional_states(),
            atol=1e-12,
        )

    def test_shuffle_is_reproducible_and_preserves_every_moment(self):
        repeated = build_control_study(self.history, shuffle_seed=23)
        np.testing.assert_array_equal(
            self.study.shuffled_order,
            repeated.shuffled_order,
        )
        self.assertFalse(
            np.array_equal(self.study.shuffled_order, self.study.sequential_order)
        )
        np.testing.assert_array_equal(
            np.sort(self.study.shuffled_order),
            np.arange(16),
        )
        np.testing.assert_allclose(
            np.mean(self.study.shuffled_densities, axis=0),
            np.mean(self.study.sequential_densities, axis=0),
            atol=1e-12,
        )

    def test_clock_dephasing_removes_only_cross_time_blocks(self):
        coherent = self.study.coherent_joint_density.reshape(16, 16, 16, 16)
        incoherent = self.study.incoherent_joint_density.reshape(16, 16, 16, 16)

        for left in range(16):
            for right in range(16):
                if left == right:
                    np.testing.assert_allclose(
                        incoherent[left, :, right, :],
                        coherent[left, :, right, :],
                        atol=1e-12,
                    )
                else:
                    np.testing.assert_allclose(
                        incoherent[left, :, right, :],
                        np.zeros((16, 16)),
                        atol=1e-12,
                    )

    def test_only_coherent_joint_state_retains_temporal_blocks(self):
        self.assertAlmostEqual(
            self.study.coherent_temporal_block_coherence,
            1.0,
            places=12,
        )
        self.assertAlmostEqual(
            self.study.incoherent_temporal_block_coherence,
            0.0,
            places=12,
        )
        self.assertAlmostEqual(self.study.coherent_joint_purity, 1.0, places=12)
        self.assertAlmostEqual(
            self.study.incoherent_joint_purity,
            1.0 / 16.0,
            places=12,
        )

    def test_coherent_and_incoherent_histories_share_system_average(self):
        np.testing.assert_allclose(
            self.study.coherent_reduced_system,
            self.study.incoherent_reduced_system,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            self.study.coherent_reduced_system,
            np.mean(self.study.sequential_densities, axis=0),
            atol=1e-12,
        )
        self.assertAlmostEqual(
            self.study.reduced_system_difference,
            0.0,
            places=12,
        )

    def test_incoherent_clock_is_maximally_mixed(self):
        np.testing.assert_allclose(
            self.study.incoherent_reduced_clock,
            np.eye(16) / 16.0,
            atol=1e-12,
        )

    def test_order_sensitive_distances_can_distinguish_shuffle(self):
        self.assertEqual(self.study.sequential_adjacent_distances.shape, (15,))
        self.assertEqual(self.study.shuffled_adjacent_distances.shape, (15,))
        self.assertFalse(
            np.allclose(
                self.study.sequential_adjacent_distances,
                self.study.shuffled_adjacent_distances,
                atol=1e-12,
            )
        )


if __name__ == "__main__":
    unittest.main()
