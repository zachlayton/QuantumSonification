from __future__ import annotations

import threading
import unittest

import numpy as np

from density.live_gate_injection import apply_live_gate
from qac_quantumsonification_bridge_v1.qac_quantumsonification_bridge_v1 import (
    BridgeCore,
    QACOSCBridge,
)


def basis_density(index: int, dimension: int = 16) -> np.ndarray:
    state = np.zeros(dimension, dtype=np.complex128)
    state[index] = 1.0
    return np.outer(state, state.conj())


class RecordingClient:
    def __init__(self) -> None:
        self.messages = []

    def send_message(self, address, value) -> None:
        self.messages.append((address, value))


class LiveGateMathTests(unittest.TestCase):
    def test_q0_is_engine_most_significant_axis(self) -> None:
        result, delta = apply_live_gate(basis_density(0), "x", [0])
        self.assertGreater(delta, 0.0)
        self.assertAlmostEqual(float(result[8, 8].real), 1.0)

    def test_h_then_cx_creates_qac_q0_q1_bell_pair(self) -> None:
        rho, _ = apply_live_gate(basis_density(0), "h", [0])
        rho, _ = apply_live_gate(rho, "cx", [0, 1])
        self.assertAlmostEqual(float(rho[0, 0].real), 0.5)
        self.assertAlmostEqual(float(rho[12, 12].real), 0.5)
        self.assertAlmostEqual(float(rho[0, 12].real), 0.5)

    def test_gate_preserves_mixed_state_spectrum(self) -> None:
        rng = np.random.default_rng(19)
        matrix = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
        rho = matrix @ matrix.conj().T
        rho /= np.trace(rho).real
        before = np.linalg.eigvalsh(rho)
        after, delta = apply_live_gate(rho, "h", [3])
        self.assertGreater(delta, 0.0)
        np.testing.assert_allclose(np.linalg.eigvalsh(after), before, atol=1e-10)


class LiveGateRelayTests(unittest.TestCase):
    def make_bridge(self) -> QACOSCBridge:
        bridge = object.__new__(QACOSCBridge)
        bridge.core = BridgeCore(expected_qubits=4, shots=0)
        bridge.client = RecordingClient()
        bridge.engine_client = RecordingClient()
        bridge.live_gate_revision = -1
        bridge.live_gate_lock = threading.RLock()
        return bridge

    def test_bridge_relays_revisioned_gate_in_q0_lsb_semantics(self) -> None:
        bridge = self.make_bridge()
        bridge._gate("/qmw/qac/gate", 101, "cx", 0, 1)
        self.assertEqual(
            bridge.engine_client.messages,
            [("/qmw/state/gate", [101, "cx", 0, 1, "q0_lsb"])],
        )
        self.assertEqual(bridge.live_gate_revision, 101)

    def test_bridge_rejects_stale_gate(self) -> None:
        bridge = self.make_bridge()
        bridge._gate("/qmw/qac/gate", 101, "h", 0)
        bridge._gate("/qmw/qac/gate", 101, "x", 0)
        self.assertEqual(len(bridge.engine_client.messages), 1)
        self.assertEqual(bridge.client.messages[-1][0], "/qmw/qac/error")


if __name__ == "__main__":
    unittest.main()
