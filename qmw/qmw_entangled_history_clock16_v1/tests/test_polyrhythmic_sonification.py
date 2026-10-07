"""Tests for the sixteen-voice polyrhythmic projection."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import prepare_floquet_history_state
from qmw_entangled_history_clock16_v1.polyrhythmic_sonification import (
    PolyrhythmicHistoryConfig,
    render_polyrhythmic_history,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class PolyrhythmicHistoryTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16()
        self.history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        self.config = PolyrhythmicHistoryConfig(
            sample_rate=8_000,
            duration_seconds=1.0,
            reference_interval_ms_start=150.0,
            reference_interval_ms_end=120.0,
            conditional_grain_seconds=0.025,
            clock_grain_seconds=0.02,
        )

    def test_stems_are_finite_bounded_nonzero_stereo(self):
        render = render_polyrhythmic_history(self.history, self.config)
        for signal in (
            render.conditional_polycloud,
            render.coherent_clock_polyrhythm,
            render.dephased_clock_polyrhythm,
            render.combined,
        ):
            self.assertEqual(signal.shape, (8_000, 2))
            self.assertTrue(np.isfinite(signal).all())
            self.assertGreater(float(np.max(np.abs(signal))), 0.0)
            self.assertLessEqual(float(np.max(np.abs(signal))), 0.92 + 1e-12)

    def test_pi_paired_modes_have_sqrt_two_interval_ratio(self):
        render = render_polyrhythmic_history(self.history, self.config)
        self.assertAlmostEqual(
            render.report["pi_pair_interval_ratio"],
            np.sqrt(2.0),
            places=12,
        )

    def test_coherent_and_dephased_share_clocks_but_sound_different(self):
        render = render_polyrhythmic_history(self.history, self.config)
        self.assertGreater(
            float(np.linalg.norm(
                render.coherent_clock_polyrhythm
                - render.dephased_clock_polyrhythm
            )),
            1.0,
        )
        self.assertEqual(len(render.report["voice_sounding_event_counts"]), 16)
        self.assertEqual(render.report["voice_count"], 16)

    def test_global_phase_does_not_change_audio(self):
        phased = prepare_floquet_history_state(
            self.model,
            np.exp(0.81j) * computational_basis_state(0),
        )
        first = render_polyrhythmic_history(self.history, self.config)
        second = render_polyrhythmic_history(phased, self.config)
        np.testing.assert_allclose(first.combined, second.combined, atol=1e-11)


if __name__ == "__main__":
    unittest.main()
