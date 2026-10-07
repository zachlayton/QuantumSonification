"""Analytical channel, energy, and density-matrix validity checks."""
import unittest
import numpy as np
from qmw.core.frame import StateData
from qmw.physics.lindblad import HamiltonianBuilder, LindbladModel


class LindbladTests(unittest.TestCase):
    def test_four_qubit_builder_has_12_local_and_18_pair_energy_terms(self):
        builder = HamiltonianBuilder(4)
        self.assertEqual(len([name for name in builder.terms if name.startswith("h_")]), 12)
        self.assertEqual(len([name for name in builder.terms if name.startswith("j_")]), 18)
        for term in builder.terms.values():
            np.testing.assert_array_equal(term, term.conj().T)
            np.testing.assert_array_equal(term @ term, np.eye(16))
        h = builder.build({"h_z0": 2, "j_xx01": .3})
        np.testing.assert_array_equal(h, 2*builder.terms["h_z0"]+.3*builder.terms["j_xx01"])
        self.assertEqual(builder.term_contributions({"h_z0": 2})["h_z0"]["unit"], "scaled energy")

    def test_amplitude_damping_matches_exact_coherence_and_population(self):
        gamma, gap, hbar, duration = .83, 1.7, .7, .61
        lowering = np.array([[0, 1], [0, 0]], complex)
        model = LindbladModel(np.diag([0, gap]), [np.sqrt(gamma)*lowering], hbar=hbar)
        ket = np.array([np.sqrt(.4), 1j*np.sqrt(.6)])
        rho = np.outer(ket, ket.conj())
        evolved = model.step(StateData(rho=rho), {}, duration)
        excited = .6*np.exp(-gamma*duration)
        coherence = rho[0, 1]*np.exp((1j*gap/hbar-gamma/2)*duration)
        np.testing.assert_allclose(evolved.rho,
                                   [[1-excited, coherence], [coherence.conjugate(), excited]],
                                   atol=4e-14)
        obs = model.compute_observables(evolved)
        self.assertAlmostEqual(obs.source_power, -gamma*gap*excited, places=13)
        self.assertAlmostEqual(model.environment_energy_step(StateData(rho=rho), evolved),
                               gap*(excited-.6), places=13)
        self.assertIsNone(obs.phase)
        self.assertIsNone(obs.energy_flux)

    def test_choi_matrix_of_noncommuting_evolution_is_positive(self):
        # This checks complete positivity on an entangled auxiliary system,
        # stronger than evolving only unentangled sample states.
        gamma = .4
        lowering = np.array([[0, 1], [0, 0]], complex)
        h = np.array([[.3, .7-.2j], [.7+.2j, -.3]])
        model = LindbladModel(h, [np.sqrt(gamma)*lowering])
        choi = np.zeros((4, 4), complex)
        for i in range(2):
            for j in range(2):
                matrix_unit = np.zeros((2, 2), complex)
                matrix_unit[i, j] = 1
                channel_block = model.step(StateData(rho=matrix_unit), {}, .9).rho
                choi[2*i:2*i+2, 2*j:2*j+2] = channel_block/2
        np.testing.assert_allclose(choi, choi.conj().T, atol=2e-14)
        self.assertGreaterEqual(np.linalg.eigvalsh(choi).min(), -3e-14)
        partial_trace = np.trace(choi.reshape(2, 2, 2, 2), axis1=1, axis2=3)
        np.testing.assert_allclose(partial_trace, np.eye(2)/2, atol=2e-14)

    def test_closed_unitary_uses_energy_divided_by_hbar(self):
        gap, hbar, t = 1.3, .4, .9
        model = LindbladModel(np.diag([0, gap]), [])
        model.hbar = hbar
        rho = np.full((2, 2), .5, complex)
        result = model.step(StateData(rho=rho), {}, t)
        self.assertAlmostEqual(result.rho[0, 1], .5*np.exp(1j*gap*t/hbar), places=13)
        self.assertAlmostEqual(model.compute_observables(result).total_energy, gap/2, places=13)

    def test_invalid_trace_and_negative_eigenvalue_remain_visible(self):
        model = LindbladModel(np.diag([0, 1]), [])
        invalid = StateData(rho=np.diag([1.2, -.1]).astype(complex))
        result = model.step(invalid, {}, .3)
        diagnostics = model.diagnostics(result)
        self.assertAlmostEqual(diagnostics.trace_error, .1, places=13)
        self.assertAlmostEqual(diagnostics.positivity_error, .1, places=13)
        np.testing.assert_allclose(result.rho, invalid.rho, atol=2e-14)

    def test_four_qubit_map_preserves_validity_and_has_cached_propagator(self):
        model = LindbladModel()
        controls = {"init": "ghz", "j_xx01": .21, "j_zz23": .18}
        state = model.initialize(controls)
        for _ in range(20):
            state = model.step(state, controls, .01)
        diagnostics = model.diagnostics(state)
        self.assertLess(diagnostics.trace_error, 3e-13)
        self.assertLess(diagnostics.hermiticity_error, 3e-13)
        self.assertLess(diagnostics.positivity_error, 3e-13)
        self.assertEqual(len(model._propagators), 1)

    def test_generator_and_exponential_have_same_column_vectorization(self):
        h = np.array([[.1, .3j], [-.3j, .7]])
        c = np.array([[0, .4+.2j], [0, 0]])
        model = LindbladModel(h, [c], hbar=1.7)
        rho = np.array([[.4, .1+.2j], [.1-.2j, .6]])
        rate = (model.liouvillian() @ rho.reshape(-1, order="F")).reshape((2, 2), order="F")
        np.testing.assert_allclose(rate, model.derivative(rho), atol=2e-14)


if __name__ == "__main__":
    unittest.main()
