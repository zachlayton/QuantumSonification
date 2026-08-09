from __future__ import annotations

import json
import unittest

from qmw.synthesis import SynthesisOSCPublisher, synthesize_qft
from qmw_circuit_bridge import QMWCircuitBridge


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class LoopbackLoadClient(RecordingClient):
    def __init__(self, bridge: QMWCircuitBridge) -> None:
        super().__init__()
        self.bridge = bridge
        self.handlers = {
            "/qmw/circuit/load/begin": bridge._osc_load_begin,
            "/qmw/circuit/load/op": bridge._osc_load_operation,
            "/qmw/circuit/load/metadata": bridge._osc_load_metadata,
            "/qmw/circuit/load/commit": bridge._osc_load_commit,
            "/qmw/circuit/load/abort": bridge._osc_load_abort,
        }

    def send_message(self, address: str, value: object) -> None:
        super().send_message(address, value)
        handler = self.handlers[address]
        args = value if isinstance(value, list) else [value]
        handler(address, *args)


class SynthesisOSCProtocolTests(unittest.TestCase):
    def make_bridge(self, n_qubits: int = 2) -> tuple[QMWCircuitBridge, RecordingClient]:
        bridge = QMWCircuitBridge(n_qubits=n_qubits, n_steps=16)
        output = RecordingClient()
        bridge.client._sock.close()
        bridge.client = output
        return bridge, output

    def test_load_is_not_visible_before_commit(self) -> None:
        bridge, _ = self.make_bridge()
        original_names = [op.name for op in bridge.registry_circuit.operations]

        bridge._osc_load_begin("/begin", 100, 2, 0, 2, "test")
        bridge._osc_load_operation("/op", 100, 0, "h", "0", "", "")
        bridge._osc_load_operation("/op", 100, 1, "cx", "0,1", "", "")

        self.assertEqual(
            [op.name for op in bridge.registry_circuit.operations],
            original_names,
        )
        bridge._osc_load_commit("/commit", 100)
        self.assertEqual(
            [op.name for op in bridge.registry_circuit.operations],
            ["h", "cx"],
        )

    def test_publisher_round_trips_complete_score_through_receiver(self) -> None:
        bridge, output = self.make_bridge()
        result = synthesize_qft(2)
        loopback = LoopbackLoadClient(bridge)

        revision = SynthesisOSCPublisher(client=loopback).publish(
            result,
            revision=101,
        )

        self.assertEqual(revision, 101)
        self.assertEqual(
            [op.name for op in bridge.registry_circuit.operations],
            [op.name for op in result.composer_circuit.operations],
        )
        self.assertEqual(bridge._circuit_load_revision, 101)
        self.assertEqual(bridge._last_circuit_load_metadata["kind"], "qft")
        self.assertEqual(loopback.messages[0][0], "/qmw/circuit/load/begin")
        self.assertEqual(loopback.messages[-1], ("/qmw/circuit/load/commit", 101))
        self.assertIn(
            "/qmw/circuit/load/accepted",
            [address for address, _ in output.messages],
        )

    def test_incomplete_and_stale_loads_are_rejected(self) -> None:
        bridge, output = self.make_bridge()
        bridge._osc_load_begin("/begin", 200, 2, 0, 2, "test")
        bridge._osc_load_operation("/op", 200, 0, "h", "0", "", "")
        bridge._osc_load_commit("/commit", 200)
        self.assertEqual(output.messages[-1][0], "/qmw/circuit/load/error")

        bridge._pending_circuit_load = None
        bridge._circuit_load_revision = 200
        bridge._osc_load_begin("/begin", 199, 2, 0, 0, "test")
        self.assertEqual(output.messages[-1][0], "/qmw/circuit/load/error")

    def test_metadata_must_be_revisioned_json_object(self) -> None:
        bridge, output = self.make_bridge()
        bridge._osc_load_begin("/begin", 300, 2, 0, 0, "test")
        bridge._osc_load_metadata("/metadata", 300, json.dumps({"voice": "gold"}))
        bridge._osc_load_commit("/commit", 300)
        self.assertEqual(bridge._last_circuit_load_metadata, {"voice": "gold"})

        bridge._osc_load_begin("/begin", 301, 2, 0, 0, "test")
        bridge._osc_load_metadata("/metadata", 301, "[]")
        self.assertEqual(output.messages[-1][0], "/qmw/circuit/load/error")


if __name__ == "__main__":
    unittest.main()
