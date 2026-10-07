"""Declared downstream mappings for the existing paired live H/rho observer.

This module owns neither evolution nor scheduling. The caller supplies the
actual transition, admitted native note and independent body; the result tells
its latest-only scheduler which interval to use before another event. Only
features available from this native source are selectable. A new backend must
explicitly supply real timing/amplitude data before exposing further sources.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np

from .adapters import (state_features, operator_feature, transition_features,
                       note_pitch_feature, timbre_features)
from .amplitude import TransitionAmplitudeProjector
from .basis import BasisProjector
from .contracts import (ClockStamp, Provenance, FeatureId, FeatureValue,
                        FeatureFrame, MappingSpec, RouteSpec, RoutingPreset,
                        BasisProjectionFrame, RhythmEvent, plain)
from .integration import PreparedRoutedEvent, prepare_routed_event
from .rhythm import RhythmProjector
from .router import FeatureBus, SonificationRouter


AMPLITUDE_SOURCES = ('matrix_element_magnitude', 'state_weighted_magnitude', 'diagnostic_activity')
RHYTHM_SOURCES = ('energy_gap', 'absolute_order')
QUANTIZATIONS = ('continuous', 'lattice')
ANALYSIS_BASES = ('computational', 'hamiltonian', 'qho', 'qft')
GAP_STRETCH = 8. / math.tau


@dataclass(frozen=True)
class LiveRoutingConfig:
    """Immutable calibration of the live ANALYSIS route preset.

    The fixed amplitude reference has the selected source's explicitly logged
    operator units (squared for diagnostic activity). With the current Pauli
    coupling it defaults to 1 dimensionless, or 1 dimensionless squared.

    Gap timing maps 2*pi*hbar/abs(DeltaE) with the named musical stretch
    GAP_STRETCH=8/(2*pi). This is not a physical waiting-time prediction.
    Safety interval limits are a declared second mapping, not source units.
    """
    amplitude_source: str = 'state_weighted_magnitude'
    amplitude_reference: float = 1.
    rhythm_source: str = 'absolute_order'
    base_interval_seconds: float = 8.
    gap_time_scale: float = GAP_STRETCH
    quantization: str = 'continuous'
    lattice_quantum_seconds: float = .125
    minimum_interval_seconds: float = .5
    maximum_interval_seconds: float = 8.
    analysis_basis: str = 'computational'
    revision: int = 0

    def __post_init__(self):
        for name, choices in (('amplitude_source', AMPLITUDE_SOURCES),
                              ('rhythm_source', RHYTHM_SOURCES),
                              ('quantization', QUANTIZATIONS),
                              ('analysis_basis', ANALYSIS_BASES)):
            if getattr(self, name) not in choices:
                raise ValueError(f'unsupported live {name}; available selections: {choices}')
        if type(self.revision) is not int or self.revision < 0:
            raise ValueError('routing revision must be a nonnegative integer')
        for name in ('amplitude_reference', 'base_interval_seconds', 'gap_time_scale',
                     'lattice_quantum_seconds', 'minimum_interval_seconds', 'maximum_interval_seconds'):
            value = getattr(self, name)
            if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
                raise ValueError(f'{name} must be a finite positive number')
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be a finite positive number')
            object.__setattr__(self, name, float(value))
        if self.minimum_interval_seconds > self.maximum_interval_seconds:
            raise ValueError('minimum interval cannot exceed maximum interval')

    def to_dict(self):
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class LiveRoutingResult:
    prepared: PreparedRoutedEvent
    rhythm_event: RhythmEvent
    mapped_interval_seconds: float
    scheduled_interval_seconds: float
    feature_frame: FeatureFrame
    analysis: BasisProjectionFrame
    audit: dict
    configuration_digest: str


def _identity(feature):
    return RouteSpec(feature.id.path, feature.id, MappingSpec(
        'live.route:' + feature.id.path, '1', 'identity', (feature.id,),
        feature.units, 'none', {'input_units': (feature.units,)}))


def _hash_array(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def _mapping_dict(mapping):
    return {name: plain(getattr(mapping, name)) for name in mapping.__dataclass_fields__}


def _analysis(rho, hamiltonian, operator, configuration):
    projector = BasisProjector()
    choice = configuration.analysis_basis
    n = rho.provenance.basis.dimension
    if choice == 'hamiltonian':
        basis = projector.hamiltonian(hamiltonian)
    elif choice == 'qho':
        # Explicit coordinate labeling only: do not infer oscillator evolution
        # or replace the real source Hamiltonian with an oscillator model.
        basis = projector.qho(n, rho.provenance, canonical_coordinates='fock')
    elif choice == 'qft':
        basis = projector.qft(n, rho.provenance)
    else:
        basis = projector.computational(n, rho.provenance)
    projected = projector.project(rho, basis, operators={'H': hamiltonian, 'A': operator})
    restored = projector.inverse(projected.rho, basis)
    audit = {'selected_basis': choice, 'basis': basis.metadata.to_dict(),
             'rho_roundtrip_error': float(np.linalg.norm(restored-rho.value)),
             'physical_evolution': False, 'state_installation': False,
             'source_subsystem_order': rho.provenance.basis.subsystem_order,
             'coordinate_conversion': 'none; native source is already q0_lsb',
             'populations': projected.populations,
             'diagnostics': projected.diagnostics,
             'provenance': projected.provenance.to_dict()}
    if choice == 'qho':
        audit['qho_encoding'] = {
            'convention': 'computational integer n assigned to truncated Fock label n for this view',
            'source_hamiltonian_claim': False, 'physical_oscillator_evolution': False}
    return projected, audit


def _validate_snapshot(state, context, units, configuration):
    if not isinstance(configuration, LiveRoutingConfig):
        raise ValueError('live routing requires LiveRoutingConfig')
    if state.dimension != 16 or context.time_unit != 's' or units.time_unit != 's':
        raise ValueError('native live routing requires a four-qubit source with declared seconds')
    if context.basis_id != 'four_qubit_computational:q0-lsb':
        raise ValueError('native live source must explicitly declare its existing q0-lsb coordinates')


def _source_audit(state, context, operator, rho):
    return {'source_id': context.source_id, 'source_revision': context.frame_id,
            'clock': rho.provenance.clock.to_dict(), 'basis': rho.provenance.basis.to_dict(),
            'backend': 'numpy', 'rho_sha256': _hash_array(state.rho),
            'hamiltonian_sha256': _hash_array(state.hamiltonian),
            'operator_sha256': _hash_array(operator)}


def analyze_live_snapshot(*, state, context, units, operator, configuration) -> dict:
    """Observe the selected representation even when no transition is admitted.

    Returns JSON-safe source identity and passive basis evidence. This observer
    fabricates no note, route, excitation amplitude or timing event. The exact
    same basis and source-audit helpers are used for admitted musical events.
    """
    _validate_snapshot(state, context, units, configuration)
    source = state_features(state, context, units, backend='numpy')
    rho = source.get('quantum.state.rho')
    h = source.get('quantum.state.hamiltonian')
    a = operator_feature(operator, context, units, backend='numpy')
    _, analysis_audit = _analysis(rho, h, a, configuration)
    return plain({'schema': 'qmw.live.analysis.audit.v2',
        'configuration': configuration.to_dict(), 'configuration_digest': configuration.digest,
        'source': _source_audit(state, context, operator, rho), 'analysis': analysis_audit})


def route_live_event(*, state, context, units, operator, transition, note,
                     pitch_projector, body, geometry, configuration, now) -> LiveRoutingResult:
    """Prepare one caller-admitted event using the actual shared architecture.

    ``now`` is the musical scheduler's elapsed monotonic time in seconds; source
    simulation time remains unchanged in every native frame. Playback starts
    on receipt. The caller schedules its next eligible observation at
    ``now + scheduled_interval_seconds`` with no queued catch-up events.
    The note's declared strike/pitched duration remains independent of rhythm.
    """
    _validate_snapshot(state, context, units, configuration)
    clock_value = np.asarray(now)
    if clock_value.ndim != 0 or clock_value.dtype.kind not in 'iuf' or not np.isfinite(clock_value):
        raise ValueError('live musical anchor must be finite real seconds')
    now = float(now)
    if transition.context != context or note.context != context or body.context != context:
        raise ValueError('live inputs must share the actual source snapshot context')
    if transition.units != units:
        raise ValueError('live transition units must match the declared source units')
    if geometry.space_id != context.basis_id:
        raise ValueError('live geometry must use the actual source Hilbert coordinates')

    source = state_features(state, context, units, backend='numpy')
    rho = source.get('quantum.state.rho')
    h = source.get('quantum.state.hamiltonian')
    a = operator_feature(operator, context, units, backend='numpy')
    transitions = transition_features(transition, rho, h, a)
    edge = f'transition.n{note.source_state}.m{note.target_state}'
    activity = transitions.get(edge + '.diagnostic_activity')
    pitch = note_pitch_feature(note, transitions.get(edge + '.endpoints'),
                               pitch_projector, admission_feature=activity)

    config_p = Provenance('live.routing:' + configuration.digest,
        'live.routing.configuration', 'declared_live_mapping_configuration', '1',
        {'configuration': configuration.to_dict(), 'configuration_sha256': configuration.digest,
         'mode': 'ANALYSIS'}, '1', 'none', rho.provenance.basis,
        ClockStamp(float(configuration.revision), 'revision', 'configuration', 'sequence', 'live.routing'),
        'declared_configuration', 'declared_musical_configuration')

    amplitude_input = transitions.get(edge + '.' + configuration.amplitude_source)
    amplitude_projector = TransitionAmplitudeProjector(configuration.amplitude_source,
        reference=configuration.amplitude_reference, reference_units=amplitude_input.units,
        mapping_id='live.transition_amplitude', normalization='fixed_reference', overflow='clip')
    amplitude = amplitude_projector.project(amplitude_input)

    rhythm_input = transitions.get(edge + ('.delta_E' if configuration.rhythm_source == 'energy_gap' else '.absolute_order'))
    rhythm_parameters = {'input_units': (rhythm_input.units,),
                         'quantization': configuration.quantization}
    if configuration.quantization == 'lattice':
        rhythm_parameters['lattice_quantum_seconds'] = configuration.lattice_quantum_seconds
    if configuration.rhythm_source == 'energy_gap':
        rhythm_parameters.update(energy_constant_kind='hbar', energy_constant=units.hbar,
            energy_constant_unit=units.hbar_unit, source_time_unit=units.time_unit,
            source_seconds_per_unit=1., frequency_convention='angular',
            time_scale=configuration.gap_time_scale)
    else:
        rhythm_parameters['base_interval_seconds'] = configuration.base_interval_seconds
    rhythm_projector = RhythmProjector(MappingSpec('live.selected_rhythm', '1', 'rhythm',
        (rhythm_input.id,), 's', 'none', rhythm_parameters))
    anchor = ClockStamp(now, 's', 'musical', 'elapsed', 'live.monotonic_scheduler')
    rhythm = rhythm_projector.project(rhythm_input, note.event_id, anchor)
    interval = rhythm_projector.as_feature(rhythm)
    interval_route = RouteSpec('rhythm.scheduled_interval', interval.id,
        MappingSpec('live.bounded_scheduler_interval', '1', 'clip', (interval.id,), 's', 'none',
                    {'input_units': ('s',), 'minimum': configuration.minimum_interval_seconds,
                     'maximum': configuration.maximum_interval_seconds}))
    bounded = SonificationRouter(RoutingPreset('live.schedule', (interval_route,))).route(
        FeatureFrame(source.frame_id + ':rhythm', (interval,)))
    scheduled = bounded.values['rhythm.scheduled_interval']
    onset = FeatureValue(FeatureId('note.onset', 'musical_onset'), now,
        rhythm.provenance.derive(note.event_id + ':live_onset', 'caller_admitted_musical_anchor',
            parameters={'onset_anchor': anchor.to_dict(), 'playback_policy': 'on_receipt',
                'source_time_conversion': 'none', 'scheduler_policy': 'at_most_one_event_per_observation_no_catchup',
                'next_eligible_offset_seconds': scheduled.value,
                'current_admission': 'caller_checked_previous_deadline; no queue'},
            parents=(rhythm.provenance, scheduled.provenance), units='s',
            clock=anchor, source_path='note.onset', evidence='musical_mapping'))
    duration = FeatureValue(FeatureId('note.duration', 'excitation_envelope_duration'), note.duration_seconds,
        config_p.derive(note.event_id + ':duration', 'declared_excitation_envelope_duration',
            parameters={'duration_seconds': note.duration_seconds,
                        'interpretation': 'caller declared strike or pitched envelope; independent of inter-event rhythm'},
            parents=(config_p, pitch.provenance), units='s', source_path='note.duration',
            evidence='declared_musical_configuration'))

    geometry_p = config_p.derive(geometry.geometry_id + ':configuration', 'declared_independent_geometry_modes',
        parameters={'geometry_id': geometry.geometry_id, 'mode_ids': geometry.mode_ids,
                    'hilbert_vectors_sha256': _hash_array(geometry.hilbert_vectors),
                    'legacy_provenance': geometry.provenance,
                    'physical_embedding_claim': False, 'note_dependence': False})
    modes = FeatureValue(FeatureId('geometry.hilbert_modes', 'hilbert_mode_vectors', 'matrix'),
        geometry.hilbert_vectors, geometry_p)
    body_features = timbre_features(body, rho, modes)
    body_config = []
    for path, quantity, values, unit in (
        ('body.frequencies', 'modal_frequency', geometry.frequencies_hz, 'Hz'),
        ('body.quality_factors', 'modal_quality_factor', geometry.quality_factors, '1'),
        ('body.acoustic_phases', 'acoustic_phase', geometry.acoustic_phases_rad, 'rad')):
        body_config.append(FeatureValue(FeatureId(path, quantity, 'vector'), values,
            geometry_p.derive(geometry.geometry_id + ':' + path, 'declared_body_configuration',
                parameters={'values': values, 'units': unit}, units=unit,
                source_path=path, evidence='declared_musical_configuration')))
    frame = FeatureFrame(source.frame_id + ':live-routing', source.features + (a,) + transitions.features +
        (pitch, amplitude, interval, scheduled, onset, duration, modes) + body_features.features + tuple(body_config),
        {'routing_configuration_sha256': configuration.digest, 'configuration_revision': configuration.revision,
         'authority': 'read_only_native_paired_snapshot', 'backend': 'numpy'})
    bus = FeatureBus(frame)
    audible = (pitch, amplitude, onset, duration, body_features.get('body.modal_weights'), *body_config)
    preset = RoutingPreset('live.four_qubit.analysis.v2', tuple(_identity(feature) for feature in audible))
    router = SonificationRouter(preset)
    routed = router.route(bus)
    prepared = prepare_routed_event(note, body, routed)
    analysis, analysis_audit = _analysis(rho, h, a, configuration)

    amplitude_evaluation = amplitude.provenance.parameters['evaluation']
    audit = {
        'schema': 'qmw.live.routing.audit.v2', 'event_id': note.event_id,
        'configuration': configuration.to_dict(), 'configuration_digest': configuration.digest,
        'routing_preset': {'preset_id': preset.preset_id, 'mode': router.mode.value,
            'routes': tuple({'destination': route.destination,
                             'primary_source': route.primary_source.to_dict(),
                             'mapping': _mapping_dict(route.mapping)} for route in preset.routes)},
        'source': _source_audit(state, context, operator, rho),
        'admission': {'activity': note.strength, 'activity_name': note.activity_name,
                      'activity_units': note.activity_units,
                      'policy': 'caller retains deterministic transition admission; amplitude does not select events'},
        'amplitude': {'source': configuration.amplitude_source,
                      'source_feature': amplitude_input.id.to_dict(),
                      'source_value': amplitude_evaluation['source_value'],
                      'reference': configuration.amplitude_reference, 'reference_units': amplitude_input.units,
                      'normalization': 'fixed_reference', 'normalized_excitation': amplitude.value,
                      'clipped': amplitude_evaluation['clipped'], 'selection_probability': 'not_used'},
        'rhythm': {'source': configuration.rhythm_source, 'source_feature': rhythm_input.id.to_dict(),
                   'mapping': _mapping_dict(rhythm_projector.mapping),
                   'gap_stretch_name': 'GAP_STRETCH=8/(2*pi)' if configuration.gap_time_scale == GAP_STRETCH else 'explicit_custom_musical_stretch',
                   'unbounded_interval_seconds': interval.value, 'scheduled_interval_seconds': scheduled.value,
                   'interval_limited': not math.isclose(interval.value, scheduled.value, abs_tol=0, rel_tol=0),
                   'limits_seconds': (configuration.minimum_interval_seconds, configuration.maximum_interval_seconds),
                   'scheduler_policy': 'at_most_one_event_per_observation_no_catchup',
                   'clock': anchor.to_dict(), 'physical_rate_claim': False,
                   'provenance': scheduled.provenance.to_dict()},
        'analysis': analysis_audit,
        'active_parameters': {path: feature.to_dict() for path, feature in routed.values.items()},
        'preparation_provenance': prepared.provenance.to_dict(),
        'prepared_excitation': {'event_id': prepared.excitation.event_id,
            'amplitude': prepared.excitation.strength, 'units': prepared.excitation.activity_units,
            'onset_seconds': prepared.excitation.onset_seconds, 'duration_seconds': prepared.excitation.duration_seconds,
            'target_frequency_hz': prepared.excitation.target_frequency_hz},
    }
    return LiveRoutingResult(prepared, rhythm, float(interval.value), float(scheduled.value),
        frame, analysis, plain(audit), configuration.digest)


__all__ = ['LiveRoutingConfig', 'LiveRoutingResult', 'route_live_event', 'analyze_live_snapshot',
           'AMPLITUDE_SOURCES', 'RHYTHM_SOURCES', 'QUANTIZATIONS', 'ANALYSIS_BASES']
