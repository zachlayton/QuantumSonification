"""Three-condition experiment and durable JSON export."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from .model import HexanyOptimizationModel, HexanyProblem, build_hexany_problem
from .optimizers import (
    OptimizationTrace,
    optimize_acoustic_feedback_spsa,
    optimize_quantum_natural_gradient,
    optimize_spsa,
)


@dataclass(frozen=True)
class ExperimentResult:
    problem: HexanyProblem
    initial_theta: tuple[float, ...]
    spsa: OptimizationTrace
    acoustic_feedback_spsa: OptimizationTrace
    natural_gradient: OptimizationTrace

    @property
    def traces(self) -> tuple[OptimizationTrace, ...]:
        return self.spsa, self.acoustic_feedback_spsa, self.natural_gradient

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "qmw.geometric_quantum_optimization.v2",
            "problem": self.problem.to_dict(),
            "initial_theta": list(self.initial_theta),
            "traces": {trace.optimizer: trace.to_dict() for trace in self.traces},
        }

    def export_json(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return output


def run_comparison(
    *,
    steps_spsa: int = 60,
    steps_feedback: int = 60,
    steps_natural_gradient: int = 24,
    seed: int = 731,
    layers: int = 2,
    feedback_mix: float = 1.0,
    initial_theta: np.ndarray | None = None,
) -> ExperimentResult:
    problem = build_hexany_problem()
    model = HexanyOptimizationModel(problem, layers=layers)
    theta = (
        np.random.default_rng(seed).uniform(-0.9, 0.9, size=model.parameter_count)
        if initial_theta is None
        else np.asarray(initial_theta, dtype=np.float64)
    )
    if theta.shape != (model.parameter_count,):
        raise ValueError(f"initial_theta must have shape ({model.parameter_count},)")
    return ExperimentResult(
        problem=problem,
        initial_theta=tuple(float(value) for value in theta),
        spsa=optimize_spsa(model, theta, steps=steps_spsa, seed=seed),
        acoustic_feedback_spsa=optimize_acoustic_feedback_spsa(
            model,
            theta,
            steps=steps_feedback,
            seed=seed,
            feedback_mix=feedback_mix,
        ),
        natural_gradient=optimize_quantum_natural_gradient(
            model,
            theta,
            steps=steps_natural_gradient,
            seed=seed,
        ),
    )
