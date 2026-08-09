from __future__ import annotations

import math
import unittest

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, random_unitary

from qmw.euler import (
    decompose_one_qubit,
    decompose_qiskit_circuit,
    euler_osc_messages,
)


class OneQubitEulerTests(unittest.TestCase):
    def test_random_unitary_round_trips_with_visual_scalar(self) -> None:
        matrix = random_unitary(2, seed=23).data
        result = decompose_one_qubit(matrix)

        self.assertTrue(result.verified)
        np.testing.assert_allclose(
            result.reconstruct(),
            matrix,
            atol=1e-10,
        )
        lam, theta, phi = result.visual_phases
        self.assertAlmostEqual(lam, result.lam)
        self.assertAlmostEqual(theta, result.theta)
        self.assertAlmostEqual(phi, result.phi)
        self.assertAlmostEqual(
            result.zx_scalar_phase,
            result.gamma
            - 0.5 * (result.phi + result.theta + result.lam),
        )

    def test_phase_gate_keeps_global_phase(self) -> None:
        phase = np.diag([1.0, 1.0j]).astype(complex)
        result = decompose_one_qubit(phase)

        self.assertTrue(result.verified)
        self.assertAlmostEqual(result.theta, 0.0)
        np.testing.assert_allclose(result.reconstruct(), phase, atol=1e-12)

    def test_all_euler_bases_serialize_temporal_axes(self) -> None:
        matrix = random_unitary(2, seed=41).data
        for basis in ("ZXZ", "ZYZ", "XYX", "XZX"):
            with self.subTest(basis=basis):
                result = decompose_one_qubit(matrix, basis=basis)
                payload = result.to_dict()
                self.assertEqual(
                    payload["visual_axes"],
                    list(reversed(basis)),
                )
                self.assertTrue(math.isfinite(payload["zx_scalar_phase"]))
                np.testing.assert_allclose(
                    result.reconstruct(),
                    matrix,
                    atol=1e-10,
                )

    def test_nonunitary_matrix_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not unitary"):
            decompose_one_qubit(np.array([[1, 1], [0, 1]], dtype=complex))

    def test_circuit_report_marks_nonlocal_and_measurement_operations(self) -> None:
        circuit = QuantumCircuit(2, 1, name="euler-test")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.ry(math.pi / 7, 1)
        circuit.measure(0, 0)

        report = decompose_qiskit_circuit(circuit)

        self.assertEqual(
            [(item.operation, item.qubit) for item in report.decompositions],
            [("h", 0), ("ry", 1)],
        )
        self.assertEqual(
            [(item.operation, item.reason) for item in report.skipped],
            [
                ("cx", "not a one-qubit instruction"),
                ("measure", "classical or measurement instruction"),
            ],
        )
        for item in report.decompositions:
            expected = Operator(
                circuit.data[item.instruction_index].operation
            ).data
            np.testing.assert_allclose(
                item.decomposition.reconstruct(),
                expected,
                atol=1e-10,
            )

    def test_osc_transaction_is_atomic_and_bounded(self) -> None:
        circuit = QuantumCircuit(1)
        circuit.h(0)
        circuit.rz(math.pi / 5, 0)
        report = decompose_qiskit_circuit(circuit)
        messages = list(euler_osc_messages(report, revision=41))

        self.assertEqual(messages[0][0], "/qmw/circuit/euler/begin")
        self.assertEqual(messages[-1][0], "/qmw/circuit/euler/end")
        self.assertEqual(
            [address for address, _payload in messages].count(
                "/qmw/circuit/euler/gate"
            ),
            2,
        )
        self.assertEqual(messages[1][1][0], 41)
        self.assertEqual(len(messages[1][1]), 11)


if __name__ == "__main__":
    unittest.main()
