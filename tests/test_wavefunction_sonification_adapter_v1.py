import unittest
from dataclasses import replace

import numpy as np

from excitation.wavefunction_sonification_adapter_v1 import (
    WavefunctionGrainConfig,
    WavefunctionSonificationAdapter,
    grains_from_wavefunction_frame,
)
from excitation.wavefunction_sources_v1 import create_wavefunction_source
from examples.wavefunction_cloud_osc_v1 import grid_parameters_for_source


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class WavefunctionSonificationAdapterTests(unittest.TestCase):
    def frame(self):
        source = create_wavefunction_source(
            "schrodinger_packet_3d",
            grid_shape=12,
        )
        return source.frame(0.01)

    def test_every_grain_has_five_millisecond_decay(self):
        cloud = grains_from_wavefunction_frame(self.frame(), frame_id=3)
        self.assertEqual(len(cloud.grains), 16)
        self.assertTrue(all(grain.decay_ms == 5.0 for grain in cloud.grains))

    def test_grain_controls_are_bounded_and_sample_probability_mass(self):
        frame = self.frame()
        cloud = grains_from_wavefunction_frame(
            frame,
            frame_id=7,
            config=WavefunctionGrainConfig(grains_per_frame=24),
        )
        self.assertAlmostEqual(cloud.norm, 1.0, places=9)
        self.assertEqual(len(cloud.grains), 24)
        for grain in cloud.grains:
            self.assertTrue(-1.0 <= grain.x <= 1.0)
            self.assertTrue(-1.0 <= grain.y <= 1.0)
            self.assertTrue(-1.0 <= grain.z <= 1.0)
            self.assertTrue(0.0 <= grain.amplitude <= 1.0)
            self.assertTrue(-1.0 <= grain.phase <= 1.0)
            self.assertTrue(0.0 <= grain.energy <= 1.0)
        self.assertGreater(float(np.mean([grain.amplitude for grain in cloud.grains])), 0.0)

    def test_identical_frame_id_is_deterministic(self):
        frame = self.frame()
        first = grains_from_wavefunction_frame(frame, frame_id=11)
        second = grains_from_wavefunction_frame(frame, frame_id=11)
        self.assertEqual(first, second)

    def test_publishes_frame_grains_and_end_to_all_clients(self):
        max_sc = RecordingClient()
        processing = RecordingClient()
        adapter = WavefunctionSonificationAdapter(
            (max_sc, processing),
            WavefunctionGrainConfig(grains_per_frame=8),
        )
        cloud = adapter.publish_frame(self.frame())

        self.assertEqual(max_sc.messages, processing.messages)
        self.assertEqual(max_sc.messages[0][0], "/qmw/wavefunction/cloud/frame")
        self.assertEqual(max_sc.messages[-1][0], "/qmw/wavefunction/cloud/end")
        self.assertEqual(len(max_sc.messages), 10)
        grain_messages = [value for address, value in max_sc.messages if address.endswith("/grain")]
        self.assertEqual(len(grain_messages), 8)
        self.assertTrue(all(packet[-1] == 5.0 for packet in grain_messages))
        self.assertEqual(cloud.frame_id, 0)

    def test_adaptive_rate_responds_to_probability_redistribution(self):
        frame = self.frame()
        config = WavefunctionGrainConfig(
            adaptive_rate=True,
            min_grains_per_frame=2,
            max_grains_per_frame=40,
            density_change_sensitivity=32.0,
            current_weight=0.0,
            rate_smoothing=1.0,
        )
        adapter = WavefunctionSonificationAdapter(config=config)
        still = adapter.publish_frame(frame)
        shifted = replace(frame, probability=np.roll(frame.probability, 4, axis=0))
        moving = adapter.publish_frame(shifted)
        self.assertEqual(len(still.grains), 2)
        self.assertGreater(moving.density_change, 0.0)
        self.assertGreater(moving.activity, still.activity)
        self.assertGreater(len(moving.grains), len(still.grains))
        self.assertLessEqual(len(moving.grains), 40)

    def test_every_discussed_instrument_reaches_the_grain_pipeline(self):
        names = (
            "schrodinger_packet_3d",
            "harmonic_oscillator",
            "harmonic_oscillator_3d",
            "coherent_state",
            "squeezed_state",
            "particle_in_box",
            "quantum_rotor",
            "double_well",
            "barrier_scattering",
            "periodic_lattice",
            "hydrogen_orbital_field",
            "hydrogen_superposition_3d",
            "spherical_harmonic",
        )
        for name in names:
            with self.subTest(source=name):
                source = create_wavefunction_source(
                    name,
                    **grid_parameters_for_source(name, 8),
                )
                frame = source.frame(0.01)
                cloud = grains_from_wavefunction_frame(
                    frame,
                    frame_id=0,
                    config=WavefunctionGrainConfig(grains_per_frame=2),
                )
                self.assertEqual(len(cloud.grains), 2)
                self.assertAlmostEqual(cloud.norm, 1.0, places=8)

    def test_irregular_onsets_are_ordered_bounded_and_deterministic(self):
        first = WavefunctionSonificationAdapter.grain_onset_fractions(7, 12)
        second = WavefunctionSonificationAdapter.grain_onset_fractions(7, 12)
        another_frame = WavefunctionSonificationAdapter.grain_onset_fractions(8, 12)
        self.assertEqual(first, second)
        self.assertNotEqual(first, another_frame)
        self.assertEqual(len(first), 12)
        self.assertTrue(all(0.0 < onset < 1.0 for onset in first))
        self.assertTrue(all(a < b for a, b in zip(first, first[1:])))
        gaps = np.diff((0.0, *first, 1.0))
        self.assertGreater(float(np.std(gaps)), 0.01)

    def test_adaptive_mode_can_emit_a_silent_frame(self):
        config = WavefunctionGrainConfig(
            adaptive_rate=True,
            min_grains_per_frame=0,
            max_grains_per_frame=12,
            current_weight=0.0,
        )
        cloud = WavefunctionSonificationAdapter(config=config).publish_frame(self.frame())
        self.assertEqual(len(cloud.grains), 0)


if __name__ == "__main__":
    unittest.main()
