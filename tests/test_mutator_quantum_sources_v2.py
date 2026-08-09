from __future__ import annotations

import math
import sys
import types
import unittest


class _HamiltonianState:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x, self.y, self.z = x, y, z

    def normalize(self):
        norm = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if norm > 0.0:
            self.x /= norm
            self.y /= norm
            self.z /= norm
        return self


stub = types.ModuleType("hamiltonian.hamiltonian_state")
stub.HamiltonianState = _HamiltonianState
sys.modules.setdefault("hamiltonian.hamiltonian_state", stub)

from hamiltonian.mutator_quantum_sources_v2 import HamiltonianMutator  # noqa: E402


class MutatorV2Tests(unittest.TestCase):
    def test_original_names_remain_available(self) -> None:
        names = HamiltonianMutator.available_sources()
        for name in ("audio", "hydrogen_spectrum", "hydrogen_orbital", "schrodinger_packet"):
            self.assertIn(name, names)

    def test_sources_are_lazy(self) -> None:
        mutator = HamiltonianMutator(excitation_kind="schrodinger_packet_3d")
        self.assertEqual(mutator._sources, {})
        frame = mutator.source_frame(0.01)
        self.assertEqual(frame.dimension, 3)
        self.assertIn("schrodinger_packet_3d", mutator._sources)

    def test_legacy_event_source_rejects_frame_request(self) -> None:
        mutator = HamiltonianMutator(excitation_kind="hydrogen_spectrum")
        descriptor = mutator.source_descriptor(0.01)
        self.assertTrue(0.0 <= descriptor.energy <= 1.0)
        with self.assertRaises(TypeError):
            mutator.source_frame(0.01)

    def test_wavefunction_descriptor_mutates_hamiltonian(self) -> None:
        mutator = HamiltonianMutator(
            excitation_kind="quantum_rotor",
            source_parameters={"n_points": 64},
        )
        result = mutator.mutate_from_physics_source(_HamiltonianState(0.0, 0.0, 1.0), 0.01)
        norm = math.sqrt(result.x**2 + result.y**2 + result.z**2)
        self.assertAlmostEqual(norm, 1.0, places=10)


if __name__ == "__main__":
    unittest.main()
