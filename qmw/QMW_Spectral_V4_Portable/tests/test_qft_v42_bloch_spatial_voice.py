from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
ADDON = (
    ROOT / "supercollider" / "qmw_bloch_harmonics_spatial_v4_2.scd"
).read_text(encoding="utf-8")
MIXER = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v3.scd"
).read_text(encoding="utf-8")
WRAPPER = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v4_2.scd"
).read_text(encoding="utf-8")
LAUNCHER = (
    ROOT / "qmw" / "qft" / "StartQMWQFTV4_2.command"
).read_text(encoding="utf-8")
GEN_DSP_PATH = (
    REPOSITORY
    / "BLOCH_HARMONICS"
    / "bloch_harmonics_four_qubit_spat_v8"
    / "qmw_qubit_resonator.gendsp"
)


def _genexpr_code() -> str:
    patch = json.loads(GEN_DSP_PATH.read_text(encoding="utf-8"))
    for wrapped in patch["patcher"]["boxes"]:
        box = wrapped["box"]
        if box.get("maxclass") == "codebox":
            return str(box["code"])
    raise AssertionError("v8 GenDSP source has no codebox")


class QFTV42BlochSpatialVoiceTests(unittest.TestCase):
    def test_authoritative_local_v8_source_is_present(self) -> None:
        code = _genexpr_code()
        self.assertIn("shape = mix(0.65,1.45,pur);", code)
        self.assertIn("tilt = clamp(0.90-0.75*coh+0.25*ent,0.05,1);", code)
        self.assertIn("out1 = tanh(s*0.42)*amp*(0.35+0.65*r);", code)

    def test_v42_adds_only_one_fifth_mixer_lane(self) -> None:
        self.assertIn("~qmwQFTV42BlochVoiceEnabled = true", WRAPPER)
        self.assertIn("qmw_bloch_harmonics_spatial_v4_2.scd", WRAPPER)
        self.assertIn("var voiceCount = if(blochVoiceEnabled, { 5 }, { 4 })", MIXER)
        self.assertIn(
            "(~qmwQFTV42BlochVoiceEnabled ? false).asBoolean", MIXER
        )
        self.assertNotIn(
            '["4.2", "4.2b"].includes(displayVersion)', MIXER
        )
        self.assertIn("~qmwQFTV3BlochVoiceEnabled = blochVoiceEnabled", MIXER)
        self.assertIn("Bus.control(s, voiceCount)", MIXER)
        self.assertIn('++ if(blochVoiceEnabled, { ["Bloch"] }, { [] })', MIXER)
        self.assertIn('"%-VOICE MIXER — LIVE GAIN".format(voiceCount)', MIXER)
        self.assertIn('% audio voices (Bloch %)', MIXER)
        self.assertIn("~qmwQFTV42BlochVoiceOnline = true", ADDON)
        self.assertIn("Bloch audio online: mixer lane 5", ADDON)

    def test_fifth_lane_defaults_to_exact_bypass(self) -> None:
        self.assertIn("if(voice == 1, { 1.0 }, { 0.0 })", MIXER)
        self.assertIn("~qmwQFTV3VoiceGainBus.index + 4", ADDON)
        self.assertIn("var fifthVoiceGain = In.kr(voiceGainBus, 1)", ADDON)
        self.assertIn("* fifthVoiceGain", ADDON)

    def test_bloch_lane_alone_has_six_db_more_fader_headroom(self) -> None:
        self.assertIn("~qmwQFTV3VoiceGainCeilings = Array.fill", MIXER)
        self.assertIn(
            "if(blochVoiceEnabled and: { voice == 4 }, { 4.0 }, { 2.0 })",
            MIXER,
        )
        self.assertIn("~qmwQFTV3VoiceGainSliderValues", MIXER)
        self.assertIn("~qmwQFTV3VoiceGainCeilings[voice]", MIXER)
        self.assertIn("In.kr(voiceGainBus, 1).clip(0, 4)", ADDON)

    def test_genexpr_equation_is_native_and_persistent(self) -> None:
        self.assertIn("SynthDef(\\qmwQFTV42BlochSpatialVoice", ADDON)
        self.assertIn("var sources = Array.fill(4", ADDON)
        self.assertIn("partials = Mix.fill(8", ADDON)
        self.assertIn("(value.abs + 0.0001).pow(shape)", ADDON)
        self.assertIn("phaseSigns[index] * pi", ADDON)
        self.assertIn("(partials * 0.42).tanh", ADDON)
        self.assertIn("* (0.35 + (0.65 * radius))", ADDON)
        self.assertNotIn("Ringz.ar", ADDON)
        self.assertNotIn("Impulse.ar", ADDON)

    def test_local_v8_defaults_and_global_descriptors_are_preserved(self) -> None:
        self.assertIn("[55.0, 110.0, 220.0, 275.0]", ADDON)
        self.assertIn("~qmwQFTV42BlochLocalAmplitude = 0.12", ADDON)
        self.assertIn("purity.linlin(0, 1, 0.65, 1.45)", ADDON)
        self.assertIn("0.90 - (0.75 * coherence) + (0.25 * entropy)", ADDON)
        self.assertIn("msg[1].asFloat / 15", ADDON)
        self.assertIn("msg[1].asFloat / 4", ADDON)

    def test_state_updates_have_adjustable_continuous_interpolation(self) -> None:
        self.assertIn("~qmwQFTV42BlochInterpolationSeconds = 0.35", ADDON)
        self.assertIn("interpolationSeconds=0.35", ADDON)
        self.assertIn("sx = Lag.kr(xs[qubit], glide)", ADDON)
        self.assertIn("sy = Lag.kr(ys[qubit], glide)", ADDON)
        self.assertIn("sz = Lag.kr(zs[qubit] - 1, glide) + 1", ADDON)
        self.assertIn('"state glide s"', ADDON)

    def test_pitch_sources_do_not_claim_pitch_from_density_alone(self) -> None:
        self.assertIn("~qmwQFTV42BlochPitchMode = 0", ADDON)
        self.assertIn('"pitch: manual q0–q3 bases"', ADDON)
        self.assertIn('"pitch: user ratio × fundamental"', ADDON)
        self.assertIn('"pitch: Hamiltonian gap ratios"', ADDON)
        self.assertIn(
            "~qmwQFTV42BlochUserRatios = (~qmwQFTV42BlochUserRatios", ADDON
        )
        self.assertIn("? [1.0, 2.0, 4.0, 5.0]", ADDON)
        self.assertIn("text.asString.split($:)", ADDON)
        self.assertIn("tokens.size != 4", ADDON)
        self.assertIn("value < 0.01 or: { value > 64 }", ADDON)
        self.assertIn("(~qmwQFTV3Fundamental ? 55.0) * ratio", ADDON)
        self.assertIn("~qmwQFTV42BlochApplyRatioText", ADDON)
        self.assertIn("1:2:4:5 or 2:5:7:11", ADDON)
        self.assertIn('"/qmw/density_field/harmonics"', ADDON)
        self.assertIn("~qmwQFTV42BlochHamiltonianRatios", ADDON)
        self.assertIn("Array.fill(4, { 1.0 })", ADDON)
        self.assertIn("~qmwQFTV3Fundamental", ADDON)
        self.assertIn("~qmwQFTV42BlochPushAudio", MIXER)

    def test_spatial_fold_down_keeps_v8_control_equations(self) -> None:
        self.assertIn("distance = 1 + (1.5 * (1 - radius))", ADDON)
        self.assertIn("aperture = 20 + (140 * (1 - radius))", ADDON)
        self.assertIn("sy / horizontalRadius.max(0.000001)", ADDON)
        self.assertIn("Pan2.ar", ADDON)

    def test_osc_is_a_read_only_full_engine_mirror(self) -> None:
        for qubit in range(4):
            self.assertIn('"/qmw/qubit/%/bloch".format(qubit)', ADDON)
        self.assertIn('"/qmw/density/purity"', ADDON)
        self.assertIn('"/qmw/density/coherence_l1"', ADDON)
        self.assertIn('"/qmw/density/von_neumann_entropy"', ADDON)
        self.assertIn("recvPort: blochPort", ADDON)
        self.assertIn("never evolves, reduces or writes back to rho", ADDON)

    def test_voice_joins_main_voice_pair_and_obeys_global_sound_gate(self) -> None:
        self.assertIn("\\out, ~qmwQFTV3SourceBus", ADDON)
        self.assertNotIn("\\out, ~qmwQFTV3FieldBus", ADDON)
        self.assertIn("~qmwQFTV3SoundEnabled", ADDON)
        self.assertIn("\\rendererGate, rendererGate", ADDON)
        self.assertIn("plucks + Bloch voice:        outputs 1-2", LAUNCHER)
        self.assertIn("field + overtone:            outputs 3-4", LAUNCHER)

    def test_launcher_manages_full_engine_and_configurable_mirror(self) -> None:
        self.assertIn('BLOCH_SC_PORT="${QMW_BLOCH_SC_PORT:-17832}"', LAUNCHER)
        self.assertIn('7402 17830 17831 17860 17861 17863 "$BLOCH_SC_PORT"', LAUNCHER)
        self.assertIn('ENGINE_SCRIPT="$SUPPORT_ROOT/quantumsonification_engine.py"', LAUNCHER)
        self.assertIn('--implementation=resonator_v9', LAUNCHER)
        self.assertIn('--osc-profile=full', LAUNCHER)
        self.assertIn('BLOCH_RATE_HZ="${QMW_BLOCH_RATE_HZ:-20}"', LAUNCHER)
        self.assertIn('--diagnostics-hz "$BLOCH_RATE_HZ"', LAUNCHER)
        self.assertIn('--sc-osc-port "$BLOCH_SC_PORT"', LAUNCHER)
        self.assertIn('ENGINE_PID=$!', LAUNCHER)
        self.assertIn('NUMBA_CACHE_DIR="$NUMBA_CACHE_ROOT"', LAUNCHER)
        self.assertIn('for PID in "$ENGINE_PID" "$QHO_PID" "$FIELD_PID"', LAUNCHER)
        self.assertNotIn(
            'quantumsonification_conductor.py --supercollider-port', LAUNCHER
        )

    def test_panel_describes_the_managed_single_command_source(self) -> None:
        self.assertIn("V4.2 launcher manages the canonical", ADDON)
        self.assertNotIn("Start the canonical conductor", ADDON)


if __name__ == "__main__":
    unittest.main()
