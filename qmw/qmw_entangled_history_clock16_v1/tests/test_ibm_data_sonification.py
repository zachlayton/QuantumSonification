"""Tests for direct IBM shot-record sonification."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1.ibm_data_sonification import (
    IBMDataSonificationConfig,
    decode_shot,
    render_ibm_data,
)


class IBMDataSonificationTests(unittest.TestCase):
    def setUp(self):
        self.shots = {
            "computational": [
                "0000000000",
                "0000011111",
                "0000100000",
                "0000110011",
            ],
            "clock_fourier": [
                "0000110000",
                "1000110000",
                "0001000000",
                "1001000000",
            ],
        }
        self.ideal = np.full(64, 1.0 / 64.0)
        self.config = IBMDataSonificationConfig(
            sample_rate=8_000,
            grain_seconds=0.008,
            ab_gap_seconds=0.05,
        )

    def test_ten_qubit_bit_order(self):
        self.assertEqual(decode_shot("1000110101"), (35, 5))

    def test_one_event_per_shot_and_forbidden_history_is_reported(self):
        render = render_ibm_data(self.shots, self.ideal, self.config)
        self.assertEqual(render.report["shots_per_circuit"], 4)
        self.assertEqual(render.report["computational_forbidden_shots"], 1)
        self.assertAlmostEqual(
            render.report["computational_historical_consistency"],
            0.75,
        )
        for signal in (
            render.ibm_computational,
            render.ibm_clock_fourier,
            render.ibm_combined,
            render.ideal_combined,
            render.ibm_then_ideal,
        ):
            self.assertTrue(np.isfinite(signal).all())
            self.assertGreater(float(np.max(np.abs(signal))), 0.0)

    def test_render_is_deterministic(self):
        first = render_ibm_data(self.shots, self.ideal, self.config)
        second = render_ibm_data(self.shots, self.ideal, self.config)
        np.testing.assert_allclose(first.ibm_then_ideal, second.ibm_then_ideal)


if __name__ == "__main__":
    unittest.main()
