from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import wave

import numpy as np

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame
from qmw_iching_laplacian_modal_renderer_v1 import (
    RenderConfig,
    _compress_complex_activity,
    _degenerate_clusters,
    graph_wave_transfer_curve,
    modal_parameters_from_laplacian,
    render_audio,
    render_audio_from_frame,
    wilson_hexagram_tuning,
    wilson_node_parameters_from_laplacian,
    write_wav,
)


class TestIChingLaplacianModalRenderer(unittest.TestCase):
    def test_degenerate_clusters_do_not_split_close_eigenvalues(self):
        clusters = _degenerate_clusters(np.array([2.0, 0.0, 1.0, 1.0 + 1e-8]), 1e-6)
        self.assertEqual(clusters, [[1], [2, 3], [0]])

    def test_numerical_near_zero_mode_cannot_set_frequency_reference(self):
        hadamard = 0.5 * np.array([
            [1, 1, 1, 1], [1, -1, 1, -1],
            [1, 1, -1, -1], [1, -1, -1, 1],
        ], dtype=float)
        eigenvalues = np.array([0.0, 1e-10, 1.0, 4.0])
        laplacian = (hadamard * eigenvalues) @ hadamard.T
        frequencies, *_ = modal_parameters_from_laplacian(
            SimpleNamespace(primary=0), laplacian,
            RenderConfig(
                mode_count=4, base_frequency_hz=90.0,
                frequency_mapping="logarithmic",
            ),
        )
        # Exact and numerical zero share one basis-invariant cluster voice.
        np.testing.assert_allclose(np.sort(frequencies), [90.0, 90.0, 225.0])
        self.assertLess(float(frequencies.max()), 4320.0)

    def test_resolved_modes_may_use_full_twenty_kilohertz_range(self):
        hadamard = np.array([[1, 1], [1, -1]], dtype=float) / np.sqrt(2.0)
        laplacian = (hadamard * np.array([1.0, 62_500.0])) @ hadamard.T
        frequencies, *_ = modal_parameters_from_laplacian(
            SimpleNamespace(primary=0), laplacian,
            RenderConfig(
                mode_count=2, base_frequency_hz=80.0,
                frequency_mapping="linear",
            ),
        )
        np.testing.assert_allclose(np.sort(frequencies), [80.0, 20_000.0])

    def test_logarithmic_mapping_compresses_wide_resolved_ratios(self):
        hadamard = np.array([[1, 1], [1, -1]], dtype=float) / np.sqrt(2.0)
        laplacian = (hadamard * np.array([1.0, 10_000.0])) @ hadamard.T
        frequencies, *_ = modal_parameters_from_laplacian(
            SimpleNamespace(primary=0), laplacian,
            RenderConfig(
                mode_count=2, base_frequency_hz=90.0,
                frequency_mapping="logarithmic",
            ),
        )
        self.assertAlmostEqual(float(frequencies.min()), 90.0)
        self.assertGreater(float(frequencies.max()), 500.0)
        self.assertLess(float(frequencies.max()), 1_200.0)

    def test_two_node_wave_reaches_opposite_node(self):
        laplacian = np.array([[1.0, -1.0], [-1.0, 1.0]])
        arrival = np.pi / np.sqrt(2.0)
        times = np.linspace(0.0, 2.0 * arrival, 2001)
        result = graph_wave_transfer_curve(
            SimpleNamespace(primary=0, transformed=1), laplacian, times
        )
        self.assertAlmostEqual(result["p0"], 0.0, places=12)
        self.assertAlmostEqual(result["max_transfer"], 1.0, places=8)
        self.assertAlmostEqual(result["first_peak_time"], arrival, places=3)

    def test_same_node_diagnostic_is_survival_not_transport(self):
        laplacian = np.array([[1.0, -1.0], [-1.0, 1.0]])
        result = graph_wave_transfer_curve(
            SimpleNamespace(primary=0, transformed=0), laplacian,
            np.linspace(0.0, 5.0, 501),
        )
        self.assertTrue(result["primary_equals_transformed"])
        self.assertAlmostEqual(result["p0"], 1.0, places=12)

    def test_real_reading_modal_parameters_are_physical(self):
        frame, _, _, _, laplacian, _ = build_control_frame(seed=42, depth=1, revision=7)
        config = RenderConfig(
            mode_count=12, duration_seconds=0.05,
            frequency_mapping="logarithmic",
        )
        frequencies, decays, pans, coefficients, rates, retained = (
            modal_parameters_from_laplacian(frame, laplacian, config)
        )
        count = len(frequencies)
        self.assertGreater(count, 0)
        self.assertTrue(all(len(values) == count for values in (decays, pans, coefficients, rates)))
        self.assertTrue(np.all(frequencies > 0))
        self.assertTrue(np.all(decays > 0))
        self.assertTrue(np.all(np.abs(pans) <= 1.0))
        self.assertTrue(np.all(coefficients >= 0))
        self.assertGreater(retained, 0.0)
        self.assertLessEqual(retained, 1.0 + 1e-10)

    def test_wilson_field_is_the_complete_six_factor_pascal_aggregate(self):
        config = RenderConfig(sample_rate=48_000)
        tones = wilson_hexagram_tuning(config)
        self.assertEqual(len(tones), 64)
        self.assertEqual(
            [sum(tone.grade == grade for tone in tones) for grade in range(7)],
            [1, 6, 15, 20, 15, 6, 1],
        )
        # Empty subset: (1 / 13) folded by four octaves.  The top-line factor
        # 13 is the exact 1/1 audition anchor.
        self.assertEqual((tones[0].ratio_numerator, tones[0].ratio_denominator), (16, 13))
        self.assertEqual((tones[1 << 5].ratio_numerator, tones[1 << 5].ratio_denominator), (1, 1))
        self.assertEqual(tones[0].factors, ())
        self.assertEqual(tones[(1 << 1) | (1 << 4)].factors, (3, 11))

    def test_wilson_node_bank_uses_full_graph_wave_and_retains_primary(self):
        laplacian = np.zeros((64, 64), dtype=float)
        frame = SimpleNamespace(primary=37)
        config = RenderConfig(
            sample_rate=8_000, duration_seconds=0.05, mode_count=4,
            graph_control_rate_hz=100.0,
        )
        tones, frequencies, decays, pans, wave_field, retained = (
            wilson_node_parameters_from_laplacian(frame, laplacian, config)
        )
        self.assertIn(37, [tone.hexagram for tone in tones])
        primary_row = [tone.hexagram for tone in tones].index(37)
        np.testing.assert_allclose(wave_field[primary_row], 1.0)
        self.assertEqual(wave_field.shape[0], 4)
        self.assertEqual(len(frequencies), len(decays))
        self.assertEqual(len(frequencies), len(pans))
        np.testing.assert_allclose(decays, config.max_decay_seconds)
        self.assertAlmostEqual(retained, 1.0)

    def test_wilson_activity_compression_reveals_quiet_nodes_without_adding_energy(self):
        wave = np.array([
            [1.0 + 0.0j, 0.0 + 0.5j],
            [0.01 + 0.0j, 0.005 + 0.0j],
        ])
        compressed = _compress_complex_activity(wave, 0.5)
        np.testing.assert_allclose(
            np.sum(np.abs(compressed) ** 2, axis=0),
            np.sum(np.abs(wave) ** 2, axis=0),
        )
        self.assertGreater(
            abs(compressed[1, 0] / compressed[0, 0]),
            abs(wave[1, 0] / wave[0, 0]),
        )
        self.assertAlmostEqual(float(np.angle(compressed[0, 1])), np.pi / 2)

    def test_wilson_probe_is_localized_but_chordal_at_onset(self):
        adjacency = np.zeros((64, 64), dtype=float)
        for node in range(64):
            for line in range(6):
                adjacency[node, node ^ (1 << line)] = 1.0
        laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
        config = RenderConfig(
            sample_rate=8_000, duration_seconds=0.05, mode_count=64,
            graph_control_rate_hz=100.0, wilson_probe_blur=1.0,
        )
        tones, _frequencies, _decays, _pans, wave_field, retained = (
            wilson_node_parameters_from_laplacian(
                SimpleNamespace(primary=10), laplacian, config
            )
        )
        nodes = [tone.hexagram for tone in tones]
        onset = np.abs(wave_field[:, 0])
        primary_row = nodes.index(10)
        self.assertEqual(int(np.argmax(onset)), primary_row)
        self.assertGreater(int(np.sum(onset > 0.02)), 1)
        self.assertAlmostEqual(float(np.linalg.norm(onset)), 1.0)
        self.assertAlmostEqual(retained, 1.0)

    def test_short_render_writes_stereo_pcm(self):
        config = RenderConfig(
            sample_rate=8_000, duration_seconds=0.05, seed=42, depth=1,
            mode_count=8, base_frequency_hz=80.0,
        )
        audio, _frame, _frequencies, _decays, _pans, retained = render_audio(config)
        self.assertEqual(audio.shape, (400, 2))
        self.assertTrue(np.all(np.isfinite(audio)))
        self.assertGreater(float(np.max(np.abs(audio))), 0.0)
        self.assertGreater(retained, 0.0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "render.wav"
            write_wav(path, audio, config.sample_rate)
            with wave.open(str(path), "rb") as handle:
                self.assertEqual(handle.getnchannels(), 2)
                self.assertEqual(handle.getsampwidth(), 2)
                self.assertEqual(handle.getframerate(), 8_000)
                self.assertEqual(handle.getnframes(), 400)

    def test_frozen_frame_renderer_does_not_recast(self):
        frame, _, _, _, laplacian, _ = build_control_frame(seed=42, depth=1, revision=88)
        config = RenderConfig(
            sample_rate=8_000, duration_seconds=0.025, mode_count=8,
            base_frequency_hz=80.0,
        )
        audio, frequencies, decays, pans, retained = render_audio_from_frame(
            frame, laplacian, config
        )
        self.assertEqual(frame.revision, 88)
        self.assertEqual(audio.shape, (200, 2))
        self.assertEqual(len(frequencies), len(decays))
        self.assertEqual(len(frequencies), len(pans))
        self.assertGreater(retained, 0.0)


if __name__ == "__main__":
    unittest.main()
