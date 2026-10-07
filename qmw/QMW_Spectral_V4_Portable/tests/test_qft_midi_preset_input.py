from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v3.scd"
).read_text(encoding="utf-8")


class QFTMIDIPresetInputTests(unittest.TestCase):
    def test_c0_starts_the_chromatic_32_preset_range(self):
        self.assertIn("~qmwQFTMIDIPresetBaseNote ? 12", SOURCE)
        self.assertIn(
            "slot.inclusivelyBetween(0, presetSlotCount - 1)", SOURCE
        )
        self.assertIn("presetSlotCount = 32", SOURCE)

    def test_dropdown_filters_note_on_to_selected_source(self):
        self.assertIn('"MIDI INPUT — PRESET RECALL"', SOURCE)
        self.assertIn("midiInputMenu = PopUpMenu", SOURCE)
        self.assertIn(
            "}, nil, nil, selectedSource.uid);",
            SOURCE,
        )

    def test_akai_mpk_is_preferred_and_hotplug_can_refresh(self):
        self.assertIn('.toLower.contains("mpk")', SOURCE)
        self.assertIn('states_([["refresh MIDI"]])', SOURCE)
        self.assertIn("refreshMIDIInputs.()", SOURCE)

    def test_later_menu_modes_do_not_overflow_legacy_voice_gains(self):
        self.assertIn(
            "if(savedVoiceMode < 4, { savedVoiceMode }, { 1 })",
            SOURCE,
        )


if __name__ == "__main__":
    unittest.main()
