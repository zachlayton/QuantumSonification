from __future__ import annotations

import unittest

import numpy as np

from qmw_qiskit_bridge_v1.experiments import compare_floquet_routes


class FloquetComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compare_floquet_routes(periods=6, seed=9)

    def test_all_local_routes_share_ticks_and_observables(self) -> None:
        self.assertEqual(
            set(self.result.routes),
            {
                "qmw_dense_exact", "qiskit_statevector_exact",
                "qiskit_trotter_order_1", "qiskit_trotter_order_2", "aer_noisy",
            },
        )
        for route in self.result.routes.values():
            self.assertEqual([frame.time for frame in route.frames], list(range(7)))
            self.assertEqual(
                set(route.frames[0].expectations),
                {"magnetization_z", "return_probability", "purity"},
            )

    def test_qiskit_exact_matches_qmw_dense_authority(self) -> None:
        metrics = self.result.summary["qiskit_statevector_exact"]
        self.assertLess(metrics["maximum_trace_distance"], 1e-10)
        self.assertLess(metrics["maximum_magnetization_error"], 1e-10)

    def test_second_order_improves_over_first_order(self) -> None:
        first = self.result.summary["qiskit_trotter_order_1"]
        second = self.result.summary["qiskit_trotter_order_2"]
        self.assertLess(second["maximum_trace_distance"], first["maximum_trace_distance"])
        self.assertLess(second["final_trace_distance"], first["final_trace_distance"])

    def test_noisy_route_is_physical_and_distinct(self) -> None:
        noisy = self.result.routes["aer_noisy"]
        for rho in noisy.density_matrices:
            self.assertTrue(np.allclose(rho, rho.conj().T, atol=1e-10))
            self.assertAlmostEqual(float(np.trace(rho).real), 1.0, places=10)
            self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(rho))), -1e-10)
        self.assertGreater(self.result.summary["aer_noisy"]["maximum_trace_distance"], 1e-5)

    def test_hardware_route_is_explicitly_deferred(self) -> None:
        self.assertEqual(self.result.deferred_routes, ("ibm_runtime_v2",))


if __name__ == "__main__":
    unittest.main()
