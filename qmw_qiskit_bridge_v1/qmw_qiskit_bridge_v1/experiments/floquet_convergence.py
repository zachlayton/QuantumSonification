"""Convergence and circuit-cost controls for the QMW Floquet benchmark."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from qiskit import transpile

from .floquet_comparison import (
    _model_operators,
    _qiskit_statevector,
    _qmw_dense,
    _trace_distance,
    _trotter,
    _trotter_period_circuit,
    noncommuting_benchmark_model,
)


@dataclass(frozen=True)
class ConvergencePoint:
    configuration: str
    order: int
    repetitions: int
    magnetization_rmse: float
    maximum_magnetization_error: float
    final_trace_distance: float
    maximum_trace_distance: float
    gates_per_period: int
    depth_per_period: int
    two_qubit_gates_per_period: int

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class ConvergenceStudy:
    periods: int
    configurations: dict[str, dict[str, Any]]
    exact_route_maximum_trace_distance: dict[str, float]
    points: tuple[ConvergencePoint, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "periods": self.periods,
            "configurations": self.configurations,
            "exact_route_maximum_trace_distance": dict(
                self.exact_route_maximum_trace_distance
            ),
            "points": [point.as_dict() for point in self.points],
        }


def _default_control_model():
    # Reuse the existing model without changing its default Hamiltonian.
    benchmark = noncommuting_benchmark_model()
    model_type = type(benchmark)
    return model_type()


def _circuit_cost(model, interaction, kick, *, order: int, reps: int) -> tuple[int, int, int]:
    circuit = _trotter_period_circuit(
        model, interaction, kick, order=order, reps=reps
    )
    compiled = transpile(
        circuit,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=0,
        seed_transpiler=2718,
    )
    counts = compiled.count_ops()
    return (
        int(sum(counts.values())),
        int(compiled.depth()),
        int(counts.get("cx", 0)),
    )


def run_floquet_convergence_study(
    *,
    periods: int = 16,
    repetitions: tuple[int, ...] = (1, 2, 4, 8),
) -> ConvergenceStudy:
    if periods < 1:
        raise ValueError("periods must be positive")
    if not repetitions or any(int(value) < 1 for value in repetitions):
        raise ValueError("repetitions must contain positive integers")

    configurations = {
        "commuting_control": _default_control_model(),
        "noncommuting_benchmark": noncommuting_benchmark_model(),
    }
    points: list[ConvergencePoint] = []
    exact_agreement: dict[str, float] = {}

    for configuration, model in configurations.items():
        interaction, kick, magnetization_op = _model_operators(model)
        magnetization = np.asarray(magnetization_op.to_matrix())
        reference = _qmw_dense(model, periods, magnetization)
        qiskit_exact = _qiskit_statevector(
            model, periods, interaction, kick, magnetization
        )
        exact_agreement[configuration] = max(
            _trace_distance(left, right)
            for left, right in zip(
                reference.density_matrices, qiskit_exact.density_matrices
            )
        )

        for order in (1, 2):
            for reps in repetitions:
                route = _trotter(
                    model,
                    periods,
                    interaction,
                    kick,
                    magnetization,
                    order=order,
                    reps=int(reps),
                )
                magnetization_delta = (
                    route.magnetization_z - reference.magnetization_z
                )
                distances = np.asarray(
                    [
                        _trace_distance(left, right)
                        for left, right in zip(
                            route.density_matrices,
                            reference.density_matrices,
                        )
                    ]
                )
                gates, depth, two_qubit = _circuit_cost(
                    model,
                    interaction,
                    kick,
                    order=order,
                    reps=int(reps),
                )
                points.append(
                    ConvergencePoint(
                        configuration=configuration,
                        order=order,
                        repetitions=int(reps),
                        magnetization_rmse=float(
                            np.sqrt(np.mean(magnetization_delta**2))
                        ),
                        maximum_magnetization_error=float(
                            np.max(np.abs(magnetization_delta))
                        ),
                        final_trace_distance=float(distances[-1]),
                        maximum_trace_distance=float(np.max(distances)),
                        gates_per_period=gates,
                        depth_per_period=depth,
                        two_qubit_gates_per_period=two_qubit,
                    )
                )

    return ConvergenceStudy(
        periods,
        {
            name: asdict(model.config)
            for name, model in configurations.items()
        },
        exact_agreement,
        tuple(points),
    )
