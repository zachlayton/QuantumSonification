from __future__ import annotations

import math
import unittest

import numpy as np

from qmw_one_qubit.mapping import observe_one_qubit
from qmw_one_qubit.physics import OneQubitEngine, OneQubitPhysicsControls


class OneQubitPhysicsTests(unittest.TestCase):
    def test_exact_x_rotation_matches_analytic_bloch_trajectory(self) -> None:
        omega = 2.3
        elapsed = 0.47
        engine = OneQubitEngine(
            OneQubitPhysicsControls(omega_x=omega, omega_y=0, omega_z=0)
        )
        observation = observe_one_qubit(engine.step(elapsed))
        self.assertAlmostEqual(
            observation.energy_gap_over_hbar_rad_per_second, omega, places=12
        )
        np.testing.assert_allclose(
            observation.bloch_xyz,
            [0.0, -math.sin(omega * elapsed), math.cos(omega * elapsed)],
            atol=1e-12,
        )
        self.assertAlmostEqual(observation.purity, 1.0, places=12)

    def test_closed_evolution_preserves_density_invariants_and_energy(self) -> None:
        engine = OneQubitEngine(
            OneQubitPhysicsControls(omega_x=1.2, omega_y=-0.7, omega_z=0.35),
            preparation="+i",
        )
        initial = engine.snapshot()
        initial_energy = float(np.trace(initial.rho @ initial.hamiltonian).real)
        for _ in range(250):
            frame = engine.step(0.007)
            self.assertAlmostEqual(float(np.trace(frame.rho).real), 1.0, places=11)
            self.assertLess(float(np.max(np.abs(frame.rho - frame.rho.conj().T))), 1e-12)
            self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(frame.rho))), -1e-11)
            self.assertFalse(frame.rho.flags.writeable)
        final_energy = float(np.trace(frame.rho @ frame.hamiltonian).real)
        self.assertAlmostEqual(final_energy, initial_energy, places=10)

    def test_t1_channel_matches_exponential_excited_population(self) -> None:
        t1, elapsed = 2.0, 0.7
        engine = OneQubitEngine(
            OneQubitPhysicsControls(0, 0, 0, t1_seconds=t1), preparation="1"
        )
        observation = observe_one_qubit(engine.step(elapsed))
        self.assertAlmostEqual(observation.population_1, math.exp(-elapsed / t1), places=12)
        self.assertAlmostEqual(observation.population_0, 1.0 - math.exp(-elapsed / t1), places=12)

    def test_pure_dephasing_matches_exponential_coherence(self) -> None:
        tphi, elapsed = 1.3, 0.8
        engine = OneQubitEngine(
            OneQubitPhysicsControls(0, 0, 0, tphi_seconds=tphi), preparation="+"
        )
        observation = observe_one_qubit(engine.step(elapsed))
        self.assertAlmostEqual(observation.coherence_l1, math.exp(-elapsed / tphi), places=12)
        self.assertAlmostEqual(observation.population_0, 0.5, places=12)

    def test_hamiltonian_commit_preserves_rho_and_measurement_is_discrete(self) -> None:
        engine = OneQubitEngine(preparation="0")
        before = engine.snapshot()
        quenched = engine.set_controls(OneQubitPhysicsControls(0, 0, 3.0))
        np.testing.assert_array_equal(quenched.rho, before.rho)
        self.assertEqual(quenched.revision, before.revision + 1)
        event, measured = engine.measure_z()
        self.assertEqual(event.outcome, 0)
        self.assertEqual(event.probability, 1.0)
        self.assertEqual(event.pre_revision, quenched.revision)
        self.assertEqual(event.post_revision, measured.revision)


if __name__ == "__main__":
    unittest.main()
