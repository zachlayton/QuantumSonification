"""Controlled Aer noise sweep over one fixed compiled Floquet circuit family."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .floquet_comparison import (
    _aer_noisy,
    _model_operators,
    _qmw_dense,
    _trace_distance,
    noncommuting_benchmark_model,
)


@dataclass(frozen=True)
class NoiseControlPoint:
    noise_scale: float
    single_qubit_error: float
    two_qubit_error: float
    maximum_trace_distance_from_qmw: float
    maximum_trace_distance_from_zero_noise: float
    final_trace_distance_from_zero_noise: float
    final_purity: float
    minimum_purity: float

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class NoiseControlStudy:
    periods: int
    base_single_qubit_error: float
    base_two_qubit_error: float
    points: tuple[NoiseControlPoint, ...]
    circuit_control: str = "same order-2 compiled circuit and gate alphabet"

    def as_dict(self) -> dict[str, Any]:
        return {
            "periods": self.periods,
            "base_single_qubit_error": self.base_single_qubit_error,
            "base_two_qubit_error": self.base_two_qubit_error,
            "circuit_control": self.circuit_control,
            "points": [point.as_dict() for point in self.points],
        }


def run_floquet_noise_control_study(
    *,
    periods: int = 16,
    noise_scales: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0),
    base_single_qubit_error: float = 0.0015,
    base_two_qubit_error: float = 0.012,
    seed: int = 2718,
) -> NoiseControlStudy:
    if periods < 1:
        raise ValueError("periods must be positive")
    if not noise_scales or any(float(scale) < 0 for scale in noise_scales):
        raise ValueError("noise scales must be non-negative")
    if 0.0 not in noise_scales:
        raise ValueError("noise_scales must include the zero-noise control")

    model = noncommuting_benchmark_model()
    interaction, kick, magnetization_op = _model_operators(model)
    magnetization = np.asarray(magnetization_op.to_matrix())
    reference = _qmw_dense(model, periods, magnetization)
    routes = {}
    for scale in noise_scales:
        routes[float(scale)] = _aer_noisy(
            model,
            periods,
            interaction,
            kick,
            magnetization,
            single_qubit_error=base_single_qubit_error * float(scale),
            two_qubit_error=base_two_qubit_error * float(scale),
            seed=seed,
        )
    zero_noise = routes[0.0]

    points = []
    for scale in noise_scales:
        route = routes[float(scale)]
        from_qmw = np.asarray(
            [
                _trace_distance(left, right)
                for left, right in zip(
                    route.density_matrices, reference.density_matrices
                )
            ]
        )
        from_zero = np.asarray(
            [
                _trace_distance(left, right)
                for left, right in zip(
                    route.density_matrices, zero_noise.density_matrices
                )
            ]
        )
        purities = np.real(
            np.einsum(
                "tij,tji->t",
                route.density_matrices,
                route.density_matrices,
            )
        )
        points.append(
            NoiseControlPoint(
                noise_scale=float(scale),
                single_qubit_error=base_single_qubit_error * float(scale),
                two_qubit_error=base_two_qubit_error * float(scale),
                maximum_trace_distance_from_qmw=float(np.max(from_qmw)),
                maximum_trace_distance_from_zero_noise=float(np.max(from_zero)),
                final_trace_distance_from_zero_noise=float(from_zero[-1]),
                final_purity=float(purities[-1]),
                minimum_purity=float(np.min(purities)),
            )
        )

    return NoiseControlStudy(
        periods,
        base_single_qubit_error,
        base_two_qubit_error,
        tuple(points),
    )
