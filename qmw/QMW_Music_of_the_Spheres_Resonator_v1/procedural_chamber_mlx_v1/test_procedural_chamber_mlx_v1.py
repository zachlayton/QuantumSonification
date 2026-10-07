#!/usr/bin/env python3
"""Small standard-library regression tests for procedural_chamber_mlx_v1."""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

import mlx.core as mx

from procedural_chamber_mlx_v1 import (
    AcousticConfig,
    ChamberConfig,
    RenderConfig,
    analyze_geometry,
    analyze_surface_spectrum,
    build_acoustic_model,
    construct_chamber_mesh,
    is_prime,
    render_stereo_ir_mlx,
    run,
)


class ProceduralChamberMLXV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mx.set_default_device(mx.cpu)
        cls.chamber = ChamberConfig(
            shape="tetra",
            subdivisions=2,
            radius_m=3.0,
            deformation=0.22,
            fractal_octaves=3,
            seed=1234,
        )
        cls.acoustics = AcousticConfig(
            sample_rate=8_000,
            duration_s=0.25,
            rt60_s=0.6,
            hf_cutoff_hz=3_000.0,
            n_early_reflections=8,
            chunk_bins=128,
        )
        cls.mesh = construct_chamber_mesh(cls.chamber)
        cls.geometry = analyze_geometry(cls.mesh)
        cls.spectral = analyze_surface_spectrum(cls.mesh, cls.acoustics.n_lines)
        cls.model = build_acoustic_model(
            cls.mesh, cls.geometry, cls.spectral, cls.acoustics
        )

    def test_geometry_is_non_degenerate(self) -> None:
        self.assertGreater(self.geometry.volume_m3, 0.0)
        self.assertGreater(self.geometry.surface_area_m2, 0.0)
        self.assertGreaterEqual(self.geometry.vertex_count, 17)

    def test_feedback_matrix_is_orthogonal(self) -> None:
        a = self.model.feedback_matrix
        identity_error = mx.max(mx.abs(a.T @ a - mx.eye(16)))
        mx.eval(identity_error)
        self.assertLess(float(identity_error.item()), 2.0e-4)

    def test_delay_lengths_are_unique_primes(self) -> None:
        delays = self.model.delay_samples
        self.assertEqual(len(delays), 16)
        self.assertEqual(len(set(delays)), 16)
        self.assertTrue(all(is_prime(value) for value in delays))

    def test_ir_is_finite_stereo(self) -> None:
        stereo, stats = render_stereo_ir_mlx(self.model, self.acoustics)
        finite = mx.all(mx.isfinite(stereo))
        mx.eval(finite)
        self.assertTrue(bool(finite.item()))
        self.assertEqual(stereo.shape, (2_000, 2))
        self.assertTrue(math.isclose(float(stats["post_normalization_peak"]), 0.95, abs_tol=1e-4))

    def test_export_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run(
                self.chamber,
                self.acoustics,
                RenderConfig(
                    output_dir=temp_dir,
                    name="regression_chamber",
                    device="cpu",
                    render_ir=False,
                ),
            )
            self.assertTrue(Path(result["obj"]).exists())
            self.assertTrue(Path(result["json"]).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
