"""Independent quadrature, analytic Fourier and finite graph checks."""
import unittest
import numpy as np
from qmw.core import Domain, StateData, ObservableData, PhysicsFrame
from qmw.projection import RegionProjector, ModalProjector, GraphModes, GraphModalProjector, MODULE_SPECS


def make_frame(domain, state, observables=None):
    return PhysicsFrame(0, 0.0, 0.0, "projection-test", domain, state,
                        ObservableData() if observables is None else observables)


class RegionProjectionTests(unittest.TestCase):
    def test_quadrature_partition_probability_energy_charge(self):
        domain = Domain.periodic(2048, 10.0)
        x = domain.coordinates
        psi = np.ones(domain.size, complex) / np.sqrt(domain.length)
        energy = 3.0 + np.cos(2 * np.pi * x / domain.length)
        charge = -2.0 + 0.4 * np.sin(4 * np.pi * x / domain.length)
        frame = make_frame(domain, StateData(psi=psi), ObservableData(
            total_energy_density=energy, charge_density=charge))
        projector = RegionProjector(domain, 16)
        regions = projector.project(frame)
        np.testing.assert_array_equal(projector.masks.sum(axis=0), np.ones(domain.size))
        np.testing.assert_allclose(regions.probability, np.full(16, 1 / 16), atol=2e-15)
        self.assertAlmostEqual(regions.energy.sum(), 30.0, places=12)
        self.assertAlmostEqual(regions.charge.sum(), -20.0, places=12)
        self.assertIsNone(regions.incoming_energy_flux)
        # Projection is read-only with respect to the state.
        np.testing.assert_array_equal(frame.state.psi, psi)

    def test_incoming_flux_analytic_derivative_and_periodic_sum(self):
        domain = Domain.periodic(256, 2 * np.pi)
        x = domain.coordinates
        psi = np.ones(domain.size, complex) / np.sqrt(domain.length)
        flux = np.sin(3 * x) + 0.2 * np.cos(x)
        expected_divergence = 3 * np.cos(3 * x) - 0.2 * np.sin(x)
        projector = RegionProjector(domain, 13)
        regions = projector.project(make_frame(domain, StateData(psi=psi), ObservableData(
            probability_current=flux, energy_flux=2 * flux, charge_current=-flux)))
        expected = -domain.spacing[0] * (projector.masks @ expected_divergence)
        np.testing.assert_allclose(regions.incoming_probability_flux, expected, atol=2e-14)
        np.testing.assert_allclose(regions.incoming_energy_flux, 2 * expected, atol=4e-14)
        np.testing.assert_allclose(regions.incoming_charge_flux, -expected, atol=2e-14)
        self.assertAlmostEqual(regions.incoming_energy_flux.sum(), 0.0, places=13)

    def test_basis_bins_no_spatial_flux(self):
        domain = Domain.basis(16)
        populations = np.arange(1, 17, dtype=float)
        populations /= populations.sum()
        frame = make_frame(domain, StateData(rho=np.diag(populations)))
        regions = RegionProjector(domain, 4).project(frame)
        np.testing.assert_allclose(regions.probability, populations.reshape(4, 4).sum(axis=1))
        np.testing.assert_allclose(regions.centers, [1.5, 5.5, 9.5, 13.5])
        self.assertIsNone(regions.incoming_probability_flux)
        self.assertIsNone(regions.energy)

    def test_scalar_energy_and_charge_without_probability(self):
        domain = Domain.periodic(64, 8.0)
        phi = np.ones(64, complex)
        pi = 1j * phi
        frame = make_frame(domain, StateData(phi=phi, pi=pi), ObservableData(
            total_energy_density=np.full(64, 2.0), charge_density=np.ones(64)))
        regions = RegionProjector(domain, 4).project(frame)
        np.testing.assert_allclose(regions.energy, [4, 4, 4, 4])
        np.testing.assert_allclose(regions.charge, [2, 2, 2, 2])
        self.assertIsNone(regions.probability)

    def test_reject_history_domain_and_wrong_frame_domain(self):
        with self.assertRaises(ValueError):
            RegionProjector(Domain("time_history", (32,)))
        d1, d2 = Domain.periodic(64, 8.0), Domain.periodic(64, 16.0)
        frame = make_frame(d2, StateData(psi=np.ones(64, complex)))
        with self.assertRaises(ValueError):
            RegionProjector(d1).project(frame)


class ModalProjectionTests(unittest.TestCase):
    def test_weighted_orthonormal_basis_and_explicit_operator(self):
        domain = Domain.periodic(2048, 64.0)
        projector = ModalProjector(domain, 16)
        gram = projector.basis.conj().T @ (domain.weights[:, None] * projector.basis)
        np.testing.assert_allclose(gram, np.eye(16), atol=2e-15)
        np.testing.assert_array_equal(projector.mode_indices[:7], [0, 1, -1, 2, -2, 3, -3])
        np.testing.assert_allclose(projector.eigenvalues, (2 * np.pi * projector.mode_indices / 64.0) ** 2)
        self.assertIn("not_energy_or_audio_hz", projector.operator_semantics)

    def test_partial_capture_and_exact_complex_coefficients(self):
        domain = Domain.periodic(128, 2 * np.pi)
        x, length = domain.coordinates, domain.length
        # Three analytically orthogonal components: modes 0,+1 and +19.
        psi = (np.sqrt(0.2) + 1j * np.sqrt(0.5) * np.exp(1j * x)
               + np.sqrt(0.3) * np.exp(19j * x)) / np.sqrt(length)
        result = ModalProjector(domain, 16).project(make_frame(domain, StateData(psi=psi)))
        expected_coefficients = np.zeros(16, complex)
        expected_coefficients[0] = np.sqrt(0.2)
        expected_coefficients[1] = 1j * np.sqrt(0.5)
        np.testing.assert_allclose(result.coefficients, expected_coefficients, atol=4e-15)
        self.assertAlmostEqual(result.captured_norm, 0.7, places=13)
        self.assertAlmostEqual(domain.spacing[0] * np.sum(np.abs(psi) ** 2), 1.0, places=13)

    def test_full_fourier_basis_handles_even_nyquist_once(self):
        domain = Domain.periodic(32, 5.0)
        projector = ModalProjector(domain, 32)
        self.assertEqual(len(set(projector.mode_indices)), 32)
        self.assertIn(-16, projector.mode_indices)
        gram = domain.spacing[0] * projector.basis.conj().T @ projector.basis
        np.testing.assert_allclose(gram, np.eye(32), atol=4e-15)

    def test_mixed_state_has_populations_without_phase(self):
        domain = Domain.basis(16)
        vector = np.zeros(16, complex)
        vector[0], vector[3] = 1 / np.sqrt(2), 1j / np.sqrt(2)
        rho = 0.6 * np.outer(vector, vector.conj())
        rho[7, 7] += 0.4
        projector = ModalProjector(domain, 16)
        result = projector.project(make_frame(domain, StateData(rho=rho)))
        expected = np.zeros(16)
        expected[0], expected[3], expected[7] = 0.3, 0.3, 0.4
        np.testing.assert_allclose(result.populations, expected, atol=2e-16)
        self.assertIsNone(result.coefficients)
        self.assertEqual(result.basis_id, "computational")
        self.assertEqual(result.operator_semantics, "basis_index_not_energy")
        np.testing.assert_array_equal(result.eigenvalues, np.arange(16))
        self.assertAlmostEqual(result.captured_norm, 1.0, places=14)

    def test_computational_pure_state_and_truncation(self):
        domain = Domain.basis(16)
        psi = np.zeros(16, complex)
        psi[2], psi[14] = np.sqrt(0.75), 0.5j
        result = ModalProjector(domain, 8).project(make_frame(domain, StateData(psi=psi)))
        self.assertAlmostEqual(result.captured_norm, 0.75, places=14)
        np.testing.assert_array_equal(result.coefficients, psi[:8])

    def test_scalar_modes_declared_as_field_l2_amplitudes(self):
        domain = Domain.periodic(64, 8.0)
        phi = 2 * np.ones(64, complex)
        result = ModalProjector(domain, 16).project(make_frame(
            domain, StateData(phi=phi, pi=np.zeros(64, complex))))
        self.assertAlmostEqual(result.captured_norm, 32.0, places=12)
        self.assertIn("scalar_field_l2_amplitudes_not_quantum_probabilities", result.operator_semantics)

    def test_reject_history_and_nonhermitian_rho(self):
        with self.assertRaises(ValueError):
            ModalProjector(Domain("time_history", (32,)))
        rho = np.eye(16, dtype=complex) / 16
        rho[0, 1] = 0.1j
        with self.assertRaises(ValueError):
            ModalProjector(Domain.basis(16)).project(make_frame(
                Domain.basis(16), StateData(rho=rho)))


class GraphProjectionTests(unittest.TestCase):
    def test_path_spectrum_and_zero_mode_retained(self):
        nodes = 9
        a = np.zeros((nodes, nodes))
        for index in range(nodes - 1):
            a[index, index + 1] = a[index + 1, index] = 1.0
        modes = GraphModes(a)
        # Analytic spectrum of the combinatorial unweighted path Laplacian.
        expected = 2 - 2 * np.cos(np.pi * np.arange(nodes) / nodes)
        np.testing.assert_allclose(modes.eigenvalues, expected, atol=1e-14)
        np.testing.assert_allclose(modes.laplacian @ modes.basis,
                                   modes.basis * modes.eigenvalues[None, :], atol=2e-15)
        domain = Domain("graph", (nodes,))
        result = GraphModalProjector(domain, modes).project(make_frame(
            domain, StateData(psi=np.ones(nodes) / np.sqrt(nodes))))
        self.assertAlmostEqual(result.populations[0], 1.0, places=13)
        self.assertEqual(result.populations.size, nodes)
        self.assertAlmostEqual(result.eigenvalues[0], 0.0, places=13)

    def test_mixed_projection_in_graph_basis(self):
        a = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
        modes = GraphModes(a)
        low = np.ones(3) / np.sqrt(3)
        high = np.array([1, -2, 1]) / np.sqrt(6)
        rho = 0.25 * np.outer(low, low) + 0.75 * np.outer(high, high)
        domain = Domain.basis(3)
        result = GraphModalProjector(domain, modes).project(make_frame(domain, StateData(rho=rho)))
        np.testing.assert_allclose(result.populations, [0.25, 0, 0.75], atol=4e-16)
        self.assertIsNone(result.coefficients)
        self.assertAlmostEqual(result.captured_norm, 1.0, places=14)
        self.assertIn("not_quantum_energy_or_audio_hz", result.operator_semantics)

    def test_disconnected_graph_retains_all_zero_modes(self):
        modes = GraphModes(np.zeros((3, 3)))
        np.testing.assert_array_equal(modes.eigenvalues, [0.0, 0.0, 0.0])
        np.testing.assert_allclose(modes.basis.conj().T @ modes.basis, np.eye(3))

    def test_invalid_adjacency_rejected(self):
        for a in (np.zeros((2, 3)), [[0, -1], [-1, 0]], [[0, 1], [0, 0]],
                  [[1, 0], [0, 0]], [[0, np.nan], [np.nan, 0]]):
            with self.subTest(adjacency=a):
                with self.assertRaises(ValueError):
                    GraphModes(a)

    def test_metadata_exposes_equations_assumptions_and_destinations(self):
        self.assertEqual(len(MODULE_SPECS), 4)
        for spec in MODULE_SPECS:
            self.assertTrue(spec.equation_latex)
            self.assertTrue(spec.equation_text)
            self.assertTrue(spec.assumptions)
            self.assertTrue(spec.destinations)


if __name__ == "__main__":
    unittest.main()
