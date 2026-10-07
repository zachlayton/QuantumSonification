import unittest
import numpy as np
from qmw.core.domain import Domain
from qmw.core.frame import (PhysicsFrame, StateData, ObservableData, RegionalData,
                            PhysicsEvent, EventType, SoundEvent)
from qmw.sound import SonificationPolicy, render


def sound_fixture():
    domain = Domain.periodic(32, 16)
    psi = np.full(domain.size, 1 / np.sqrt(domain.length), complex)
    event = PhysicsEvent(EventType.ENERGY_ARRIVAL, .1, .25,
                         "incoming_energy_flux", region=2,
                         detail="Region 3 incoming flux 0.25 exceeded threshold 0.01.")
    return PhysicsFrame(7, .1, .002, "schrodinger_1d", domain,
                        StateData(psi=psi), ObservableData(),
                        regions=RegionalData(np.arange(16), energy=np.ones(16)),
                        events=[event])


class SoundTests(unittest.TestCase):
    def test_mapping_is_explicit_and_does_not_mutate_physics(self):
        frame = sound_fixture()
        original = frame.state.psi.copy()
        policy = SonificationPolicy(fundamental_hz=110, gain=.2, flux_scale=1)
        sound = policy.map(frame)
        self.assertEqual(sound.events[0].frequency_hz, 330)
        self.assertAlmostEqual(sound.events[0].amplitude, .1)
        self.assertIn("threshold 0.01", sound.events[0].explanation)
        self.assertIn("110 Hz", sound.events[0].explanation)
        self.assertEqual(sound.events[0].event_id, policy.map(frame).events[0].event_id)
        np.testing.assert_array_equal(frame.state.psi, original)

    def test_no_event_means_no_new_sound(self):
        frame = sound_fixture()
        frame.events = []
        self.assertEqual(SonificationPolicy().map(frame).events, [])
        np.testing.assert_array_equal(render([], .25), np.zeros((12000, 2)))

    def test_rendered_harmonic_pitch_and_safe_mix(self):
        event = SoundEvent("one", 0, 200, .5, .5, 0, 0, None, "test", "test")
        audio = render([event], 1, 16000)
        self.assertEqual(audio.shape, (16000, 2))
        np.testing.assert_allclose(audio[:, 0], audio[:, 1], atol=1e-15)
        spectrum = abs(np.fft.rfft(audio[:, 0]))
        frequencies = np.fft.rfftfreq(len(audio), 1 / 16000)
        self.assertEqual(frequencies[np.argmax(spectrum)], 200)
        self.assertGreater(spectrum[400], spectrum[403] * 3)
        mixed = render([event] * 100, 1, 16000)
        self.assertLessEqual(float(np.max(np.abs(mixed))), .95000000000001)
        self.assertTrue(np.isfinite(mixed).all())

    def test_reject_invalid_gain_and_mapping(self):
        with self.assertRaises(ValueError):
            SonificationPolicy(gain=2)
        with self.assertRaises(ValueError):
            SonificationPolicy(pitch_mapping="mode_sqrt").map(sound_fixture())


if __name__ == "__main__":
    unittest.main()
