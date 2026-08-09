from __future__ import annotations

import math
import unittest

from zeeman_resonator_v1.zeeman_model import PRESETS, lande_g


class ZeemanModelTests(unittest.TestCase):
    def test_lande_factors_for_sodium_terms(self) -> None:
        self.assertAlmostEqual(lande_g(0.0, 0.5, 0.5), 2.0)
        self.assertAlmostEqual(lande_g(1.0, 0.5, 0.5), 2.0 / 3.0)
        self.assertAlmostEqual(lande_g(1.0, 0.5, 1.5), 4.0 / 3.0)

    def test_normal_triplet_is_symmetric_about_carrier(self) -> None:
        state = PRESETS["normal"].state(2.0, 30.0, 220.0)
        voice = state["voices"][0]
        self.assertEqual(voice["lower_hz"], 160.0)
        self.assertEqual(voice["upper_hz"], 280.0)
        self.assertEqual(state["dry_pi_strength"], 1.0)

    def test_d1_and_d2_have_expected_line_counts(self) -> None:
        self.assertEqual(len(PRESETS["sodium_d1"].components) * 2, 4)
        self.assertEqual(len(PRESETS["sodium_d2"].components) * 2, 6)

    def test_component_amplitudes_are_constant_power_normalized(self) -> None:
        for preset in PRESETS.values():
            amplitudes = preset.normalized_amplitudes()
            self.assertTrue(math.isclose(sum(a * a for a in amplitudes), 1.0))

    def test_physical_and_audible_scales_remain_separate(self) -> None:
        voice = PRESETS["sodium_d2"].state(1.0, 40.0, 440.0)["voices"][2]
        self.assertAlmostEqual(voice["audible_shift_hz"], 200.0 / 3.0)
        self.assertGreater(voice["physical_shift_hz"], 20_000_000_000.0)

    def test_quadrature_ring_products_isolate_both_sidebands(self) -> None:
        carrier_phase = 1.234
        modulator_phase = 0.456
        ring_cos = math.cos(carrier_phase) * math.cos(modulator_phase)
        ring_sin = math.sin(carrier_phase) * math.sin(modulator_phase)
        self.assertAlmostEqual(ring_cos + ring_sin, math.cos(carrier_phase - modulator_phase))
        self.assertAlmostEqual(ring_cos - ring_sin, math.cos(carrier_phase + modulator_phase))


if __name__ == "__main__":
    unittest.main()
