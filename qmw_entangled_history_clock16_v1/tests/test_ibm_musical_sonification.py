"""Tests for the musically organized IBM histogram rendering."""

from __future__ import annotations

import unittest

import numpy as np

from qmw_entangled_history_clock16_v1.ibm_musical_sonification import (
    IBMMusicalConfig,
    _euclidean_pattern,
    render_ibm_musical_form,
)


class IBMMusicalSonificationTests(unittest.TestCase):
    def setUp(self):
        computational = []
        fourier = []
        for clock in range(64):
            count = 2 + clock % 5
            computational.extend(
                f"{clock:06b}{(0 if clock % 2 == 0 else 15):04b}"
                for _ in range(count)
            )
            if clock % 9 == 0:
                computational.append(f"{clock:06b}{3:04b}")
            fourier.extend(f"{clock:06b}{0:04b}" for _ in range(1 + clock % 7))
        self.shots = {
            "computational": computational,
            "clock_fourier": fourier,
        }
        self.config = IBMMusicalConfig(
            sample_rate=8_000,
            duration_seconds=4.0,
            grain_seconds=0.012,
        )

    def test_euclidean_cells_preserve_requested_hit_count(self):
        for hits in range(1, 16):
            pattern = _euclidean_pattern(16, hits, rotation=3)
            self.assertEqual(int(pattern.sum()), hits)

    def test_sixteen_voices_form_a_bounded_nonzero_render(self):
        render = render_ibm_musical_form(self.shots, self.config)
        self.assertEqual(render.voice_stems.shape, (16, 32_000, 2))
        self.assertEqual(len(render.report["rhythm_patterns"]), 16)
        self.assertEqual(len(render.report["fourier_prominence_order"]), 16)
        self.assertTrue(np.isfinite(render.musical_form).all())
        self.assertGreater(float(np.max(np.abs(render.musical_form))), 0.0)
        self.assertLessEqual(float(np.max(np.abs(render.musical_form))), 0.92 + 1e-12)

    def test_render_is_deterministic(self):
        first = render_ibm_musical_form(self.shots, self.config)
        second = render_ibm_musical_form(self.shots, self.config)
        np.testing.assert_allclose(first.musical_form, second.musical_form)


if __name__ == "__main__":
    unittest.main()
