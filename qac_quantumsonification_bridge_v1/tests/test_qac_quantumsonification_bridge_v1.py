import importlib.util
import math
import sys
import unittest
from pathlib import Path
from urllib.parse import quote

import numpy as np


MODULE_PATH = Path(__file__).parents[1] / "qac_quantumsonification_bridge_v1.py"
SPEC = importlib.util.spec_from_file_location("qac_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
qac = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qac
SPEC.loader.exec_module(qac)


BELL_QASM2 = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


class QACBridgeTests(unittest.TestCase):
    def test_qasm2_bell_state_and_quantum_material(self):
        circuit = qac.parse_qasm(BELL_QASM2)
        frame = qac.analyze(circuit, 7, shots=0)
        expected = np.zeros(16, dtype=np.complex128)
        expected[0] = expected[3] = 1 / math.sqrt(2)
        np.testing.assert_allclose(frame.statevector, expected, atol=1e-12)
        np.testing.assert_allclose(frame.bloch[0], [0, 0, 0], atol=1e-12)
        np.testing.assert_allclose(frame.bloch[1], [0, 0, 0], atol=1e-12)
        np.testing.assert_allclose(frame.bloch[2], [0, 0, 1], atol=1e-12)
        self.assertAlmostEqual(frame.mutual_information["01"], 2.0)
        self.assertAlmostEqual(frame.pauli["IIXX"], 1.0)
        self.assertAlmostEqual(frame.pauli["IIZZ"], 1.0)
        self.assertAlmostEqual(frame.purity, 1.0)
        self.assertEqual(len(frame.pauli), 34)

    def test_qasm3_rotations_and_lsb_ordering(self):
        qasm3 = """
        OPENQASM 3.0;
        include "stdgates.inc";
        qubit[4] q;
        bit[4] c;
        rx(pi) q[0];
        ry(pi/2) q[2];
        c[0] = measure q[0];
        """
        frame = qac.analyze(qac.parse_qasm(qasm3), 1, shots=0)
        self.assertAlmostEqual(frame.probabilities[1], 0.5)
        self.assertAlmostEqual(frame.probabilities[5], 0.5)
        np.testing.assert_allclose(frame.bloch[0], [0, 0, -1], atol=1e-12)
        np.testing.assert_allclose(frame.bloch[2], [1, 0, 0], atol=1e-12)
        self.assertIsNotNone(frame.euler)
        assert frame.euler is not None
        self.assertEqual(
            [(item.operation, item.qubit) for item in frame.euler.decompositions],
            [("rx", 0), ("ry", 2)],
        )
        self.assertTrue(frame.euler.verified)

    def test_chunk_transfer_and_revision_rejection(self):
        core = qac.BridgeCore(shots=0)
        encoded = quote(BELL_QASM2, safe="")
        midpoint = len(encoded) // 2
        chunks = [encoded[:midpoint], encoded[midpoint:]]
        core.begin(4, len(chunks))
        for index, chunk in enumerate(chunks):
            core.chunk(4, index, len(chunks), chunk)
        frame = core.end(4)
        self.assertEqual(frame.revision, 4)
        with self.assertRaisesRegex(qac.QASMError, "Stale revision"):
            core.submit(BELL_QASM2, 3)

    def test_gate_family_and_measurements_parse(self):
        source = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[4]; creg c[4];
        x q[0]; y q[1]; z q[2]; s q[0]; sdg q[0]; t q[1]; tdg q[1];
        u3(pi/2, pi/3, -pi/4) q[3];
        cz q[0],q[2]; swap q[1],q[3]; ccx q[0],q[1],q[2];
        measure q[3] -> c[3];
        """
        circuit = qac.parse_qasm(source)
        state = qac.simulate(circuit)
        self.assertAlmostEqual(float(np.linalg.norm(state)), 1.0)
        self.assertEqual(circuit.measurements, ((3, 3),))
        report = qac.circuit_euler_report(circuit)
        self.assertEqual(
            len(report.decompositions),
            sum(len(operation.qubits) == 1 for operation in circuit.operations),
        )
        self.assertIn(
            ("measure", "classical or measurement instruction"),
            [(item.operation, item.reason) for item in report.skipped],
        )

    def test_frame_json_carries_shared_euler_data(self):
        frame = qac.analyze(qac.parse_qasm(BELL_QASM2), 9, shots=0)
        payload = qac.frame_to_json(frame)

        self.assertEqual(payload["euler"]["basis"], "ZXZ")
        self.assertEqual(
            payload["euler"]["decompositions"][0]["operation"],
            "h",
        )
        decomposition = payload["euler"]["decompositions"][0]["decomposition"]
        self.assertIn("theta", decomposition)
        self.assertIn("phi", decomposition)
        self.assertIn("lambda", decomposition)
        self.assertIn("gamma", decomposition)
        self.assertIn("zx_scalar_phase", decomposition)

    def test_osc_publish_sends_euler_to_main_and_processing_mirror(self):
        class Capture:
            def __init__(self):
                self.messages = []

            def send_message(self, address, payload):
                self.messages.append((address, payload))

        bridge = qac.QACOSCBridge.__new__(qac.QACOSCBridge)
        bridge.client = Capture()
        bridge.euler_client = Capture()
        bridge.engine_client = None
        frame = qac.analyze(qac.parse_qasm(BELL_QASM2), 17, shots=0)

        bridge.publish(frame)

        main_addresses = [address for address, _ in bridge.client.messages]
        mirror_addresses = [
            address for address, _ in bridge.euler_client.messages
        ]
        self.assertIn("/qmw/circuit/euler/begin", main_addresses)
        self.assertIn("/qmw/circuit/euler/gate", main_addresses)
        self.assertIn("/qmw/circuit/euler/end", main_addresses)
        self.assertEqual(
            mirror_addresses,
            [
                "/qmw/circuit/euler/begin",
                "/qmw/circuit/euler/gate",
                "/qmw/circuit/euler/end",
            ],
        )

    def test_rejects_wrong_qubit_count_and_unsafe_angle(self):
        with self.assertRaisesRegex(qac.QASMError, "Expected 4 qubits"):
            qac.parse_qasm("OPENQASM 2.0; qreg q[2]; h q[0];")
        with self.assertRaisesRegex(qac.QASMError, "Unsupported angle"):
            qac.parse_qasm("OPENQASM 2.0; qreg q[4]; rx(__import__('os')) q[0];")


if __name__ == "__main__":
    unittest.main()
