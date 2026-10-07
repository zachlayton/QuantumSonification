"""One selected physical/derived feature to declared musical timing.

This observer does not select transitions, integrate current, sample lifetimes,
or evolve a state. Native TransitionEngine, flux-event and decay owners supply
the features. A gap's inverse frequency is a *musical period mapping*, never a
prediction of a stochastic waiting time.

Use ``RhythmProjector(MappingSpec(..., operation='rhythm', input_ids=(id,),
output_units='s', normalization='none', parameters={...}))``. Required options:

* All sources: ``input_units=(unit,)``. ``time_scale`` is a positive musical
  time stretch, default 1; it is distinct from ``source_seconds_per_unit``.
* energy_gap: energy_constant_kind ('h' or 'hbar'), energy_constant,
  energy_constant_unit ('<input unit>*<source_time_unit>'), source_time_unit,
  source_seconds_per_unit, frequency_convention ('Hz' for h, 'angular' for
  hbar). T = h/abs(gap) = 2*pi*hbar/abs(gap), followed by time stretch.
* signed_order: base_interval_seconds and explicit order_policy='power_of_two'
  (T=base*2**(-alpha)), 'positive_only', or 'negative_only' (T=base/abs(alpha)
  on the selected sign). absolute_order uses T=base/abs(alpha).
* decay_lifetime: source_seconds_per_unit. A lifetime is a mapped duration;
  no random decay event is generated.
* event_timestamp, flux_event_timestamp, decay_event_time, collider_event_time:
  input_clock={unit,domain,semantics,origin}, source_origin_value and
  source_seconds_per_unit. The scalar must equal its provenance ClockStamp
  value. Incidental arrival time is rejected. Proper and lab clocks remain
  distinct; conversion is never inferred from event sequence or metadata.

Quantization is 'continuous' (default), 'lattice' (positive
lattice_quantum_seconds; nearest, half ties upward), or 'ratio' (positive
base_interval_seconds and explicit positive ratios; nearest logarithm, ties
choose the smaller ratio). For timestamp sources quantization applies to the
offset from the declared source origin, preserving simultaneous onsets. For
other sources it applies to the mapped interval. Sequence timestamp intervals
are differences of final musical onsets and retain both source records.

``project`` requires an explicit musical onset anchor. ``project_sequence``
uses the same anchor for timestamp mapping, or accumulates intervals otherwise.
Zero energy gaps/orders emit inactive events with no interval. Missing/censored
timing and nonfinite/invalid inputs reject; they never become zero timing.
``as_feature`` exposes active intervals for an explicit router identity route.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math

import numpy as np

from .contracts import (
    ClockStamp, FeatureId, FeatureValue, MappingSpec, RhythmEvent, RhythmFrame,
    finite, nonempty,
)


_TIMESTAMPS = frozenset({
    'event_timestamp', 'flux_event_timestamp', 'decay_event_time', 'collider_event_time',
})
_SOURCES = _TIMESTAMPS | {'energy_gap', 'signed_order', 'absolute_order', 'decay_lifetime'}
_COMMON = {'input_units', 'time_scale', 'quantization'}
_ENERGY = {'energy_constant_kind', 'energy_constant', 'energy_constant_unit',
           'source_time_unit', 'source_seconds_per_unit', 'frequency_convention'}
_TIME_FACTORS = {'s': 1., 'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9, 'ps': 1e-12, 'fs': 1e-15}


def _positive(value, name):
    try:
        number = finite(value, name)
    except (TypeError, OverflowError) as exc:
        raise ValueError(f'{name} requires a finite numeric value') from exc
    if number <= 0:
        raise ValueError(f'{name} must be positive')
    return number


def _scalar(feature):
    raw = np.asarray(feature.require_available())
    if raw.ndim != 0 or raw.dtype.kind not in 'iuf':
        raise ValueError('rhythm source must be a finite real scalar, not an array/boolean')
    return finite(raw.item(), 'rhythm source value')


def _seconds_factor(unit, factor):
    number = _positive(factor, 'source_seconds_per_unit')
    if unit in _TIME_FACTORS and not math.isclose(number, _TIME_FACTORS[unit], rel_tol=1e-12, abs_tol=0):
        raise ValueError('source_seconds_per_unit contradicts the declared time unit')
    return number


def _anchor(value):
    if not isinstance(value, ClockStamp) or value.domain != 'musical' or value.unit != 's' or value.value is None:
        raise ValueError('an available musical onset anchor in seconds is required')
    return value


class RhythmProjector:
    """Deterministic, synthesis-free projector configured by a shared mapping."""

    def __init__(self, mapping: MappingSpec):
        if not isinstance(mapping, MappingSpec) or mapping.operation != 'rhythm':
            raise ValueError('RhythmProjector requires a declared rhythm MappingSpec')
        if len(mapping.input_ids) != 1 or mapping.input_ids[0].kind != 'scalar':
            raise ValueError('rhythm requires exactly one selected scalar source')
        if mapping.output_units != 's' or mapping.normalization != 'none':
            raise ValueError('rhythm outputs musical seconds without data normalization')
        self.source_id = mapping.input_ids[0]
        self.source_kind = self.source_id.quantity
        if self.source_kind not in _SOURCES:
            raise ValueError(f'unsupported rhythm source quantity: {self.source_kind}')
        p = dict(mapping.parameters)
        units = p.get('input_units')
        if not isinstance(units, tuple) or len(units) != 1:
            raise ValueError('input_units must declare exactly one source unit')
        nonempty(units[0], 'input unit')
        allowed = set(_COMMON)
        quantization = p.setdefault('quantization', 'continuous')
        if quantization == 'lattice':
            allowed.add('lattice_quantum_seconds')
            p['lattice_quantum_seconds'] = _positive(p.get('lattice_quantum_seconds'), 'lattice_quantum_seconds')
        elif quantization == 'ratio':
            allowed.update({'base_interval_seconds', 'ratios'})
            ratios = p.get('ratios')
            if not isinstance(ratios, tuple) or not ratios:
                raise ValueError('ratio mapping requires an explicit nonempty ratio tuple')
            p['ratios'] = tuple(sorted(_positive(r, 'ratio') for r in ratios))
            if len(set(p['ratios'])) != len(p['ratios']):
                raise ValueError('ratio entries must be distinct')
            p['base_interval_seconds'] = _positive(p.get('base_interval_seconds'), 'base_interval_seconds')
        elif quantization != 'continuous':
            raise ValueError('unknown rhythm quantization')
        p['time_scale'] = _positive(p.get('time_scale', 1.), 'time_scale')
        if self.source_kind == 'energy_gap':
            allowed.update(_ENERGY)
            kind = p.get('energy_constant_kind')
            if kind not in ('h', 'hbar'):
                raise ValueError('energy conversion requires explicitly declared h or hbar')
            convention = 'Hz' if kind == 'h' else 'angular'
            if p.get('frequency_convention') != convention:
                raise ValueError('h gives Hz; hbar gives angular frequency: declare the correct convention')
            p['energy_constant'] = _positive(p.get('energy_constant'), 'energy_constant')
            nonempty(p.get('source_time_unit'), 'source_time_unit')
            if p.get('energy_constant_unit') != f'{units[0]}*{p["source_time_unit"]}':
                raise ValueError('energy constant unit must match source energy and time units')
            p['source_seconds_per_unit'] = _seconds_factor(p['source_time_unit'], p.get('source_seconds_per_unit'))
        elif self.source_kind in ('signed_order', 'absolute_order'):
            allowed.add('base_interval_seconds')
            p['base_interval_seconds'] = _positive(p.get('base_interval_seconds'), 'base_interval_seconds')
            if units[0] not in ('index', '1'):
                raise ValueError('transition order requires index or dimensionless units')
            if self.source_kind == 'signed_order':
                allowed.add('order_policy')
                if p.get('order_policy') not in ('power_of_two', 'positive_only', 'negative_only'):
                    raise ValueError('signed order requires an explicit directional order_policy')
        elif self.source_kind == 'decay_lifetime':
            allowed.add('source_seconds_per_unit')
            p['source_seconds_per_unit'] = _seconds_factor(units[0], p.get('source_seconds_per_unit'))
        else:
            allowed.update({'input_clock', 'source_origin_value', 'source_seconds_per_unit'})
            clock = p.get('input_clock')
            if not isinstance(clock, Mapping) or set(clock) != {'unit', 'domain', 'semantics', 'origin'}:
                raise ValueError('timing requires an explicit input_clock unit/domain/semantics/origin')
            for key in clock:
                nonempty(clock[key], f'input_clock.{key}')
            if clock['unit'] != units[0]:
                raise ValueError('timing scalar and declared clock units must agree')
            if clock['semantics'] in ('unavailable', 'arrival', 'sequence', 'index') or clock['domain'] in ('arrival', 'ingestion', 'sequence', 'index'):
                raise ValueError('arrival/index clocks do not supply physical event timing')
            if 'source_origin_value' not in p:
                raise ValueError('source_origin_value must be explicitly declared')
            p['source_origin_value'] = finite(p['source_origin_value'], 'source_origin_value')
            p['source_seconds_per_unit'] = _seconds_factor(units[0], p.get('source_seconds_per_unit'))
        if set(p) - allowed:
            raise ValueError(f'unknown or inapplicable rhythm parameters: {sorted(set(p) - allowed)}')
        self.mapping = MappingSpec(mapping.mapping_id, mapping.version, mapping.operation,
            mapping.input_ids, mapping.output_units, mapping.normalization, p)

    def _quantize(self, seconds, *, allow_zero=False):
        p = self.mapping.parameters
        seconds = finite(seconds, 'mapped seconds', minimum=0)
        if seconds == 0:
            if allow_zero:
                return 0.
            raise ValueError('active rhythm interval underflowed to zero')
        if p['quantization'] == 'continuous':
            return seconds
        if p['quantization'] == 'lattice':
            quantum = p['lattice_quantum_seconds']
            ticks = finite(seconds / quantum, 'lattice tick count', minimum=0)
            count = math.floor(ticks + .5)
            return finite(max(0 if allow_zero else 1, count) * quantum, 'quantized seconds')
        base = p['base_interval_seconds']
        chosen = min(p['ratios'], key=lambda r: (abs(math.log(seconds) - math.log(base) - math.log(r)), r))
        return _positive(base * chosen, 'quantized seconds')

    def _energy_metadata_check(self, provenance):
        """Do not silently contradict the native model's declared hbar."""
        p = self.mapping.parameters
        hbar = p['energy_constant'] / (math.tau if p['energy_constant_kind'] == 'h' else 1.)
        hbar_seconds = _positive(hbar * p['source_seconds_per_unit'], 'mapped hbar in energy*seconds')
        energy_prefix = p['input_units'][0] + '*'
        pending = [provenance]
        while pending:
            node = pending.pop()
            declared = node.parameters
            declared_unit = declared.get('hbar_unit', '')
            if 'hbar' in declared and isinstance(declared_unit, str) and declared_unit.startswith(energy_prefix):
                declared_time = declared_unit[len(energy_prefix):]
                if declared_time == p['source_time_unit']:
                    factor = p['source_seconds_per_unit']
                elif declared_time in _TIME_FACTORS:
                    factor = _TIME_FACTORS[declared_time]
                else:
                    raise ValueError('cannot compare source hbar across an undeclared source time conversion')
                declared_seconds = _positive(declared['hbar'], 'source hbar') * factor
                if not math.isclose(hbar_seconds, declared_seconds, rel_tol=1e-10, abs_tol=0):
                    raise ValueError('rhythm energy constant contradicts source model hbar')
            pending.extend(node.parents)

    def project(self, feature: FeatureValue, event_id: str, onset_anchor: ClockStamp) -> RhythmEvent:
        nonempty(event_id, 'event_id')
        onset_anchor = _anchor(onset_anchor)
        if not isinstance(feature, FeatureValue) or feature.id != self.source_id:
            raise ValueError('feature must exactly match the selected typed rhythm source')
        if feature.units != self.mapping.parameters['input_units'][0]:
            raise ValueError('feature units differ from declared rhythm input_units')
        value = _scalar(feature)
        p = self.mapping.parameters
        active, interval, onset = True, None, onset_anchor
        evaluation = {'source_value': value}
        if self.source_kind == 'energy_gap':
            self._energy_metadata_check(feature.provenance)
            gap = abs(value)
            evaluation['absolute_energy_gap'] = gap
            if gap == 0:
                active = False
                evaluation['inactive_reason'] = 'zero_energy_gap'
            else:
                native_frequency = gap / p['energy_constant']
                frequency_per_second = _positive(native_frequency / p['source_seconds_per_unit'], 'converted frequency')
                multiplier = math.tau if p['energy_constant_kind'] == 'hbar' else 1.
                interval = multiplier / frequency_per_second * p['time_scale']
                evaluation.update(frequency_value=frequency_per_second,
                    frequency_units='rad/s' if multiplier == math.tau else 'Hz')
        elif self.source_kind in ('signed_order', 'absolute_order'):
            if value != math.trunc(value):
                raise ValueError('transition order must be an integer in the declared sequence ordering')
            if self.source_kind == 'absolute_order' and value < 0:
                raise ValueError('absolute transition order cannot be negative')
            if value == 0:
                active = False
                evaluation['inactive_reason'] = 'zero_transition_order'
            elif self.source_kind == 'signed_order' and p['order_policy'] == 'power_of_two':
                try:
                    interval = math.ldexp(p['base_interval_seconds'], -int(value)) * p['time_scale']
                except (OverflowError, TypeError) as exc:
                    raise ValueError('signed-order mapping exceeds finite interval range') from exc
            else:
                excluded = (self.source_kind == 'signed_order' and
                    ((p['order_policy'] == 'positive_only' and value < 0) or
                     (p['order_policy'] == 'negative_only' and value > 0)))
                if excluded:
                    active = False
                    evaluation['inactive_reason'] = 'order_direction_excluded'
                else:
                    interval = p['base_interval_seconds'] / abs(value) * p['time_scale']
        elif self.source_kind == 'decay_lifetime':
            interval = _positive(value, 'decay lifetime') * p['source_seconds_per_unit'] * p['time_scale']
        else:
            clock = feature.provenance.clock
            if clock.value is None or any(getattr(clock, k) != v for k, v in p['input_clock'].items()):
                raise ValueError('source timing clock differs from the declared input clock')
            if value != clock.value:
                raise ValueError('timing scalar must match the actual event clock, not an unrelated arrival clock')
            elapsed = finite((value - p['source_origin_value']) * p['source_seconds_per_unit'] * p['time_scale'],
                             'source-relative musical offset', minimum=0)
            offset = self._quantize(elapsed, allow_zero=True)
            onset = ClockStamp(finite(onset_anchor.value + offset, 'mapped onset'), 's', 'musical',
                               onset_anchor.semantics, onset_anchor.origin)
            evaluation.update(unquantized_seconds=elapsed, quantized_seconds=offset,
                              quantization_target='source_origin_relative_onset')
        if interval is not None:
            evaluation['unquantized_seconds'] = interval
            interval = self._quantize(interval)
            evaluation.update(quantized_seconds=interval, quantization_target='interval')
        interpretation = ('musical_period_mapping_not_physical_waiting_time' if self.source_kind == 'energy_gap'
                          else 'declared_downstream_timing_mapping')
        params = {'mapping_id': self.mapping.mapping_id, 'mapping_version': self.mapping.version,
            'selected_source': feature.id.to_dict(), 'configuration': dict(p),
            'input_units': feature.units, 'input_clock': feature.provenance.clock.to_dict(),
            'onset_anchor': onset_anchor.to_dict(), 'evaluation': evaluation,
            'interpretation': interpretation, 'source_uncertainty': feature.uncertainty,
            'uncertainty_policy': 'source_retained_not_propagated', 'active': active}
        provenance = feature.provenance.derive(event_id + ':rhythm', 'qmw.rhythm.project',
            self.mapping.version, params, units='s', normalization='none', clock=onset,
            source_path='rhythm.timing', evidence='musical_mapping')
        return RhythmEvent(event_id, onset, interval, feature.id, provenance, active)

    def project_sequence(self, features: Sequence[FeatureValue], frame_id: str,
                         event_ids: Sequence[str], onset_anchor: ClockStamp) -> RhythmFrame:
        nonempty(frame_id, 'frame_id')
        features, event_ids = tuple(features), tuple(event_ids)
        if not features or len(features) != len(event_ids) or len(set(event_ids)) != len(event_ids):
            raise ValueError('sequence requires nonempty features and one unique event ID each')
        onset_anchor = _anchor(onset_anchor)
        events = []
        next_anchor = onset_anchor
        previous = None
        for feature, event_id in zip(features, event_ids):
            event = self.project(feature, event_id, next_anchor)
            if self.source_kind in _TIMESTAMPS:
                if previous is not None:
                    if _scalar(feature) < _scalar(previous):
                        raise ValueError('timestamp sequence must be nondecreasing in one clock')
                    interval = finite(event.onset.value - events[-1].onset.value, 'mapped event difference', minimum=0)
                    params = dict(event.provenance.parameters)
                    params.update(interval_operation='difference_of_mapped_onsets',
                        previous_source_record_id=previous.provenance.record_id,
                        previous_onset=events[-1].onset.to_dict(), previous_source_value=_scalar(previous))
                    prov = feature.provenance.derive(event.provenance.record_id, 'qmw.rhythm.timestamp_difference',
                        self.mapping.version, params, units='s', clock=event.onset, normalization='none',
                        parents=(previous.provenance, feature.provenance), source_path='rhythm.timing', evidence='musical_mapping')
                    event = RhythmEvent(event.event_id, event.onset, interval, event.source_feature, prov, event.active)
            else:
                if events:
                    params = dict(event.provenance.parameters)
                    params.update(onset_operation='accumulate_previous_mapped_interval',
                                  previous_rhythm_event_id=events[-1].event_id)
                    prov = feature.provenance.derive(event.provenance.record_id, 'qmw.rhythm.accumulated_schedule',
                        self.mapping.version, params, units='s', clock=event.onset, normalization='none',
                        parents=(events[-1].provenance, feature.provenance), source_path='rhythm.timing', evidence='musical_mapping')
                    event = RhythmEvent(event.event_id, event.onset, event.interval_seconds, event.source_feature, prov, event.active)
                if event.active:
                    next_anchor = ClockStamp(finite(next_anchor.value + event.interval_seconds, 'next onset'),
                        's', 'musical', onset_anchor.semantics, onset_anchor.origin)
            events.append(event)
            previous = feature
        provenance = events[0].provenance.derive(frame_id, 'qmw.rhythm.sequence', self.mapping.version,
            {'mapping_id': self.mapping.mapping_id, 'event_ids': event_ids,
             'schedule': 'source_clock_onsets' if self.source_kind in _TIMESTAMPS else 'accumulated_mapped_intervals'},
            parents=tuple(e.provenance for e in events), clock=onset_anchor, units='s',
            source_path='rhythm.frame', normalization='none', evidence='musical_mapping')
        return RhythmFrame(frame_id, tuple(events), self.mapping.mapping_id, provenance)

    def as_feature(self, event: RhythmEvent, path='rhythm.interval') -> FeatureValue:
        """Publish the declared interval for a separate SonificationRouter route."""
        if not isinstance(event, RhythmEvent) or not event.active or event.interval_seconds is None:
            raise ValueError('only active, available mapped intervals may be routed')
        if (event.source_feature != self.source_id or
                event.provenance.parameters.get('mapping_id') != self.mapping.mapping_id or
                event.provenance.parameters.get('mapping_version') != self.mapping.version or
                event.provenance.parameters.get('configuration') != self.mapping.parameters):
            raise ValueError('rhythm event was produced by a different mapping/source')
        return FeatureValue(FeatureId(path, 'rhythm_interval'), event.interval_seconds, event.provenance)
