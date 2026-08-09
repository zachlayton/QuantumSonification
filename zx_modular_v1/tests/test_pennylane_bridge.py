from __future__ import annotations

import importlib.util
import math
import unittest

import numpy as np

from zx_modular_v1 import linear_map, pennylane_to_modular


HAS_PENNYLANE_ZX = (
    importlib.util.find_spec("pennylane") is not None
    and importlib.util.find_spec("pyzx") is not None
)


@unittest.skipUnless(
    HAS_PENNYLANE_ZX,
    "PennyLane/PyZX optional integration is not installed",
)
class PennyLaneBridgeTests(unittest.TestCase):
    @staticmethod
    def bell_phase(theta: float) -> None:
        import pennylane as qml

        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        qml.RZ(theta, wires=1)

    def test_pennylane_pyzx_import_is_semantically_exact(self) -> None:
        result = pennylane_to_modular(
            self.bell_phase,
            0.37,
            name="test_bell_phase",
        )
        report = result.import_report
        self.assertTrue(report.verified)
        self.assertLess(report.absolute_error, 2e-12)
        np.testing.assert_allclose(
            linear_map(report.diagram),
            result.pyzx_graph.to_matrix(preserve_scalar=True),
            atol=1e-12,
        )

    def test_wire_order_and_scalar_are_explicit(self) -> None:
        result = pennylane_to_modular(self.bell_phase, math.pi / 3.0)
        report = result.import_report
        self.assertEqual(report.input_wire_to_boundary, {0: 1, 1: 0})
        self.assertEqual(report.output_wire_to_boundary, {0: 1, 1: 0})
        metadata = result.patch_plan.metadata
        self.assertEqual(
            metadata["basis_ordering"],
            "|q[n-1] ... q1 q0>; boundary 0 is LSB",
        )
        self.assertAlmostEqual(
            metadata["global_scalar"]["real"],
            math.sqrt(2.0),
        )

    def test_optional_pyzx_simplification_stays_exact(self) -> None:
        result = pennylane_to_modular(
            self.bell_phase,
            -0.92,
            simplify=True,
        )
        self.assertTrue(result.import_report.verified)
        self.assertLess(result.import_report.absolute_error, 2e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
