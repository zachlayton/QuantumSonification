from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v3.scd"
).read_text(encoding="utf-8")
V42_WRAPPER = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v4_2.scd"
).read_text(encoding="utf-8")


class QFTFieldRendererModeTests(unittest.TestCase):
    def test_renderer_menu_exposes_field_plucks_and_hybrid(self):
        self.assertIn('items_(["Field", "Plucks", "Hybrid"])', SOURCE)
        self.assertIn("~qmwQFTV3RendererMode = menu.value", SOURCE)
        self.assertIn("synth.set(\\fieldLevel, fieldLevel)", SOURCE)
        self.assertIn("synth.set(\\pulseLevel, pulseLevel)", SOURCE)

    def test_continuous_voice_uses_committed_phi_pi_projection(self):
        self.assertIn("\\fieldAmplitudes", SOURCE)
        self.assertIn("\\fieldPhases", SOURCE)
        self.assertIn("\\fieldDrives", SOURCE)
        self.assertIn(
            "~qmwQFTV3Pi[site].atan2(~qmwQFTV3Phi[site])", SOURCE
        )
        self.assertIn("var fieldVoice = Mix.fill(siteCount", SOURCE)
        self.assertIn("var signal = fieldVoice + vacuumVoice", SOURCE)

    def test_field_voice_obeys_pitch_and_stereo_adapters(self):
        self.assertIn("fundamental * sitePitchRatios[site]", SOURCE)
        self.assertIn(
            "(((site % 2) * 2) - 1) * fieldStereoWidth", SOURCE
        )

    def test_field_mix_and_mode_round_trip_through_presets(self):
        self.assertIn("rendererMode: rendererModeMenu.value", SOURCE)
        self.assertIn("fieldMix: fieldMixSlider.value", SOURCE)
        self.assertIn("preset[\\rendererMode] ? 2", SOURCE)
        self.assertIn("preset[\\fieldMix] ? 0.20", SOURCE)

    def test_field_has_an_independent_sixteen_component_mixer(self):
        self.assertIn("FIELD SPECTRAL MIXER — CONTINUOUS FIELD ONLY", SOURCE)
        self.assertIn("~qmwQFTV3FieldLaneGains = Array.fill", SOURCE)
        self.assertIn("~qmwQFTV3FieldLaneMutes = Array.fill", SOURCE)
        self.assertIn("\\fieldLaneGains", SOURCE)
        self.assertIn("* fieldLaneGains[site]", SOURCE)
        self.assertIn("fieldLaneGains: ~qmwQFTV3FieldLaneGains.copy", SOURCE)
        self.assertIn("fieldLaneMutes: ~qmwQFTV3FieldLaneMutes.copy", SOURCE)
        self.assertIn(
            "pluck lane gains remain independent", SOURCE
        )

    def test_field_only_mode_does_not_allocate_new_plucks(self):
        self.assertGreaterEqual(
            SOURCE.count("and: { ~qmwQFTV3RendererMode > 0 }"), 2
        )

    def test_v42_routes_plucks_and_field_to_separate_stereo_pairs(self):
        self.assertIn("~qmwQFTSplitFieldOutput = true", V42_WRAPPER)
        self.assertIn("numOutputBusChannels.max(4)", V42_WRAPPER)
        self.assertIn("~qmwQFTV3FieldBus = if(splitFieldOutput", SOURCE)
        self.assertIn("\\out, ~qmwQFTV3FieldBus", SOURCE)
        self.assertIn("[\\inBus, ~qmwQFTV3SourceBus, \\out, 0]", SOURCE)
        self.assertIn("[\\inBus, ~qmwQFTV3FieldBus, \\out, 2]", SOURCE)
        self.assertIn("plucks 1–2, field 3–4", SOURCE)
        self.assertIn("if(splitFieldOutput, { 4 }, { 2 })", SOURCE)


if __name__ == "__main__":
    unittest.main()
