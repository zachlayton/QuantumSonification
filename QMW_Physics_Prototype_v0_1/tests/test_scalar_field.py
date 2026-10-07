"""Analytic frequencies, charge conservation, stability, and checked 1-D profile."""
import unittest
import numpy as np
from qmw.core.domain import Domain
from qmw.core.frame import StateData
from qmw.core.operators import derivative, spectral_tail_fraction
from qmw.physics.scalar_field import ScalarFieldModel, PolynomialPotential, checked_qball_profile


class ScalarFieldTests(unittest.TestCase):
    def test_linear_plane_wave_has_correct_signed_charge_and_frequency(self):
        domain = Domain.periodic(128, 2*np.pi)
        mass_squared, amplitude, k, duration = 1.7, .4, 2, .4
        model = ScalarFieldModel(domain, PolynomialPotential(mass_squared, 0, 0))
        omega = np.sqrt(k*k+mass_squared)
        phi = amplitude*np.exp(1j*k*domain.coordinates)
        initial = StateData(phi=phi, pi=-1j*omega*phi)
        observations = model.compute_observables(initial)
        self.assertIsNone(observations.norm)
        self.assertIsNone(observations.probability_density)
        self.assertAlmostEqual(observations.total_charge, -omega*amplitude**2*domain.length, places=12)
        self.assertAlmostEqual(observations.total_energy, omega**2*amplitude**2*domain.length, places=12)
        errors = []
        for dt in (.002, .001):
            state = initial
            for _ in range(round(duration/dt)):
                state = model.step(state, {}, dt)
            exact = phi*np.exp(-1j*omega*duration)
            errors.append(np.sqrt(domain.integrate(np.abs(state.phi-exact)**2)))
        self.assertGreater(errors[0]/errors[1], 3.9)
        self.assertLess(errors[0]/errors[1], 4.1)

    def test_verlet_charge_exact_for_nonlinear_inhomogeneous_field(self):
        domain = Domain.periodic(128, 32.0)
        model = ScalarFieldModel(domain)
        state = model.initialize({"amplitude": .7, "rotation_frequency": .81})
        initial_state = StateData(phi=state.phi.copy(), pi=state.pi.copy())
        q0 = model.compute_observables(state).total_charge
        for _ in range(1000):
            state = model.step(state, {}, .003)
        self.assertLess(abs(model.compute_observables(state).total_charge-q0), 2e-12)
        np.testing.assert_array_equal(initial_state.phi, model.initialize({"amplitude": .7, "rotation_frequency": .81}).phi)

    def test_verlet_energy_error_refines_quadratically(self):
        domain = Domain.periodic(128, 2*np.pi)
        model = ScalarFieldModel(domain, PolynomialPotential(1.2, 0, 0))
        initial = StateData(phi=.3*np.cos(2*domain.coordinates).astype(complex),
                            pi=np.zeros(domain.shape, complex))
        energy = model.compute_observables(initial).total_energy
        errors = []
        for dt in (.02, .01):
            state = initial
            maximum_error = 0
            for _ in range(round(.8/dt)):
                state = model.step(state, {}, dt)
                maximum_error = max(maximum_error, abs(model.compute_observables(state).total_energy-energy))
            errors.append(maximum_error)
        self.assertGreater(errors[0]/errors[1], 3.9)
        self.assertLess(errors[0]/errors[1], 4.1)

    def test_default_scalar_initializer_is_explicitly_not_qball(self):
        model = ScalarFieldModel()
        model.initialize()
        self.assertEqual(model.initialization_metadata["initializer"], "rotating-gaussian-scalar-demo")

    def test_broad_gaussian_is_smooth_at_periodic_seam(self):
        domain = Domain.periodic(256, 64)
        model = ScalarFieldModel(domain)
        state = model.initialize({"width": 16, "amplitude": .7})
        self.assertLess(spectral_tail_fraction(state.phi, domain), 1e-25)
        self.assertLess(abs(derivative(state.phi, domain)[0]), 1e-13)
        # The seam also remains smooth when the center moves through it.
        shifted = model.initialize({"width": 16, "amplitude": .7, "center": 31.3})
        self.assertLess(spectral_tail_fraction(shifted.phi, domain), 1e-25)
        initial_charge = model.compute_observables(shifted).total_charge
        for _ in range(50):
            shifted = model.step(shifted, {}, .002)
        self.assertAlmostEqual(model.compute_observables(shifted).total_charge, initial_charge, places=11)

    def test_gaussian_width_rejects_unresolved_or_excessive_values(self):
        model = ScalarFieldModel(Domain.periodic(128, 32))
        for width in (.49, 8.01):
            with self.subTest(width=width), self.assertRaises(ValueError):
                model.initialize({"width": width})

    def test_checked_one_dimensional_qball_stationary_profile_and_rotation(self):
        domain = Domain.periodic(512, 64)
        model = ScalarFieldModel(domain)
        state = model.initialize({"init": "qball", "rotation_frequency": .95})
        metadata = model.initialization_metadata
        self.assertEqual(metadata["dimension"], 1)
        self.assertLess(metadata["stationary_relative_residual"], 1e-7)
        initial = state.phi.copy()
        q0 = model.compute_observables(state).total_charge
        for _ in range(100):
            state = model.step(state, {}, .002)
        exact = initial*np.exp(.95j*.2)
        self.assertLess(np.sqrt(domain.integrate(abs(state.phi-exact)**2)), 2e-7)
        self.assertAlmostEqual(model.compute_observables(state).total_charge, q0, places=12)

    def test_qball_rejects_domain_overlap_and_invalid_frequency(self):
        potential = PolynomialPotential()
        with self.assertRaises(ValueError):
            checked_qball_profile(Domain.periodic(128, 4.0), potential, .95)
        for frequency in (.5, 1.2):
            with self.subTest(frequency=frequency), self.assertRaises(ValueError):
                checked_qball_profile(Domain.periodic(), potential, frequency)

    def test_stability_and_domain_validation_reject_invalid_steps(self):
        model = ScalarFieldModel(Domain.periodic(128, 2*np.pi))
        state = model.initialize()
        for dt in (model.stable_dt_bound(state), float("nan"), -.1, True):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                model.step(state, {}, dt)
        with self.assertRaises(ValueError):
            ScalarFieldModel(Domain.basis(16))
        with self.assertRaises(ValueError):
            PolynomialPotential(1, 1, 0)


if __name__ == "__main__":
    unittest.main()
