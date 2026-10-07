"""Checks for the six-qubit, 64-state temporal-mechanics example."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

import numpy as np

from qmw_entangled_history_clock16_v1 import (
    analyze_history,
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
    / "qmw_entangled_history_temporal_mechanics_clicks64_v1.scd"
)


class History64TemporalMechanicsTests(unittest.TestCase):
    def setUp(self):
        self.history = prepare_floquet_history_state(
            FloquetTimeCrystal16(),
            computational_basis_state(0),
            clock_qubits=6,
        )
        self.source = SC_PATH.read_text()

    def _normalized_coherence(self) -> np.ndarray:
        density = reduced_clock_density(self.history)
        diagonal = np.diag(density).real
        scale = np.sqrt(np.outer(diagonal, diagonal))
        return np.divide(
            density,
            scale,
            out=np.zeros_like(density),
            where=scale > 1e-15,
        )

    def test_six_clock_qubits_create_1024_amplitude_history(self):
        diagnostics = analyze_history(self.history)
        self.assertEqual(self.history.clock_qubits, 6)
        self.assertEqual(self.history.clock_states, 64)
        self.assertEqual(self.history.system_dimension, 16)
        self.assertEqual(self.history.joint_dimension, 1024)
        self.assertEqual(self.history.state_vector.shape, (1024,))
        np.testing.assert_allclose(
            self.history.clock_probabilities(),
            np.full(64, 1.0 / 64.0),
            atol=1e-12,
        )
        self.assertAlmostEqual(diagnostics.clock_purity, 0.5, places=12)
        self.assertAlmostEqual(
            diagnostics.system_time_linear_entropy,
            0.5,
            places=12,
        )
        self.assertEqual(diagnostics.effective_schmidt_rank, 2)
        self.assertAlmostEqual(
            diagnostics.schmidt_participation_number,
            2.0,
            places=12,
        )
        self.assertAlmostEqual(
            diagnostics.schmidt_von_neumann_entropy_bits,
            1.0,
            places=12,
        )
        np.testing.assert_allclose(
            diagnostics.clock_schmidt_eigenvalues[:2],
            [0.5, 0.5],
            atol=1e-12,
        )
        np.testing.assert_allclose(
            diagnostics.clock_schmidt_eigenvalues[2:],
            0.0,
            atol=1e-12,
        )

        supports = [
            set(np.flatnonzero(np.abs(mode) > 1e-10) % 2)
            for mode in diagnostics.clock_schmidt_modes[:2]
        ]
        self.assertEqual(supports, [{0}, {1}])

    def test_embedded_phases_match_all_sixty_four_history_branches(self):
        match = re.search(
            r"~qmwTemporal64ConditionalPhases\s*=\s*\[(.*?)\];",
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
        self.assertEqual(embedded.shape, (64,))
        np.testing.assert_allclose(embedded, exact, atol=5e-12)

    def test_two_mean_fields_equal_full_pairwise_coherence_force(self):
        coherence = self._normalized_coherence()
        for left in range(64):
            for right in range(64):
                expected = 1.0 if (left % 2) == (right % 2) else 0.0
                self.assertAlmostEqual(abs(coherence[left, right]), expected)

        rng = np.random.default_rng(31)
        oscillator_phases = rng.uniform(-np.pi, np.pi, size=64)
        states = self.history.conditional_states()
        conditional_phases = np.asarray([
            np.angle(state[np.argmax(np.abs(state))]) for state in states
        ])
        pairwise = np.zeros(64)
        for voice in range(64):
            terms = [
                np.imag(
                    coherence[voice, other]
                    * np.exp(1j * (
                        oscillator_phases[other] - oscillator_phases[voice]
                    ))
                )
                for other in range(64)
                if other != voice
            ]
            pairwise[voice] = sum(terms) / 31.0

        transformed = oscillator_phases - conditional_phases
        mean_field = np.zeros(64)
        for voice in range(64):
            community = np.arange(voice % 2, 64, 2)
            mean_field[voice] = np.sum(
                np.sin(transformed[community] - transformed[voice])
            ) / 31.0
        np.testing.assert_allclose(mean_field, pairwise, atol=1e-12)
        self.assertEqual(self.source.count("LocalIn.kr(32, 0)"), 1)
        self.assertIn("qmwTemporalMechanicsClicks64EvenV1", self.source)
        self.assertIn("qmwTemporalMechanicsClicks64OddV1", self.source)
        self.assertIn("var octaveOffsets = [0, 1, -1, 2]", self.source)
        self.assertIn("parityPan = 0.32", self.source)
        self.assertIn("/ 31.0", self.source)


if __name__ == "__main__":
    unittest.main()
