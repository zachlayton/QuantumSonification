from __future__ import annotations

import unittest

import numpy as np

from excitation.wavefunction_sources_v1 import (
    WAVEFUNCTION_SOURCE_NAMES,
    HydrogenSuperpositionSource3D,
    PotentialWavefunctionSource,
    SchrodingerPacketSource1D,
    SchrodingerPacketSource3D,
    SphericalHarmonicSource,
    create_wavefunction_source,
)


def assert_descriptor_in_range(test_case: unittest.TestCase, descriptor) -> None:
    for name in ("energy", "phase", "probability", "structure", "coherence", "current"):
        value = getattr(descriptor, name)
        test_case.assertTrue(0.0 <= value <= 1.0, (name, value))


class WavefunctionSourceTests(unittest.TestCase):
    def test_registry_contains_original_and_new_sources(self) -> None:
        self.assertIn("schrodinger_packet", WAVEFUNCTION_SOURCE_NAMES)
        self.assertIn("schrodinger_packet_3d", WAVEFUNCTION_SOURCE_NAMES)
        self.assertIn("hydrogen_superposition_3d", WAVEFUNCTION_SOURCE_NAMES)
        self.assertIn("spherical_harmonic", WAVEFUNCTION_SOURCE_NAMES)

    def test_1d_split_step_preserves_norm(self) -> None:
        source = SchrodingerPacketSource1D(grid_shape=128)
        for _ in range(20):
            frame = source.frame(0.01)
        self.assertAlmostEqual(frame.norm, 1.0, places=10)
        self.assertEqual(frame.psi.shape, (128,))
        self.assertEqual(len(frame.probability_current), 1)
        assert_descriptor_in_range(self, frame.descriptor)

    def test_3d_split_step_preserves_norm_and_shape(self) -> None:
        source = SchrodingerPacketSource3D(grid_shape=(16, 18, 20))
        initial = source.frame(0.0)
        evolved = source.frame(0.02)
        self.assertEqual(evolved.psi.shape, (16, 18, 20))
        self.assertEqual(len(evolved.probability_current), 3)
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertFalse(np.allclose(initial.psi, evolved.psi))
        assert_descriptor_in_range(self, evolved.descriptor)

    def test_every_potential_runs_in_three_dimensions(self) -> None:
        for potential in PotentialWavefunctionSource.POTENTIALS:
            source = PotentialWavefunctionSource(
                dimensions=3,
                grid_shape=12,
                extent=12.0,
                potential=potential,
            )
            frame = source.frame(0.005)
            self.assertTrue(np.all(np.isfinite(frame.psi)), potential)
            self.assertAlmostEqual(frame.norm, 1.0, places=9)

    def test_analytic_sources_are_normalized(self) -> None:
        cases = (
            ("harmonic_oscillator", {"grid_shape": 96}),
            ("coherent_state", {"grid_shape": 96}),
            ("squeezed_state", {"grid_shape": 96}),
            ("particle_in_box", {"n_points": 96}),
            ("quantum_rotor", {"n_points": 96}),
            ("double_well", {"grid_shape": 96}),
            ("barrier_scattering", {"grid_shape": 96}),
            ("periodic_lattice", {"grid_shape": 96}),
        )
        for name, parameters in cases:
            frame = create_wavefunction_source(name, **parameters).frame(0.01)
            self.assertAlmostEqual(frame.norm, 1.0, places=9, msg=name)
            assert_descriptor_in_range(self, frame.descriptor)

    def test_hydrogen_superposition_is_continuous_3d_field(self) -> None:
        source = HydrogenSuperpositionSource3D(grid_shape=16)
        initial = source.frame(0.0)
        evolved = source.frame(0.5)
        self.assertEqual(evolved.psi.shape, (16, 16, 16))
        self.assertAlmostEqual(evolved.norm, 1.0, places=9)
        self.assertFalse(np.allclose(initial.probability, evolved.probability))

    def test_spherical_harmonic_uses_theta_phi_grid(self) -> None:
        source = SphericalHarmonicSource(n_theta=24, n_phi=48)
        frame = source.frame(0.05)
        self.assertEqual(frame.psi.shape, (24, 48))
        self.assertEqual(frame.coordinates[0].shape, (24,))
        self.assertEqual(frame.coordinates[1].shape, (48,))
        self.assertAlmostEqual(frame.norm, 1.0, places=9)

    def test_reset_restores_initial_packet(self) -> None:
        source = SchrodingerPacketSource3D(grid_shape=14)
        initial = source.frame(0.0).psi.copy()
        source.frame(0.1)
        source.reset()
        restored = source.frame(0.0).psi
        self.assertTrue(np.allclose(initial, restored))


if __name__ == "__main__":
    unittest.main()
