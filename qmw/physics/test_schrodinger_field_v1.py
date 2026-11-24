import unittest

import numpy as np

from qmw.core import Domain, PhysicsFrame, PhysicsTrajectory
from qmw.physics import ControlState, FieldEngine
from qmw.physics.schrodinger import SchrodingerConfig, SchrodingerModel
from qmw.physics.schrodinger import potentials as P
from qmw.physics.schrodinger import states as S
from qmw.projectors import RegionProjector


def make(boundary="dirichlet", V=None, W=None, psi=None, n=2048, L=50.0, dt=0.002, regions=True):
    base = SchrodingerModel(SchrodingerConfig(n=n, x_min=-L, x_max=L, boundary=boundary))
    x = base.x
    cfg = SchrodingerConfig(n=n, x_min=-L, x_max=L, boundary=boundary,
                            potential=None if V is None else V(x), absorber=None if W is None else W(x),
                            initial_psi=S.gaussian_packet(x, -20, 2, 2.0) if psi is None else psi(x))
    model = SchrodingerModel(cfg)
    return FieldEngine(model, dt, RegionProjector(model.domain) if regions else None)


class DomainTests(unittest.TestCase):
    def test_gradient_refused_on_time_history(self):
        d = Domain("time_history", (2048,))
        with self.assertRaises(TypeError):
            d.require_spatial("gradient")
        with self.assertRaises(TypeError):
            RegionProjector(d)

    def test_trajectory_alias(self):
        self.assertIs(PhysicsTrajectory, PhysicsFrame)


class ConservationTests(unittest.TestCase):
    def check_closed(self, boundary):
        e = make(boundary, V=lambda x: P.barrier(x, 2.2, 0, 1.0, 0.05))
        for _ in range(2000):
            f = e.step()
        self.assertLess(abs(f.diagnostics.norm_error), 1e-10)
        self.assertLess(abs(f.diagnostics.energy_drift), 1e-10)
        self.assertLess(f.diagnostics.probability_continuity_error, 1e-9)

    def test_dirichlet_closed_system(self):
        self.check_closed("dirichlet")

    def test_periodic_closed_system(self):
        self.check_closed("periodic")

    def test_absorber_is_physical_not_numerical(self):
        e = make(W=lambda x: P.absorbing_layer(x, 10.0, 0.5), psi=lambda x: S.gaussian_packet(x, 20, 2, 3.0))
        for _ in range(10000):
            f = e.step()
        self.assertLess(f.observables.norm, 0.5)                      # most has been absorbed
        self.assertLess(abs(f.diagnostics.norm_error), 1e-10)          # ...and fully accounted for
        self.assertIsNone(f.diagnostics.energy_drift)
        self.assertLess(f.diagnostics.probability_continuity_error, 1e-9)

    def test_changing_potential_is_external_work(self):
        e = make(V=P.free)
        x = e.model.x
        for i in range(1500):
            V = P.harmonic(x, omega=0.05 * min(1, i / 500))
            f = e.step(ControlState(potential=V))
        self.assertGreater(abs(f.conservation.external_work), 1e-3)
        self.assertLess(abs(f.diagnostics.energy_drift), 1e-10)


class PhysicsTests(unittest.TestCase):
    def test_group_velocity(self):
        e = make("periodic", psi=lambda x: S.gaussian_packet(x, -20, 4, 1.5), n=4096, L=60)
        x0 = e.frame.observables.position_mean
        for _ in range(5000):
            f = e.step()
        v = (f.observables.position_mean - x0) / f.t
        self.assertAlmostEqual(v, 1.5, delta=0.015)

    def test_harmonic_ground_state(self):
        e = make(V=lambda x: P.harmonic(x, 1.0), psi=lambda x: S.gaussian_packet(x, 0, np.sqrt(0.5), 0), L=20)
        rho0 = e.frame.observables.probability_density
        self.assertAlmostEqual(e.frame.observables.total_energy, 0.5, delta=1e-3)
        for _ in range(1000):
            f = e.step()
        self.assertLess(np.abs(f.observables.probability_density - rho0).max(), 2e-3)


class RegionTests(unittest.TestCase):
    def test_partition_of_unity_and_totals(self):
        e = make(V=lambda x: P.barrier(x, 2.2, 0, 1.0, 0.05))
        self.assertTrue(np.allclose(e.projector.W.sum(0), 1.0))
        f = e.step()
        self.assertEqual(f.regions.probability.shape, (16,))
        self.assertAlmostEqual(f.regions.probability.sum(), f.observables.norm, places=12)
        self.assertAlmostEqual(f.regions.energy.sum(), f.observables.total_energy, places=10)

    def test_inflow_matches_regional_change(self):
        e = make(dt=0.0005)
        for _ in range(4000):
            e.step()
        a = e.frame
        b = e.step()
        measured = (b.regions.probability - a.regions.probability) / e.dt
        predicted = 0.5 * (a.regions.probability_inflow + b.regions.probability_inflow)
        self.assertLess(np.abs(measured - predicted).max(), 1e-3 * np.abs(measured).max() + 1e-12)


if __name__ == "__main__":
    unittest.main()
