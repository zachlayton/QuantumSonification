from __future__ import annotations

import numpy as np
import pytest
from qiskit.primitives import StatevectorEstimator
from qiskit_machine_learning.gradients import SPSAEstimatorGradient

from spsa_sonification_v1.feedback import (
    AudioFeedbackState,
    controls_from_feedback,
)
from spsa_sonification_v1.osc_publisher import SPSAOSCPublisher
from spsa_sonification_v1.spsa_engine import build_demo_problem, compute_spsa_step


class CaptureClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


def make_step(*, seed: int = 47, batch_size: int = 3):
    circuit, observable, theta = build_demo_problem()
    step = compute_spsa_step(
        estimator=StatevectorEstimator(),
        circuit=circuit,
        observable=observable,
        theta=theta,
        epsilon=0.06,
        batch_size=batch_size,
        learning_rate=0.12,
        rng=np.random.default_rng(seed),
        step_index=7,
    )
    return circuit, observable, theta, step


def test_exposed_probes_match_qiskit_spsa_gradient() -> None:
    circuit, observable, theta, step = make_step()
    official = SPSAEstimatorGradient(
        StatevectorEstimator(), epsilon=0.06, batch_size=3, seed=47
    )
    official_gradient = official.run([circuit], [observable], [theta]).result().gradients[0]
    np.testing.assert_allclose(step.gradient, official_gradient, atol=1e-12)


def test_step_is_reproducible_and_updates_by_gradient_descent() -> None:
    _, _, theta, step = make_step()
    _, _, _, repeated = make_step()
    np.testing.assert_allclose(step.gradient, repeated.gradient)
    np.testing.assert_allclose(step.theta_after, theta - 0.12 * step.gradient)
    assert len(step.probes) == 3
    assert all(set(probe.delta) <= {-1.0, 1.0} for probe in step.probes)


def test_osc_contract_preserves_probe_order_without_waiting() -> None:
    _, _, _, step = make_step(batch_size=2)
    client = CaptureClient()
    publisher = SPSAOSCPublisher(client, sleep=lambda _: None)
    publisher.publish(step)
    addresses = [address for address, _ in client.messages]

    assert addresses[0] == "/qmw/spsa/step/begin"
    assert addresses[-1] == "/qmw/spsa/step/end"
    assert addresses.count("/qmw/spsa/probe/plus") == 2
    assert addresses.count("/qmw/spsa/probe/minus") == 2
    assert addresses.index("/qmw/spsa/probe/plus") < addresses.index(
        "/qmw/spsa/probe/minus"
    )
    assert addresses.count("/qmw/spsa/gradient") == 1
    assert addresses.count("/qmw/spsa/update") == 1


def test_audio_feedback_is_clipped_and_changes_next_question() -> None:
    state = AudioFeedbackState()
    frame = state.update(2.0, 0.9, 0.75, 0.8, 0.9)
    controls = controls_from_feedback(
        frame,
        base_epsilon=0.1,
        base_batch_size=2,
        base_learning_rate=0.2,
        mix=1.0,
    )
    assert frame.energy == 1.0
    assert controls.epsilon > 0.1
    assert controls.batch_size == 5
    assert controls.learning_rate > 0.2
    assert controls.perturbation_polarity == -1.0


def test_zero_feedback_mix_recovers_base_controls() -> None:
    state = AudioFeedbackState()
    frame = state.update(1.0, 1.0, 1.0, 1.0, 1.0)
    controls = controls_from_feedback(
        frame,
        base_epsilon=0.12,
        base_batch_size=3,
        base_learning_rate=0.18,
        mix=0.0,
    )
    assert controls.epsilon == pytest.approx(0.12)
    assert controls.batch_size == 3
    assert controls.learning_rate == pytest.approx(0.18)


@pytest.mark.parametrize(
    ("epsilon", "batch_size", "learning_rate"),
    [(0.0, 1, 0.1), (0.1, 0, 0.1), (0.1, 1, -0.1)],
)
def test_invalid_configuration_is_rejected(
    epsilon: float, batch_size: int, learning_rate: float
) -> None:
    circuit, observable, theta = build_demo_problem()
    with pytest.raises(ValueError):
        compute_spsa_step(
            estimator=StatevectorEstimator(),
            circuit=circuit,
            observable=observable,
            theta=theta,
            epsilon=epsilon,
            batch_size=batch_size,
            learning_rate=learning_rate,
            rng=np.random.default_rng(1),
            step_index=0,
        )
