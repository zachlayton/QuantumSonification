"""Revisioned OSC contract for optimization, sound, and geometry clients."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from .model import HexanyProblem
from .optimizers import OptimizationStep, OptimizationTrace


@dataclass
class GeometricOptimizationOSCPublisher:
    client: Any
    root: str = "/qmw/geometric_opt"
    sleep: Callable[[float], None] = time.sleep

    def publish_problem(self, problem: HexanyProblem, *, revision: int = 1) -> None:
        self.client.send_message(
            f"{self.root}/problem/begin",
            [revision, len(problem.vertices), len(problem.johnson_edges)],
        )
        for vertex in problem.vertices:
            self.client.send_message(
                f"{self.root}/problem/vertex",
                [
                    revision,
                    vertex.index,
                    vertex.bitmask,
                    vertex.label,
                    vertex.complement_index,
                    vertex.ratio,
                    vertex.cents,
                    float(problem.cut_values[vertex.index]),
                    float(problem.energies[vertex.index]),
                ],
            )
        for edge_index, (left, right) in enumerate(problem.johnson_edges):
            self.client.send_message(
                f"{self.root}/problem/edge",
                [revision, edge_index, left, right],
            )
        self.client.send_message(f"{self.root}/problem/end", revision)

    def publish_step(
        self,
        optimizer: str,
        step: OptimizationStep,
        *,
        revision: int = 1,
        gesture_seconds: float = 0.0,
    ) -> None:
        pause = max(0.0, float(gesture_seconds)) / 4.0
        prefix = f"{self.root}/frame"
        self.client.send_message(f"{prefix}/begin", [revision, optimizer, step.index])
        self.client.send_message(
            f"{prefix}/theta", [revision, optimizer, step.index, *step.theta]
        )
        self.client.send_message(
            f"{prefix}/summary",
            [
                revision,
                optimizer,
                step.index,
                step.objective_before,
                step.objective,
                step.expected_cut,
                step.approximation_ratio,
                step.optimum_probability,
                step.entropy_bits,
                step.participation,
                step.phase_order,
                step.geodesic_step,
                step.cumulative_geodesic,
                step.shell_leakage,
                step.gradient_norm,
                step.model_evaluations,
            ],
        )
        for probe in step.probes:
            common = [revision, optimizer, step.index, probe.index]
            self.client.send_message(f"{prefix}/probe/begin", [*common, *probe.delta])
            self.client.send_message(
                f"{prefix}/probe/plus", [*common, probe.expectation_plus]
            )
            self.sleep(pause)
            self.client.send_message(
                f"{prefix}/probe/minus", [*common, probe.expectation_minus]
            )
            self.sleep(pause)
            self.client.send_message(
                f"{prefix}/probe/gradient", [*common, *probe.gradient]
            )
            self.client.send_message(f"{prefix}/probe/end", [*common, probe.difference])
        for vertex_index, (probability, phase) in enumerate(
            zip(step.probabilities, step.phases)
        ):
            self.client.send_message(
                f"{prefix}/vertex",
                [revision, optimizer, step.index, vertex_index, probability, phase],
            )
        for edge_index, (left, right, current) in enumerate(step.edge_currents):
            self.client.send_message(
                f"{prefix}/edge",
                [revision, optimizer, step.index, edge_index, left, right, current],
            )
        if step.acoustic_feedback is not None:
            frame = step.acoustic_feedback
            self.client.send_message(
                f"{prefix}/feedback",
                [
                    revision,
                    optimizer,
                    step.index,
                    frame.energy,
                    frame.centroid,
                    frame.flux,
                    frame.stereo_balance,
                    frame.resonance,
                ],
            )
        if step.feedback_controls is not None:
            controls = step.feedback_controls
            self.client.send_message(
                f"{prefix}/controls",
                [
                    revision,
                    optimizer,
                    step.index,
                    controls.source_step,
                    controls.epsilon,
                    controls.batch_size,
                    controls.learning_rate,
                    controls.perturbation_polarity,
                ],
            )
        self.client.send_message(f"{prefix}/end", [revision, optimizer, step.index])

    def publish_trace(
        self,
        trace: OptimizationTrace,
        *,
        revision: int = 1,
        gesture_seconds: float = 0.0,
        step_pause: float = 0.0,
    ) -> None:
        self.client.send_message(
            f"{self.root}/trace/begin", [revision, trace.optimizer, len(trace.steps)]
        )
        for step in trace.steps:
            self.publish_step(
                trace.optimizer,
                step,
                revision=revision,
                gesture_seconds=gesture_seconds,
            )
            self.sleep(max(0.0, step_pause))
        self.client.send_message(
            f"{self.root}/trace/end",
            [revision, trace.optimizer, trace.final.index],
        )
