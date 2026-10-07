"""Tests for element 5: offline history-clock audio rendering."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    HistorySonificationConfig,
    prepare_floquet_history_state,
    render_history_audio,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class HistorySonificationTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16()
        self.config = HistorySonificationConfig(
            sample_rate=8_000,
            step_duration_seconds=0.02,
            fade_seconds=0.002,
        )

    def test_render_produces_finite_nonzero_stereo_stems(self):
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_history_audio(history, self.config)
        expected_shape = (16 * 160, 2)

        for signal in (
            render.conditional,
            render.temporal_average,
            render.clock_interference,
            render.dephased_clock_reference,
            render.combined,
        ):
            self.assertEqual(signal.shape, expected_shape)
            self.assertTrue(np.isfinite(signal).all())
            self.assertGreater(float(np.max(np.abs(signal))), 0.0)
            self.assertLessEqual(float(np.max(np.abs(signal))), 0.92 + 1e-12)

    def test_audio_is_invariant_under_initial_global_phase(self):
        initial = computational_basis_state(0)
        original = prepare_floquet_history_state(self.model, initial)
        phase_shifted = prepare_floquet_history_state(
            self.model,
            np.exp(0.731j) * initial,
        )
        first = render_history_audio(original, self.config)
        second = render_history_audio(phase_shifted, self.config)

        np.testing.assert_allclose(first.conditional, second.conditional, atol=1e-11)
        np.testing.assert_allclose(
            first.temporal_average,
            second.temporal_average,
            atol=1e-11,
        )
        np.testing.assert_allclose(
            first.clock_interference,
            second.clock_interference,
            atol=1e-11,
        )

    def test_coherent_clock_sound_differs_from_dephased_reference(self):
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_history_audio(history, self.config)
        difference = float(
            np.linalg.norm(
                render.clock_interference - render.dephased_clock_reference
            )
        )
        self.assertGreater(difference, 1.0)


if __name__ == "__main__":
    unittest.main()
