"""Cross-check the SuperCollider temporal-mechanics constants."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    prepare_floquet_history_state,
    reduced_clock_density,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


SC_PATH = (
    Path(__file__).resolve().parents[2]
    / "supercollider"
    / "qmw_entangled_history_temporal_mechanics_clicks_v1.scd"
)


class SuperColliderTemporalMechanicsTests(unittest.TestCase):
    def setUp(self):
        self.history = prepare_floquet_history_state(
            FloquetTimeCrystal16(),
            computational_basis_state(0),
        )
        self.source = SC_PATH.read_text()

    def test_embedded_conditional_phases_match_exact_history(self):
        match = re.search(
            r"~qmwTemporalConditionalPhases\s*=\s*\[(.*?)\];",
            self.source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        embedded = np.asarray([
            float(value)
            for value in re.findall(r"[-+]?\d+(?:\.\d+)?", match.group(1))
        ])
        states = self.history.conditional_states()
        exact = np.asarray([
            np.angle(state[np.argmax(np.abs(state))]) for state in states
        ])
        self.assertEqual(embedded.shape, (16,))
        np.testing.assert_allclose(embedded, exact, atol=5e-12)

    def test_clock_coherence_has_two_parity_communities(self):
        density = reduced_clock_density(self.history)
        diagonal = np.diag(density).real
        scale = np.sqrt(np.outer(diagonal, diagonal))
        normalized = np.divide(
            density,
            scale,
            out=np.zeros_like(density),
            where=scale > 1e-15,
        )
        for left in range(16):
            for right in range(16):
                expected = 1.0 if (left % 2) == (right % 2) else 0.0
                self.assertAlmostEqual(abs(normalized[left, right]), expected)
        self.assertIn("LocalIn.kr(16, 0)", self.source)
        self.assertIn("~qmwTemporalCoupling.(0.0)", self.source)


if __name__ == "__main__":
    unittest.main()
