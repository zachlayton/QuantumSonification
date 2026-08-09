#!/usr/bin/env python3
import pathlib
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import qmw_iching_gauge_bridge_v1 as gauge
from qmw_iching_dynamic_density_oracle8_v3 import reduced_density_matrix


def random_density(seed=17):
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=256) + 1j * rng.normal(size=256)
    vector /= np.linalg.norm(vector)
    return np.outer(vector, vector.conj())


class IChingGaugeBridgeTests(unittest.TestCase):
    def test_complex64_trace_roundoff_is_normalized(self):
        state = np.ones(256, dtype=np.complex64) / np.sqrt(np.float32(256))
        rho = np.outer(state, state.conj()).astype(np.complex64)
        rho *= np.float32(0.9999995)
        reduced = gauge.hexagram_density_matrix(rho)
        self.assertAlmostEqual(float(np.trace(reduced).real), 1.0, places=12)

    @classmethod
    def setUpClass(cls):
        cls.rho8 = random_density()
        cls.snapshot = gauge.build_gauge_snapshot(
            cls.rho8, (0.25, 0.35, 0.45, 0.55, 0.65, 0.75)
        )

    def test_hexagram_partial_trace_matches_v3(self):
        expected = reduced_density_matrix(self.rho8, tuple(range(6)))
        actual = gauge.hexagram_density_matrix(self.rho8)
        np.testing.assert_allclose(actual, expected, atol=1e-12)
        self.assertAlmostEqual(float(np.trace(actual).real), 1.0, places=12)

    def test_q6_has_192_single_line_edges(self):
        edges = gauge.build_hexagram_hypercube()
        self.assertEqual(len(edges), 192)
        self.assertEqual(len(set(edges)), 192)
        for source, target, line in edges:
            self.assertEqual((source ^ target).bit_count(), 1)
            self.assertEqual(source ^ target, 1 << (line - 1))

    def test_magnetic_laplacian_uses_absolute_degree_and_is_psd(self):
        adjacency, laplacian = self.snapshot.adjacency, self.snapshot.laplacian
        self.assertTrue(np.allclose(adjacency, adjacency.conj().T, atol=1e-12))
        self.assertTrue(np.allclose(laplacian, laplacian.conj().T, atol=1e-12))
        np.testing.assert_allclose(np.diag(laplacian).real,
                                   np.sum(np.abs(adjacency), axis=1), atol=1e-12)
        self.assertGreaterEqual(float(np.linalg.eigvalsh(laplacian).min()), -1e-10)

    def test_all_240_canonical_plaquettes_are_unique(self):
        plaquettes = self.snapshot.plaquettes
        self.assertEqual(len(plaquettes), 240)
        self.assertEqual(len({(p.base, p.line_a, p.line_b) for p in plaquettes}), 240)
        for line_a in range(1, 7):
            for line_b in range(line_a + 1, 7):
                group = [p for p in plaquettes if p.line_a == line_a and p.line_b == line_b]
                self.assertEqual(len(group), 16)
                for item in group:
                    self.assertFalse(item.base & (1 << (line_a - 1)))
                    self.assertFalse(item.base & (1 << (line_b - 1)))

    def test_all_plaquette_fluxes_are_gauge_invariant(self):
        rng = np.random.default_rng(91)
        phases = rng.uniform(-np.pi, np.pi, 64)
        transform = np.exp(1j * phases)
        changed = transform[:, None].conj() * self.snapshot.adjacency * transform[None, :]
        before = self.snapshot.plaquettes
        after = gauge.square_cycle_fluxes(changed)
        np.testing.assert_allclose(
            [item.flux_radians for item in before],
            [item.flux_radians for item in after], atol=1e-11,
        )
        np.testing.assert_allclose(
            [item.strength for item in before],
            [item.strength for item in after], atol=1e-12,
        )

    def test_descriptors_cover_15_pairs_and_low_spectrum(self):
        descriptors = self.snapshot.descriptors
        self.assertEqual(descriptors.plaquette_count, 240)
        self.assertEqual(len(self.snapshot.line_pairs), 15)
        self.assertTrue(all(pair.count == 16 for pair in self.snapshot.line_pairs))
        self.assertEqual(len(descriptors.low_laplacian_eigenvalues), 8)
        self.assertGreaterEqual(descriptors.laplacian_minimum_eigenvalue, -1e-10)
        self.assertGreaterEqual(descriptors.circular_variance, 0.0)
        self.assertLessEqual(descriptors.circular_variance, 1.0 + 1e-12)
        self.assertGreaterEqual(descriptors.strongest_plaquette_index, 0)
        self.assertLess(descriptors.strongest_plaquette_index, 240)


if __name__ == "__main__":
    unittest.main()
