import unittest

import numpy as np

from guidance.two_particle_pilot_1d_v1 import TwoParticlePilot1D


class TwoParticlePilot1DTests(unittest.TestCase):
    def test_joint_phase_makes_particle_one_velocity_depend_on_particle_two(self):
        pilot = TwoParticlePilot1D.entangled(
            n_points=96, phase_coupling=0.65
        )
        response = pilot.nonlocal_response(
            fixed_x1=0.5,
            x2_values=np.array([-1.0, 0.0, 1.0]),
        )
        np.testing.assert_allclose(response, [-0.65, 0.0, 0.65], atol=2e-4)
        self.assertEqual(pilot.field.coordinate_semantics, "two_particle_1d")

    def test_separable_state_has_no_remote_velocity_dependence(self):
        pilot = TwoParticlePilot1D.separable(n_points=96)
        response = pilot.nonlocal_response(
            fixed_x1=0.25,
            x2_values=np.array([-2.0, 0.0, 2.0]),
        )
        np.testing.assert_allclose(response, response[0], atol=2e-5)

    def test_joint_norm_and_seeded_configurations_survive_evolution(self):
        pilot = TwoParticlePilot1D.entangled(n_points=64)
        initial = pilot.seed_configurations(1500, seed=19)
        self.assertEqual(initial.shape, (1500, 2))
        for _ in range(20):
            pilot.step(0.01)
        self.assertAlmostEqual(pilot.field.norm, 1.0, places=12)
        self.assertTrue(np.all(np.isfinite(pilot.configurations)))
        self.assertGreater(abs(pilot.snapshot().covariance), 0.05)


if __name__ == "__main__":
    unittest.main()

