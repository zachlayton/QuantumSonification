"""Shared preparation and live mappings exercise actual QMW projectors."""
from dataclasses import replace
import json
import math

import numpy as np
import pytest

from qmw.core.state_frame import QuantumStateFrame
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
from qmw.acoustics.note_timbre import (
    GeometryModes, QuantumTimbreProjector, RatioField, TransitionPitchProjector,
)
from qmw.architecture_v1.contracts import RoutingPreset
from qmw.architecture_v1.integration import prepare_routed_event, render_routed_event
from qmw.architecture_v1.live import LiveRoutingConfig, route_live_event, analyze_live_snapshot
from qmw.architecture_v1.router import SonificationRouter


def inputs(*, gap=1., order=1, duration=.001, geometry_kind='identity', rho=None):
    if rho is None:
        rho = np.diag([.25, .75] + [0.] * 14)
    context = FrameContext('runtime-test', 7, .14, .02,
                           'four_qubit_computational:q0-lsb')
    units = QuantumUnits()
    h = np.diag(np.arange(16) * gap)
    x = np.array([[0., 1.], [1., 0.]])
    a = np.kron(np.eye(8), x) if order == 1 else np.kron(np.eye(4), np.kron(x, np.eye(2)))
    state = QuantumStateFrame(context.time, context.dt, rho, h, context.source_id)
    transition = TransitionEngine(units=units).process(h, a, rho, context)
    pitch = TransitionPitchProjector(state_degrees=tuple(range(16)),
        ratio_field=RatioField((1., 9/8, 5/4, 4/3, 3/2), reference_hz=220.),
        duration_seconds=duration, min_activity=1e-6)
    note = next(n for n in pitch.process(transition)
                if (n.source_state, n.target_state) == (0, order))
    phi = (np.eye(16) if geometry_kind == 'identity'
           else np.exp(2j * np.pi * np.outer(np.arange(16), np.arange(16)) / 16) / 4)
    f = np.linspace(220., 1600., 16)
    geometry = GeometryModes(phi, context.basis_id, 'declared-abstract-' + geometry_kind,
        tuple(f'mode-{j}' for j in range(16)), f, np.pi*f*.18, np.zeros(16),
        provenance=('abstract Hilbert modes; no physical embedding',))
    body = QuantumTimbreProjector().process(rho=rho, geometry_modes=geometry, context=context)
    return dict(state=state, context=context, units=units, operator=a,
                transition=transition, note=note, pitch_projector=pitch,
                body=body, geometry=geometry)


@pytest.mark.parametrize('source,expected', [
    ('matrix_element_magnitude', 1.), ('state_weighted_magnitude', .5),
    ('diagnostic_activity', .25),
])
@pytest.mark.parametrize('rhythm', ['energy_gap', 'absolute_order'])
def test_selected_sources_reuse_actual_features_and_relabel_excitation(source, expected, rhythm):
    data = inputs()
    result = route_live_event(**data, configuration=LiveRoutingConfig(
        amplitude_source=source, rhythm_source=rhythm), now=4.)
    assert result.prepared.original_note is data['note']
    assert result.prepared.body is data['body']
    assert result.prepared.excitation.strength == pytest.approx(expected)
    assert result.prepared.excitation.activity_name == 'mapped_linear_excitation_amplitude'
    assert result.prepared.excitation.activity_units == '1'
    assert result.prepared.original_note.strength == .25
    assert result.prepared.excitation.event_id == data['note'].event_id
    assert result.prepared.excitation.onset_seconds == 4.
    assert result.prepared.excitation.duration_seconds == .001
    assert result.mapped_interval_seconds == pytest.approx(8.)
    assert result.scheduled_interval_seconds == pytest.approx(8.)
    assert result.rhythm_event.source_feature.quantity == rhythm
    assert len(result.audit['active_parameters']) == 8
    amplitude = result.audit['amplitude']
    assert amplitude['source'] == source
    assert amplitude['normalized_excitation'] == pytest.approx(expected)
    assert amplitude['selection_probability'] == 'not_used'
    assert amplitude['reference_units'] == ('dimensionless^2' if source == 'diagnostic_activity' else 'dimensionless')
    json.dumps(result.audit, allow_nan=False)


def test_calibration_changes_excitation_only_and_clips_with_provenance():
    data = inputs()
    a = route_live_event(**data, configuration=LiveRoutingConfig(amplitude_reference=1.), now=0.)
    b = route_live_event(**data, configuration=LiveRoutingConfig(amplitude_reference=2.), now=0.)
    c = route_live_event(**data, configuration=LiveRoutingConfig(amplitude_reference=.1), now=0.)
    assert a.prepared.excitation.strength == 2*b.prepared.excitation.strength
    assert c.prepared.excitation.strength == 1.
    assert c.audit['amplitude']['clipped']
    assert a.prepared.excitation.event_id == b.prepared.excitation.event_id
    np.testing.assert_array_equal(a.prepared.body.amplitude_gains, b.prepared.body.amplitude_gains)
    assert a.scheduled_interval_seconds == b.scheduled_interval_seconds


def test_rhythm_quantization_and_bounds_remain_separate_from_envelope_duration():
    data = inputs(gap=11., duration=.25)
    config = LiveRoutingConfig(rhythm_source='energy_gap', quantization='lattice')
    result = route_live_event(**data, configuration=config, now=12.)
    assert result.mapped_interval_seconds == .75
    assert result.scheduled_interval_seconds == .75
    assert result.prepared.excitation.duration_seconds == .25
    assert result.audit['rhythm']['scheduler_policy'] == 'at_most_one_event_per_observation_no_catchup'
    for gap, bound in [(100., .5), (.001, 8.)]:
        limited = route_live_event(**inputs(gap=gap), configuration=replace(config, quantization='continuous'), now=0.)
        assert limited.scheduled_interval_seconds == bound
        assert limited.audit['rhythm']['interval_limited']
        assert limited.audit['rhythm']['unbounded_interval_seconds'] == limited.mapped_interval_seconds


@pytest.mark.parametrize('source', ['energy_gap', 'absolute_order'])
def test_default_rhythm_calibration_retains_audible_source_contrast(source):
    config = LiveRoutingConfig(rhythm_source=source)
    a = route_live_event(**inputs(), configuration=config, now=0.)
    changed = inputs(gap=2.) if source == 'energy_gap' else inputs(order=2)
    b = route_live_event(**changed, configuration=config, now=0.)
    assert a.mapped_interval_seconds == pytest.approx(8.)
    assert b.mapped_interval_seconds == pytest.approx(4.)
    assert a.scheduled_interval_seconds == pytest.approx(8.)
    assert b.scheduled_interval_seconds == pytest.approx(4.)
    assert a.audit['rhythm']['interval_limited'] is False
    assert b.audit['rhythm']['interval_limited'] is False


@pytest.mark.parametrize('view', ['computational', 'hamiltonian', 'qho', 'qft'])
def test_basis_view_is_passive_and_does_not_change_note_or_body(view):
    data = inputs()
    before_rho, before_h = data['state'].rho.copy(), data['state'].hamiltonian.copy()
    result = route_live_event(**data, configuration=LiveRoutingConfig(analysis_basis=view), now=0.)
    assert result.analysis.basis.metadata.kind == view
    assert result.audit['analysis']['rho_roundtrip_error'] < 1e-10
    assert result.audit['analysis']['physical_evolution'] is False
    assert result.audit['analysis']['source_subsystem_order'] == 'q0_lsb'
    np.testing.assert_array_equal(before_rho, data['state'].rho)
    np.testing.assert_array_equal(before_h, data['state'].hamiltonian)
    np.testing.assert_array_equal(result.prepared.body.amplitude_gains, data['body'].amplitude_gains)
    assert result.prepared.excitation.target_frequency_hz == data['note'].target_frequency_hz
    if view == 'qho':
        assert result.audit['analysis']['qho_encoding']['source_hamiltonian_claim'] is False


def test_q0_lsb_input_and_body_independence():
    rho = np.diag([.25, .75] + [0.] * 14)
    data = inputs(rho=rho)
    a = route_live_event(**data, configuration=LiveRoutingConfig(), now=0.)
    b = route_live_event(**inputs(rho=rho, geometry_kind='fourier'), configuration=LiveRoutingConfig(), now=0.)
    captured = a.feature_frame.get('quantum.state.rho')
    np.testing.assert_array_equal(captured.value, rho)
    assert captured.value[1,1] == .75 and captured.value[8,8] == 0
    assert a.prepared.excitation.strength == b.prepared.excitation.strength
    assert a.prepared.excitation.target_frequency_hz == b.prepared.excitation.target_frequency_hz
    assert not np.allclose(a.prepared.body.amplitude_gains, b.prepared.body.amplitude_gains)


def test_duplicate_amplitude_and_stale_body_fail_same_shared_junction():
    data = inputs()
    result = route_live_event(**data, configuration=LiveRoutingConfig(), now=0.)
    preset = result.audit['routing_preset']
    assert preset['mode'] == 'ANALYSIS'
    amplitude = result.feature_frame.get('note.amplitude')
    from qmw.architecture_v1.contracts import MappingSpec, RouteSpec
    route = RouteSpec('note.amplitude', amplitude.id,
        MappingSpec('identity-amplitude', '1', 'identity', (amplitude.id,), '1', 'none'))
    with pytest.raises(ValueError, match='already'):
        SonificationRouter(RoutingPreset('bad', (route, route)))
    wrong_body = replace(data['body'], frequencies_hz=data['body'].frequencies_hz*1.01,
                         decay_seconds=data['body'].decay_seconds/1.01)
    with pytest.raises(ValueError, match='body'):
        prepare_routed_event(data['note'], wrong_body, result.prepared.routed)


def test_offline_and_live_use_identical_prepared_values():
    data = inputs(duration=.001)
    # Explicitly align the musical anchor with this offline buffer's clock.
    result = route_live_event(**data, configuration=LiveRoutingConfig(), now=data['context'].time)
    offline, provenance = render_routed_event(data['note'], data['body'], result.prepared.routed,
                                             duration_seconds=.1)
    for field in ('strength', 'activity_name', 'activity_units', 'duration_seconds',
                  'onset_seconds', 'event_id', 'target_frequency_hz'):
        assert getattr(offline.excitation, field) == getattr(result.prepared.excitation, field)
    assert provenance.parameters['prepared_event_digest'] == result.prepared.provenance.digest
    assert len(provenance.parents) == 8


def test_configuration_is_explicit_reproducible_and_rejects_unavailable_live_sources():
    config = LiveRoutingConfig()
    assert len(config.digest) == 64 and int(config.digest, 16) >= 0
    assert config.digest == LiveRoutingConfig(**config.to_dict()).digest
    for change in (dict(revision=1), dict(amplitude_reference=2), dict(analysis_basis='qft'),
                   dict(rhythm_source='energy_gap'), dict(quantization='lattice')):
        assert replace(config, **change).digest != config.digest
    for change in (dict(amplitude_source='decay_survival'), dict(rhythm_source='collider_event_time'),
                   dict(amplitude_reference=0), dict(amplitude_reference=True), dict(analysis_basis='physical_mesh'),
                   dict(gap_time_scale=math.nan), dict(minimum_interval_seconds=9), dict(revision=-1),
                   dict(quantization='unknown')):
        with pytest.raises(ValueError):
            replace(config, **change)


def test_shared_junction_rejects_nonfinite_or_nonscalar_timing():
    from qmw.architecture_v1.contracts import FeatureValue, RoutedFrame
    data = inputs()
    result = route_live_event(**data, configuration=LiveRoutingConfig(), now=0.)
    for path, value in [('note.onset', np.nan), ('note.duration', -1.), ('note.duration', np.array([.1]))]:
        old = result.prepared.routed.values[path]
        with pytest.raises(ValueError):
            feature = FeatureValue(old.id, value, old.provenance)
            bad = RoutedFrame(result.prepared.routed.frame_id,
                dict(result.prepared.routed.values) | {path: feature},
                result.prepared.routed.mode, result.prepared.routed.preset_id)
            prepare_routed_event(data['note'], data['body'], bad)


@pytest.mark.parametrize('now', [True, 1+0j, np.inf, [0.], None, '0'])
def test_live_clock_must_be_finite_real_scalar_seconds(now):
    with pytest.raises(ValueError, match='anchor'):
        route_live_event(**inputs(), configuration=LiveRoutingConfig(), now=now)


def test_no_transition_snapshot_still_computes_all_four_basis_views():
    data = inputs()
    state = replace(data['state'], rho=np.eye(16)/16)
    operator = np.diag([1., -1.] * 8)
    transition = TransitionEngine(units=data['units']).process(
        state.hamiltonian, operator, state.rho, data['context'])
    assert data['pitch_projector'].process(transition) == ()
    rho_before, h_before, a_before = state.rho.copy(), state.hamiltonian.copy(), operator.copy()
    for choice in ('computational', 'hamiltonian', 'qho', 'qft'):
        config = LiveRoutingConfig(analysis_basis=choice)
        result = analyze_live_snapshot(state=state, context=data['context'], units=data['units'],
                                       operator=operator, configuration=config)
        assert result['schema'] == 'qmw.live.analysis.audit.v2'
        assert result['configuration_digest'] == config.digest
        assert result['analysis']['selected_basis'] == choice
        assert result['analysis']['rho_roundtrip_error'] < 1e-10
        assert result['analysis']['physical_evolution'] is False
        assert result['source']['source_revision'] == data['context'].frame_id
        assert len(result['source']['rho_sha256']) == 64
        assert 'active_parameters' not in result and 'prepared_excitation' not in result
        json.dumps(result, allow_nan=False)
    np.testing.assert_array_equal(state.rho, rho_before)
    np.testing.assert_array_equal(state.hamiltonian, h_before)
    np.testing.assert_array_equal(operator, a_before)
