from __future__ import annotations

import unittest

from qiskit import QuantumCircuit

from qmw_qiskit_bridge_v1 import AerProvider, QMWOperator


class AerTests(unittest.TestCase):
    def test_expectation_and_sampling_share_frame_contract(self) -> None:
        circuit = QuantumCircuit(1)
        provider = AerProvider(shots=2048, seed=11)
        z = QMWOperator.from_mapping("Z", {"Z": 1})
        expectation = provider.run_expectations(circuit, [z], time=0.25)
        samples = provider.run_samples(circuit, shots=128, time=0.25)
        self.assertAlmostEqual(expectation.expectations["Z"], 1.0, places=12)
        self.assertEqual(samples.samples, {"0": 128})
        self.assertEqual(expectation.time, samples.time)


if __name__ == "__main__":
    unittest.main()
