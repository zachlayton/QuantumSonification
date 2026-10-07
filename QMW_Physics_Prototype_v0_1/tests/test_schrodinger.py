"""Analytic and convergence checks for periodic split-step Schrödinger evolution."""
import unittest

import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import StateData
from qmw.physics.schrodinger import SchrodingerModel


class SchrodingerTests(unittest.TestCase):
    def setUp(self):
        self.domain = Domain.periodic(512, 64.0)
        self.model = SchrodingerModel(self.domain)

    def test_plane_wave_matches_exact_phase_and_hamiltonian(self):
        hbar, mass, mode = 0.7, 1.4, 7
        model = SchrodingerModel(self.domain, hbar=hbar, mass=mass)
        k = 2*np.pi*mode/self.domain.length
        psi = np.exp(1j*k*self.domain.coordinates)/np.sqrt(self.domain.length)
        energy = hbar**2*k**2/(2*mass)
        dt = 0.31
        np.testing.assert_allclose(model.hamiltonian_apply(psi), energy*psi,
                                   atol=4e-13, rtol=4e-13)
        np.testing.assert_allclose(model.step(StateData(psi=psi), {}, dt).psi,
                                   psi*np.exp(-1j*energy*dt/hbar), atol=2e-14, rtol=2e-14)

    def test_long_evolution_preserves_actual_initial_norm(self):
        controls = {"potential_strength": 0.8, "barrier_height": 0.4,
                    "packet_center": -8.0, "packet_momentum": 1.2}
        state = self.model.initialize(controls)
        state.psi *= 1.7  # The stepper must not silently repair an unnormalized state.
        initial = float(self.domain.integrate(np.abs(state.psi)**2))
        for _ in range(1000):
            state = self.model.step(state, controls, 0.01)
        final = float(self.domain.integrate(np.abs(state.psi)**2))
        self.assertLess(abs(final-initial), 2e-12)
        self.assertAlmostEqual(final, 1.7**2, places=11)

    def test_free_gaussian_translates_and_spreads_analytically(self):
        hbar, mass, width, center, momentum = 0.8, 1.6, 1.7, -9.0, 2.4
        model = SchrodingerModel(self.domain, hbar=hbar, mass=mass)
        controls = {"packet_width": width, "packet_center": center,
                    "packet_momentum": momentum}
        state = model.initialize(controls)
        for _ in range(100):
            state = model.step(state, controls, 0.02)
        t = 2.0
        density = np.abs(state.psi)**2
        actual_center = float(self.domain.integrate(self.domain.coordinates*density))
        variance = float(self.domain.integrate((self.domain.coordinates-actual_center)**2*density))
        self.assertAlmostEqual(actual_center, center+momentum*t/mass, places=10)
        expected_variance = width**2+(hbar*t/(2*mass*width))**2
        self.assertAlmostEqual(variance, expected_variance, places=10)

    def test_strang_splitting_is_second_order_for_nonconstant_potential(self):
        controls = {"potential_strength": 3.0, "barrier_height": 2.5,
                    "barrier_width": 1.0, "packet_center": -2.0,
                    "packet_width": 1.0, "packet_momentum": 1.3}
        initial = self.model.initialize(controls)
        def evolve(dt):
            state = initial
            for _ in range(round(0.8/dt)):
                state = self.model.step(state, controls, dt)
            return state.psi
        reference = evolve(0.00125)
        coarse, fine = evolve(0.04), evolve(0.02)
        error_coarse = np.sqrt(self.domain.integrate(np.abs(coarse-reference)**2))
        error_fine = np.sqrt(self.domain.integrate(np.abs(fine-reference)**2))
        self.assertGreater(error_coarse/error_fine, 3.8)
        self.assertLess(error_coarse/error_fine, 4.3)

    def test_current_mass_changes_hamiltonian_without_mutating_state(self):
        state = self.model.initialize()
        unchanged = state.psi.copy()
        h1 = self.model.hamiltonian_apply(state.psi, {"mass": 1.0})
        h2 = self.model.hamiltonian_apply(state.psi, {"mass": 2.0})
        np.testing.assert_allclose(h2, h1/2, atol=1e-14)
        self.model.step(state, {"mass": 2.0}, 0.03)
        np.testing.assert_array_equal(state.psi, unchanged)

    def test_periodic_initializer_accepts_noninteger_local_momentum(self):
        controls = {"packet_center": 31.7, "packet_momentum": 1.234,
                    "packet_width": 1.0}
        state = self.model.initialize(controls)
        spectrum = np.abs(np.fft.fft(state.psi))**2
        self.assertLess(spectrum[np.abs(self.model.k)>0.75*np.max(np.abs(self.model.k))].sum()
                        /spectrum.sum(), 1e-20)
        self.assertAlmostEqual(float(self.domain.integrate(np.abs(state.psi)**2)), 1.0, places=13)

    def test_rejects_invalid_controls_and_wrong_domain(self):
        invalid = ({"unknown": 1.0}, {"mass": 0.0}, {"mass": True},
                   {"potential_strength": np.inf}, {"packet_width": 0.01},
                   {"barrier_width": 100.0}, {"packet_momentum": 1000.0})
        for controls in invalid:
            with self.subTest(controls=controls), self.assertRaises(ValueError):
                self.model.initialize(controls)
        with self.assertRaises(ValueError):
            SchrodingerModel(Domain.basis(16))
        state = self.model.initialize()
        for dt in (-0.1, float("nan"), True):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                self.model.step(state, {}, dt)


if __name__ == "__main__":
    unittest.main()
