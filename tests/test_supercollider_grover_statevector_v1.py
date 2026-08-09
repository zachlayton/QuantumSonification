from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercollider/qmw_grover_statevector_sonification_v1.scd"


class SuperColliderGroverStatevectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_consumes_literal_statevector_addresses(self):
        for address in (
            "/qmw/grover/statevector/frame",
            "/qmw/grover/statevector/modes",
            "/qmw/grover/statevector/found",
            "/qmw/grover/statevector/state",
        ):
            self.assertIn(address, self.source)
        self.assertNotIn("sin((2 * iteration", self.source)
        self.assertIn("thisProcess.openUDPPort(7494)", self.source)
        self.assertEqual(self.source.count("nil, 7494);"), 4)

    def test_all_complex_walsh_modes_are_persistent_and_smoothed(self):
        self.assertIn("NamedControl.kr(\\coeffReal, Array.fill(64", self.source)
        self.assertIn("NamedControl.kr(\\coeffImag, Array.fill(64", self.source)
        self.assertIn("VarLag.kr(real", self.source)
        self.assertIn("Mix.fill(64", self.source)
        self.assertIn("setn(\\coeffReal, real)", self.source)
        self.assertIn("setn(\\coeffImag, imag)", self.source)

    def test_tangle_geometry_uses_requested_depths(self):
        self.assertIn("wetGain = 0.7", self.source)
        self.assertIn("geometryDepth = 0.7", self.source)
        self.assertIn("ringDepth = 0.8", self.source)
        self.assertIn("111.952149", self.source)
        self.assertIn("460.084351", self.source)
        self.assertIn("Mix.fill(24", self.source)
        self.assertIn("Mix.fill(8", self.source)

    def test_found_event_freezes_post_geometry_spectrum(self):
        self.assertIn("PV_MagFreeze", self.source)
        self.assertIn("~qmwGroverSCFX.set(\\freeze, 1)", self.source)
        self.assertIn("input * dryGain * (1 - freezeLag)", self.source)
        self.assertIn("~qmwGroverSCFX.set(\\freeze, 0)", self.source)

    def test_has_cleanup_and_limiter(self):
        self.assertIn("~qmwGroverSCStop", self.source)
        self.assertIn("Limiter.ar", self.source)
        self.assertIn("~qmwGroverSCBus.free", self.source)


if __name__ == "__main__":
    unittest.main()
