from pathlib import Path
import unittest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "supercollider"
    / "QuantumResonantMembraneV1.scd"
).read_text(encoding="utf-8")
ADDON = (
    Path(__file__).resolve().parents[1]
    / "supercollider"
    / "QMWInterferenceTimbreAddonV1.scd"
).read_text(encoding="utf-8")


class SuperColliderControlTests(unittest.TestCase):
    def test_interference_timbre_is_revision_matched_and_audio_rate_smoothed(self) -> None:
        self.assertIn("~qrmInterferenceTimbreGains", SOURCE)
        self.assertIn("~qrmStageInterferenceTimbreGains", SOURCE)
        self.assertIn("/timbre/interference", SOURCE)
        self.assertIn("/timbre/gain_factors", SOURCE)
        self.assertIn("revision == ~qrmStageRevision", SOURCE)
        self.assertIn("\\interferenceTimbreGains, Array.fill(modeCount, 1.0)", SOURCE)
        self.assertGreaterEqual(SOURCE.count("Lag.kr(interferenceTimbreGains[index]"), 6)
        self.assertIn("\\interferenceTimbreSlew", SOURCE)
        self.assertIn("* timbreGain", SOURCE)

    def test_interference_addon_exposes_phase_spread_depth_source_and_pair(self) -> None:
        self.assertIn("QMW INTERFERENCE TIMBRE", ADDON)
        self.assertIn("~qrmOpenInterferenceTimbre = {", ADDON)
        self.assertIn("QMWInterferenceTimbreAddonV1.scd", SOURCE)
        self.assertIn('states_([["PHASE TIMBRE"]])', SOURCE)
        self.assertIn('root ++ "/control/interference_phase"', ADDON)
        self.assertIn('root ++ "/control/interference_spread"', ADDON)
        self.assertIn('root ++ "/control/interference_depth"', ADDON)
        self.assertIn('root ++ "/control/interference_slew"', ADDON)
        self.assertIn('root ++ "/control/interference_source"', ADDON)
        self.assertIn('root ++ "/control/interference_pair"', ADDON)
        self.assertIn("MultiSliderView", ADDON)
        self.assertIn("M1-M20", ADDON)
    def test_numeric_fields_have_contrasting_normal_and_typing_colors(self) -> None:
        self.assertGreaterEqual(SOURCE.count("numberView.normalColor = Color.white"), 3)
        self.assertGreaterEqual(SOURCE.count("numberView.typingColor = Color.white"), 3)
        self.assertGreaterEqual(
            SOURCE.count('numberView.background = Color.fromHexString("080b10")'),
            3,
        )

    def test_native_and_derived_banks_are_distinct(self) -> None:
        self.assertIn("var modeCount = 20", SOURCE)
        self.assertIn("var harmonicCount = 16", SOURCE)
        self.assertIn("20 INDEPENDENT MODE VOLUMES", SOURCE)
        self.assertIn("DERIVED HARMONIC MONITOR", SOURCE)
        self.assertIn("~qrmModeAudioWeights", SOURCE)
        self.assertIn("~qrmHarmonicAudioWeights", SOURCE)
        self.assertIn("isolate M", SOURCE)
        self.assertIn("isolate H", SOURCE)

    def test_each_native_mode_has_an_independent_upstream_volume(self) -> None:
        self.assertIn("20 INDEPENDENT MODE VOLUMES", SOURCE)
        self.assertIn("~qrmSetModeGain = { |index, gain|", SOURCE)
        self.assertIn("~qrmModeGains[lane] = gain.clip(0, 2)", SOURCE)
        self.assertIn("var changedLane = difference.maxIndex", SOURCE)
        self.assertIn("~qrmSetModeGain.(changedLane, requested[changedLane])", SOURCE)
        self.assertIn("~qrmPushModeMix", SOURCE)
        self.assertIn("* nativeWeights.copyRange(0, harmonicCount - 1)", SOURCE)
        self.assertNotIn("~qrmModeGains = view.value.collect", SOURCE)
        self.assertIn("/mixer/mode_gain", SOURCE)
        self.assertIn("/mixer/mode_gains", SOURCE)
        self.assertIn("~qrmSetModeCombination", SOURCE)
        self.assertIn("expected 20 gains", SOURCE)

    def test_v42_style_wavefield_uses_raw_modes_and_velocity_envelope(self) -> None:
        self.assertIn("3D MODAL WAVEFIELD", SOURCE)
        self.assertIn("/membrane/raw_modes", SOURCE)
        self.assertIn("/membrane/velocities", SOURCE)
        self.assertIn("/density/rho_real", SOURCE)
        self.assertIn("/density/rho_imag", SOURCE)
        self.assertIn("rho  |.| / phase", SOURCE)
        self.assertIn("~qrmWaveHistory", SOURCE)
        self.assertIn("raw motion + velocity envelope", SOURCE)
        self.assertIn("Color(0.98, 0.16, 0.72", SOURCE)
        self.assertIn("Color(0.08, 0.82, 1.0", SOURCE)
        self.assertIn("Color(0.18, 0.95, 0.52", SOURCE)
        self.assertIn("layer * height * 0.20", SOURCE)

    def test_temporal_audio_controls_are_not_physical_controls(self) -> None:
        self.assertIn("TIME ENGINE + TEMPORAL SOUND ADAPTER", SOURCE)
        self.assertIn('"body s"', SOURCE)
        self.assertIn('"event decay"', SOURCE)
        self.assertIn("decay.clip(0.02, 4.0)", SOURCE)
        self.assertIn("72, 42, \\exp", SOURCE)
        for name in (
            "Event Threshold (live)",
            "Quantum / Bures",
            "Fixed",
            "Euclidean",
            "Q-Euclidean",
            "Q-Geodesic",
            "Q-Recursive",
        ):
            self.assertIn(f'"{name}"', SOURCE)
        self.assertIn("~qrmRouteCrossing", SOURCE)
        self.assertIn("~qrmRouteBuresPulse", SOURCE)
        self.assertIn("/temporal/global", SOURCE)
        self.assertIn('"Bures d/p"', SOURCE)
        self.assertIn('"sched x"', SOURCE)
        self.assertIn('"SCHEDULER / RECORD SCALE"', SOURCE)
        self.assertIn("/control/clock_scale", SOURCE)
        self.assertIn("/control/event_threshold", SOURCE)
        self.assertIn("EVENT FLUX THRESHOLD", SOURCE)
        self.assertIn("fill %%%", SOURCE)
        self.assertIn("~qrmTimeClock", SOURCE)
        self.assertIn("PHYSICAL DENSITY-ENGINE CONTROLS", SOURCE)
        self.assertIn("/control/freeze", SOURCE)
        self.assertIn("/control/drive", SOURCE)

    def test_field_and_event_buses_are_observed_separately(self) -> None:
        self.assertIn("/field/global", SOURCE)
        self.assertIn("/field/frequency_offsets", SOURCE)
        self.assertIn("/field/susceptibility", SOURCE)
        self.assertIn("/event/global", SOURCE)
        self.assertIn("FIELD dw", SOURCE)
        self.assertIn("EVENT +%  dP", SOURCE)
        self.assertIn("Ringz.ar", SOURCE)
        self.assertIn("Impulse.ar(0)", SOURCE)
        self.assertIn("future filtered-noise/LPG voice", SOURCE)

    def test_named_density_preparations_are_visible_and_backend_owned(self) -> None:
        for name in ("localized", "coherent", "squeezed", "thermal", "vacuum"):
            self.assertIn(f'"{name}"', SOURCE)
        self.assertIn("~qrmPreparationMenu", SOURCE)
        self.assertIn("/control/state", SOURCE)
        self.assertIn("/density/preparation", SOURCE)
        self.assertIn("~qrmPreparationSemantics", SOURCE)

    def test_continuous_body_is_a_spatial_mode_pulse_field(self) -> None:
        self.assertIn("~qrmPulseRates", SOURCE)
        self.assertIn("\\pulseRates", SOURCE)
        self.assertIn("pulseExcitations", SOURCE)
        self.assertIn("Impulse.ar", SOURCE)
        self.assertIn("var pulseEnvelope = EnvGen.ar", SOURCE)
        self.assertIn("[0, 1, 0.42, 0]", SOURCE)
        self.assertIn("pulseAttack.clip(0.001, 0.25)", SOURCE)
        self.assertIn("pulseRelease.clip(0.05, 6.0)", SOURCE)
        self.assertIn('"pulse mix"', SOURCE)
        self.assertIn("~qrmPulseDepth = 0.8", SOURCE)
        self.assertIn('"volume"', SOURCE)
        self.assertIn('"attack"', SOURCE)
        self.assertIn('"decay"', SOURCE)
        self.assertIn('"release"', SOURCE)
        self.assertIn("\\pulseLevel, ~qrmPulseLevel", SOURCE)
        self.assertIn("\\pulseAttack, ~qrmPulseAttack", SOURCE)
        self.assertIn("\\pulseDecay, ~qrmPulseDecay", SOURCE)
        self.assertIn("\\pulseRelease, ~qrmPulseRelease", SOURCE)
        self.assertIn("pulseDecay * pulseDecayScales[index]", SOURCE)
        self.assertNotIn("pulseDecay + pulseRelease", SOURCE)
        self.assertIn("var resonant = Ringz.ar", SOURCE)
        self.assertIn("XFade2.ar", SOURCE)
        self.assertIn("sustained * amplitude", SOURCE)
        self.assertNotIn("amplitude * XFade2.ar", SOURCE)
        self.assertIn("PinkNoise.ar(0.34)", SOURCE)
        self.assertIn("pulseActivities[index].clip(0, 1).sqrt", SOURCE)
        self.assertNotIn("0.08 + (0.92 * pulseActivities", SOURCE)
        self.assertIn("~qrmCrossingAudioEnabled = ~qrmCrossingAudioEnabled ? true", SOURCE)
        self.assertIn("(~qrmCrossingAudioEnabled ? true) and: { ~qrmSonify }", SOURCE)
        self.assertIn("~qrmPulseAttack = 0.012", SOURCE)
        self.assertIn("~qrmPulseDecay = 0.28", SOURCE)
        self.assertIn("~qrmPulseRelease = 0.9", SOURCE)
        self.assertIn("qrmModalPulseAuditionV1", SOURCE)
        self.assertIn("~qrmAuditionModalPulse", SOURCE)
        self.assertIn("AUDITION PULSE + ADAPTERS", SOURCE)
        self.assertIn("\\dynamicDetunes, ~qrmPulseDetunes", SOURCE)
        self.assertIn("\\pulseActivities", SOURCE)
        self.assertIn("\\pulseBrightness", SOURCE)
        self.assertIn("\\pulseDetunes", SOURCE)
        self.assertIn("\\pulseDrives", SOURCE)
        self.assertIn("Absolute activity is intentionally not normalized", SOURCE)
        self.assertNotIn("~qrmRawModes[index].abs / modePeak", SOURCE)
        self.assertIn("Splay.ar(signals", SOURCE)

    def test_v42_dynamic_event_adapters_are_restored(self) -> None:
        self.assertIn("~qrmEffectiveCrossingDecay", SOURCE)
        self.assertIn('"field depth"', SOURCE)
        self.assertIn('"momentum"', SOURCE)
        self.assertIn('"E→decay"', SOURCE)
        self.assertIn("~qrmUpdateDynamicAdapters", SOURCE)
        self.assertIn("pulseFrequency", SOURCE)
        self.assertIn("var coloredBands = Ringz.ar", SOURCE)
        self.assertIn("persistence.clip(1, 64)", SOURCE)
        self.assertIn("\\coherence, (~qrmCoherence / 3).clip(0, 1)", SOURCE)

    def test_v42_pitch_maps_are_restored_without_changing_mode_gains(self) -> None:
        for name in (
            "physical", "harmonics 1-16", "odd harmonics", "geometric tuning"
        ):
            self.assertIn(f'"{name}"', SOURCE)
        self.assertIn("~qrmUpdatePitchRatios", SOURCE)
        self.assertIn("(index % 16) + 1.0", SOURCE)
        self.assertIn("(2 * (index % 16)) + 1.0", SOURCE)
        self.assertIn("audio mapping; M1-M20 remain independent", SOURCE)
        for family in (
            "n-EDO", "Wilson", "Tenney", "La Monte Young", "Scala dictionary"
        ):
            self.assertIn(f'"{family}"', SOURCE)
        self.assertIn("~qrmParseScalaFile", SOURCE)
        self.assertIn("~qrmOpenTuning", SOURCE)
        self.assertIn("FILTER DICTIONARY", SOURCE)
        self.assertIn("scala_archive/scl", SOURCE)

    def test_reset_is_sonically_transactional_and_polyphony_is_bounded(self) -> None:
        self.assertIn("~qrmSonicReset", SOURCE)
        self.assertIn("~qrmSonicGeneration", SOURCE)
        self.assertIn("~qrmSonicGateUntil", SOURCE)
        self.assertIn("~qrmStrikeGroup !? _.freeAll", SOURCE)
        self.assertIn("~qrmMaxStrikeVoices = 16", SOURCE)
        self.assertIn("~qrmMaxCrossingsPerFrame = 6", SOURCE)
        self.assertIn("resetFrame.not", SOURCE)

    def test_core_audio_menu_and_real_multichannel_graphs_are_present(self) -> None:
        self.assertIn("s.options.numWireBufs.max(2048)", SOURCE)
        self.assertIn("AUDIO ROUTING 2/8/16", SOURCE)
        self.assertIn("ServerOptions.outDevices", SOURCE)
        self.assertIn("~qrmRefreshAudioDevices", SOURCE)
        self.assertIn("menu.value.notNil", SOURCE)
        self.assertIn("~qrmAudioDeviceMenu.value ? 0", SOURCE)
        self.assertIn("~qrmOutputLayoutMenu.value ? 0", SOURCE)
        self.assertIn("~qrmApplyAudioOutput", SOURCE)
        self.assertIn("s.options.outDevice = selectedDevice", SOURCE)
        self.assertIn("s.options.numOutputBusChannels = outputChannels", SOURCE)
        self.assertIn("s.reboot(configureAndReload", SOURCE)
        self.assertIn("Ableton bridge", SOURCE)
        self.assertIn("blackhole", SOURCE.lower())
        self.assertIn("BlackHole 2ch cannot carry % discrete buses", SOURCE)
        self.assertIn("if(selectedDevice.isNil, { nil }", SOURCE)

        self.assertIn("SynthDef(\\qrmMembraneBody8V1", SOURCE)
        self.assertIn("SynthDef(\\qrmBoundaryStrike8V1", SOURCE)
        self.assertIn("SynthDef(\\qrmMembraneBody16V1", SOURCE)
        self.assertIn("SynthDef(\\qrmBoundaryStrike16V1", SOURCE)
        self.assertIn("PanAz.ar(8, signals[index]", SOURCE)
        self.assertIn("PanAz.ar(16, signals[index]", SOURCE)
        self.assertIn("16 TRANSDUCERS", SOURCE)
        self.assertIn("Mix.fill(modeCount", SOURCE)
        self.assertIn("Limiter expands per channel", SOURCE)
        self.assertIn("\\qrmMembraneBody8V1", SOURCE)
        self.assertIn("\\qrmBoundaryStrike8V1", SOURCE)
        self.assertIn("contact[1].atan2(contact[0]) / pi", SOURCE)

    def test_audio_reboot_preserves_backend_and_relocks_sound(self) -> None:
        self.assertIn("backend state remains live", SOURCE)
        self.assertIn("~qrmSonify = false", SOURCE)
        self.assertIn("~qrmSoundButton !? { |button| button.value_(0) }", SOURCE)
        self.assertIn("s.doWhenBooted({ ~qrmBuildAudio.value })", SOURCE)
        self.assertIn("s.makeBundle(nil", SOURCE)
        self.assertNotIn("s.bind({", SOURCE)
        self.assertIn("Applying routing locks sound but does not reset rho", SOURCE)

    def test_v42_performance_fx_are_restored_with_exact_bypass(self) -> None:
        self.assertIn("TIME + FX + PRESETS", SOURCE)
        self.assertIn("base Hz × H1…H16", SOURCE)
        self.assertIn("ringHarmonic.round.clip(1, 16)", SOURCE)
        self.assertIn("dry * SinOsc.ar(ringFrequency) * 2.sqrt", SOURCE)
        self.assertIn("Fuzz Face-inspired two-stage transfer", SOURCE)
        self.assertIn("var firstStage", SOURCE)
        self.assertIn("var secondStage", SOURCE)
        self.assertIn("var asymmetric", SOURCE)
        self.assertIn("fuzzTone.clip(800, 12000)", SOURCE)
        self.assertIn("Fuzz blend 0 is exact bypass", SOURCE)

    def test_performance_presets_are_32_slot_and_do_not_capture_rho(self) -> None:
        self.assertIn("~qrmPresetSlotCount = 32", SOURCE)
        self.assertIn("~qrmCapturePerformancePreset", SOURCE)
        self.assertIn("~qrmRecallPerformancePreset", SOURCE)
        self.assertIn("MIDI C0-G2 recalls", SOURCE)
        self.assertIn("MIDIFunc.noteOn", SOURCE)
        self.assertIn("qrm_v1_performance_slots.archive", SOURCE)
        self.assertIn("~qrmPerformanceBuresSlider !?", SOURCE)
        self.assertIn("~qrmPerformanceClockSlider !?", SOURCE)
        self.assertIn("~qrmPerformanceWindow === performanceWindow", SOURCE)
        capture = SOURCE.split("~qrmCapturePerformancePreset = {", 1)[1].split(
            "~qrmRecallPerformancePreset = {", 1
        )[0]
        self.assertNotIn("rho", capture.lower())
        self.assertNotIn("outDevice", capture)
        self.assertIn("eventThreshold", capture)
        self.assertIn("pulseLevel", capture)
        self.assertIn("pulseDecay", capture)
        self.assertIn("energyDecayAmount", capture)
        self.assertIn("fieldTimbreDepth", capture)
        self.assertIn("momentumTimbreDepth", capture)
        self.assertIn("pitchMode", capture)
        self.assertIn("tuningFamily", capture)
        self.assertIn("tuningDegreeOffset", capture)
        self.assertIn("scalaFile", capture)


if __name__ == "__main__":
    unittest.main()
