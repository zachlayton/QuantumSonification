"""Tests for element 1: exact preparation of the Floquet history state."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    prepare_discrete_history_state,
    prepare_floquet_history_state,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class DiscreteHistoryStateTests(unittest.TestCase):
    def test_four_clock_qubits_and_four_system_qubits_form_256_state_vector(self):
        model = FloquetTimeCrystal16()
        history = prepare_floquet_history_state(
            model,
            computational_basis_state(0),
        )

        self.assertEqual(history.clock_qubits, 4)
        self.assertEqual(history.clock_states, 16)
        self.assertEqual(history.system_qubits, 4)
        self.assertEqual(history.system_dimension, 16)
        self.assertEqual(history.joint_dimension, 256)
        self.assertEqual(history.state_vector.shape, (256,))
        self.assertEqual(history.branch_states.shape, (16, 16))
        self.assertAlmostEqual(
            float(np.vdot(history.state_vector, history.state_vector).real),
            1.0,
            places=12,
        )

    def test_every_clock_branch_equals_the_matching_floquet_power(self):
        model = FloquetTimeCrystal16()
        initial = computational_basis_state(5)
        history = prepare_floquet_history_state(model, initial)

        for clock_index in range(16):
            expected = np.linalg.matrix_power(
                model.floquet_unitary,
                clock_index,
            ) @ initial
            np.testing.assert_allclose(
                history.conditional_state(clock_index),
                expected,
                atol=1e-11,
            )
            np.testing.assert_allclose(
                history.clock_block(clock_index),
                expected / 4.0,
                atol=1e-11,
            )

    def test_binary_controlled_power_ordering(self):
        phases = np.exp(1j * np.arange(16) / 13.0)
        unitary = np.diag(phases)
        initial = np.full(16, 0.25, dtype=np.complex128)
        history = prepare_discrete_history_state(unitary, initial)

        # 13 = 1 + 4 + 8 exercises clock bits 0, 2, and 3.
        expected = np.linalg.matrix_power(unitary, 13) @ initial
        np.testing.assert_allclose(
            history.conditional_state(13),
            expected,
            atol=1e-12,
        )

    def test_joint_density_is_pure_and_normalized(self):
        model = FloquetTimeCrystal16()
        history = prepare_floquet_history_state(
            model,
            computational_basis_state(0),
        )
        density = history.density_matrix()

        self.assertEqual(density.shape, (256, 256))
        self.assertAlmostEqual(float(np.trace(density).real), 1.0, places=12)
        self.assertAlmostEqual(
            float(np.trace(density @ density).real),
            1.0,
            places=12,
        )

    def test_all_clock_conditionals_are_normalized_and_equiprobable(self):
        model = FloquetTimeCrystal16()
        history = prepare_floquet_history_state(
            model,
            computational_basis_state(0),
        )

        probabilities = history.clock_probabilities()
        states = history.conditional_states()
        densities = history.conditional_densities()

        np.testing.assert_allclose(
            probabilities,
            np.full(16, 1.0 / 16.0),
            atol=1e-12,
        )
        self.assertAlmostEqual(float(probabilities.sum()), 1.0, places=12)
        np.testing.assert_allclose(
            np.sum(np.abs(states) ** 2, axis=1),
            np.ones(16),
            atol=1e-12,
        )
        self.assertEqual(densities.shape, (16, 16, 16))
        np.testing.assert_allclose(
            np.trace(densities, axis1=1, axis2=2),
            np.ones(16),
            atol=1e-12,
        )
        for clock_index in range(16):
            np.testing.assert_allclose(
                densities[clock_index],
                history.conditional_density(clock_index),
                atol=1e-12,
            )

    def test_conditional_densities_match_floquet_trajectory(self):
        model = FloquetTimeCrystal16()
        initial = computational_basis_state(0)
        history = prepare_floquet_history_state(model, initial)
        trajectory = model.run(
            15,
            rho0=np.outer(initial, initial.conj()),
        )

        np.testing.assert_allclose(
            history.conditional_densities(),
            trajectory.density_matrices,
            atol=1e-11,
        )

    def test_rejects_nonunitary_operation(self):
        with self.assertRaisesRegex(ValueError, "unitary failed validation"):
            prepare_discrete_history_state(
                np.zeros((16, 16), dtype=np.complex128),
                computational_basis_state(0),
            )


if __name__ == "__main__":
    unittest.main()
