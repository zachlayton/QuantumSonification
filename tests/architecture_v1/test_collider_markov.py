import numpy as np
import pytest

from qmw.architecture_v1.collider_markov import (
    ColliderMarkovModel,
    ColliderMarkovTrainingSequence,
    TraversalSemantics,
)
from qmw.architecture_v1.contracts import (
    BasisMetadata,
    ClockStamp,
    FeatureId,
    FeatureValue,
    Provenance,
)


_BASIS = BasisMetadata(
    'collider.markov.test.two_spin', 4, 'computational', 'q0_lsb', '00,01,10,11',
    details={
        'tensor_factors_msb_to_lsb': ('top', 'antitop'),
        'logical_subsystems_q0_first': ('antitop', 'top'),
    },
)
_NO_CLOCK = ClockStamp(None, 's', 'simulation_ensemble', 'unavailable', 'test-fixture')


def state_feature(state_id, populations, *, evidence='simulation'):
    return FeatureValue(
        FeatureId(f'collider.simulation.{state_id}.rho', 'density_matrix', 'matrix'),
        np.diag(populations).astype(complex),
        Provenance(
            f'test-state:{state_id}', f'fixture://collider/{state_id}', 'simulated_ensemble_state', '1',
            {'state_id': state_id, 'origin': 'explicit test simulation fixture'}, '1', 'trace_one',
            _BASIS, _NO_CLOCK, 'test_collider_simulator', evidence,
        ),
    )


def sequence(sequence_id, state_ids, semantics=TraversalSemantics.SIMULATED_KINEMATIC_PATH):
    return ColliderMarkovTrainingSequence(
        sequence_id,
        state_ids,
        semantics,
        Provenance(
            f'test-sequence:{sequence_id}', f'fixture://collider/{sequence_id}', 'declare_simulated_path', '1',
            {'sequence_id': sequence_id, 'purpose': 'test only'}, '1', 'none', _BASIS, _NO_CLOCK,
            'test_collider_simulator', 'simulation',
        ),
    )


@pytest.fixture
def states():
    return {
        'low': state_feature('low', [1., 0., 0., 0.]),
        'mid': state_feature('mid', [0., 1., 0., 0.]),
        'high': state_feature('high', [0., 0., 1., 0.]),
    }


def test_trains_only_from_declared_ordered_simulation_paths(states):
    model = ColliderMarkovModel.fit(
        states,
        (
            sequence('up', ('low', 'mid', 'high')),
            sequence('partial-up', ('low', 'mid')),
        ),
    )

    np.testing.assert_array_equal(model.transition_counts, [[0, 2, 0], [0, 0, 1], [0, 0, 0]])
    np.testing.assert_allclose(model.transition_matrix, [[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    assert model.state_ids == ('low', 'mid', 'high')
    assert model.metadata['time_semantics'] == 'no_physical_collider_time'
    assert model.metadata['purpose'] == 'offline_performance_state_selection'


def test_independent_monte_carlo_event_order_is_not_a_training_sequence(states):
    with pytest.raises(ValueError, match='independent Monte Carlo events'):
        ColliderMarkovTrainingSequence(
            'bad-row-order', ('low', 'mid'), 'independent_monte_carlo_events',
            sequence('source', ('low', 'mid')).provenance,
        )

    with pytest.raises(ValueError, match='simulation evidence'):
        ColliderMarkovModel.fit(
            {**states, 'recorded': state_feature('recorded', [0., 0., 0., 1.], evidence='recorded')},
            (sequence('bad-evidence', ('low', 'recorded')),),
        )


def test_generation_is_seeded_and_stops_at_an_observed_terminal_state(states):
    model = ColliderMarkovModel.fit(states, (sequence('up', ('low', 'mid', 'high')),))
    first = model.generate(start_state_id='low', maximum_transitions=9, seed=17)
    second = model.generate(start_state_id='low', maximum_transitions=9, seed=17)

    assert first.state_ids == ('low', 'mid', 'high')
    assert first.state_ids == second.state_ids
    assert first.terminated_at_observed_terminal is True
    assert first.state_features[-1].id.path == 'collider.performance.rho'
    assert first.state_features[-1].provenance.clock.semantics == 'unavailable'
    assert first.state_features[-1].provenance.parameters['timing_claim'] == 'none'


def test_temperature_is_explicit_sampling_control_not_collider_temperature(states):
    model = ColliderMarkovModel.fit(
        states,
        (
            sequence('a', ('low', 'mid')),
            sequence('b', ('low', 'mid')),
            sequence('c', ('low', 'mid')),
            sequence('d', ('low', 'high')),
        ),
    )

    np.testing.assert_allclose(model.next_probabilities('low', temperature=1.), [0., .75, .25])
    np.testing.assert_allclose(model.next_probabilities('low', temperature=.5), [0., .9, .1])
    assert model.next_probabilities('low', temperature=2.)[1] < .75
    assert model.metadata['temperature_semantics'] == 'performance_sampling_temperature_not_physical_temperature'


def test_interpolation_stays_a_density_matrix_and_is_labelled_composed(states):
    model = ColliderMarkovModel.fit(states, (sequence('up', ('low', 'mid')),))
    traversal = model.generate(start_state_id='low', maximum_transitions=1, seed=4)
    rho = model.interpolate(traversal, transition_index=0, fraction=.25)

    np.testing.assert_allclose(rho.value, np.diag([.75, .25, 0., 0.]))
    np.testing.assert_allclose(rho.value, rho.value.conj().T)
    assert np.trace(rho.value) == pytest.approx(1.)
    assert np.linalg.eigvalsh(rho.value).min() >= 0
    assert rho.provenance.parameters['interpolation'] == 'convex_density_matrix_path'
    assert rho.provenance.parameters['interpretation'] == 'composed traversal; not collider evolution or event time'


def test_non_two_qubit_or_invalid_density_inputs_fail_before_training(states):
    bad_basis = BasisMetadata('one-qubit', 2, 'computational', 'q0_lsb', '0,1')
    bad = FeatureValue(
        FeatureId('collider.simulation.bad.rho', 'density_matrix', 'matrix'), np.eye(2) / 2,
        Provenance('bad', 'fixture://bad', 'fixture', '1', {}, '1', 'trace_one', bad_basis,
                   _NO_CLOCK, 'test', 'simulation'),
    )
    with pytest.raises(ValueError, match='4x4'):
        ColliderMarkovModel.fit({**states, 'bad': bad}, (sequence('bad-dimension', ('low', 'bad')),))
