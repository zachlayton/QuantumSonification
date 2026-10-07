from __future__ import annotations

import unittest

import numpy as np
from qiskit import QuantumCircuit

from qmw_qiskit_bridge_v1 import QMWOperator, StatevectorProvider
from qmw_qiskit_bridge_v1.hamiltonian import expectation_trajectory


class OperatorTests(unittest.TestCase):
    def test_q0_is_rightmost_pauli_symbol(self) -> None:
        op = QMWOperator.from_mapping("X_q0", {"IX": 1})
        expected = np.kron(np.eye(2), np.array([[0, 1], [1, 0]]))
        np.testing.assert_allclose(op.matrix(), expected)

    def test_rejects_mixed_width(self) -> None:
        with self.assertRaisesRegex(ValueError, "same width"):
            QMWOperator.from_mapping("bad", {"X": 1, "ZZ": 1})


class StatevectorTests(unittest.TestCase):
    def test_bell_expectations_and_correlations(self) -> None:
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        observables = [
            QMWOperator.from_mapping("Z0", {"IZ": 1}),
            QMWOperator.from_mapping("ZZ", {"ZZ": 1}),
        ]
        frame = StatevectorProvider(seed=7).run_expectations(circuit, observables)
        self.assertAlmostEqual(frame.expectations["Z0"], 0.0, places=12)
        self.assertAlmostEqual(frame.expectations["ZZ"], 1.0, places=12)
        self.assertAlmostEqual(frame.variances["ZZ"], 0.0, places=12)

    def test_sampling_is_seeded(self) -> None:
        circuit = QuantumCircuit(1)
        circuit.h(0)
        a = StatevectorProvider(seed=19).run_samples(circuit, shots=64)
        b = StatevectorProvider(seed=19).run_samples(circuit, shots=64)
        self.assertEqual(a.samples, b.samples)
        self.assertEqual(sum(a.samples.values()), 64)

    def test_material_frame_maps_are_immutable(self) -> None:
        frame = StatevectorProvider().run_expectations(
            QuantumCircuit(1), [QMWOperator.from_mapping("Z", {"Z": 1})]
        )
        with self.assertRaises(TypeError):
            frame.expectations["Z"] = 0  # type: ignore[index]


class HamiltonianTests(unittest.TestCase):
    def test_x_rotation_matches_cosine_z_trajectory(self) -> None:
        hamiltonian = QMWOperator.from_mapping("H", {"X": 0.5})
        observable = QMWOperator.from_mapping("Z", {"Z": 1})
        times = np.linspace(0, np.pi, 7)
        frames = expectation_trajectory(
            StatevectorProvider(), hamiltonian, [observable], times, reps=2
        )
        actual = np.array([frame.expectations["Z"] for frame in frames])
        np.testing.assert_allclose(actual, np.cos(times), atol=1e-10)
        np.testing.assert_allclose([frame.time for frame in frames], times)


if __name__ == "__main__":
    unittest.main()
