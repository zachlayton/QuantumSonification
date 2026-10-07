from __future__ import annotations

from pathlib import Path
import unittest


class SpectralV4SuperColliderBridgeTests(unittest.TestCase):
    def test_v3_fx_bridge_is_explicit_opt_in_and_16_mode_ready(self) -> None:
        path = (
            Path(__file__).resolve().parents[1]
            / "supercollider"
            / "qmw_spectral_v4_v3_fx_bridge.scd"
        )
        source = path.read_text(encoding="utf-8")
        self.assertIn("~qriFXSendBus.isNil", source)
        self.assertIn("Array.fill(16", source)
        self.assertIn("'/qmw/v4/spectral/frame'", source)
        self.assertIn("recvPort: 7404", source)
        self.assertIn("~qmwV4SpectralDryLevel = 0.0", source)
        self.assertIn("~qmwV4SpectralSetMix", source)
        self.assertIn("~qmwV4SpectralPerformance", source)
        self.assertIn("~qmwV4SpectralApplyAudioGate", source)
        self.assertIn("voice.run(monitorRunning)", source)
        self.assertIn("~qmsvEnabled = true", source)
        self.assertIn("~qmsvHilbertFollow = false", source)
        self.assertIn("~qmgInfluence = 1.0", source)
        self.assertIn("~qmgDensityPositionFollow = true", source)
        self.assertIn('NetAddr("127.0.0.1", 17888)', source)
        self.assertIn('"/qmw/4_4/dynamics/control/"', source)
        self.assertIn("V4 FOUR-QUBIT PHYSICAL EVOLUTION", source)
        self.assertIn("not the Hilbert event clock", source)
        self.assertIn("RHO POSITION + ROTATION FOLLOW", source)
        self.assertIn("{ ~qmwV4SpectralOpenControls.value }.defer", source)
        self.assertNotIn("\\qmwV4SpectralPopulationEvent", source)

    def test_bridge_keeps_v3_fx_return_as_a_downstream_adapter(self) -> None:
        path = (
            Path(__file__).resolve().parents[1]
            / "supercollider"
            / "qmw_spectral_v4_v3_fx_bridge.scd"
        )
        source = path.read_text(encoding="utf-8")
        self.assertIn("Out.ar(fxBus, stereo * Lag.kr(fxSend.clip(0, 1), 0.08))", source)
        self.assertIn("stateMotion", source)
        self.assertIn("purity = (message[4]", source)
        self.assertIn("entropy = (message[5]", source)
        self.assertIn("participationRank = (message[6]", source)
        self.assertIn("commutatorNorm = (message[7]", source)
        self.assertIn("var offset = 8 + (index * 2)", source)
        self.assertIn("purity %   entropy % nats   participation %", source)
        self.assertIn("does not synthesize a pulse for every analysis frame", source)
        self.assertIn("Pitch belongs to the canonical Wilson/dodecahedral", source)
        self.assertIn("~qmgFrame[\\frequencies]", source)
        self.assertIn("V4 4Q PHYSICAL  |  purity %  entropy %  motion %", source)
        self.assertIn("All audio follows QRM's visible SOUND LOCKED", source)
        self.assertIn("Group.before(~qriFXGroup)", source)

    def test_launcher_composes_external_v3_without_restoring_it(self) -> None:
        root = Path(__file__).resolve().parents[1]
        launcher = root / "qmw" / "qft" / "StartQMWUnifiedInstrumentResonatorV4.command"
        bootstrap = root / "supercollider" / "qmw_spectral_v4_v3_bootstrap.scd"
        launcher_source = launcher.read_text(encoding="utf-8")
        bootstrap_source = bootstrap.read_text(encoding="utf-8")
        self.assertIn('DEFAULT_V3_ROOT="$REPO_ROOT/worktrees/qmw-v3-runtime"', launcher_source)
        self.assertIn('V3_ROOT="${QMW_V3_ROOT:-$DEFAULT_V3_ROOT}"', launcher_source)
        self.assertIn("QMW_V3_SC_FILE", launcher_source)
        self.assertIn("QMW_V4_SPECTRAL_BRIDGE_FILE", launcher_source)
        self.assertIn('QMW_PLUCK_THRESHOLD="${QMW_PLUCK_THRESHOLD:-0.005}"', launcher_source)
        self.assertIn("no stashed work has been restored automatically", launcher_source)
        self.assertIn("thisProcess.interpreter.executeFile(v3File)", bootstrap_source)
        self.assertIn("~qriFXSendBus.notNil", bootstrap_source)
        self.assertIn('"QMW_V3_SC_FILE".getenv', bootstrap_source)
        self.assertNotIn("Platform.getenv", bootstrap_source)


if __name__ == "__main__":
    unittest.main()
