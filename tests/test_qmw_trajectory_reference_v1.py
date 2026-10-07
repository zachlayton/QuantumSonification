from __future__ import annotations

import unittest
import socket

import numpy as np

from qmw_trajectory_reference_v1.granular import project_grains
from qmw_trajectory_reference_v1.osc import OSC_ROOT, TrajectoryGrainOSCPublisher, select_indices
from qmw_trajectory_reference_v1.xy import run_xy_trajectory


class _RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, list[object]]] = []

    def send_message(self, address: str, payload: list[object]) -> None:
        self.messages.append((address, payload))


class XYTrajectoryReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.trajectory = run_xy_trajectory(samples=257, duration=12.0)
        cls.controls = project_grains(cls.trajectory)

    def test_trajectory_preserves_closed_system_invariants(self) -> None:
        validation = self.trajectory.validate()
        self.assertLess(validation["state_norm_error_max"], 1.0e-11)
        self.assertLess(validation["trace_error_max"], 1.0e-11)
        self.assertLess(validation["hermiticity_error_max"], 1.0e-11)
        self.assertGreaterEqual(validation["minimum_density_eigenvalue"], -1.0e-11)
        self.assertLess(validation["excitation_error_max"], 1.0e-11)
        self.assertLess(validation["energy_drift_max"], 1.0e-11)
        self.assertLess(validation["site_continuity_error_max"], 1.0e-11)

    def test_transport_and_controls_are_dynamic_and_bounded(self) -> None:
        self.assertGreater(np.ptp(self.trajectory.population_center), 0.2)
        self.assertGreater(np.ptp(self.trajectory.edge_current_left_to_right), 0.2)
        self.assertGreater(np.ptp(self.controls.position), 0.05)
        self.assertGreater(np.ptp(self.controls.density_hz), 1.0)
        self.assertTrue(all(self.controls.validate().values()))

    def test_observer_bridge_preserves_source_order(self) -> None:
        received = self.trajectory.observe_with(
            lambda *, time, frame_index, hamiltonian, rho: (time, frame_index, hamiltonian.shape, rho.shape)
        )
        self.assertEqual(len(received), self.trajectory.samples)
        self.assertEqual(received[0][1], 0)
        self.assertEqual(received[-1][1], self.trajectory.samples - 1)
        self.assertEqual(received[0][2:], ((16, 16), (16, 16)))

    def test_osc_transaction_is_bounded_and_ordered(self) -> None:
        publisher = TrajectoryGrainOSCPublisher(maximum_hz=20.0)
        messages = publisher.messages(self.trajectory, self.controls, revision=7)
        self.assertEqual(messages[0][0], f"{OSC_ROOT}/begin")
        self.assertEqual(messages[-1], (f"{OSC_ROOT}/end", [7]))
        grains = [payload for address, payload in messages if address.endswith("/grain")]
        self.assertLess(len(grains), self.trajectory.samples)
        self.assertEqual(grains[0][1], 0)
        self.assertEqual(grains[-1][1], self.trajectory.samples - 1)
        self.assertTrue(all(payload[0] == 7 for payload in grains))

    def test_select_indices_includes_both_trajectory_endpoints(self) -> None:
        indices = select_indices(self.trajectory.time, maximum_hz=5.0)
        self.assertEqual(indices[0], 0)
        self.assertEqual(indices[-1], self.trajectory.samples - 1)

    def test_publish_sends_a_complete_finite_transaction(self) -> None:
        client = _RecordingClient()
        publisher = TrajectoryGrainOSCPublisher((client,), maximum_hz=1.0)
        sent = publisher.publish(self.trajectory, self.controls, revision=3, speed=1.0e9)
        self.assertEqual(sent, len(client.messages))
        self.assertEqual(client.messages[0][0], f"{OSC_ROOT}/begin")
        self.assertEqual(client.messages[-1][0], f"{OSC_ROOT}/end")

    def test_udp_publisher_emits_a_real_osc_packet(self) -> None:
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(listener.close)
        try:
            listener.bind(("127.0.0.1", 0))
        except PermissionError:
            self.skipTest("the restricted test sandbox does not permit loopback UDP binding")
        listener.settimeout(1.0)
        port = listener.getsockname()[1]
        publisher = TrajectoryGrainOSCPublisher.from_udp("127.0.0.1", port, maximum_hz=1.0)
        self.addCleanup(publisher.close)
        publisher.publish(self.trajectory, self.controls, revision=4, speed=1.0e9)
        packet, _address = listener.recvfrom(4096)
        self.assertTrue(packet.startswith((f"{OSC_ROOT}/begin" + "\x00").encode("utf-8")))


if __name__ == "__main__":
    unittest.main()
