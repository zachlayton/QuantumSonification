import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import qmw_iching_oracle8_v2 as oracle
from qmw_iching_ibm_compare_v1 import (
    build_measurement_circuits,
    IBMComparisonService,
    compact_count_key,
    compare_counts,
    correlation_from_counts,
    moving_probabilities_from_counts,
    publish_comparison,
    qiskit_parity,
    reading_from_data,
    run_aer,
)


class FakeClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, values):
        self.messages.append((address, values))


class FakeAudioPlayer:
    def __init__(self):
        self.calls = []

    def play(self, comparison, output_path):
        self.calls.append((comparison, Path(output_path)))


class TestIChingIBMCompareV1(unittest.TestCase):
    def test_qiskit_translation_matches_existing_oracle(self):
        parity = qiskit_parity(seed=42, depth=3)
        self.assertAlmostEqual(parity["state_fidelity"], 1.0, places=11)
        self.assertLess(parity["max_probability_error"], 1e-12)

    def test_four_measurement_families(self):
        circuits = build_measurement_circuits(seed=42, depth=1)
        self.assertEqual(tuple(circuits), ("cast", "zx", "xz", "yy"))
        self.assertTrue(all(circuit.num_qubits == 8 for circuit in circuits.values()))
        self.assertTrue(all(circuit.num_clbits == 8 for circuit in circuits.values()))

    def test_count_bit_order_and_correlations(self):
        counts = {"00000000": 3, "01000001": 1}
        self.assertEqual(compact_count_key("0000 0001"), "00000001")
        self.assertAlmostEqual(correlation_from_counts(counts, 0, 6), 1.0)
        self.assertAlmostEqual(correlation_from_counts(counts, 0, 7), 0.5)

    def test_shared_sampling_is_deterministic(self):
        state = oracle.build(42, 1)
        distribution = np.abs(state) ** 2
        moving = oracle.moving_probs(state)
        first = reading_from_data(42, distribution, moving)
        second = reading_from_data(42, distribution, moving)
        self.assertEqual(first, second)

    def test_local_route_reproduces_the_frozen_oracle_reading(self):
        reading, state, _rho, _reduced, _field = oracle.consult(42, depth=3)
        route = reading_from_data(42, np.abs(state) ** 2, oracle.moving_probs(state))
        self.assertEqual(route.primary, reading.primary_binary)
        self.assertEqual(route.moving_mask, reading.moving_mask)
        self.assertEqual(route.transformed, reading.transformed_binary)

    def test_aer_comparison_is_close_to_ideal(self):
        comparison, counts = run_aer(seed=42, depth=1, shots=8192)
        self.assertEqual(set(counts), {"cast", "zx", "xz", "yy"})
        self.assertLess(comparison.primary_tvd, 0.12)
        self.assertGreater(comparison.primary_hellinger_fidelity, 0.96)
        self.assertLess(comparison.moving_probability_mae, 0.06)

    def test_comparison_is_published_as_one_atomic_frame(self):
        comparison, _counts = run_aer(seed=42, depth=1, shots=2048)
        client = FakeClient()
        publish_comparison(client, revision=77, comparison=comparison)
        self.assertEqual(
            [address.rsplit("/", 1)[-1] for address, _values in client.messages],
            ["begin", "reading", "metrics", "moving", "end"],
        )
        self.assertTrue(all(values[0] == 77 for _address, values in client.messages))
        self.assertEqual(len(client.messages[3][1]), 13)

    def test_service_hands_completed_comparison_to_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(
                confirm_ibm=False, shots=1024, account="unused", backend=None,
                save_dir=Path(directory),
            )
            visual, stop, audio = FakeClient(), FakeClient(), FakeAudioPlayer()
            service = IBMComparisonService(args, visual, audio, stop)
            service._lock.acquire()
            service._run(revision=81, seed=42, depth=1)
            self.assertEqual(stop.messages, [("/qmw/iching/audio/stop", [81])])
            self.assertEqual(len(audio.calls), 1)
            self.assertEqual(audio.calls[0][1].name, "comparison-sonification-v1.wav")
            self.assertTrue(any(address.endswith("/end") for address, _ in visual.messages))


if __name__ == "__main__":
    unittest.main()
