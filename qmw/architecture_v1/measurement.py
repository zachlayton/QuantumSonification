"""Discrete simulated/observed measurements; state installation stays upstream.

The 16-state X/Y/Z path wraps the existing ProjectiveMeasurementInstrument,
after strict density validation. Its native tolerance repair is measured and
reported. Generic grouped Kraus operations implement an instrument:
Phi_a(rho)=sum_j K_aj rho K_aj^dagger, p(a)=Tr(Phi_a(rho)); conditional states
are Phi_a(rho)/p(a). Effects alone determine probabilities, not a unique state
update. Rectangular output spaces are not supported by this V1 adapter.

References: John Watrous, The Theory of Quantum Information, Section 2.3,
Definition 2.34 and equations 2.255–2.260:
https://cs.uwaterloo.ca/~watrous/TQI/TQI.pdf

All results use supervisor-owned MeasurementRecord. Source FeatureValues are
observed without mutation. A computed posterior is a candidate for an explicit
authority transaction; this module never installs it, publishes OSC, routes
sound, or treats a hardware count histogram as a sequence of real events.
"""
from __future__ import annotations

from collections.abc import Mapping
import copy

import numpy as np

from density.measurement_instrument_v1 import ProjectiveMeasurementInstrument, basis_unitary
from qmw.qmw_representation_laboratory_v4.core.state_transform import validate_density_matrix

from .contracts import BasisMetadata, FeatureId, FeatureValue, MeasurementRecord, finite, nonempty


_NATIVE = 'density.measurement_instrument_v1.ProjectiveMeasurementInstrument'
_SIMULATOR = 'numpy:measurement_simulator'


def _integer(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return int(value)


def _state(feature, tolerance):
    if not isinstance(feature, FeatureValue) or feature.id.quantity != 'density_matrix' or feature.id.kind != 'matrix':
        raise ValueError('measurement requires a typed density_matrix feature')
    value = feature.require_available()
    if feature.units not in ('1', 'dimensionless'):
        raise ValueError('density matrix must be dimensionless')
    state = validate_density_matrix(value, tolerance=tolerance)
    if state.shape[0] != feature.provenance.basis.dimension:
        raise ValueError('state dimension and declared coordinate basis disagree')
    return np.array(state, dtype=complex, copy=True)


def _operator(value, dimension):
    try:
        result = np.array(value, dtype=complex, copy=True)
    except (ValueError, TypeError) as exc:
        raise ValueError('measurement operators must be numeric matrices') from exc
    if result.shape != (dimension, dimension) or not np.all(np.isfinite(result)):
        raise ValueError('measurement operators must be finite square matrices in the state coordinates')
    return result


class MeasurementEngine:
    """Local measurement adapter; each draw has auditable RNG and provenance."""

    def __init__(self, seed=29, tolerance=1e-10):
        self.seed = _integer(seed, 'seed')
        self.tolerance = finite(tolerance, 'tolerance')
        if not 0 < self.tolerance <= 1e-6:
            raise ValueError('measurement tolerance must be positive and <=1e-6')
        self.projective_instrument = ProjectiveMeasurementInstrument(seed=self.seed)
        # Reuse one actual seeded generator, keeping mixed instrument sequences reproducible.
        self.rng = self.projective_instrument.rng

    def _rng_context(self):
        return {'algorithm': type(self.rng.bit_generator).__name__, 'seed': self.seed,
            'numpy_version': np.__version__, 'state_before': copy.deepcopy(self.rng.bit_generator.state),
            'replay_scope': 'full_generator_checkpoint', 'selection': 'numpy.random.Generator.choice'}

    def projective(self, rho_feature: FeatureValue, event_id: str, *, basis='Z', mode='collapse',
                   revision_before=0, request_id=0) -> MeasurementRecord:
        """Wrap the actual four-qubit instrument; do not install its posterior.

        Probe samples the Born distribution but does not compute a physical
        posterior. Only collapse mode returns the native posterior candidate.
        The original instrument's revision_after is a proposal, not evidence
        of a transaction on the authoritative state.
        """
        nonempty(event_id, 'event_id')
        state = _state(rho_feature, self.tolerance)
        source_basis = rho_feature.provenance.basis
        if state.shape != (16, 16):
            raise ValueError('the existing projective instrument requires 16-state/four-qubit rho')
        if source_basis.kind != 'computational' or source_basis.subsystem_order not in ('q0_lsb', 'q0_msb'):
            raise ValueError('native X/Y/Z measurement requires declared computational qubit coordinates/order')
        if not isinstance(basis, str) or basis.upper() not in ('X', 'Y', 'Z'):
            raise ValueError('projective basis must be X, Y, or Z')
        if mode not in ('probe', 'collapse'):
            raise ValueError('projective mode must be probe or collapse')
        revision_before, request_id = _integer(revision_before, 'revision_before'), _integer(request_id, 'request_id')
        clock = rho_feature.provenance.clock
        if clock.value is None:
            raise ValueError('native simulated projective measurement requires a declared logical clock value')
        axis = basis.upper()
        measured_basis = BasisMetadata(f'{source_basis.basis_id}:measurement:{axis}', 16,
            'product_projective', source_basis.subsystem_order, 'outcome_index_ascending',
            'native_basis_unitary', {'axis': axis, 'coordinate_basis': source_basis.to_dict(),
             'unitary_convention': 'apply_U_then_Z; columns_of_U_dagger_are_measurement_kets'})
        rng = self._rng_context()
        native = self.projective_instrument.measure(state, basis=axis, mode=mode,
            logical_time=clock.value, revision_before=revision_before, request_id=request_id)
        validate_density_matrix(native.rho_before, tolerance=self.tolerance)
        if mode == 'collapse':
            validate_density_matrix(native.rho_after, tolerance=self.tolerance)
        repair = float(np.linalg.norm(native.rho_before - state))
        metadata = {'native_instrument': _NATIVE, 'native_event_id': native.event_id,
            'request_id': request_id, 'source_revision_before': revision_before,
            'native_proposed_revision_after': native.revision_after,
            'state_installation': 'caller_authority_only', 'authority_state_mutated': False,
            'mode': mode, 'bitstring': native.bitstring,
            'bitstring_order': 'q3_q2_q1_q0' if source_basis.subsystem_order == 'q0_lsb' else 'q0_q1_q2_q3',
            'post_state_availability': 'computed_candidate' if mode == 'collapse' else 'not_computed_for_probe',
            'native_roundoff_correction_fro': repair,
            'input_validation': 'strict_existing_representation_validator_before_native_tolerance_repair',
            'tolerance': self.tolerance, 'rng': rng, 'selection': 'seeded_simulated_draw',
            'trace_distance': native.trace_distance,
            'probability_semantics': 'native_Born_probability_for_sampled_state'}
        provenance = rho_feature.provenance.derive(event_id, 'qmw.measurement.native_projective', '1',
            {**metadata, 'basis_unitary': basis_unitary(axis), 'outcome': native.outcome,
             'probability': native.probability, 'source_uncertainty': rho_feature.uncertainty},
            units='1', normalization='native_Born_probability_normalization', basis=measured_basis,
            backend=_SIMULATOR, source_path='measurement.projective', evidence='simulated_sample')
        return MeasurementRecord(event_id, rho_feature.provenance.record_id, 'projective',
            'simulated_sample', native.outcome, native.probability, measured_basis, clock,
            _SIMULATOR, provenance, native.rho_before, native.rho_after if mode == 'collapse' else None,
            1, metadata)

    def _analyze(self, rho_feature, measurement_feature):
        state = _state(rho_feature, self.tolerance)
        if (not isinstance(measurement_feature, FeatureValue) or measurement_feature.id.kind != 'record'
                or measurement_feature.id.quantity not in ('kraus_instrument', 'povm_effects')):
            raise ValueError('measurement definition must be a grouped kraus_instrument or povm_effects record')
        definition = measurement_feature.require_available()
        if not isinstance(definition, Mapping) or not definition:
            raise ValueError('measurement definition must contain named nonempty outcomes')
        if measurement_feature.units not in ('1', 'dimensionless') or measurement_feature.provenance.basis != rho_feature.provenance.basis:
            raise ValueError('measurement operators require dimensionless units and identical declared coordinates')
        labels, dimension = tuple(definition), state.shape[0]
        for label in labels:
            nonempty(label, 'outcome label')
        total = np.zeros_like(state)
        numerators, raw_probabilities, kraus_counts = [], [], {}
        is_instrument = measurement_feature.id.quantity == 'kraus_instrument'
        with np.errstate(over='ignore', invalid='ignore'):
            for label in labels:
                if is_instrument:
                    group = definition[label]
                    if not isinstance(group, tuple) or not group:
                        raise ValueError('each outcome requires a nonempty tuple of Kraus operators')
                    operators = tuple(_operator(k, dimension) for k in group)
                    effect = sum((k.conj().T @ k for k in operators), np.zeros_like(state))
                    numerator = sum((k @ state @ k.conj().T for k in operators), np.zeros_like(state))
                    probability = complex(np.trace(numerator))
                    kraus_counts[label] = len(operators)
                else:
                    effect = _operator(definition[label], dimension)
                    if not np.allclose(effect, effect.conj().T, atol=self.tolerance, rtol=0):
                        raise ValueError('POVM effects must be Hermitian')
                    if np.linalg.eigvalsh(effect).min() < -self.tolerance:
                        raise ValueError('POVM effects must be positive semidefinite')
                    numerator = None
                    probability = complex(np.trace(effect @ state))
                if not np.all(np.isfinite(effect)) or not np.isfinite(probability):
                    raise ValueError('measurement operation exceeded finite numerical range')
                if numerator is not None and not np.all(np.isfinite(numerator)):
                    raise ValueError('measurement posterior exceeded finite numerical range')
                if abs(probability.imag) > self.tolerance or probability.real < -self.tolerance or probability.real > 1 + self.tolerance:
                    raise ValueError('measurement produced an invalid Born probability')
                total += effect
                raw_probabilities.append(probability.real)
                numerators.append(numerator)
        if not np.allclose(total, np.eye(dimension), atol=self.tolerance, rtol=0):
            raise ValueError('measurement must be complete: sum_a E_a = sum_aj K_aj^dagger K_aj = I')
        raw = np.asarray(raw_probabilities, dtype=float)
        if abs(float(raw.sum()) - 1.) > self.tolerance * dimension:
            raise ValueError('Born probabilities must sum to one before numerical normalization')
        probabilities = np.clip(raw, 0., 1.)
        denominator = float(probabilities.sum())
        if denominator <= 0:
            raise ValueError('measurement has zero total probability')
        probabilities /= denominator
        diagnostics = {'outcome_labels': labels, 'raw_probabilities': raw,
            'sampling_probabilities': probabilities, 'probability_sum_before_normalization': float(raw.sum()),
            'numerical_normalization_denominator': denominator,
            'numerical_policy': 'clip_only_tolerance_roundoff_and_normalize_sampling_distribution',
            'completeness_residual_fro': float(np.linalg.norm(total - np.eye(dimension))),
            'kraus_counts': kraus_counts, 'tolerance': self.tolerance,
            'source_uncertainty': rho_feature.uncertainty, 'definition_uncertainty': measurement_feature.uncertainty,
            'uncertainty_policy': 'inputs_retained_not_propagated',
            'probability_formula': 'Tr(sum_j K_aj rho K_aj^dagger)' if is_instrument else 'Tr(E_a rho)'}
        return state, labels, probabilities, numerators, diagnostics

    def probabilities(self, rho_feature: FeatureValue, measurement_feature: FeatureValue) -> FeatureValue:
        """Return the normalized Born distribution without drawing an outcome."""
        _state_value, _labels, probabilities, _numerators, diagnostics = self._analyze(rho_feature, measurement_feature)
        provenance = rho_feature.provenance.derive(
            f'{rho_feature.provenance.record_id}:{measurement_feature.provenance.record_id}:probabilities',
            'qmw.measurement.Born_probabilities', '1', diagnostics,
            units='1', normalization='declared_tolerance_roundoff_only',
            parents=(rho_feature.provenance, measurement_feature.provenance),
            source_path='measurement.probabilities', backend=_SIMULATOR, evidence='calculated_probability')
        return FeatureValue(FeatureId('measurement.probabilities', 'outcome_probabilities', 'vector'), probabilities, provenance)

    def _general_record(self, rho_feature, measurement_feature, event_id, outcome, *, effects_only):
        nonempty(event_id, 'event_id')
        required = 'povm_effects' if effects_only else 'kraus_instrument'
        if not isinstance(measurement_feature, FeatureValue) or measurement_feature.id.quantity != required:
            raise ValueError(f'this method requires a {required} definition')
        state, labels, probabilities, numerators, diagnostics = self._analyze(rho_feature, measurement_feature)
        if outcome is None:
            rng = self._rng_context()
            index = int(self.rng.choice(len(labels), p=probabilities))
            origin, selection = 'simulated_sample', 'seeded_simulated_draw'
        else:
            if outcome not in labels:
                raise ValueError('requested outcome is absent from this instrument')
            index = labels.index(outcome)
            rng = None
            origin, selection = 'conditional_evaluation', 'specified_outcome_conditioning'
        probability = float(probabilities[index])
        if probability <= 0:
            raise ValueError('cannot condition on a zero probability outcome')
        if effects_only:
            posterior = None
            post_availability = 'effects_do_not_determine_instrument'
        else:
            # The conditional CP output is normalized by its own raw trace,
            # rather than by the separately roundoff-normalized sampling mass.
            raw_probability = float(diagnostics['raw_probabilities'][index])
            if raw_probability <= 0:
                raise ValueError('cannot normalize a zero probability instrument output')
            posterior = numerators[index] / raw_probability
            validate_density_matrix(posterior, tolerance=self.tolerance)
            post_availability = 'computed_candidate'
        metadata = {**diagnostics, 'rng': rng, 'selection': selection,
            'state_installation': 'caller_authority_only', 'authority_state_mutated': False,
            'post_state_availability': post_availability,
            'post_state_formula': None if effects_only else 'sum_j K_aj rho K_aj^dagger / raw_probability',
            'instrument_scope': 'same_input_output_coordinate_space',
            'basis_semantics': 'operator_coordinates; general_outcomes_need_not_define_an_orthogonal_basis',
            'probability_semantics': 'Born_probability_for_declared_source_density_and_measurement'}
        kind = 'povm_effects_only' if effects_only else 'general_instrument'
        provenance = rho_feature.provenance.derive(event_id, 'qmw.measurement.' + kind, '1',
            {**metadata, 'outcome': labels[index], 'probability': probability,
             'measurement_definition': measurement_feature.value}, units='1',
            normalization='conditional_CP_output_trace' if posterior is not None else 'no_post_state',
            parents=(rho_feature.provenance, measurement_feature.provenance),
            source_path='measurement.' + kind, backend=_SIMULATOR, evidence=origin)
        return MeasurementRecord(event_id, rho_feature.provenance.record_id, kind, origin, labels[index],
            probability, rho_feature.provenance.basis, rho_feature.provenance.clock, _SIMULATOR,
            provenance, state, posterior, 1 if origin == 'simulated_sample' else None, metadata)

    def instrument(self, rho_feature: FeatureValue, kraus_feature: FeatureValue, event_id: str,
                   *, outcome=None) -> MeasurementRecord:
        """Sample a grouped Kraus instrument, or explicitly condition on an outcome."""
        return self._general_record(rho_feature, kraus_feature, event_id, outcome, effects_only=False)

    def povm(self, rho_feature: FeatureValue, effects_feature: FeatureValue, event_id: str,
             *, outcome=None) -> MeasurementRecord:
        """Sample/condition an effects-only POVM; a posterior is unavailable."""
        return self._general_record(rho_feature, effects_feature, event_id, outcome, effects_only=True)

    def backend_observed(self, record_feature: FeatureValue, *, event_id: str, outcome,
                         measurement_kind: str, basis: BasisMetadata,
                         probability=None, shots=None) -> MeasurementRecord:
        """Wrap one supplied measurement record, retaining its real/unknown clock.

        This requires an event record containing an outcome, not counts. Any
        probability/shot metadata requested for retention must already be in
        that source record. Nothing here reconstructs individual measurements
        or unavailable quantum states from a backend result.
        """
        nonempty(event_id, 'event_id')
        nonempty(measurement_kind, 'measurement_kind')
        if (not isinstance(record_feature, FeatureValue) or record_feature.id.kind != 'record'
                or record_feature.id.quantity != 'measurement_event'):
            raise ValueError('backend wrapping requires an actual measurement_event record; counts are not events')
        data = record_feature.require_available()
        if record_feature.provenance.evidence not in ('backend_observed', 'observed', 'recorded', 'recorded_measurement', 'experimental_observation'):
            raise ValueError('backend observation requires source evidence of an observed/recorded measurement')
        if not isinstance(data, Mapping) or 'outcome' not in data or 'counts' in data:
            raise ValueError('backend event must provide an individual outcome, not a count histogram')
        if isinstance(outcome, (bool, np.bool_)) or not isinstance(outcome, (str, int)) or data['outcome'] != outcome:
            raise ValueError('requested outcome must match the supplied backend event outcome')
        if isinstance(outcome, str):
            nonempty(outcome, 'outcome')
        if not isinstance(basis, BasisMetadata) or basis != record_feature.provenance.basis:
            raise ValueError('backend record basis must preserve the supplied basis metadata')
        if probability is not None:
            probability = finite(probability, 'probability')
            if not 0 <= probability <= 1 or data.get('probability') != probability:
                raise ValueError('probability must match an available supplied backend probability/estimate')
        if shots is not None:
            shots = _integer(shots, 'shots')
            if shots == 0 or data.get('shots') != shots:
                raise ValueError('shots must match supplied positive backend shot metadata')
        metadata = {'rng': None, 'selection': 'supplied_backend_observation',
            'pre_state_availability': 'not_exposed_by_event_record', 'post_state_availability': 'not_exposed_by_event_record',
            'authority_state_mutated': False, 'state_installation': 'not_applicable',
            'source_payload': data, 'source_uncertainty': record_feature.uncertainty,
            'probability_semantics': data.get('probability_semantics', 'source_supplied_unspecified') if probability is not None else 'not_supplied',
            'clock_policy': 'retain_source_event_clock_or_explicit_unavailability'}
        provenance = record_feature.provenance.derive(event_id, 'qmw.measurement.backend_record_adapter', '1',
            {**metadata, 'outcome': outcome, 'measurement_kind': measurement_kind,
             'probability': probability, 'shots': shots}, units='1', normalization='none',
            source_path='measurement.backend_observed', evidence='backend_observed')
        return MeasurementRecord(event_id, record_feature.provenance.record_id, measurement_kind,
            'backend_observed', outcome, probability, basis, record_feature.provenance.clock,
            record_feature.provenance.backend, provenance, None, None, shots, metadata)
