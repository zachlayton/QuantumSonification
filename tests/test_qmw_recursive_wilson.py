from __future__ import annotations

import unittest

try:
    import qiskit  # noqa: F401
except ImportError:  # pragma: no cover
    qiskit = None

from qmw.recursive_wilson import HEXANY_MASKS, RecursiveWilsonEngine, hexany_voices


@unittest.skipIf(qiskit is None, "Qiskit is not installed")
class RecursiveWilsonTests(unittest.TestCase):
    def test_exchange_recursion_stays_in_hexany_shell(self) -> None:
        engine = RecursiveWilsonEngine(seed=7, temperature=0.7, max_depth=8)
        steps = [engine.next() for _ in range(8)]

        self.assertTrue(all(abs(step.shell_probability - 1.0) < 1e-10 for step in steps))
        self.assertTrue(all(step.qubits[0] != step.qubits[1] for step in steps))
        shell_probability, voices = hexany_voices(engine.state)
        self.assertAlmostEqual(shell_probability, 1.0)
        self.assertEqual({voice.basis_index for voice in voices}, set(HEXANY_MASKS))

    def test_seed_makes_recursion_replayable(self) -> None:
        first = RecursiveWilsonEngine(seed=19, temperature=1.1, max_depth=4)
        second = RecursiveWilsonEngine(seed=19, temperature=1.1, max_depth=4)

        first_steps = [first.next() for _ in range(4)]
        second_steps = [second.next() for _ in range(4)]
        self.assertEqual(first_steps, second_steps)

    def test_exchange_reports_directed_probability_flow(self) -> None:
        engine = RecursiveWilsonEngine(seed=23, temperature=0.65, max_depth=1)
        step = engine.next()

        self.assertTrue(step.flows)
        exchange_mask = (1 << step.qubits[0]) | (1 << step.qubits[1])
        for flow in step.flows:
            self.assertIn(flow.source_basis_index, HEXANY_MASKS)
            self.assertIn(flow.destination_basis_index, HEXANY_MASKS)
            self.assertEqual(
                flow.source_basis_index ^ flow.destination_basis_index,
                exchange_mask,
            )
            self.assertGreater(flow.conditional_probability_flow, 0.0)
            self.assertLessEqual(flow.conditional_probability_flow, 1.0)
        self.assertTrue(step.basis_flows)
        self.assertGreater(step.basis_flows[0].probability_flow, 0.0)

    def test_programmer_gate_reports_cross_shell_flow(self) -> None:
        engine = RecursiveWilsonEngine(seed=5)
        flows = engine.apply_gate("h", (1,))

        self.assertTrue(flows)
        strongest = flows[0]
        self.assertEqual(strongest.source_basis_index, 0b0101)
        self.assertEqual(strongest.destination_basis_index, 0b0111)
        self.assertAlmostEqual(strongest.probability_flow, 0.5)

    def test_phase_gate_has_no_false_probability_flow(self) -> None:
        engine = RecursiveWilsonEngine(seed=5)
        flows = engine.apply_gate("z", (0,))
        self.assertEqual(flows, ())

    def test_result_transpiles_to_supported_qmw_basis(self) -> None:
        engine = RecursiveWilsonEngine(seed=3, max_depth=2)
        engine.next()
        engine.next()
        result = engine.synthesis_result()

        self.assertEqual(result.kind, "recursive_wilson_hexany")
        self.assertTrue(result.composer_circuit.operations)
        self.assertNotIn("xx_plus_yy", result.qiskit_circuit.count_ops())

    def test_programmer_circuit_starts_from_zero_not_hidden_probe(self) -> None:
        engine = RecursiveWilsonEngine(seed=5)
        engine.load_qasm2(
            "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[4]; z q[0];"
        )
        shell_probability, _ = hexany_voices(engine.state)
        self.assertAlmostEqual(shell_probability, 0.0)
        self.assertAlmostEqual(abs(engine.state.data[0]) ** 2, 1.0)


if __name__ == "__main__":
    unittest.main()
