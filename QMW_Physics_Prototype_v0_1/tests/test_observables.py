"""Analytic field identities and budget checks, independent of the solvers."""
import unittest
import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import ObservableData, StateData
from qmw.observables import schrodinger_observables, scalar_observables
from qmw.conservation import ConservationMonitor


class QuadraticPotential:
    def __init__(self, mass_squared):
        self.mass_squared = mass_squared

    def energy(self, phi):
        return 0.5 * self.mass_squared * np.abs(phi)**2

    def derivative_s(self, s):
        return np.full_like(s, 0.5 * self.mass_squared)


class FieldObservableTests(unittest.TestCase):
    def test_plane_wave_probability_energy_and_flux(self):
        domain = Domain.periodic(128, 2.0 * np.pi)
        hbar, mass, k, V = 1.7, 2.3, 3, -0.45
        psi = np.exp(1j * k * domain.coordinates) / np.sqrt(domain.length)
        before = psi.copy()
        state = StateData(psi=psi)
        obs = schrodinger_observables(state, domain, V, hbar=hbar, mass=mass)
        particle_energy = hbar**2 * k**2 / (2.0 * mass) + V
        density = 1.0 / domain.length
        current = hbar * k / mass * density
        # Analytic plane-wave transport: the energy carried per probability
        # equals the stationary state's Hamiltonian eigenvalue.
        np.testing.assert_allclose(obs.probability_density, density, atol=2e-15)
        np.testing.assert_allclose(obs.probability_current, current, atol=3e-14)
        np.testing.assert_allclose(obs.total_energy_density, particle_energy * density, atol=2e-13)
        np.testing.assert_allclose(obs.energy_flux, particle_energy * current, atol=8e-13)
        self.assertAlmostEqual(obs.norm, 1.0, places=13)
        self.assertAlmostEqual(obs.total_energy, particle_energy, places=12)
        np.testing.assert_array_equal(psi, before)

    def test_smooth_superposition_probability_and_energy_continuity(self):
        domain = Domain.periodic(128, 2.0 * np.pi)
        x, hbar, mass = domain.coordinates, 1.3, 0.9
        a = 0.6 * np.exp(-2j * x) / np.sqrt(domain.length)
        b = 0.8j * np.exp(3j * x) / np.sqrt(domain.length)
        psi = a + b
        # Independent analytic derivatives of these two Fourier modes.
        analytic_x = -2j * a + 3j * b
        analytic_xx = -4 * a - 9 * b
        V = 0.2 + 0.15 * np.cos(x) + 0.05 * np.sin(2 * x)
        analytic_Hpsi = -(hbar**2 / (2 * mass)) * analytic_xx + V * psi
        analytic_t = -1j * analytic_Hpsi / hbar
        state = StateData(psi=psi)
        obs = schrodinger_observables(state, domain, V, hbar, mass)
        np.testing.assert_allclose(obs.probability_rate,
                                   2 * np.real(np.conj(psi) * analytic_t), atol=3e-13)
        np.testing.assert_allclose(obs.kinetic_energy_density,
                                   hbar**2 / (2 * mass) * abs(analytic_x)**2, atol=3e-13)
        expected_E = hbar**2 / (2 * mass) * (0.36 * 4 + 0.64 * 9) + 0.2
        self.assertAlmostEqual(obs.total_energy, expected_E, places=12)
        _, diagnostics = ConservationMonitor(domain).evaluate(state, obs)
        self.assertLess(diagnostics.probability_continuity_error, 2e-12)
        self.assertLess(diagnostics.energy_continuity_error, 2e-10)

    def test_continuity_residual_decreases_with_spatial_refinement(self):
        # A narrow packet under-resolves nonlinear products on a coarse grid.
        # Refinement, rather than forcing a zero residual, resolves the error.
        errors = []
        for n in (32, 64, 128):
            domain = Domain.periodic(n, 16.0)
            x = domain.coordinates
            psi = np.exp(-0.5 * ((x + 0.7) / 0.6)**2) * np.exp(2.5j * x)
            psi /= np.sqrt(domain.integrate(abs(psi)**2))
            state = StateData(psi=psi)
            V = 0.4 * np.cos(2 * np.pi * x / domain.length)
            obs = schrodinger_observables(state, domain, V)
            _, diagnostics = ConservationMonitor(domain).evaluate(state, obs)
            errors.append((diagnostics.probability_continuity_error,
                           diagnostics.energy_continuity_error))
        errors = np.asarray(errors)
        self.assertTrue(np.all(errors[1] < 1e-3 * errors[0]))
        self.assertTrue(np.all(errors[2] < 1e-6 * errors[1]))
        self.assertLess(errors[-1, 1], 1e-10)

    def test_linear_scalar_traveling_wave_energy_and_charge(self):
        domain = Domain.periodic(128, 2 * np.pi)
        k, mass_squared, amplitude = 2, 1.5, 0.37
        omega = np.sqrt(k**2 + mass_squared)
        phi = amplitude * np.exp(1j * k * domain.coordinates)
        state = StateData(phi=phi, pi=-1j * omega * phi)
        obs = scalar_observables(state, domain, QuadraticPotential(mass_squared))
        # With the half-normalized Lagrangian: e=omega² A²,
        # S=omega*k*A², q=-omega*A² and j_Q=-k*A².
        np.testing.assert_allclose(obs.total_energy_density, omega**2 * amplitude**2, atol=6e-14)
        np.testing.assert_allclose(obs.energy_flux, omega * k * amplitude**2, atol=6e-14)
        np.testing.assert_allclose(obs.charge_density, -omega * amplitude**2, atol=2e-15)
        np.testing.assert_allclose(obs.charge_current, -k * amplitude**2, atol=2e-14)
        self.assertAlmostEqual(obs.total_energy, domain.length * omega**2 * amplitude**2, places=12)
        self.assertAlmostEqual(obs.total_charge, -domain.length * omega * amplitude**2, places=12)
        self.assertIsNone(obs.probability_density)
        self.assertIsNone(obs.norm)
        _, diagnostics = ConservationMonitor(domain).evaluate(state, obs)
        self.assertLess(diagnostics.energy_continuity_error, 2e-12)
        self.assertLess(diagnostics.charge_continuity_error, 2e-12)

    def test_scalar_nonlinear_smooth_continuity(self):
        class PolynomialPotential:
            def energy(self, phi):
                s = abs(phi)**2
                return 0.5 * s - 0.25 * s**2 + s**3 / 6

            def derivative_s(self, s):
                return 0.5 - 0.5 * s + 0.5 * s**2

        domain = Domain.periodic(128, 2 * np.pi)
        x = domain.coordinates
        phi = 0.3 * np.exp(2j * x) + 0.1 * np.exp(-3j * x)
        pi = 0.2j * np.exp(1j * x) - 0.15 * np.exp(-2j * x)
        state = StateData(phi=phi, pi=pi)
        obs = scalar_observables(state, domain, PolynomialPotential())
        _, diagnostics = ConservationMonitor(domain).evaluate(state, obs)
        self.assertLess(diagnostics.energy_continuity_error, 1e-12)
        self.assertLess(diagnostics.charge_continuity_error, 1e-12)

    def test_time_history_domain_and_complex_potential_rejected(self):
        domain = Domain.periodic(32, 2 * np.pi)
        state = StateData(psi=np.ones(domain.shape, dtype=complex))
        history = Domain("time_history", domain.shape, spacing=(0.01,))
        with self.assertRaises(ValueError):
            schrodinger_observables(state, history, 0.0)
        with self.assertRaises(ValueError):
            schrodinger_observables(state, domain, 1 + 1e-12j)
        with self.assertRaises(ValueError):
            schrodinger_observables(state, domain, np.zeros(31))
        with self.assertRaises(ValueError):
            schrodinger_observables(state, domain, 0.0, mass=0.0)


class ConservationTests(unittest.TestCase):
    def test_work_and_environment_ledger_offsets(self):
        domain = Domain.basis(2)
        state = StateData(rho=np.eye(2, dtype=complex) / 2)
        monitor = ConservationMonitor(domain)
        monitor.initialize(state, ObservableData(norm=1.0, total_energy=2.0),
                           cumulative_work=5.0, cumulative_environment_energy=-1.0)
        # Work adds three units, environment removes half a unit: E=4.5.
        _, diag = monitor.evaluate(state, ObservableData(norm=1.0, total_energy=4.5),
                                   cumulative_work=8.0, cumulative_environment_energy=-1.5)
        self.assertAlmostEqual(diag.energy_drift, 0.0)
        _, diag = monitor.evaluate(state, ObservableData(norm=1.0, total_energy=4.7),
                                   cumulative_work=8.0, cumulative_environment_energy=-1.5)
        self.assertAlmostEqual(diag.energy_drift, 0.2)

    def test_density_matrix_invariants_without_clipping(self):
        domain = Domain.basis(2)
        rho = np.diag([1.1, -0.1]).astype(complex)
        before = rho.copy()
        _, diag = ConservationMonitor(domain).evaluate(StateData(rho=rho), ObservableData())
        self.assertEqual(diag.trace_error, 0.0)
        self.assertEqual(diag.hermiticity_error, 0.0)
        self.assertAlmostEqual(diag.positivity_error, 0.1)
        np.testing.assert_array_equal(rho, before)
        rho = np.array([[0.5, 0.1 + 0.2j], [0.15 - 0.2j, 0.5 + 0.05j]])
        _, diag = ConservationMonitor(domain).evaluate(StateData(rho=rho), ObservableData())
        self.assertAlmostEqual(diag.trace_error, 0.05)
        self.assertGreater(diag.hermiticity_error, 0.05)
        self.assertTrue(any("Hermitian part" in note for note in diag.notes))
        self.assertIsNone(diag.probability_continuity_error)

    def test_monitor_detects_bad_norm_and_requires_reset_to_switch_models(self):
        domain = Domain.periodic(32, 2 * np.pi)
        state = StateData(psi=np.ones(domain.shape, dtype=complex) / np.sqrt(domain.length / 2))
        monitor = ConservationMonitor(domain)
        _, diag = monitor.evaluate(state, schrodinger_observables(state, domain, 0.0))
        self.assertAlmostEqual(diag.norm_error, 1.0)
        # The conservation stage measures state independently of supplied norm.
        _, diag = monitor.evaluate(state, ObservableData(norm=1.0, total_energy=0.0))
        self.assertAlmostEqual(diag.norm_error, 1.0)
        scalar = StateData(phi=np.ones(domain.shape, dtype=complex), pi=np.zeros(domain.shape, dtype=complex))
        obs = scalar_observables(scalar, domain, QuadraticPotential(1.0))
        with self.assertRaises(ValueError):
            monitor.evaluate(scalar, obs)
        monitor.reset()
        _, diag = monitor.evaluate(scalar, obs)
        self.assertIsNone(diag.norm_error)
        self.assertEqual(diag.energy_drift, 0.0)
        self.assertEqual(diag.charge_drift, 0.0)


if __name__ == "__main__":
    unittest.main()
