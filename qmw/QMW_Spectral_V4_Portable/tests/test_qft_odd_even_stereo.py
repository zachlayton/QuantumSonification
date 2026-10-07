from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v3.scd"
).read_text(encoding="utf-8")


class QFTOddEvenStereoTests(unittest.TestCase):
    def test_lane_parity_maps_odd_harmonics_left_and_even_right(self):
        # Lanes are zero-based while harmonic labels are one-based.
        pans = [(((lane % 2) * 2) - 1) for lane in range(16)]
        self.assertEqual(pans[0::2], [-1] * 8)
        self.assertEqual(pans[1::2], [1] * 8)
        self.assertGreaterEqual(SOURCE.count("(((site % 2) * 2) - 1) * stereoWidth"), 2)

    def test_dynamic_and_pooled_mixers_share_the_width_control(self):
        self.assertIn(
            "SynthDef(\\qmwQFTV3PulseLaneMixer", SOURCE
        )
        self.assertIn(
            "SynthDef(\\qmwQFTV3PooledPulseMixer", SOURCE
        )
        self.assertGreaterEqual(SOURCE.count("oddEvenWidth=1"), 2)
        self.assertGreaterEqual(SOURCE.count("\\oddEvenWidth, ~qmwQFTV3OddEvenStereoWidth"), 2)

    def test_width_is_user_adjustable_and_preset_persistent(self):
        self.assertIn('"odd L / even R"', SOURCE)
        self.assertIn(
            "~qmwQFTV3OddEvenStereoWidth = view.value", SOURCE
        )
        self.assertIn(
            "oddEvenStereoWidth: oddEvenStereoSlider.value", SOURCE
        )
        self.assertIn(
            "preset[\\oddEvenStereoWidth] ? 1", SOURCE
        )


if __name__ == "__main__":
    unittest.main()
