"""Ideal Qiskit checks for the optimized 64-state IBM circuit."""

from __future__ import annotations

import unittest

from qmw_entangled_history_clock16_v1.ibm_history_clock64 import (
    build_compiled_history_circuit64,
    build_history_circuit64,
    build_measurement_circuits64,
    ideal_validation,
)


class IBMHistoryClock64Tests(unittest.TestCase):
    def test_optimized_circuit_matches_numpy_history(self):
        report = ideal_validation()
        self.assertEqual(report["qubits"], 10)
        self.assertEqual(report["joint_amplitudes"], 1024)
        self.assertLess(report["statevector_max_error"], 1e-11)
        self.assertLess(report["compiled_statevector_max_error"], 1e-11)
        self.assertLess(report["clock_qft_probability_max_error"], 1e-11)

    def test_binary_power_circuit_uses_structured_controlled_gates(self):
        circuit = build_history_circuit64()
        operations = circuit.count_ops()
        self.assertEqual(operations["h"], 6)
        self.assertEqual(operations["crx"], 4)
        self.assertEqual(operations["crz"], 4)
        self.assertEqual(sum(
            count for name, count in operations.items() if "rzz" in name
        ), 18)
        self.assertNotIn("unitary", operations)

    def test_closed_form_hardware_compilation_is_exact_and_shallow(self):
        circuit = build_compiled_history_circuit64()
        operations = circuit.count_ops()
        self.assertEqual(operations["h"], 6)
        self.assertEqual(operations["p"], 6)
        self.assertEqual(operations["cx"], 4)
        self.assertLessEqual(circuit.depth(), 7)

    def test_two_targeted_measurement_circuits(self):
        circuits = build_measurement_circuits64()
        self.assertEqual(set(circuits), {"computational", "clock_fourier"})
        self.assertTrue(all(circuit.num_qubits == 10 for circuit in circuits.values()))


if __name__ == "__main__":
    unittest.main()
