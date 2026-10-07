"""Tests for the randomized-basis, non-grid clock rendering."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1.history_state import (
    prepare_floquet_history_state,
)
from qmw_entangled_history_clock16_v1.randomized_clock_sonification import (
    RandomizedClockConfig,
    render_randomized_clock,
)
from qmw_entangled_history_clock16_v1.render_randomized_clock64 import (
    tilted_product_state,
)
from qmw_temporal_crystal16_v1 import FloquetIsingConfig, FloquetTimeCrystal16


class RandomizedClockSonificationTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16(FloquetIsingConfig(
            pulse_error=0.05,
            transverse_fields=(0.07, -0.11, 0.13, -0.17),
        ))
        self.initial = tilted_product_state()
        self.history = prepare_floquet_history_state(
            self.model,
            self.initial,
            clock_qubits=6,
        )
        self.config = RandomizedClockConfig(
            sample_rate=8_000,
            duration_seconds=1.2,
            grain_seconds=0.010,
            seed=712,
        )

    def test_rank_expanded_history_uses_all_sixteen_voices(self):
        render = render_randomized_clock(self.history, self.config)
        self.assertEqual(render.report["rendered_mode_count"], 16)
        self.assertGreater(
            render.report["schmidt_participation_number"],
            9.0,
        )
        self.assertGreater(render.report["linear_entropy_E2"], 0.89)
        self.assertEqual(render.mode_stems.shape, (16, 9_600, 2))
        self.assertTrue(all(count > 0 for count in render.report["event_counts"]))

    def test_independent_intervals_are_variable_and_phase_audible(self):
        render = render_randomized_clock(self.history, self.config)
        variations = [
            item["coefficient_of_variation"]
            for item in render.report["interval_statistics"]
        ]
        self.assertGreater(float(np.median(variations)), 0.15)
        self.assertGreater(
            float(np.linalg.norm(
                render.coherent_measurement_rhythm
                - render.phase_erased_control
            )),
            1.0,
        )

    def test_fixed_seed_is_reproducible_and_global_phase_invariant(self):
        reference = render_randomized_clock(self.history, self.config)
        phased_history = prepare_floquet_history_state(
            self.model,
            np.exp(0.817j) * self.initial,
            clock_qubits=6,
        )
        transformed = render_randomized_clock(phased_history, self.config)
        np.testing.assert_allclose(
            transformed.coherent_measurement_rhythm,
            reference.coherent_measurement_rhythm,
            atol=1e-11,
        )


if __name__ == "__main__":
    unittest.main()
