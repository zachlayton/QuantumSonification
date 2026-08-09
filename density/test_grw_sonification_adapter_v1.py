from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import wave

import numpy as np

from density.grw_event_channel_v1 import GRWConfig, GRWEventChannel, ghz_density
from density.grw_sonification_adapter_v1 import (
    GRWSonificationAdapter,
    frame_from_grw_event,
)
from density.grw_ghz_sonification_experiment_v1 import render_ghz_experiment


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class GRWSonificationAdapterTests(unittest.TestCase):
    def event(self, *, qubit=2, strength=1.0):
        channel = GRWEventChannel(GRWConfig(seed=19))
        return channel.apply_hit(
            ghz_density(),
            revision_before=4,
            qubit=qubit,
            outcome=0,
            basis="Z",
            strength=strength,
        )

    def test_mapping_contract_for_projective_ghz_hit(self):
        event = self.event(qubit=2)
        frame = frame_from_grw_event(event)

        self.assertEqual(frame.branch, 2)
        self.assertAlmostEqual(frame.excitation_amplitude, event.trace_distance)
        self.assertAlmostEqual(frame.coherence_loss_fraction, 1.0)
        self.assertAlmostEqual(frame.bandwidth, 1.0)
        self.assertAlmostEqual(frame.grain_structure, 1.0)
        self.assertIn(frame.pauli_axis, "XYZ")
        self.assertEqual(len(frame.branch_levels), 4)
        self.assertEqual(len(frame.post_population), 16)
        self.assertEqual(len(frame.post_rho_magnitude), 256)
        self.assertEqual(len(frame.delta_rho_magnitude), 256)
        self.assertAlmostEqual(sum(frame.post_population), 1.0)
        self.assertAlmostEqual(max(frame.post_rho_magnitude), 1.0)
        self.assertAlmostEqual(max(frame.delta_rho_magnitude), 1.0)

    def test_zero_strength_event_has_no_excitation_or_grain(self):
        frame = frame_from_grw_event(self.event(strength=0.0))
        self.assertAlmostEqual(frame.excitation_amplitude, 0.0, places=13)
        self.assertAlmostEqual(frame.coherence_loss_fraction, 0.0, places=13)
        self.assertAlmostEqual(frame.grain_structure, 0.0, places=13)
        self.assertAlmostEqual(frame.delta_peak, 0.0, places=13)
        np.testing.assert_allclose(frame.delta_rho_real, 0.0, atol=1e-13)

    def test_publishes_state_before_trigger_to_all_clients_once(self):
        max_sc = RecordingClient()
        processing = RecordingClient()
        adapter = GRWSonificationAdapter((max_sc, processing))
        event = self.event()

        frame = adapter.publish_event(event)
        duplicate = adapter.publish_event(event)

        self.assertIsNotNone(frame)
        self.assertIsNone(duplicate)
        self.assertEqual(max_sc.messages, processing.messages)
        addresses = [address for address, _ in max_sc.messages]
        self.assertEqual(addresses[-1], "/qmw/grw/sonification/event")
        self.assertLess(
            addresses.index("/qmw/grw/sonification/post/rho_magnitude"),
            addresses.index("/qmw/grw/sonification/event"),
        )
        self.assertEqual(len(max_sc.messages[-1][1]), 10)

    def test_resonator_engine_forwards_each_current_step_event(self):
        from quantum_population_osc_v9_resonator import MLXQuantumResonatorEngine

        events = [self.event(qubit=0), self.event(qubit=3)]
        engine = object.__new__(MLXQuantumResonatorEngine)
        engine.density_engine = SimpleNamespace(grw_events=events)
        engine.grw_sonification = Mock()
        engine.grw_sonification.publish_event.side_effect = ["a", "b"]

        frames = engine.send_grw_sonification_events()

        self.assertEqual(frames, ["a", "b"])
        self.assertEqual(
            engine.grw_sonification.publish_event.call_args_list,
            [unittest.mock.call(events[0]), unittest.mock.call(events[1])],
        )

    def test_first_ghz_experiment_renders_a_deterministic_stereo_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.wav"
            second = Path(directory) / "second.wav"
            _, frame = render_ghz_experiment(
                first,
                sample_rate=8_000,
                pre_event_seconds=0.02,
                post_event_seconds=0.04,
            )
            render_ghz_experiment(
                second,
                sample_rate=8_000,
                pre_event_seconds=0.02,
                post_event_seconds=0.04,
            )
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertGreater(frame.excitation_amplitude, 0.0)
            with wave.open(str(first), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), 480)
                samples = np.frombuffer(wav_file.readframes(480), dtype="<i2")
            self.assertGreater(int(np.max(np.abs(samples))), 0)


if __name__ == "__main__":
    unittest.main()
