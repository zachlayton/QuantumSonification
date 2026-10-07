from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from qmw.performance.resonant_recording import ResonantPerformanceRecorder


class ResonantRecordingTests(unittest.TestCase):
    def test_recorder_is_inert_then_writes_json_and_musicxml(self) -> None:
        event = SimpleNamespace(
            event_id="test",
            channel="simple",
            kind="pluck",
            source_inputs=(0,),
            source_outputs=(1,),
            amplitude=0.5 + 0.25j,
            membrane_energy=np.full(20, 1 / 400),
            dominant_mode=2,
            contact_azimuth=0.0,
        )
        frame = type("Frame", (), {"time": 1.25, "revision": 7, "events": (event,)})()
        with TemporaryDirectory() as directory:
            recorder = ResonantPerformanceRecorder(directory)
            recorder.capture(frame)
            self.assertEqual(recorder.events, [])
            recorder.start(
                take_id="take 1",
                name="Test",
                wav_path="take.wav",
                fundamental_hz=110,
                decay_seconds=0.2,
                bpm=120,
                pitch_ratios=[1.0] * 20,
            )
            recorder.capture(frame)
            artifact = recorder.stop()
            self.assertEqual(artifact["event_count"], 1)
            self.assertTrue(Path(artifact["event_json"]).is_file())
            self.assertTrue(Path(artifact["musicxml"]).is_file())


if __name__ == "__main__":
    unittest.main()
