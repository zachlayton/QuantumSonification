"""Analytical contracts for the instantaneous energy-basis transition observer."""
from dataclasses import replace
from unittest.mock import patch
import unittest

import numpy as np

from qmw.core import QuantumDataBus, QuantumStateFrame
from qmw.core.transition import (
    FrameContext, QuantumUnits, Transition, TransitionEdge, TransitionEngine,
)


X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1., -1.])
RHO = np.array([[.7, .1j], [-.1j, .3]])
CTX = FrameContext("transition-test", 16, .5, .01, "four-qubit:q0-lsb")


def unitary(dimension):
    rng = np.random.default_rng(734)
    return np.linalg.qr(rng.normal(size=(dimension, dimension))
                        + 1j*rng.normal(size=(dimension, dimension)))[0]


class TransitionEngineTests(unittest.TestCase):
    def test_01_mandatory_pauli_x_has_exactly_two_directed_transitions(self):
        omega0 = 3.25
        # Both levels populated: default activity filtering admits both directions.
        frame = TransitionEngine(hbar=1).compute((omega0/2)*Z, np.eye(2)/2, X, .75)
        self.assertEqual([(e.source, e.target) for e in frame.transitions], [(0, 1), (1, 0)])
        np.testing.assert_allclose(frame.energies, [-omega0/2, omega0/2])
        np.testing.assert_allclose([e.delta_E for e in frame.transitions], [omega0, -omega0])
        np.testing.assert_allclose([e.omega for e in frame.transitions], [omega0, -omega0])
        np.testing.assert_allclose([e.magnitude for e in frame.transitions], [1, 1])
        np.testing.assert_allclose(frame.diagnostic_activity, [[0, .5], [.5, 0]])
        self.assertEqual(frame.time, .75)
        self.assertIs(Transition, TransitionEdge)

    def test_02_mandatory_pauli_z_has_no_off_diagonal_transitions(self):
        frame = TransitionEngine().compute((3.25/2)*Z, np.eye(2)/2, Z)
        self.assertEqual(frame.transitions, ())
        np.testing.assert_allclose(frame.magnitudes, np.eye(2))
        np.testing.assert_allclose(frame.diagnostic_activity, np.eye(2)/2)
        np.testing.assert_array_equal(np.diag(frame.delta_E), 0)
        # The earlier candidate interface remains available to old consumers.
        self.assertEqual(len(frame.edges), 2)

    def test_03_four_qubit_sixteen_state_smoke_and_state_bus_integration(self):
        # H=sum_q 2**q Z_q/2: nondegenerate 16-state spectrum; q0 is LSB.
        levels = np.arange(16)
        h = np.diag(sum((2**q)/2 * (1-2*((levels >> q) & 1)) for q in range(4)))
        a = np.kron(np.eye(8), X)
        psi = np.zeros(16, complex)
        psi[0], psi[15] = 1/np.sqrt(2), 1j/np.sqrt(2)
        rho = .8*np.outer(psi, psi.conj()) + .2*np.eye(16)/16
        state = QuantumStateFrame(CTX.time, CTX.dt, rho.copy(), h.copy(), CTX.source_id)
        seen = []
        bus = QuantumDataBus()
        engine = TransitionEngine()
        bus.state_bus.subscribe(lambda s: seen.append(engine.process_state(s, a, CTX)))
        bus.publish_state(state)
        frame = seen[0]
        self.assertEqual(len(frame.transitions), 16)
        self.assertEqual([(e.source, e.target) for e in frame.transitions], [(n, n ^ 1) for n in range(16)])
        for edge in frame.transitions:
            self.assertAlmostEqual(edge.magnitude, 1)
            self.assertAlmostEqual(abs(edge.delta_E), 1)
        for name in ("amplitudes", "magnitudes", "phases", "rho_E", "coherences", "delta_E", "omega", "diagnostic_activity"):
            self.assertEqual(getattr(frame, name).shape, (16, 16))
            self.assertTrue(np.all(np.isfinite(getattr(frame, name))))
        self.assertGreater(np.linalg.norm(frame.coherences), 0)
        self.assertAlmostEqual(frame.populations.sum(), 1)
        self.assertIs(bus.latest_state, state)
        np.testing.assert_array_equal(state.rho, rho)
        np.testing.assert_array_equal(state.hamiltonian, h)
        u = unitary(16)
        rotated = engine.compute(u@h@u.conj().T, u@rho@u.conj().T, u@a@u.conj().T)
        self.assertEqual([(e.source, e.target) for e in rotated.transitions], [(n, n ^ 1) for n in range(16)])
        np.testing.assert_allclose(rotated.populations, frame.populations, atol=1e-12)
        np.testing.assert_allclose(rotated.diagnostic_activity, frame.diagnostic_activity, atol=1e-12)

    def test_rotated_complex_observable_and_coherences_reconstruct_inputs(self):
        u = unitary(2)
        h, rho, a = [u@m@u.conj().T for m in (np.diag([-2., 3.]), RHO, Y)]
        frame = TransitionEngine(hbar=.25).compute(h, rho, a)
        v = frame.eigenvectors
        np.testing.assert_allclose(v@np.diag(frame.energies)@v.conj().T, h, atol=1e-12)
        np.testing.assert_allclose(v@frame.A_E@v.conj().T, a, atol=1e-12)
        np.testing.assert_allclose(v@frame.rho_E@v.conj().T, rho, atol=1e-12)
        np.testing.assert_allclose(frame.coherences+np.diag(frame.populations), frame.rho_E, atol=1e-12)
        np.testing.assert_allclose(frame.amplitudes, frame.magnitudes*np.exp(1j*frame.phases), atol=1e-12)
        np.testing.assert_allclose(frame.delta_E, [[0, -5], [5, 0]], atol=1e-12)
        np.testing.assert_allclose(frame.omega, frame.delta_E/.25)
        np.testing.assert_allclose(frame.diagnostic_activity, frame.populations[None, :]*frame.magnitudes**2)
        for edge in frame.transitions:
            m, n = edge.target, edge.source
            self.assertEqual(edge.A_mn, frame.A_E[m, n])
            self.assertEqual(edge.coherence_mn, frame.rho_E[m, n])
            self.assertEqual(edge.coherence_nm, frame.rho_E[n, m])
            self.assertEqual(edge.delta_E, frame.delta_E[m, n])
            self.assertEqual(edge.omega, frame.omega[m, n])

    def test_complex_phase_and_source_population_orientation(self):
        frame = TransitionEngine().compute(np.diag([0., 2.]), RHO, Y)
        self.assertEqual([e.A_mn for e in frame.transitions], [1j, -1j])
        np.testing.assert_allclose([e.phase_rad for e in frame.transitions], [np.pi/2, -np.pi/2])
        np.testing.assert_allclose(frame.diagnostic_activity, [[0, .3], [.7, 0]])
        np.testing.assert_allclose([e.source_population for e in frame.transitions], [.7, .3])
        self.assertIn("diagnostic", frame.activity_interpretation)
        self.assertIn("not a universal transition rate", frame.activity_interpretation)

    def test_thresholds_are_strict_and_leave_full_matrices_intact(self):
        h = np.diag([0., 2.])
        ref = TransitionEngine().compute(h, RHO, X)
        for kwargs, expected in [({"amplitude_threshold": 1}, []),
                                 ({"activity_threshold": .3}, [(0, 1)]),
                                 ({"activity_threshold": .7}, [])]:
            with self.subTest(kwargs=kwargs):
                frame = TransitionEngine(**kwargs).compute(h, RHO, X)
                self.assertEqual([(e.source, e.target) for e in frame.transitions], expected)
                np.testing.assert_array_equal(frame.amplitudes, ref.amplitudes)
                np.testing.assert_array_equal(frame.diagnostic_activity, ref.diagnostic_activity)
        zero = TransitionEngine(amplitude_threshold=0, activity_threshold=0).compute(h, np.diag([1., 0.]), X)
        self.assertEqual([(e.source, e.target) for e in zero.transitions], [(0, 1)])
        self.assertEqual(TransitionEngine(1., 0., 0.).compute(h, RHO, np.zeros((2, 2))).transitions, ())

    def test_passive_rotation_does_not_admit_forbidden_edges(self):
        u = unitary(2)
        frame = TransitionEngine().compute(u@Z@u.conj().T, u@RHO@u.conj().T, u@Z@u.conj().T)
        self.assertEqual(frame.transitions, ())

    def test_sorted_by_source_then_target_not_activity_or_signed_gap(self):
        frame = TransitionEngine().compute(np.diag([0., 2., 5.]), np.diag([.2, .5, .3]), np.ones((3, 3)))
        self.assertEqual([(e.source, e.target) for e in frame.transitions],
                         [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])

    def test_zero_gap_and_diagonal_policies_are_explicit(self):
        frame = TransitionEngine().compute(np.eye(2), RHO, X)
        self.assertEqual(frame.transitions, ())
        self.assertEqual(frame.energy_degenerate_groups, ((0, 1),))
        frame = TransitionEngine(include_zero_gap=True, include_diagonal=True).compute(np.eye(2), RHO, np.ones((2, 2)))
        self.assertEqual(len(frame.edges), 4)
        self.assertEqual(len(frame.transitions), 2)
        self.assertTrue(all(e.zero_gap and not e.diagonal and e.basis_dependent_degenerate_endpoint for e in frame.transitions))
        one = TransitionEngine(include_zero_gap=True, include_diagonal=True).compute([[2]], [[1]], [[3]])
        self.assertEqual(one.transitions, ())
        np.testing.assert_array_equal(one.diagnostic_activity, [[9]])

    def test_malformed_shapes_and_nonfinite_inputs_are_rejected(self):
        invalid = ([], [1, 2], np.empty((0, 0)), np.ones((2, 3)), np.eye(3),
                   np.full((2, 2), np.nan), np.full((2, 2), np.inf))
        for position in range(3):
            for value in invalid:
                with self.subTest(position=position, shape=np.shape(value)), self.assertRaises(ValueError):
                    args = [Z, RHO, X]
                    args[position] = value
                    TransitionEngine().compute(*args)

    def test_hamiltonian_density_and_observable_must_be_hermitian(self):
        for position in range(3):
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, "Hermitian"):
                args = [Z, RHO, X]
                args[position] = args[position] + .01j*np.eye(2)
                TransitionEngine().compute(*args)
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            TransitionEngine().compute(1e-22*(Z+1j*X), RHO, X)
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            TransitionEngine().compute(Z, RHO, 1e-22*(X+1j*Z))

    def test_density_trace_and_positivity_rejection(self):
        for rho, message in [(np.eye(2), "trace one"), (np.diag([1.1, -.1]), "positive semidefinite"),
                             (np.array([[.5, .6], [.6, .5]]), "positive semidefinite")]:
            with self.subTest(rho=rho), self.assertRaisesRegex(ValueError, message):
                TransitionEngine().compute(Z, rho, X)

    def test_tolerated_roundoff_is_reported_without_repairing_density(self):
        rho = np.diag([1+1e-12, -1e-12])
        before = rho.copy()
        frame = TransitionEngine(tolerance=1e-10).compute(np.diag([0., 2.]), rho, X)
        self.assertLess(frame.populations.min(), 0)
        self.assertAlmostEqual(frame.diagnostics["minimum_density_eigenvalue"], -1e-12, delta=1e-16)
        self.assertGreater(frame.diagnostics["negative_eigenvalue_mass"], 0)
        np.testing.assert_array_equal(frame.rho_E, before)
        np.testing.assert_array_equal(rho, before)
        # Existing nonnegative diagnostic floors only tolerance-sized negatives.
        self.assertEqual(frame.diagnostic_activity[0, 1], 0)
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            TransitionEngine(tolerance=1e-14).compute(Z, rho, X)
        rho = np.eye(2)*(.5+2e-12)
        frame = TransitionEngine().compute(Z, rho, X)
        self.assertGreater(frame.diagnostics["trace_error_abs"], 0)
        np.testing.assert_array_equal(np.sort(frame.populations), np.diag(rho))

    def test_small_hermiticity_roundoff_is_accepted_and_measured(self):
        h = Z.astype(complex)
        h[0, 1] = 1e-12
        rho = RHO.copy()
        rho[0, 1] += 1e-12
        a = X.copy()
        a[0, 1] += 1e-12
        frame = TransitionEngine(tolerance=1e-10).compute(h, rho, a)
        self.assertGreater(frame.diagnostics["hamiltonian_hermiticity_residual_fro"], 0)
        self.assertGreater(frame.diagnostics["density_hermiticity_residual_fro"], 0)
        with self.assertRaises(ValueError):
            TransitionEngine(tolerance=1e-14).compute(h, rho, a)

    def test_invalid_configuration_and_time(self):
        for name in ("hbar", "tolerance", "gap_tolerance", "amplitude_threshold", "activity_threshold"):
            for value in (-1, np.nan, np.inf):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    TransitionEngine(**{name: value})
        for name in ("hbar", "tolerance"):
            with self.assertRaises(ValueError):
                TransitionEngine(**{name: 0})
        for time in (np.nan, np.inf):
            with self.assertRaises(ValueError):
                TransitionEngine().compute(Z, RHO, X, time)
        with self.assertRaisesRegex(ValueError, "must agree"):
            TransitionEngine(hbar=1, units=QuantumUnits(hbar=.5))

    def test_units_and_explicit_snapshot_context(self):
        units = QuantumUnits(hbar=1e-34, energy_unit="J")
        frame = TransitionEngine(units=units, gap_tolerance=1e-25).compute(1e-22*Z, RHO, X, CTX.time, context=CTX)
        np.testing.assert_allclose(np.abs([e.omega for e in frame.transitions]), 2e12)
        self.assertEqual(frame.units.omega_unit, "rad/s")
        self.assertIs(frame.context, CTX)
        for ctx, time in [(CTX, 0), (replace(CTX, time_unit="tick"), CTX.time)]:
            with self.assertRaisesRegex(ValueError, "must agree"):
                TransitionEngine().compute(Z, RHO, X, time, context=ctx)

    def test_general_coupling_process_keeps_legacy_contract(self):
        a = np.array([[0, 3j], [0, 0]])
        frame = TransitionEngine().process(np.diag([0., 2.]), a, RHO, CTX)
        self.assertEqual(len(frame.edges), 2)
        self.assertIsNone(frame.edges[0].phase_rad)
        self.assertEqual(frame.edges[1].A_mn, 3j)
        self.assertEqual([(e.source, e.target) for e in frame.transitions], [(1, 0)])
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            TransitionEngine().compute(Z, RHO, a)

    def test_custom_diagnostic_activity_uses_same_filter_and_retains_matrix(self):
        class MatrixOnly:
            name = "matrix_only"
            units = "operator_unit_squared"
            def evaluate(self, spectrum, operator_in_energy_basis):
                return np.abs(operator_in_energy_basis)**2
        frame = TransitionEngine(activity_model=MatrixOnly(), activity_threshold=.5).compute(Z, np.diag([1., 0.]), X)
        self.assertEqual(len(frame.transitions), 2)
        self.assertEqual(frame.activity_name, "matrix_only")
        np.testing.assert_array_equal(frame.diagnostic_activity, X.real)

    def test_invalid_activity_models_are_rejected(self):
        class Bad:
            name = "bad"
            units = "diagnostic"
            def evaluate(self, *args):
                return self.result
        for value in (np.ones((2, 2), complex), np.full((2, 2), np.nan),
                      np.full((2, 2), np.inf), -np.ones((2, 2)), np.ones((3, 3))):
            model = Bad()
            model.result = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                TransitionEngine(activity_model=model).compute(Z, RHO, X)

    def test_nonfinite_derived_matrices_are_rejected_even_without_edges(self):
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            TransitionEngine(hbar=np.finfo(float).tiny, gap_tolerance=100).compute(4*Z, RHO, Z)
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            TransitionEngine().compute(Z, RHO, 1e200*X)

    def test_no_mutation_and_all_matrix_products_are_readonly(self):
        args = [Z.copy(), RHO.copy(), X.copy()]
        originals = [a.copy() for a in args]
        frame = TransitionEngine().compute(*args)
        for a, original in zip(args, originals):
            np.testing.assert_array_equal(a, original)
        for name in ("energies", "eigenvectors", "amplitudes", "A_E", "magnitudes", "phases", "rho_E", "populations", "coherences", "delta_E", "omega", "diagnostic_activity"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                getattr(frame, name).flat[0] = 123
        args[0][:] = 123
        np.testing.assert_array_equal(frame.energies, [-1, 1])
        with self.assertRaises(TypeError):
            frame.diagnostics["bad"] = True
        with self.assertRaises(TypeError):
            frame.transitions[0].activity["bad"] = 1

    def test_eigenvector_gauge_changes_phase_not_activity(self):
        engine = TransitionEngine()
        ref = engine.compute(np.diag([0., 2.]), RHO, X)
        eigh = np.linalg.eigh
        def phased(a):
            values, vectors = eigh(a)
            return values, vectors*np.exp(1j*np.array([.2, 1.1]))
        with patch("qmw.core.quantum_spectrum.np.linalg.eigh", side_effect=phased):
            changed = engine.compute(np.diag([0., 2.]), RHO, X)
        self.assertNotAlmostEqual(ref.transitions[0].phase_rad, changed.transitions[0].phase_rad)
        np.testing.assert_allclose(ref.magnitudes, changed.magnitudes, atol=1e-12)
        np.testing.assert_allclose(ref.diagnostic_activity, changed.diagnostic_activity, atol=1e-12)

    def test_state_adapter_rejects_missing_or_mismatched_authority(self):
        state = QuantumStateFrame(CTX.time, CTX.dt, RHO, None, CTX.source_id)
        with self.assertRaisesRegex(ValueError, "Hamiltonian"):
            TransitionEngine().process_state(state, X, CTX)
        state.hamiltonian = Z
        with self.assertRaisesRegex(ValueError, "must agree"):
            TransitionEngine().process_state(state, X, replace(CTX, time=2))


if __name__ == "__main__":
    unittest.main()
