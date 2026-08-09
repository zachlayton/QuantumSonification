"""Tests for the granular revision of element 5."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1.granular_sonification import (
    GranularHistoryConfig,
    render_granular_history,
)
from qmw_entangled_history_clock16_v1 import prepare_floquet_history_state
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class GranularHistoryTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16()
        self.config = GranularHistoryConfig(
            sample_rate=8_000,
            duration_seconds=0.8,
            rhythm_word="10101",
            clock_interval_ms_start=134.0,
            clock_interval_ms_end=117.0,
            conditional_grain_seconds=0.04,
            average_grain_seconds=0.06,
            clock_grain_seconds=0.035,
            onset_spread_fraction=0.05,
            rhythm_pulse_seconds=0.02,
        )

    def test_granular_stems_are_finite_bounded_and_nonzero(self):
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_granular_history(history, self.config)
        expected_shape = (6_400, 2)
        for signal in (
            render.rhythm_grid,
            render.conditional_cloud,
            render.temporal_average_cloud,
            render.clock_interference_cloud,
            render.dephased_clock_cloud,
            render.combined,
        ):
            self.assertEqual(signal.shape, expected_shape)
            self.assertTrue(np.isfinite(signal).all())
            self.assertGreater(float(np.max(np.abs(signal))), 0.0)
            self.assertLessEqual(float(np.max(np.abs(signal))), 0.92 + 1e-12)

    def test_render_is_reproducible_and_global_phase_invariant(self):
        initial = computational_basis_state(0)
        history = prepare_floquet_history_state(self.model, initial)
        phased = prepare_floquet_history_state(
            self.model,
            np.exp(1.123j) * initial,
        )
        first = render_granular_history(history, self.config)
        second = render_granular_history(phased, self.config)
        np.testing.assert_allclose(first.combined, second.combined, atol=1e-11)

    def test_clock_cloud_differs_from_matched_dephased_control(self):
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_granular_history(history, self.config)
        self.assertGreater(
            float(np.linalg.norm(
                render.clock_interference_cloud - render.dephased_clock_cloud
            )),
            1.0,
        )

    def test_every_sounding_step_contains_all_sixteen_conditionals(self):
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_granular_history(history, self.config)
        self.assertEqual(
            render.report["event_counts"]["conditional"],
            render.report["event_counts"]["sounding_steps"] * 16,
        )

    def test_binary_word_has_millisecond_cells_and_true_rests(self):
        config = GranularHistoryConfig(
            sample_rate=8_000,
            duration_seconds=0.72,
            rhythm_word="10101",
            clock_interval_ms_start=125.0,
            clock_interval_ms_end=125.0,
            conditional_grain_seconds=0.04,
            average_grain_seconds=0.05,
            clock_grain_seconds=0.035,
            rhythm_pulse_seconds=0.02,
            onset_spread_fraction=0.04,
        )
        history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        render = render_granular_history(history, config)
        step_samples = 1_000  # 125 ms per binary cell at 8 kHz.
        energy = [
            float(np.sum(render.combined[
                index * step_samples:(index + 1) * step_samples
            ] ** 2))
            for index in range(5)
        ]
        self.assertGreater(energy[0], 0.0)
        self.assertEqual(energy[1], 0.0)
        self.assertGreater(energy[2], 0.0)
        self.assertEqual(energy[3], 0.0)
        self.assertGreater(energy[4], 0.0)


if __name__ == "__main__":
    unittest.main()
