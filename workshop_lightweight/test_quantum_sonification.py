import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

import quantum_sonification as qs


class WorkshopExamplesTest(unittest.TestCase):
    def test_named_states_have_expected_probabilities(self):
        p0, p1, x, y, z = qs.observables(*qs.qubit(np.pi / 2.0, 0.0))
        self.assertAlmostEqual(float(p0), 0.5)
        self.assertAlmostEqual(float(p1), 0.5)
        self.assertAlmostEqual(float(x), 1.0)
        self.assertAlmostEqual(float(y), 0.0)
        self.assertAlmostEqual(float(z), 0.0)

    def test_procedural_irs_are_distinct(self):
        bright = qs.procedural_ir("bright", 11)
        dark = qs.procedural_ir("dark", 29)
        self.assertLess(len(bright), len(dark))
        self.assertTrue(np.isfinite(bright).all())
        self.assertTrue(np.isfinite(dark).all())

    def test_bell_and_product_states_share_marginals_but_not_correlations(self):
        product = qs.two_qubit_observables(qs.two_qubit_state("plus_plus"))
        bell = qs.two_qubit_observables(qs.two_qubit_state("bell"))
        self.assertAlmostEqual(product[1], bell[1])
        self.assertAlmostEqual(product[2], bell[2])
        self.assertAlmostEqual(product[3], 0.0)
        self.assertAlmostEqual(bell[3], 1.0)
        self.assertFalse(np.allclose(product[0], bell[0]))

    def test_wavetable_has_exact_size_and_reflects_state(self):
        zero = qs.amplitudes_to_wavetable(np.array([1, 0]), size=256)
        plus = qs.amplitudes_to_wavetable(np.array([1, 1]) / np.sqrt(2), size=256)
        self.assertEqual(len(zero), 256)
        self.assertAlmostEqual(float(np.mean(zero)), 0.0, places=12)
        self.assertFalse(np.allclose(zero, plus))

    def test_rendered_wavetable_has_exactly_256_frames(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            qs.render_wavetables(output)
            path = output / "wavetable_256_two_qubit_bell.wav"
            with wave.open(str(path), "rb") as audio:
                self.assertEqual(audio.getnframes(), 256)
                self.assertEqual(audio.getnchannels(), 1)

    def test_reverb_demo_writes_valid_wav_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            qs.render_reverb(output)
            paths = sorted(output.glob("*.wav"))
            self.assertEqual(len(paths), 6)
            with wave.open(str(paths[-1]), "rb") as audio:
                self.assertEqual(audio.getframerate(), qs.SAMPLE_RATE)
                self.assertGreater(audio.getnframes(), qs.SAMPLE_RATE)


if __name__ == "__main__":
    unittest.main()
