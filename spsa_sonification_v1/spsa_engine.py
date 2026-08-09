"""Reproducible SPSA probe-pair computation using Qiskit Estimator V2.

The calculation intentionally mirrors Qiskit Machine Learning's
``SPSAEstimatorGradient`` so that every hidden plus/minus evaluation is available
for sonification before the batch is averaged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


@dataclass(frozen=True)
class SPSAProbe:
    """One simultaneous plus/minus perturbation and its gradient estimate."""

    index: int
    delta: np.ndarray
    theta_plus: np.ndarray
    theta_minus: np.ndarray
    expectation_plus: float
    expectation_minus: float
    gradient: np.ndarray

    @property
    def difference(self) -> float:
        return self.expectation_plus - self.expectation_minus


@dataclass(frozen=True)
class SPSAStep:
    """One averaged SPSA gradient and gradient-descent update."""

    index: int
    theta_before: np.ndarray
    theta_after: np.ndarray
    objective_before: float
    objective_after: float
    gradient: np.ndarray
    probes: tuple[SPSAProbe, ...]

    @property
    def gradient_norm(self) -> float:
        return float(np.linalg.norm(self.gradient))


def build_demo_problem() -> tuple[QuantumCircuit, SparsePauliOp, np.ndarray]:
    """Return a compact four-parameter entangled landscape for auditioning SPSA."""

    theta = ParameterVector("theta", 4)
    circuit = QuantumCircuit(2)
    circuit.ry(theta[0], 0)
    circuit.rz(theta[1], 0)
    circuit.ry(theta[2], 1)
    circuit.rz(theta[3], 1)
    circuit.cx(0, 1)
    circuit.ry(0.35, 0)
    circuit.cx(1, 0)

    observable = SparsePauliOp.from_list(
        [("ZZ", 0.50), ("XX", 0.30), ("ZI", 0.15), ("IY", 0.05)]
    )
    initial_theta = np.array([0.25, 1.10, -0.70, 0.45], dtype=float)
    return circuit, observable, initial_theta


def _expectations(
    estimator: Any,
    circuit: QuantumCircuit,
    observable: SparsePauliOp,
    parameter_values: list[np.ndarray],
) -> np.ndarray:
    pubs = [(circuit, observable, values) for values in parameter_values]
    result = estimator.run(pubs).result()
    return np.asarray([float(pub_result.data.evs) for pub_result in result])


def expectation(
    estimator: Any,
    circuit: QuantumCircuit,
    observable: SparsePauliOp,
    theta: np.ndarray,
) -> float:
    """Evaluate one expectation value."""

    return float(_expectations(estimator, circuit, observable, [theta])[0])


def compute_spsa_step(
    *,
    estimator: Any,
    circuit: QuantumCircuit,
    observable: SparsePauliOp,
    theta: np.ndarray,
    epsilon: float,
    batch_size: int,
    learning_rate: float,
    rng: np.random.Generator,
    step_index: int,
    perturbation_polarity: float = 1.0,
) -> SPSAStep:
    """Compute all probe pairs, average their gradients, and descend one step."""

    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if learning_rate < 0:
        raise ValueError("learning_rate must be non-negative")
    if perturbation_polarity not in (-1.0, 1.0):
        raise ValueError("perturbation_polarity must be -1 or +1")

    theta = np.asarray(theta, dtype=float)
    deltas = [
        perturbation_polarity * ((-1.0) ** rng.integers(0, 2, theta.size))
        for _ in range(batch_size)
    ]
    plus = [theta + epsilon * delta for delta in deltas]
    minus = [theta - epsilon * delta for delta in deltas]
    values = _expectations(estimator, circuit, observable, plus + minus)
    values_plus = values[:batch_size]
    values_minus = values[batch_size:]

    probes: list[SPSAProbe] = []
    for index, (delta, theta_plus, theta_minus, value_plus, value_minus) in enumerate(
        zip(deltas, plus, minus, values_plus, values_minus)
    ):
        directional_difference = (value_plus - value_minus) / (2.0 * epsilon)
        gradient = directional_difference / delta
        probes.append(
            SPSAProbe(
                index=index,
                delta=np.asarray(delta),
                theta_plus=theta_plus,
                theta_minus=theta_minus,
                expectation_plus=float(value_plus),
                expectation_minus=float(value_minus),
                gradient=np.asarray(gradient),
            )
        )

    gradient = np.mean([probe.gradient for probe in probes], axis=0)
    theta_after = theta - learning_rate * gradient
    objective_before, objective_after = _expectations(
        estimator, circuit, observable, [theta, theta_after]
    )
    return SPSAStep(
        index=step_index,
        theta_before=theta.copy(),
        theta_after=theta_after,
        objective_before=float(objective_before),
        objective_after=float(objective_after),
        gradient=np.asarray(gradient),
        probes=tuple(probes),
    )


def default_estimator() -> StatevectorEstimator:
    """Create the exact local estimator used by the demo."""

    return StatevectorEstimator()
