"""Scientific contracts written before the first implementation; see red.log."""
from dataclasses import fields, replace
from unittest.mock import patch
import unittest

import numpy as np

from qmw.core.state_frame import QuantumStateFrame
from qmw.core.quantum_data_bus import QuantumDataBus
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
from qmw.acoustics.note_timbre import (
    GeometryModes, QuantumTimbreProjector, RatioField,
    TransitionPitchProjector, OfflineModalResonator,
)


X = np.array([[0, 1], [1, 0]], complex)
Z = np.diag([1., -1.])
H = np.diag([0., 2.])
RHO = np.array([[.7, .1j], [-.1j, .3]])
CTX = FrameContext(source_id="fixture", frame_id=7, time=.5, dt=.02,
                   basis_id="qubit:q0-lsb", provenance=("prepared fixture",))


def unitary(n, seed=23):
    rng = np.random.default_rng(seed)
    return np.linalg.qr(rng.normal(size=(n, n)) + 1j*rng.normal(size=(n, n)))[0]


def geometry(n=2, vectors=None, **kw):
    phi = np.eye(n, dtype=complex) if vectors is None else vectors
    count = phi.shape[1]
    args = dict(hilbert_vectors=phi, space_id=CTX.basis_id,
                geometry_id="declared-hilbert-body", mode_ids=tuple(f"mode-{j+1}" for j in range(count)),
                frequencies_hz=np.linspace(220, 1100, count),
                quality_factors=np.full(count, 30.), acoustic_phases_rad=np.zeros(count),
                complete=count == n, provenance=("independently declared body",))
    return GeometryModes(**(args | kw))


def pitch(n=2, **kw):
    return TransitionPitchProjector(state_degrees=tuple(range(n)),
        ratio_field=RatioField((1., 9/8, 5/4, 4/3, 3/2), period=2., reference_hz=220.,
                              name="just-five"), **kw)


class TransitionContracts(unittest.TestCase):
    def test_x_z_selection_signed_gaps_and_units(self):
        f = TransitionEngine(units=QuantumUnits(hbar=.5, energy_unit="eV")).process(H, X, RHO, CTX)
        self.assertEqual([(e.source, e.target) for e in f.edges], [(0, 1), (1, 0)])
        self.assertEqual([e.delta_E for e in f.edges], [2., -2.])
        self.assertEqual([e.omega for e in f.edges], [4., -4.])
        self.assertEqual(f.units.omega_unit, "rad/s")
        self.assertEqual(f.units.hbar_unit, "eV*s")
        self.assertEqual([e.magnitude for e in f.edges], [1., 1.])
        self.assertAlmostEqual(f.edges[0].activity["population_weighted_matrix_element"], .7)
        self.assertEqual(pitch().process(TransitionEngine().process(H, Z, RHO, CTX)), ())

    def test_transforms_and_residuals(self):
        u = unitary(2)
        h, a, rho = [u @ m @ u.conj().T for m in (H, X, RHO)]
        f = TransitionEngine().process(h, a, rho, CTX)
        v = f.spectrum.energy_eigenvectors
        np.testing.assert_allclose(h @ v, v * f.spectrum.energy_eigenvalues, atol=1e-12)
        np.testing.assert_allclose(f.operator_in_energy_basis, v.conj().T @ a @ v)
        np.testing.assert_allclose(f.spectrum.rho_in_energy_basis, v.conj().T @ rho @ v)
        e = f.edges[0]
        self.assertEqual(e.A_mn, f.operator_in_energy_basis[e.target, e.source])
        self.assertEqual(e.coherence_mn, f.spectrum.rho_in_energy_basis[e.target, e.source])
        self.assertEqual(e.coherence_nm, f.spectrum.rho_in_energy_basis[e.source, e.target])
        self.assertLess(f.diagnostics["hamiltonian_residual_fro"], 1e-12)
        self.assertLess(f.diagnostics["density_reconstruction_residual_fro"], 1e-12)

    def test_nonhermitian_coupling_is_allowed(self):
        a = np.array([[0., 3j], [0., 0.]])
        f = TransitionEngine().process(H, a, RHO, CTX)
        self.assertEqual(f.edges[1].A_mn, 3j)
        self.assertAlmostEqual(f.edges[1].phase_rad, np.pi/2)
        self.assertIsNone(f.edges[0].phase_rad)
        self.assertEqual([(e.source_state, e.target_state) for e in pitch().process(f)], [(1, 0)])

    def test_diagonal_and_zero_gap_policy(self):
        f = TransitionEngine().process(np.eye(2), X, RHO, CTX)
        self.assertEqual(f.edges, ())
        self.assertEqual(f.energy_degenerate_groups, ((0, 1),))
        self.assertIn("frame-local", f.label_convention)
        f = TransitionEngine(include_zero_gap=True, include_diagonal=True).process(np.eye(2), X, RHO, CTX)
        self.assertEqual(len(f.edges), 4)
        self.assertTrue(all(e.zero_gap for e in f.edges))
        self.assertTrue(all(e.basis_dependent_degenerate_endpoint for e in f.edges))
        # The downstream default still does not emit diagonal/zero-gap notes.
        self.assertEqual(pitch().process(f), ())

    def test_energy_gauge_changes_phase_but_not_activity(self):
        original = TransitionEngine().process(H, X, RHO, CTX)
        eigh = np.linalg.eigh
        def phased(a):
            vals, vecs = eigh(a)
            return vals, vecs @ np.diag(np.exp(1j*np.array([.2, 1.1])))
        with patch("qmw.core.quantum_spectrum.np.linalg.eigh", side_effect=phased):
            shifted = TransitionEngine().process(H, X, RHO, CTX)
        self.assertNotAlmostEqual(original.edges[0].phase_rad, shifted.edges[0].phase_rad)
        for e, s in zip(original.edges, shifted.edges):
            self.assertAlmostEqual(e.magnitude, s.magnitude)
            self.assertAlmostEqual(e.activity["population_weighted_matrix_element"],
                                   s.activity["population_weighted_matrix_element"])

    def test_activity_model_is_named_and_validated(self):
        class MatrixOnly:
            name = "matrix_element_squared"
            units = "operator_unit_squared"
            def evaluate(self, spectrum, operator_in_energy_basis):
                return np.abs(operator_in_energy_basis)**2
        f = TransitionEngine(activity_model=MatrixOnly()).process(H, X, RHO, CTX)
        self.assertEqual(f.activity_name, MatrixOnly.name)
        self.assertEqual(f.edges[0].activity[MatrixOnly.name], 1.)
        self.assertIn("diagnostic", f.activity_interpretation)
        class Bad(MatrixOnly):
            def evaluate(self, *args):
                return np.full((2, 2), np.nan)
        with self.assertRaises(ValueError):
            TransitionEngine(activity_model=Bad()).process(H, X, RHO, CTX)

    def test_complex_activity_is_rejected_without_discarding_imaginary_values(self):
        class Bad:
            name = "invalid_complex_diagnostic"
            units = "dimensionless"
            def evaluate(self, *args):
                return np.ones((2,2))*(1+2j)
        with self.assertRaises(ValueError):
            TransitionEngine(activity_model=Bad()).process(H,X,RHO,CTX)

    def test_passive_basis_does_not_admit_numerical_forbidden_edges(self):
        u = unitary(2)
        f = TransitionEngine().process(u@H@u.conj().T, u@Z@u.conj().T, u@RHO@u.conj().T, CTX)
        self.assertEqual(pitch().process(f), ())

    def test_si_units_and_time_context_consistency(self):
        f = TransitionEngine(units=QuantumUnits(hbar=1e-34,energy_unit="J"), gap_tolerance=1e-25).process(1e-22*H,X,RHO,CTX)
        self.assertAlmostEqual(f.edges[0].omega/1e12, 2.)
        with self.assertRaises(ValueError):
            TransitionEngine().process(H,X,RHO,replace(CTX,time_unit="model_tick"))

    def test_invalid_operator_hamiltonian_and_tolerances(self):
        for h, a in [(H+1j*np.eye(2), X), (H, np.ones((3,3))),
                     (H, X*np.nan), (np.ones((2,3)), X)]:
            with self.subTest(h=h, a=a), self.assertRaises(ValueError):
                TransitionEngine().process(h, a, RHO, CTX)
        for value in [0, -1, np.nan, np.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                TransitionEngine(tolerance=value)
            with self.assertRaises(ValueError):
                QuantumUnits(hbar=value)
        # SI-scale H still must be Hermitian relative to its own norm.
        with self.assertRaises(ValueError):
            TransitionEngine().process(1e-22*(H+1j*X), X, RHO, CTX)

    def test_no_mutation_and_readonly_products(self):
        args = [H.copy(), X.copy(), RHO.copy()]
        old = [a.copy() for a in args]
        f = TransitionEngine().process(*args, CTX)
        for a, b in zip(args, old):
            np.testing.assert_array_equal(a, b)
        args[0][0,0] = 123
        self.assertEqual(f.spectrum.energy_eigenvalues[0], 0)
        with self.assertRaises(ValueError):
            f.operator_in_energy_basis[0,0] = 12
        with self.assertRaises(TypeError):
            f.edges[0].activity["bad"] = 1


class TimbreContracts(unittest.TestCase):
    def test_density_reconstruction_modal_expectations_and_statistics(self):
        phi = unitary(2)
        b = QuantumTimbreProjector().process(rho=RHO, geometry_modes=geometry(vectors=phi), context=CTX)
        v, lam = b.density_eigenvectors, b.density_eigenvalues
        np.testing.assert_allclose((v*lam) @ v.conj().T, RHO, atol=1e-12)
        np.testing.assert_allclose(b.density_geometry_overlap, phi.conj().T @ v)
        expected = np.diag(phi.conj().T @ RHO @ phi).real
        np.testing.assert_allclose(b.modal_probability_weights, expected, atol=1e-12)
        np.testing.assert_allclose(b.amplitude_gains**2, expected, atol=1e-12)
        self.assertAlmostEqual(b.captured_weight, 1.)
        self.assertAlmostEqual(b.purity, np.trace(RHO @ RHO).real)
        self.assertAlmostEqual(b.entropy_nats, -sum(lam*np.log(lam)))
        np.testing.assert_allclose(b.decay_seconds, b.quality_factors/(np.pi*b.frequencies_hz))
        self.assertLess(b.diagnostics["modal_expectation_residual_max"], 1e-12)

    def test_degenerate_density_and_eigenvector_phase_invariance(self):
        rho = np.eye(4)/4
        g = geometry(4, unitary(4))
        project = QuantumTimbreProjector()
        ref = project.process(rho=rho, geometry_modes=g, context=CTX)
        eigh = np.linalg.eigh
        def rotated(a):
            vals, vecs = eigh(a)
            return vals, vecs @ unitary(4, 65)
        with patch("qmw.core.quantum_spectrum.np.linalg.eigh", side_effect=rotated):
            other = project.process(rho=rho, geometry_modes=g, context=CTX)
        np.testing.assert_allclose(other.modal_probability_weights, ref.modal_probability_weights, atol=1e-12)
        self.assertAlmostEqual(other.entropy_nats, np.log(4))
        self.assertFalse(np.allclose(ref.density_eigenvectors, other.density_eigenvectors))

    def test_passive_coordinates_and_geometry_column_phases(self):
        u, phi = unitary(2), unitary(2, 47)
        p = QuantumTimbreProjector()
        a = p.process(rho=RHO, geometry_modes=geometry(vectors=phi), context=CTX)
        b = p.process(rho=u.conj().T @ RHO @ u,
            geometry_modes=geometry(vectors=u.conj().T @ phi @ np.diag([1j, -1])), context=CTX)
        np.testing.assert_allclose(a.modal_probability_weights, b.modal_probability_weights, atol=1e-12)

    def test_geometry_is_independent_and_changes_weights(self):
        p = QuantumTimbreProjector()
        a = p.process(rho=np.diag([1.,0.]), geometry_modes=geometry(), context=CTX)
        phi = np.array([[1,1],[1,-1]])/np.sqrt(2)
        b = p.process(rho=np.diag([1.,0.]), geometry_modes=geometry(vectors=phi), context=CTX)
        np.testing.assert_allclose(a.modal_probability_weights, [1,0])
        np.testing.assert_allclose(b.modal_probability_weights, [.5,.5])

    def test_incomplete_basis_preserves_captured_weight_including_zero(self):
        g = geometry(vectors=np.eye(2)[:,1:])
        p = QuantumTimbreProjector()
        b = p.process(rho=RHO, geometry_modes=g, context=CTX)
        self.assertAlmostEqual(b.captured_weight, .3)
        self.assertAlmostEqual(b.modal_probability_weights[0], .3)
        self.assertFalse(b.complete_basis)
        b = p.process(rho=np.diag([1.,0.]), geometry_modes=g, context=CTX)
        self.assertEqual(b.captured_weight, 0.)
        np.testing.assert_array_equal(b.amplitude_gains, [0.])

    def test_invalid_density_rejection_and_explicit_roundoff(self):
        p = QuantumTimbreProjector(tolerance=1e-10)
        for rho in [np.diag([1.1,-.1]), np.eye(2), RHO+1j*np.eye(2),
                    np.array([[.5, .1],[.2,.5]]), np.full((2,2),np.inf), np.array([])]:
            with self.subTest(rho=rho), self.assertRaises(ValueError):
                p.process(rho=rho, geometry_modes=geometry(), context=CTX)
        rho = np.diag([1+1e-12, -1e-12])
        b = p.process(rho=rho, geometry_modes=geometry(), context=CTX)
        self.assertLess(min(b.density_eigenvalues), 0)
        self.assertLess(min(b.modal_probability_weights), 0)
        self.assertEqual(min(b.amplitude_gains), 0)
        self.assertGreater(b.diagnostics["negative_eigenvalue_mass"], 0)
        np.testing.assert_array_equal(rho, np.diag([1+1e-12,-1e-12]))

    def test_invalid_geometry_and_unsupported_spaces_rejected(self):
        for kw in [dict(hilbert_vectors=np.ones((2,2))), dict(frequencies_hz=[0,200]),
                   dict(quality_factors=[1,-1]), dict(acoustic_phases_rad=[0,np.nan]),
                   dict(mode_ids=("a","a")), dict(inner_product="mesh_mass"),
                   dict(complete=True, hilbert_vectors=np.eye(2)[:,:1]),
                   dict(hilbert_vectors=np.eye(3)[:,:2]), dict(space_id="mesh-vertices")]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                QuantumTimbreProjector().process(rho=RHO, geometry_modes=geometry(**kw), context=CTX)

    def test_snapshot_inputs_and_outputs(self):
        phi, rho = unitary(2), RHO.copy()
        old_phi, old_rho = phi.copy(), rho.copy()
        b = QuantumTimbreProjector().process(rho=rho, geometry_modes=geometry(vectors=phi), context=CTX)
        np.testing.assert_array_equal(phi, old_phi)
        np.testing.assert_array_equal(rho, old_rho)
        for name in ["density_eigenvalues", "density_eigenvectors", "density_geometry_overlap",
                     "modal_probability_weights", "frequencies_hz", "amplitude_gains"]:
            self.assertFalse(getattr(b, name).flags.writeable)

    def test_public_body_frame_rejects_invalid_acoustic_replacements(self):
        b = QuantumTimbreProjector().process(rho=RHO,geometry_modes=geometry(),context=CTX)
        for kw in [dict(frequencies_hz=[0,300]),dict(amplitude_gains=[-1,1]),
                   dict(acoustic_phases_rad=[0,np.inf]),dict(mode_ids=("x","x")),
                   dict(decay_seconds=[1,1]),dict(space_id="unrelated_space")]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                replace(b,**kw)

    def test_non_degenerate_density_eigenvector_phase_invariance(self):
        p, g = QuantumTimbreProjector(), geometry(vectors=unitary(2))
        ref = p.process(rho=RHO, geometry_modes=g, context=CTX)
        eigh = np.linalg.eigh
        def phased(a):
            vals, vecs = eigh(a)
            return vals, vecs*np.exp(1j*np.array([1.2,-.8]))
        with patch("qmw.core.quantum_spectrum.np.linalg.eigh", side_effect=phased):
            b = p.process(rho=RHO,geometry_modes=g,context=CTX)
        np.testing.assert_allclose(ref.modal_probability_weights,b.modal_probability_weights,atol=1e-12)
        self.assertFalse(np.allclose(ref.density_geometry_overlap,b.density_geometry_overlap))

    def test_near_hermitian_trace_and_positivity_tolerances_are_explicit(self):
        rho = RHO.copy(); rho[0,1] += 1e-12
        b = QuantumTimbreProjector().process(rho=rho, geometry_modes=geometry(),context=CTX)
        self.assertGreater(b.diagnostics["density_hermiticity_residual_fro"],0)
        self.assertGreater(b.diagnostics["density_reconstruction_residual_fro"],0)
        with self.assertRaises(ValueError):
            QuantumTimbreProjector(tolerance=1e-14).process(rho=rho,geometry_modes=geometry(),context=CTX)
        for eps in [1e-8,-1e-8]:
            with self.assertRaises(ValueError):
                QuantumTimbreProjector().process(rho=RHO+eps*np.eye(2),geometry_modes=geometry(),context=CTX)


class PitchAndJunctionContracts(unittest.TestCase):
    def test_deterministic_ratio_projection_and_provenance(self):
        f = TransitionEngine().process(H, X, RHO, CTX)
        p = pitch()
        a, b = p.process(f), p.process(f)
        self.assertEqual(a, b)
        self.assertEqual(a[0].source_frequency_hz, 220.)
        self.assertEqual(a[0].target_frequency_hz, 247.5)
        self.assertEqual(a[0].source_ratio, 1.)
        self.assertEqual(a[0].target_ratio, 9/8)
        self.assertEqual(a[0].context, CTX)
        self.assertEqual(a[0].onset_seconds, CTX.time)
        self.assertEqual(a[0].delta_E, 2.)
        self.assertIn("prepared fixture", a[0].provenance)
        self.assertFalse({"timbre", "purity", "entropy", "modal_weights"} & {x.name for x in fields(a[0])})
        self.assertNotEqual(a[0].event_id, a[1].event_id)

    def test_degree_period_negative_degrees_and_admission(self):
        ratios = RatioField((1, 5/4, 3/2), period=3, reference_hz=100, name="non-octave")
        self.assertAlmostEqual(ratios.ratio(-1), .5)
        self.assertAlmostEqual(ratios.frequency_hz(3), 300)
        f = TransitionEngine().process(H, X, RHO, CTX)
        a = pitch(min_activity=.4, max_events=1, delay_seconds=.125, duration_seconds=.05).process(f)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].onset_seconds, .625)
        self.assertEqual(a[0].strength, .7)
        self.assertEqual(a[0].duration_seconds, .05)
        self.assertEqual(pitch(min_activity=.7).process(f), ())
        for ratios in [(1,0),(1,np.nan),()]:
            with self.assertRaises(ValueError):
                RatioField(ratios)
        with self.assertRaises(ValueError):
            pitch(3).process(f)
        with self.assertRaises(ValueError):
            pitch(duration_seconds=-1)

    def test_branch_separation_in_both_directions_and_executable_audio(self):
        engine, tp, renderer = TransitionEngine(), QuantumTimbreProjector(), OfflineModalResonator(sample_rate=8000, duration_seconds=.064)
        f = engine.process(H, X, RHO, CTX)
        note = pitch().process(f)[0]
        g = geometry()
        body = tp.process(rho=RHO, geometry_modes=g, context=CTX)
        changed_body = tp.process(rho=RHO, geometry_modes=replace(g, frequencies_hz=np.array([330.,660.])), context=CTX)
        a, b = [renderer.process(excitation=note, timbre=body_) for body_ in [body, changed_body]]
        self.assertIs(a.excitation, note)
        self.assertIs(a.timbre, body)
        self.assertGreater(np.max(np.abs(a.audio)), 0)
        self.assertTrue(np.all(np.isfinite(a.audio)))
        self.assertFalse(np.allclose(a.audio, b.audio))
        np.testing.assert_array_equal(a.excitation_signal, b.excitation_signal)
        other = pitch(min_activity=.2).process(engine.process(2*H, 2*X, RHO, CTX))[0]
        c = renderer.process(excitation=other, timbre=body)
        np.testing.assert_array_equal(a.impulse_response, c.impulse_response)
        self.assertIs(c.timbre, body)
        np.testing.assert_array_equal(a.audio, renderer.process(excitation=note, timbre=body).audio)

    def test_renderer_uses_existing_ir_and_true_convolution(self):
        from density.density_matrix_modal_renderer_v2 import render_modal_frame
        note = pitch().process(TransitionEngine().process(H,X,RHO,CTX))[0]
        body = QuantumTimbreProjector().process(rho=RHO, geometry_modes=geometry(acoustic_phases_rad=[.3,.7]), context=CTX)
        r = OfflineModalResonator(sample_rate=8000, duration_seconds=.064)
        with patch("density.density_matrix_modal_renderer_v2.render_modal_frame", wraps=render_modal_frame) as reused:
            a = r.process(excitation=note, timbre=body)
        self.assertEqual(reused.call_count, 1)
        for channel in range(2):
            np.testing.assert_allclose(a.audio[:,channel],
                np.convolve(a.excitation_signal,a.impulse_response[:,channel])[:len(a.audio)], atol=1e-12)
        t = np.arange(len(a.audio))/8000
        expected = sum(amp*np.exp(-t/tau)*np.sin(2*np.pi*f*t+ph)/np.sqrt(2)
                       for f,amp,tau,ph in zip(body.frequencies_hz,body.amplitude_gains,body.decay_seconds,body.acoustic_phases_rad))
        np.testing.assert_allclose(a.impulse_response[:,0],expected,atol=1e-12)

    def test_silence_and_gauge_phase_is_metadata_only(self):
        note = pitch().process(TransitionEngine().process(H,X,RHO,CTX))[0]
        body = QuantumTimbreProjector().process(rho=RHO, geometry_modes=geometry(), context=CTX)
        r = OfflineModalResonator(sample_rate=8000, duration_seconds=.064)
        a = r.process(excitation=note, timbre=body)
        b = r.process(excitation=replace(note, phase_rad=1.7), timbre=body)
        np.testing.assert_array_equal(a.audio, b.audio)
        silent = r.process(excitation=replace(note, strength=0), timbre=body)
        np.testing.assert_array_equal(silent.audio, np.zeros_like(a.audio))

    def test_coherence_can_change_body_while_notes_remain_identical(self):
        engine, projector = TransitionEngine(), QuantumTimbreProjector()
        rho0 = np.diag([.7,.3]).astype(complex)
        rho1 = rho0 + .2*X
        notes0 = pitch().process(engine.process(H,X,rho0,CTX))
        notes1 = pitch().process(engine.process(H,X,rho1,CTX))
        self.assertEqual(notes0,notes1)
        phi = np.array([[1,1],[1,-1]])/np.sqrt(2)
        bodies = [projector.process(rho=rho,geometry_modes=geometry(vectors=phi),context=CTX) for rho in [rho0,rho1]]
        self.assertFalse(np.allclose(bodies[0].modal_probability_weights,bodies[1].modal_probability_weights))

    def test_body_acoustic_phase_changes_ir_without_changing_notes(self):
        note = pitch().process(TransitionEngine().process(H,X,RHO,CTX))[0]
        p = QuantumTimbreProjector()
        bodies = [p.process(rho=RHO,geometry_modes=geometry(acoustic_phases_rad=phase),context=CTX)
                  for phase in [[0,0],[1,1]]]
        r = OfflineModalResonator(sample_rate=8000,duration_seconds=.064)
        a,b = [r.process(excitation=note,timbre=body) for body in bodies]
        np.testing.assert_array_equal(a.excitation_signal,b.excitation_signal)
        self.assertFalse(np.allclose(a.impulse_response,b.impulse_response))

    def test_tuning_changes_excitation_but_keeps_the_body_response_fixed(self):
        f = TransitionEngine().process(H,X,RHO,CTX)
        note0 = pitch().process(f)[0]
        note1 = TransitionPitchProjector(state_degrees=(0,1),
            ratio_field=RatioField((1.,7/6),reference_hz=220.,name="septimal")).process(f)[0]
        self.assertNotEqual(note0.target_frequency_hz,note1.target_frequency_hz)
        body = QuantumTimbreProjector().process(rho=RHO,geometry_modes=geometry(),context=CTX)
        r = OfflineModalResonator(sample_rate=8000,duration_seconds=.064)
        a,b = [r.process(excitation=note,timbre=body) for note in [note0,note1]]
        self.assertIs(a.timbre,b.timbre)
        np.testing.assert_array_equal(a.impulse_response,b.impulse_response)
        self.assertFalse(np.allclose(a.excitation_signal,b.excitation_signal))
        self.assertFalse(np.allclose(a.audio,b.audio))

    def test_aliasing_and_mismatched_frame_rejected(self):
        note = pitch().process(TransitionEngine().process(H,X,RHO,CTX))[0]
        body = QuantumTimbreProjector().process(rho=RHO, geometry_modes=geometry(), context=CTX)
        r = OfflineModalResonator(sample_rate=8000, duration_seconds=.064)
        with self.assertRaises(ValueError):
            r.process(excitation=replace(note,target_frequency_hz=5000), timbre=body)
        with self.assertRaises(ValueError):
            r.process(excitation=note, timbre=replace(body,context=replace(CTX,frame_id=8)))

    def test_four_qubit_state_bus_vertical_slice_with_passive_qft_basis(self):
        # Four-qubit GHZ mixed with I/16; q0 is least-significant bit.
        psi = np.zeros(16, complex); psi[0] = psi[15] = 1/np.sqrt(2)
        rho = .8*np.outer(psi,psi.conj()) + .2*np.eye(16)/16
        h = np.diag(np.arange(16, dtype=float))
        a = np.kron(np.eye(8), X)
        qft = np.exp(2j*np.pi*np.outer(np.arange(16),np.arange(16))/16)/4
        ctx = replace(CTX, frame_id=16)
        frame = QuantumStateFrame(t=ctx.time, dt=ctx.dt, rho=rho.copy(), hamiltonian=h.copy(), source_name=ctx.source_id)
        bus, seen = QuantumDataBus(), []
        bus.state_bus.subscribe(lambda snapshot: seen.append(TransitionEngine().process_state(snapshot, a, ctx)))
        bus.publish_state(frame)
        # The canonical bus attaches spectrum diagnostics at publication.
        # Note/body projection must preserve those existing observer fields.
        arrays_before = {key: value.copy() for key, value in frame.arrays.items()}
        spectrum_before = frame.spectrum
        observables_before = dict(frame.observables)
        f = seen[0]
        self.assertIs(bus.latest_state, frame)
        notes = pitch(16).process(f)
        self.assertEqual(len(notes), 16)
        self.assertTrue(all(n.source_state ^ n.target_state == 1 for n in notes))
        body = QuantumTimbreProjector().process(rho=rho, geometry_modes=geometry(16,qft), context=ctx)
        np.testing.assert_allclose(body.modal_probability_weights, np.diag(qft.conj().T@rho@qft).real, atol=1e-12)
        self.assertAlmostEqual(body.purity, .8**2+(1-.8**2)/16)
        result = OfflineModalResonator(sample_rate=12000,duration_seconds=.05).process(excitation=notes[0],timbre=body)
        self.assertEqual(result.audio.shape,(600,2))
        self.assertGreater(np.linalg.norm(result.audio),0)
        np.testing.assert_array_equal(frame.rho,rho)
        np.testing.assert_array_equal(frame.hamiltonian,h)
        self.assertEqual(set(frame.arrays), set(arrays_before))
        for key, value in arrays_before.items():
            np.testing.assert_array_equal(frame.arrays[key], value)
        self.assertIs(frame.spectrum, spectrum_before)
        self.assertEqual(frame.observables,observables_before)


if __name__ == "__main__":
    unittest.main()
