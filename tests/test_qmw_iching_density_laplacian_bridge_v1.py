import unittest

import numpy as np

import qmw_iching_density_laplacian_bridge_v1 as bridge


class TestPhaseAwareBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = bridge.build_control_frame(seed=42, depth=1, revision=108)
        (cls.frame, cls.rho, cls.rho_lu, cls.adjacency,
         cls.laplacian, cls.field) = cls.result

    def test_frozen_reading_and_xor(self):
        self.assertEqual(self.frame.transformed,
                         self.frame.primary ^ self.frame.moving_mask)
        self.assertEqual(self.frame.revision, 108)

    def test_four_qubit_density_is_physical(self):
        self.assertEqual(self.rho.shape, (16, 16))
        self.assertTrue(np.allclose(self.rho, self.rho.conj().T, atol=1e-12))
        self.assertAlmostEqual(np.trace(self.rho).real, 1.0, places=12)
        self.assertGreaterEqual(np.linalg.eigvalsh(self.rho).min(), -1e-10)

    def test_phase_graph_is_hermitian(self):
        self.assertEqual(len(self.frame.edges), 64 * 6 // 2)
        self.assertTrue(np.allclose(self.adjacency, self.adjacency.conj().T, atol=1e-12))
        self.assertTrue(np.allclose(self.laplacian, self.laplacian.conj().T, atol=1e-12))
        self.assertGreaterEqual(np.linalg.eigvalsh(self.laplacian).min(), -1e-10)

    def test_line_phases_and_gauge_fluxes_are_bounded(self):
        self.assertEqual(len(self.frame.line_phases), 6)
        self.assertEqual(len(self.frame.cycle_fluxes), 15)
        for item in self.frame.line_phases:
            self.assertGreaterEqual(item.phase_radians, -np.pi)
            self.assertLessEqual(item.phase_radians, np.pi)
        for item in self.frame.cycle_fluxes:
            self.assertGreaterEqual(item.flux_radians, -np.pi)
            self.assertLessEqual(item.flux_radians, np.pi)

    def test_cycle_flux_is_gauge_invariant(self):
        rng = np.random.default_rng(9)
        phases = rng.uniform(-np.pi, np.pi, 64)
        gauge = np.exp(1j * phases)
        transformed = gauge[:, None].conj() * self.adjacency * gauge[None, :]
        before = bridge.square_cycle_fluxes(self.adjacency, self.frame.primary)
        after = bridge.square_cycle_fluxes(transformed, self.frame.primary)
        self.assertTrue(np.allclose([x.flux_radians for x in before],
                                    [x.flux_radians for x in after], atol=1e-12))

    def test_atomic_osc_transaction(self):
        messages = list(bridge.osc_messages(self.frame, self.rho))
        self.assertEqual(messages[0][0], bridge.NETWORK_ROOT + "/begin")
        self.assertEqual(messages[-1], (bridge.NETWORK_ROOT + "/end", [108]))
        self.assertEqual(sum(path.endswith("/real_row") for path, _ in messages), 16)
        self.assertEqual(sum(path.endswith("/imag_row") for path, _ in messages), 16)
        for _path, arguments in messages:
            self.assertEqual(arguments[0], 108)


if __name__ == "__main__":
    unittest.main()
