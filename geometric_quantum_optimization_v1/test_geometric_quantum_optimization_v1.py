from __future__ import annotations

import unittest

import numpy as np

from geometric_quantum_optimization_v1.experiment import run_comparison
from geometric_quantum_optimization_v1.feedback import controls_from_feedback
from geometric_quantum_optimization_v1.model import (
    HexanyOptimizationModel,
    build_hexany_problem,
    fubini_study_distance,
)
from geometric_quantum_optimization_v1.optimizers import (
    optimize_acoustic_feedback_spsa,
    optimize_quantum_natural_gradient,
    optimize_spsa,
)
from geometric_quantum_optimization_v1.osc_publisher import (
    GeometricOptimizationOSCPublisher,
)


class CaptureClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class HexanyProblemTests(unittest.TestCase):
    def test_problem_is_johnson_four_two_with_complement_symmetry(self) -> None:
        problem = build_hexany_problem()
        self.assertEqual(len(problem.vertices), 6)
        self.assertEqual(len(problem.johnson_edges), 12)
        degrees = [0] * 6
        for left, right in problem.johnson_edges:
            degrees[left] += 1
            degrees[right] += 1
        self.assertEqual(degrees, [4] * 6)
        self.assertEqual(len(problem.optimum_vertices), 2)
        for vertex in problem.vertices:
            complement = problem.vertices[vertex.complement_index]
            self.assertEqual(vertex.bitmask ^ complement.bitmask, 0b1111)
            self.assertAlmostEqual(
                problem.cut_values[vertex.index],
                problem.cut_values[vertex.complement_index],
            )


class QuantumGeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = HexanyOptimizationModel(layers=2)
        self.theta = np.array([0.31, -0.52, 0.77, 0.24])

    def test_ansatz_is_normalized_and_confined_to_shell(self) -> None:
        state = self.model.state(self.theta)
        self.assertAlmostEqual(float(np.vdot(state, state).real), 1.0, places=12)
        self.assertEqual(self.model.metrics_from_state(state).shell_leakage, 0.0)

    def test_fubini_study_distance_ignores_global_phase(self) -> None:
        state = self.model.state(self.theta)
        self.assertAlmostEqual(
            fubini_study_distance(state, np.exp(1j * 1.234) * state),
            0.0,
            places=7,
        )

    def test_quantum_metric_is_positive_semidefinite(self) -> None:
        gradient, metric = self.model.objective_gradient_and_metric(self.theta)
        self.assertEqual(gradient.shape, (4,))
        np.testing.assert_allclose(metric, metric.T, atol=1e-10)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(metric))), -1e-8)


class FeedbackTests(unittest.TestCase):
    def test_feedback_controls_are_bounded_and_causal(self) -> None:
        model = HexanyOptimizationModel(layers=2)
        trace = optimize_acoustic_feedback_spsa(
            model,
            np.array([0.4, -0.7, 0.2, 0.6]),
            steps=8,
            seed=12,
        )
        for step in trace.steps[1:]:
            self.assertIsNotNone(step.acoustic_feedback)
            self.assertIsNotNone(step.feedback_controls)
            controls = step.feedback_controls
            assert controls is not None
            self.assertEqual(controls.source_step, step.index - 1)
            self.assertGreater(controls.epsilon, 0.0)
            self.assertGreaterEqual(controls.batch_size, 1)
            self.assertLessEqual(controls.batch_size, 8)
            self.assertGreater(controls.learning_rate, 0.0)
            self.assertEqual(len(step.probes), controls.batch_size)
            self.assertEqual(step.shell_leakage, 0.0)

    def test_zero_mix_recovers_base_controls(self) -> None:
        model = HexanyOptimizationModel()
        state = model.state(np.zeros(4))
        trace = optimize_acoustic_feedback_spsa(
            model, np.zeros(4), steps=1, feedback_mix=0.0
        )
        frame = trace.steps[0].acoustic_feedback
        assert frame is not None
        controls = controls_from_feedback(
            frame,
            base_epsilon=0.12,
            base_batch_size=3,
            base_learning_rate=0.18,
            mix=0.0,
        )
        self.assertAlmostEqual(controls.epsilon, 0.12)
        self.assertEqual(controls.batch_size, 3)
        self.assertAlmostEqual(controls.learning_rate, 0.18)
        self.assertEqual(state.shape, (6,))

    def test_zero_mix_reproduces_ordinary_spsa_exactly(self) -> None:
        model = HexanyOptimizationModel()
        theta = np.array([0.4, -0.7, 0.2, 0.6])
        baseline = optimize_spsa(model, theta, steps=12, seed=23)
        open_loop = optimize_acoustic_feedback_spsa(
            model,
            theta,
            steps=12,
            seed=23,
            feedback_mix=0.0,
        )
        np.testing.assert_allclose(baseline.final.theta, open_loop.final.theta)
        self.assertAlmostEqual(baseline.final.objective, open_loop.final.objective)
        self.assertEqual(
            baseline.final.model_evaluations,
            open_loop.final.model_evaluations,
        )


class OptimizationTests(unittest.TestCase):
    def test_natural_gradient_trace_is_monotone(self) -> None:
        model = HexanyOptimizationModel(layers=2)
        trace = optimize_quantum_natural_gradient(
            model, np.array([0.4, -0.7, 0.2, 0.6]), steps=10
        )
        objectives = np.array([step.objective for step in trace.steps])
        self.assertTrue(np.all(np.diff(objectives) <= 1e-10))
        self.assertLess(objectives[-1], objectives[0])

    def test_three_condition_comparison_is_reproducible(self) -> None:
        first = run_comparison(
            steps_spsa=5, steps_feedback=5, steps_natural_gradient=3, seed=19
        )
        second = run_comparison(
            steps_spsa=5, steps_feedback=5, steps_natural_gradient=3, seed=19
        )
        self.assertEqual(first.initial_theta, second.initial_theta)
        for left, right in zip(first.traces, second.traces):
            self.assertEqual(left.final.theta, right.final.theta)


class OSCContractTests(unittest.TestCase):
    def test_problem_and_feedback_frame_are_transactional(self) -> None:
        result = run_comparison(
            steps_spsa=1, steps_feedback=2, steps_natural_gradient=1, seed=5
        )
        client = CaptureClient()
        publisher = GeometricOptimizationOSCPublisher(client, sleep=lambda _: None)
        publisher.publish_problem(result.problem, revision=17)
        publisher.publish_trace(result.acoustic_feedback_spsa, revision=17)
        addresses = [address for address, _ in client.messages]
        self.assertEqual(addresses[0], "/qmw/geometric_opt/problem/begin")
        self.assertEqual(
            addresses[addresses.index("/qmw/geometric_opt/problem/end")],
            "/qmw/geometric_opt/problem/end",
        )
        self.assertEqual(addresses.count("/qmw/geometric_opt/problem/vertex"), 6)
        self.assertEqual(addresses.count("/qmw/geometric_opt/problem/edge"), 12)
        self.assertEqual(addresses.count("/qmw/geometric_opt/frame/begin"), 3)
        self.assertEqual(addresses.count("/qmw/geometric_opt/frame/end"), 3)
        self.assertGreater(addresses.count("/qmw/geometric_opt/frame/probe/plus"), 0)
        self.assertEqual(
            addresses.count("/qmw/geometric_opt/frame/probe/plus"),
            addresses.count("/qmw/geometric_opt/frame/probe/minus"),
        )
        self.assertEqual(addresses.count("/qmw/geometric_opt/frame/feedback"), 3)
        self.assertEqual(addresses.count("/qmw/geometric_opt/frame/controls"), 2)
        self.assertEqual(addresses[-1], "/qmw/geometric_opt/trace/end")


if __name__ == "__main__":
    unittest.main()
