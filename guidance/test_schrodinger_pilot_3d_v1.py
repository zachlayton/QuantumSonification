import unittest

import numpy as np

from guidance.schrodinger_pilot_3d_v1 import SchrodingerPilot3D


class SchrodingerPilot3DTests(unittest.TestCase):
    def test_real_1s_orbital_has_zero_bohm_velocity(self):
        pilot = SchrodingerPilot3D.hydrogenic(
            grid_shape=24,
            extent=18.0,
            states=((1, 0, 0, 1.0 + 0.0j),),
        )
        points = np.array([[3.0, 0.0, 0.0], [0.0, 3.0, 0.0], [2.0, 2.0, 0.0]])
        velocity, _density, valid = pilot.field.velocity_at(points)
        self.assertTrue(np.all(valid))
        np.testing.assert_allclose(velocity, 0.0, atol=2e-12)

    def test_complex_m_one_orbital_has_azimuthal_circulation(self):
        pilot = SchrodingerPilot3D.hydrogenic(
            grid_shape=24,
            extent=18.0,
            states=((2, 1, 1, 1.0 + 0.0j),),
        )
        points = np.array([[3.0, 0.0, 0.0], [0.0, 3.0, 0.0]])
        spherical = pilot.spherical_velocity_components(points)
        np.testing.assert_allclose(spherical[:, 0], 0.0, atol=2e-3)
        np.testing.assert_allclose(spherical[:, 1], 0.0, atol=2e-3)
        np.testing.assert_allclose(spherical[:, 2], 1.0 / 3.0, atol=0.008)

    def test_analytic_hydrogen_evolution_preserves_norm_and_trajectories(self):
        pilot = SchrodingerPilot3D.hydrogenic(
            grid_shape=24,
            extent=18.0,
            states=((1, 0, 0, 1.0 + 0.0j), (2, 1, 1, 0.0 + 0.7j)),
        )
        pilot.seed_trajectories(300, seed=21)
        for _ in range(10):
            pilot.step(0.01)
        self.assertAlmostEqual(pilot.field.norm, 1.0, places=12)
        self.assertAlmostEqual(pilot.time, 0.1, places=12)
        self.assertTrue(np.all(np.isfinite(pilot.trajectory_positions)))

    def test_free_gaussian_propagation_preserves_norm(self):
        pilot = SchrodingerPilot3D.gaussian(
            grid_shape=24,
            extent=18.0,
            center=(-2.0, 0.0, 0.0),
            sigma=1.0,
            momentum=(1.5, 0.0, 0.0),
        )
        initial_x = pilot.snapshot().expectation_position[0]
        for _ in range(10):
            pilot.step(0.01)
        final = pilot.snapshot()
        self.assertAlmostEqual(final.norm, 1.0, places=12)
        self.assertAlmostEqual(final.expectation_position[0] - initial_x, 0.15, delta=0.01)


if __name__ == "__main__":
    unittest.main()
