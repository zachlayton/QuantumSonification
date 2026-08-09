import tempfile
import unittest
from pathlib import Path

import numpy as np

from feedback.render_memory_oracle_tanglecube_v1 import (
    DEFAULT_TANGLE_PACKET,
    TangleCubeOracleRenderConfig,
    axis_angle_rotation,
    geometry_reverb_frequency_ratios,
    ideal_grover_angles,
    load_tanglecube_modal_field,
    oracle_rotation_path,
    orientation_sonification_controls,
    reference_memory_oracle,
    render_tanglecube_oracle_audio,
    smooth_state_trajectory,
    slewed_oracle_orientations,
    spatial_modal_coupling,
)


class TangleCubeOracleRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field = load_tanglecube_modal_field(DEFAULT_TANGLE_PACKET)
        cls.oracle = reference_memory_oracle()

    def test_real_tanglecube_packet_is_spatial(self):
        self.assertEqual(self.field.vertices.shape, (7828, 3))
        self.assertEqual(self.field.eigenvectors.shape, (7828, 24))
        self.assertEqual(len(self.field.frequencies_hz), 24)

    def test_axis_angle_is_a_proper_rotation(self):
        rotation = axis_angle_rotation(np.array([1.0, 2.0, -0.5]), 0.73)
        np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(float(np.linalg.det(rotation)), 1.0, places=12)

    def test_oracle_path_uses_all_eigenphases(self):
        phases, axes, orientations = oracle_rotation_path(self.oracle)
        self.assertEqual(phases.shape, (8,))
        self.assertEqual(axes.shape, (8, 3))
        self.assertEqual(orientations.shape, (8, 3, 3))
        np.testing.assert_allclose(np.linalg.norm(axes, axis=1), 1.0, atol=1e-12)
        np.testing.assert_allclose(phases, self.oracle.phase_angles, atol=1e-12)

    def test_slew_starts_stationary_and_reaches_exact_targets(self):
        phases, axes, targets = oracle_rotation_path(self.oracle)
        events = np.arange(8, dtype=np.float64) * 2.0 + 0.5
        times = np.concatenate(([0.0], events + 1.0))
        slewed = slewed_oracle_orientations(times, events, phases, axes, 1.0)
        np.testing.assert_allclose(slewed[0], np.eye(3), atol=1e-12)
        np.testing.assert_allclose(slewed[1:], targets, atol=1e-12)

    def test_grover_rotation_is_sixty_degrees_per_iteration(self):
        theta, angles = ideal_grover_angles(3, 2, 7)
        self.assertAlmostEqual(np.degrees(theta), 30.0)
        np.testing.assert_allclose(np.degrees(angles), [30, 90, 150, 210, 270, 330, 390])
        interpolated = smooth_state_trajectory(
            np.array([0.0, 0.5, 1.0]),
            np.array([0.0, 1.0]),
            np.array([theta, 3.0 * theta]),
        )
        self.assertAlmostEqual(interpolated[1], 2.0 * theta)

    def test_rotation_changes_actual_modal_coupling(self):
        source = np.array([0.82, 0.31, 0.48])
        listener = np.array([-0.38, 0.86, 0.34])
        first, first_indices = spatial_modal_coupling(
            self.field, np.eye(3), source, listener, 0.2
        )
        rotated, rotated_indices = spatial_modal_coupling(
            self.field, axis_angle_rotation(np.array([0.2, 1.0, 0.4]), 1.1), source, listener, 0.2
        )
        self.assertNotEqual(first_indices, rotated_indices)
        self.assertGreater(float(np.linalg.norm(first - rotated)), 0.1)

    def test_orientation_controls_pan_and_modal_aperture(self):
        identity = orientation_sonification_controls(np.eye(3), 24, 0.92, 0.88)
        turned = orientation_sonification_controls(
            axis_angle_rotation(np.array([0.3, 0.8, 0.2]), 1.4),
            24,
            0.92,
            0.88,
            sonic_angle=-1.2,
        )
        self.assertNotAlmostEqual(identity[0], turned[0])
        self.assertNotAlmostEqual(identity[1], turned[1])
        self.assertGreater(float(np.linalg.norm(identity[2] - turned[2])), 0.1)

    def test_geometry_reverb_rotation_morphs_frequencies(self):
        orientations = np.asarray(
            [
                np.eye(3),
                axis_angle_rotation(np.array([0.3, 0.8, 0.2]), 1.4),
            ]
        )
        ratios = geometry_reverb_frequency_ratios(
            orientations, np.array([0.0, -1.2]), 24
        )
        np.testing.assert_allclose(ratios[0], np.ones(24), atol=1e-12)
        self.assertGreater(float(np.max(np.abs(ratios[1] - 1.0))), 0.02)

    def test_short_render_is_finite_stereo_and_rotation_is_audible(self):
        with tempfile.TemporaryDirectory() as directory:
            config = TangleCubeOracleRenderConfig(
                output_path=Path(directory) / "rotating.wav",
                static_output_path=Path(directory) / "static.wav",
                diagnostics_path=Path(directory) / "render.json",
                sample_rate=8_000,
                duration_seconds=1.0,
                rotation_slew_seconds=0.06,
            )
            rotating, diagnostics = render_tanglecube_oracle_audio(config, rotate_geometry=True)
            static, _ = render_tanglecube_oracle_audio(config, rotate_geometry=False)
        self.assertEqual(rotating.shape, (8_000, 2))
        self.assertTrue(np.all(np.isfinite(rotating)))
        self.assertLessEqual(float(np.max(np.abs(rotating))), config.output_ceiling + 1e-12)
        self.assertGreater(float(np.linalg.norm(rotating - static)), 0.05)
        self.assertGreater(int(diagnostics["unique_spatial_samples"]), 1)
        self.assertGreater(int(diagnostics["unique_control_vertex_samples"]), 1)
        self.assertGreater(diagnostics["pan_range"][1] - diagnostics["pan_range"][0], 0.1)
        self.assertGreater(
            diagnostics["mode_center_range"][1] - diagnostics["mode_center_range"][0], 0.1
        )
        self.assertEqual(diagnostics["source_representation"], "exact_pauli64")
        self.assertEqual(diagnostics["source_mode_count"], 64)
        self.assertEqual(diagnostics["tangle_reverb_mode_count"], 24)
        self.assertEqual(len(diagnostics["pauli_active_coefficients"]), 7)
        self.assertEqual(
            diagnostics["frequency_morph_model"],
            "qmw_realtime_surface_reverb_delay_deformation",
        )
        self.assertGreater(
            diagnostics["frequency_ratio_range"][1]
            - diagnostics["frequency_ratio_range"][0],
            0.02,
        )
        self.assertEqual(diagnostics["wet_ring_mod_depth"], config.wet_ring_mod_depth)


if __name__ == "__main__":
    unittest.main()
