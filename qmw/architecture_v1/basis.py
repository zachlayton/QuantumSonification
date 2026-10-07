"""Passive basis adapters over the existing QMW representation laboratory.

The shared ``AnalysisBasis.vectors`` contains columns V expressed in declared
reference coordinates. The laboratory exposes the coordinate transform U=V†.
Neither this adapter nor its continuity bookkeeping evolves the source state.
"""
from __future__ import annotations

import hashlib
import json
from typing import Mapping

import numpy as np

from qmw.qmw_representation_laboratory_v4.core.state_transform import validate_density_matrix
from qmw.qmw_representation_laboratory_v4.transforms._spectral import canonicalize_eigenspaces
from qmw.qmw_representation_laboratory_v4.transforms.hamiltonian import (
    HamiltonianBasisTracker, HamiltonianEigenbasis,
)
from qmw.qmw_representation_laboratory_v4.transforms.identity import IdentityOperator
from qmw.qmw_representation_laboratory_v4.transforms.qft import QFTOperator

from .contracts import (
    AnalysisBasis, BasisMetadata, BasisProjectionFrame, FeatureFrame, FeatureId,
    FeatureValue, Provenance, frozen_array, plain,
)


VERSION = '1'
CONVENTION = 'rho_basis = V_dagger rho V'


def _matrix(value, name, *, square=True):
    a = np.asarray(value, dtype=complex)
    if a.ndim != 2 or min(a.shape) < 1 or not np.all(np.isfinite(a)):
        raise ValueError(f'{name} must be a nonempty finite matrix')
    if square and a.shape[0] != a.shape[1]:
        raise ValueError(f'{name} must be square')
    return a


def _dimension(dimension, provenance):
    if isinstance(dimension, (bool, np.bool_)) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError('dimension must be a positive integer')
    if not isinstance(provenance, Provenance) or provenance.basis.dimension != dimension:
        raise ValueError('basis source must declare matching reference coordinates')
    return dimension


def _basis_key(metadata):
    return json.dumps(metadata.to_dict(), sort_keys=True, separators=(',', ':'))


def _reference_matches(basis, reference):
    declared = basis.metadata.details.get('reference_basis')
    return json.dumps(plain(declared), sort_keys=True, separators=(',', ':')) == _basis_key(reference)


def _same_coordinates(a, b):
    if _basis_key(a) != _basis_key(b):
        raise ValueError('sources must use the same declared reference coordinates')


def _groups(values, tolerance):
    """Groups retain actual column indices, even after overlap ordering."""
    order = np.argsort(values, kind='stable')
    groups = []
    start = 0
    while start < len(order):
        stop = start+1
        while stop < len(order) and abs(values[order[stop]]-values[order[start]]) <= tolerance:
            stop += 1
        if stop-start > 1:
            groups.append(tuple(sorted(int(i) for i in order[start:stop])))
        start = stop
    return tuple(groups)


class BasisProjector:
    """Stateless, provenance-preserving observer of declared input coordinates.

    Continuity is opt-in by passing an earlier ``AnalysisBasis``; an explicit
    snapshot avoids hidden tracker state or implicit ordering changes. Fourier
    QFT means the finite Hilbert-space Fourier transform, not quantum field
    dynamics. QHO Fock encoding is an explicit model interpretation.
    """

    def __init__(self, *, tolerance=1e-10, phase_tolerance=1e-14,
                 near_degeneracy_tolerance=1e-8):
        for name, value in (('tolerance', tolerance), ('phase_tolerance', phase_tolerance),
                            ('near_degeneracy_tolerance', near_degeneracy_tolerance)):
            if isinstance(value, (bool, np.bool_)) or not np.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        self.tolerance = float(tolerance)
        self.phase_tolerance = float(phase_tolerance)
        self.near_degeneracy_tolerance = float(near_degeneracy_tolerance)

    def _basis(self, vectors, provenance, *, basis_id, kind, ordering, gauge,
               details=None, eigenvalues=None, parents=None):
        v = _matrix(vectors, 'basis columns')
        dimension = _dimension(v.shape[0], provenance)
        metadata = BasisMetadata(
            basis_id, dimension, kind, provenance.basis.subsystem_order, ordering, gauge,
            {'convention': CONVENTION, 'reference_basis': provenance.basis.to_dict(),
             **(details or {})})
        parameters = {
            'convention': CONVENTION, 'basis_metadata': metadata.to_dict(),
            'vectors_sha256': hashlib.sha256(np.asarray(v, dtype='<c16').tobytes()).hexdigest(),
        }
        if eigenvalues is not None:
            parameters['eigenvalue_units'] = provenance.units
            parameters['eigenvalues'] = eigenvalues
        basis_provenance = provenance.derive(
            f'{provenance.record_id}:basis:{basis_id}', 'analysis_basis_construction', VERSION,
            parameters, units='1', normalization='orthonormal_columns', basis=metadata,
            parents=(provenance,) if parents is None else parents,
            source_path=f'analysis.basis.{basis_id}')
        return AnalysisBasis(metadata, v, basis_provenance, eigenvalues)

    def computational(self, dimension, provenance, *, basis_id='computational'):
        _dimension(dimension, provenance)
        return self._basis(
            IdentityOperator().unitary(dimension), provenance, basis_id=basis_id,
            kind='computational', ordering='coordinate_index', gauge='declared_coordinates')

    def qft(self, dimension, provenance, *, inverse=False, basis_id='qft'):
        _dimension(dimension, provenance)
        if not isinstance(inverse, bool):
            raise ValueError('inverse must be boolean')
        u = QFTOperator(inverse=inverse).unitary(dimension)
        return self._basis(
            u.conj().T, provenance, basis_id=basis_id, kind='qft',
            ordering='fourier_index', gauge='fixed_discrete_fourier_phase',
            details={'coordinate_fourier_sign': -1 if inverse else 1,
                     'column_fourier_sign': 1 if inverse else -1,
                     'inverse': inverse, 'index_origin': 0,
                     'interpretation': 'finite_hilbert_space_fourier_representation',
                     'reuse': 'qmw.qmw_representation_laboratory_v4.transforms.qft.QFTOperator'})

    def hamiltonian(self, hamiltonian_feature, *, previous=None, basis_id='hamiltonian'):
        if not isinstance(hamiltonian_feature, FeatureValue):
            raise TypeError('Hamiltonian requires a typed source feature')
        p = hamiltonian_feature.provenance
        h = _matrix(hamiltonian_feature.require_available(), 'Hamiltonian')
        n = _dimension(h.shape[0], p)
        # Relative validation matters for SI Hamiltonians, whose entries may
        # all be much smaller than a typical absolute floating-point tolerance.
        scale = float(np.max(np.abs(h)))
        scaled = h/scale if scale else np.zeros_like(h)
        if np.max(np.abs(scaled-scaled.conj().T)) > self.tolerance:
            raise ValueError('Hamiltonian must be Hermitian relative to its own scale')
        scaled = (scaled+scaled.conj().T)/2
        exact_tolerance = np.finfo(float).eps*max(1, n)*8
        tracking = {'tracking_applied': False, 'minimum_matched_overlap': 1.0}
        parents = (p,)
        if previous is None:
            values, vectors = np.linalg.eigh(scaled)
            # The legacy convenience constructor groups within 1e-9. Pass a
            # roundoff-scale tolerance explicitly to avoid mixing distinct
            # but nearby levels. Keep its established deterministic gauge.
            vectors = canonicalize_eigenspaces(values, vectors, tolerance=exact_tolerance)
            legacy = HamiltonianEigenbasis.from_eigendecomposition(scaled, values, vectors)
            ordering = 'ascending_energy'
            gauge = 'project_computational_axes_in_degenerate_space_then_largest_pivot_real_positive'
        else:
            if not isinstance(previous, AnalysisBasis) or previous.metadata.kind != 'hamiltonian':
                raise ValueError('previous must be a Hamiltonian AnalysisBasis')
            if previous.metadata.dimension != n or not _reference_matches(previous, p.basis):
                raise ValueError('previous basis must use identical reference coordinates')
            tracker = HamiltonianBasisTracker(degeneracy_tolerance=exact_tolerance)
            # Narrow adapter seam: the existing tracker has reset/solve but no
            # snapshot import. Seed only its documented previous-vector state;
            # do not duplicate its assignment, SVD, or phase-alignment logic.
            tracker._previous_vectors = np.array(previous.vectors, copy=True)
            legacy, tracking = tracker.solve(scaled)
            parents = (p, previous.provenance)
            ordering = 'overlap_identity'
            gauge = 'previous_overlap_phase_and_exact_degenerate_subspace_alignment'
        vectors = legacy.unitary(n).conj().T
        values = legacy.eigenvalues
        diagonalization_error = float(np.linalg.norm(
            vectors.conj().T@scaled@vectors-np.diag(values)))
        if diagonalization_error > self.tolerance*max(1.0, float(np.linalg.norm(scaled))):
            raise ValueError('tracked columns do not diagonalize the Hamiltonian')
        exact_groups = _groups(values, exact_tolerance)
        return self._basis(
            vectors, p, basis_id=basis_id, kind='hamiltonian', ordering=ordering,
            gauge=gauge, eigenvalues=values*scale, parents=parents,
            details={**tracking, 'hamiltonian_scale': scale,
                     'hamiltonian_units': p.units,
                     'scaled_diagonalization_error': diagonalization_error,
                     'scaled_exact_degeneracy_tolerance': exact_tolerance,
                     'scaled_near_degeneracy_tolerance': self.near_degeneracy_tolerance,
                     'degenerate_groups': exact_groups,
                     'near_degenerate_groups': _groups(values, self.near_degeneracy_tolerance),
                     'individual_degenerate_vectors_unique': not bool(exact_groups),
                     'continuity_limit': 'gauge_choice_only; crossings_may_reorder_energies',
                     'reuse': 'qmw.qmw_representation_laboratory_v4.transforms.hamiltonian'})

    def qho(self, dimension, provenance, *, canonical_coordinates=None, vectors=None,
            basis_id='qho'):
        _dimension(dimension, provenance)
        if vectors is None:
            if canonical_coordinates != 'fock':
                raise ValueError('QHO identity requires canonical_coordinates="fock"; otherwise supply verified vectors')
            v = IdentityOperator().unitary(dimension)
            parents = (provenance,)
            model = 'declared_truncated_fock_encoding'
            gauge = 'declared_fock_state_phases'
        else:
            if canonical_coordinates is not None:
                raise ValueError('choose a Fock declaration or supplied QHO columns')
            if not isinstance(vectors, FeatureValue):
                raise TypeError('supplied QHO vectors require source provenance')
            _same_coordinates(provenance.basis, vectors.provenance.basis)
            v = _matrix(vectors.require_available(), 'QHO columns')
            if v.shape != (dimension, dimension):
                raise ValueError('QHO columns must match the Hilbert dimension')
            parents = (provenance, vectors.provenance)
            model = 'caller_supplied_verified_basis'
            gauge = 'caller_declared_column_phases'
        return self._basis(
            v, provenance, basis_id=basis_id, kind='qho', ordering='excitation_number',
            gauge=gauge, parents=parents,
            details={'oscillator_model': model, 'index_origin': 0,
                     'fock_number_labels': list(range(dimension)),
                     'physical_oscillator_dynamics_inferred': False})

    def geometry(self, vectors_feature, *, basis_id='geometry'):
        if not isinstance(vectors_feature, FeatureValue):
            raise TypeError('geometry vectors require a typed source feature')
        return self._basis(
            vectors_feature.require_available(), vectors_feature.provenance,
            basis_id=basis_id, kind='geometry', ordering='declared_mode_index',
            gauge='caller_declared_column_phases',
            details={'metric': 'euclidean_inner_product',
                     'requirement': 'square_complete_orthonormal_bank',
                     'physical_geometry_inferred': False})

    def project(self, rho_feature, basis, operators: Mapping[str, FeatureValue] | None = None,
                *, frame_id=None):
        if not isinstance(rho_feature, FeatureValue) or not isinstance(basis, AnalysisBasis):
            raise TypeError('projection requires a typed rho feature and shared AnalysisBasis')
        if not _reference_matches(basis, rho_feature.provenance.basis):
            raise ValueError('rho and basis must use identical reference coordinates')
        density = validate_density_matrix(rho_feature.require_available(), tolerance=self.tolerance)
        if density.shape != basis.vectors.shape:
            raise ValueError('rho dimension does not match basis')
        v = basis.vectors
        projected = v.conj().T@density@v
        projected = (projected+projected.conj().T)/2
        ops = {}
        operator_sources = {}
        parents = [rho_feature.provenance, basis.provenance]
        for name, source in (operators or {}).items():
            if not isinstance(name, str) or not name.strip() or not isinstance(source, FeatureValue):
                raise ValueError('operators require nonempty names and typed source features')
            _same_coordinates(source.provenance.basis, rho_feature.provenance.basis)
            matrix = _matrix(source.require_available(), name)
            if matrix.shape != density.shape:
                raise ValueError('operator dimension does not match rho')
            ops[name] = v.conj().T@matrix@v
            operator_sources[name] = {'feature_id': source.id.to_dict(), 'units': source.units,
                                      'source_provenance_digest': source.provenance.digest}
            parents.append(source.provenance)
        populations = np.real(np.diag(projected))
        coherences = projected-np.diag(np.diag(projected))
        phase_valid = np.abs(coherences) > self.phase_tolerance
        phases = np.where(phase_valid, np.angle(coherences), 0.0)
        original_values = np.linalg.eigvalsh(density)
        output_values = np.linalg.eigvalsh(projected)
        eigenvalues = np.maximum(output_values, 0)
        nonzero = eigenvalues > 0
        purity = float(np.trace(projected@projected).real)
        ident = frame_id or f'{rho_feature.provenance.record_id}:basis:{basis.metadata.basis_id}'
        provenance = rho_feature.provenance.derive(
            ident, 'passive_basis_projection', VERSION,
            {'convention': CONVENTION, 'rho_feature': rho_feature.id.to_dict(),
             'operator_sources': operator_sources,
             'basis_provenance_digest': basis.provenance.digest,
             'phase_tolerance': self.phase_tolerance, 'phases': 'off_diagonal_radians_with_valid_mask'},
            parents=parents, basis=basis.metadata,
            source_path=f'analysis.basis.{basis.metadata.basis_id}.rho',
            normalization='unitary_similarity_no_state_renormalization')
        return BasisProjectionFrame(
            ident, basis, projected, ops, populations, coherences, phases, phase_valid,
            {'trace_error': abs(complex(np.trace(projected))-1),
             'purity': purity, 'purity_error': abs(purity-float(np.trace(density@density).real)),
             'entropy_nats': float(-np.sum(eigenvalues[nonzero]*np.log(eigenvalues[nonzero]))),
             'coherence_l1': float(np.sum(np.abs(coherences))),
             'roundtrip_error': float(np.linalg.norm(v@projected@v.conj().T-density)),
             'spectrum_error': float(np.max(np.abs(original_values-output_values))),
             'minimum_eigenvalue': float(output_values[0]),
             'basis_dependent': ('populations', 'coherences', 'phases', 'coherence_l1'),
             'phase_units': 'rad', 'operator_sources': operator_sources,
             'state_evolution': False}, provenance)

    def inverse(self, projected, basis):
        """Undo a square unitary coordinate change; this is not an evolution."""
        if not isinstance(basis, AnalysisBasis):
            raise TypeError('inverse requires AnalysisBasis; modal banks have no generic inverse')
        if isinstance(projected, FeatureValue):
            _same_coordinates(projected.provenance.basis, basis.metadata)
            projected = projected.require_available()
        a = _matrix(projected, 'projected matrix')
        if a.shape != basis.vectors.shape:
            raise ValueError('projected matrix dimension does not match basis')
        return frozen_array(basis.vectors@a@basis.vectors.conj().T)

    def project_modal(self, rho_feature, modes_feature, *, frame_id=None):
        """Observe C†rhoC and its Gram matrix for any declared finite mode bank.

        For nonorthogonal banks, its trace is an unnormalized response weight,
        not a probability. For orthonormal columns it is the probability mass
        captured by their span. Neither branch silently renormalizes rho.
        """
        if not isinstance(rho_feature, FeatureValue) or not isinstance(modes_feature, FeatureValue):
            raise TypeError('modal projection requires typed rho and mode-bank features')
        _same_coordinates(rho_feature.provenance.basis, modes_feature.provenance.basis)
        density = validate_density_matrix(rho_feature.require_available(), tolerance=self.tolerance)
        c = _matrix(modes_feature.require_available(), 'mode bank', square=False)
        if c.shape[0] != density.shape[0]:
            raise ValueError('mode bank rows must match the declared source dimension')
        gram = c.conj().T@c
        projected = c.conj().T@density@c
        weight = float(np.trace(projected).real)
        orthonormal = bool(np.allclose(gram, np.eye(c.shape[1]), atol=self.tolerance, rtol=0))
        metadata = BasisMetadata(
            f'modal:{modes_feature.id.path}', c.shape[1], 'modal_projection',
            rho_feature.provenance.basis.subsystem_order, 'declared_mode_index',
            'caller_declared_column_phases',
            {'source_dimension': c.shape[0], 'reference_basis': rho_feature.provenance.basis.to_dict(),
             'square_unitary_basis': False, 'orthonormal': orthonormal})
        ident = frame_id or f'{rho_feature.provenance.record_id}:modal:{modes_feature.provenance.record_id}'
        parents = (rho_feature.provenance, modes_feature.provenance)
        parameters = {'rho_feature': rho_feature.id.to_dict(), 'mode_bank_feature': modes_feature.id.to_dict(),
                      'convention': 'C_dagger rho C', 'orthonormal': orthonormal,
                      'automatic_density_normalization': False, 'metric': 'euclidean_inner_product'}
        outputs = []
        for path, quantity, kind, value, operation, units in (
            ('analysis.modal.matrix', 'modal_response_matrix', 'matrix', projected, 'modal_projection',
             f'{rho_feature.units}*({modes_feature.units})^2'),
            ('analysis.modal.gram', 'mode_bank_gram', 'matrix', gram, 'mode_bank_gram', f'({modes_feature.units})^2'),
            ('analysis.modal.captured_weight', 'captured_probability' if orthonormal else 'unnormalized_response_weight',
             'scalar', weight, 'modal_response_trace', f'{rho_feature.units}*({modes_feature.units})^2'),
        ):
            prov = rho_feature.provenance.derive(
                f'{ident}:{quantity}', operation, VERSION, parameters, units=units,
                normalization='none', basis=metadata, parents=parents, source_path=path)
            outputs.append(FeatureValue(FeatureId(path, quantity, kind), value, prov))
        return FeatureFrame(ident, tuple(outputs),
            {'orthonormal': orthonormal, 'trace_is_probability': orthonormal,
             'unprojected_probability': max(0., 1-weight) if orthonormal else None,
             'source_dimension': c.shape[0], 'mode_count': c.shape[1],
             'rank': int(np.linalg.matrix_rank(c)),
             'gram_identity_error': float(np.linalg.norm(gram-np.eye(c.shape[1]))),
             'automatic_inverse_available': False, 'density_matrix_claimed': False})


__all__ = ['BasisProjector']
