"""Optional integration checks using installed sclang/scsynth, no audio hardware."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCLANG = os.environ.get("QMW_SCLANG_PATH") or shutil.which("sclang")
SCSYNTH = os.environ.get("QMW_SCSYNTH_PATH") or shutil.which("scsynth")


def language_command(fixture: str) -> list[str]:
    command = [SCLANG, "-D"]
    config = os.environ.get("QMW_SCLANG_CONFIG")
    if config:
        command += ["-l", config]
    return command + [str(ROOT / "tests" / fixture)]


@unittest.skipUnless(SCLANG, "install SuperCollider to run its native integration checks")
class SuperColliderTests(unittest.TestCase):
    def test_actual_language_mapping_receiver_and_dsp_compilation(self):
        result = subprocess.run(language_command("test_yang_mills_supercollider_v1.scd"),
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: SuperCollider power conservation", result.stdout)

    def test_real_python_to_sclang_osc_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / "ready.txt"
            env = dict(os.environ, QMW_SC_READY_PATH=str(ready))
            process = subprocess.Popen(language_command("receive_yang_mills_supercollider_v1.scd"),
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
            try:
                deadline = time.monotonic() + 10
                while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(ready.exists(), "sclang did not publish its receiver port")
                source = subprocess.run([sys.executable, "-m", "yang_mills_v1", "--osc",
                    "--steps", "15", "--port", ready.read_text()], cwd=ROOT,
                    capture_output=True, text=True, timeout=10)
                self.assertEqual(source.returncode, 0, source.stderr)
                output, _ = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, output)
                self.assertIn("PASS: actual Python OSC bundles", output)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()

    @unittest.skipUnless(SCSYNTH, "scsynth is required for non-realtime DSP rendering")
    def test_native_render_is_finite_audible_and_mutable(self):
        with tempfile.TemporaryDirectory() as directory:
            score = Path(directory) / "score.osc"
            audio = Path(directory) / "render.wav"
            env = dict(os.environ, QMW_SC_SCORE_PATH=str(score))
            result = subprocess.run(language_command("render_yang_mills_supercollider_v1.scd"),
                cwd=ROOT, capture_output=True, text=True, timeout=30, env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            command = [SCSYNTH, "-D", "0", "-o", "2", "-i", "0"]
            plugins = os.environ.get("QMW_SC_PLUGINS_PATH")
            if plugins:
                command += ["-U", plugins]
            command += ["-N", str(score), "_", str(audio), "48000", "WAV", "float"]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            raw = audio.read_bytes()
            position, samples, channels, rate = 12, None, None, None
            while position + 8 <= len(raw):
                name = raw[position:position + 4]
                size = struct.unpack_from("<I", raw, position + 4)[0]
                chunk = raw[position + 8:position + 8 + size]
                if name == b"fmt ":
                    format, channels, rate = struct.unpack_from("<HHI", chunk)
                    self.assertEqual(format, 3)  # IEEE float WAV
                elif name == b"data":
                    samples = np.frombuffer(chunk, dtype="<f4").reshape(-1, channels)
                position += 8 + size + size % 2
            self.assertIsNotNone(samples)
            self.assertTrue(np.isfinite(samples).all())
            self.assertLessEqual(np.max(np.abs(samples)), 0.951)
            active = samples[int(0.1 * rate):int(0.45 * rate)]
            self.assertGreater(np.sqrt(np.mean(active ** 2)), 1e-4)
            # Separate fresh synths check coupling=0, master=0 and vacuum.
            for start, stop in ((0.65, 0.95), (1.15, 1.45), (1.65, 1.95)):
                self.assertLess(np.max(np.abs(samples[int(start * rate):int(stop * rate)])), 1e-10)


if __name__ == "__main__":
    unittest.main()
