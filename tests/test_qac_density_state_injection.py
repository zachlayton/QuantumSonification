from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
import unittest

import numpy as np

from density.density_state_injection import (
    AtomicDensityStateReceiver,
    DensityStateError,
    bit_reversal_permutation,
    qac_lsb_to_engine_density,
    validate_density_matrix,
)
from quantum_oscilloscope.osc_control import start_visual_control_server
from quantum_population_osc_v9_resonator import MLXQuantumResonatorEngine


ROOT = Path(__file__).resolve().parent
QAC_PATH = ROOT / "qac_quantumsonification_bridge_v1" / "qac_quantumsonification_bridge_v1.py"
SPEC = importlib.util.spec_from_file_location("qac_density_test_bridge", QAC_PATH)
assert SPEC and SPEC.loader
qac = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qac
SPEC.loader.exec_module(qac)

BELL = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
h q[0];
cx q[0],q[1];
"""


class DensityInjectionTests(unittest.TestCase):
    def test_resonator_mirrors_commit_and_snapshot_to_status_port(self):
        class Capture:
            def __init__(self): self.messages = []
            def send_message(self, address, value): self.messages.append((address, value))
        engine = MLXQuantumResonatorEngine.__new__(MLXQuantumResonatorEngine)
        engine.density_state_lock = threading.RLock()
        engine.density_state_revision = -1
        engine.density_engine = SimpleNamespace(rho=None)
        engine.previous_density_field_rho = None
        engine.osc = Capture()
        engine.status_osc = Capture()
        engine.quiet = True
        state = np.zeros(16, dtype=np.complex128)
        state[0] = state[12] = 1 / np.sqrt(2)
        rho = np.outer(state, state.conj())
        engine.commit_density_state(rho, 11, "q0_lsb")
        addresses = [address for address, _ in engine.status_osc.messages]
        self.assertIn("/qmw/state/committed", addresses)
        self.assertIn("/qmw/state/snapshot/probabilities", addresses)
        self.assertIn("/qmw/state/snapshot/purity", addresses)
        self.assertIn("/qmw/state/snapshot/pauli/XXII", addresses)

    def test_bit_reversal_maps_qac_q0_to_engine_q0_axis(self):
        self.assertEqual(bit_reversal_permutation(4).tolist()[1], 8)
        state = np.zeros(16, dtype=np.complex128)
        state[1] = 1.0  # QAC q0=1 (LSB)
        converted = qac_lsb_to_engine_density(np.outer(state, state.conj()))
        self.assertAlmostEqual(converted[8, 8].real, 1.0)  # engine q0=1 (MSB)

    def test_atomic_receiver_commits_complete_new_physical_state(self):
        committed = []
        receiver = AtomicDensityStateReceiver(
            lambda rho, revision, order: committed.append((rho, revision, order))
        )
        frame = qac.analyze(qac.parse_qasm(BELL), 4, shots=0)
        receiver.begin(4, 4, "q0_lsb")
        receiver.set_real(4, frame.rho.real.reshape(-1))
        receiver.set_imag(4, frame.rho.imag.reshape(-1))
        converted = receiver.commit(4)
        self.assertEqual(len(committed), 1)
        self.assertAlmostEqual(converted[0, 0].real, 0.5)
        self.assertAlmostEqual(converted[12, 12].real, 0.5)
        self.assertAlmostEqual(abs(converted[0, 12]), 0.5)
        with self.assertRaisesRegex(DensityStateError, "Stale"):
            receiver.begin(4, 4)

    def test_rejects_nonphysical_density(self):
        bad = np.eye(16, dtype=np.complex128) / 16
        bad[0, 1] = 0.25
        with self.assertRaisesRegex(DensityStateError, "Hermitian"):
            validate_density_matrix(bad)

    def test_real_udp_qac_frame_commits_to_engine_control(self):
        class FakeEngine:
            quiet = True
            def __init__(self):
                self.event = threading.Event()
                self.committed = None
                self.error = None
            def commit_density_state(self, rho, revision, source_order):
                self.committed = (rho, revision, source_order)
                self.event.set()
            def report_density_state_error(self, message):
                self.error = message
                self.event.set()

        engine = FakeEngine()
        control = start_visual_control_server(engine, port=0)
        control_port = control.server_address[1]
        bridge = qac.QACOSCBridge(
            in_port=0,
            out_port=control_port,
            shots=0,
            engine_control_host="127.0.0.1",
            engine_control_port=control_port,
        )
        class CaptureClient:
            def send_message(self, _address, _value):
                pass
        bridge.client._sock.close()
        bridge.client = CaptureClient()
        try:
            frame = qac.analyze(qac.parse_qasm(BELL), 9, shots=0)
            bridge.inject_density(frame)
            self.assertTrue(engine.event.wait(2.0), "density commit did not arrive over UDP")
            self.assertIsNone(engine.error)
            rho, revision, order = engine.committed
            self.assertEqual((revision, order), (9, "q0_lsb"))
            self.assertAlmostEqual(rho[12, 12].real, 0.5)
        finally:
            bridge.engine_client._sock.close()
            bridge.server.server_close()
            control.shutdown()
            control.server_close()


if __name__ == "__main__":
    unittest.main()
