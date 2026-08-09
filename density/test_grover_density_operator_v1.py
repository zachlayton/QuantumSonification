"""Tests for density-matrix Grover amplitude amplification."""

from __future__ import annotations

import math
import unittest

import numpy as np

from density.grover_density_operator_v1 import (
    DecoherenceConfig,
    GroverDensityOperator,
    apply_continuous_decoherence,
    diffusion_operator,
    marked_projector,
    oracle_operator,
    run_density_grover,
    uniform_density,
)


class GroverDensityOperatorV1Tests(unittest.TestCase):
    def test_projector_marks_multiple_basis_states(self) -> None:
        projector = marked_projector(3, ["001", "101"])
        self.assertEqual(float(np.trace(projector).real), 2.0)
        np.testing.assert_array_equal(np.diag(projector).real, [0, 1, 0, 0, 0, 1, 0, 0])
        np.testing.assert_allclose(projector @ projector, projector, atol=1e-12)

    def test_partial_oracle_is_a_continuous_unitary_phase(self) -> None:
        identity_oracle = oracle_operator(2, "11", strength=0.0)
        half_oracle = oracle_operator(2, "11", strength=0.5)
        full_oracle = oracle_operator(2, "11", strength=1.0)
        np.testing.assert_allclose(identity_oracle, np.eye(4), atol=1e-12)
        self.assertAlmostEqual(half_oracle[3, 3], -1j)
        self.assertAlmostEqual(full_oracle[3, 3], -1.0)
        np.testing.assert_allclose(half_oracle.conj().T @ half_oracle, np.eye(4), atol=1e-12)

    def test_full_strength_density_search_matches_grover_formula(self) -> None:
        result = run_density_grover(3, "101", 2, time_step=0.0)
        theta = math.asin(math.sqrt(1.0 / 8.0))
        expected = [math.sin((2 * step + 1) * theta) ** 2 for step in range(3)]
        np.testing.assert_allclose(
            [metrics.marked_probability for metrics in result.metrics],
            expected,
            atol=1e-12,
        )
        self.assertAlmostEqual(result.final_metrics.purity, 1.0, places=12)

    def test_partial_strength_produces_partial_amplification_without_mixing(self) -> None:
        partial = run_density_grover(
            3, "101", 1, oracle_strength=0.5, time_step=0.0
        )
        full = run_density_grover(3, "101", 1, time_step=0.0)
        initial_probability = 1.0 / 8.0
        self.assertGreater(partial.final_metrics.marked_probability, initial_probability)
        self.assertLess(
            partial.final_metrics.marked_probability,
            full.final_metrics.marked_probability,
        )
        self.assertAlmostEqual(partial.final_metrics.purity, 1.0, places=12)

    def test_multiple_marked_states_amplify_together(self) -> None:
        result = run_density_grover(4, ["0011", "1100"], 2, time_step=0.0)
        theta = math.asin(math.sqrt(2.0 / 16.0))
        expected = math.sin(5.0 * theta) ** 2
        self.assertAlmostEqual(result.final_metrics.marked_probability, expected, places=12)
        self.assertAlmostEqual(result.final_rho[3, 3].real, result.final_rho[12, 12].real)

    def test_decoherence_reduces_purity_and_coherence_continuously(self) -> None:
        clean = run_density_grover(3, "101", 2, time_step=0.2)
        noisy = run_density_grover(
            3,
            "101",
            2,
            time_step=0.2,
            decoherence=DecoherenceConfig(
                dephasing_rate=0.8,
                amplitude_damping_rate=0.25,
                depolarizing_rate=0.15,
            ),
        )
        self.assertLess(noisy.final_metrics.purity, clean.final_metrics.purity)
        self.assertLess(noisy.final_metrics.coherence_l1, clean.final_metrics.coherence_l1)
        self.assertAlmostEqual(noisy.final_metrics.trace, 1.0, places=12)
        self.assertGreaterEqual(noisy.final_metrics.minimum_eigenvalue, 0.0)

    def test_dephasing_rate_obeys_time_composition(self) -> None:
        rho = uniform_density(2)
        config = DecoherenceConfig(dephasing_rate=0.7)
        half_twice = apply_continuous_decoherence(
            apply_continuous_decoherence(rho, config, 0.3, 2), config, 0.3, 2
        )
        full_once = apply_continuous_decoherence(rho, config, 0.6, 2)
        np.testing.assert_allclose(half_twice, full_once, atol=1e-12)

    def test_hamiltonian_evolves_state_between_grover_steps(self) -> None:
        pauli_x_q0 = np.kron(np.eye(2), np.array([[0.0, 1.0], [1.0, 0.0]]))
        without_h = run_density_grover(2, "11", 1, time_step=0.25)
        with_h = run_density_grover(
            2,
            "11",
            1,
            time_step=0.25,
            hamiltonian=math.pi * pauli_x_q0,
        )
        self.assertFalse(np.allclose(with_h.final_rho, without_h.final_rho))
        self.assertAlmostEqual(with_h.final_metrics.purity, 1.0, places=12)

    def test_callable_hamiltonian_receives_iteration_and_state(self) -> None:
        calls: list[tuple[int, tuple[int, int]]] = []

        def hamiltonian(iteration: int, rho: np.ndarray) -> np.ndarray:
            calls.append((iteration, rho.shape))
            return np.zeros_like(rho)

        operator = GroverDensityOperator(2, "10", hamiltonian=hamiltonian, time_step=0.1)
        result = operator.run(None, 3)
        self.assertEqual(calls, [(1, (4, 4)), (2, (4, 4)), (3, (4, 4))])
        self.assertEqual(len(result.metrics), 4)

    def test_invalid_density_and_controls_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_density_grover(2, "11", -1)
        with self.assertRaises(ValueError):
            oracle_operator(2, "11", strength=1.1)
        with self.assertRaises(ValueError):
            DecoherenceConfig(dephasing_rate=-0.1)
        with self.assertRaises(ValueError):
            run_density_grover(2, "11", 1, initial_rho=np.eye(3))
        non_positive = np.diag([1.2, -0.2, 0.0, 0.0])
        with self.assertRaises(ValueError):
            run_density_grover(2, "11", 1, initial_rho=non_positive)

    def test_diffusion_is_a_unitary_reflection(self) -> None:
        diffusion = diffusion_operator(3)
        np.testing.assert_allclose(diffusion @ diffusion, np.eye(8), atol=1e-12)
        np.testing.assert_allclose(diffusion, diffusion.conj().T, atol=1e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
