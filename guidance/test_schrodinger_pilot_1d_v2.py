import unittest

import numpy as np

from guidance.schrodinger_pilot_1d_v2 import SchrodingerPilot1D


class SchrodingerPilot1DTests(unittest.TestCase):
    def test_free_gaussian_has_physical_carrier_velocity(self):
        pilot = SchrodingerPilot1D.free_gaussian(
            n_points=256,
            center=-2.0,
            sigma=0.8,
            momentum=2.5,
            mass=2.0,
            hbar=1.0,
        )
        velocity, density, valid = pilot.field.velocity_at(np.array([-2.0]))
        self.assertTrue(bool(valid))
        self.assertGreater(float(density), 0.0)
        self.assertAlmostEqual(float(velocity[0]), 1.25, places=8)
        self.assertAlmostEqual(pilot.snapshot().expectation_p, 2.5, places=10)

    def test_harmonic_ground_state_is_stationary_and_q_plus_v_is_constant(self):
        pilot = SchrodingerPilot1D.harmonic_ground(
            n_points=256, x_min=-8.0, x_max=8.0, omega=1.0
        )
        initial_density = pilot.field.density.copy()
        initial_energy = pilot.snapshot().energy
        high_density = pilot.field.density > 1e-5
        total_effective_potential = pilot.field.quantum_potential + pilot.potential
        self.assertAlmostEqual(
            float(np.mean(total_effective_potential[high_density])), 0.5, delta=2e-4
        )
        self.assertLess(float(np.std(total_effective_potential[high_density])), 4e-4)

        for _ in range(100):
            pilot.step(0.005)
        self.assertAlmostEqual(pilot.field.norm, 1.0, places=12)
        self.assertAlmostEqual(pilot.snapshot().energy, initial_energy, delta=2e-8)
        self.assertLess(float(np.max(np.abs(pilot.field.density - initial_density))), 2e-6)
        self.assertLess(float(np.max(np.abs(pilot.field.velocity[0]))), 1e-4)

    def test_seeded_trajectories_are_deterministic_and_follow_the_packet(self):
        first = SchrodingerPilot1D.free_gaussian(n_points=256, momentum=2.0)
        second = SchrodingerPilot1D.free_gaussian(n_points=256, momentum=2.0)
        first.seed_trajectories(1000, seed=44)
        second.seed_trajectories(1000, seed=44)
        for _ in range(20):
            first.step(0.01)
            second.step(0.01)
        np.testing.assert_allclose(first.trajectory_positions, second.trajectory_positions)
        self.assertAlmostEqual(
            float(np.mean(first.trajectory_positions)),
            first.snapshot().expectation_x,
            delta=0.08,
        )


if __name__ == "__main__":
    unittest.main()

