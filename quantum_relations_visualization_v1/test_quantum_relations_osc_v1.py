import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from quantum_relations_visualization_v1.quantum_relations_osc_v1 import (
    QuantumRelationsOSC,
    RelationConfig,
)


class _RecordingClient:
    def __init__(self, *_args, **_kwargs):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class _Server:
    def __init__(self, address, _dispatcher):
        self.server_address = address

    def serve_forever(self):
        return None

    def shutdown(self):
        return None

    def server_close(self):
        return None


class QuantumRelationsOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.rho_path = Path(self.tempdir.name) / "rho.npz"
        ket = np.zeros(16, dtype=complex)
        ket[0] = ket[15] = 1.0 / np.sqrt(2.0)
        np.savez(self.rho_path, rho=np.outer(ket, ket.conj()))

        # Positional arguments preserve the original constructor contract.
        module = "quantum_relations_visualization_v1.quantum_relations_osc_v1"
        with (
            patch(f"{module}.SimpleUDPClient", _RecordingClient),
            patch(f"{module}.ThreadingOSCUDPServer", _Server),
        ):
            self.app = QuantumRelationsOSC(
                self.rho_path,
                "rho",
                "127.0.0.1",
                7450,
                "127.0.0.1",
                0,
                RelationConfig(measurement_mode="collapse", watch_file=False),
            )
        self.app.reply_port = 7451

    def tearDown(self):
        self.app.server.server_close()
        self.tempdir.cleanup()

    def test_legacy_measure_call_requests_engine_without_private_collapse(self):
        rho_before = self.app.rho.copy()
        request_id = self.app.measure("Z", "collapse")

        np.testing.assert_allclose(self.app.rho, rho_before)
        self.assertIn(request_id, self.app.pending_measurements)
        address, payload = self.app.state_client.messages[-1]
        self.assertEqual(address, "/quantum/state/control/measure")
        self.assertEqual(payload[:3], ["Z", "collapse", request_id])

    def test_legacy_control_address_remains_valid(self):
        self.app._process(
            "/quantum/relations/control/measure",
            ("X",),
        )
        address, payload = self.app.state_client.messages[-1]
        self.assertEqual(address, "/quantum/state/control/measure")
        self.assertEqual(payload[0], "X")
        self.assertEqual(payload[1], "collapse")

    def test_authoritative_result_republishes_legacy_visualization_messages(self):
        request_id = self.app.measure("Y", "probe")
        self.app._process(
            "/quantum/state/event/measurement",
            (
                request_id,
                7,
                14,
                14,
                "probe",
                "Y",
                9,
                "1001",
                0.184,
                0.0,
                0,
            ),
        )

        self.assertNotIn(request_id, self.app.pending_measurements)
        messages = dict(self.app.client.messages)
        self.assertEqual(messages["/quantum/measurement/outcome"], 9)
        self.assertEqual(messages["/quantum/measurement/bitstring"], "1001")
        self.assertEqual(messages["/quantum/measurement/mode"], "probe")
        self.assertEqual(messages["/quantum/measurement/flash"], 1)
        self.assertEqual(messages["/quantum/measurement/revision"], 14)

    def test_authoritative_rho_supersedes_file_fallback_and_rejects_stale_revision(self):
        collapsed = np.zeros((16, 16), dtype=complex)
        collapsed[9, 9] = 1.0
        payload = (
            15,
            16,
            *collapsed.real.reshape(-1),
            *collapsed.imag.reshape(-1),
        )
        self.app._process("/quantum/state/event/rho", payload)
        np.testing.assert_allclose(self.app.rho, collapsed)
        self.assertTrue(self.app.authoritative_state_active)
        self.assertEqual(self.app.authoritative_revision, 15)

        older = np.zeros((16, 16), dtype=complex)
        older[0, 0] = 1.0
        stale_payload = (
            14,
            16,
            *older.real.reshape(-1),
            *older.imag.reshape(-1),
        )
        self.app._process("/quantum/state/event/rho", stale_payload)
        np.testing.assert_allclose(self.app.rho, collapsed)


if __name__ == "__main__":
    unittest.main()
