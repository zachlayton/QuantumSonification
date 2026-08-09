import unittest

import numpy as np

from guidance.schrodinger_pilot_2d_v1 import SchrodingerPilot2D


class SchrodingerPilot2DTests(unittest.TestCase):
    def test_commensurate_plane_wave_velocity(self):
        length = 12.0
        wavevector = (2.0 * np.pi * 2 / length, -2.0 * np.pi / length)
        pilot = SchrodingerPilot2D.plane_wave(
            grid_shape=64,
            extent=length,
            wavevector=wavevector,
            mass=2.0,
            hbar=1.5,
        )
        velocity, _density, valid = pilot.field.velocity_at(np.array([0.3, -0.4]))
        self.assertTrue(bool(valid))
        np.testing.assert_allclose(
            velocity, 1.5 * np.asarray(wavevector) / 2.0, atol=1e-11
        )

    def test_vortex_winding_and_circulation_agree(self):
        pilot = SchrodingerPilot2D.vortex(
            grid_shape=96, extent=16.0, sigma=2.0, charge=1
        )
        winding = pilot.phase_winding(2.0)
        circulation = pilot.circulation(2.0)
        self.assertAlmostEqual(winding, 2.0 * np.pi, delta=0.02)
        self.assertAlmostEqual(circulation, 2.0 * np.pi, delta=0.04)
        center_index = tuple(np.argmin(np.abs(axis)) for axis in pilot.axes)
        self.assertFalse(pilot.field.valid_mask[center_index])

    def test_free_gaussian_ensemble_remains_born_distributed(self):
        pilot = SchrodingerPilot2D.gaussian(
            grid_shape=64,
            extent=16.0,
            center=(-2.0, 0.0),
            sigma=0.9,
            momentum=(2.0, 0.0),
        )
        pilot.seed_trajectories(5000, seed=123)
        for _ in range(20):
            pilot.step(0.01)
        snapshot = pilot.snapshot()
        empirical_mean = np.mean(pilot.trajectory_positions, axis=0)
        empirical_spread = np.std(pilot.trajectory_positions, axis=0)
        np.testing.assert_allclose(
            empirical_mean, snapshot.expectation_position, atol=0.035
        )
        np.testing.assert_allclose(empirical_spread, snapshot.spread, atol=0.035)
        self.assertAlmostEqual(snapshot.norm, 1.0, places=12)

    def test_harmonic_ground_is_bounded_and_energy_stable(self):
        pilot = SchrodingerPilot2D.harmonic_ground(
            grid_shape=64, extent=14.0, omega=1.0
        )
        initial = pilot.snapshot()
        for _ in range(60):
            pilot.step(0.005)
        final = pilot.snapshot()
        self.assertAlmostEqual(final.norm, 1.0, places=12)
        self.assertAlmostEqual(final.energy, initial.energy, delta=3e-7)
        np.testing.assert_allclose(final.spread, initial.spread, atol=2e-5)

    def test_double_slit_experiment_develops_multiple_fringes(self):
        pilot = SchrodingerPilot2D.double_slit(
            emerging=True,
            grid_shape=(96, 80),
            extent=(20.0, 14.0),
            slit_separation=2.4,
            slit_width=0.5,
        )
        for _ in range(50):
            pilot.step(0.02)
        x_index = int(np.argmin(np.abs(pilot.axes[0] - 2.0)))
        line = pilot.field.density[x_index]
        peaks = int(np.sum((line[1:-1] > line[:-2]) & (line[1:-1] > line[2:])))
        self.assertGreaterEqual(peaks, 3)
        self.assertAlmostEqual(pilot.field.norm, 1.0, places=12)


if __name__ == "__main__":
    unittest.main()

