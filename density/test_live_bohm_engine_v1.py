import unittest
from types import SimpleNamespace

import numpy as np

from density.density_matrix_engine_4q import DensityMatrixEngine
from guidance.live_bohm_guidance_v1 import BohmEventFamily, BohmGuidanceConfig
from qmw_circuit_bridge import H, single_qubit_unitary


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class NativeUnfoldingBridge:
    def __init__(self):
        self.client = RecordingClient()
        self.circuit = SimpleNamespace(to_openqasm2_lines=lambda: ["h q[0];"])
        self.registry_circuit = SimpleNamespace(active_measurement_bases=lambda: [])
        self.used = False
        self.authoritative_frame = None

    def take_due_circuit_column(self, _dt):
        if self.used:
            return None, None, []
        self.used = True
        return single_qubit_unitary(H, 0, 4), 0, ["H q0"]

    def set_authoritative_pilot_frame(self, frame):
        self.authoritative_frame = frame

    def update_and_send(self, _rho, *_args):
        return self.authoritative_frame


class IdleNativeBridge(NativeUnfoldingBridge):
    def __init__(self):
        super().__init__()
        self.used = True


def basis_density(index: int) -> np.ndarray:
    rho = np.zeros((16, 16), dtype=np.complex128)
    rho[index, index] = 1.0
    return rho


class LiveBohmEngineTests(unittest.TestCase):
    def make_engine(self) -> DensityMatrixEngine:
        engine = DensityMatrixEngine(enable_circuit_bridge_control=False)
        socket = getattr(engine.qmw_bridge.client, "_sock", None)
        if socket is not None:
            socket.close()
        engine.qmw_bridge.client = RecordingClient()
        return engine

    def test_native_circuit_gate_is_unfolded_and_drives_actual_configuration(self):
        engine = self.make_engine()
        engine.qmw_bridge = NativeUnfoldingBridge()
        engine.rho = basis_density(0)
        engine.bohm.reset(engine.rho)
        engine.configuration_revision = engine.bohm.configuration_revision
        engine.hamiltonian = lambda: np.zeros((16, 16), dtype=np.complex128)

        engine.step(0.01)

        populations = np.real(np.diag(engine.rho))
        np.testing.assert_allclose(populations[[0, 8]], [0.5, 0.5], atol=1e-12)
        self.assertAlmostEqual(float(np.sum(populations)), 1.0)
        self.assertIn(engine.bohm.configuration, (0, 8))
        self.assertEqual(
            engine.circuit_state["bohm"]["actual_configuration"],
            engine.bohm.configuration,
        )
        self.assertEqual(
            engine.qmw_bridge.authoritative_frame.next_node,
            engine.bohm.configuration,
        )
        families = [event.family for event in engine.bohm.events_this_frame]
        self.assertIn(BohmEventFamily.CIRCUIT_CURRENT, families)
        addresses = {address for address, _value in engine.qmw_bridge.client.messages}
        self.assertIn("/quantum/bohm/event/family", addresses)

    def test_environmental_amplitude_jump_is_a_distinct_family(self):
        engine = self.make_engine()
        engine.rho = basis_density(8)
        engine.bohm.reset(engine.rho)
        engine.configuration_revision = engine.bohm.configuration_revision
        engine.dephase = 0.0
        engine.depolarize = 0.0
        engine.damping = 1.0

        jumps = []
        for _ in range(20):
            events = engine.apply_noise_trajectory()
            jumps = [event for event in events if event.jumped]
            if jumps:
                break

        self.assertTrue(jumps)
        jump = jumps[-1]
        self.assertEqual(jump.channel, "amplitude_damping")
        self.assertEqual(engine.bohm.configuration, 0)
        self.assertEqual(
            engine.bohm.last_event.family,
            BohmEventFamily.ENVIRONMENTAL_JUMP,
        )
        self.assertEqual(engine.last_event_type, BohmEventFamily.ENVIRONMENTAL_JUMP)

    def test_environment_trajectory_can_be_enabled_in_the_live_step(self):
        engine = DensityMatrixEngine(
            enable_circuit_bridge_control=False,
            bohm_config=BohmGuidanceConfig(
                environment_trajectory_enabled=True,
                environment_seed=17,
            ),
        )
        socket = getattr(engine.qmw_bridge.client, "_sock", None)
        if socket is not None:
            socket.close()
        engine.qmw_bridge = IdleNativeBridge()
        engine.hamiltonian = lambda: np.zeros((16, 16), dtype=np.complex128)

        engine.step(0.01)

        self.assertEqual(len(engine.environment_events), 12)
        self.assertTrue(
            engine.circuit_state["bohm"]["environment_trajectory_enabled"]
        )

    def test_measurement_and_grw_have_different_configuration_rules(self):
        engine = self.make_engine()
        engine.rho = basis_density(3)
        engine.bohm.reset(engine.rho)
        before = engine.bohm.configuration

        # A GRW discontinuity retains N(t), even if this deliberately strong
        # test branch removes its support.
        engine.bohm.record_discontinuity(
            BohmEventFamily.SPONTANEOUS_LOCALIZATION,
            basis_density(12),
            logical_time=0.0,
        )
        self.assertEqual(engine.bohm.configuration, before)

        # Explicit Z measurement supplies a pointer outcome and repairs an
        # unsupported configuration to that post-measurement branch.
        engine.rho = basis_density(12)
        engine.perform_measurement("Z", "collapse", request_id=5)
        self.assertEqual(engine.bohm.configuration, 12)
        self.assertEqual(engine.bohm.last_event.family, BohmEventFamily.EXPLICIT_MEASUREMENT)


if __name__ == "__main__":
    unittest.main()
