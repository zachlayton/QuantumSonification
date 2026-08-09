from __future__ import annotations

import pathlib
import sys
import unittest

import numpy as np

MODULE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))

from qmw_iching_dynamic_density_oracle8_v3 import (  # noqa: E402
    CHANGE_QUBITS,
    DIM,
    HEXAGRAM_QUBITS,
    DynamicIChingDensityOracle,
    entropy,
    index_from_lines,
    lines_from_index,
    reduced_density_matrix,
)


class DynamicDensityOracleTests(unittest.TestCase):
    def test_observe_is_non_destructive_and_complete(self) -> None:
        oracle = DynamicIChingDensityOracle(seed=1)
        before = oracle.density_matrix()
        frame = oracle.observe()
        np.testing.assert_array_equal(oracle.density_matrix(), before)
        self.assertAlmostEqual(sum(frame.hexagram_probabilities), 1.0, places=12)
        self.assertEqual(len(frame.hexagram_probabilities), 64)
        self.assertEqual(len(frame.moving_probabilities), 6)
        self.assertEqual(len(frame.pauli81_values), 81)
        self.assertEqual(len(frame.pauli81_labels), 81)
        self.assertIn(frame.dominant_pauli_word, frame.pauli81_values)

    def test_physical_invariants_survive_evolution(self) -> None:
        oracle = DynamicIChingDensityOracle(seed=2)
        oracle.evolve(0.02, steps=2)
        frame = oracle.observe()
        self.assertLess(frame.trace_error, 1e-10)
        self.assertLess(frame.hermiticity_error, 1e-10)
        self.assertGreaterEqual(frame.minimum_eigenvalue, -1e-9)
        self.assertLessEqual(frame.purity, 1.0 + 1e-9)

    def test_pure_complement_entropies_match(self) -> None:
        rng = np.random.default_rng(3)
        state = rng.normal(size=DIM) + 1j * rng.normal(size=DIM)
        state /= np.linalg.norm(state)
        rho = np.outer(state, state.conj())
        s_lu = entropy(reduced_density_matrix(rho, HEXAGRAM_QUBITS))
        s_c = entropy(reduced_density_matrix(rho, CHANGE_QUBITS))
        self.assertAlmostEqual(s_lu, s_c, places=10)

    def test_line_ontology_xor_and_traditional_values(self) -> None:
        for index in range(64):
            self.assertEqual(index_from_lines(lines_from_index(index)), index)
        oracle = DynamicIChingDensityOracle(seed=4)
        result = oracle.consult()
        self.assertEqual(result.H1, [a ^ b for a, b in zip(result.H0, result.M)])
        self.assertEqual(len(result.traditional_lines), 6)
        self.assertTrue(set(result.traditional_lines) <= {6, 7, 8, 9})
        for line, moving, traditional in zip(result.H0, result.M, result.traditional_lines):
            expected = 9 if line and moving else 7 if line else 6 if moving else 8
            self.assertEqual(traditional, expected)

    def test_consultation_collapses_hexagram_subspace(self) -> None:
        oracle = DynamicIChingDensityOracle(seed=5)
        result = oracle.consult()
        rho = oracle.density_matrix()
        support = [i for i in range(DIM) if (i & 0x3F) == result.h0_index]
        complement = [i for i in range(DIM) if (i & 0x3F) != result.h0_index]
        self.assertAlmostEqual(float(np.trace(rho).real), 1.0, places=12)
        self.assertLess(np.linalg.norm(rho[np.ix_(complement, range(DIM))]), 1e-12)
        self.assertGreater(float(np.trace(rho[np.ix_(support, support)]).real), 0.999999)

    def test_open_and_mixed_state_behavior(self) -> None:
        oracle = DynamicIChingDensityOracle(
            seed=6, dephasing_rate=0.2, damping_rate=0.1
        )
        oracle.set_density_matrix(np.eye(DIM, dtype=np.complex128) / DIM)
        initial = oracle.observe()
        self.assertAlmostEqual(initial.purity, 1.0 / DIM, places=12)
        self.assertAlmostEqual(initial.entropy_hexagram, 6.0, places=10)
        oracle.evolve(0.005)
        evolved = oracle.observe()
        self.assertLess(evolved.trace_error, 1e-10)
        self.assertGreaterEqual(evolved.minimum_eigenvalue, -1e-9)

    def test_mlx_agrees_when_installed(self) -> None:
        try:
            import mlx.core  # noqa: F401
        except ImportError:
            self.skipTest("MLX is not installed")
        numpy_oracle = DynamicIChingDensityOracle(backend="numpy", seed=7)
        mlx_oracle = DynamicIChingDensityOracle(
            backend="mlx", seed=7, allow_backend_fallback=False
        )
        numpy_oracle.evolve(0.005)
        mlx_oracle.evolve(0.005)
        np.testing.assert_allclose(
            mlx_oracle.density_matrix(), numpy_oracle.density_matrix(), atol=3e-5, rtol=3e-5
        )
        np_frame, mx_frame = numpy_oracle.observe(), mlx_oracle.observe()
        np.testing.assert_allclose(
            mx_frame.hexagram_probabilities,
            np_frame.hexagram_probabilities,
            atol=3e-5,
        )
        np.testing.assert_allclose(
            list(mx_frame.pauli81_values.values()),
            list(np_frame.pauli81_values.values()),
            atol=5e-5,
        )


if __name__ == "__main__":
    unittest.main()
