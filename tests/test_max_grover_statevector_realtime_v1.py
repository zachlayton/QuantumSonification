from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"


def load(name: str):
    return json.loads((MAX / name).read_text())["patcher"]


def boxes(patcher):
    return {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}


def links(patcher):
    return {(tuple(x["patchline"]["source"]), tuple(x["patchline"]["destination"])) for x in patcher["lines"]}


class MaxGroverStatevectorRealtimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(MAX / "build_qmw_grover_statevector_realtime_v1.py")], cwd=ROOT, check=True)

    def test_receives_exact_operator_and_mode_stream(self):
        patch = load("QMW_Grover_Statevector_Realtime_v1.maxpat")
        b = boxes(patch)
        self.assertEqual(b["udp"]["text"], "udpreceive 7493")
        self.assertEqual(b["root"]["text"], "OSC-route /qmw/grover/statevector")
        self.assertIn("/frame /modes /found /state", b["route"]["text"])
        self.assertIn("64 @steal 0", b["poly"]["text"])

    def test_statevector_audio_enters_existing_surface_engine(self):
        patch = load("QMW_Grover_Statevector_Realtime_v1.maxpat")
        b = boxes(patch)
        l = links(patch)
        self.assertEqual(b["send_l"]["text"], "send~ qmw_spectral_L")
        self.assertEqual(b["wet_l"]["text"], "receive~ qmw_surface_L")
        self.assertIn((("poly", 0), ("send_l", 0)), l)
        self.assertIn((("dispatch", 3), ("surface_ctl", 0)), l)
        self.assertEqual(
            b["surface"]["name"], "QMW_Realtime_Surface_Reverb_Grover_v1.maxpat"
        )
        self.assertTrue((MAX / b["surface"]["name"]).is_file())

    def test_ableton_dsp_and_stable_hold_are_wired(self):
        patch = load("QMW_Grover_Statevector_Realtime_v1.maxpat")
        b = boxes(patch)
        l = links(patch)
        self.assertIn("@mix 0.8", b["ringmod"]["text"])
        self.assertTrue(b["tides"]["text"].startswith("abl.dsp.tides~"))
        self.assertTrue(b["prism"]["text"].startswith("abl.dsp.prism~"))
        self.assertEqual(b["freeze"]["text"], "freeze 1")
        self.assertIn((("dispatch", 4), ("event_sel", 0)), l)
        self.assertIn((("freeze", 0), ("prism", 0)), l)
        self.assertIn((("prism", 0), ("hold_l", 0)), l)

    def test_output_is_audible_before_high_confidence(self):
        patch = load("QMW_Grover_Statevector_Realtime_v1.maxpat")
        b = boxes(patch)
        gain = b["gain"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual(gain["parameter_initial"], [-9.0])
        self.assertEqual(gain["parameter_initial_enable"], 1)
        dispatcher = (MAX / "qmw_grover_statevector_dispatch_v1.js").read_text()
        self.assertIn("0.75 + 0.25", dispatcher)
        self.assertNotIn("Math.max(0.02, probability)", dispatcher)

    def test_voice_slews_signed_walsh_coefficients_without_clicks(self):
        voice = load("qmw_grover_walsh_mode_voice_v1.maxpat")
        b = boxes(voice)
        l = links(voice)
        self.assertEqual(b["route"]["text"], "route mode")
        self.assertEqual(b["gain_line"]["text"], "line~")
        self.assertIn((("gain_line", 0), ("amp", 1)), l)
        self.assertEqual(b["out_l"]["text"], "out~ 1")
        self.assertEqual(b["out_r"]["text"], "out~ 2")


if __name__ == "__main__":
    unittest.main()
