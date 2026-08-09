"""Tests for Phase-3 quantum-memory resonance and oracle generation."""

from __future__ import annotations

import unittest

import numpy as np

from feedback.quantum_memory import QuantumMemory
from feedback.quantum_memory_oracle_v1 import (
    MemoryOracleConfig,
    ResonanceWeights,
    build_quantum_memory_oracle,
    density_fidelity,
    pauli_coefficient_similarity,
    resonance_metrics,
    score_quantum_memory,
    trace_distance,
)
from hamiltonian.hamiltonian_state import HamiltonianState


def ket_density(index: int, dimension: int = 4) -> np.ndarray:
    ket = np.zeros(dimension, dtype=np.complex128)
    ket[index] = 1.0
    return np.outer(ket, ket.conj())


class QuantumMemoryOracleV1Tests(unittest.TestCase):
    def test_density_metrics_distinguish_identical_and_orthogonal_states(self) -> None:
        zero = ket_density(0)
        one = ket_density(1)
        self.assertAlmostEqual(density_fidelity(zero, zero), 1.0)
        self.assertAlmostEqual(trace_distance(zero, zero), 0.0)
        self.assertAlmostEqual(pauli_coefficient_similarity(zero, zero), 1.0)
        self.assertAlmostEqual(density_fidelity(zero, one), 0.0)
        self.assertAlmostEqual(trace_distance(zero, one), 1.0)
        self.assertAlmostEqual(pauli_coefficient_similarity(zero, one), 0.0)

    def test_bures_entropy_and_coherence_metrics_are_normalized(self) -> None:
        plus = np.ones(4, dtype=np.complex128) / 2.0
        metrics = resonance_metrics(plus, np.eye(4) / 4.0)
        for key, value in metrics.as_dict().items():
            if key == "bures_distance" or value is None:
                continue
            self.assertGreaterEqual(value, 0.0, key)
            self.assertLessEqual(value, 1.0, key)
        self.assertGreaterEqual(metrics.bures_distance, 0.0)
        self.assertLessEqual(metrics.bures_distance, np.sqrt(2.0))

    def test_memory_scoring_selects_closest_state(self) -> None:
        memory = QuantumMemory(decay=0.7)
        memory.encode(ket_density(0), events=["target"])
        memory.encode(ket_density(1), events=["other"])
        memory.encode(np.eye(4) / 4.0, events=["mixed"])
        matches = score_quantum_memory(
            memory,
            ket_density(0),
            config=MemoryOracleConfig(recency_decay=0.0),
        )
        self.assertEqual(matches[0].snapshot.events, ["target"])
        self.assertAlmostEqual(matches[0].resonance, 1.0)

    def test_recency_breaks_equal_resonance_ties(self) -> None:
        memory = QuantumMemory()
        memory.encode(ket_density(2), events=["old"])
        memory.encode(ket_density(2), events=["new"])
        matches = score_quantum_memory(memory, ket_density(2))
        self.assertEqual(matches[0].snapshot.events, ["new"])
        self.assertGreater(matches[0].selection_weight, matches[1].selection_weight)

    def test_context_metrics_affect_hamiltonian_and_trajectory_similarity(self) -> None:
        memory = QuantumMemory()
        trajectory = {
            "trajectory_speed": 0.2,
            "trajectory_acceleration": 0.1,
            "trajectory_direction_change": 0.4,
        }
        memory.encode(
            ket_density(0),
            hamiltonian=HamiltonianState(1.0, 0.0, 0.0),
            metrics=trajectory,
            events=["context-match"],
        )
        memory.encode(
            ket_density(0),
            hamiltonian=HamiltonianState(-1.0, 0.0, 0.0),
            metrics={key: value * 8.0 for key, value in trajectory.items()},
            events=["context-miss"],
        )
        weights = ResonanceWeights(
            fidelity=0.0,
            trace=0.0,
            bures=0.0,
            entropy=0.0,
            coherence=0.0,
            pauli=0.0,
            hamiltonian=0.5,
            trajectory=0.5,
        )
        matches = score_quantum_memory(
            memory,
            ket_density(0),
            current_hamiltonian=HamiltonianState(1.0, 0.0, 0.0),
            current_metrics=trajectory,
            config=MemoryOracleConfig(weights=weights, recency_decay=0.0),
        )
        self.assertEqual(matches[0].snapshot.events, ["context-match"])
        self.assertAlmostEqual(matches[0].resonance, 1.0)

    def test_identical_pure_memory_generates_full_phase_reflection(self) -> None:
        target = ket_density(2)
        memory = QuantumMemory()
        memory.encode(target)
        result = build_quantum_memory_oracle(
            memory,
            target,
            config=MemoryOracleConfig(top_k=1, recency_decay=0.0),
        )
        expected = np.eye(4, dtype=np.complex128) - 2.0 * target
        np.testing.assert_allclose(result.oracle, expected, atol=1e-12)
        self.assertAlmostEqual(result.effective_strength, 1.0)

    def test_soft_oracle_is_unitary_and_preserves_density_spectrum(self) -> None:
        memory = QuantumMemory()
        memory.encode(0.8 * ket_density(0) + 0.2 * ket_density(1))
        memory.encode(0.6 * ket_density(0) + 0.4 * ket_density(2))
        current = 0.7 * ket_density(0) + 0.3 * ket_density(3)
        result = build_quantum_memory_oracle(memory, current)
        identity = np.eye(4)
        np.testing.assert_allclose(result.oracle.conj().T @ result.oracle, identity, atol=1e-12)
        eigenvalues = np.linalg.eigvalsh(result.resonance_generator)
        self.assertGreaterEqual(float(np.min(eigenvalues)), -1e-12)
        self.assertAlmostEqual(float(np.max(eigenvalues)), 1.0)
        after = result.apply(current)
        np.testing.assert_allclose(np.linalg.eigvalsh(after), np.linalg.eigvalsh(current), atol=1e-12)

    def test_nonresonant_threshold_returns_identity(self) -> None:
        memory = QuantumMemory()
        memory.encode(ket_density(0))
        result = build_quantum_memory_oracle(
            memory,
            ket_density(1),
            config=MemoryOracleConfig(minimum_resonance=0.95),
        )
        self.assertFalse(result.has_resonance)
        np.testing.assert_allclose(result.oracle, np.eye(4), atol=1e-12)
        self.assertEqual(result.effective_strength, 0.0)

    def test_multiple_nonorthogonal_memories_form_mixed_generator(self) -> None:
        plus = np.ones(4, dtype=np.complex128) / 2.0
        query_ket = plus + np.array([1.0, 0.0, 0.0, 0.0])
        query_ket /= np.linalg.norm(query_ket)
        memory = QuantumMemory()
        memory.encode(ket_density(0))
        memory.encode(plus)
        result = build_quantum_memory_oracle(
            memory,
            np.outer(query_ket, query_ket.conj()),
            config=MemoryOracleConfig(top_k=2, minimum_resonance=0.0, recency_decay=0.0),
        )
        eigenvalues = np.linalg.eigvalsh(result.memory_mixture)
        self.assertGreater(np.count_nonzero(eigenvalues > 1e-10), 1)
        self.assertEqual(len(result.selected_matches), 2)

    def test_empty_memory_returns_inactive_identity_oracle(self) -> None:
        result = build_quantum_memory_oracle(QuantumMemory(), ket_density(0))
        self.assertFalse(result.has_resonance)
        np.testing.assert_allclose(result.oracle, np.eye(4), atol=1e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
