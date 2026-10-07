"""Tests for element 3: system--time and clock-frequency diagnostics."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    analyze_history,
    prepare_discrete_history_state,
    prepare_floquet_history_state,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class HistoryDiagnosticsTests(unittest.TestCase):
    def test_stationary_history_is_separable_and_zero_frequency(self):
        identity = np.eye(16, dtype=np.complex128)
        initial = computational_basis_state(3)
        history = prepare_discrete_history_state(identity, initial)
        diagnostics = analyze_history(history)

        self.assertAlmostEqual(diagnostics.clock_purity, 1.0, places=12)
        self.assertAlmostEqual(
            diagnostics.system_time_linear_entropy,
            0.0,
            places=12,
        )
        self.assertAlmostEqual(
            diagnostics.discrete_loschmidt_echo_average,
            1.0,
            places=12,
        )
        self.assertEqual(diagnostics.dominant_clock_fourier_mode, 0)
        self.assertEqual(diagnostics.effective_schmidt_rank, 1)
        self.assertAlmostEqual(
            diagnostics.schmidt_participation_number,
            1.0,
            places=12,
        )
        self.assertAlmostEqual(
            diagnostics.schmidt_von_neumann_entropy_bits,
            0.0,
            places=12,
        )
        expected_modes = np.zeros(16)
        expected_modes[0] = 1.0
        np.testing.assert_allclose(
            diagnostics.clock_fourier_probabilities,
            expected_modes,
            atol=1e-12,
        )

    def test_clock_qft_resolves_a_stationary_system_global_phase(self):
        mode = 3
        phases = np.ones(16, dtype=np.complex128)
        phases[5] = np.exp(2j * np.pi * mode / 16.0)
        unitary = np.diag(phases)
        initial = computational_basis_state(5)
        history = prepare_discrete_history_state(unitary, initial)
        diagnostics = analyze_history(history)

        self.assertAlmostEqual(
            diagnostics.system_time_linear_entropy,
            0.0,
            places=12,
        )
        self.assertEqual(diagnostics.dominant_clock_fourier_mode, mode)
        self.assertAlmostEqual(
            diagnostics.clock_fourier_probabilities[mode],
            1.0,
            places=12,
        )

    def test_orthogonal_cyclic_history_is_maximally_entangled(self):
        shift = np.zeros((16, 16), dtype=np.complex128)
        for basis_index in range(16):
            shift[(basis_index + 1) % 16, basis_index] = 1.0
        initial = computational_basis_state(0)
        history = prepare_discrete_history_state(shift, initial)
        diagnostics = analyze_history(history)

        np.testing.assert_allclose(
            diagnostics.clock_density,
            np.eye(16) / 16.0,
            atol=1e-12,
        )
        self.assertAlmostEqual(diagnostics.clock_purity, 1.0 / 16.0, places=12)
        self.assertEqual(diagnostics.effective_schmidt_rank, 16)
        self.assertAlmostEqual(
            diagnostics.schmidt_participation_number,
            16.0,
            places=10,
        )
        self.assertAlmostEqual(
            diagnostics.schmidt_von_neumann_entropy_bits,
            4.0,
            places=10,
        )
        np.testing.assert_allclose(
            diagnostics.clock_schmidt_eigenvalues,
            np.full(16, 1.0 / 16.0),
            atol=1e-12,
        )
        self.assertAlmostEqual(
            diagnostics.system_time_linear_entropy,
            15.0 / 16.0,
            places=12,
        )
        self.assertAlmostEqual(
            diagnostics.discrete_loschmidt_echo_average,
            1.0 / 16.0,
            places=12,
        )
        np.testing.assert_allclose(
            diagnostics.clock_fourier_probabilities,
            np.full(16, 1.0 / 16.0),
            atol=1e-12,
        )

    def test_floquet_reduced_states_and_fourier_probabilities_are_consistent(self):
        model = FloquetTimeCrystal16()
        history = prepare_floquet_history_state(
            model,
            computational_basis_state(0),
        )
        diagnostics = analyze_history(history)

        expected_average = np.mean(
            history.conditional_densities(),
            axis=0,
        )
        np.testing.assert_allclose(
            diagnostics.system_average_density,
            expected_average,
            atol=1e-11,
        )
        self.assertAlmostEqual(
            float(np.trace(diagnostics.clock_density).real),
            1.0,
            places=12,
        )
        self.assertAlmostEqual(
            float(np.trace(diagnostics.system_average_density).real),
            1.0,
            places=12,
        )
        self.assertAlmostEqual(
            diagnostics.clock_purity,
            diagnostics.system_average_purity,
            places=11,
        )
        self.assertAlmostEqual(
            float(diagnostics.clock_fourier_probabilities.sum()),
            1.0,
            places=12,
        )
        self.assertTrue(
            np.all(diagnostics.clock_fourier_probabilities >= 0.0)
        )
        self.assertTrue(np.all(diagnostics.loschmidt_echoes >= 0.0))
        self.assertTrue(np.all(diagnostics.loschmidt_echoes <= 1.0 + 1e-12))


if __name__ == "__main__":
    unittest.main()
