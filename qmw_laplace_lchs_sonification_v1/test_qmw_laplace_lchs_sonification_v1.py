import tempfile
import unittest
from pathlib import Path

import numpy as np

from qmw_laplace_lchs_sonification_v1.qmw_laplace_lchs_sonification_v1 import (
    Config, analytical_response, build, laplace_grid, numerical_response, render_audio,
)


class LaplaceLchsSonificationTests(unittest.TestCase):
    def test_numerical_response_agrees_with_closed_form(self) -> None:
        config = Config(samples=8, integration_points=8000)
        s = laplace_grid(config)
        measured, _ = numerical_response(s, config)
        self.assertLess(float(np.max(np.abs(measured - analytical_response(s, config)))), 3e-4)

    def test_audio_is_stereo_finite_and_bounded(self) -> None:
        config = Config(samples=8, duration_seconds=1.5, sample_rate=8000, integration_points=4000)
        s = laplace_grid(config)
        response, _ = numerical_response(s, config)
        audio = render_audio(response, s, config)
        self.assertEqual(audio.shape, (12000, 2))
        self.assertTrue(np.isfinite(audio).all())
        self.assertLessEqual(float(np.max(np.abs(audio))), config.ceiling + 1e-9)

    def test_build_exports_canonical_response_separately_from_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Config(output_dir=Path(directory), samples=4, duration_seconds=0.5,
                            sample_rate=8000, integration_points=3000)
            outputs = build(config)
            self.assertTrue(all(path.exists() for path in outputs.values()))
            data = np.load(outputs["response"])
            self.assertIn("response", data.files)
            self.assertIn("analytical_response", data.files)


if __name__ == "__main__":
    unittest.main()
