from __future__ import annotations

import json
import unittest
from pathlib import Path

from qmw_pauli_basis_laboratory_v2.bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
)
from qmw_pauli_basis_laboratory_v2.laboratory import run_basis_laboratory

from .osc_service import BasisLaboratoryOSCPublisher, basis_from_name


ROOT = Path(__file__).resolve().parents[1]
MAX_PATCH = ROOT / "max" / "QMW_Pauli_Basis_Laboratory_v3.maxpat"


class CaptureClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, list[object]]] = []

    def send_message(self, address: str, payload: list[object]) -> None:
        self.messages.append((address, payload))


class BasisMenuTests(unittest.TestCase):
    def test_v3_menu_constructs_all_supported_operators(self) -> None:
        self.assertIsInstance(basis_from_name("identity"), IdentityBasis)
        self.assertIsInstance(basis_from_name("hadamard"), HadamardBasis)
        self.assertIsInstance(basis_from_name("qft"), QFTBasis)
        inverse = basis_from_name("inverse_qft")
        self.assertIsInstance(inverse, QFTBasis)
        self.assertTrue(inverse.inverse)
        self.assertIsInstance(
            basis_from_name("hamiltonian"),
            HamiltonianEigenbasis,
        )

    def test_unknown_basis_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown basis"):
            basis_from_name("epistrophe")


class PairedPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_basis_laboratory(
            QFTBasis(),
            preset="ghz",
            shots=32,
            seed=19,
        )

    def test_publication_is_two_complete_full4q_transactions(self) -> None:
        publisher = BasisLaboratoryOSCPublisher(packet_delay_ms=0)
        capture = CaptureClient()
        publisher.tomography.client._sock.close()
        publisher.tomography.client = capture

        revisions = publisher.publish(self.result, 700)
        self.assertEqual(revisions, (700, 701))

        by_address: dict[str, list[list[object]]] = {}
        for address, payload in capture.messages:
            by_address.setdefault(address, []).append(payload)

        root = "/qmw/tomography"
        self.assertEqual(len(by_address[f"{root}/begin"]), 2)
        self.assertEqual(len(by_address[f"{root}/setting"]), 162)
        self.assertEqual(len(by_address[f"{root}/pauli"]), 510)
        self.assertEqual(len(by_address[f"{root}/shell"]), 10)
        self.assertEqual(len(by_address[f"{root}/metrics"]), 2)
        self.assertEqual(len(by_address[f"{root}/end"]), 2)

        begins = by_address[f"{root}/begin"]
        self.assertEqual(
            [(row[0], row[1], row[3]) for row in begins],
            [
                (700, "basis_computational", "identity"),
                (701, "basis_experimental", "qft"),
            ],
        )
        ends = by_address[f"{root}/end"]
        self.assertEqual(ends, [[700, 81, 255], [701, 81, 255]])

        addresses = [address for address, _payload in capture.messages]
        first_end = addresses.index(f"{root}/end")
        second_begin = addresses.index(f"{root}/begin", 1)
        self.assertLess(first_end, second_begin)


class MaxArtifactTests(unittest.TestCase):
    def test_generated_patch_is_v3_and_keeps_two_surfaces(self) -> None:
        document = json.loads(MAX_PATCH.read_text(encoding="utf-8"))
        boxes = [
            item["box"]
            for item in document["patcher"]["boxes"]
        ]
        texts = {box.get("text", "") for box in boxes}
        ids = {box["id"] for box in boxes}

        self.assertIn("o.pack /qmw/basis/run", texts)
        self.assertIn("udpreceive 7436", texts)
        self.assertIn(
            "js qmw_pauli_basis_laboratory_receiver_v3.js",
            texts,
        )
        self.assertIn("computational_heatmap", ids)
        self.assertIn("experimental_heatmap", ids)
        self.assertIn("difference_paulis", ids)
        self.assertEqual(
            sum(box["maxclass"] == "jit.pwindow" for box in boxes),
            2,
        )


if __name__ == "__main__":
    unittest.main()
