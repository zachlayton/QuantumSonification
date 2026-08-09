from __future__ import annotations

import math
import unittest

import numpy as np

from qasm_circuit_bridge_v1 import ComposerCircuit

try:
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator
except ImportError:  # pragma: no cover - optional project dependency
    QuantumCircuit = None


@unittest.skipIf(QuantumCircuit is None, "Qiskit is not installed")
class QiskitComposerBridgeTests(unittest.TestCase):
    def assert_circuits_equivalent(self, left, right) -> None:
        left_unitary = np.asarray(Operator(left).data)
        right_unitary = np.asarray(Operator(right).data)
        overlap = np.vdot(left_unitary.reshape(-1), right_unitary.reshape(-1))
        phase = overlap / abs(overlap) if abs(overlap) else 1.0
        np.testing.assert_allclose(left_unitary, phase.conjugate() * right_unitary, atol=1e-10)

    def test_imports_and_round_trips_current_u_gate(self) -> None:
        source = QuantumCircuit(2)
        source.h(0)
        source.u(0.17, -0.31, 0.42, 1)
        source.cx(0, 1)

        score = ComposerCircuit.from_qiskit_circuit(source)

        self.assertEqual([op.name for op in score.operations], ["h", "u3", "cx"])
        self.assertEqual(score.n_bits, 0)
        self.assert_circuits_equivalent(source, score.to_qiskit_circuit())

    def test_legacy_u_family_targets_qiskit_2_api(self) -> None:
        score = ComposerCircuit(n_qubits=1, n_bits=0)
        score.add("u1", [0], [0.2])
        score.add("u2", [0], [0.3, 0.4])
        score.add("u3", [0], [0.5, 0.6, 0.7])

        circuit = score.to_qiskit_circuit()

        self.assertEqual([item.operation.name for item in circuit.data], ["p", "u", "u"])

    def test_preserves_named_classical_register_measurements(self) -> None:
        qreg = QuantumRegister(2, "voice")
        pitch = ClassicalRegister(1, "pitch")
        energy = ClassicalRegister(1, "energy")
        source = QuantumCircuit(qreg, pitch, energy)
        source.h(qreg[0])
        source.measure(qreg[0], pitch[0])
        source.measure(qreg[1], energy[0])

        score = ComposerCircuit.from_qiskit_circuit(source)
        rebuilt = score.to_qiskit_circuit()

        self.assertEqual(score.classical_register, "pitch")
        self.assertIn("energy", score.classical_registers)
        self.assertEqual(
            [op.classical_target for op in score.operations if op.name == "measure"],
            ["pitch[0]", "energy[0]"],
        )
        self.assertEqual(
            [op.measurement_route.target_register for op in score.operations if op.name == "measure"],
            ["pitch", "energy"],
        )
        self.assertEqual([register.name for register in rebuilt.cregs], ["pitch", "energy"])

    def test_symbolic_parameter_survives_round_trip(self) -> None:
        theta = Parameter("theta")
        source = QuantumCircuit(1)
        source.ry(theta, 0)

        score = ComposerCircuit.from_qiskit_circuit(source)
        rebuilt = score.to_qiskit_circuit()

        self.assertEqual(score.operations[0].params, ["theta"])
        self.assert_circuits_equivalent(
            source.assign_parameters({theta: math.pi / 7.0}),
            rebuilt.assign_parameters({next(iter(rebuilt.parameters)): math.pi / 7.0}),
        )

    def test_symbolic_expression_is_rejected_instead_of_changed(self) -> None:
        theta = Parameter("theta")
        source = QuantumCircuit(1)
        source.ry(2 * theta, 0)

        with self.assertRaisesRegex(ValueError, "not a bare parameter"):
            ComposerCircuit.from_qiskit_circuit(source)

    def test_barriers_are_ignored_by_default(self) -> None:
        source = QuantumCircuit(1)
        source.h(0)
        source.barrier()
        source.x(0)

        score = ComposerCircuit.from_qiskit_circuit(source)

        self.assertEqual([op.name for op in score.operations], ["h", "x"])

    def test_unsupported_instruction_has_actionable_error(self) -> None:
        source = QuantumCircuit(2)
        source.rxx(0.25, 0, 1)

        with self.assertRaisesRegex(ValueError, "rxx.*transpile"):
            ComposerCircuit.from_qiskit_circuit(source)

    def test_shared_euler_report_is_available_from_every_composer_score(self) -> None:
        score = ComposerCircuit(n_qubits=2, n_bits=0)
        score.add("h", [0])
        score.add("u3", [1], [0.2, -0.3, 0.4])
        score.add("cx", [0, 1])

        report = score.euler_decomposition_report()
        messages = score.euler_osc_messages(revision=73)

        self.assertEqual(
            [item.operation for item in report.decompositions],
            ["h", "u"],
        )
        self.assertEqual(
            [(item.operation, item.reason) for item in report.skipped],
            [("cx", "not a one-qubit instruction")],
        )
        self.assertEqual(messages[0][0], "/qmw/circuit/euler/begin")
        self.assertEqual(messages[-1][0], "/qmw/circuit/euler/end")


if __name__ == "__main__":
    unittest.main()
