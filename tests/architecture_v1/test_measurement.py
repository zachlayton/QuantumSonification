import math

import numpy as np
import pytest

from qmw.architecture_v1.contracts import BasisMetadata, ClockStamp, FeatureId, FeatureValue, Provenance
from qmw.architecture_v1.measurement import MeasurementEngine
from density.measurement_instrument_v1 import ProjectiveMeasurementInstrument


def feature(value, quantity='density_matrix', *, name='state.rho', dimension=None, basis=None,
            clock=None, backend='numpy', evidence='simulated', kind=None):
    if dimension is None:
        dimension = np.shape(value)[0] if isinstance(value, np.ndarray) else 2
    basis = basis or BasisMetadata('computational', dimension, 'computational', 'q0_lsb')
    clock = clock or ClockStamp(2.5, 's', 'simulation', 'elapsed', 'run:1')
    provenance = Provenance('frame:' + name, name, 'source_capture', '1', {}, '1', 'none',
                            basis, clock, backend, evidence)
    return FeatureValue(FeatureId(name, quantity, kind or ('record' if isinstance(value, dict) else 'matrix')),
                        value, provenance)


def ghz():
    ket = np.zeros(16, complex)
    ket[[0, 15]] = 1 / math.sqrt(2)
    return np.outer(ket, ket.conj())


def z_instrument(*, flip=False):
    zero, one = np.diag([1., 0.]), np.diag([0., 1.])
    x = np.array([[0., 1.], [1., 0.]])
    return feature({'0': (x @ zero if flip else zero,), '1': (x @ one if flip else one,)},
                   'kraus_instrument', name='measurement.kraus')


def z_effects():
    return feature({'0': np.diag([1., 0.]), '1': np.diag([0., 1.])},
                   'povm_effects', name='measurement.effects')


@pytest.mark.parametrize('basis', ['X', 'Y', 'Z'])
def test_actual_four_qubit_projective_instrument_is_called_without_installation(basis):
    rho = feature(ghz())
    raw = rho.value.copy()
    engine = MeasurementEngine(seed=8)
    assert isinstance(engine.projective_instrument, ProjectiveMeasurementInstrument)
    record = engine.projective(rho, 'measurement:1', basis=basis, mode='collapse', revision_before=17, request_id=91)
    assert engine.projective_instrument.event_count == 1
    assert record.origin == 'simulated_sample' and record.kind == 'projective'
    assert record.clock == rho.provenance.clock
    assert record.metadata['native_instrument'] == 'density.measurement_instrument_v1.ProjectiveMeasurementInstrument'
    assert record.metadata['state_installation'] == 'caller_authority_only'
    assert record.metadata['source_revision_before'] == 17
    assert record.metadata['authority_state_mutated'] is False
    np.testing.assert_array_equal(rho.value, raw)
    np.testing.assert_allclose(record.pre_state, raw, atol=1e-12)
    assert np.trace(record.post_state) == pytest.approx(1.)
    np.testing.assert_allclose(record.post_state @ record.post_state, record.post_state, atol=1e-12)
    for state in (record.pre_state, record.post_state):
        assert not state.flags.writeable
        with pytest.raises(ValueError):
            state.setflags(write=True)


def test_projective_probe_is_sampling_without_post_measurement_state():
    rho = feature(ghz())
    record = MeasurementEngine(seed=3).projective(rho, 'probe', basis='Z', mode='probe')
    assert record.post_state is None
    assert record.pre_state is not None
    assert record.metadata['post_state_availability'] == 'not_computed_for_probe'
    assert record.probability == pytest.approx(.5)


def test_projective_y_convention_on_plus_y_product_state():
    plus_y = np.array([1., 1j]) / math.sqrt(2.)
    ket = plus_y
    for _ in range(3):
        ket = np.kron(ket, plus_y)
    rho = feature(np.outer(ket, ket.conj()))
    record = MeasurementEngine(seed=19).projective(rho, 'y', basis='Y')
    assert record.outcome == 0 and record.probability == pytest.approx(1.)
    assert record.basis.subsystem_order == 'q0_lsb'
    assert record.metadata['bitstring_order'] == 'q3_q2_q1_q0'


@pytest.mark.parametrize('bad', [np.eye(16), np.diag([-0.1, 1.1] + [0.] * 14),
    np.eye(16) / 16 + 0.1j * np.eye(16), np.ones((16, 16)) / 16 + np.diag([1j] + [0j] * 15)])
def test_invalid_rho_rejected_before_native_repair_or_rng_use(bad):
    rho = feature(bad)
    engine = MeasurementEngine(seed=7)
    state = engine.projective_instrument.rng.bit_generator.state
    with pytest.raises(ValueError):
        engine.projective(rho, 'invalid')
    assert engine.projective_instrument.event_count == 0
    assert engine.projective_instrument.rng.bit_generator.state == state


def test_native_dimension_basis_and_unavailable_source_rejection():
    engine = MeasurementEngine()
    with pytest.raises(ValueError):
        engine.projective(feature(np.eye(2) / 2), 'wrongdimension')
    raw = feature(ghz())
    with pytest.raises(ValueError):
        engine.projective(raw, 'wrongaxis', basis='W')
    with pytest.raises(ValueError):
        engine.projective(feature(ghz(), basis=BasisMetadata('energy', 16, 'hamiltonian')), 'wrongcoords')
    missing = FeatureValue(raw.id, None, raw.provenance, 'missing', 'not available from hardware')
    with pytest.raises(ValueError, match='not available from hardware'):
        engine.projective(missing, 'missing')


def test_projective_and_general_sampling_are_seed_reproducible():
    one, two = MeasurementEngine(seed=29), MeasurementEngine(seed=29)
    rho = feature(ghz())
    samples_one = [one.projective(rho, f'm:{i}').outcome for i in range(20)]
    samples_two = [two.projective(rho, f'm:{i}').outcome for i in range(20)]
    assert samples_one == samples_two
    rho2 = feature(np.eye(2) / 2)
    a = one.instrument(rho2, z_instrument(), 'general:1')
    b = two.instrument(rho2, z_instrument(), 'general:1')
    assert a.outcome == b.outcome
    assert a.metadata['rng']['state_before'] == b.metadata['rng']['state_before']
    assert a.metadata['rng']['algorithm'] == 'PCG64'


def test_grouped_kraus_born_probabilities_and_mixed_conditional_state():
    rho = feature(np.array([[.5, .5], [.5, .5]]))
    # One recorded outcome groups two hidden Kraus branches, causing dephasing.
    kraus = feature({'dephase': (np.diag([1., 0.]), np.diag([0., 1.]))},
                    'kraus_instrument', name='measurement.grouped')
    engine = MeasurementEngine(seed=4)
    probabilities = engine.probabilities(rho, kraus)
    np.testing.assert_allclose(probabilities.value, [1.])
    record = engine.instrument(rho, kraus, 'grouped')
    np.testing.assert_allclose(record.post_state, np.eye(2) / 2)
    assert record.metadata['kraus_counts'] == {'dephase': 2}
    assert record.probability == 1. and record.outcome == 'dephase'
    assert {p.record_id for p in record.provenance.parents} == {rho.provenance.record_id, kraus.provenance.record_id}


def test_effects_only_povm_does_not_invent_a_poststate():
    rho = feature(np.diag([.25, .75]))
    engine = MeasurementEngine(seed=7)
    np.testing.assert_allclose(engine.probabilities(rho, z_effects()).value, [.25, .75])
    record = engine.povm(rho, z_effects(), 'povm')
    assert record.kind == 'povm_effects_only' and record.post_state is None
    assert record.metadata['post_state_availability'] == 'effects_do_not_determine_instrument'
    assert record.pre_state is not None


def test_same_effects_distinct_instruments_have_different_conditional_poststates():
    rho = feature(np.eye(2) / 2)
    engine = MeasurementEngine(seed=2)
    a = engine.instrument(rho, z_instrument(), 'a', outcome='0')
    b = engine.instrument(rho, z_instrument(flip=True), 'b', outcome='0')
    assert a.probability == b.probability == .5
    assert a.origin == b.origin == 'conditional_evaluation'
    assert a.metadata['selection'] == 'specified_outcome_conditioning'
    assert a.metadata['rng'] is None and b.metadata['rng'] is None
    np.testing.assert_allclose(a.post_state, np.diag([1., 0.]))
    np.testing.assert_allclose(b.post_state, np.diag([0., 1.]))
    # Effects-only conditioning still cannot choose either of these updates.
    assert engine.povm(rho, z_effects(), 'effects', outcome='0').post_state is None


def test_impossible_outcome_is_not_normalized_into_a_state_or_sampled():
    rho = feature(np.diag([1., 0.]))
    engine = MeasurementEngine(seed=1)
    assert engine.instrument(rho, z_instrument(), 'draw').outcome == '0'
    with pytest.raises(ValueError, match='zero'):
        engine.instrument(rho, z_instrument(), 'impossible', outcome='1')
    with pytest.raises(ValueError):
        engine.povm(rho, z_effects(), 'unknown', outcome='9')


@pytest.mark.parametrize('value,quantity', [
    ({'only': (np.eye(2) / 2,)}, 'kraus_instrument'),
    ({'negative': np.diag([-.1, .5]), 'rest': np.diag([1.1, .5])}, 'povm_effects'),
    ({'bad': np.array([[1., 1.], [0., 0.]]), 'rest': np.diag([0., 1.])}, 'povm_effects'),
    ({'empty': ()}, 'kraus_instrument'),
    ({'bad': (np.ones((3, 2)),)}, 'kraus_instrument'),
])
def test_general_measurement_completeness_positivity_shape_and_group_validation(value, quantity):
    rho = feature(np.eye(2) / 2)
    operators = feature(value, quantity, name='measurement.invalid')
    with pytest.raises(ValueError):
        MeasurementEngine().probabilities(rho, operators)


def test_instrument_and_effects_require_matching_declared_coordinates():
    rho = feature(np.eye(2) / 2)
    original = z_instrument()
    mismatch = feature(dict(original.value), 'kraus_instrument',
        basis=BasisMetadata('energy', 2, 'hamiltonian'), name='different.kraus')
    with pytest.raises(ValueError):
        MeasurementEngine().instrument(rho, mismatch, 'wrongcoords')


def backend_record(*, value=None, clock=None):
    return feature(value or {'outcome': '0101', 'probability': .2, 'shots': 1},
        'measurement_event', name='backend.measurements.event42', dimension=16,
        backend='hardware:recorded', evidence='observed',
        clock=clock or ClockStamp(1234., 's', 'backend', 'recorded_event_time', 'device:run42'))


def test_backend_record_preserves_supplied_event_clock_outcome_and_no_quantum_states():
    raw = backend_record()
    record = MeasurementEngine().backend_observed(raw, event_id='recorded:42', outcome='0101',
        measurement_kind='backend_measurement', basis=raw.provenance.basis, probability=.2, shots=1)
    assert record.origin == 'backend_observed'
    assert record.clock == raw.provenance.clock
    assert record.outcome == '0101' and record.probability == .2
    assert record.pre_state is None and record.post_state is None
    assert record.metadata['rng'] is None
    assert record.provenance.parents == (raw.provenance,)


def test_unknown_backend_time_remains_missing_not_arrival_or_sequence_time():
    raw = backend_record(clock=ClockStamp(None, 's', 'backend', 'unavailable', 'device:run42'))
    record = MeasurementEngine().backend_observed(raw, event_id='42', outcome='0101',
        measurement_kind='backend_measurement', basis=raw.provenance.basis)
    assert record.clock.value is None and record.probability is None and record.shots is None


def test_counts_cannot_be_expanded_to_fabricated_backend_event_or_timing():
    counts = feature({'0': 17, '1': 9}, 'counts', name='backend.counts', backend='hardware', evidence='observed')
    with pytest.raises(ValueError, match='event'):
        MeasurementEngine().backend_observed(counts, event_id='invented', outcome='0',
            measurement_kind='backend_measurement', basis=counts.provenance.basis)
    raw = backend_record()
    with pytest.raises(ValueError, match='outcome'):
        MeasurementEngine().backend_observed(raw, event_id='invented', outcome='1111',
            measurement_kind='backend_measurement', basis=raw.provenance.basis)
    with pytest.raises(ValueError, match='probability'):
        MeasurementEngine().backend_observed(raw, event_id='invented', outcome='0101',
            measurement_kind='backend_measurement', basis=raw.provenance.basis, probability=.9)


def test_simulated_event_cannot_be_relabelled_as_backend_observation():
    simulated = feature({'outcome': '0'}, 'measurement_event', name='simulation.sample')
    with pytest.raises(ValueError, match='observ'):
        MeasurementEngine().backend_observed(simulated, event_id='falserecord', outcome='0',
            measurement_kind='backend_measurement', basis=simulated.provenance.basis)


def test_probabilities_and_conditional_evaluation_do_not_advance_rng():
    engine = MeasurementEngine(seed=17)
    before = engine.rng.bit_generator.state
    rho = feature(np.eye(2) / 2)
    engine.probabilities(rho, z_instrument())
    engine.instrument(rho, z_instrument(), 'conditioned', outcome='0')
    engine.povm(rho, z_effects(), 'conditioned_effects', outcome='1')
    assert engine.rng.bit_generator.state == before


def test_general_events_preserve_uncertainty_and_definition_arrays_immutably():
    source = feature(np.eye(2) / 2)
    source = FeatureValue(source.id, source.value, source.provenance,
        uncertainty={'kind': 'tomography', 'covariance_ref': 'estimator:covariance:1'})
    record = MeasurementEngine().instrument(source, z_instrument(), 'event', outcome='0')
    assert record.provenance.parameters['source_uncertainty']['covariance_ref'] == 'estimator:covariance:1'
    matrix = record.provenance.parameters['measurement_definition']['0'][0]
    with pytest.raises(ValueError):
        matrix.setflags(write=True)


def test_actual_density_backend_snapshot_can_feed_measurement_without_unit_relabeling():
    from types import SimpleNamespace
    from qmw.architecture_v1.backend import DensitySnapshotBackend, DENSITY
    from qmw.architecture_v1.contracts import ExecutionRequest
    rho = feature(ghz())
    owner = SimpleNamespace(rho=rho.value, logical_time=2.5, state_revision=8)
    backend = DensitySnapshotBackend(owner, rho.provenance)
    result = backend.execute(ExecutionRequest('snapshot', 'snapshot', frozenset({DENSITY.path}), rho.provenance.clock))
    captured = next(f for f in result.features if f.id == DENSITY)
    assert captured.units == 'dimensionless'
    record = MeasurementEngine().projective(captured, 'backend:snapshot:measurement')
    assert record.provenance.parents == (captured.provenance,)
    assert record.probability == pytest.approx(.5)
