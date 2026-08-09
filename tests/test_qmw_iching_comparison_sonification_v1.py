import unittest
from types import SimpleNamespace

import numpy as np

import qmw_iching_oracle8_v2 as oracle
from qmw_iching_comparison_sonification_v1 import (
    ComparisonSonificationConfig,
    build_shared_reference,
    comparison_audio_markers,
    modal_render_config,
    render_comparison_audio,
    sonification_manifest,
)
from qmw_iching_density_laplacian_bridge_v1 import build_control_frame
from qmw_iching_laplacian_modal_renderer_v1 import render_audio_from_frame


def comparison(external_primary=None, tvd=0.0, fidelity=1.0, moving_mae=0.0):
    reading, _state, _rho, _reduced, _field = oracle.consult(42, depth=1)
    local = SimpleNamespace(
        primary=reading.primary_binary,
        moving_mask=reading.moving_mask,
        transformed=reading.transformed_binary,
        change_register=reading.change_register,
        moving_probabilities=tuple(reading.moving_probabilities),
    )
    primary = local.primary if external_primary is None else int(external_primary)
    external = SimpleNamespace(
        primary=primary,
        moving_mask=local.moving_mask,
        transformed=primary ^ local.moving_mask,
        change_register=local.change_register,
        moving_probabilities=local.moving_probabilities,
    )
    return SimpleNamespace(
        seed=42, depth=1, source="aer", backend="aer_simulator", job_id="local",
        local=local, external=external, primary_tvd=tvd,
        primary_hellinger_fidelity=fidelity, moving_probability_mae=moving_mae,
    )


class TestIChingComparisonSonificationV1(unittest.TestCase):
    def setUp(self):
        self.config = ComparisonSonificationConfig(
            sample_rate=8_000, route_seconds=0.4, gap_seconds=0.05,
            coda_seconds=0.2, base_frequency_hz=90.0, mode_count=8,
        )

    def test_render_is_stereo_bounded_and_deterministic(self):
        first = render_comparison_audio(comparison(), self.config)
        second = render_comparison_audio(comparison(), self.config)
        expected = round(comparison_audio_markers(self.config)["duration_seconds"] * 8_000)
        self.assertEqual(first.shape, (expected, 2))
        self.assertTrue(np.all(np.isfinite(first)))
        self.assertLessEqual(float(np.max(np.abs(first))), self.config.output_ceiling + 1e-12)
        np.testing.assert_array_equal(first, second)

    def test_local_route_is_exactly_the_c_renderer(self):
        value = comparison()
        rendered = render_comparison_audio(value, self.config)
        frame, _rho, _rho_lu, _adj, laplacian, _field = build_control_frame(42, 1)
        expected, *_rest = render_audio_from_frame(
            frame, laplacian, modal_render_config(self.config)
        )
        route_count = round(self.config.route_seconds * self.config.sample_rate)
        np.testing.assert_array_equal(rendered[:route_count], expected)

    def test_external_h0_changes_only_the_external_modal_route(self):
        baseline = render_comparison_audio(comparison(), self.config)
        local_primary = comparison().local.primary
        changed = render_comparison_audio(
            comparison(local_primary ^ 1, tvd=0.4, fidelity=0.6, moving_mae=0.3),
            self.config,
        )
        external = round(comparison_audio_markers(self.config)["external_start_seconds"] * 8_000)
        np.testing.assert_array_equal(baseline[:external], changed[:external])
        self.assertGreater(float(np.linalg.norm(baseline[external:] - changed[external:])), 1.0)

    def test_both_routes_share_one_reference_laplacian(self):
        value = comparison(comparison().local.primary ^ 2)
        local_frame, external_frame, laplacian = build_shared_reference(value)
        self.assertEqual(local_frame.primary, value.local.primary)
        self.assertEqual(external_frame.primary, value.external.primary)
        self.assertTrue(np.allclose(laplacian, laplacian.conj().T))

    def test_coda_beating_encodes_disagreement(self):
        same = render_comparison_audio(comparison(), self.config)
        different = render_comparison_audio(
            comparison(tvd=0.5, fidelity=0.5, moving_mae=0.25), self.config
        )
        coda = round(comparison_audio_markers(self.config)["coda_start_seconds"] * 8_000)
        self.assertLess(float(np.max(np.abs(same[coda:, 0] - same[coda:, 1]))), 1e-10)
        self.assertGreater(float(np.max(np.abs(different[coda:, 0] - different[coda:, 1]))), 0.01)

    def test_manifest_states_shared_geometry_and_phase_limit(self):
        manifest = sonification_manifest(comparison(), self.config)
        self.assertEqual(manifest["mapping"]["instrument"],
                         "shared 24-node Wilson CPS magnetic graph-wave renderer")
        self.assertIn("1-3-5-7-11-13",
                      manifest["mapping"]["carrier_frequency_mapping"])
        self.assertIn("do not reconstruct phases", manifest["mapping"]["hardware_phase_claim"])
        self.assertEqual(manifest["modal_diagnostics"]["reference"],
                         "frozen local magnetic Laplacian and Wilson tuning field")


if __name__ == "__main__":
    unittest.main()
