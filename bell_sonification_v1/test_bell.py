from __future__ import annotations

import json
import unittest

import numpy as np

from bell_sonification_v1 import render, source


class BellTests(unittest.TestCase):
    def test_ideal_probabilities_sum_and_curve(self):
        for t in np.linspace(0, np.pi, 7):
            p = source.ideal_probabilities("entangled", t)
            self.assertAlmostEqual(p.sum(), 1.0)
            self.assertAlmostEqual(p[0] + p[3] - p[1] - p[2], np.cos(t))

    def test_ideal_entangled_always_agrees_at_zero(self):
        run = source.sample_ideal("entangled", 0.0, 2000, seed=1)
        self.assertTrue(run.agree.all())
        self.assertAlmostEqual(run.shots[:, 0].mean(), 0.5, delta=0.04)   # each side alone: a fair coin

    def test_ideal_curve_points(self):
        self.assertAlmostEqual(source.sample_ideal("entangled", np.pi / 2, 20000, 2).correlation, 0.0, delta=0.03)
        self.assertTrue((~source.sample_ideal("entangled", np.pi, 2000, 3).agree).all())
        self.assertAlmostEqual(source.sample_ideal("independent", 0.0, 20000, 4).correlation, 0.0, delta=0.03)

    def test_aer_matches_ideal(self):
        run = source.sample_aer("entangled", 0.0, 1000, seed=5)
        self.assertTrue(run.agree.all())
        for t in (np.pi / 3, 2 * np.pi / 3):
            self.assertAlmostEqual(source.sample_aer("entangled", t, 8000, seed=6).correlation, np.cos(t), delta=0.04)
        self.assertAlmostEqual(source.sample_aer("independent", 0.0, 8000, seed=7).correlation, 0.0, delta=0.04)

    def test_bit_order(self):
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
        qc = QuantumCircuit(2, 2); qc.x(0); qc.measure(0, 0); qc.measure(1, 1)
        mem = AerSimulator().run(transpile(qc, AerSimulator()), shots=4, memory=True).result().get_memory()
        self.assertTrue((source._bits_from_strings(mem) == [1, 0]).all())   # a=1, b=0

    def test_archive_roundtrip(self, tmp=None):
        import tempfile, pathlib
        runs = [source.sample_ideal("entangled", t, 16, 8) for t in (0.0, np.pi)]
        d = pathlib.Path(tempfile.mkdtemp())
        payload = {"source": "ibm", "backend": "fake", "job_id": "x", "kind": "entangled",
                   "runs": [{"theta": r.theta, "shots": r.shots.tolist()} for r in runs]}
        (d / "a.json").write_text(json.dumps(payload))
        back = source.load_archive(d / "a.json")
        self.assertEqual(back[0].provenance["source"], "archived ibm")
        self.assertTrue((back[1].shots == runs[1].shots).all())

    def test_renders_finite(self):
        ent = source.sample_ideal("entangled", 0.0, 12, 9)
        ind = source.sample_ideal("independent", 0.0, 12, 10)
        for audio in (render.render_voices([ent]), render.render_agreement([ent, ind]), render.render_sweep([ent, ind])):
            self.assertEqual(audio.shape[1], 2)
            self.assertTrue(np.isfinite(audio).all())

    def test_agreement_tone_tracks_agreement(self):
        ent = source.sample_ideal("entangled", 0.0, 40, 11)
        opp = source.sample_ideal("entangled", np.pi, 40, 12)        # never agree
        def tone_energy(a):   # the tone is identical in both channels; clicks are not
            mid = (a[:, 0] + a[:, 1]) / 2
            side = (a[:, 0] - a[:, 1]) / 2
            return float(np.mean(mid ** 2) - np.mean(side ** 2))
        self.assertGreater(tone_energy(render.render_agreement([ent])), 10 * max(tone_energy(render.render_agreement([opp])), 1e-6))


if __name__ == "__main__":
    unittest.main()
