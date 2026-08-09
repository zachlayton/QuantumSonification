"""Tests for continuous Z-plane phase-oracle sonification."""

from __future__ import annotations

import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from density.grover_density_operator_v1 import uniform_density
from density.render_grover_phase_oracle_zplane_v1 import (
    ZPlanePhaseRenderConfig,
    coherence_pairs,
    oracle_sweep_density,
    render_to_wav,
    render_zplane_phase_audio,
    smooth_oracle_strength,
)


class GroverPhaseOracleZPlaneV1Tests(unittest.TestCase):
    def config(self, output: Path) -> ZPlanePhaseRenderConfig:
        return ZPlanePhaseRenderConfig(
            output_path=output,
            sample_rate=8_000,
            duration_seconds=0.6,
        )

    def test_three_qubit_upper_triangle_has_28_coherences(self) -> None:
        self.assertEqual(len(coherence_pairs(8)), 28)

    def test_strength_sweep_has_exact_smooth_endpoints(self) -> None:
        strength = smooth_oracle_strength(101)
        self.assertEqual(strength[0], 0.0)
        self.assertEqual(strength[-1], 1.0)
        self.assertTrue(np.all(np.diff(strength) >= 0.0))

    def test_oracle_sweep_rotates_phase_without_changing_population_or_spectrum(self) -> None:
        rho = uniform_density(3)
        partial = oracle_sweep_density(rho, 3, ("010", "101"), 0.37)
        expected_phase = np.exp(-1j * np.pi * 0.37)
        np.testing.assert_allclose(np.diag(partial), np.diag(rho), atol=1e-14)
        np.testing.assert_allclose(np.linalg.eigvalsh(partial), np.linalg.eigvalsh(rho), atol=1e-14)
        self.assertAlmostEqual(partial[2, 0] / rho[2, 0], expected_phase)

    def test_render_is_deterministic_and_invariant_diagnostics_are_small(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(Path(directory) / "phase.wav")
            first, first_diagnostics = render_zplane_phase_audio(config)
            second, second_diagnostics = render_zplane_phase_audio(config)
            self.assertEqual(first.shape, (4_800, 2))
            np.testing.assert_array_equal(first, second)
            self.assertEqual(first_diagnostics, second_diagnostics)
            self.assertLess(first_diagnostics["maximum_population_error"], 1e-12)
            self.assertLess(first_diagnostics["maximum_spectrum_error"], 1e-12)
            self.assertGreater(float(np.max(np.abs(first))), 0.1)

    def test_wav_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "phase.wav"
            render_to_wav(self.config(output))
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 2)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), 4_800)


if __name__ == "__main__":
    unittest.main(verbosity=2)
