from __future__ import annotations

import math
import unittest

import numpy as np

from qmw.core.state_frame import QuantumStateFrame
from wilson_quantum_geometry_v1 import (
    WilsonAdapterConfig,
    WilsonOSCPublisher,
    WilsonStateAdapter,
)


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class WilsonStateAdapterTests(unittest.TestCase):
    def test_pure_state_preserves_relative_phase_and_shell_probability(self) -> None:
        adapter = WilsonStateAdapter()
        state = np.zeros(16, dtype=np.complex128)
        state[0b0011] = 1 / math.sqrt(2)
        state[0b0101] = 1j / math.sqrt(2)
        frame = adapter.adapt_statevector(state, time=0.0, dt=0.1)

        self.assertAlmostEqual(frame.shell_probability, 1.0)
        self.assertAlmostEqual(frame.leakage_probability, 0.0)
        self.assertAlmostEqual(frame.conditional_shell_purity, 1.0)
        by_mask = {vertex.bitmask: vertex for vertex in frame.vertices}
        self.assertAlmostEqual(by_mask[0b0011].conditional_probability, 0.5)
        self.assertAlmostEqual(by_mask[0b0101].conditional_probability, 0.5)
        self.assertAlmostEqual(by_mask[0b0101].phase_coherence, 1.0)
        self.assertGreater(by_mask[0b0101].relative_phase, 0.0)

    def test_mixed_density_state_does_not_invent_phase_coherence(self) -> None:
        adapter = WilsonStateAdapter()
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0b0011, 0b0011] = 0.5
        rho[0b0101, 0b0101] = 0.5
        frame = adapter.adapt_density_matrix(rho, time=0.0, dt=0.1)

        self.assertAlmostEqual(frame.conditional_shell_purity, 0.5)
        by_mask = {vertex.bitmask: vertex for vertex in frame.vertices}
        self.assertAlmostEqual(by_mask[0b0101].phase_coherence, 0.0)
        self.assertAlmostEqual(by_mask[0b0101].relative_phase, 0.0)

    def test_leakage_and_auditory_persistence_are_independent(self) -> None:
        adapter = WilsonStateAdapter(
            WilsonAdapterConfig(attack_ms=20.0, persistence_ms=1000.0)
        )
        shell_state = np.zeros(16, dtype=np.complex128)
        shell_state[0b0011] = 1.0
        active = adapter.adapt_statevector(shell_state, time=0.0, dt=0.1)
        initial_activation = active.vertices[0].activation
        self.assertGreater(initial_activation, 0.9)

        leaked_state = np.zeros(16, dtype=np.complex128)
        leaked_state[0] = 1.0
        leaked = adapter.adapt_statevector(leaked_state, time=0.1, dt=0.1)
        self.assertAlmostEqual(leaked.shell_probability, 0.0)
        self.assertAlmostEqual(leaked.leakage_probability, 1.0)
        self.assertGreater(leaked.vertices[0].activation, 0.8)
        self.assertLess(leaked.vertices[0].activation, initial_activation)

    def test_canonical_quantum_frame_contract(self) -> None:
        adapter = WilsonStateAdapter()
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0b1100, 0b1100] = 1.0
        source = QuantumStateFrame(t=1.25, dt=0.05, rho=rho)
        frame = adapter.adapt_quantum_frame(source, revision=7)
        self.assertEqual(frame.revision, 7)
        self.assertEqual(frame.time, 1.25)
        self.assertEqual(frame.reference_vertex, 5)

    def test_osc_contract_publishes_definition_edges_then_dynamic_frame(self) -> None:
        client = RecordingClient()
        adapter = WilsonStateAdapter()
        publisher = WilsonOSCPublisher(adapter, [client])
        state = np.zeros(16, dtype=np.complex128)
        state[0b0011] = 1.0
        frame = adapter.adapt_statevector(state, time=0.0, dt=0.1)
        publisher.publish(frame)

        addresses = [address for address, _ in client.messages]
        self.assertEqual(addresses[0], "/qmw/wilson/cps/definition")
        self.assertEqual(addresses.count("/qmw/wilson/cps/edge"), 12)
        self.assertEqual(addresses.count("/qmw/wilson/cps/vertex"), 6)
        self.assertLess(
            addresses.index("/qmw/wilson/cps/frame"),
            addresses.index("/qmw/wilson/cps/vertex"),
        )
        self.assertEqual(addresses[-1], "/qmw/wilson/cps/end")

        second = adapter.adapt_statevector(state, time=0.1, dt=0.1)
        publisher.publish(second)
        later_addresses = [address for address, _ in client.messages[len(addresses):]]
        self.assertNotIn("/qmw/wilson/cps/definition", later_addresses)
        self.assertNotIn("/qmw/wilson/cps/edge", later_addresses)
        self.assertEqual(later_addresses.count("/qmw/wilson/cps/vertex"), 6)

        publisher.publish_measurement(
            revision=second.revision,
            basis_index=0b0011,
            probability=1.0,
        )
        self.assertEqual(client.messages[-1][0], "/qmw/wilson/cps/measurement")
        self.assertEqual(client.messages[-1][1][-1], 1)

        publisher.publish_flow(
            revision=second.revision,
            generation=2,
            source_basis_index=0b0011,
            destination_basis_index=0b0101,
            absolute_flow=0.2,
            conditional_flow=0.25,
            theta=0.4,
            beta=-0.2,
            relative_phase=0.7,
        )
        self.assertEqual(client.messages[-1][0], "/qmw/wilson/cps/flow")
        self.assertEqual(client.messages[-1][1][2:4], [0, 1])


if __name__ == "__main__":
    unittest.main()
