"""Declared Pauli correlations, estimate uncertainty, and explicit reconstruction.

Logical labels list q0 FIRST; matrices use tensor order q(n-1) ... q0. The
existing representation laboratory owns Pauli operators and density validation.
Correlations are observable expectations, not automatic entanglement measures or
density matrices. Linear reconstruction is a separately requested operation.
"""
from __future__ import annotations

from collections.abc import Mapping
from itertools import product
import hashlib

import numpy as np

from qmw.qmw_representation_laboratory_v4.observables import pauli_matrix, pauli_expectation
from qmw.qmw_representation_laboratory_v4.core.state_transform import validate_density_matrix
from .contracts import FeatureFrame, FeatureId, FeatureValue


_AXES = ('X', 'Y', 'Z')
_TOLERANCE = 1e-10


def _n(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError('n_qubits must be a positive integer')
    return int(value)


def _label(value, n):
    if not isinstance(value, str) or len(value) != n or any(axis not in 'IXYZ' for axis in value):
        raise ValueError('Pauli labels must be uppercase I/X/Y/Z with q0 first and length n_qubits')
    return value


def _real(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f'{name} must be a finite real scalar')
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f'{name} must be a finite real scalar')
    return value


def _expectation(value, label):
    number = _real(value, label)
    if abs(number) > 1 + _TOLERANCE:
        raise ValueError(f'{label} must be a Pauli expectation within [-1, 1]')
    if set(label) == {'I'} and abs(number - 1) > _TOLERANCE:
        raise ValueError('identity Pauli expectation must equal one')
    return number


def _standard_error(feature):
    u = feature.uncertainty
    if u is None or 'standard_error' not in u:
        return None
    value = _real(u['standard_error'], 'standard_error')
    if value < 0:
        raise ValueError('standard_error must be nonnegative')
    return value


def _coordinates(feature, n):
    if not isinstance(feature, FeatureValue):
        raise TypeError('correlations require typed shared FeatureValue sources')
    basis = feature.provenance.basis
    if basis.dimension != 2 ** n or basis.subsystem_order != 'q0_lsb':
        raise ValueError('sources must declare matching qubit dimension and q0_lsb coordinates')
    if basis.kind != 'computational' and basis.details.get('qubit_tensor_product') is not True:
        raise ValueError('sources must declare computational qubit coordinates or an explicit qubit tensor product')
    if feature.units not in ('1', 'dimensionless'):
        raise ValueError('Pauli/density sources must be dimensionless')


def _axes(n, supplied=None, *, basis_id=None):
    if supplied is None:
        return dict(axis_order=_AXES, pauli_label_order='q0_first', hilbert_tensor_order='q(n-1)...q0',
                    subsystem_labels=tuple(f'q{k}' for k in range(n)), axis_frame=f'Pauli axes of {basis_id}')
    if not isinstance(supplied, Mapping):
        raise ValueError('axes_metadata must declare the Pauli and tensor conventions')
    result = dict(supplied)
    if (tuple(result.get('axis_order', ())) != _AXES
            or result.get('pauli_label_order') != 'q0_first'
            or result.get('hilbert_tensor_order') != 'q(n-1)...q0'):
        raise ValueError('axes require X/Y/Z order, q0_first labels and q(n-1)...q0 Hilbert tensor order')
    labels = tuple(result.get('subsystem_labels', ()))
    if (len(labels) != n or len(set(labels)) != n
            or any(not isinstance(x, str) or not x.strip() for x in labels)
            or not isinstance(result.get('axis_frame'), str) or not result['axis_frame'].strip()):
        raise ValueError('axes require distinct subsystem labels and a named axis_frame')
    result['axis_order'], result['subsystem_labels'] = _AXES, labels
    return result


def _metadata(n, axes, labels, source_kind, covariance=None, missing=None):
    return dict(n_qubits=n, dimension=2 ** n, axes=axes, available_labels=tuple(labels),
                source_kind=source_kind, covariance=covariance, missing_observables=missing or {},
                is_density_matrix=False,
                interpretation='Pauli observable correlations; not an entanglement measure and not a density matrix')


def _identifier(record_id, labels):
    signature = hashlib.sha256('|'.join(labels).encode()).hexdigest()[:12]
    return f'{record_id}:pauli_correlations:{signature}'


def correlations_from_rho(rho: FeatureValue, labels=None) -> FeatureFrame:
    """Observe existing rho in its declared qubit coordinates without mutation."""
    if not isinstance(rho, FeatureValue) or rho.id.quantity != 'density_matrix':
        raise ValueError('requires an available typed density_matrix source')
    matrix = validate_density_matrix(rho.require_available(), tolerance=_TOLERANCE)
    dim = len(matrix)
    if dim < 2 or dim & (dim - 1):
        raise ValueError('Pauli tensor analysis requires dimension 2**n for n>=1')
    n = dim.bit_length() - 1
    _coordinates(rho, n)
    chosen = tuple(''.join(x) for x in product('IXYZ', repeat=n)) if labels is None else tuple(labels)
    if not chosen or len(set(chosen)) != len(chosen):
        raise ValueError('labels must be a nonempty distinct sequence')
    for label in chosen:
        _label(label, n)
    axes = _axes(n, basis_id=rho.provenance.basis.basis_id)
    identifier = _identifier(rho.provenance.record_id, chosen)
    features = []
    for label in chosen:
        value = _expectation(pauli_expectation(matrix, label), label)
        path = 'correlation.pauli.' + label
        p = rho.provenance.derive(identifier + ':' + label, 'qmw.qmw_representation_laboratory_v4.pauli_expectation',
            parameters={'label': label, 'formula': 'real(Tr(rho P_label))', 'axes': axes,
                        'state_evolution': False}, units='1', normalization='none', source_path=path)
        uncertainty = None if rho.uncertainty is None else {
            'kind': 'unpropagated_state_uncertainty', 'source_uncertainty': rho.uncertainty,
            'reason': 'density uncertainty needs a declared matrix-entry covariance transform'}
        features.append(FeatureValue(FeatureId(path, 'pauli_expectation'), value, p, uncertainty=uncertainty))
    return FeatureFrame(identifier, tuple(features), _metadata(n, axes, chosen, 'density_observer'))


def _validated_covariance(covariance, estimates):
    if covariance is None:
        return None
    if not isinstance(covariance, Mapping) or 'labels' not in covariance or 'matrix' not in covariance:
        raise ValueError('covariance requires explicit ordered labels and matrix')
    labels = tuple(covariance['labels'])
    if len(labels) != len(set(labels)) or set(labels) != set(estimates):
        raise ValueError('covariance labels must match every available estimate exactly once')
    raw = np.asarray(covariance['matrix'])
    if np.iscomplexobj(raw):
        raise ValueError('estimate covariance must be real')
    matrix = np.asarray(raw, dtype=float)
    if matrix.shape != (len(labels), len(labels)) or not np.all(np.isfinite(matrix)):
        raise ValueError('covariance shape/finiteness must match labels')
    if not len(labels):
        raise ValueError('empty covariance has no available estimates')
    scale = max(float(np.max(np.abs(matrix))), np.finfo(float).tiny)
    if np.max(np.abs(matrix - matrix.T)) > _TOLERANCE * scale:
        raise ValueError('covariance must be symmetric')
    if np.any(np.diag(matrix) < 0) or np.linalg.eigvalsh(matrix).min() < -_TOLERANCE * scale:
        raise ValueError('covariance must be positive semidefinite')
    for k, label in enumerate(labels):
        error = _standard_error(estimates[label])
        if error is not None:
            expected = error ** 2
            if abs(matrix[k, k] - expected) > _TOLERANCE * max(expected, abs(matrix[k, k]), np.finfo(float).tiny):
                raise ValueError('covariance diagonal must match supplied standard errors squared')
        if set(label) == {'I'} and matrix[k, k] != 0:
            raise ValueError('the identity observable is fixed and requires zero covariance variance')
    return dict(labels=labels, matrix=matrix)


def correlations_from_estimates(n_qubits, estimates, axes_metadata, covariance=None) -> FeatureFrame:
    """Ingest ensemble expectation estimates; absent observables remain absent.

    Covariance uses ``{'labels': ordered_labels, 'matrix': C}``, with exact label
    coverage of available inputs. Unknown cross-covariance stays None even when
    individual standard errors are supplied. No independence is inferred.
    """
    n = _n(n_qubits)
    axes = _axes(n, axes_metadata)
    if not isinstance(estimates, Mapping) or not estimates:
        raise ValueError('estimates must be a nonempty mapping of labels to typed features')
    available, missing = {}, {}
    first = None
    for label, feature in estimates.items():
        _label(label, n)
        _coordinates(feature, n)
        if feature.id.kind != 'scalar' or feature.id.quantity not in ('pauli_expectation', 'correlation_estimate', 'expectation_value'):
            raise ValueError('estimate features must carry scalar Pauli expectation quantities')
        p = feature.provenance
        if first is None:
            first = p
        elif first.basis.to_dict() != p.basis.to_dict() or first.clock != p.clock:
            raise ValueError('ensemble estimates require identical declared basis and acquisition clock')
        error = _standard_error(feature)
        if set(label) == {'I'} and error is not None and error != 0:
            raise ValueError('identity Pauli observable has zero standard error')
        if feature.availability != 'available':
            missing[label] = dict(availability=feature.availability, reason=feature.reason,
                                  source_provenance=p.to_dict())
            continue
        _expectation(feature.require_available(), label)
        available[label] = feature
    labels = tuple(sorted(available, key=lambda x: tuple('IXYZ'.index(c) for c in x)))
    cov = _validated_covariance(covariance, available)
    identifier = _identifier(first.record_id, labels)
    cov_p = None
    if cov is not None:
        cov_p = first.derive(identifier + ':covariance', 'declared_ensemble_estimate_covariance',
            parameters={'covariance': cov, 'axes': axes, 'origin': 'caller_supplied; not computed from expectation means'},
            units='1', normalization='none', parents=tuple(f.provenance for f in available.values()),
            source_path='correlation.estimate_covariance')
    features = []
    for label in labels:
        source = available[label]
        path = 'correlation.pauli.' + label
        parents = (source.provenance,) if cov_p is None else (source.provenance, cov_p)
        p = source.provenance.derive(identifier + ':' + label, 'declared_pauli_estimate_ingestion',
            parameters={'label': label, 'axes': axes, 'level': 'ensemble_estimate',
                        'source_uncertainty': source.uncertainty}, units='1', normalization='none',
            parents=parents, source_path=path, evidence='derived_estimate')
        uncertainty = source.uncertainty
        if cov is not None and _standard_error(source) is None:
            k = cov['labels'].index(label)
            uncertainty = {'kind': 'standard_error_from_declared_covariance',
                           'standard_error': float(np.sqrt(cov['matrix'][k, k])),
                           'source_uncertainty': source.uncertainty}
        features.append(FeatureValue(FeatureId(path, 'pauli_expectation'), source.value, p, uncertainty=uncertainty))
    return FeatureFrame(identifier, tuple(features), _metadata(n, axes, labels, 'ensemble_estimates', cov, missing))


def _frame(frame):
    if not isinstance(frame, FeatureFrame):
        raise TypeError('requires a shared correlation FeatureFrame')
    n = _n(frame.metadata.get('n_qubits'))
    _axes(n, frame.metadata.get('axes'))
    if frame.metadata.get('source_kind') not in ('density_observer', 'ensemble_estimates'):
        raise ValueError('correlation frame must declare its source kind')
    return n


def _subsystems(frame, subsystems):
    n = _frame(frame)
    subsystems = tuple(subsystems)
    if not subsystems or any(isinstance(s, (bool, np.bool_)) or not isinstance(s, (int, np.integer))
                            or not 0 <= s < n for s in subsystems) or len(set(subsystems)) != len(subsystems):
        raise ValueError('subsystems must be distinct in-range integer qubit indices')
    return n, tuple(int(s) for s in subsystems)


def _get(frame, label):
    try:
        feature = frame.get('correlation.pauli.' + label)
    except KeyError as exc:
        raise ValueError(f'missing observable {label}; no imputation is performed') from exc
    _coordinates(feature, frame.metadata['n_qubits'])
    if feature.id != FeatureId('correlation.pauli.' + label, 'pauli_expectation'):
        raise ValueError('correlation feature has incompatible quantity/type')
    if feature.provenance.parameters.get('label') != label:
        raise ValueError('correlation label and source provenance disagree')
    _expectation(feature.require_available(), label)
    return feature


def _consistent_sources(features):
    first = features[0].provenance
    for feature in features[1:]:
        p = feature.provenance
        if first.basis.to_dict() != p.basis.to_dict() or first.clock != p.clock:
            raise ValueError('tensor/reconstruction dependencies must share basis and clock')


def _tensor_labels(n, subsystems):
    result = []
    for axes in product(_AXES, repeat=len(subsystems)):
        label = ['I'] * n
        for subsystem, axis in zip(subsystems, axes):
            label[subsystem] = axis
        result.append(''.join(label))
    return tuple(result)


def _raw_uncertainty(frame, labels, features):
    if frame.metadata['source_kind'] != 'ensemble_estimates' and all(f.uncertainty is None for f in features):
        return None
    covariance = frame.metadata['covariance']
    C = None
    if covariance is not None:
        indices = [covariance['labels'].index(label) for label in labels]
        C = covariance['matrix'][np.ix_(indices, indices)]
    return dict(kind='correlation_tensor_estimate', flattened_label_order=labels,
                standard_errors=tuple(_standard_error(f) for f in features), covariance=C,
                covariance_status='known' if C is not None else 'unknown',
                source_uncertainties=tuple(f.uncertainty for f in features))


def multipartite_tensor(frame: FeatureFrame, subsystems) -> FeatureValue:
    """Tensor of full products of X/Y/Z on exactly the requested ordered qubits."""
    n, subsystems = _subsystems(frame, subsystems)
    labels = _tensor_labels(n, subsystems)
    features = tuple(_get(frame, label) for label in labels)
    _consistent_sources(features)
    shape = (3,) * len(subsystems)
    values = np.array([f.value for f in features]).reshape(shape)
    suffix = '_'.join(f'q{s}' for s in subsystems)
    path = 'correlation.multipartite.' + suffix
    p = features[0].provenance.derive(frame.frame_id + ':' + suffix, 'ordered_pauli_correlation_tensor',
        parameters={'subsystems': subsystems, 'axes': frame.metadata['axes'], 'flattened_label_order': labels,
                    'shape': shape, 'is_entanglement_measure': False}, units='1', normalization='none',
        parents=tuple(f.provenance for f in features), source_path=path)
    return FeatureValue(FeatureId(path, 'pauli_correlation_tensor', 'tensor'), values, p,
                        uncertainty=_raw_uncertainty(frame, labels, features))


def pair_tensor(frame: FeatureFrame, a, b, connected=False) -> FeatureValue:
    """T_ij=<sigma_i(a)sigma_j(b)> or C_ij=T_ij-<sigma_i(a)><sigma_j(b)>.

    Estimate covariance for C uses an explicitly labeled first-order delta
    method. Without joint covariance, connected standard errors remain unknown.
    Ordinary connected correlations are not an entanglement classification.
    """
    if not isinstance(connected, bool):
        raise ValueError('connected must be boolean')
    n, subsystems = _subsystems(frame, (a, b))
    joint_labels = _tensor_labels(n, subsystems)
    joint = tuple(_get(frame, label) for label in joint_labels)
    values = np.array([f.value for f in joint]).reshape(3, 3)
    labels, features = joint_labels, joint
    uncertainty = _raw_uncertainty(frame, labels, features)
    if connected:
        left_labels = _tensor_labels(n, (a,))
        right_labels = _tensor_labels(n, (b,))
        left = tuple(_get(frame, label) for label in left_labels)
        right = tuple(_get(frame, label) for label in right_labels)
        lv, rv = np.array([f.value for f in left]), np.array([f.value for f in right])
        values = values - np.outer(lv, rv)
        labels, features = joint_labels + left_labels + right_labels, joint + left + right
        if frame.metadata['source_kind'] == 'ensemble_estimates' or any(f.uncertainty is not None for f in features):
            cov = frame.metadata['covariance']
            if cov is None:
                uncertainty = dict(kind='connected_uncertainty_unavailable', covariance=None, standard_errors=None,
                    reason='joint estimate covariance is unknown; marginal standard errors do not justify independence',
                    input_standard_errors={label: _standard_error(f) for label, f in zip(labels, features)})
            else:
                J = np.zeros((9, len(cov['labels'])))
                for i in range(3):
                    for j in range(3):
                        row = 3 * i + j
                        J[row, cov['labels'].index(joint_labels[row])] += 1
                        J[row, cov['labels'].index(left_labels[i])] -= rv[j]
                        J[row, cov['labels'].index(right_labels[j])] -= lv[i]
                C = J @ cov['matrix'] @ J.T
                uncertainty = dict(kind='first_order_delta_method', covariance=C,
                    standard_errors=np.sqrt(np.maximum(np.diag(C), 0)), jacobian=J,
                    input_covariance_labels=cov['labels'], flattened_label_order=joint_labels,
                    approximation='first-order propagation; nonlinear-product bias and higher moments omitted',
                    variance_roundoff_policy='negative diagonal roundoff floored at zero only for square roots')
        else:
            uncertainty = None
    _consistent_sources(features)
    path = f'correlation.pair.q{a}_q{b}' + ('.connected' if connected else '')
    p = joint[0].provenance.derive(frame.frame_id + ':' + path,
        'connected_pauli_correlation_tensor' if connected else 'pairwise_pauli_correlation_tensor',
        parameters={'subsystems': subsystems, 'axes': frame.metadata['axes'], 'flattened_joint_labels': joint_labels,
                    'all_dependency_labels': labels, 'formula': 'T_ij-r_i*s_j' if connected else 'T_ij',
                    'is_entanglement_measure': False,
                    'uncertainty_method': uncertainty['kind'] if uncertainty else 'no estimator uncertainty supplied'},
        units='1', normalization='none', parents=tuple(f.provenance for f in features), source_path=path)
    return FeatureValue(FeatureId(path, 'connected_pauli_correlations' if connected else 'pauli_correlation_tensor', 'matrix'),
                        values, p, uncertainty=uncertainty)


def reconstruct_density_linear(frame: FeatureFrame) -> FeatureValue:
    """Explicit rho=(1/2**n) sum_P <P>P; complete input and physical result required.

    Validation preserves raw reconstruction within the declared floating-point
    tolerance. It never clips eigenvalues, repairs trace, or performs maximum-
    likelihood tomography. Estimated coefficients yield an estimated state only.
    """
    n = _frame(frame)
    labels = tuple(''.join(x) for x in product('IXYZ', repeat=n))
    present = set(frame.metadata['available_labels'])
    if present != set(labels):
        raise ValueError('linear reconstruction requires the complete 4**n Pauli set including identity')
    features = tuple(_get(frame, label) for label in labels)
    _consistent_sources(features)
    dim = 2 ** n
    matrix = sum(float(f.value) * pauli_matrix(label) for label, f in zip(labels, features)) / dim
    # This is the existing strict source validator, with no positivity repair.
    validate_density_matrix(matrix, tolerance=_TOLERANCE)
    eigenvalues = np.linalg.eigvalsh(matrix)
    estimated = frame.metadata['source_kind'] == 'ensemble_estimates'
    cov = frame.metadata['covariance']
    uncertainty = None
    if estimated or any(f.uncertainty is not None for f in features):
        C = None
        if cov is not None:
            indices = [cov['labels'].index(label) for label in labels]
            C = cov['matrix'][np.ix_(indices, indices)]
        uncertainty = dict(kind='linear_pauli_reconstruction', coefficient_labels=labels,
            coefficient_covariance=C, coefficient_standard_errors=tuple(_standard_error(f) for f in features),
            linear_map='rho=(1/d)*sum_j coefficient_j*P_j; P_j uses declared q0-first labels',
            matrix_entry_covariance=None,
            interpretation='coefficient covariance retained exactly; no confidence region or physicality repair inferred')
    path = 'quantum.state.reconstructed_rho'
    p = features[0].provenance.derive(frame.frame_id + ':linear_reconstruction', 'complete_pauli_linear_reconstruction',
        parameters={'formula': 'rho=(1/d)*sum_P expectation(P)*P', 'dimension': dim,
                    'labels': labels, 'axes': frame.metadata['axes'], 'identity_required': True,
                    'minimum_eigenvalue': float(eigenvalues.min()),
                    'trace_error': float(abs(np.trace(matrix) - 1)),
                    'hermiticity_residual': float(np.linalg.norm(matrix - matrix.conj().T)),
                    'validation_tolerance': _TOLERANCE, 'psd_clipping': False,
                    'source_kind': frame.metadata['source_kind'], 'state_authority': 'reconstructed_observer'},
        units='1', normalization='linear_pauli_identity_coefficient',
        parents=tuple(f.provenance for f in features), source_path=path,
        evidence='reconstructed_estimate' if estimated else 'derived')
    return FeatureValue(FeatureId(path, 'density_matrix', 'matrix'), matrix, p, uncertainty=uncertainty)
