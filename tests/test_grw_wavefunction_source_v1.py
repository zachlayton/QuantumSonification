import unittest

import numpy as np

from excitation.grw_wavefunction_source_v1 import (
    GRWWavefunctionConfig,
    GRWWavefunctionSource,
)
from excitation.wavefunction_sonification_adapter_v1 import (
    WavefunctionGrainConfig,
    WavefunctionSonificationAdapter,
)
from excitation.wavefunction_sources_v1 import create_wavefunction_source


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class GRWWavefunctionSourceTests(unittest.TestCase):
    def wrapper(self, *, rate=2.0, width=0.7, seed=23):
        base = create_wavefunction_source("schrodinger_packet_3d", grid_shape=12)
        return GRWWavefunctionSource(
            base,
            GRWWavefunctionConfig(
                rate_hz=rate,
                localization_width=width,
                seed=seed,
            ),
        )

    def test_jump_splits_evolution_at_exact_time_and_preserves_norm(self):
        source = self.wrapper()
        source.next_event_time = 0.05
        frame = source.frame(0.1)
        self.assertEqual(len(source.events), 1)
        event = source.events[0]
        self.assertAlmostEqual(event.logical_time, 0.05, places=12)
        self.assertAlmostEqual(source.logical_time, 0.1, places=12)
        self.assertAlmostEqual(frame.time, 0.1, places=12)
        self.assertAlmostEqual(frame.norm, 1.0, places=10)
        self.assertAlmostEqual(event.frame_after.norm, 1.0, places=10)
        self.assertGreater(event.total_variation, 0.0)
        self.assertGreater(float(np.max(np.abs(event.delta_probability))), 0.0)

    def test_jump_probability_delta_conserves_total_mass(self):
        source = self.wrapper()
        source.next_event_time = 0.02
        source.frame(0.03)
        event = source.events[0]
        spacing = [float(np.mean(np.diff(axis))) for axis in event.frame_after.coordinates]
        measure = abs(float(np.prod(spacing)))
        self.assertAlmostEqual(float(np.sum(event.delta_probability) * measure), 0.0, places=9)

    def test_seeded_poisson_waiting_times_have_configured_mean(self):
        source = self.wrapper(rate=4.0, seed=91)
        waits = np.asarray(source.sample_waiting_time(50_000))
        self.assertAlmostEqual(float(np.mean(waits)), 0.25, delta=0.004)
        self.assertGreater(float(np.std(waits)), 0.24)

    def test_reset_reproduces_first_jump_time(self):
        source = self.wrapper(seed=17)
        first = source.next_event_time
        source.frame(0.01)
        source.reset()
        self.assertAlmostEqual(source.next_event_time, first, places=12)

    def test_analytic_source_is_rejected_because_collapse_would_not_persist(self):
        analytic = create_wavefunction_source("particle_in_box", n_points=32)
        with self.assertRaises(TypeError):
            GRWWavefunctionSource(analytic)

    def test_osc_grains_are_derived_only_from_jump_delta(self):
        source = self.wrapper()
        source.next_event_time = 0.02
        source.frame(0.03)
        event = source.events[0]
        client = RecordingClient()
        adapter = WavefunctionSonificationAdapter(
            (client,),
            WavefunctionGrainConfig(decay_ms=5.0, amplitude_gain=0.5),
        )
        cloud = adapter.publish_grw_event(event, min_grains=1, max_grains=16)
        grain_packets = [value for address, value in client.messages if address.endswith("/grain")]
        self.assertEqual(len(grain_packets), len(cloud.grains))
        self.assertGreater(len(grain_packets), 0)
        self.assertTrue(all(packet[-1] == 5.0 for packet in grain_packets))
        self.assertEqual(client.messages[0][0], "/qmw/wavefunction/cloud/frame")
        self.assertEqual(client.messages[-1][0], "/qmw/wavefunction/cloud/end")


if __name__ == "__main__":
    unittest.main()
