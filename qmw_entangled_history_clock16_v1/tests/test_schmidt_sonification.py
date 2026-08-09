"""Tests for the Schmidt temporal-mode rhythmic rendering."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1.history_state import (
    prepare_floquet_history_state,
)
from qmw_entangled_history_clock16_v1.schmidt_sonification import (
    SchmidtRhythmConfig,
    render_schmidt_rhythm,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class SchmidtSonificationTests(unittest.TestCase):
    def setUp(self):
        self.history = prepare_floquet_history_state(
            FloquetTimeCrystal16(),
            computational_basis_state(0),
            clock_qubits=6,
        )
        self.config = SchmidtRhythmConfig(
            sample_rate=8_000,
            duration_seconds=1.0,
            clock_interval_ms_start=55.0,
            clock_interval_ms_end=43.0,
            grain_seconds=0.018,
        )

    def test_default_history_renders_two_interlocking_schmidt_modes(self):
        render = render_schmidt_rhythm(self.history, self.config)
        self.assertEqual(render.report["clock_states"], 64)
        self.assertEqual(render.report["effective_schmidt_rank"], 2)
        self.assertEqual(render.report["rendered_mode_count"], 2)
        np.testing.assert_allclose(
            render.report["active_eigenvalues"],
            [0.5, 0.5],
            atol=1e-12,
        )
        supports = render.report["mode_clock_supports"]
        self.assertEqual(set(np.asarray(supports[0]) % 2), {0})
        self.assertEqual(set(np.asarray(supports[1]) % 2), {1})
        self.assertEqual(render.mode_stems.shape, (2, 8_000, 2))
        self.assertTrue(np.isfinite(render.coherent_phase_rhythm).all())
        self.assertLessEqual(
            float(np.max(np.abs(render.coherent_phase_rhythm))),
            0.92 + 1e-12,
        )
        self.assertGreater(
            float(np.max(np.abs(
                render.coherent_phase_rhythm
                - render.magnitude_only_control
            ))),
            1e-4,
        )

    def test_render_is_invariant_under_initial_global_phase(self):
        phased = prepare_floquet_history_state(
            FloquetTimeCrystal16(),
            np.exp(0.731j) * computational_basis_state(0),
            clock_qubits=6,
        )
        reference = render_schmidt_rhythm(self.history, self.config)
        transformed = render_schmidt_rhythm(phased, self.config)
        np.testing.assert_allclose(
            transformed.coherent_phase_rhythm,
            reference.coherent_phase_rhythm,
            atol=1e-12,
        )


if __name__ == "__main__":
    unittest.main()
