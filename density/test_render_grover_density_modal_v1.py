"""Tests for the Grover density modal WAV renderer."""

from __future__ import annotations

import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from density.render_grover_density_modal_v1 import (
    GroverModalConfig,
    brightness_from_coherence,
    pin_modal_root,
    render_grover_modal_audio,
    render_to_wav,
)


class GroverDensityModalRenderV1Tests(unittest.TestCase):
    def config(self, output: Path) -> GroverModalConfig:
        return GroverModalConfig(
            output_path=output,
            sample_rate=8_000,
            duration_seconds=0.5,
            iterations=2,
        )

    def test_render_is_deterministic_stereo_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(Path(directory) / "grover.wav")
            first, first_result = render_grover_modal_audio(config)
            second, second_result = render_grover_modal_audio(config)
            self.assertEqual(first.shape, (4_000, 2))
            np.testing.assert_array_equal(first, second)
            self.assertGreater(float(np.max(np.abs(first))), 0.1)
            self.assertLessEqual(float(np.max(np.abs(first))), config.output_ceiling)
            self.assertEqual(len(first_result.states), 3)
            self.assertEqual(first_result.metrics, second_result.metrics)

    def test_brightness_maps_coherence_across_configured_range(self) -> None:
        self.assertAlmostEqual(brightness_from_coherence(0.0, 3, 0.18, 0.96), 0.18)
        self.assertAlmostEqual(brightness_from_coherence(7.0, 3, 0.18, 0.96), 0.96)
        self.assertAlmostEqual(brightness_from_coherence(3.5, 3, 0.18, 0.96), 0.57)

    def test_modal_root_is_pinned_without_changing_intervals(self) -> None:
        original = np.array([49.875, 103.0, 157.25])
        pinned = pin_modal_root(original, 66.6, 44_100)
        self.assertAlmostEqual(pinned[0], 66.6)
        np.testing.assert_allclose(pinned / pinned[0], original / original[0])

    def test_wav_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "grover.wav"
            config = self.config(output)
            render_to_wav(config)
            self.assertTrue(output.is_file())
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 2)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), 4_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
