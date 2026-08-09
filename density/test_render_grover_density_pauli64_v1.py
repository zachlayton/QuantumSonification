"""Tests for the exact 64-coefficient Pauli resonator render."""

from __future__ import annotations

import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from density.render_grover_density_modal_v1 import GroverModalConfig, grover_modal_trajectory
from density.render_grover_density_pauli64_v1 import (
    Pauli64RenderConfig,
    pauli_coefficients,
    pauli_labels,
    pauli_mode_frequencies,
    pauli_weight,
    reconstruct_density_from_pauli,
    render_pauli64_audio,
    render_to_wav,
)


class GroverDensityPauli64RenderV1Tests(unittest.TestCase):
    def config(self, output: Path) -> Pauli64RenderConfig:
        return Pauli64RenderConfig(
            output_path=output,
            sample_rate=8_000,
            duration_seconds=0.5,
        )

    def test_three_qubits_have_64_weight_grouped_labels(self) -> None:
        labels = pauli_labels(3)
        self.assertEqual(len(labels), 64)
        self.assertEqual(len(set(labels)), 64)
        self.assertEqual(
            [sum(pauli_weight(label) == weight for label in labels) for weight in range(4)],
            [1, 9, 27, 27],
        )

    def test_pauli_coefficients_exactly_reconstruct_every_density_state(self) -> None:
        trajectory = grover_modal_trajectory(GroverModalConfig())
        for rho in trajectory.states:
            coefficients = pauli_coefficients(rho)
            reconstructed = reconstruct_density_from_pauli(coefficients, 3)
            np.testing.assert_allclose(reconstructed, rho, atol=2e-15)
            self.assertAlmostEqual(coefficients["III"], 1.0, places=12)

    def test_frequency_families_are_separated_and_complete(self) -> None:
        labels = pauli_labels(3)
        frequencies = pauli_mode_frequencies(labels, 44_100)
        self.assertEqual(set(frequencies), set(labels))
        for lower_weight in range(3):
            lower = [frequencies[label] for label in labels if pauli_weight(label) == lower_weight]
            upper = [frequencies[label] for label in labels if pauli_weight(label) == lower_weight + 1]
            self.assertLess(max(lower), min(upper))

    def test_render_is_deterministic_nonempty_stereo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(Path(directory) / "pauli64.wav")
            first, first_coefficients = render_pauli64_audio(config)
            second, second_coefficients = render_pauli64_audio(config)
            self.assertEqual(first.shape, (4_000, 2))
            np.testing.assert_array_equal(first, second)
            self.assertEqual(first_coefficients, second_coefficients)
            self.assertGreater(float(np.max(np.abs(first))), 0.1)
            self.assertLessEqual(float(np.max(np.abs(first))), config.output_ceiling)

    def test_wav_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pauli64.wav"
            render_to_wav(self.config(output))
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 2)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), 4_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
