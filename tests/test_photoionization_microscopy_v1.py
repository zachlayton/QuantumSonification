from __future__ import annotations

import math
from pathlib import Path
import runpy
import unittest

import numpy as np

from photoionization_microscopy_v1 import (
    PhotoionizationConfig,
    PhotoionizationMicroscopySource,
    PhotoionizationOSCPublisher,
    RESONANCE_CATALOG,
    encode_osc_message,
    resonance_by_label,
)
from photoionization_microscopy_v1.model import interpolate_reference_profile
from photoionization_microscopy_v1.reference_data import REFERENCE_PROFILES
from photoionization_microscopy_v1.geometry import (
    DensityArrayGeometryConfig,
    DensityGrid,
    RasterGeometryConfig,
    load_density_grid_npz,
    marching_tetrahedra,
    mesh_edge_diagnostics,
    sample_density_grid_volume,
    sample_axisymmetric_volume,
)


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class PhotoionizationMicroscopyTests(unittest.TestCase):
    def test_table_i_catalog_is_complete(self) -> None:
        self.assertEqual(len(RESONANCE_CATALOG), 14)
        resonance = resonance_by_label("(1,28,0)")
        self.assertEqual(resonance.family, "red")
        self.assertTrue(math.isclose(resonance.energy_cm_inverse, -169.617))

    def test_unknown_resonance_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            resonance_by_label("(99,99,0)")

    def test_anchor_fields_return_digitized_curves(self) -> None:
        for field_t, expected in REFERENCE_PROFILES.items():
            actual = interpolate_reference_profile(field_t)
            np.testing.assert_allclose(actual, expected, atol=1.0e-12)
            self.assertTrue(math.isclose(float(actual.max()), 1.0, abs_tol=1.0e-12))

    def test_intermediate_field_is_normalized_linear_morph(self) -> None:
        actual = interpolate_reference_profile(1.0)
        expected = 0.5 * (REFERENCE_PROFILES[0.0] + REFERENCE_PROFILES[2.0])
        expected /= float(expected.max())
        np.testing.assert_allclose(actual, expected, atol=1.0e-12)

    def test_reference_range_is_enforced(self) -> None:
        with self.assertRaises(ValueError):
            PhotoionizationConfig(magnetic_field_t=8.1)
        source = PhotoionizationMicroscopySource()
        with self.assertRaises(ValueError):
            source.set_magnetic_field(-0.1)

    def test_reference_conditions_cannot_be_relabelled(self) -> None:
        with self.assertRaisesRegex(ValueError, "Figure 5 conditions"):
            PhotoionizationConfig(electric_field_v_per_cm=100.0)
        with self.assertRaisesRegex(ValueError, "Figure 5 conditions"):
            PhotoionizationConfig(resonance_label="(0,29,0)")

    def test_figure_five_energy_anchors_are_preserved(self) -> None:
        source = PhotoionizationMicroscopySource()
        expected = {0.0: -169.617, 2.0: -169.103, 4.0: -167.764, 6.0: -166.048, 8.0: -164.020}
        for field_t, energy in expected.items():
            source.set_magnetic_field(field_t)
            self.assertTrue(math.isclose(source.state.resonance_energy_cm_inverse, energy))

    def test_magnetic_focusing_reduces_radial_rms(self) -> None:
        source = PhotoionizationMicroscopySource()
        rms_zero = source.state.radial_rms_um
        source.set_magnetic_field(8.0)
        self.assertLess(source.state.radial_rms_um, rms_zero)
        self.assertLess(source.state.radial_extent_um, 0.06)

    def test_eight_lane_adapter_is_normalized(self) -> None:
        source = PhotoionizationMicroscopySource()
        self.assertEqual(source.state.detector_lanes.shape, (8,))
        self.assertTrue(math.isclose(float(source.state.detector_lanes.sum()), 1.0))

    def test_single_dominant_peak_remains_at_eight_tesla(self) -> None:
        source = PhotoionizationMicroscopySource(PhotoionizationConfig(magnetic_field_t=8.0))
        self.assertEqual(len(source.state.peak_rho_um), 1)
        self.assertLess(source.state.peak_rho_um[0], 0.02)

    def test_arrays_are_defensive_copies(self) -> None:
        source = PhotoionizationMicroscopySource()
        arrays = source.arrays()
        arrays["photoionization_detector_flux"][0] = 999.0
        self.assertNotEqual(source.state.detector_flux[0], 999.0)

    def test_descriptor_is_bounded(self) -> None:
        source = PhotoionizationMicroscopySource(PhotoionizationConfig(magnetic_field_t=5.0))
        descriptor = source.descriptor
        for value in (
            descriptor.energy,
            descriptor.phase,
            descriptor.probability,
            descriptor.coherence,
            descriptor.entanglement,
            descriptor.spin,
            descriptor.topology,
            descriptor.curvature,
        ):
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_sweep_advances_and_loops(self) -> None:
        source = PhotoionizationMicroscopySource(
            PhotoionizationConfig(magnetic_field_t=7.5, sweep_rate_t_per_second=1.0)
        )
        source.step(1.0)
        self.assertTrue(math.isclose(source.state.magnetic_field_t, 0.5))
        with self.assertRaises(ValueError):
            source.step(-1.0)

    def test_osc_publisher_uses_dedicated_namespace(self) -> None:
        client = RecordingClient()
        source = PhotoionizationMicroscopySource()
        PhotoionizationOSCPublisher(client).publish(source)
        addresses = {address for address, _ in client.messages}
        self.assertIn("/qmw/photoionization/detector/radial_flux", addresses)
        self.assertIn("/qmw/photoionization/detector/lanes", addresses)
        self.assertIn("/qmw/photoionization/reference_status", addresses)
        self.assertNotIn("/qmw/source/wavepacket/probability", addresses)

    def test_reference_status_is_scientifically_explicit(self) -> None:
        status = PhotoionizationMicroscopySource().state.reference_status.lower()
        self.assertIn("digitized", status)
        self.assertIn("not newly calculated", status)

    def test_processing_triangle_sweep_reaches_both_bounds(self) -> None:
        module = runpy.run_path(
            str(Path(__file__).parent / "examples/photoionization_processing_stream.py"),
            run_name="photoionization_processing_stream_test",
        )
        triangle_field = module["triangle_field"]
        self.assertTrue(math.isclose(triangle_field(0.0, 24.0), 0.0))
        self.assertTrue(math.isclose(triangle_field(6.0, 24.0), 4.0))
        self.assertTrue(math.isclose(triangle_field(12.0, 24.0), 8.0))
        self.assertTrue(math.isclose(triangle_field(18.0, 24.0), 4.0))
        self.assertTrue(math.isclose(triangle_field(24.0, 24.0), 0.0))

    def test_standard_library_osc_encoder(self) -> None:
        packet = encode_osc_message("/qmw/test", [1.5, 2, "ok"])
        self.assertTrue(packet.startswith(b"/qmw/test\x00"))
        self.assertIn(b",fis\x00", packet)

    def test_processing_spatial_reference_atlas_is_complete(self) -> None:
        data = (
            Path(__file__).parent
            / "photoionization_microscopy_v1"
            / "processing"
            / "QMWPhotoionizationMicroscopyV1"
            / "data"
        )
        figure5 = [data / f"figure5_spatial_b{field}.png" for field in (0, 2, 4, 6, 8)]
        figure4 = [
            data / f"figure4_{state}_b{field}.png"
            for state in ("red_0_29_0", "red_3_26_0", "blue_23_0_0", "blue_20_3_0")
            for field in (0, 6)
        ]
        for image_path in figure5 + figure4:
            self.assertTrue(image_path.is_file(), image_path)
            self.assertGreater(image_path.stat().st_size, 1_000)

    def test_axisymmetric_volume_revolution(self) -> None:
        density = np.zeros((9, 17), dtype=float)
        density[:4, 5:12] = 1.0
        config = RasterGeometryConfig(axial_resolution=20, transverse_resolution=18)
        volume, axes = sample_axisymmetric_volume(density, config)
        self.assertEqual(volume.shape, (20, 18, 18))
        self.assertTrue(np.allclose(volume[:, :, :], volume[:, :, ::-1]))
        self.assertEqual(tuple(len(axis) for axis in axes), volume.shape)

    def test_marching_tetrahedra_closes_a_sphere(self) -> None:
        axis = np.linspace(-1.2, 1.2, 18)
        x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
        samples = 1.0 - (x * x + y * y + z * z)
        vertices, faces = marching_tetrahedra(samples, (axis, axis, axis), 0.0)
        self.assertGreater(len(vertices), 500)
        self.assertGreater(len(faces), 1_000)
        self.assertEqual(mesh_edge_diagnostics(faces)["boundary_edges"], 0)
        self.assertEqual(mesh_edge_diagnostics(faces)["nonmanifold_edges"], 0)

    def test_numerical_density_grid_revolves_without_images(self) -> None:
        rho = np.linspace(0.0, 0.2, 12)
        z = np.linspace(-0.5, 0.1, 24)
        rr, zz = np.meshgrid(rho, z, indexing="ij")
        density = np.exp(-((rr / 0.06) ** 2 + ((zz + 0.15) / 0.18) ** 2))
        grid = DensityGrid(density, rho, z, {"state": "synthetic_test_only"})
        config = DensityArrayGeometryConfig(axial_resolution=22, transverse_resolution=18)
        volume, axes = sample_density_grid_volume(grid, config)
        self.assertEqual(volume.shape, (22, 18, 18))
        self.assertEqual(tuple(len(axis) for axis in axes), volume.shape)
        self.assertTrue(np.allclose(volume, volume[:, :, ::-1]))

    def test_density_npz_contract_accepts_complex_wavefunction(self) -> None:
        import tempfile

        rho = np.linspace(0.0, 0.2, 5)
        z = np.linspace(-0.5, 0.1, 7)
        psi = np.ones((5, 7), dtype=np.complex128) * (1.0 + 1.0j)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "grid.npz"
            np.savez(path, rho_um=rho, z_um=z, psi_rho_z=psi, metadata_json='{"B_T": 6}')
            grid = load_density_grid_npz(path)
        np.testing.assert_allclose(grid.density_rho_z, 2.0)
        self.assertEqual(grid.metadata["B_T"], 6)
        self.assertEqual(grid.metadata["loaded_quantity"], "abs(psi_rho_z)^2")


if __name__ == "__main__":
    unittest.main()
