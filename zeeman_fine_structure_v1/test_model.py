from __future__ import annotations

import unittest

import numpy as np

from zeeman_fine_structure_v1.engine_bridge import ZeemanFineLayer, attach, detach
from zeeman_fine_structure_v1.model import (
    PRESETS,
    S_Z,
    ZeemanFineConfig,
    diagonalise,
    dipole_pattern,
    directivity_ambisonics,
    frame,
    hamiltonian,
    hanle_polarization,
    merge_lines,
    quantum_beats,
    sweep,
)


def sigma_lines(cfg, b, rel=1e-3):
    merged = [m for m in merge_lines(frame(cfg, b).lines, tol_hz=1e-6) if m[0] == "sigma"]
    total = sum(s for _, _, s in merged)
    return [(f, s / total) for _, f, s in merged if s / total > rel]


class ZeemanFineTests(unittest.TestCase):
    def test_hermitian_and_conserves_magnetisation(self):
        h = hamiltonian(PRESETS["anomalous"], 2.5)
        self.assertTrue(np.allclose(h, h.conj().T))
        self.assertTrue(np.allclose(h @ S_Z, S_Z @ h))

    def test_normal_zeeman_pascal_degeneracies(self):
        cfg = ZeemanFineConfig(g=(2.0,) * 4, coupling_hz=0.0)
        e, _, _ = diagonalise(hamiltonian(cfg, 1.0))
        values, counts = np.unique(np.round(e, 9), return_counts=True)
        self.assertEqual(list(counts), [1, 4, 6, 4, 1])
        self.assertTrue(np.allclose(np.diff(values), 2.0 * 40.0))

    def test_larmor_theorem_equal_g_single_sigma_line(self):
        cfg = PRESETS["normal"]  # coupling on, equal g
        lines = sigma_lines(cfg, 3.0)
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(lines[0][0], 2.0 * 3.0 * 40.0, places=6)

    def test_anomalous_splits_sigma_line(self):
        self.assertGreater(len(sigma_lines(PRESETS["anomalous"], 3.0)), 1)

    def test_free_spins_flip_at_own_g(self):
        lines = sigma_lines(PRESETS["free_spins"], 2.0)
        freqs = sorted(round(f, 6) for f, _ in lines)
        expected = sorted(round(g * 2.0 * 40.0, 6) for g in PRESETS["free_spins"].g)
        self.assertEqual(freqs, expected)

    def test_weak_field_strongest_line_uses_mean_g(self):
        cfg = ZeemanFineConfig(g=PRESETS["anomalous"].g, coupling_hz=200.0)
        b = 0.05
        f, _ = max(sigma_lines(cfg, b), key=lambda item: item[1])
        mean_g = float(np.mean(cfg.g))
        self.assertAlmostEqual(f / (b * 40.0), mean_g, delta=0.02)

    def test_strong_field_approaches_individual_g(self):
        cfg = PRESETS["anomalous"]
        b = 200.0
        freqs = [f / (b * 40.0) for f, s in sigma_lines(cfg, b, rel=0.02)]
        for g in cfg.g:
            self.assertLess(min(abs(x - g) for x in freqs), 0.01)

    def test_sweep_tracking_is_continuous(self):
        frames = sweep(PRESETS["anomalous"], np.linspace(0.0, 4.0, 400))
        e = np.array([fr.energies_hz for fr in frames])
        self.assertLess(np.max(np.abs(np.diff(e, axis=0))), 2.0)
        m = np.array([fr.magnetisation for fr in frames])
        self.assertTrue(np.all(m == m[0]))

    def test_directivity_sum_rule_and_ambisonics(self):
        c = np.linspace(-1, 1, 101)
        total = dipole_pattern("pi", c) + 2 * dipole_pattern("sigma", c)
        self.assertTrue(np.allclose(total, 2.0))
        pi = directivity_ambisonics("pi")
        sigma = directivity_ambisonics("sigma")
        self.assertAlmostEqual(pi[0], 1.0)
        self.assertTrue(np.allclose(pi[1:4], 0.0, atol=1e-3))
        self.assertAlmostEqual(pi[6], -0.2, places=2)
        self.assertAlmostEqual(sigma[6], 0.1, places=2)
        tilted = directivity_ambisonics("pi", (1.0, 0.0, 0.0))
        self.assertLess(tilted[8], 0.0)  # pattern now minimal along x

    def test_hanle_half_polarisation(self):
        cfg = PRESETS["normal"]
        tau, g = 0.01, 2.0
        b_half = 1.0 / (2.0 * 2 * np.pi * g * cfg.hz_per_tesla * tau)
        self.assertAlmostEqual(float(hanle_polarization(cfg, 0.0, g, tau)), 1.0)
        self.assertAlmostEqual(float(hanle_polarization(cfg, b_half, g, tau)), 0.5)

    def test_quantum_beats_precess_at_larmor(self):
        cfg = ZeemanFineConfig(g=(2.0,) * 4, coupling_hz=6.0)
        sr, b = 8000, 2.0
        sig = quantum_beats(cfg, b, 2.0, sr, decay_hz=0.0)
        spectrum = np.abs(np.fft.rfft(sig))
        peak = np.fft.rfftfreq(sig.size, 1 / sr)[np.argmax(spectrum)]
        self.assertAlmostEqual(peak, 2.0 * b * 40.0, delta=1.0)

    def test_engine_bridge_adds_and_restores(self):
        class Dummy:
            def hamiltonian(self):
                return np.eye(16, dtype=np.complex128)

        eng = Dummy()
        layer = attach(eng, ZeemanFineLayer(field_t=1.0))
        self.assertTrue(np.allclose(eng.hamiltonian(), np.eye(16) + layer.operator()))
        layer.set_field(0.0)
        layer.set_coupling(0.0)
        self.assertTrue(np.allclose(eng.hamiltonian(), np.eye(16)))
        detach(eng)
        self.assertTrue(np.allclose(eng.hamiltonian(), np.eye(16)))


if __name__ == "__main__":
    unittest.main()
