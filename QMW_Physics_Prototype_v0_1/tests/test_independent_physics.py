"""Independent analytic and refinement checks for the declared physics.

Expected values come from closed forms or independently diagonalized operators;
they are not computed by another call to the production observable function.
"""
import unittest
import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import PhysicsFrame, StateData, ObservableData, RegionalData, EventType
from qmw.core.operators import derivative


def frame(domain, state, obs=None):
    return PhysicsFrame(0, 0.0, 0.01, "independent-test", domain, state,
                        obs if obs is not None else ObservableData())


def weighted_error(actual, expected, domain):
    return float(np.sqrt(domain.spacing[0]*np.sum(np.abs(actual-expected)**2)))


class TestDomainAndQuadrature(unittest.TestCase):
    def test_spatial_quadrature_integrates_constant_over_length(self):
        domain = Domain.periodic(128, 11.0)
        self.assertAlmostEqual(domain.integrate(np.ones(128)), 11.0, places=13)

    def test_time_history_and_basis_are_not_spatial_derivatives(self):
        for domain in (Domain("time_history", (32,), spacing=(0.01,)), Domain.basis(32)):
            with self.assertRaises(ValueError):
                derivative(np.arange(32.0), domain)

    def test_spatial_coordinates_are_not_mutable_aliases(self):
        x = np.arange(32.0)
        domain = Domain("space_1d", (32,), x, (1.0,), "periodic")
        x[0] = 999
        self.assertEqual(domain.coordinates[0], 0.0)
        with self.assertRaises(ValueError):
            domain.coordinates[0] = 1.0

    def test_fourier_derivative_matches_exact_low_modes(self):
        domain = Domain.periodic(128, 2*np.pi)
        x = domain.coordinates
        field = np.exp(3j*x) + .7*np.exp(-2j*x)
        first = 3j*np.exp(3j*x) - 1.4j*np.exp(-2j*x)
        second = -9*np.exp(3j*x) - 2.8*np.exp(-2j*x)
        np.testing.assert_allclose(derivative(field, domain), first, atol=2e-13)
        np.testing.assert_allclose(derivative(field, domain, 2), second, atol=3e-12)


class TestIndependentObservables(unittest.TestCase):
    def test_plane_wave_current_energy_flux_with_units_and_offset(self):
        from qmw.observables.schrodinger import schrodinger_observables
        domain = Domain.periodic(256, 2*np.pi)
        hbar, mass, v, k = 1.7, 2.3, .45, 3
        psi = np.exp(1j*k*domain.coordinates)/np.sqrt(domain.length)
        obs = schrodinger_observables(StateData(psi=psi), domain,
                                     np.full(domain.shape, v), hbar=hbar, mass=mass)
        energy = hbar*hbar*k*k/(2*mass) + v
        current = hbar*k/(mass*domain.length)
        np.testing.assert_allclose(obs.probability_density, 1/domain.length, atol=2e-14)
        np.testing.assert_allclose(obs.probability_current, current, atol=2e-13)
        np.testing.assert_allclose(obs.energy_flux, energy*current, atol=2e-12)
        self.assertAlmostEqual(obs.total_energy, energy, places=11)
        self.assertAlmostEqual(obs.norm, 1.0, places=13)

    def test_smooth_superposition_local_continuity_closed_form(self):
        from qmw.observables.schrodinger import schrodinger_observables
        domain = Domain.periodic(256, 2*np.pi)
        hbar, mass, v, k1, k2 = 1.3, 1.9, .25, 2, -1
        a, b = np.sqrt(.4), 1j*np.sqrt(.6)
        psi = (a*np.exp(1j*k1*domain.coordinates) +
               b*np.exp(1j*k2*domain.coordinates))/np.sqrt(domain.length)
        obs = schrodinger_observables(StateData(psi=psi), domain,
                                     np.full(domain.shape, v), hbar=hbar, mass=mass)
        e1, e2 = hbar*hbar*k1*k1/(2*mass)+v, hbar*hbar*k2*k2/(2*mass)+v
        cross = np.conj(a)*b*np.exp(1j*(k2-k1)*domain.coordinates)/domain.length
        delta_omega = (e2-e1)/hbar
        expected_probability_rate = 2*delta_omega*cross.imag
        cross_energy = hbar*hbar*k1*k2/(2*mass)+v
        expected_energy_rate = 2*cross_energy*delta_omega*cross.imag
        expected_flux = hbar/mass*((e1*k1*abs(a)**2+e2*k2*abs(b)**2)/domain.length +
                                  (e1*k2+e2*k1)*cross.real)
        np.testing.assert_allclose(obs.probability_rate, expected_probability_rate, atol=3e-12)
        np.testing.assert_allclose(obs.energy_rate, expected_energy_rate, atol=3e-10)
        np.testing.assert_allclose(obs.energy_flux, expected_flux, atol=2e-12)
        np.testing.assert_allclose(obs.probability_rate+derivative(obs.probability_current, domain),
                                   0, atol=3e-12)
        np.testing.assert_allclose(obs.energy_rate+derivative(obs.energy_flux, domain),
                                   0, atol=4e-10)

    def test_local_aliasing_is_measured_and_resolves_with_spatial_refinement(self):
        from qmw.observables.schrodinger import schrodinger_observables
        from qmw.conservation import ConservationMonitor
        errors = []
        for n in (32, 64):
            domain = Domain.periodic(n, 2*np.pi)
            psi = (np.exp(9j*domain.coordinates)+1j*np.exp(-8j*domain.coordinates))/np.sqrt(2*domain.length)
            state = StateData(psi=psi)
            obs = schrodinger_observables(state, domain, 0)
            _, diagnostics = ConservationMonitor(domain).evaluate(state, obs)
            self.assertAlmostEqual(obs.norm, 1, places=12)
            self.assertAlmostEqual(obs.total_energy, (9**2+8**2)/4, places=10)
            errors.append(diagnostics.probability_continuity_error)
        self.assertGreater(errors[0], 1.0)
        self.assertLess(errors[1], 2e-11)

    def test_scalar_linear_wave_density_flux_charge_analytic(self):
        from qmw.observables.scalar import scalar_observables
        from qmw.physics.scalar_field import PolynomialPotential
        domain = Domain.periodic(256, 2*np.pi)
        amplitude, mass_squared, k = .37, 1.5, 2
        omega = np.sqrt(k*k+mass_squared)
        phi = amplitude*np.exp(1j*k*domain.coordinates)
        pi = -1j*omega*phi
        obs = scalar_observables(StateData(phi=phi, pi=pi), domain,
                                 PolynomialPotential(mass_squared=mass_squared, attraction=0, repulsion=0))
        np.testing.assert_allclose(obs.total_energy_density,
                                  omega*omega*amplitude*amplitude, atol=2e-12)
        np.testing.assert_allclose(obs.energy_flux, omega*k*amplitude*amplitude, atol=2e-12)
        np.testing.assert_allclose(obs.charge_density, -omega*amplitude*amplitude, atol=2e-13)
        np.testing.assert_allclose(obs.charge_current, -k*amplitude*amplitude, atol=2e-13)
        self.assertAlmostEqual(obs.total_charge, -omega*amplitude**2*domain.length, places=11)
        np.testing.assert_allclose(obs.charge_rate, 0, atol=3e-12)


class TestIndependentSchrodinger(unittest.TestCase):
    def test_exact_plane_wave_phase_at_nonunit_hbar_and_mass(self):
        from qmw.physics.schrodinger import SchrodingerModel
        domain = Domain.periodic(256, 2*np.pi)
        hbar, mass, k, duration = 1.3, 2.1, -3, .71
        model = SchrodingerModel(domain, hbar=hbar, mass=mass)
        psi = np.exp(1j*k*domain.coordinates)/np.sqrt(domain.length)
        state = model.step(StateData(psi=psi.copy()), {}, duration)
        energy = hbar*hbar*k*k/(2*mass)
        expected = psi*np.exp(-1j*energy*duration/hbar)
        np.testing.assert_allclose(state.psi, expected, atol=3e-14)
        np.testing.assert_allclose(psi, np.exp(1j*k*domain.coordinates)/np.sqrt(domain.length), atol=0)

    def test_no_hidden_per_step_normalization(self):
        from qmw.physics.schrodinger import SchrodingerModel
        domain = Domain.periodic(128, 2*np.pi)
        psi = 1.1*np.exp(2j*domain.coordinates)/np.sqrt(domain.length)
        state = StateData(psi=psi.copy())
        model = SchrodingerModel(domain)
        for _ in range(100):
            state = model.step(state, {}, .03)
        self.assertAlmostEqual(domain.spacing[0]*np.sum(abs(state.psi)**2), 1.21, places=12)

    def test_gaussian_group_velocity_and_dispersion(self):
        from qmw.physics.schrodinger import SchrodingerModel
        domain = Domain.periodic(2048, 64.0)
        hbar, mass, sigma, center, momentum, duration = 1.4, 2.3, 1.7, -5.0, 1.2, 1.1
        model = SchrodingerModel(domain, hbar=hbar, mass=mass)
        controls = {"packet_width": sigma, "packet_center": center,
                    "packet_momentum": momentum}
        state = model.initialize(controls)
        for _ in range(110):
            state = model.step(state, controls, .01)
        density = abs(state.psi)**2
        mean = domain.spacing[0]*np.sum(domain.coordinates*density)
        variance = domain.spacing[0]*np.sum((domain.coordinates-mean)**2*density)
        self.assertAlmostEqual(mean, center+momentum*duration/mass, places=10)
        self.assertAlmostEqual(variance, sigma*sigma+(hbar*duration/(2*mass*sigma))**2, places=10)

    def test_splitting_is_second_order_against_independent_dense_exponential(self):
        from qmw.physics.schrodinger import SchrodingerModel
        domain = Domain.periodic(64, 2*np.pi)
        hbar, mass, strength, duration = 1.3, 1.4, .8, 1.0
        n = domain.size
        # Independent Fourier matrix and explicit diagonalization are feasible
        # only in this small oracle; production avoids a dense spatial operator.
        integers = np.arange(n)
        integers = np.where(integers < n//2, integers, integers-n)
        fourier = np.exp(1j*np.outer(domain.coordinates, integers))/np.sqrt(n)
        kinetic = hbar*hbar*integers*integers/(2*mass)
        potential = strength*(1-np.cos(domain.coordinates))
        hamiltonian = (fourier*kinetic) @ fourier.conj().T + np.diag(potential)
        energies, vectors = np.linalg.eigh(hamiltonian)
        psi = (np.sqrt(.7)*np.exp(1j*domain.coordinates)+
               1j*np.sqrt(.3)*np.exp(-2j*domain.coordinates))/np.sqrt(domain.length)
        exact = vectors @ (np.exp(-1j*energies*duration/hbar)*(vectors.conj().T @ psi))
        errors = []
        for dt in (.05, .025):
            model = SchrodingerModel(domain, hbar=hbar, mass=mass)
            state = StateData(psi=psi.copy())
            for _ in range(round(duration/dt)):
                state = model.step(state, {"potential_strength": strength}, dt)
            errors.append(weighted_error(state.psi, exact, domain))
        self.assertGreater(errors[0]/errors[1], 3.8)
        self.assertLess(errors[0]/errors[1], 4.2)
        self.assertLess(errors[1], 2e-4)

    def test_long_closed_evolution_preserves_norm_and_bounded_energy(self):
        from qmw.physics.schrodinger import SchrodingerModel
        domain = Domain.periodic(256, 2*np.pi)
        psi = (np.sqrt(.6)*np.exp(1j*domain.coordinates)+
               1j*np.sqrt(.4)*np.exp(-2j*domain.coordinates))/np.sqrt(domain.length)
        model = SchrodingerModel(domain)
        controls = {"potential_strength": .7}
        state = StateData(psi=psi.copy())
        energy0 = model.compute_observables(state, controls).total_energy
        max_drift = 0.0
        for step in range(1000):
            state = model.step(state, controls, .001)
            if step % 50 == 49:
                obs = model.compute_observables(state, controls)
                self.assertAlmostEqual(obs.norm, 1, places=11)
                max_drift = max(max_drift, abs(obs.total_energy-energy0))
        self.assertLess(max_drift, 4e-7)


class TestIndependentProjection(unittest.TestCase):
    def test_region_energy_quadrature_and_flux_balance(self):
        from qmw.projection import RegionProjector
        domain = Domain.periodic(256, 10.0)
        x = domain.coordinates
        density = 2 + .5*np.cos(2*np.pi*x/10)
        flux = .8*np.sin(2*np.pi*x/10)
        obs = ObservableData(total_energy_density=density, energy_flux=flux)
        regions = RegionProjector(domain, count=16).project(frame(domain, StateData(psi=np.ones(256)), obs))
        self.assertAlmostEqual(regions.energy.sum(), 20.0, places=12)
        self.assertAlmostEqual(regions.incoming_energy_flux.sum(), 0.0, places=12)
        # A sine flux decreases energy where its spatial derivative is positive.
        projector = RegionProjector(domain, count=16)
        analytic_incoming = projector.masks @ (-.8*(2*np.pi/10)*np.cos(2*np.pi*x/10))*domain.spacing[0]
        np.testing.assert_allclose(regions.incoming_energy_flux, analytic_incoming, atol=2e-13)

    def test_weighted_fourier_modal_populations_match_known_coefficients(self):
        from qmw.projection import ModalProjector
        domain = Domain.periodic(256, 13.0)
        x, length = domain.coordinates, domain.length
        a, b = np.sqrt(.3), np.sqrt(.7)*np.exp(.43j)
        psi = (a*np.exp(2j*np.pi*x/length)+b*np.exp(-4j*np.pi*x/length))/np.sqrt(length)
        projector = ModalProjector(domain, count=8)
        np.testing.assert_allclose(projector.basis.conj().T @ (domain.weights[:, None]*projector.basis),
                                  np.eye(8), atol=2e-14)
        modes = projector.project(frame(domain, StateData(psi=psi)))
        expected = np.zeros(8, dtype=complex)
        expected[1], expected[4] = a, b
        np.testing.assert_allclose(modes.coefficients, expected, atol=2e-14)
        np.testing.assert_allclose(modes.populations, abs(expected)**2, atol=2e-14)
        self.assertAlmostEqual(modes.captured_norm, 1.0, places=13)

    def test_mixed_state_has_populations_without_invented_coefficients(self):
        from qmw.projection import ModalProjector
        domain = Domain.basis(3)
        rho = np.array([[.2, .05j, 0], [-.05j, .3, .02], [0, .02, .5]], complex)
        modes = ModalProjector(domain, count=3).project(frame(domain, StateData(rho=rho)))
        self.assertIsNone(modes.coefficients)
        np.testing.assert_allclose(modes.populations, [.2, .3, .5], atol=1e-14)
        self.assertAlmostEqual(modes.captured_norm, 1.0, places=13)

    def test_region_projector_rejects_time_history(self):
        from qmw.projection import RegionProjector
        with self.assertRaises(ValueError):
            RegionProjector(Domain("time_history", (64,), spacing=(.01,)))


class TestIndependentConservation(unittest.TestCase):
    def test_work_and_environment_are_separate_signed_energy_ledgers(self):
        from qmw.conservation import ConservationMonitor
        domain = Domain.basis(2)
        state = StateData(rho=np.diag([.4, .6]).astype(complex))
        monitor = ConservationMonitor(domain)
        monitor.evaluate(state, ObservableData(total_energy=10, norm=1),
                         cumulative_work=3, cumulative_environment_energy=-1)
        _, diagnostics = monitor.evaluate(state, ObservableData(total_energy=11.5, norm=1),
                                           cumulative_work=5, cumulative_environment_energy=-1.5)
        self.assertAlmostEqual(diagnostics.energy_drift, 0, places=14)
        _, diagnostics = monitor.evaluate(state, ObservableData(total_energy=11.6, norm=1),
                                           cumulative_work=5, cumulative_environment_energy=-1.5)
        self.assertAlmostEqual(diagnostics.energy_drift, .1, places=13)


class TestIndependentEvents(unittest.TestCase):
    def test_flux_hysteresis_refractory_and_repeated_sequence(self):
        from qmw.events import FlowEventDetector
        domain = Domain.periodic(32, 8)
        detector = FlowEventDetector(threshold=1, hysteresis=.5, refractory=.08)
        previous = None

        def sample(sequence, t, flux):
            nonlocal previous
            current = frame(domain, StateData(psi=np.ones(32)))
            current.sequence, current.t = sequence, t
            current.regions = RegionalData(np.array([0.0]), incoming_energy_flux=np.array([flux]))
            events = detector.update(previous, current)
            previous = current
            return events

        self.assertEqual(sample(0, 0, 0), [])
        first = sample(1, .01, 1.1)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].type, EventType.ENERGY_ARRIVAL)
        self.assertEqual(sample(2, .02, 1.3), [])
        self.assertEqual(sample(3, .03, .7), [])  # No rearm above lower threshold.
        self.assertEqual(sample(4, .04, 1.2), [])
        self.assertEqual(sample(5, .05, .4), [])
        self.assertEqual(sample(6, .06, 1.2), [])  # Rearmed but refractory.
        self.assertEqual(len(sample(7, .10, 1.2)), 1)
        self.assertEqual(detector.update(previous, previous), [])


class TestIndependentOscWire(unittest.TestCase):
    def test_complete_wire_packet_against_standard_bytes(self):
        import struct
        from qmw.io import encode_message, encode_bundle
        message = encode_message("/qa", [17, .25, "ab", b"xyz"])
        expected = (b"/qa\0,ifsb\0\0\0" + struct.pack(">if", 17, .25) +
                    b"ab\0\0" + struct.pack(">i", 3) + b"xyz\0")
        self.assertEqual(message, expected)
        self.assertEqual(encode_bundle([message]),
                         b"#bundle\0" + struct.pack(">Q", 1) + struct.pack(">i", len(expected)) + expected)


class TestIndependentRuntime(unittest.TestCase):
    def test_constructor_controls_actually_initialize_the_requested_state(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(n=256, controls={"packet_center": 0, "packet_momentum": 1.1})
        probability = abs(engine.state.psi)**2
        mean = engine.model.domain.spacing[0]*np.sum(engine.model.domain.coordinates*probability)
        self.assertAlmostEqual(mean, 0, places=11)
        self.assertAlmostEqual(engine.frame.observables.expectations["mean_momentum"], 1.1, places=11)
        scalar = PhysicsEngine(model="scalar", controls={"init": "qball"})
        self.assertEqual(scalar.model.initialization_metadata["initializer"], "checked-periodized-1d-qball")
        self.assertEqual(scalar.t, 0)
        self.assertEqual(scalar.cumulative_work, 0)

    def test_mixed_invalid_control_update_is_atomic(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(n=256)
        before_controls = dict(engine.controls)
        before_state = engine.state.psi.copy()
        before_sequence = engine.sequence
        with self.assertRaises(ValueError):
            engine.set_controls({"mass": -1, "gain": .4})
        self.assertEqual(engine.controls, before_controls)
        self.assertEqual(engine.sequence, before_sequence)
        np.testing.assert_array_equal(engine.state.psi, before_state)
        self.assertEqual(engine.cumulative_work, 0)

    def test_quench_work_matches_closed_form_gaussian_expectation(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(n=256)
        psi0 = engine.state.psi.copy()
        engine.set_controls({"mass": .75, "potential_strength": .3})
        # Initial p=.6, sigma=2.5, center=-L/4. <cos(2pi*x/L)>=0;
        # kinetic energy=(p²+1/(4sigma²))/(2m), independent of solver methods.
        expected = .3 + (.6**2+1/(4*2.5**2))/2*(1/.75-1/.5)
        self.assertAlmostEqual(engine.cumulative_work, expected, places=11)
        self.assertLess(engine.frame.diagnostics.energy_drift, 2e-13)
        np.testing.assert_array_equal(engine.state.psi, psi0)
        self.assertEqual(engine.t, 0)
        self.assertEqual(engine.frame.events[0].type, EventType.QUENCH)

    def test_scalar_unstable_timestep_is_rejected_before_commit(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(model="scalar")
        before_controls, before_sequence = dict(engine.controls), engine.sequence
        before_phi = engine.state.phi.copy()
        with self.assertRaises(ValueError):
            engine.set_controls({"dt": .02})
        self.assertEqual(engine.controls, before_controls)
        self.assertEqual(engine.sequence, before_sequence)
        np.testing.assert_array_equal(engine.state.phi, before_phi)

    def test_model_switch_rejects_inherited_unstable_timestep_atomically(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine()
        engine.set_controls({"dt": .02})
        before_controls, before_sequence = dict(engine.controls), engine.sequence
        before_state = engine.state.psi.copy()
        with self.assertRaises(ValueError):
            engine.set_controls({"model": "scalar"})
        self.assertEqual(engine.model_kind, "schrodinger")
        self.assertEqual(engine.controls, before_controls)
        self.assertEqual(engine.sequence, before_sequence)
        np.testing.assert_array_equal(engine.state.psi, before_state)

    def test_initializer_metadata_changes_only_when_new_state_is_instantiated(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(model="scalar")
        original_phi = engine.state.phi.copy()
        original_metadata = dict(engine.model.initialization_metadata)
        engine.set_controls({"init": "qball"})
        self.assertEqual(engine.model.initialization_metadata, original_metadata)
        np.testing.assert_array_equal(engine.state.phi, original_phi)
        engine.reset()
        self.assertEqual(engine.model.initialization_metadata["initializer"], "checked-periodized-1d-qball")
        self.assertLess(engine.model.initialization_metadata["stationary_relative_residual"], 1e-5)
        self.assertFalse(np.array_equal(engine.state.phi, original_phi))

    def test_lindblad_environment_and_hamiltonian_work_are_distinct(self):
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(model="lindblad")
        initial_energy = engine.frame.observables.total_energy
        engine.step(10)
        # The independent source-power ledger uses trapezoidal quadrature,
        # leaving a small, explicitly measured O(dt²) integration residual.
        residual = abs(engine.cumulative_environment_energy-
                       (engine.frame.observables.total_energy-initial_energy))
        self.assertAlmostEqual(engine.frame.diagnostics.energy_drift, residual, places=14)
        self.assertLess(residual, 1e-9)
        self.assertEqual(engine.cumulative_work, 0)
        rho0 = engine.state.rho.copy()
        x = np.array([[0, 1], [1, 0]], complex)
        x0 = np.kron(np.kron(np.kron(x, np.eye(2)), np.eye(2)), np.eye(2))
        expected_work = .2*np.trace(x0 @ rho0).real
        environment_before = engine.cumulative_environment_energy
        engine.set_controls({"h_x0": .55})
        self.assertAlmostEqual(engine.cumulative_work, expected_work, places=13)
        self.assertEqual(engine.cumulative_environment_energy, environment_before)
        np.testing.assert_array_equal(engine.state.rho, rho0)
        engine.step(2)
        self.assertLess(engine.frame.diagnostics.energy_drift, 1e-9)
        self.assertLess(engine.frame.diagnostics.trace_error, 3e-13)
        self.assertLess(engine.frame.diagnostics.positivity_error, 3e-13)

    def test_environment_power_ledger_matches_analytic_damping_and_refines(self):
        from qmw.runtime import PhysicsEngine
        gamma, duration = .8, .2
        errors = []
        for dt in (.02, .01):
            engine = PhysicsEngine(model="lindblad")
            engine.set_controls({"dt": dt, "h_x0": 0, "damping_rate": gamma,
                                 "dephasing_rate": 0})
            engine.reset()
            engine.step(round(duration/dt))
            # Four independent qubits, H=-sum(Z_i)/2 and initial |++++>:
            # E(t)=-2+2 exp(-gamma*t), P(t)=-2 gamma exp(-gamma*t).
            exact_energy = -2+2*np.exp(-gamma*duration)
            exact_power = -2*gamma*np.exp(-gamma*duration)
            q = np.exp(-gamma*dt)
            exact_trapezoid = -gamma*dt*(1+q)*(1-np.exp(-gamma*duration))/(1-q)
            self.assertAlmostEqual(engine.frame.observables.total_energy, exact_energy, places=12)
            self.assertAlmostEqual(engine.frame.observables.source_power, exact_power, places=12)
            self.assertAlmostEqual(engine.cumulative_environment_energy, exact_trapezoid, places=12)
            errors.append(abs(engine.cumulative_environment_energy-exact_energy))
        self.assertGreater(errors[0]/errors[1], 3.99)
        self.assertLess(errors[0]/errors[1], 4.01)

    def test_snapshot_json_clock_and_state_semantics(self):
        import json
        from qmw.runtime import PhysicsEngine
        engine = PhysicsEngine(n=256)
        engine.step(3)
        snapshot = engine.snapshot(include_state=True)
        encoded = json.dumps(snapshot, allow_nan=False)
        decoded = json.loads(encoded)
        self.assertAlmostEqual(decoded["physics"]["t"], .006, places=14)
        self.assertEqual(decoded["physics"]["sequence"], engine.sequence)
        self.assertEqual(decoded["physics"]["domain"]["kind"], "space_1d")
        self.assertIn("real", decoded["physics"]["state"]["psi"])
        self.assertIn("imag", decoded["physics"]["state"]["psi"])
        self.assertNotIn("state", engine.snapshot(include_state=False)["physics"])


class TestIndependentLindblad(unittest.TestCase):
    def test_amplitude_damping_exact_populations_and_coherence(self):
        from qmw.physics.lindblad import LindbladModel
        gamma, gap, hbar, duration = .73, 1.2, 1.6, .9
        lowering = np.array([[0, 1], [0, 0]], complex)
        model = LindbladModel(np.diag([0, gap]), [np.sqrt(gamma)*lowering], hbar=hbar)
        ket = np.array([np.sqrt(.3), np.sqrt(.7)*np.exp(.27j)])
        rho = np.outer(ket, ket.conj())
        state = StateData(rho=rho.copy())
        for _ in range(30):
            state = model.step(state, {}, duration/30)
        excited = .7*np.exp(-gamma*duration)
        coherence = rho[0, 1]*np.exp((1j*gap/hbar-gamma/2)*duration)
        expected = np.array([[1-excited, coherence], [coherence.conjugate(), excited]])
        np.testing.assert_allclose(state.rho, expected, atol=4e-14)
        np.testing.assert_allclose(rho, np.outer(ket, ket.conj()), atol=0)
        self.assertAlmostEqual(np.trace(state.rho).real, 1.0, places=13)
        self.assertGreaterEqual(np.linalg.eigvalsh(state.rho).min(), -2e-14)

    def test_dephasing_exact_and_purity_loss(self):
        from qmw.physics.lindblad import LindbladModel
        gamma, duration = .6, 1.3
        z = np.diag([1, -1]).astype(complex)
        model = LindbladModel(np.zeros((2, 2)), [np.sqrt(gamma/2)*z])
        state = model.step(StateData(rho=np.full((2, 2), .5, complex)), {}, duration)
        coherence = .5*np.exp(-gamma*duration)
        expected = np.array([[.5, coherence], [coherence, .5]])
        np.testing.assert_allclose(state.rho, expected, atol=2e-14)
        obs = model.compute_observables(state, {})
        self.assertAlmostEqual(obs.purity, .5+.5*np.exp(-2*gamma*duration), places=13)
        self.assertLess(obs.purity, 1)

    def test_noncommuting_hamiltonian_and_channels_remain_cptp(self):
        from qmw.physics.lindblad import LindbladModel
        x = np.array([[0, 1], [1, 0]], complex)
        lowering = np.array([[0, 1], [0, 0]], complex)
        z = np.diag([1, -1])
        model = LindbladModel(.7*x+.4*z, [.3*lowering, .2*z], hbar=1.4)
        state = StateData(rho=np.array([[.3, .1+.2j], [.1-.2j, .7]]))
        for _ in range(100):
            state = model.step(state, {}, .013)
            self.assertAlmostEqual(np.trace(state.rho).real, 1, places=12)
            np.testing.assert_allclose(state.rho, state.rho.conj().T, atol=4e-14)
            self.assertGreater(np.linalg.eigvalsh(state.rho).min(), -3e-14)


class TestIndependentScalar(unittest.TestCase):
    def test_linear_wave_frequency_and_second_order_time_convergence(self):
        from qmw.physics.scalar_field import ScalarFieldModel, PolynomialPotential
        domain = Domain.periodic(128, 2*np.pi)
        k, mass_squared, amplitude, duration = 2, 1.3, .23, .4
        omega = np.sqrt(k*k+mass_squared)
        initial = amplitude*np.exp(1j*k*domain.coordinates)
        exact = initial*np.exp(-1j*omega*duration)
        errors = []
        for dt in (.002, .001):
            model = ScalarFieldModel(domain, PolynomialPotential(mass_squared=mass_squared, attraction=0, repulsion=0))
            state = StateData(phi=initial.copy(), pi=-1j*omega*initial.copy())
            for _ in range(round(duration/dt)):
                state = model.step(state, {}, dt)
            errors.append(weighted_error(state.phi, exact, domain))
        self.assertLess(errors[1], 2e-6)
        self.assertGreater(errors[0]/errors[1], 3.8)
        self.assertLess(errors[0]/errors[1], 4.2)

    def test_nonlinear_scalar_charge_is_preserved_without_projection(self):
        from qmw.physics.scalar_field import ScalarFieldModel, PolynomialPotential
        domain = Domain.periodic(128, 20.0)
        model = ScalarFieldModel(domain, PolynomialPotential(mass_squared=1.0, attraction=.3, repulsion=.08))
        x = domain.coordinates
        phi = .4*np.exp(-x*x/8)*np.exp(.3j*np.sin(np.pi*x/10))
        state = StateData(phi=phi.copy(), pi=-.6j*phi)
        q0 = domain.spacing[0]*np.sum(np.imag(np.conj(state.phi)*state.pi))
        for _ in range(300):
            state = model.step(state, {}, .003)
        q1 = domain.spacing[0]*np.sum(np.imag(np.conj(state.phi)*state.pi))
        self.assertAlmostEqual(q1, q0, places=12)
        np.testing.assert_allclose(phi, .4*np.exp(-x*x/8)*np.exp(.3j*np.sin(np.pi*x/10)), atol=0)


if __name__ == "__main__":
    unittest.main()
