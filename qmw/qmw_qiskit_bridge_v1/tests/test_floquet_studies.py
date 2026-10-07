from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qmw_qiskit_bridge_v1.experiments import (
    generate_floquet_comparison_report,
    run_floquet_convergence_study,
    run_floquet_noise_control_study,
)


class ConvergenceStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.study = run_floquet_convergence_study(
            periods=5, repetitions=(1, 2, 4)
        )

    def test_exact_routes_agree_for_both_configurations(self) -> None:
        for error in self.study.exact_route_maximum_trace_distance.values():
            self.assertLess(error, 1e-10)

    def test_commuting_control_is_exact_at_every_product_formula_setting(self) -> None:
        points = [
            point
            for point in self.study.points
            if point.configuration == "commuting_control"
        ]
        self.assertTrue(points)
        self.assertLess(max(point.maximum_trace_distance for point in points), 1e-10)

    def test_noncommuting_state_error_converges_with_repetitions(self) -> None:
        for order in (1, 2):
            points = sorted(
                (
                    point
                    for point in self.study.points
                    if point.configuration == "noncommuting_benchmark"
                    and point.order == order
                ),
                key=lambda point: point.repetitions,
            )
            errors = [point.maximum_trace_distance for point in points]
            self.assertTrue(all(right < left for left, right in zip(errors, errors[1:])))
            self.assertTrue(
                all(
                    right.gates_per_period > left.gates_per_period
                    for left, right in zip(points, points[1:])
                )
            )


class NoiseControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.study = run_floquet_noise_control_study(
            periods=4, noise_scales=(0.0, 0.5, 1.0), seed=17
        )

    def test_zero_noise_is_the_explicit_baseline(self) -> None:
        zero = self.study.points[0]
        self.assertEqual(zero.noise_scale, 0.0)
        self.assertLess(zero.maximum_trace_distance_from_zero_noise, 1e-12)
        self.assertAlmostEqual(zero.final_purity, 1.0, places=10)

    def test_controlled_noise_departs_from_baseline_and_reduces_purity(self) -> None:
        noisy = self.study.points[-1]
        self.assertGreater(noisy.maximum_trace_distance_from_zero_noise, 1e-4)
        self.assertLess(noisy.final_purity, 0.99)


class ReportTests(unittest.TestCase):
    def test_json_and_npz_are_consistent_and_rerunnable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            json_path, npz_path = generate_floquet_comparison_report(
                directory,
                periods=3,
                repetitions=(1, 2),
                noise_scales=(0.0, 1.0),
            )
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            arrays = np.load(npz_path)
            self.assertEqual(payload["schema"], "qmw.floquet_execution_comparison.v1")
            self.assertEqual(payload["hardware"]["status"], "deferred")
            self.assertEqual(payload["software"]["qiskit"], version("qiskit"))
            self.assertEqual(
                payload["conventions"]["basis_order"], "|q3 q2 q1 q0>"
            )
            self.assertIn(
                "transverse_fields",
                payload["convergence"]["configurations"]["noncommuting_benchmark"],
            )
            self.assertEqual(
                len(payload["convergence"]["points"]),
                len(arrays["convergence_order"]),
            )
            self.assertEqual(
                len(payload["noise_controls"]["points"]),
                len(arrays["noise_scale"]),
            )


if __name__ == "__main__":
    unittest.main()
