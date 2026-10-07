"""Offline simulation-trained collider state traversal for performance.

This module is intentionally downstream of the collider-state authority.  It
does not reconstruct a spin state from event kinematics, reorder independent
Monte Carlo events, simulate a collision, or assign physical collider time.
Instead it learns a row-stochastic traversal grammar from *declared ordered*
simulation paths over independently supplied two-spin density matrices.  The
result can select and interpolate valid density matrices for a QMW performance
trajectory, with the resulting selection and interpolation marked as composed.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

import numpy as np

from qmw.qmw_representation_laboratory_v4.core.state_transform import validate_density_matrix

from .contracts import (
    ClockStamp,
    FeatureId,
    FeatureValue,
    Provenance,
    finite,
    freeze,
    frozen_array,
    nonempty,
)


_SIMULATION_EVIDENCE = frozenset({'simulation', 'test_fixture'})
_TRAINING_SEMANTICS = frozenset({
    'simulated_decay_chain',
    'simulated_kinematic_path',
})


class TraversalSemantics(str, Enum):
    """The declared origin of an ordering supplied for Markov training."""

    SIMULATED_DECAY_CHAIN = 'simulated_decay_chain'
    SIMULATED_KINEMATIC_PATH = 'simulated_kinematic_path'
    COMPOSED_KINEMATIC_PATH = 'composed_kinematic_path'


def _semantics(value) -> TraversalSemantics:
    if value == 'independent_monte_carlo_events':
        raise ValueError(
            'independent Monte Carlo events have no physical successor relation and cannot train a traversal model'
        )
    try:
        return TraversalSemantics(value)
    except ValueError as exc:
        raise ValueError('unknown declared traversal semantics') from exc


def _state_id(value, name='state_id') -> str:
    value = nonempty(value, name)
    if any(character.isspace() for character in value):
        raise ValueError(f'{name} may not contain whitespace')
    return value


def _unavailable_performance_clock(origin: str) -> ClockStamp:
    return ClockStamp(None, 's', 'performance_traversal', 'unavailable', origin)


def _validate_state_feature(feature: FeatureValue) -> np.ndarray:
    """Validate a supplied top-antitop two-spin state without changing it."""
    if not isinstance(feature, FeatureValue):
        raise TypeError('collider Markov states must be shared FeatureValue instances')
    if feature.id.quantity != 'density_matrix' or feature.id.kind != 'matrix':
        raise ValueError('collider Markov states require a typed density_matrix feature')
    matrix = np.asarray(feature.require_available(), dtype=complex)
    if matrix.shape != (4, 4):
        raise ValueError('collider Markov states require a 4x4 two-qubit density matrix')
    basis = feature.provenance.basis
    if basis.dimension != 4 or basis.kind != 'computational' or basis.subsystem_order != 'q0_lsb':
        raise ValueError('collider Markov states require declared 4D computational q0_lsb coordinates')
    logical = tuple(basis.details.get('logical_subsystems_q0_first', ()))
    if logical and logical != ('antitop', 'top'):
        raise ValueError('collider Markov state subsystem labels must retain q0=antitop, q1=top')
    if feature.units != '1':
        raise ValueError('collider Markov density matrices must be dimensionless')
    return validate_density_matrix(matrix)


@dataclass(frozen=True)
class ColliderMarkovTrainingSequence:
    """An explicitly ordered simulated path used as offline training evidence."""

    sequence_id: str
    state_ids: tuple[str, ...]
    semantics: TraversalSemantics
    provenance: Provenance

    def __post_init__(self):
        object.__setattr__(self, 'sequence_id', _state_id(self.sequence_id, 'sequence_id'))
        if isinstance(self.state_ids, (str, bytes)):
            raise ValueError('state_ids must be an ordered sequence, not a string')
        state_ids = tuple(_state_id(value) for value in self.state_ids)
        if len(state_ids) < 2:
            raise ValueError('a Markov training sequence needs at least one declared transition')
        if not isinstance(self.provenance, Provenance):
            raise ValueError('training sequence provenance is required')
        object.__setattr__(self, 'state_ids', state_ids)
        object.__setattr__(self, 'semantics', _semantics(self.semantics))


@dataclass(frozen=True)
class ColliderPerformanceTraversal:
    """A reproducible, composed sequence of selected collider density matrices."""

    traversal_id: str
    state_ids: tuple[str, ...]
    state_features: tuple[FeatureValue, ...]
    terminated_at_observed_terminal: bool
    provenance: Provenance
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        nonempty(self.traversal_id, 'traversal_id')
        state_ids = tuple(_state_id(value) for value in self.state_ids)
        features = tuple(self.state_features)
        if not state_ids or len(state_ids) != len(features):
            raise ValueError('a traversal needs one selected state feature per state id')
        if not all(isinstance(feature, FeatureValue) for feature in features):
            raise ValueError('traversal state features must use shared FeatureValue contracts')
        if not isinstance(self.terminated_at_observed_terminal, bool):
            raise ValueError('terminal status must be boolean')
        if not isinstance(self.provenance, Provenance):
            raise ValueError('traversal provenance is required')
        object.__setattr__(self, 'state_ids', state_ids)
        object.__setattr__(self, 'state_features', features)
        object.__setattr__(self, 'metadata', freeze(self.metadata))


@dataclass(frozen=True)
class ColliderMarkovModel:
    """A finite-state, simulation-trained performance grammar.

    Rows with zero retained outgoing transitions are terminal.  They remain
    zero rather than receiving an invented self-loop or a uniform fallback.
    """

    state_ids: tuple[str, ...]
    state_features: tuple[FeatureValue, ...]
    transition_counts: np.ndarray
    transition_matrix: np.ndarray
    provenance: Provenance
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        state_ids = tuple(_state_id(value) for value in self.state_ids)
        features = tuple(self.state_features)
        if not state_ids or len(set(state_ids)) != len(state_ids):
            raise ValueError('model state ids must be nonempty and distinct')
        if len(state_ids) != len(features) or not all(isinstance(feature, FeatureValue) for feature in features):
            raise ValueError('model state features must align with model state ids')
        reference_basis = None
        for feature in features:
            _validate_state_feature(feature)
            if feature.provenance.evidence not in _SIMULATION_EVIDENCE:
                raise ValueError('collider Markov training requires simulation evidence, not recorded or measured states')
            if reference_basis is None:
                reference_basis = feature.provenance.basis
            elif feature.provenance.basis.to_dict() != reference_basis.to_dict():
                raise ValueError('all collider Markov states require one declared basis')
        n = len(state_ids)
        counts = frozen_array(self.transition_counts, dtype=np.int64)
        matrix = frozen_array(self.transition_matrix, dtype=float)
        if counts.shape != (n, n) or matrix.shape != (n, n):
            raise ValueError('transition counts and matrix must be square over declared states')
        if np.any(counts < 0) or not np.all(np.isfinite(matrix)) or np.any(matrix < 0):
            raise ValueError('transition counts and probabilities must be finite and nonnegative')
        row_totals = counts.sum(axis=1)
        expected = np.zeros((n, n), dtype=float)
        nonterminal = row_totals > 0
        expected[nonterminal] = counts[nonterminal] / row_totals[nonterminal, None]
        if not np.allclose(matrix, expected, atol=1e-12, rtol=0):
            raise ValueError('transition matrix must be the exact row-normalized declared count matrix')
        if not isinstance(self.provenance, Provenance):
            raise ValueError('model provenance is required')
        if self.provenance.basis.to_dict() != reference_basis.to_dict():
            raise ValueError('model provenance basis must match supplied density matrices')
        object.__setattr__(self, 'state_ids', state_ids)
        object.__setattr__(self, 'state_features', features)
        object.__setattr__(self, 'transition_counts', counts)
        object.__setattr__(self, 'transition_matrix', matrix)
        object.__setattr__(self, 'metadata', freeze(self.metadata))

    @classmethod
    def fit(cls, states: Mapping[str, FeatureValue], sequences: Sequence[ColliderMarkovTrainingSequence]):
        """Count transitions only from explicit ordered simulation paths.

        Independent generated-event rows are deliberately unsupported.  A
        caller must establish an ordering as a decay-chain path or an explicit
        kinematic-state path before this observer can learn a grammar.
        """
        if not isinstance(states, Mapping) or not states:
            raise ValueError('states must be a nonempty mapping of state ids to density features')
        state_ids = tuple(_state_id(state_id) for state_id in states)
        features = tuple(states[state_id] for state_id in state_ids)
        for feature in features:
            _validate_state_feature(feature)
            if feature.provenance.evidence not in _SIMULATION_EVIDENCE:
                raise ValueError('collider Markov training requires simulation evidence, not recorded or measured states')
        training = tuple(sequences)
        if not training or not all(isinstance(item, ColliderMarkovTrainingSequence) for item in training):
            raise ValueError('training requires at least one ColliderMarkovTrainingSequence')
        index = {state_id: position for position, state_id in enumerate(state_ids)}
        counts = np.zeros((len(state_ids), len(state_ids)), dtype=np.int64)
        for path in training:
            if path.semantics.value not in _TRAINING_SEMANTICS:
                raise ValueError('only declared simulated decay-chain or kinematic paths may train the Markov model')
            if path.provenance.evidence not in _SIMULATION_EVIDENCE:
                raise ValueError('training-path provenance must carry simulation evidence')
            unknown = tuple(state_id for state_id in path.state_ids if state_id not in index)
            if unknown:
                raise ValueError(f'training path {path.sequence_id!r} references undeclared states: {unknown}')
            for source, target in zip(path.state_ids, path.state_ids[1:]):
                counts[index[source], index[target]] += 1
        if not counts.any():
            raise ValueError('declared paths contained no retained state transitions')
        totals = counts.sum(axis=1)
        matrix = np.zeros_like(counts, dtype=float)
        has_successor = totals > 0
        matrix[has_successor] = counts[has_successor] / totals[has_successor, None]
        model_signature = hashlib.sha256(json.dumps({
            'state_ids': state_ids,
            'counts': counts.tolist(),
            'training_ids': tuple(path.sequence_id for path in training),
        }, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        root = features[0].provenance.derive(
            f'collider-markov:{model_signature}', 'fit_offline_collider_markov_transition_grammar',
            parameters={
                'state_ids': state_ids,
                'training_sequence_ids': tuple(path.sequence_id for path in training),
                'training_semantics': tuple(path.semantics.value for path in training),
                'count_rule': 'one unit count for every adjacent pair in each declared path',
                'normalization': 'row-normalized observed counts; terminal rows remain zero',
                'time_semantics': 'no_physical_collider_time',
                'purpose': 'offline_performance_state_selection',
                'prohibited_input': 'arbitrary ordering of independent Monte Carlo events',
                'state_authority': 'input density matrices remain unchanged and upstream',
            },
            units='1', normalization='row_stochastic_from_declared_counts',
            parents=tuple(feature.provenance for feature in features) + tuple(path.provenance for path in training),
            clock=_unavailable_performance_clock('collider-markov-training'),
            source_path='collider.markov.model', backend='collider_markov.offline', evidence='derived_simulation',
        )
        metadata = {
            'time_semantics': 'no_physical_collider_time',
            'purpose': 'offline_performance_state_selection',
            'temperature_semantics': 'performance_sampling_temperature_not_physical_temperature',
            'terminal_state_policy': 'retain a zero outgoing row; never invent a self-loop or fallback distribution',
            'interpolation_policy': 'explicit convex density-matrix path is composed and never collider evolution',
        }
        return cls(state_ids, features, counts, matrix, root, metadata)

    def _index(self, state_id: str) -> int:
        state_id = _state_id(state_id)
        try:
            return self.state_ids.index(state_id)
        except ValueError as exc:
            raise KeyError(f'unknown collider Markov state {state_id!r}') from exc

    def next_probabilities(self, state_id: str, *, temperature: float = 1.) -> np.ndarray:
        """Return a temperature-shaped performance distribution for one state.

        ``temperature`` only changes the compositional sampling distribution:
        ``p_j ∝ T_ij ** (1 / temperature)``.  It has no thermodynamic or
        collider interpretation and preserves unavailable outgoing rows.
        """
        temperature = finite(temperature, 'temperature')
        if temperature <= 0:
            raise ValueError('temperature must be positive')
        row = np.asarray(self.transition_matrix[self._index(state_id)], dtype=float)
        if not np.any(row):
            return frozen_array(np.zeros_like(row), dtype=float)
        shaped = np.zeros_like(row)
        positive = row > 0
        shaped[positive] = np.exp(np.log(row[positive]) / temperature)
        return frozen_array(shaped / shaped.sum(), dtype=float)

    def _selected_feature(self, traversal_id: str, ordinal: int, state_id: str, temperature: float) -> FeatureValue:
        feature = self.state_features[self._index(state_id)]
        provenance = self.provenance.derive(
            f'{traversal_id}:state:{ordinal}:{state_id}', 'select_simulation_state_for_offline_performance',
            parameters={
                'selected_state_id': state_id,
                'ordinal': ordinal,
                'sampling_temperature': temperature,
                'temperature_semantics': 'performance_sampling_temperature_not_physical_temperature',
                'timing_claim': 'none',
                'interpretation': 'simulation-trained Markov state selection; not collider evolution, event ordering, or event time',
            },
            units='1', normalization='trace_one', parents=(self.provenance, feature.provenance),
            clock=_unavailable_performance_clock(traversal_id), source_path='collider.performance.rho',
            backend='collider_markov.performance', evidence='composed_selection',
        )
        return FeatureValue(
            FeatureId('collider.performance.rho', 'density_matrix', 'matrix'), feature.value, provenance,
            uncertainty=feature.uncertainty,
        )

    def generate(self, *, start_state_id: str, maximum_transitions: int, seed: int | None = None,
                 temperature: float = 1.) -> ColliderPerformanceTraversal:
        """Sample a bounded reproducible performance traversal from the model."""
        if isinstance(maximum_transitions, (bool, np.bool_)) or not isinstance(maximum_transitions, (int, np.integer)):
            raise ValueError('maximum_transitions must be a nonnegative integer')
        maximum_transitions = int(maximum_transitions)
        if maximum_transitions < 0:
            raise ValueError('maximum_transitions must be a nonnegative integer')
        if seed is not None and (isinstance(seed, (bool, np.bool_)) or not isinstance(seed, (int, np.integer))):
            raise ValueError('seed must be an integer or None')
        temperature = finite(temperature, 'temperature')
        if temperature <= 0:
            raise ValueError('temperature must be positive')
        start_index = self._index(start_state_id)
        rng = np.random.default_rng(seed)
        selected = [self.state_ids[start_index]]
        current = start_index
        terminal = False
        for _ in range(maximum_transitions):
            probabilities = self.next_probabilities(self.state_ids[current], temperature=temperature)
            if not np.any(probabilities):
                terminal = True
                break
            current = int(rng.choice(len(self.state_ids), p=probabilities))
            selected.append(self.state_ids[current])
        else:
            terminal = not np.any(self.next_probabilities(self.state_ids[current], temperature=temperature))
        traversal_payload = {
            'model_record_id': self.provenance.record_id,
            'seed': None if seed is None else int(seed),
            'temperature': temperature,
            'state_ids': tuple(selected),
            'maximum_transitions': maximum_transitions,
        }
        signature = hashlib.sha256(json.dumps(traversal_payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:16]
        traversal_id = f'{self.provenance.record_id}:performance:{signature}'
        state_features = tuple(
            self._selected_feature(traversal_id, ordinal, state_id, temperature)
            for ordinal, state_id in enumerate(selected)
        )
        provenance = self.provenance.derive(
            traversal_id, 'sample_offline_collider_markov_performance_path',
            parameters={
                **traversal_payload,
                'terminal_policy': self.metadata['terminal_state_policy'],
                'interpretation': 'composed performance traversal through simulation-derived state grammar',
                'timing_claim': 'none',
            },
            units='1', normalization='none', parents=(self.provenance,),
            clock=_unavailable_performance_clock(traversal_id), source_path='collider.performance.path',
            backend='collider_markov.performance', evidence='composed_selection',
        )
        return ColliderPerformanceTraversal(
            traversal_id, tuple(selected), state_features, terminal, provenance,
            metadata={**traversal_payload, 'model_record_id': self.provenance.record_id},
        )

    def interpolate(self, traversal: ColliderPerformanceTraversal, *, transition_index: int, fraction: float) -> FeatureValue:
        """Build a valid convex density-matrix path between selected states.

        This is deliberately not called a geodesic or physical interpolation.
        Convex mixing preserves density-matrix validity but represents a QMW
        compositional choice between ensemble states, not a collider process.
        """
        if not isinstance(traversal, ColliderPerformanceTraversal):
            raise TypeError('interpolation requires a ColliderPerformanceTraversal')
        if traversal.metadata.get('model_record_id') != self.provenance.record_id:
            raise ValueError('traversal was generated by a different collider Markov model')
        if isinstance(transition_index, (bool, np.bool_)) or not isinstance(transition_index, (int, np.integer)):
            raise ValueError('transition_index must be an integer')
        transition_index = int(transition_index)
        if not 0 <= transition_index < len(traversal.state_features) - 1:
            raise IndexError('transition_index must identify adjacent selected states')
        fraction = finite(fraction, 'fraction')
        if not 0 <= fraction <= 1:
            raise ValueError('fraction must lie in [0, 1]')
        source = traversal.state_features[transition_index]
        target = traversal.state_features[transition_index + 1]
        source_matrix = _validate_state_feature(source)
        target_matrix = _validate_state_feature(target)
        matrix = (1. - fraction) * source_matrix + fraction * target_matrix
        validate_density_matrix(matrix)
        source_id, target_id = traversal.state_ids[transition_index:transition_index + 2]
        provenance = traversal.provenance.derive(
            f'{traversal.traversal_id}:interpolation:{transition_index}:{fraction:.12g}',
            'convex_density_matrix_interpolation',
            parameters={
                'source_state_id': source_id,
                'target_state_id': target_id,
                'fraction': fraction,
                'interpolation': 'convex_density_matrix_path',
                'interpretation': 'composed traversal; not collider evolution or event time',
                'timing_claim': 'none',
                'validity_reason': 'convex combination of two trace-one positive semidefinite density matrices',
            },
            units='1', normalization='trace_one',
            parents=(traversal.provenance, source.provenance, target.provenance),
            clock=_unavailable_performance_clock(traversal.traversal_id), source_path='collider.performance.rho',
            backend='collider_markov.performance', evidence='composed_interpolation',
        )
        return FeatureValue(FeatureId('collider.performance.rho', 'density_matrix', 'matrix'), matrix, provenance)
