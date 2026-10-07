from __future__ import annotations

import unittest

import numpy as np

from qmw.acoustics.spectral_v4 import (
    SpectralFrequencyPolicyV4,
    SpectralV4OSCSender,
    SpectralV4StateSubscriber,
    spectral_sonification_packet_v4,
)
from qmw.core import QuantumDataBus, QuantumStateFrame, analyze_quantum_spectrum


class RecordingOSCClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, payload: object) -> None:
        self.messages.append((address, payload))


class SpectralV4SonificationTests(unittest.TestCase):
    def test_energy_order_and_population_amplitudes_are_preserved(self) -> None:
        spectrum = analyze_quantum_spectrum(
            np.diag([0.2, 0.3, 0.5]), np.diag([-2.0, 0.0, 2.0])
        )
        packet = spectral_sonification_packet_v4(
            spectrum, 1.5, policy=SpectralFrequencyPolicyV4(100.0, 2.0)
        )
        self.assertEqual([voice.mode for voice in packet.voices], [1, 2, 3])
        np.testing.assert_allclose(
            [voice.frequency_hz for voice in packet.voices], [100.0, 200.0, 400.0]
        )
        np.testing.assert_allclose(
            [voice.amplitude for voice in packet.voices], np.sqrt([0.2, 0.3, 0.5])
        )

    def test_packet_is_one_compact_osc_message(self) -> None:
        spectrum = analyze_quantum_spectrum(np.diag([1.0, 0.0]), np.diag([0.0, 1.0]))
        packet = spectral_sonification_packet_v4(spectrum, 0.25)
        recorder = RecordingOSCClient()
        SpectralV4OSCSender(client=recorder).send_packet(packet)
        self.assertEqual(recorder.messages[0][0], "/qmw/v4/spectral/frame")
        payload = recorder.messages[0][1]
        self.assertEqual(len(payload), 11)
        np.testing.assert_allclose(
            payload[:7],
            [0.25, 2.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            atol=1.0e-12,
        )

    def test_fixed_energy_calibration_prevents_frame_extent_glissando(self) -> None:
        policy = SpectralFrequencyPolicyV4(
            reference_hz=100.0, octave_span=2.0, energy_min=0.0, energy_max=4.0,
        )
        first = policy.frequencies(np.array([0.0, 1.0, 4.0]))
        second = policy.frequencies(np.array([0.0, 1.0, 2.0]))
        self.assertAlmostEqual(first[1], second[1])
        self.assertAlmostEqual(first[1], 100.0 * np.sqrt(2.0))

    def test_fixed_energy_calibration_requires_two_ordered_bounds(self) -> None:
        with self.assertRaises(ValueError):
            SpectralFrequencyPolicyV4(energy_min=0.0)
        with self.assertRaises(ValueError):
            SpectralFrequencyPolicyV4(energy_min=1.0, energy_max=1.0)

    def test_degenerate_energy_labels_remain_audibly_distinct(self) -> None:
        policy = SpectralFrequencyPolicyV4(
            reference_hz=220.0, octave_span=2.0, degeneracy_spread_semitones=1.0,
        )
        frequencies = policy.frequencies(np.array([0.0, 0.0, 1.0, 1.0]))
        self.assertLess(frequencies[0], frequencies[1])
        self.assertLess(frequencies[2], frequencies[3])
        # Each equal-energy group remains centred at its energy-derived pitch.
        self.assertAlmostEqual(np.sqrt(frequencies[0] * frequencies[1]), 220.0)
        self.assertAlmostEqual(np.sqrt(frequencies[2] * frequencies[3]), 880.0)

    def test_rate_division_keeps_observer_off_each_frame(self) -> None:
        packets = []
        subscriber = SpectralV4StateSubscriber(every_n_frames=2, on_packet=packets.append)
        bus = QuantumDataBus()
        bus.state_bus.subscribe(subscriber)
        for step in range(5):
            bus.publish_state(
                QuantumStateFrame(
                    t=float(step),
                    dt=1.0,
                    rho=np.diag([0.5, 0.5]).astype(np.complex128),
                    hamiltonian=np.diag([0.0, 1.0]),
                )
            )
        self.assertEqual(len(packets), 3)
        self.assertEqual([packet.time for packet in packets], [0.0, 2.0, 4.0])
        self.assertEqual(packets[0].state_motion, 0.0)


if __name__ == "__main__":
    unittest.main()
