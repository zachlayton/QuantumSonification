"""Tests for the direct 16-voice density-matrix wavetable renderer."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
import wave

import numpy as np

from quantum_graph_canon_v1.wavetable_audio import (
    ArticulatedDensityWavetableConfig,
    DensityWavetableRenderConfig,
    articulated_density_wavetable_manifest,
    density_voice_parameters,
    density_wavetable_manifest,
    graph_qnn_voice_offsets,
    render_articulated_density_wavetable_bank,
    render_density_wavetable_bank,
    voice_wavetables_from_density,
    write_density_wavetable_wav,
)


class DensityWavetableAudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DensityWavetableRenderConfig(
            sample_rate=8_000,
            duration_seconds=0.2,
            control_rate_hz=20.0,
            base_frequency_hz=20.0,
            fade_seconds=0.005,
        )
        phases_a = np.linspace(0.0, 1.5, 16)
        phases_b = np.linspace(1.0, -2.0, 16)
        state_a = np.exp(1j * phases_a) / 4.0
        state_b = np.exp(1j * phases_b) / 4.0
        self.densities = (
            np.outer(state_a, state_a.conj()),
            np.outer(state_b, state_b.conj()),
        )

    def test_fixed_voice_and_wavetable_dimensions(self) -> None:
        tables = voice_wavetables_from_density(self.densities[0], self.config)
        self.assertEqual(tables.shape, (16, 256))
        self.assertTrue(np.all(np.isfinite(tables)))
        self.assertLess(float(np.max(np.abs(np.mean(tables, axis=1)))), 1e-12)
        self.assertLessEqual(float(np.max(np.abs(tables))), 1.0 + 1e-12)

    def test_diagonal_population_maps_to_fundamental(self) -> None:
        maximally_mixed = np.eye(16, dtype=complex) / 16.0
        tables = voice_wavetables_from_density(maximally_mixed, self.config)
        for table in tables:
            spectrum = np.abs(np.fft.rfft(table))
            self.assertEqual(int(np.argmax(spectrum[1:]) + 1), 1)

    def test_density_controls_tables_amplitudes_and_frequencies(self) -> None:
        tables_a = voice_wavetables_from_density(self.densities[0], self.config)
        tables_b = voice_wavetables_from_density(self.densities[1], self.config)
        self.assertGreater(float(np.max(np.abs(tables_a - tables_b))), 0.1)
        amplitudes, frequencies = density_voice_parameters(
            self.densities[0],
            self.config,
        )
        self.assertEqual(amplitudes.shape, (16,))
        self.assertEqual(frequencies.shape, (16,))
        self.assertAlmostEqual(float(np.linalg.norm(amplitudes)), 1.0)
        self.assertTrue(np.all(frequencies > 0.0))

    def test_short_render_is_deterministic_stereo_and_bounded(self) -> None:
        first = render_density_wavetable_bank(self.densities, self.config)
        second = render_density_wavetable_bank(self.densities, self.config)
        self.assertEqual(first.audio.shape, (1_600, 2))
        np.testing.assert_array_equal(first.audio, second.audio)
        self.assertTrue(np.all(np.isfinite(first.audio)))
        self.assertGreater(first.rms_after_normalization, 0.01)
        self.assertAlmostEqual(first.peak_after_normalization, 0.85)
        self.assertLessEqual(float(np.max(np.abs(first.audio))), 0.85 + 1e-12)

    def test_wav_header_and_manifest_record_direct_non_midi_synthesis(self) -> None:
        result = render_density_wavetable_bank(self.densities, self.config)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "density.wav"
            write_density_wavetable_wav(path, result)
            with wave.open(str(path), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 2)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), 1_600)

        manifest = density_wavetable_manifest(
            result,
            self.config,
            self.densities,
        )
        self.assertTrue(manifest["direct_synthesis"])
        self.assertFalse(manifest["midi_source"])
        self.assertEqual(manifest["config"]["voice_count"], 16)
        self.assertEqual(manifest["config"]["wavetable_size"], 256)
        self.assertEqual(manifest["render"]["clipped_sample_count"], 0)

    def test_rejects_non_fixed_bank_dimensions_and_invalid_density(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 256"):
            DensityWavetableRenderConfig(wavetable_size=128)
        with self.assertRaisesRegex(ValueError, "exactly 16"):
            DensityWavetableRenderConfig(voice_count=8)
        with self.assertRaisesRegex(ValueError, "shape"):
            voice_wavetables_from_density(np.eye(4), self.config)

    def test_networkx_qnn_offsets_anchor_the_selected_basis_voice(self) -> None:
        offsets = graph_qnn_voice_offsets(
            ((0, 1), (0, 2), (1, 3), (2, 3)),
            selected_mask=0b1010,
        )
        self.assertEqual(len(offsets), 16)
        self.assertEqual(offsets[0b1010], 0)
        self.assertGreater(len(set(offsets)), 1)

    def test_articulated_render_has_events_sections_and_dynamic_envelopes(self) -> None:
        config = ArticulatedDensityWavetableConfig(
            sample_rate=8_000,
            duration_seconds=1.0,
            base_frequency_hz=20.0,
            tempo_bpm=92.0,
            fade_seconds=0.005,
        )
        offsets = graph_qnn_voice_offsets(
            ((0, 1), (0, 2), (1, 3), (2, 3)),
            selected_mask=0b1010,
        )
        result = render_articulated_density_wavetable_bank(
            self.densities,
            config,
            voice_offsets=offsets,
            qnn_probabilities=np.full(16, 1.0 / 16.0),
        )
        repeated = render_articulated_density_wavetable_bank(
            self.densities,
            config,
            voice_offsets=offsets,
            qnn_probabilities=np.full(16, 1.0 / 16.0),
        )
        np.testing.assert_array_equal(result.audio, repeated.audio)
        self.assertGreater(result.event_count, 0)
        self.assertEqual(sum(result.events_by_voice), result.event_count)
        self.assertEqual(sum(result.events_by_section), result.event_count)
        self.assertEqual(len(result.events_by_section), 2)
        self.assertEqual(result.audio.shape, (8_000, 2))
        self.assertLessEqual(float(np.max(np.abs(result.audio))), 0.85 + 1e-12)

        mono = np.mean(np.abs(result.audio), axis=1)
        window_rms = np.sqrt(np.mean(mono.reshape(40, 200) ** 2, axis=1))
        self.assertGreater(float(np.std(window_rms) / np.mean(window_rms)), 0.2)

        manifest = articulated_density_wavetable_manifest(
            result,
            config,
            self.densities,
            qnn_probabilities=np.full(16, 1.0 / 16.0),
        )
        self.assertEqual(manifest["render"]["event_count"], result.event_count)
        self.assertTrue(
            manifest["articulation"][
                "qnn_probabilities_condition_event_likelihood"
            ]
        )

    def test_articulated_configuration_rejects_invalid_tempo(self) -> None:
        with self.assertRaisesRegex(ValueError, "tempo_bpm"):
            ArticulatedDensityWavetableConfig(tempo_bpm=0.0)


if __name__ == "__main__":
    unittest.main()
