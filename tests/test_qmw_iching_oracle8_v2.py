import itertools
import unittest

import numpy as np

import qmw_iching_oracle8_v2 as oracle


class TestLineOntology(unittest.TestCase):
    def test_traditional_values(self):
        expected = {(0, 1): 6, (1, 0): 7, (0, 0): 8, (1, 1): 9}
        self.assertEqual({key: oracle.line_ontology(*key)["value"] for key in expected}, expected)

    def test_change_is_xor(self):
        for primary, mask in itertools.product(range(64), repeat=2):
            self.assertEqual(oracle.apply_moving_mask(primary, mask), primary ^ mask)


class TestDensityMatrices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.psi = oracle.build(42, depth=1)
        cls.rho, cls.reduced, cls.entropy = oracle.density_diagnostics(cls.psi)

    def test_state_and_reduced_traces(self):
        self.assertAlmostEqual(np.linalg.norm(self.psi), 1.0, places=12)
        self.assertAlmostEqual(np.trace(self.rho).real, 1.0, places=12)
        for rho in self.reduced.values(): self.assertAlmostEqual(np.trace(rho).real, 1.0, places=12)

    def test_hermitian_positive_semidefinite(self):
        for rho in [self.rho, *self.reduced.values()]:
            self.assertTrue(np.allclose(rho, rho.conj().T, atol=1e-12))
            self.assertGreaterEqual(np.linalg.eigvalsh(rho).min(), -1e-10)

    def test_entropy_and_mutual_information_sanity(self):
        limits = {"S_L": 3, "S_U": 3, "S_C": 2, "S_LU": 6}
        for key, limit in limits.items():
            self.assertGreaterEqual(self.entropy[key], -1e-12)
            self.assertLessEqual(self.entropy[key], limit + 1e-10)
        self.assertGreaterEqual(self.entropy["I_L_U"], -1e-12)
        self.assertLessEqual(self.entropy["I_L_U"], 6 + 1e-10)


class TestPauliField(unittest.TestCase):
    def test_complete_distinct_81_word_field(self):
        winner, value, field = oracle.pauli81(oracle.build(7, depth=1))
        self.assertEqual(len(field), 81)
        self.assertEqual(set(field), {"".join(x) for x in itertools.product("XYZ", repeat=4)})
        self.assertIn(winner, field); self.assertEqual(value, field[winner])
        self.assertTrue(all(-1.0000001 <= v <= 1.0000001 for v in field.values()))


if __name__ == "__main__": unittest.main()
