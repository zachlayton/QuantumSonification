"""SPSA, acoustically adapted SPSA, and quantum natural gradient."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from .feedback import (
    AcousticFeedbackFrame,
    FeedbackControls,
    analyze_acoustic_response,
    controls_from_feedback,
)
from .model import HexanyOptimizationModel

Array = np.ndarray


@dataclass(frozen=True)
class ProbeRecord:
    index: int
    delta: tuple[float, ...]
    expectation_plus: float
    expectation_minus: float
    gradient: tuple[float, ...]

    @property
    def difference(self) -> float:
        return self.expectation_plus - self.expectation_minus


@dataclass(frozen=True)
class OptimizationStep:
    index: int
    theta: tuple[float, ...]
    objective_before: float
    objective: float
    expected_cut: float
    approximation_ratio: float
    optimum_probability: float
    entropy_bits: float
    participation: float
    phase_order: float
    geodesic_step: float
    cumulative_geodesic: float
    shell_leakage: float
    gradient_norm: float
    natural_gradient_norm: float | None
    metric_condition: float | None
    accepted_learning_rate: float
    model_evaluations: int
    probabilities: tuple[float, ...]
    phases: tuple[float, ...]
    edge_currents: tuple[tuple[int, int, float], ...]
    probes: tuple[ProbeRecord, ...] = ()
    acoustic_feedback: AcousticFeedbackFrame | None = None
    feedback_controls: FeedbackControls | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class OptimizationTrace:
    optimizer: str
    seed: int
    steps: tuple[OptimizationStep, ...]

    @property
    def final(self) -> OptimizationStep:
        return self.steps[-1]

    def to_dict(self) -> dict[str, object]:
        return {
            "optimizer": self.optimizer,
            "seed": self.seed,
            "steps": [step.to_dict() for step in self.steps],
        }


def _record_step(
    model: HexanyOptimizationModel,
    *,
    index: int,
    theta: Array,
    objective_before: float,
    previous_state: Array | None,
    cumulative_geodesic: float,
    gradient_norm: float,
    natural_gradient_norm: float | None,
    metric_condition: float | None,
    accepted_learning_rate: float,
    model_evaluations: int,
    probes: tuple[ProbeRecord, ...] = (),
    acoustic_feedback: AcousticFeedbackFrame | None = None,
    feedback_controls: FeedbackControls | None = None,
) -> tuple[OptimizationStep, Array, float]:
    state = model.state(theta)
    metrics = model.metrics_from_state(state, previous_state=previous_state)
    cumulative = cumulative_geodesic + metrics.geodesic_step
    probabilities = np.abs(state) ** 2
    return (
        OptimizationStep(
            index=index,
            theta=tuple(float(value) for value in theta),
            objective_before=float(objective_before),
            objective=metrics.objective,
            expected_cut=metrics.expected_cut,
            approximation_ratio=metrics.approximation_ratio,
            optimum_probability=metrics.optimum_probability,
            entropy_bits=metrics.entropy_bits,
            participation=metrics.participation,
            phase_order=metrics.phase_order,
            geodesic_step=metrics.geodesic_step,
            cumulative_geodesic=cumulative,
            shell_leakage=metrics.shell_leakage,
            gradient_norm=float(gradient_norm),
            natural_gradient_norm=(
                None if natural_gradient_norm is None else float(natural_gradient_norm)
            ),
            metric_condition=None if metric_condition is None else float(metric_condition),
            accepted_learning_rate=float(accepted_learning_rate),
            model_evaluations=int(model_evaluations),
            probabilities=tuple(float(value) for value in probabilities),
            phases=tuple(float(value) for value in np.angle(state)),
            edge_currents=model.edge_currents_from_state(state),
            probes=probes,
            acoustic_feedback=acoustic_feedback,
            feedback_controls=feedback_controls,
        ),
        state,
        cumulative,
    )


def _probe_batch(
    model: HexanyOptimizationModel,
    theta: Array,
    *,
    epsilon: float,
    batch_size: int,
    polarity: float,
    rng: np.random.Generator,
) -> tuple[Array, tuple[ProbeRecord, ...], int]:
    records: list[ProbeRecord] = []
    gradients: list[Array] = []
    for index in range(batch_size):
        delta = polarity * rng.choice((-1.0, 1.0), size=model.parameter_count)
        plus = model.objective(theta + epsilon * delta)
        minus = model.objective(theta - epsilon * delta)
        gradient = ((plus - minus) / (2.0 * epsilon)) * delta
        gradients.append(gradient)
        records.append(
            ProbeRecord(
                index=index,
                delta=tuple(float(value) for value in delta),
                expectation_plus=float(plus),
                expectation_minus=float(minus),
                gradient=tuple(float(value) for value in gradient),
            )
        )
    return np.mean(gradients, axis=0), tuple(records), 2 * batch_size


def optimize_spsa(
    model: HexanyOptimizationModel,
    initial_theta: Array,
    *,
    steps: int = 60,
    seed: int = 731,
    learning_rate: float = 0.22,
    perturbation: float = 0.16,
    stability: float = 8.0,
    alpha: float = 0.602,
    gamma: float = 0.101,
) -> OptimizationTrace:
    theta = np.asarray(initial_theta, dtype=np.float64).copy()
    rng = np.random.default_rng(seed)
    objective = model.objective(theta)
    initial, previous_state, cumulative = _record_step(
        model,
        index=0,
        theta=theta,
        objective_before=objective,
        previous_state=None,
        cumulative_geodesic=0.0,
        gradient_norm=0.0,
        natural_gradient_norm=None,
        metric_condition=None,
        accepted_learning_rate=0.0,
        model_evaluations=1,
    )
    records = [initial]
    evaluations = 1
    for index in range(1, steps + 1):
        rate = learning_rate / ((index + stability) ** alpha)
        epsilon = perturbation / (index**gamma)
        objective_before = records[-1].objective
        gradient, probes, used = _probe_batch(
            model, theta, epsilon=epsilon, batch_size=1, polarity=1.0, rng=rng
        )
        evaluations += used
        theta -= rate * gradient
        evaluations += 1
        record, previous_state, cumulative = _record_step(
            model,
            index=index,
            theta=theta,
            objective_before=objective_before,
            previous_state=previous_state,
            cumulative_geodesic=cumulative,
            gradient_norm=float(np.linalg.norm(gradient)),
            natural_gradient_norm=None,
            metric_condition=None,
            accepted_learning_rate=rate,
            model_evaluations=evaluations,
            probes=probes,
        )
        records.append(record)
    return OptimizationTrace("spsa", seed, tuple(records))


def optimize_acoustic_feedback_spsa(
    model: HexanyOptimizationModel,
    initial_theta: Array,
    *,
    steps: int = 60,
    seed: int = 731,
    learning_rate: float = 0.22,
    perturbation: float = 0.16,
    base_batch_size: int = 1,
    feedback_mix: float = 1.0,
    stability: float = 8.0,
    alpha: float = 0.602,
    gamma: float = 0.101,
) -> OptimizationTrace:
    """SPSA whose next complete probe batch is shaped by the last answer."""

    theta = np.asarray(initial_theta, dtype=np.float64).copy()
    rng = np.random.default_rng(seed)
    state = model.state(theta)
    probabilities = np.abs(state) ** 2
    feedback = analyze_acoustic_response(
        model, state, step=0, previous_probabilities=None
    )
    objective = model.objective_from_state(state)
    initial, previous_state, cumulative = _record_step(
        model,
        index=0,
        theta=theta,
        objective_before=objective,
        previous_state=None,
        cumulative_geodesic=0.0,
        gradient_norm=0.0,
        natural_gradient_norm=None,
        metric_condition=None,
        accepted_learning_rate=0.0,
        model_evaluations=1,
        acoustic_feedback=feedback,
    )
    records = [initial]
    evaluations = 1
    for index in range(1, steps + 1):
        base_rate = learning_rate / ((index + stability) ** alpha)
        base_epsilon = perturbation / (index**gamma)
        controls = controls_from_feedback(
            feedback,
            base_epsilon=base_epsilon,
            base_batch_size=base_batch_size,
            base_learning_rate=base_rate,
            mix=feedback_mix,
        )
        objective_before = records[-1].objective
        gradient, probes, used = _probe_batch(
            model,
            theta,
            epsilon=controls.epsilon,
            batch_size=controls.batch_size,
            polarity=controls.perturbation_polarity,
            rng=rng,
        )
        evaluations += used
        theta -= controls.learning_rate * gradient
        new_state = model.state(theta)
        evaluations += 1
        new_probabilities = np.abs(new_state) ** 2
        new_feedback = analyze_acoustic_response(
            model,
            new_state,
            step=index,
            previous_probabilities=probabilities,
        )
        record, previous_state, cumulative = _record_step(
            model,
            index=index,
            theta=theta,
            objective_before=objective_before,
            previous_state=previous_state,
            cumulative_geodesic=cumulative,
            gradient_norm=float(np.linalg.norm(gradient)),
            natural_gradient_norm=None,
            metric_condition=None,
            accepted_learning_rate=controls.learning_rate,
            model_evaluations=evaluations,
            probes=probes,
            acoustic_feedback=new_feedback,
            feedback_controls=controls,
        )
        records.append(record)
        feedback = new_feedback
        probabilities = new_probabilities
    return OptimizationTrace("acoustic_feedback_spsa", seed, tuple(records))


def optimize_quantum_natural_gradient(
    model: HexanyOptimizationModel,
    initial_theta: Array,
    *,
    steps: int = 24,
    seed: int = 731,
    learning_rate: float = 0.8,
    regularization: float = 2e-3,
    derivative_epsilon: float = 1e-5,
    max_geodesic_step: float = 0.24,
    max_backtracks: int = 8,
) -> OptimizationTrace:
    theta = np.asarray(initial_theta, dtype=np.float64).copy()
    objective = model.objective(theta)
    initial, previous_state, cumulative = _record_step(
        model,
        index=0,
        theta=theta,
        objective_before=objective,
        previous_state=None,
        cumulative_geodesic=0.0,
        gradient_norm=0.0,
        natural_gradient_norm=0.0,
        metric_condition=1.0,
        accepted_learning_rate=0.0,
        model_evaluations=1,
    )
    records = [initial]
    evaluations = 1
    for index in range(1, steps + 1):
        gradient, metric = model.objective_gradient_and_metric(
            theta, epsilon=derivative_epsilon
        )
        evaluations += 1 + 2 * model.parameter_count
        regularized = metric + regularization * np.eye(model.parameter_count)
        direction = np.linalg.solve(regularized, gradient)
        condition = float(np.linalg.cond(regularized))
        speed_squared = float(direction @ metric @ direction)
        if speed_squared > 0:
            direction *= min(1.0, max_geodesic_step / math.sqrt(speed_squared))
        objective_before = records[-1].objective
        accepted = learning_rate
        proposal = theta.copy()
        for _ in range(max_backtracks + 1):
            candidate = theta - accepted * direction
            evaluations += 1
            proposal = candidate
            if model.objective(candidate) <= objective_before + 1e-12:
                break
            accepted *= 0.5
        else:
            accepted = 0.0
            proposal = theta.copy()
        theta = proposal
        evaluations += 1
        record, previous_state, cumulative = _record_step(
            model,
            index=index,
            theta=theta,
            objective_before=objective_before,
            previous_state=previous_state,
            cumulative_geodesic=cumulative,
            gradient_norm=float(np.linalg.norm(gradient)),
            natural_gradient_norm=float(np.linalg.norm(direction)),
            metric_condition=condition,
            accepted_learning_rate=accepted,
            model_evaluations=evaluations,
        )
        records.append(record)
    return OptimizationTrace("quantum_natural_gradient", seed, tuple(records))
