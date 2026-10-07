"""Adapters around approved 001A/001B and frozen decay sources, never generators.

External local implementations are mandatory and fingerprint checked. Kinematics
do not produce spin states; source entries and sequence numbers are not clocks.
Signed statistical weights retain their declared units and estimator meaning.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
from pathlib import Path

import numpy as np

from .contracts import (
    BackendCapabilities, BasisMetadata, ClockStamp, ExecutionRequest, ExecutionResult,
    FeatureFrame, FeatureId, FeatureValue, Provenance, nonempty,
)
from .upstream import load_collider_runtime, load_decay_runtime


def _collider_runtime(runtime):
    approved = load_collider_runtime()
    if runtime is not None and (getattr(runtime, 'root', None) != approved.root
            or any(getattr(runtime, name, None) is not getattr(approved, name)
                   for name in ('model', 'io', 'backend', 'spectrum'))):
        raise ValueError('runtime must be the actual approved collider source handoff')
    return approved


def _decay_runtime(runtime):
    approved = load_decay_runtime()
    if runtime is not None and (getattr(runtime, 'archive', None) != approved.archive
            or getattr(runtime, 'sha256', None) != approved.sha256
            or any(getattr(runtime, name, None) is not getattr(approved, name)
                   for name in ('contracts', 'validation', 'admission'))):
        raise ValueError('runtime must be the actual frozen decay source handoff')
    return approved


def _check_input(path, digest):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'loaded input unavailable: {path}')
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f'loaded input changed: {path}; explicitly reload the source')


def _feature(root, path, quantity, value, units, *, operation='source_field_adapter',
             parameters=None, parents=None, kind='scalar', availability='available',
             reason=None, uncertainty=None, basis=None, evidence='derived'):
    p = root.derive(root.record_id + ':' + path, operation, parameters=parameters or {},
        units=units, normalization='none', parents=parents, source_path=path,
        basis=basis, evidence=evidence)
    return FeatureValue(FeatureId(path, quantity, kind), value, p, availability=availability,
                        reason=reason, uncertainty=uncertainty)


class ColliderFeatureAdapter:
    """Offline recorded-source backend over the actual 001A/001B implementation."""

    @classmethod
    def from_json(cls, *, event_path, weight_unit, weight_meaning, runtime=None,
                  edges_gev=None, state_path=None):
        if weight_unit not in ('1', 'pb'):
            raise ValueError('weight_unit must explicitly be 1 or pb, never probability/amplitude')
        nonempty(weight_meaning, 'weight_meaning')
        r = _collider_runtime(runtime)
        dataset = r.io.load_dataset(event_path)
        edges = r.backend.DEFAULT_EDGES_GEV if edges_gev is None else edges_gev
        kinematics = r.backend.ColliderBackend(dataset, edges)
        states = None if state_path is None else r.spectrum.load_states(state_path, kinematics)
        spectral = None if states is None else r.spectrum.ColliderSpectralBackend(kinematics, states)
        result = cls()
        result.runtime, result.kinematics, result.states, result.spectral = r, kinematics, states, spectral
        result.weight_unit, result.weight_meaning = weight_unit, weight_meaning
        result._events = {event.event_id: event for event in dataset.events}
        result._summary = kinematics.summary()
        provenance = asdict(dataset.provenance)
        basis = BasisMetadata('collider_001a.kinematics', 0, 'classical_kinematics', 'not_applicable',
                              'source_entry_zero_based', details={'units': dict(r.model.UNITS)})
        clock = ClockStamp(None, 's', 'event_acquisition', 'unavailable', dataset.provenance.dataset_id)
        result._source = Provenance(dataset.provenance.dataset_id + ':' + dataset.input_sha256,
            'collider.dataset', 'collider_001a.JsonEventLoader', '1',
            {'source_provenance': provenance, 'input_path': dataset.input_path,
             'input_sha256': dataset.input_sha256, 'runtime_root': r.root,
             'runtime_fingerprints': dict(r.fingerprints), 'units': dict(r.model.UNITS),
             'weight_unit': weight_unit, 'weight_meaning': weight_meaning,
             'time_limit': '001A has source indices, not acquisition or decay timestamps'},
            'mixed', 'none', basis, clock, 'collider_001a.recorded', dataset.provenance.source_kind)
        result._state_source = None
        if states is not None:
            state_basis = BasisMetadata('collider_001b.two_spin', 4, 'computational', 'q0_lsb',
                '00,01,10,11', details={'source_basis': states.basis,
                    'tensor_factors_msb_to_lsb': ('top', 'antitop'),
                    'logical_subsystems_q0_first': ('antitop', 'top'),
                    'spin_axis_calibration': 'not supplied by the 001B contract; retain basis description'})
            state_clock = ClockStamp(None, 's', 'ensemble_state_acquisition', 'unavailable', states.provenance['source_uri'])
            result._state_source = Provenance(states.input_sha256, 'collider.state_table',
                'collider_001b.load_states', '1',
                {'state_provenance': states.provenance, 'basis': states.basis,
                 'input_path': states.input_path, 'input_sha256': states.input_sha256,
                 'event_input_sha256': states.event_input_sha256, 'event_dataset_id': states.event_dataset_id,
                 'edges_gev': states.edges_gev, 'runtime_fingerprints': dict(r.fingerprints),
                 'independently_supplied': True, 'kinematics_to_density': False},
                '1', 'source_trace_one', state_basis, state_clock, 'collider_001b.recorded', states.provenance['source_kind'])
        available = {'collider.event.source_entry', 'collider.event.mass', 'collider.event.weight',
            'collider.ensemble.count', 'collider.ensemble.event_fraction', 'collider.ensemble.sum_weights',
            'collider.ensemble.sum_weights_squared', 'collider.ensemble.mean_mass', 'collider.ensemble.std_mass'}
        if any(event.top is not None for event in dataset.events):
            available |= {'collider.event.top_momentum', 'collider.event.antitop_momentum'}
        usable_states = states is not None and any(spectral.frame(i)['status'] == 'ready' for i in states.states)
        if usable_states:
            available |= {'collider.ensemble.rho', 'collider.ensemble.density_eigenvalues', 'collider.ensemble.state_validation'}
        state_access = ('recorded' if states.provenance['source_kind'] == 'test_fixture' else 'estimated') if usable_states else 'none'
        result.capabilities = BackendCapabilities('collider_001a_001b.recorded', 'recorded',
            frozenset({'event_frame', 'ensemble_frame'}), frozenset(available), state_access,
            'q0_lsb_for_independent_two_spin_state_only',
            {'event_source_kind': dataset.provenance.source_kind,
             'external_local_runtime_required': r.root, 'per_frame_availability_must_be_checked': True,
             'event_rho_available': False, 'timing_available': False, 'spin_axis_calibration_available': False,
             'state_source_kind': None if states is None else states.provenance['source_kind']})
        return result

    def _verify(self):
        _collider_runtime(self.runtime)
        _check_input(self.kinematics.dataset.input_path, self.kinematics.dataset.input_sha256)
        if self.states is not None:
            _check_input(self.states.input_path, self.states.input_sha256)

    def event_frame(self, event_id) -> FeatureFrame:
        self._verify()
        if not isinstance(event_id, str) or event_id not in self._events:
            raise KeyError(f'unknown event_id {event_id!r}')
        event = self._events[event_id]
        root = self._source.derive(self._source.record_id + ':event:' + event_id, 'select_recorded_event',
            parameters={'event_id': event_id, 'source_entry': event.source_entry,
                        'source_entry_semantics': 'zero-based entry index, not time'})
        features = [
            _feature(root, 'collider.event.source_entry', 'source_entry_index', event.source_entry, 'index'),
            _feature(root, 'collider.event.weight', 'signed_statistical_weight', event.weight, self.weight_unit,
                parameters={'meaning': self.weight_meaning, 'is_probability': False, 'is_audio_amplitude': False}),
        ]
        momenta = []
        for name, vector in (('top', event.top), ('antitop', event.antitop)):
            momentum = _feature(root, f'collider.event.{name}_momentum', 'four_momentum',
                None if vector is None else tuple(asdict(vector).values()), 'GeV', kind='vector',
                parameters={'component_order': ('E', 'px', 'py', 'pz'), 'natural_units': 'c=1', 'metric': '+---',
                            'uncertainty': 'not supplied by 001A schema'},
                availability='missing' if vector is None else 'available',
                reason='dataset supplies mass only; parent four-momentum was not supplied' if vector is None else None)
            features.append(momentum)
            momenta.append(momentum)
        parents = tuple(f.provenance for f in momenta) if event.top is not None else (root,)
        features.append(_feature(root, 'collider.event.mass', 'invariant_mass', event.mass_gev, 'GeV',
            operation='collider_001a.invariant_mass' if event.top is not None else 'read_dataset_mass', parents=parents,
            parameters={'mass_source': event.mass_source, 'formula': 'sqrt((E_t+E_tbar)^2-|p_t+p_tbar|^2)',
                        'natural_units': 'c=1', 'metric': '+---'}))
        for suffix, quantity, kind, status, reason in (
            ('time', 'collider_event_time', 'scalar', 'missing', '001A contains source_entry indices, no experimental event timestamp'),
            ('decay_graph', 'particle_decay_graph', 'record', 'missing', '001A contains parent kinematics only, no daughter/vertex graph'),
            ('spin', 'spin_polarization', 'record', 'missing', 'no spin or polarization estimates supplied'),
            ('rho', 'density_matrix', 'matrix', 'unsupported', 'event kinematics do not determine rho; supplied 001B states are ensemble quantities'),
        ):
            features.append(_feature(root, 'collider.event.' + suffix, quantity, None,
                's' if suffix == 'time' else '1', kind=kind, availability=status, reason=reason))
        return FeatureFrame(root.record_id, tuple(features),
            {'level': 'event', 'event_id': event_id, 'source_entry': event.source_entry,
             'source_kind': self.kinematics.dataset.provenance.source_kind, 'mass_source': event.mass_source,
             'source_input_sha256': self.kinematics.dataset.input_sha256, 'timing': 'unavailable'})

    def ensemble_frame(self, bin_index) -> FeatureFrame:
        self._verify()
        phase = self.kinematics.select_bin(bin_index)
        selected_events = self.kinematics.selected_events()
        spectral = None if self.spectral is None else self.spectral.frame(bin_index)
        status = spectral['status'] if spectral is not None else ('empty_bin' if phase.statistics.count == 0 else 'missing_state')
        root = self._source.derive(self._source.record_id + f':bin:{bin_index}', 'collider_001a.ColliderBackend.select_bin',
            parameters={'bin_index': bin_index, 'low_gev': phase.low_gev, 'high_gev': phase.high_gev,
                'includes_upper_edge': phase.includes_upper_edge, 'bin_convention': self.runtime.backend.BIN_CONVENTION,
                'event_ids': tuple(e.event_id for e in selected_events),
                'source_entries': tuple(e.source_entry for e in selected_events),
                'statistics_convention': self._summary['statistics_convention']})
        s = phase.statistics
        features = []
        for suffix, quantity, value, unit in (
            ('count', 'event_count', s.count, 'count'),
            ('event_fraction', 'unweighted_event_fraction', s.fraction_of_all_events, '1'),
            ('sum_weights', 'signed_statistical_weight_sum', s.sum_weights, self.weight_unit),
            ('sum_weights_squared', 'squared_statistical_weight_sum', s.sum_weights_squared, self.weight_unit + '^2'),
            ('mean_mass', 'unweighted_mean_mass', s.mean_mass_gev, 'GeV'),
            ('std_mass', 'unweighted_population_mass_std', s.std_mass_gev, 'GeV'),
        ):
            features.append(_feature(root, 'collider.ensemble.' + suffix, quantity, value, unit,
                operation='collider_001a.BinStatistics',
                parameters={'weight_meaning': self.weight_meaning, 'fraction_denominator': len(self.kinematics.dataset.events),
                            'std_semantics': 'population dispersion, not a standard error'},
                availability='missing' if value is None else 'available',
                reason='empty mass bin has no mass samples' if value is None else None))
        if status == 'ready':
            raw = spectral['spectrum']
            rho = np.array(raw['rho_real']) + 1j * np.array(raw['rho_imag'])
            diagnostics = {k: raw[k] for k in ('hermiticity_error', 'trace_error', 'minimum_raw_eigenvalue', 'roundoff_correction_frobenius')}
            params = {'bin_index': bin_index, 'state_label': spectral['state_label'],
                      'state_provenance': self.states.provenance, 'validation': diagnostics,
                      'validation_tolerance': self.runtime.spectrum.TOLERANCE,
                      'correction_policy': 'actual 001B tolerance-sized Hermitian/PSD/trace cleanup; correction reported',
                      'kinematics_to_density': False, 'independently_supplied': True}
            p = self._state_source.derive(self._state_source.record_id + f':bin:{bin_index}',
                'collider_001b.ColliderSpectralBackend.frame', parameters=params,
                parents=(self._state_source, root), evidence=self.states.provenance['source_kind'])
            uncertainty = {'kind': 'textual_source_report', 'description': self.states.provenance['uncertainty'],
                           'numeric_covariance': None}
            features.extend((
                _feature(p, 'collider.ensemble.rho', 'density_matrix', rho, '1', kind='matrix',
                    operation='collider_001b.validate_density_matrix', parameters=params, uncertainty=uncertainty,
                    evidence=self.states.provenance['source_kind']),
                _feature(p, 'collider.ensemble.density_eigenvalues', 'density_eigenvalues', raw['eigenvalues'], '1', kind='vector',
                    parameters={'ordering': 'descending eigenvalue ranks; no eigenvector identity tracking'}),
                _feature(p, 'collider.ensemble.state_validation', 'density_validation_diagnostics', diagnostics, 'mixed', kind='record'),
            ))
        else:
            availability = 'not_applicable' if status == 'empty_bin' else 'missing'
            reason = 'empty bin: supplied states are not admitted for sonification' if status == 'empty_bin' else 'no independently supplied density matrix for this mass bin'
            for suffix, quantity, kind in (('rho', 'density_matrix', 'matrix'),
                    ('density_eigenvalues', 'density_eigenvalues', 'vector'),
                    ('state_validation', 'density_validation_diagnostics', 'record')):
                features.append(_feature(root, 'collider.ensemble.' + suffix, quantity, None, '1', kind=kind,
                    availability=availability, reason=reason))
        features.append(_feature(root, 'collider.ensemble.time', 'ensemble_acquisition_time', None, 's',
            availability='missing', reason='mass bin index does not specify acquisition or decay timing'))
        return FeatureFrame(root.record_id, tuple(features),
            {'level': 'ensemble', 'status': status, 'bin_index': bin_index,
             'source_kind': self.kinematics.dataset.provenance.source_kind,
             'state_source_kind': None if self.states is None else self.states.provenance['source_kind'],
             'underflow': self.kinematics.underflow, 'overflow': self.kinematics.overflow,
             'event_input_sha256': self.kinematics.dataset.input_sha256,
             'state_input_sha256': None if self.states is None else self.states.input_sha256})

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not isinstance(request, ExecutionRequest):
            raise TypeError('requires the shared ExecutionRequest')
        if request.operation not in self.capabilities.operations:
            raise ValueError('unsupported operation; this adapter performs offline reads only')
        if not request.required_features <= self.capabilities.available_features:
            raise ValueError('required features exceed available collider capabilities')
        field = 'event_id' if request.operation == 'event_frame' else 'bin_index'
        if set(request.payload) != {field}:
            raise ValueError(f'{request.operation} requires only {field}')
        frame = getattr(self, request.operation)(request.payload[field])
        for path in request.required_features:
            try:
                frame.get(path).require_available()
            except KeyError as exc:
                raise ValueError(f'required feature unavailable at this level: {path}') from exc
        available = tuple(f for f in frame.features if f.availability == 'available')
        p = self._source.derive(request.request_id + ':collider_result', 'offline_collider_execution',
            parameters={'request_id': request.request_id, 'operation': request.operation,
                        'frame_id': frame.frame_id}, parents=tuple(f.provenance for f in available))
        return ExecutionResult(request.request_id + ':result', request.request_id, self.capabilities, available, p,
            metadata={'frame_metadata': frame.metadata, 'request_timestamp': request.timestamp.to_dict(),
                      'unavailable_features': {f.id.path: f.reason for f in frame.features if f.availability != 'available'}})


class DecayFeatureAdapter:
    """Bounded session through actual frozen FrameAdmission; no production bypass."""

    def __init__(self, *, runtime=None, max_frames=10000, max_streams=32):
        self.runtime = _decay_runtime(runtime)
        self.admission = self.runtime.admission.FrameAdmission(max_frames=max_frames, max_streams=max_streams)
        self._parents = {}

    def process(self, frame) -> FeatureFrame:
        self.runtime = _decay_runtime(self.runtime)
        if not isinstance(frame, self.runtime.contracts.DecayFrame):
            raise TypeError('requires the actual frozen qmw_decay.contracts.DecayFrame')
        adapter = self
        class Sink:
            result = None
            root = None
            def accept(self, admitted):
                self.result, self.root = adapter._convert(admitted)
        sink = Sink()
        # Actual stage-one validation, duplicate/sequence checks, production
        # prohibition, and admission bounds all run before the adapter emits.
        self.admission.publish(frame, sink)
        self._parents[frame.frame_id] = sink.root
        return sink.result

    def _convert(self, frame):
        unresolved = tuple(parent for parent in frame.parent_frame_ids if parent not in self._parents)
        if unresolved:
            raise ValueError(f'parent frame provenance unavailable in this session: {unresolved}')
        if frame.record_kind == 'ensemble':
            t = frame.ensemble.proper_time
            clock = ClockStamp(t.value, t.unit, 'proper_time', 'elapsed', frame.provenance.source_id + ':model_origin')
        else:
            clock = ClockStamp(None, 's', 'event_acquisition', 'unavailable', frame.provenance.source_id)
        basis = BasisMetadata('qmw_decay.classical_record', 0, 'decay_record', 'not_applicable',
                              'declared_graph_node_and_vertex_ids')
        source = Provenance(frame.frame_id, 'decay.source_frame', 'qmw_decay.FrameAdmission', '1',
            {'legacy_provenance': asdict(frame.provenance), 'schema_version': frame.schema_version,
             'frame_sha256': hashlib.sha256(self.runtime.validation.to_json(frame).encode()).hexdigest(),
             'source_kind': frame.source_kind, 'record_kind': frame.record_kind,
             'evidence_level': frame.evidence_level, 'stream_id': frame.stream_id,
             'sequence': frame.sequence, 'sequence_semantics': 'record order, not time',
             'archive': self.runtime.archive, 'archive_sha256': self.runtime.sha256,
             'parent_frame_ids': frame.parent_frame_ids,
             'admission_limit': 'actual stage-one receiver rejects production simulation/collision_data'},
            'mixed', 'none', basis, clock, 'qmw_decay.frozen_stage1', frame.provenance.origin)
        root = source if not frame.parent_frame_ids else source.derive(frame.frame_id + ':lineage',
            'admitted_decay_with_resolved_parent_frames', parents=(source,) + tuple(self._parents[x] for x in frame.parent_frame_ids))
        features = []

        def quantity(path, q, quantity_name):
            availability = {'available': 'available', 'not_provided': 'missing',
                            'not_applicable': 'not_applicable', 'censored': 'censored'}[q.availability]
            uncertainty = None if q.uncertainty is None else {
                'kind': 'source_reported_numeric_uncertainty', 'value': q.uncertainty, 'units': q.unit,
                'definition': 'uncertainty convention unspecified by frozen Quantity contract'}
            f = _feature(root, path, quantity_name, q.value, q.unit,
                parameters={'source_availability': q.availability, 'quantity_origin': q.origin,
                            'method': q.method, 'source_quantity': asdict(q)},
                availability=availability, reason=q.reason, uncertainty=uncertainty)
            features.append(f)
            return f

        if frame.record_kind == 'ensemble':
            e = frame.ensemble
            proper = quantity('decay.ensemble.proper_time', e.proper_time, 'proper_evaluation_time')
            lifetime = quantity('decay.ensemble.mean_lifetime', e.mean_lifetime, 'decay_lifetime')
            quantity('decay.ensemble.width_energy', e.width_energy, 'decay_width_energy')
            for suffix, name, value, unit in (
                    ('survival_probability', 'survival_probability', e.survival_probability, '1'),
                    ('decay_density', 'decay_time_probability_density', e.decay_density_per_s, '1/s')):
                features.append(_feature(root, 'decay.ensemble.' + suffix, name, value, unit,
                    operation='admitted_constant_hazard_exponential_quantity',
                    parameters={'law': e.law, 'source_model_only': True},
                    parents=(proper.provenance, lifetime.provenance)))
            features.append(_feature(root, 'decay.ensemble.channels', 'decay_branch_table',
                {'channels': tuple(asdict(c) for c in e.channels), 'parent_pdg_id': e.parent_pdg_id,
                 'channel_semantics': e.channel_semantics, 'table_scope': e.table_scope,
                 'condition': e.condition, 'completeness': e.completeness,
                 'remainder_probability': e.remainder_probability}, '1', kind='record'))
        else:
            e = frame.event
            weight = quantity('decay.event.weight', e.weight, 'signed_statistical_weight')
            # Preserve estimator meaning directly at the typed weight node.
            features[-1] = FeatureValue(weight.id, weight.value,
                weight.provenance.derive(weight.provenance.record_id + ':meaning', 'declare_statistical_weight_meaning',
                    parameters={'weight_meaning': e.weight_meaning, 'is_probability': False, 'is_audio_amplitude': False}),
                availability=weight.availability, reason=weight.reason, uncertainty=weight.uncertainty)
            features.append(_feature(root, 'decay.event.graph', 'particle_decay_graph', asdict(e), 'mixed', kind='record',
                parameters={'topology': e.topology, 'event_id': e.event_id, 'selection_id': e.selection_id,
                            'record_kind': frame.record_kind, 'truth_vs_candidate_preserved': True}))
            for node in e.nodes:
                m = node.momentum
                uncertainty = None if m is None or m.covariance_ref is None else {
                    'kind': 'external_covariance_reference', 'reference': m.covariance_ref, 'matrix': None}
                features.append(_feature(root, f'decay.event.nodes.{node.node_id}.momentum', 'four_momentum',
                    None if m is None else m.components, 'GeV', kind='vector',
                    parameters={'node_id': node.node_id, 'pdg_id': node.pdg_id, 'node_kind': node.kind,
                                'source_ref': node.source_ref, 'momentum': None if m is None else asdict(m),
                                'component_order': ('E', 'px', 'py', 'pz'), 'natural_units': 'c=1'},
                    availability='missing' if m is None else 'available', reason=node.momentum_missing_reason,
                    uncertainty=uncertainty))
            for vertex in e.vertices:
                for name in ('proper_elapsed', 'lab_elapsed'):
                    quantity(f'decay.event.vertices.{vertex.vertex_id}.{name}', getattr(vertex, name), name)
            features.append(_feature(root, 'decay.event.time', 'decay_event_time', None, 's',
                availability='missing', reason='source frame has sequence/intervals but no acquisition timestamp'))
        return FeatureFrame(frame.frame_id + ':features', tuple(features),
            {'source_kind': frame.source_kind, 'record_kind': frame.record_kind,
             'evidence_level': frame.evidence_level, 'provenance_origin': frame.provenance.origin,
             'stream_id': frame.stream_id, 'sequence': frame.sequence, 'parent_frame_ids': frame.parent_frame_ids,
             'production_admission': 'prohibited by actual frozen stage-one receiver',
             'external_archive_sha256': self.runtime.sha256}), root
