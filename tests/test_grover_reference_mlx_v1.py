"""Tests for the exact MLX Grover reference implementation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import mlx.core as mx
import numpy as np

from grover_reference_mlx_v1 import (
    basis_index,
    compare_with_qiskit,
    diffusion_operator,
    optimal_iteration_count,
    oracle_operator,
    plot_amplitude_amplification,
    run_grover,
    theoretical_success_probability,
)


class GroverReferenceMLXV1Tests(unittest.TestCase):
    def test_basis_labels_use_qiskit_order(self) -> None:
        self.assertEqual(basis_index("101", 3), 5)
        self.assertEqual(basis_index(5, 3), 5)
        with self.assertRaises(ValueError):
            basis_index("01", 3)

    def test_oracle_and_diffusion_are_unitary_reflections(self) -> None:
        oracle = oracle_operator(3, "101")
        diffusion = diffusion_operator(3)
        identity = mx.eye(8, dtype=mx.float32).astype(mx.complex64)
        mx.eval(oracle, diffusion, identity)
        np.testing.assert_allclose(np.asarray(oracle @ oracle), identity, atol=1e-6)
        np.testing.assert_allclose(
            np.asarray(diffusion @ diffusion), identity, atol=1e-6
        )
        self.assertAlmostEqual(float(np.asarray(oracle)[5, 5].real), -1.0)

    def test_three_qubit_search_amplifies_marked_state(self) -> None:
        result = run_grover(3, "101")
        self.assertEqual(result.iterations, 2)
        self.assertAlmostEqual(result.marked_probabilities[0], 1.0 / 8.0, places=6)
        self.assertAlmostEqual(result.success_probability, 121.0 / 128.0, places=6)
        self.assertEqual(int(np.argmax(np.abs(np.asarray(result.final_state)) ** 2)), 5)

    def test_matrix_free_step_matches_explicit_operators(self) -> None:
        result = run_grover(3, "101", iterations=1)
        initial = result.states[0]
        explicit = diffusion_operator(3) @ (oracle_operator(3, "101") @ initial)
        mx.eval(explicit)
        np.testing.assert_allclose(result.final_state, explicit, atol=1e-6)

    def test_probability_history_matches_closed_form(self) -> None:
        result = run_grover(5, ["00011", "10101"], iterations=4)
        expected = [
            theoretical_success_probability(5, 2, step) for step in range(5)
        ]
        np.testing.assert_allclose(result.marked_probabilities, expected, atol=2e-6)

    def test_arbitrary_qubit_counts_and_default_iterations(self) -> None:
        for n_qubits in (2, 3, 4, 6):
            with self.subTest(n_qubits=n_qubits):
                result = run_grover(n_qubits, (1 << n_qubits) - 1)
                self.assertEqual(
                    result.iterations, optimal_iteration_count(n_qubits)
                )
                norm = np.linalg.norm(np.asarray(result.final_state))
                self.assertAlmostEqual(float(norm), 1.0, places=5)

    def test_qiskit_reference_matches_mlx(self) -> None:
        result = run_grover(4, ["0011", "1100"], iterations=2)
        comparison = compare_with_qiskit(result)
        self.assertGreater(comparison["state_fidelity"], 1.0 - 2e-6)
        self.assertLess(comparison["max_amplitude_error"], 2e-6)
        self.assertLess(comparison["probability_l1_error"], 2e-6)

    def test_plot_is_written(self) -> None:
        result = run_grover(3, "101", iterations=3)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "amplification.png"
            self.assertEqual(plot_amplitude_amplification(result, output), output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 1_000)

    def test_invalid_requests_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_grover(0, 0)
        with self.assertRaises(ValueError):
            run_grover(2, [])
        with self.assertRaises(ValueError):
            run_grover(2, [0, 1, 2, 3])
        with self.assertRaises(ValueError):
            run_grover(2, 0, iterations=-1)
        with self.assertRaises(ValueError):
            optimal_iteration_count(3, 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
