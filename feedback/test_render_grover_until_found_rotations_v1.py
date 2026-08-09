import tempfile
import unittest
from pathlib import Path

import numpy as np

from feedback.render_grover_until_found_rotations_v1 import (
    UntilFoundRenderConfig,
    render_until_found_audio,
    run_until_found,
    smooth_iteration_pulses,
)


class GroverUntilFoundRotationTests(unittest.TestCase):
    def test_57893_schedule(self):
        result = run_until_found(57_893, 0.9999)
        self.assertEqual(result.target_bits, "1110001000100101")
        self.assertEqual(result.n_qubits, 16)
        self.assertEqual(result.search_space_size, 65_536)
        self.assertEqual(result.found_iteration, 200)
        self.assertEqual(result.optimal_iteration, 201)
        self.assertGreater(result.probabilities[-1], 0.9999)
        self.assertAlmostEqual(np.degrees(result.grover_step_angle), 0.4476244158)

    def test_iteration_pulse_has_no_wrap_discontinuity(self):
        spacing = 0.1
        epsilon = 1e-7
        time = np.array([-epsilon, 0.0, epsilon, spacing - epsilon, spacing, spacing + epsilon])
        pulses = smooth_iteration_pulses(time, 0.0, spacing)
        self.assertAlmostEqual(pulses[0], pulses[1], places=10)
        self.assertAlmostEqual(pulses[1], pulses[2], places=10)
        self.assertAlmostEqual(pulses[3], pulses[4], places=10)
        self.assertAlmostEqual(pulses[4], pulses[5], places=10)

    def test_short_render_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            config = UntilFoundRenderConfig(
                output_path=Path(directory) / "search.wav",
                diagnostics_path=Path(directory) / "search.json",
                sample_rate=8_000,
                duration_seconds=0.8,
            )
            audio, diagnostics = render_until_found_audio(config)
        self.assertEqual(audio.shape, (6_400, 2))
        self.assertTrue(np.all(np.isfinite(audio)))
        self.assertLessEqual(float(np.max(np.abs(audio))), config.output_ceiling + 1e-12)
        self.assertEqual(diagnostics["found_iteration"], 200)
        self.assertGreater(diagnostics["frequency_ratio_range"][1], 1.0)


if __name__ == "__main__":
    unittest.main()
