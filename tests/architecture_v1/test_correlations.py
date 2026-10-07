from dataclasses import replace
from itertools import product

import numpy as np
import pytest

from qmw.architecture_v1.contracts import BasisMetadata, ClockStamp, FeatureFrame, FeatureId, FeatureValue, Provenance
from qmw.architecture_v1.correlations import (
    correlations_from_rho, correlations_from_estimates, pair_tensor,
    multipartite_tensor, reconstruct_density_linear,
)


def origin(n, *, kind='computational', evidence='simulated'):
    return Provenance('sample:3', 'quantum.state.rho', 'declared_fixture', '1', {}, '1', 'none',
        BasisMetadata('computational', 2 ** n, kind, 'q0_lsb'),
        ClockStamp(.25, 's', 'simulation', 'elapsed', 'run:1'), 'numpy_fixture', evidence)


def density(rho):
    return FeatureValue(FeatureId('quantum.state.rho', 'density_matrix', 'matrix'),
                        rho, origin(int(np.log2(len(rho)))))


def ket_density(ket):
    return density(np.outer(ket, np.conj(ket)))


def axes(n):
    return {'axis_order': ('X', 'Y', 'Z'), 'pauli_label_order': 'q0_first',
            'hilbert_tensor_order': 'q(n-1)...q0', 'subsystem_labels': tuple(f'q{k}' for k in range(n)),
            'axis_frame': 'declared_lab_xyz'}


def estimate(label, value, *, se=None, missing=False):
    p = replace(origin(len(label), evidence='experimental_estimate'), source_path='experiment.' + label)
    uncertainty = None if se is None else {'kind': 'standard_error', 'standard_error': se}
    return FeatureValue(FeatureId('experiment.' + label, 'pauli_expectation'),
        None if missing else value, p, availability='missing' if missing else 'available',
        reason='observable not measured' if missing else None, uncertainty=uncertainty)


def corr(frame, label):
    return frame.get('correlation.pauli.' + label)


def test_bell_pair_tensor_and_complete_reconstruction():
    bell = np.array([1, 0, 0, 1]) / np.sqrt(2)
    source = ket_density(bell)
    frame = correlations_from_rho(source)
    assert len(frame.features) == 16
    tensor = pair_tensor(frame, 0, 1)
    assert np.allclose(tensor.value, np.diag([1, -1, 1]))
    assert np.allclose(pair_tensor(frame, 0, 1, connected=True).value, tensor.value)
    recovered = reconstruct_density_linear(frame)
    assert np.allclose(recovered.value, source.value)
    assert recovered.provenance.operation == 'complete_pauli_linear_reconstruction'
    assert recovered.provenance.parameters['psd_clipping'] is False
    assert len(recovered.provenance.parents) == 16
    assert frame.metadata['is_density_matrix'] is False


def test_product_correlations_do_not_imply_entanglement():
    frame = correlations_from_rho(ket_density([1, 0, 0, 0]))
    assert corr(frame, 'ZZ').value == 1
    assert np.array_equal(pair_tensor(frame, 0, 1).value, np.diag([0, 0, 1]))
    assert np.array_equal(pair_tensor(frame, 0, 1, connected=True).value, np.zeros((3, 3)))
    assert 'not an entanglement measure' in frame.metadata['interpretation']


def test_four_qubit_bit_order_and_ghz_multipartite_tensor():
    source = np.zeros(16)
    source[1] = 1
    frame = correlations_from_rho(ket_density(source))
    assert corr(frame, 'ZIII').value == -1
    assert corr(frame, 'IIIZ').value == 1
    assert frame.metadata['axes']['pauli_label_order'] == 'q0_first'
    assert frame.metadata['axes']['hilbert_tensor_order'] == 'q(n-1)...q0'
    ghz = np.zeros(16)
    ghz[[0, 15]] = 1 / np.sqrt(2)
    gf = correlations_from_rho(ket_density(ghz))
    tensor = multipartite_tensor(gf, (0, 1, 2, 3))
    assert tensor.value.shape == (3, 3, 3, 3)
    assert tensor.value[0, 0, 0, 0] == pytest.approx(1)
    assert tensor.value[1, 1, 0, 0] == pytest.approx(-1)
    assert tensor.value[2, 2, 2, 2] == pytest.approx(1)
    assert np.allclose(reconstruct_density_linear(gf).value, ket_density(ghz).value)


def test_nondefault_subsystem_axis_order_transposes_pair_tensor():
    psi = np.kron(np.array([1, 1]) / np.sqrt(2), np.array([1, 0]))
    frame = correlations_from_rho(ket_density(psi))
    t01 = pair_tensor(frame, 0, 1)
    t10 = pair_tensor(frame, 1, 0)
    assert t01.value[2, 0] == pytest.approx(1)
    assert np.allclose(t10.value, t01.value.T)
    assert t10.provenance.parameters['subsystems'] == (1, 0)


def test_subset_and_missing_estimates_stay_absent_and_cannot_reconstruct():
    frame = correlations_from_estimates(2, {'XX': estimate('XX', .4, se=.1),
        'ZZ': estimate('ZZ', None, missing=True)}, axes(2))
    assert len(frame.features) == 1
    assert corr(frame, 'XX').uncertainty['standard_error'] == .1
    assert frame.metadata['covariance'] is None
    assert frame.metadata['source_kind'] == 'ensemble_estimates'
    with pytest.raises(KeyError): corr(frame, 'ZZ')
    with pytest.raises(ValueError, match='missing'): pair_tensor(frame, 0, 1)
    with pytest.raises(ValueError, match='complete'): reconstruct_density_linear(frame)


def estimated_two_qubit_frame(*, with_covariance):
    labels = [''.join(x) for x in product('IXYZ', repeat=2)]
    vals = {label: estimate(label, 1. if label == 'II' else .1,
                           se=0. if label == 'II' else .05) for label in labels}
    C = np.eye(16) * .05 ** 2
    C[0, 0] = 0
    # Positively correlated marginal estimates; check full Jacobian propagation.
    C[labels.index('XI'), labels.index('IX')] = .0005
    C[labels.index('IX'), labels.index('XI')] = .0005
    cf = {'labels': labels, 'matrix': C} if with_covariance else None
    return correlations_from_estimates(2, vals, axes(2), covariance=cf), labels, C


def test_covariance_alignment_standard_errors_and_connected_delta_method():
    frame, labels, C = estimated_two_qubit_frame(with_covariance=True)
    tensor = pair_tensor(frame, 0, 1, connected=True)
    assert tensor.value[0, 0] == pytest.approx(.1 - .1 * .1)
    assert tensor.uncertainty['kind'] == 'first_order_delta_method'
    gradient = np.zeros(len(labels))
    gradient[labels.index('XX')] = 1
    gradient[labels.index('XI')] = -.1
    gradient[labels.index('IX')] = -.1
    assert tensor.uncertainty['covariance'][0, 0] == pytest.approx(gradient @ C @ gradient)
    assert tensor.uncertainty['standard_errors'][0] ** 2 == pytest.approx(gradient @ C @ gradient)
    parent_paths = {p.source_path for p in tensor.provenance.parents}
    assert {'correlation.pauli.XX', 'correlation.pauli.XI', 'correlation.pauli.IX'} <= parent_paths
    raw = pair_tensor(frame, 0, 1)
    assert raw.uncertainty['standard_errors'] == pytest.approx([.05] * 9)
    assert raw.uncertainty['covariance'].shape == (9, 9)


def test_connected_errors_without_covariance_remain_unknown():
    frame, _, _ = estimated_two_qubit_frame(with_covariance=False)
    tensor = pair_tensor(frame, 0, 1, connected=True)
    assert tensor.uncertainty['covariance'] is None
    assert tensor.uncertainty['standard_errors'] is None
    assert 'unknown' in tensor.uncertainty['reason']
    assert tensor.uncertainty['input_standard_errors']


def test_estimated_reconstruction_preserves_covariance_and_estimated_status():
    frame, labels, C = estimated_two_qubit_frame(with_covariance=True)
    rho = reconstruct_density_linear(frame)
    assert rho.provenance.evidence == 'reconstructed_estimate'
    assert rho.uncertainty['kind'] == 'linear_pauli_reconstruction'
    assert rho.uncertainty['coefficient_labels'] == tuple(labels)
    assert np.array_equal(rho.uncertainty['coefficient_covariance'], C)
    assert rho.provenance.parameters['minimum_eigenvalue'] > 0


@pytest.mark.parametrize('covariance', [
    {'labels': ['X', 'Z'], 'matrix': [[.01, .02], [.0, .01]]},
    {'labels': ['X', 'Z'], 'matrix': [[.01, .02], [.02, .01]]},
    {'labels': ['X', 'Z'], 'matrix': [[-.01, 0], [0, .01]]},
    {'labels': ['X', 'Z'], 'matrix': [[.02, 0], [0, .01]]},
    {'labels': ['X', 'Y'], 'matrix': [[.01, 0], [0, .01]]},
    {'labels': ['X', 'X'], 'matrix': [[.01, 0], [0, .01]]},
])
def test_covariance_must_align_be_symmetric_psd_and_match_standard_errors(covariance):
    with pytest.raises(ValueError):
        correlations_from_estimates(1, {'X': estimate('X', .2, se=.1), 'Z': estimate('Z', .3, se=.1)},
                                   axes(1), covariance=covariance)


def test_reconstruction_rejects_nonphysical_coefficients_without_clipping():
    frame = correlations_from_estimates(1, {label: estimate(label, 1.) for label in 'IXYZ'}, axes(1))
    with pytest.raises(ValueError, match='positive semidefinite'):
        reconstruct_density_linear(frame)


@pytest.mark.parametrize('label,value', [('Q', 0), ('XX', 0), ('x', 0), ('I', .9), ('X', 1.01), ('X', 1j)])
def test_invalid_labels_values_and_identity_are_rejected(label, value):
    with pytest.raises(ValueError):
        correlations_from_estimates(1, {label: estimate(label, value)}, axes(1))


def test_invalid_axes_basis_clock_and_density_are_rejected():
    wrong_axes = axes(1) | {'pauli_label_order': 'q0_last'}
    with pytest.raises(ValueError): correlations_from_estimates(1, {'X': estimate('X', .2)}, wrong_axes)
    with pytest.raises(ValueError): correlations_from_estimates(1, {'X': estimate('X', .2)}, {})
    z = estimate('Z', .3)
    z = replace(z, provenance=replace(z.provenance, clock=replace(z.provenance.clock, value=9)))
    with pytest.raises(ValueError): correlations_from_estimates(1, {'X': estimate('X', .2), 'Z': z}, axes(1))
    with pytest.raises(ValueError): correlations_from_rho(density(np.diag([1.1, -.1])))
    source = density(np.eye(2) / 2)
    with pytest.raises(ValueError):
        correlations_from_rho(replace(source, provenance=replace(source.provenance,
            basis=replace(source.provenance.basis, kind='qho'))))
    frame = correlations_from_rho(ket_density([1, 0, 0, 0]))
    with pytest.raises(ValueError): pair_tensor(frame, 0, 0)
    with pytest.raises(ValueError): multipartite_tensor(frame, (0, 9))
    with pytest.raises(ValueError): multipartite_tensor(frame, (True, 1))


def test_correlation_arrays_and_provenance_are_immutable():
    source = density(np.eye(4) / 4)
    frame = correlations_from_rho(source)
    tensor = pair_tensor(frame, 0, 1)
    assert all(f.provenance.parents == (source.provenance,) for f in frame.features)
    with pytest.raises(ValueError): tensor.value.setflags(write=True)
    with pytest.raises(TypeError): tensor.provenance.parameters['subsystems'] = (0, 9)


def test_declared_covariance_can_supply_missing_error_without_inventing_experiment():
    sample = estimate('X', .2)
    sample = replace(sample, provenance=replace(sample.provenance, evidence='monte_carlo_estimate'))
    frame = correlations_from_estimates(1, {'X': sample}, axes(1),
        covariance={'labels': ('X',), 'matrix': [[.04]]})
    feature = corr(frame, 'X')
    assert feature.uncertainty['standard_error'] == pytest.approx(.2)
    assert feature.provenance.evidence == 'derived_estimate'
    assert feature.provenance.parents[0].evidence == 'monte_carlo_estimate'


def test_post_ingestion_mixed_clock_dependencies_are_rejected():
    frame = correlations_from_rho(density(np.eye(4) / 4))
    xx = corr(frame, 'XX')
    changed = replace(xx, provenance=replace(xx.provenance, clock=replace(xx.provenance.clock, value=99)))
    altered = FeatureFrame(frame.frame_id, tuple(changed if f is xx else f for f in frame.features), frame.metadata)
    with pytest.raises(ValueError, match='clock'): pair_tensor(altered, 0, 1)
    with pytest.raises(ValueError, match='clock'): multipartite_tensor(altered, (0, 1))
    with pytest.raises(ValueError, match='clock'): reconstruct_density_linear(altered)
