from __future__ import annotations

import unittest

try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None

from wilson_quantum_geometry_v1.circuit_tuning import (
    circuit_wilson_tuning_frame,
    wilson_tuning_vertices,
)


@unittest.skipIf(QuantumCircuit is None, "Qiskit is required")
class CircuitTuningTests(unittest.TestCase):
    def test_fixed_hexany_labels_match_exact_anchor_ratios(self) -> None:
        by_mask = {vertex.bitmask: vertex for vertex in wilson_tuning_vertices((1, 3, 5, 7))}
        expected = {
            0b0011: "1",
            0b0101: "5/3",
            0b0110: "5/4",
            0b1001: "7/6",
            0b1010: "7/4",
            0b1100: "35/24",
        }
        self.assertEqual({mask: str(vertex.ratio) for mask, vertex in by_mask.items()}, expected)
        self.assertEqual(by_mask[0b0101].factors, (1, 5))
        self.assertEqual(str(by_mask[0b0101].audition_ratio), "5/4")

    def test_reordered_global_frame_uses_qubit_specific_factor_pairs(self) -> None:
        by_mask = {vertex.bitmask: vertex for vertex in wilson_tuning_vertices((7, 1, 3, 11))}
        self.assertEqual(by_mask[0b0011].factors, (7, 1))
        self.assertEqual(by_mask[0b0011].ratio, 1)
        self.assertEqual(by_mask[0b0101].factors, (7, 3))
        self.assertEqual(str(by_mask[0b0101].ratio), "3/2")
        self.assertEqual(str(by_mask[0b1100].ratio), "33/28")

    def test_bell_ghz_and_weave_generate_distinct_tuning_frames(self) -> None:
        bell = QuantumCircuit(4)
        bell.h(0)
        bell.cx(0, 1)

        ghz = QuantumCircuit(4)
        ghz.h(0)
        ghz.cx(0, 1)
        ghz.cx(1, 2)
        ghz.cx(2, 3)

        weave = QuantumCircuit(4)
        for qubit in range(4):
            weave.h(qubit)
        weave.cx(0, 1)
        weave.cx(2, 3)
        weave.cx(1, 2)
        weave.t(0)
        weave.s(3)

        frames = tuple(map(circuit_wilson_tuning_frame, (bell, ghz, weave)))
        self.assertEqual([frame.family for frame in frames], ["paired", "global", "woven"])
        self.assertEqual(len({frame.master_set for frame in frames}), 3)
        self.assertEqual(len({frame.mos_position for frame in frames}), 3)
        self.assertEqual(frames[0].fingerprint.component_sizes, (2, 1, 1))
        self.assertEqual(frames[1].fingerprint.component_sizes, (4,))

    def test_qubit_permutation_preserves_family_and_factor_multiset(self) -> None:
        left = QuantumCircuit(4)
        left.h(0)
        left.cx(0, 1)
        right = QuantumCircuit(4)
        right.h(2)
        right.cx(2, 3)
        left_frame = circuit_wilson_tuning_frame(left)
        right_frame = circuit_wilson_tuning_frame(right)
        self.assertEqual(left_frame.family, right_frame.family)
        self.assertEqual(sorted(left_frame.master_set), sorted(right_frame.master_set))
        self.assertNotEqual(left_frame.master_set, right_frame.master_set)


if __name__ == "__main__":
    unittest.main()
