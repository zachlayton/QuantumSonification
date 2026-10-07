from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADDON = (
    ROOT / "supercollider" / "qmw_qho_parseval_v4_2.scd"
).read_text(encoding="utf-8")
WRAPPER = (
    ROOT / "supercollider" / "qmw_scalar_field_observer_v4_2.scd"
).read_text(encoding="utf-8")
LAUNCHER = (
    ROOT / "qmw" / "qft" / "StartQMWQFTV4_2.command"
).read_text(encoding="utf-8")
FLOW_SOURCE = (
    ROOT / "qmw" / "qft" / "live_flow_osc_v4_2.py"
).read_text(encoding="utf-8")
PERFORMANCE_SOURCE = (
    ROOT / "qmw" / "qft" / "performance.py"
).read_text(encoding="utf-8")


class QFTV42ParsevalOvertoneBankTests(unittest.TestCase):
    def test_v42_loads_the_parseval_lane_adapter(self) -> None:
        self.assertIn('qmw_qho_parseval_v4_2.scd', WRAPPER)
        self.assertIn('qmw.qho.osc.v1.2', ADDON)
        self.assertIn('recvPort: qhoPort', ADDON)

    def test_bank_is_persistent_and_has_one_voice_per_overtone(self) -> None:
        self.assertIn('SynthDef(\\qmwQFTV42ParsevalOvertoneBank', ADDON)
        self.assertIn('var voices = Mix.fill(16', ADDON)
        self.assertIn('frequencies[index]', ADDON)
        self.assertIn('amplitudes[index] * laneGains[index]', ADDON)
        self.assertIn('~qmwQFTV3SitePitchRatios', ADDON)
        self.assertIn('~qmwQFTV3EffectiveFieldLaneGains', ADDON)
        self.assertNotIn('Ringz.ar', ADDON)
        self.assertNotIn('Impulse.ar', ADDON)

    def test_modes_preserve_the_declared_power_policies(self) -> None:
        self.assertIn('FIXED RMS / BASIS TIMBRE', ADDON)
        self.assertIn('PURITY -> ENERGY', ADDON)
        self.assertIn('activePower.sqrt', ADDON)
        self.assertIn('* 2.sqrt', ADDON)
        self.assertIn('matrixPowerBins', ADDON)
        self.assertIn('parsevalResidual', ADDON)

    def test_adapter_keeps_v42_routing_and_exact_bypass(self) -> None:
        self.assertIn('\\out, ~qmwQFTV3FieldBus', ADDON)
        self.assertIn('~qmwQFTV42ParsevalGain = 0.0', ADDON)
        self.assertIn('~qmwQFTV3OddEvenStereoWidth', ADDON)
        self.assertIn('~qmwQFTV3RendererMode', ADDON)
        self.assertIn('one persistent', ADDON)

    def test_launcher_owns_field_qho_and_four_qubit_sidecars(self) -> None:
        self.assertIn(
            'for PORT in 7402 17830 17831 17860 17861 17863 "$BLOCH_SC_PORT"',
            LAUNCHER,
        )
        self.assertIn('-m qmw.qho.live_osc', LAUNCHER)
        self.assertIn('QHO_PID=$!', LAUNCHER)
        self.assertIn('--osc-profile=full', LAUNCHER)
        self.assertIn('ENGINE_PID=$!', LAUNCHER)
        self.assertIn('for PID in "$ENGINE_PID" "$QHO_PID" "$FIELD_PID"', LAUNCHER)
        self.assertIn('PYTHON_BIN="${QMW_PYTHON:-', LAUNCHER)
        self.assertIn('SCLANG_BIN="${QMW_SCLANG:-', LAUNCHER)

    def test_live_startup_does_not_require_optional_notation(self) -> None:
        self.assertIn(
            "from qmw.performance.osc import PerformanceSnapshotPublisher",
            FLOW_SOURCE,
        )
        import_index = PERFORMANCE_SOURCE.index(
            "from procedural_notation_v1 import write_lilypond, write_musicxml"
        )
        stop_index = PERFORMANCE_SOURCE.index("def stop(self)")
        self.assertGreater(import_index, stop_index)


if __name__ == "__main__":
    unittest.main()
