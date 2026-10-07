import unittest

import numpy as np

from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureId, FeatureValue, Provenance,
)
from qmw.architecture_v1.basis import BasisProjector
from qmw_representation_laboratory_v4.transforms.qft import QFTOperator


def feature(path, value, *, units='1', basis=None, record_id='frame-1'):
    array = np.asarray(value)
    metadata = basis or BasisMetadata('canonical', array.shape[0], 'computational')
    p = Provenance(record_id, path, 'fixture', '1', {}, units, 'none', metadata,
                   ClockStamp(0.0, 's', 'simulation', 'elapsed', 'fixture-start'),
                   'numpy', 'deterministic_fixture')
    return FeatureValue(FeatureId(path, path.split('.')[-1], 'matrix'), value, p)


class BasisTests(unittest.TestCase):
    def setUp(self):
        self.projector = BasisProjector()
        rng = np.random.default_rng(41)
        z = rng.normal(size=(16, 16)) + 1j*rng.normal(size=(16, 16))
        self.rho = z @ z.conj().T
        self.rho /= np.trace(self.rho)
        self.rho_f = feature('qmw.state.rho', self.rho)
        self.h_f = feature('qmw.state.hamiltonian', (z+z.conj().T)/2, units='J')

    def test_four_representations_roundtrip_do_not_mutate(self):
        before = self.rho.copy()
        bases = [
            self.projector.computational(16, self.rho_f.provenance),
            self.projector.hamiltonian(self.h_f),
            self.projector.qho(16, self.rho_f.provenance, canonical_coordinates='fock'),
            self.projector.qft(16, self.rho_f.provenance),
        ]
        for basis in bases:
            with self.subTest(basis=basis.metadata.kind):
                frame = self.projector.project(self.rho_f, basis, {'H': self.h_f})
                np.testing.assert_allclose(self.projector.inverse(frame.rho, basis), self.rho, atol=3e-14)
                self.assertLess(frame.diagnostics['roundtrip_error'], 3e-14)
                self.assertLess(frame.diagnostics['purity_error'], 3e-14)
                np.testing.assert_allclose(np.trace(frame.rho@frame.operators['H']),
                                           np.trace(self.rho@self.h_f.value), atol=3e-14)
                self.assertEqual(frame.provenance.parents[0], self.rho_f.provenance)
                self.assertIn(basis.provenance, frame.provenance.parents)
                self.assertIn(self.h_f.provenance, frame.provenance.parents)
                with self.assertRaises(ValueError):
                    frame.rho.setflags(write=True)
        np.testing.assert_array_equal(self.rho, before)

    def test_qft_retains_legacy_coordinate_sign_and_advertises_columns(self):
        b = self.projector.qft(16, self.rho_f.provenance)
        u = QFTOperator().unitary(16)
        np.testing.assert_allclose(b.vectors, u.conj().T)
        np.testing.assert_allclose(self.projector.project(self.rho_f, b).rho,
                                   QFTOperator().apply(self.rho), atol=1e-14)
        self.assertEqual(b.metadata.details['column_fourier_sign'], -1)
        inv = self.projector.qft(16, self.rho_f.provenance, inverse=True)
        np.testing.assert_allclose(inv.vectors, b.vectors.conj())

    def test_tiny_si_hamiltonian_is_not_treated_as_zero(self):
        h = np.array([[0, 1j], [-1j, 0]])*1e-30
        b = self.projector.hamiltonian(feature('qmw.H', h, units='J'))
        np.testing.assert_allclose(b.vectors.conj().T@(h/1e-30)@b.vectors,
                                   np.diag([-1, 1]), atol=2e-14)
        self.assertEqual(b.provenance.parameters['eigenvalue_units'], 'J')
        with self.assertRaises(ValueError):
            self.projector.hamiltonian(feature('qmw.H', [[0, 1e-30], [0, 0]], units='J'))

    def test_exact_degeneracy_has_deterministic_gauge(self):
        h = np.diag([0, 0, 1, 1]).astype(complex)
        p = feature('qmw.H', h)
        first = self.projector.hamiltonian(p)
        second = self.projector.hamiltonian(p)
        np.testing.assert_allclose(first.vectors, np.eye(4), atol=1e-14)
        np.testing.assert_array_equal(first.vectors, second.vectors)
        self.assertEqual(first.metadata.details['degenerate_groups'], ((0, 1), (2, 3)))
        self.assertFalse(first.metadata.details['individual_degenerate_vectors_unique'])

    def test_continuity_reuses_legacy_tracker_and_records_identity_order(self):
        first = self.projector.hamiltonian(self.h_f)
        next_h = feature('qmw.state.hamiltonian', self.h_f.value+1e-6*np.diag(np.arange(16)), units='J', record_id='frame-2')
        second = self.projector.hamiltonian(next_h, previous=first)
        overlaps = np.diag(first.vectors.conj().T@second.vectors)
        self.assertTrue(np.all(overlaps.real > .999))
        self.assertLess(np.max(np.abs(overlaps.imag)), 1e-13)
        self.assertEqual(second.metadata.ordering, 'overlap_identity')
        self.assertTrue(second.metadata.details['tracking_applied'])
        self.assertIn(first.provenance, second.provenance.parents)

    def test_near_degeneracy_does_not_mix_distinct_eigenvectors(self):
        angle = .31
        v = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        h = v@np.diag([1, 1+2e-10])@v.T
        b = self.projector.hamiltonian(feature('qmw.H', h))
        self.assertEqual(b.metadata.details['degenerate_groups'], ())
        self.assertEqual(b.metadata.details['near_degenerate_groups'], ((0, 1),))
        self.assertLess(np.linalg.norm(b.vectors.conj().T@h@b.vectors-np.diag(b.eigenvalues)), 1e-14)

    def test_zero_hamiltonian_remains_valid(self):
        b = self.projector.hamiltonian(feature('qmw.H', np.zeros((4, 4))))
        np.testing.assert_array_equal(b.eigenvalues, np.zeros(4))
        np.testing.assert_array_equal(b.vectors, np.eye(4))

    def test_qho_requires_declared_fock_or_supplied_basis(self):
        with self.assertRaises(ValueError):
            self.projector.qho(16, self.rho_f.provenance)
        qft = self.projector.qft(16, self.rho_f.provenance)
        supplied = feature('qho.verified.vectors', qft.vectors)
        q = self.projector.qho(16, self.rho_f.provenance, vectors=supplied)
        self.assertIn(supplied.provenance, q.provenance.parents)
        self.assertEqual(q.metadata.details['oscillator_model'], 'caller_supplied_verified_basis')

    def test_geometry_is_verified_square_orthonormal_only(self):
        b = self.projector.geometry(feature('geometry.vectors', np.eye(16)))
        np.testing.assert_array_equal(b.vectors, np.eye(16))
        for modes in (np.ones((16, 16)), np.eye(16)[:, :5], np.eye(16)*2):
            with self.assertRaises(ValueError):
                self.projector.geometry(feature('geometry.vectors', modes))

    def test_modal_projection_preserves_nonorthogonal_gram_and_no_probabilities(self):
        modes = np.eye(16)[:, :3].copy()
        modes[:, 1] = modes[:, 0]+modes[:, 1]
        m = feature('geometry.bank', modes)
        frame = self.projector.project_modal(self.rho_f, m)
        np.testing.assert_allclose(frame.get('analysis.modal.gram').value, modes.T@modes)
        np.testing.assert_allclose(frame.get('analysis.modal.matrix').value, modes.T@self.rho@modes)
        self.assertFalse(frame.metadata['orthonormal'])
        self.assertFalse(frame.metadata['trace_is_probability'])
        self.assertIn(m.provenance, frame.get('analysis.modal.matrix').provenance.parents)
        with self.assertRaises(TypeError):
            self.projector.inverse(frame.get('analysis.modal.matrix'), m)

    def test_orthonormal_truncated_modal_trace_is_captured_probability(self):
        frame = self.projector.project_modal(self.rho_f, feature('geometry.bank', np.eye(16)[:, :4]))
        self.assertTrue(frame.metadata['trace_is_probability'])
        self.assertAlmostEqual(frame.get('analysis.modal.captured_weight').value,
                               np.trace(self.rho[:4, :4]).real)
        self.assertGreaterEqual(frame.metadata['unprojected_probability'], 0)

    def test_phases_at_zero_are_masked(self):
        rho = feature('qmw.state.rho', np.diag([1., 0.]))
        frame = self.projector.project(rho, self.projector.computational(2, rho.provenance))
        self.assertFalse(np.any(frame.phase_valid))
        np.testing.assert_array_equal(frame.phases, np.zeros((2, 2)))

    def test_coordinate_mismatch_missing_invalid_density_rejected(self):
        b = self.projector.computational(16, self.rho_f.provenance)
        mismatch = feature('qmw.state.rho', self.rho, basis=BasisMetadata('other', 16, 'computational'))
        with self.assertRaises(ValueError):
            self.projector.project(mismatch, b)
        missing = FeatureValue(self.rho_f.id, None, self.rho_f.provenance, 'missing', 'rho inaccessible')
        with self.assertRaises(ValueError):
            self.projector.project(missing, b)
        with self.assertRaises(ValueError):
            self.projector.project(feature('qmw.state.rho', np.diag([2.]+[0.]*15)), b)
        wrong_op = feature('qmw.other.operator', np.eye(16), basis=BasisMetadata('other', 16, 'computational'))
        with self.assertRaises(ValueError):
            self.projector.project(self.rho_f, b, {'A': wrong_op})

    def test_basis_provenance_digest_is_deterministic_and_has_transform_values(self):
        a = self.projector.qft(16, self.rho_f.provenance)
        b = self.projector.qft(16, self.rho_f.provenance)
        self.assertEqual(a.provenance.digest, b.provenance.digest)
        self.assertEqual(len(a.provenance.parameters['vectors_sha256']), 64)
        self.assertEqual(a.metadata.details['convention'], 'rho_basis = V_dagger rho V')

    def test_nested_reference_metadata_survives_contract_freezing(self):
        md = BasisMetadata('canonical', 2, 'computational', details={'labels': ['0', '1']})
        rho = feature('qmw.rho', np.eye(2)/2, basis=md)
        basis = self.projector.computational(2, rho.provenance)
        np.testing.assert_allclose(self.projector.project(rho, basis).rho, rho.value)

    def test_complex_nonhermitian_operator_roundtrip(self):
        a = np.zeros((16, 16), complex)
        a[0, 2] = 2+3j
        af = feature('qmw.operator.ladder', a)
        b = self.projector.qft(16, self.rho_f.provenance)
        frame = self.projector.project(self.rho_f, b, {'ladder': af})
        np.testing.assert_allclose(self.projector.inverse(frame.operators['ladder'], b), a, atol=2e-14)

    def test_exact_degenerate_continuity_uses_subspace_gauge(self):
        import hashlib
        from qmw.architecture_v1.contracts import AnalysisBasis
        h = feature('qmw.H', np.diag([0., 0., 1., 2.]))
        canonical = self.projector.hamiltonian(h)
        v = canonical.vectors.copy()
        angle = .37
        v[:, :2] = v[:, :2]@np.array([[np.cos(angle), 1j*np.sin(angle)],
                                    [1j*np.sin(angle), np.cos(angle)]])
        rotated_provenance = canonical.provenance.derive(
            'fixture:degenerate_gauge', 'explicit_degenerate_subspace_rotation',
            parameters={**canonical.provenance.parameters,
                        'vectors_sha256': hashlib.sha256(np.asarray(v, dtype='<c16').tobytes()).hexdigest(),
                        'rotation_angle': angle})
        rotated = AnalysisBasis(canonical.metadata, v, rotated_provenance, canonical.eigenvalues)
        tracked = self.projector.hamiltonian(h, previous=rotated)
        np.testing.assert_allclose(tracked.vectors[:, :2], rotated.vectors[:, :2], atol=2e-14)
        np.testing.assert_allclose(tracked.vectors.conj().T@h.value@tracked.vectors,
                                   np.diag(tracked.eigenvalues), atol=2e-14)

    def test_overlap_order_can_cross_energy_order_without_claiming_ascending(self):
        a = self.projector.hamiltonian(feature('qmw.H', np.diag([-.1, .1])))
        b = self.projector.hamiltonian(feature('qmw.H', np.diag([.1, -.1])), previous=a)
        np.testing.assert_allclose(b.vectors, a.vectors)
        np.testing.assert_allclose(b.eigenvalues, [.1, -.1])
        self.assertEqual(b.metadata.ordering, 'overlap_identity')


if __name__ == '__main__':
    unittest.main()
