from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import numpy as np

from full4q_tomography_v1.engine import (
    PAULI_LABELS,
    SETTINGS,
    reconstruct_tomography,
    simulate_tomography,
    tomography_result_from_dict,
)
from full4q_tomography_v1.osc_service import TomographyOSCPublisher, save_result
from full4q_tomography_v1.ibm_runner import build_measurement_circuits, counts_row


class Full4QTomographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_tomography(
            preset="ghz", transform="none", shots=256, seed=23
        )

    def test_combinatorics(self) -> None:
        self.assertEqual(len(SETTINGS), 81)
        self.assertEqual(len(set(SETTINGS)), 81)
        self.assertEqual((SETTINGS[0], SETTINGS[-1]), ("XXXX", "ZZZZ"))
        self.assertEqual(len(PAULI_LABELS), 256)
        self.assertEqual(len(set(PAULI_LABELS)), 256)
        shell_counts = Counter(label.count("X") + label.count("Y") + label.count("Z")
                               for label in PAULI_LABELS)
        self.assertEqual([shell_counts[i] for i in range(5)], [1, 12, 54, 108, 81])

    def test_ibm_circuit_batch_matches_score_order(self) -> None:
        circuits = build_measurement_circuits("ghz", "none")
        self.assertEqual(len(circuits), 81)
        self.assertEqual(circuits[0].name, "qmw_00_XXXX")
        self.assertEqual(circuits[-1].name, "qmw_80_ZZZZ")
        self.assertTrue(all(circuit.num_qubits == 4 for circuit in circuits))
        self.assertTrue(all(circuit.num_clbits == 4 for circuit in circuits))

    def test_ibm_count_key_conversion(self) -> None:
        row = counts_row({"0000": 120, "1111": 136})
        self.assertEqual(row[0], 120)
        self.assertEqual(row[15], 136)
        self.assertEqual(sum(row), 256)

    def test_all_histograms_have_exact_shot_count(self) -> None:
        self.assertEqual(len(self.result.settings), 81)
        for setting in self.result.settings:
            self.assertEqual(len(setting.counts), 16)
            self.assertEqual(sum(setting.counts), 256)
        self.assertEqual(self.result.total_shots, 20_736)

    def test_ghz_stabilizers(self) -> None:
        expectations = {
            pauli.label: pauli.expectation for pauli in self.result.paulis
        }
        self.assertAlmostEqual(expectations["XXXX"], 1.0)
        self.assertAlmostEqual(expectations["ZZII"], 1.0)
        self.assertAlmostEqual(expectations["IZZI"], 1.0)
        self.assertAlmostEqual(expectations["IIZZ"], 1.0)

    def test_density_products_are_well_formed(self) -> None:
        linear = np.array(self.result.density_linear_real) + 1j * np.array(
            self.result.density_linear_imag
        )
        physical = np.array(self.result.density_physical_real) + 1j * np.array(
            self.result.density_physical_imag
        )
        self.assertEqual(linear.shape, (16, 16))
        self.assertAlmostEqual(float(np.real(np.trace(linear))), 1.0)
        self.assertAlmostEqual(float(np.real(np.trace(physical))), 1.0)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(physical))), -1e-10)

    def test_reconstructs_hardware_shaped_count_rows(self) -> None:
        reconstructed = reconstruct_tomography(
            [setting.counts for setting in self.result.settings],
            preset="ghz",
            transform="none",
            shots=256,
            source="ibm_hardware",
        )
        self.assertEqual(reconstructed.source, "ibm_hardware")
        self.assertEqual(reconstructed.total_shots, 20_736)
        self.assertEqual(
            [pauli.expectation for pauli in reconstructed.paulis],
            [pauli.expectation for pauli in self.result.paulis],
        )

    def test_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "result.json"
            save_result(self.result, destination)
            payload = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "qmw.full4q.tomography.v1")
        self.assertEqual(len(payload["settings"]), 81)
        self.assertEqual(len(payload["paulis"]), 256)
        restored = tomography_result_from_dict(payload)
        self.assertEqual(restored.source, self.result.source)
        self.assertEqual(restored.settings[80].counts, self.result.settings[80].counts)

    def test_osc_transaction_shape(self) -> None:
        messages: list[tuple[str, list[object]]] = []

        class CaptureClient:
            def send_message(self, address: str, payload: list[object]) -> None:
                messages.append((address, payload))

        publisher = TomographyOSCPublisher(packet_delay_ms=0)
        publisher.client._sock.close()
        publisher.client = CaptureClient()
        publisher.publish(self.result, revision=77)

        addresses = Counter(address for address, _payload in messages)
        self.assertEqual(addresses["/qmw/tomography/begin"], 1)
        self.assertEqual(addresses["/qmw/tomography/setting"], 81)
        self.assertEqual(addresses["/qmw/tomography/pauli"], 255)
        self.assertEqual(addresses["/qmw/tomography/shell"], 5)
        self.assertEqual(addresses["/qmw/tomography/metrics"], 1)
        self.assertEqual(addresses["/qmw/tomography/end"], 1)
        self.assertEqual(messages[0][1][0], 77)
        self.assertEqual(messages[-1][1], [77, 81, 255])


if __name__ == "__main__":
    unittest.main()
