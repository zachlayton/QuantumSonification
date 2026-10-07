"""Order analysis consumes the actual engine and canonical oscillator operators."""
from dataclasses import replace

import numpy as np
import pytest

from qmw.architecture_v1.adapters import operator_feature, state_features, transition_features
from qmw.architecture_v1.contracts import FeatureFrame
from qmw.architecture_v1.transition_order import TransitionOrderAnalyzer, order_fourier
from qmw.core.state_frame import QuantumStateFrame
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
from qmw.qho.model import OscillatorSpec
from qmw.qho.operators import oscillator_operators


def make_frame(H, A, rho=None, *, units=None, diagonal=False, zero_gap=False):
    dim = len(H)
    rho = np.eye(dim) / dim if rho is None else rho
    units = units or QuantumUnits()
    context = FrameContext('order-fixture', 7, .25, .01, 'q0-lsb', units.time_unit)
    state = QuantumStateFrame(context.time, context.dt, rho, H, context.source_id)
    sources = state_features(state, context, units)
    engine = TransitionEngine(units=units, include_diagonal=diagonal,
                              include_zero_gap=zero_gap, gap_tolerance=0)
    frame = engine.process(H, A, rho, context)
    adapted = transition_features(frame, sources.get('quantum.state.rho'),
                                  sources.get('quantum.state.hamiltonian'),
                                  operator_feature(A, context, units))
    return frame, adapted


def values(frame, path):
    return frame.get('transition_order.' + path).value


def test_one_qubit_x_and_z_selection_structure_retains_zero_edges():
    H = np.diag([-.5, .5])
    x, xf = make_frame(H, np.array([[0, 1], [1, 0]]), diagonal=True, zero_gap=True)
    z, zf = make_frame(H, np.diag([1, -1]), diagonal=True, zero_gap=True)
    xo = TransitionOrderAnalyzer().process(x, xf)
    zo = TransitionOrderAnalyzer().process(z, zf)
    assert np.array_equal(values(xo, 'signed.axis'), [-1, 0, 1])
    assert np.array_equal(values(xo, 'signed.raw'), [1, 0, 1])
    assert np.array_equal(values(zo, 'signed.raw'), [0, 2, 0])
    assert len(values(xo, 'edges')) == len(x.edges) == 4
    assert {r['edge_id'] for r in values(xo, 'edges')} == {
        'order-fixture:7:0->0', 'order-fixture:7:0->1',
        'order-fixture:7:1->0', 'order-fixture:7:1->1'}


@pytest.mark.parametrize('weight', ['magnitude', 'matrix_element_squared',
                                   'population_weighted_matrix_element'])
def test_sixteen_state_qho_orders_signed_energy_relation_and_conservation(weight):
    spec = OscillatorSpec(dimension=16, omega=2.75, hbar=.8)
    ops = oscillator_operators(spec)
    A = ops.x + .2 * (ops.annihilation @ ops.annihilation + ops.creation @ ops.creation)
    rho = np.diag(np.arange(1, 17) / 136)
    units = QuantumUnits(hbar=spec.hbar, operator_unit='model_position')
    frame, sources = make_frame(ops.hamiltonian, A, rho, units=units,
                                diagonal=True, zero_gap=True)
    result = TransitionOrderAnalyzer(weight=weight, normalization='sum').process(frame, sources)
    rows = values(result, 'edges')
    assert len(rows) == 256
    for edge, row in zip(frame.edges, rows):
        assert row['source_n'] == edge.source
        assert row['target_m'] == edge.target
        assert row['signed_order'] == edge.target - edge.source
        assert row['absolute_order'] == abs(edge.target - edge.source)
        assert row['omega'] == pytest.approx(row['signed_order'] * spec.omega, abs=1e-12)
        assert row['delta_E'] / spec.hbar == pytest.approx(row['omega'])
        assert row['A_mn'] == edge.A_mn
        assert dict(row['activity']) == dict(edge.activity)
    active = {row['signed_order'] for row in rows if row['weight'] > 1e-12}
    assert active == {-2, -1, 1, 2}
    assert values(result, 'signed.raw').sum() == pytest.approx(sum(row['weight'] for row in rows))
    assert values(result, 'absolute.raw').sum() == pytest.approx(values(result, 'signed.raw').sum())
    assert values(result, 'signed.weights').sum() == pytest.approx(1)
    assert values(result, 'absolute.weights').sum() == pytest.approx(1)
    assert result.metadata['energy_difference_convention'] == 'E_m-E_n'
    assert result.metadata['angular_frequency_unit'] == 'rad/s'
    assert 'not a physical transition rate' in result.metadata['weight_interpretation']


def test_actual_four_qubit_ghz_frame_retains_endpoint_orders():
    # q0 is the rightmost/least-significant displayed bit, as in QMW adapters.
    x = np.array([[0., 1.], [1., 0.]])
    number_qubit = np.diag([0., 1.])
    H = sum((2 ** q) * np.kron(np.eye(2 ** (3 - q)),
                np.kron(number_qubit, np.eye(2 ** q))) for q in range(4))
    A = np.kron(np.eye(8), x) + .2 * np.kron(np.eye(4), np.kron(x, np.eye(2)))
    ghz = np.zeros(16, dtype=complex)
    ghz[[0, 15]] = 1 / np.sqrt(2)
    rho = np.outer(ghz, ghz.conj())
    before = rho.copy()
    frame, sources = make_frame(H, A, rho)
    result = TransitionOrderAnalyzer(weight='population_weighted_matrix_element',
                                     normalization='sum').process(frame, sources)
    nonzero = [r for r in values(result, 'edges') if r['weight'] > 0]
    assert {(r['source_n'], r['target_m']) for r in nonzero} == {(0, 1), (0, 2), (15, 14), (15, 13)}
    assert {r['signed_order'] for r in nonzero} == {-2, -1, 1, 2}
    assert len(values(result, 'edges')) == 240
    assert np.array_equal(rho, before)


def test_si_scale_gap_checks_use_relative_tolerance_without_unit_floor():
    units = QuantumUnits(hbar=1.054571817e-34, energy_unit='J')
    frame, sources = make_frame(np.diag([0., 1e-25]), np.ones((2, 2)), units=units)
    result = TransitionOrderAnalyzer().process(frame, sources)
    assert values(result, 'edges')[0]['energy_unit'] == 'J'
    edge = replace(frame.edges[0], delta_E=2e-25)
    with pytest.raises(ValueError, match='delta_E'):
        TransitionOrderAnalyzer().process(replace(frame, edges=(edge,) + frame.edges[1:]), sources)


def test_zero_weights_stay_zero_and_nonzero_origin_does_not_change_order():
    frame, sources = make_frame(np.diag([0., 1., 2.]), np.zeros((3, 3)))
    result = TransitionOrderAnalyzer(normalization='sum', sequence_origin=1).process(frame, sources)
    assert np.array_equal(values(result, 'signed.weights'), np.zeros(5))
    assert np.array_equal(values(result, 'absolute.weights'), np.zeros(3))
    assert result.metadata['normalization_denominator'] == 0
    assert result.metadata['sequence_origin'] == 1
    assert values(result, 'edges')[0]['source_label'] == frame.edges[0].source + 1
    assert values(result, 'edges')[0]['signed_order'] == frame.edges[0].target - frame.edges[0].source


def test_degeneracy_and_frame_local_ordering_are_explicit():
    frame, sources = make_frame(np.diag([0., 0., 1.]), np.ones((3, 3)), zero_gap=True)
    result = TransitionOrderAnalyzer().process(frame, sources)
    assert result.metadata['energy_degenerate_groups'] == ((0, 1),)
    assert result.metadata['ordering'] == frame.label_convention
    assert 'degenerate' in result.metadata['ordering_limit']
    assert any(row['basis_dependent_degenerate_endpoint'] for row in values(result, 'edges'))


@pytest.mark.parametrize('order', ['signed', 'absolute'])
@pytest.mark.parametrize('normalization', ['backward', 'forward', 'ortho'])
def test_explicit_order_fourier_is_reversible_and_not_time_frequency(order, normalization):
    frame, sources = make_frame(np.diag([0., 1., 3., 7.]), np.ones((4, 4)))
    result = TransitionOrderAnalyzer(normalization='sum').process(frame, sources)
    fourier = order_fourier(result, order=order, normalization=normalization)
    coefficients = fourier.get('transition_order.fourier.coefficients')
    recovered = np.fft.ifft(coefficients.value, norm=normalization)
    assert np.allclose(recovered, values(result, order + '.weights'))
    frequency = fourier.get('transition_order.fourier.index_frequency')
    assert frequency.units == 'cycles/order_index'
    assert fourier.metadata['input_axis_origin'] == values(result, order + '.axis')[0]
    assert coefficients.provenance.operation == 'numpy.fft.fft_order_distribution'
    assert coefficients.provenance.parents[0] == result.get('transition_order.' + order + '.weights').provenance
    assert 'not a temporal frequency' in fourier.metadata['interpretation']


def test_all_derived_features_have_full_source_chains_and_are_immutable():
    frame, sources = make_frame(np.diag([0., 1.]), np.ones((2, 2)))
    result = TransitionOrderAnalyzer(weight='population_weighted_matrix_element').process(frame, sources)

    def roots(p):
        return {p.source_path} if not p.parents else set().union(*(roots(q) for q in p.parents))

    for feature in result.features:
        assert feature.provenance.parents
        assert feature.provenance.clock.value == frame.context.time
        assert feature.provenance.basis.kind == 'hamiltonian'
    assert roots(result.get('transition_order.signed.raw').provenance) == {
        'quantum.state.rho', 'quantum.state.hamiltonian', 'quantum.operator.A'}
    with pytest.raises(TypeError):
        values(result, 'edges')[0]['signed_order'] = 99
    with pytest.raises(ValueError):
        values(result, 'signed.raw').setflags(write=True)


@pytest.mark.parametrize('change', [
    {'source': 9}, {'source': True}, {'delta_E': 123.}, {'omega': 123.},
    {'magnitude': -1.}, {'magnitude': float('nan')},
    {'activity': {'matrix_element_squared': -1., 'population_weighted_matrix_element': .5}},
])
def test_invalid_actual_edge_contracts_are_rejected(change):
    frame, sources = make_frame(np.diag([0., 1.]), np.ones((2, 2)))
    bad = replace(frame, edges=(replace(frame.edges[0], **change),) + frame.edges[1:])
    with pytest.raises(ValueError):
        TransitionOrderAnalyzer().process(bad, sources)


def test_missing_stale_duplicate_or_unavailable_source_evidence_rejected():
    frame, sources = make_frame(np.diag([0., 1.]), np.ones((2, 2)))
    magnitude = sources.get('transition.n0.m1.matrix_element_magnitude')
    for replacement in [replace(magnitude, value=2.),
                        replace(magnitude, value=None, availability='missing', reason='not measured'),
                        replace(magnitude, provenance=replace(magnitude.provenance,
                            clock=replace(magnitude.provenance.clock, value=9.)))]:
        modified = FeatureFrame(sources.frame_id, tuple(replacement if f is magnitude else f for f in sources.features))
        with pytest.raises(ValueError):
            TransitionOrderAnalyzer().process(frame, modified)
    with pytest.raises(ValueError, match='missing'):
        TransitionOrderAnalyzer().process(frame, FeatureFrame('missing', ()))
    with pytest.raises(ValueError, match='duplicate'):
        TransitionOrderAnalyzer().process(replace(frame, edges=frame.edges + (frame.edges[0],)), sources)


def test_unsupported_policies_and_no_edges_fail_explicitly_without_inventing_provenance():
    with pytest.raises(ValueError): TransitionOrderAnalyzer(weight='universal_rate')
    with pytest.raises(ValueError): TransitionOrderAnalyzer(normalization='probability')
    with pytest.raises(ValueError): TransitionOrderAnalyzer(sequence_origin=True)
    frame, sources = make_frame(np.eye(2), np.ones((2, 2)))
    with pytest.raises(ValueError, match='empty'):
        TransitionOrderAnalyzer().process(frame, sources)
    frame, sources = make_frame(np.diag([0., 1.]), np.ones((2, 2)))
    result = TransitionOrderAnalyzer().process(frame, sources)
    with pytest.raises(ValueError): order_fourier(result, order='time')
    with pytest.raises(ValueError): order_fourier(result, normalization='auto')
