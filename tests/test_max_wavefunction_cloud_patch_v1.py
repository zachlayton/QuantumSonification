import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"


def load_patcher(name):
    return json.loads((MAX / name).read_text())["patcher"]


def boxes_by_id(patcher):
    return {item["box"]["id"]: item["box"] for item in patcher["boxes"]}


def connections(patcher):
    return {
        (
            tuple(item["patchline"]["source"]),
            tuple(item["patchline"]["destination"]),
        )
        for item in patcher["lines"]
    }


class MaxWavefunctionCloudPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(MAX / "build_qmw_wavefunction_cloud_grains_v1.py")],
            cwd=ROOT,
            check=True,
        )

    def test_poly_voice_exposes_two_msp_outputs(self):
        voice = load_patcher("qmw_wavefunction_cloud_grain_voice_v1.maxpat")
        boxes = boxes_by_id(voice)
        self.assertEqual(boxes["in"]["text"], "in 1")
        self.assertEqual(boxes["out_left"]["text"], "out~ 1")
        self.assertEqual(boxes["out_right"]["text"], "out~ 2")
        self.assertEqual(boxes["out_ack"]["text"], "out 1")
        self.assertEqual(boxes["env_message"]["text"], "1., 0. $1")
        links = connections(voice)
        self.assertIn((("left", 0), ("out_left", 0)), links)
        self.assertIn((("right", 0), ("out_right", 0)), links)
        self.assertIn((("ack", 0), ("out_ack", 0)), links)

    def test_poly_outputs_feed_true_stereo_gain_and_dac(self):
        host = load_patcher("QMW_Wavefunction_Cloud_Grains_v1.maxpat")
        boxes = boxes_by_id(host)
        self.assertEqual(boxes["poly"]["outlettype"][:2], ["signal", "signal"])
        self.assertEqual(boxes["gain"]["maxclass"], "live.gain~")
        self.assertEqual(boxes["gain"]["outlettype"][:2], ["signal", "signal"])
        links = connections(host)
        for connection in (
            (("poly", 0), ("gain", 0)),
            (("poly", 1), ("gain", 1)),
            (("gain", 0), ("dac", 0)),
            (("gain", 1), ("dac", 1)),
        ):
            self.assertIn(connection, links)

    def test_cloud_uses_dedicated_max_udp_port(self):
        host = load_patcher("QMW_Wavefunction_Cloud_Grains_v1.maxpat")
        boxes = boxes_by_id(host)
        self.assertEqual(boxes["udp"]["text"], "udpreceive 7480")

    def test_output_stage_starts_audible_and_has_local_diagnostic(self):
        host = load_patcher("QMW_Wavefunction_Cloud_Grains_v1.maxpat")
        boxes = boxes_by_id(host)
        gain_attributes = boxes["gain"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual(gain_attributes["parameter_initial"], [-12.0])
        self.assertEqual(gain_attributes["parameter_initial_enable"], 1)
        self.assertEqual(boxes["dsp_on"]["text"], "loadmess 1")
        self.assertIn("grain", boxes["test_grain"]["text"])
        self.assertIn(".maxpat", boxes["poly"]["text"])
        links = connections(host)
        for connection in (
            (("poly", 0), ("pre_meter_l", 0)),
            (("poly", 1), ("pre_meter_r", 0)),
            (("dsp_on", 0), ("dac", 0)),
            (("test_grain", 0), ("poly", 0)),
        ):
            self.assertIn(connection, links)

    def test_direct_audio_diagnostic_bypasses_poly(self):
        host = load_patcher("QMW_Wavefunction_Cloud_Grains_v1.maxpat")
        boxes = boxes_by_id(host)
        self.assertEqual(boxes["direct_cycle"]["text"], "cycle~ 220")
        self.assertEqual(boxes["direct_amp"]["text"], "*~ 0.08")
        links = connections(host)
        for connection in (
            (("direct_toggle", 0), ("direct_amp", 1)),
            (("direct_cycle", 0), ("direct_amp", 0)),
            (("direct_amp", 0), ("gain", 0)),
            (("direct_amp", 0), ("gain", 1)),
        ):
            self.assertIn(connection, links)

    def test_poly_voices_are_unmuted_and_acknowledge_grains(self):
        host = load_patcher("QMW_Wavefunction_Cloud_Grains_v1.maxpat")
        boxes = boxes_by_id(host)
        self.assertEqual(boxes["unmute"]["text"], "loadmess mute 0 0")
        self.assertEqual(boxes["poly"]["numoutlets"], 3)
        links = connections(host)
        self.assertIn((("unmute", 0), ("poly", 0)), links)
        self.assertIn((("poly", 2), ("voice_ack", 1)), links)


if __name__ == "__main__":
    unittest.main()
