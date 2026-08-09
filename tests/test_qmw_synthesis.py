from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

try:
    from qiskit.quantum_info import Operator
except ImportError:  # pragma: no cover - optional project dependency
    Operator = None

from qmw.synthesis import (
    analyze_synthesis_state,
    load_clifford_qasm2,
    project_frame_to_tonnetz,
    project_frame_to_wilson_cps,
    synthesize_clifford,
    synthesize_evolution,
    synthesize_permutation,
    synthesize_qft,
    synthesize_unitary,
)


@unittest.skipIf(Operator is None, "Qiskit is not installed")
class QMWSynthesisTests(unittest.TestCase):
    def assert_round_trip(self, result) -> None:
        source = np.asarray(Operator(result.source_circuit).data)
        rebuilt = np.asarray(Operator(result.composer_circuit.to_qiskit_circuit()).data)
        overlap = np.vdot(source.reshape(-1), rebuilt.reshape(-1))
        phase = overlap / abs(overlap) if abs(overlap) else 1.0
        np.testing.assert_allclose(source, phase.conjugate() * rebuilt, atol=1e-9)

    def test_qft_enters_composer_basis(self) -> None:
        result = synthesize_qft(3)
        self.assertEqual(result.kind, "qft")
        self.assertTrue(result.composer_circuit.operations)
        self.assert_round_trip(result)

    def test_state_trajectory_metrics_are_physical_and_normalized(self) -> None:
        result = synthesize_qft(3)
        frames = analyze_synthesis_state(result, initial_basis_index=3)

        self.assertEqual(len(frames), result.qiskit_circuit.size())
        self.assertTrue(all(0.0 <= frame.expected_basis_index <= 7.0 for frame in frames))
        self.assertTrue(all(0 <= frame.dominant_basis_index <= 7 for frame in frames))
        self.assertTrue(all(0.0 <= frame.normalized_coherence <= 1.0 for frame in frames))
        self.assertTrue(all(0.0 <= frame.population_entropy <= 1.0 for frame in frames))
        self.assertTrue(all(0.0 <= frame.mean_qubit_entropy <= 1.0 for frame in frames))
        self.assertTrue(all(-np.pi <= frame.relative_phase <= np.pi for frame in frames))
        tonnetz_frames = analyze_synthesis_state(
            synthesize_qft(4), initial_basis_index=5
        )
        for frame in tonnetz_frames:
            nodes = project_frame_to_tonnetz(frame)
            self.assertAlmostEqual(sum(node.probability for node in nodes), 1.0)
            self.assertTrue(
                all(
                    node.pitch_offset
                    == 7 * node.fifth_coordinate + 4 * node.third_coordinate
                    for node in nodes
                )
            )

        wilson_nodes = project_frame_to_wilson_cps(tonnetz_frames[0])
        by_basis = {node.basis_index: node for node in wilson_nodes}
        self.assertEqual(len(wilson_nodes), 16)
        self.assertEqual(sum(node.cps_grade == 2 for node in wilson_nodes), 6)
        self.assertEqual(by_basis[3].factors, (1, 3))
        self.assertEqual(by_basis[3].complement_basis_index, 12)
        self.assertEqual(by_basis[12].complement_basis_index, 3)
        self.assertTrue(all(1.0 <= node.ratio < 2.0 for node in wilson_nodes))

    def test_line_permutation_enters_composer_basis(self) -> None:
        result = synthesize_permutation([2, 0, 1], topology="line")
        self.assertEqual(result.metadata["pattern"], [2, 0, 1])
        self.assert_round_trip(result)

    def test_unitary_enters_composer_basis(self) -> None:
        matrix = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
        result = synthesize_unitary(matrix)
        self.assert_round_trip(result)

    def test_seeded_clifford_enters_composer_basis(self) -> None:
        from qiskit.quantum_info import Operator, random_clifford

        target = random_clifford(3, seed=23)
        result = synthesize_clifford(target, method="greedy")

        self.assertEqual(result.kind, "clifford")
        self.assertEqual(result.metadata["method"], "greedy")
        self.assert_round_trip(result)
        target_matrix = np.asarray(target.to_operator().data)
        result_matrix = np.asarray(Operator(result.qiskit_circuit).data)
        overlap = np.vdot(target_matrix.reshape(-1), result_matrix.reshape(-1))
        phase = overlap / abs(overlap) if abs(overlap) else 1.0
        np.testing.assert_allclose(
            target_matrix,
            phase.conjugate() * result_matrix,
            atol=1e-9,
        )

    def test_clifford_accepts_a_compatible_circuit(self) -> None:
        from qiskit import QuantumCircuit

        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        result = synthesize_clifford(circuit)

        self.assertEqual(result.metadata["method"], "auto")
        self.assert_round_trip(result)

    def test_clifford_qasm_loader_discards_final_measurements(self) -> None:
        path = Path(__file__).parent / (
            "qac_quantumsonification_bridge_v1/example_qac_bell_4q.qasm"
        )
        result = synthesize_clifford(load_clifford_qasm2(path))

        self.assertEqual(result.metadata["clifford_qubits"], 4)
        self.assertNotIn("measure", result.summary()["operations"])
        self.assert_round_trip(result)

    def test_pauli_evolution_enters_composer_basis(self) -> None:
        result = synthesize_evolution(
            [("XX", 0.7), ("ZI", 0.2)],
            0.5,
            method="suzuki_trotter",
            reps=2,
            order=2,
        )
        self.assertEqual(result.metadata["method"], "suzuki_trotter")
        self.assert_round_trip(result)

    def test_summary_and_qasm_are_available(self) -> None:
        result = synthesize_qft(2, approximation_degree=1)
        self.assertEqual(result.summary()["qubits"], 2)
        self.assertIn("OPENQASM 3", result.qasm3())


if __name__ == "__main__":
    unittest.main()
