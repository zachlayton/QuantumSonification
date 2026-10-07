import math

import numpy as np
import pytest

from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureId, FeatureValue, MappingSpec, Provenance,
)
from qmw.architecture_v1.rhythm import RhythmProjector


def source(quantity='energy_gap', value=2., units='model_energy', clock=None, record='frame:1'):
    clock = clock or ClockStamp(0., 's', 'simulation', 'elapsed', 'run:1')
    p = Provenance(record, 'transition.source', 'capture', '1', {}, units, 'none',
                   BasisMetadata('energy', 16, 'hamiltonian'), clock, 'numpy', 'simulated')
    return FeatureValue(FeatureId('transition.source', quantity), value, p)


def anchor(value=3.):
    return ClockStamp(value, 's', 'musical', 'scheduled_onset', 'score:1')


def mapping(f, **parameters):
    return MappingSpec('rhythm:test', '1', 'rhythm', (f.id,), 's', 'none',
                       {'input_units': (f.units,), **parameters})


def energy(f, **parameters):
    return mapping(f, **{'energy_constant_kind': 'hbar', 'energy_constant': 1.,
        'energy_constant_unit': 'model_energy*s', 'source_time_unit': 's',
        'source_seconds_per_unit': 1., 'frequency_convention': 'angular',
        'time_scale': .5, **parameters})


def timestamp(f, **parameters):
    c = f.provenance.clock
    return mapping(f, **{'input_clock': {'unit': c.unit, 'domain': c.domain,
        'semantics': c.semantics, 'origin': c.origin}, 'source_origin_value': 10.,
        'source_seconds_per_unit': 1., 'time_scale': 2., **parameters})


def test_energy_period_h_and_hbar_agree_but_are_not_waiting_times():
    f = source()
    a = RhythmProjector(energy(f)).project(f, 'event:1', anchor())
    b = RhythmProjector(energy(f, energy_constant_kind='h', energy_constant=math.tau,
        frequency_convention='Hz')).project(f, 'event:1', anchor())
    assert a.interval_seconds == pytest.approx(math.pi / 2)
    assert a.interval_seconds == pytest.approx(b.interval_seconds)
    assert a.onset == anchor()
    assert a.provenance.parameters['interpretation'] == 'musical_period_mapping_not_physical_waiting_time'
    assert a.provenance.parents == (f.provenance,)
    assert a.provenance.parameters['mapping_id'] == 'rhythm:test'
    assert a.source_feature == f.id


def test_energy_unit_conversion_and_signed_gap_magnitude():
    f = source(value=-4.)
    spec = energy(f, energy_constant_unit='model_energy*ms', source_time_unit='ms',
                  source_seconds_per_unit=.001, time_scale=1000.)
    result = RhythmProjector(spec).project(f, 'e', anchor())
    assert result.interval_seconds == pytest.approx(math.pi / 2)
    assert result.provenance.parameters['evaluation']['absolute_energy_gap'] == 4.


@pytest.mark.parametrize('overrides', [
    {'frequency_convention': 'Hz'}, {'energy_constant_unit': 'eV*s'},
    {'energy_constant': 0.}, {'source_seconds_per_unit': -1.}, {'time_scale': float('inf')},
])
def test_energy_rejects_ambiguous_or_invalid_conversion(overrides):
    f = source()
    with pytest.raises(ValueError):
        RhythmProjector(energy(f, **overrides)).project(f, 'e', anchor())


def test_zero_gap_is_inactive_without_infinite_interval():
    f = source(value=0.)
    event = RhythmProjector(energy(f)).project(f, 'silent', anchor())
    assert event.active is False and event.interval_seconds is None
    with pytest.raises(ValueError):
        RhythmProjector(energy(f)).as_feature(event)


def test_one_source_and_exact_quantity_are_required():
    f = source()
    other = source('absolute_order', 2., 'index')
    with pytest.raises(ValueError):
        RhythmProjector(MappingSpec('bad', '1', 'rhythm', (f.id, other.id), 's', 'none'))
    with pytest.raises(ValueError):
        RhythmProjector(energy(f)).project(other, 'e', anchor())
    with pytest.raises(ValueError):
        RhythmProjector(energy(f)).project(f, 'e', ClockStamp(0, 's', 'simulation', 'elapsed', 'run:1'))


def test_signed_order_preserves_direction_under_declared_policy():
    positive = source('signed_order', 2, 'index')
    negative = source('signed_order', -2, 'index')
    projector = RhythmProjector(mapping(positive, order_policy='power_of_two', base_interval_seconds=1.))
    assert projector.project(positive, 'plus', anchor()).interval_seconds == .25
    assert projector.project(negative, 'minus', anchor()).interval_seconds == 4.
    with pytest.raises(ValueError):
        RhythmProjector(mapping(positive, base_interval_seconds=1.))
    absolute = source('absolute_order', 2, 'index')
    assert RhythmProjector(mapping(absolute, base_interval_seconds=1.)).project(absolute, 'a', anchor()).interval_seconds == .5
    with pytest.raises(ValueError):
        RhythmProjector(mapping(absolute, base_interval_seconds=1.)).project(source('absolute_order', -2, 'index'), 'bad', anchor())


def test_lattice_and_ratio_mapping_are_explicit_deterministic_choices():
    f = source('decay_lifetime', .375, 's')
    lattice = RhythmProjector(mapping(f, source_seconds_per_unit=1., quantization='lattice', lattice_quantum_seconds=.25))
    event = lattice.project(f, 'e', anchor())
    assert event.interval_seconds == .5  # Half ties round upward.
    ratio = RhythmProjector(mapping(f, source_seconds_per_unit=1., quantization='ratio',
        base_interval_seconds=.5, ratios=(.5, 1., 1.5, 2.)))
    assert ratio.project(f, 'e', anchor()).interval_seconds == .5
    assert event.provenance.parameters['evaluation']['unquantized_seconds'] == .375


@pytest.mark.parametrize('quantity', ['event_timestamp', 'flux_event_timestamp', 'decay_event_time', 'collider_event_time'])
def test_actual_timestamps_map_only_from_declared_clock_and_origin(quantity):
    f = source(quantity, 12., 's', ClockStamp(12., 's', 'proper_time', 'elapsed', 'event:parent'))
    event = RhythmProjector(timestamp(f)).project(f, 'e', anchor())
    assert event.onset.value == 7.
    assert event.interval_seconds is None
    assert event.provenance.parents == (f.provenance,)
    wrong = source(quantity, 12., 's', ClockStamp(12., 's', 'arrival', 'elapsed', 'receiver'))
    with pytest.raises(ValueError):
        RhythmProjector(timestamp(f)).project(wrong, 'e', anchor())
    missing = FeatureValue(f.id, None, f.provenance, 'missing', 'no measured timing')
    with pytest.raises(ValueError, match='no measured timing'):
        RhythmProjector(timestamp(f)).project(missing, 'e', anchor())


def test_timestamp_sequence_differences_keep_both_source_provenances():
    first = source('event_timestamp', 10., 's', ClockStamp(10., 's', 'simulation', 'elapsed', 'run:1'), 'frame:1')
    second = source('event_timestamp', 10.25, 's', ClockStamp(10.25, 's', 'simulation', 'elapsed', 'run:1'), 'frame:2')
    projector = RhythmProjector(timestamp(first))
    frame = projector.project_sequence((first, second), 'rhythm:frame', ('one', 'two'), anchor())
    assert [e.onset.value for e in frame.events] == [3., 3.5]
    assert frame.events[0].interval_seconds is None
    assert frame.events[1].interval_seconds == .5
    parents = frame.events[1].provenance.parents
    assert {p.record_id for p in parents} == {'frame:1', 'frame:2'}
    assert len(frame.provenance.parents) == 2
    with pytest.raises(ValueError):
        projector.project_sequence((second, first), 'reverse', ('two', 'one'), anchor())


def test_timestamp_value_cannot_be_an_unrelated_arrival_clock():
    f = source('collider_event_time', 12., 's', ClockStamp(100., 's', 'recorded', 'arrival', 'detector'))
    with pytest.raises(ValueError, match='clock'):
        RhythmProjector(timestamp(f)).project(f, 'e', anchor())


def test_quantized_timestamp_intervals_equal_actual_musical_onset_differences():
    one = source('event_timestamp', 10.1, 's', ClockStamp(10.1, 's', 'simulation', 'elapsed', 'run:1'))
    two = source('event_timestamp', 10.4, 's', ClockStamp(10.4, 's', 'simulation', 'elapsed', 'run:1'), 'frame:2')
    projector = RhythmProjector(timestamp(one, time_scale=1., quantization='lattice', lattice_quantum_seconds=.25))
    events = projector.project_sequence((one, two), 'f', ('a', 'b'), anchor()).events
    assert events[1].interval_seconds == events[1].onset.value - events[0].onset.value


def test_projected_feature_routes_with_its_full_mapping_and_source_chain():
    from qmw.architecture_v1.contracts import FeatureFrame, RouteSpec, RoutingPreset
    from qmw.architecture_v1.router import SonificationRouter
    f = source()
    projector = RhythmProjector(energy(f))
    event = projector.project(f, 'e', anchor())
    projected = projector.as_feature(event)
    identity = MappingSpec('route:rhythm', '1', 'identity', (projected.id,), 's', 'none')
    router = SonificationRouter(RoutingPreset('analysis', (RouteSpec('rhythm', projected.id, identity),)))
    result = router.route(FeatureFrame('f', (projected,)))
    assert result.values['rhythm'].value == event.interval_seconds
    assert result.values['rhythm'].provenance.parents[0].parents[0] == f.provenance


def test_invalid_values_and_unknown_options_fail_closed():
    f = source('signed_order', 1.5, 'index')
    with pytest.raises(ValueError):
        RhythmProjector(mapping(f, order_policy='power_of_two', base_interval_seconds=1.)).project(f, 'e', anchor())
    with pytest.raises(ValueError):
        RhythmProjector(energy(source(), undocumented_magic=1.))
    vector = source(value=np.array([1., 2.]))
    with pytest.raises(ValueError):
        RhythmProjector(energy(vector)).project(vector, 'e', anchor())


def test_missing_required_mapping_parameters_raise_contract_errors():
    f = source()
    with pytest.raises(ValueError):
        RhythmProjector(mapping(f))
    f = source('decay_lifetime', .2, 's')
    with pytest.raises(ValueError):
        RhythmProjector(mapping(f))


def test_accumulated_schedule_retains_previous_interval_dependencies():
    one = source('absolute_order', 1, 'index', record='frame:one')
    two = source('absolute_order', 2, 'index', record='frame:two')
    projector = RhythmProjector(mapping(one, base_interval_seconds=1.))
    frame = projector.project_sequence((one, two), 'sequence', ('a', 'b'), anchor())
    assert [e.onset.value for e in frame.events] == [3., 4.]
    assert {p.record_id for p in frame.events[1].provenance.parents} == {'a:rhythm', 'frame:two'}


def test_actual_four_qubit_transition_gap_and_authoritative_hbar_are_reused():
    from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
    from qmw.core.state_frame import QuantumStateFrame
    from qmw.architecture_v1.adapters import state_features, operator_feature, transition_features
    context = FrameContext('qho:fixture', 1, 0., .01, 'computational')
    units = QuantumUnits(hbar=2.)
    rho = np.eye(16) / 16
    h = np.diag(2. * 3. * (np.arange(16) + .5))
    operator = np.diag(np.sqrt(np.arange(1, 16)), 1)
    state = QuantumStateFrame(0., .01, rho, h, 'qho:fixture')
    raw = state.rho.copy()
    native = TransitionEngine(units=units).process(h, operator, state.rho, context)
    source_frame = state_features(state, context, units)
    features = transition_features(native, source_frame.get('quantum.state.rho'),
        source_frame.get('quantum.state.hamiltonian'), operator_feature(operator, context, units))
    gap = features.get('transition.n2.m1.delta_E')
    projector = RhythmProjector(energy(gap, energy_constant=2., time_scale=1.))
    assert projector.project(gap, 'qho:event', anchor()).interval_seconds == pytest.approx(math.tau / 3.)
    with pytest.raises(ValueError, match='hbar'):
        RhythmProjector(energy(gap)).project(gap, 'bad', anchor())
    # The same source model hbar can be declared in milliseconds explicitly.
    converted = energy(gap, energy_constant=2000., energy_constant_unit='model_energy*ms',
                       source_time_unit='ms', source_seconds_per_unit=.001, time_scale=1.)
    assert RhythmProjector(converted).project(gap, 'converted', anchor()).interval_seconds == pytest.approx(math.tau / 3.)
    with pytest.raises(ValueError, match='hbar'):
        RhythmProjector(energy(gap, energy_constant=3., energy_constant_unit='model_energy*ms',
            source_time_unit='ms', source_seconds_per_unit=.001)).project(gap, 'badunits', anchor())
    np.testing.assert_array_equal(state.rho, raw)


def test_as_feature_rejects_same_mapping_id_with_different_configuration():
    f = source()
    projector = RhythmProjector(energy(f))
    event = projector.project(f, 'e', anchor())
    other = RhythmProjector(energy(f, time_scale=2.))
    with pytest.raises(ValueError):
        other.as_feature(event)
