from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v3.scd"
).read_text(encoding="utf-8")


class QFTFundamentalTuningModeTests(unittest.TestCase):
    def test_gui_offers_smooth_and_twelve_tet_modes(self):
        self.assertIn('items_(["smooth Hz", "12-TET (A=440)"])', SOURCE)
        self.assertIn("~qmwQFTV3FundamentalMode = menu.value", SOURCE)

    def test_twelve_tet_mode_quantizes_the_applied_frequency(self):
        self.assertIn(
            "appliedFrequency.cpsmidi.round.midicps.clip(1, 220)",
            SOURCE,
        )
        self.assertIn("synth.set(\\fundamental, appliedFrequency)", SOURCE)
        self.assertIn("~qmwQFTV3UpdateRingMod.()", SOURCE)
        self.assertIn("sendPerformanceConfig.()", SOURCE)

    def test_presets_round_trip_mode_with_smooth_legacy_default(self):
        self.assertIn("fundamentalMode: fundamentalModeMenu.value", SOURCE)
        self.assertIn("preset[\\fundamentalMode] ? 0", SOURCE)


if __name__ == "__main__":
    unittest.main()
