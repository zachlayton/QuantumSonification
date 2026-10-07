from __future__ import annotations

import unittest

import numpy as np
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

from qmw_pauli_basis_laboratory_v2.bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
    transverse_ising_hamiltonian,
)
from qmw_pauli_basis_laboratory_v2.laboratory import (
    density_from_preset,
    run_basis_laboratory,
)
from qmw_pauli_basis_laboratory_v2.validation import validate_basis_operator


class BasisOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rho = density_from_preset("ghz")
        cls.hamiltonian = transverse_ising_hamiltonian(4)

    def test_initial_operators_preserve_density_invariants(self) -> None:
        operators = [
            IdentityBasis(),
            HadamardBasis(),
            QFTBasis(),
            HamiltonianEigenbasis(self.hamiltonian),
        ]
        for basis in operators:
            with self.subTest(basis=basis.name):
                report = validate_basis_operator(basis, self.rho)
                self.assertTrue(report.passed)
                self.assertLessEqual(report.covariance_error, 1e-9)
                self.assertLessEqual(report.pullback_error, 1e-9)

    def test_identity_is_exact_no_op(self) -> None:
        transformed = IdentityBasis().transform(self.rho)
        np.testing.assert_array_equal(transformed, self.rho)

    def test_hadamard_maps_zero_state_to_uniform_population(self) -> None:
        zero = np.zeros((16, 16), dtype=complex)
        zero[0, 0] = 1.0
        transformed = HadamardBasis().transform(zero)
        np.testing.assert_allclose(
            np.real(np.diag(transformed)),
            np.full(16, 1.0 / 16.0),
            atol=1e-12,
        )

    def test_qft_matches_qiskit_gate_convention(self) -> None:
        expected = Operator(QFTGate(4)).data
        actual = QFTBasis().unitary(16)
        np.testing.assert_allclose(actual, expected, atol=1e-12)

    def test_hamiltonian_transform_diagonalizes_hamiltonian(self) -> None:
        basis = HamiltonianEigenbasis(self.hamiltonian)
        unitary = basis.unitary(16)
        transformed = unitary @ self.hamiltonian @ unitary.conj().T
        np.testing.assert_allclose(
            transformed,
            np.diag(basis.eigenvalues),
            atol=1e-10,
        )

    def test_invalid_density_is_rejected(self) -> None:
        invalid = np.eye(16, dtype=complex)
        with self.assertRaisesRegex(ValueError, "trace 1"):
            QFTBasis().transform(invalid)


class BasisLaboratoryTests(unittest.TestCase):
    def test_identity_comparison_uses_identical_sampled_score(self) -> None:
        result = run_basis_laboratory(
            IdentityBasis(),
            preset="ghz",
            shots=128,
            seed=11,
        )
        self.assertEqual(result.schema, "qmw.pauli_basis_laboratory.v2")
        self.assertEqual(
            [row.counts for row in result.computational_basis.settings],
            [row.counts for row in result.experimental_basis.settings],
        )
        self.assertTrue(
            all(item.exact_delta == 0.0 for item in result.observable_comparisons)
        )

    def test_qft_outputs_preserve_full4q_contract(self) -> None:
        result = run_basis_laboratory(
            QFTBasis(),
            preset="weave",
            shots=128,
            seed=17,
        )
        computational, experimental = result.tomography_outputs()
        for output in (computational, experimental):
            self.assertEqual(output.schema, "qmw.full4q.tomography.v1")
            self.assertEqual(len(output.settings), 81)
            self.assertEqual(len(output.paulis), 256)
            self.assertEqual(len(output.shells), 5)
            self.assertEqual(output.total_shots, 81 * 128)
        self.assertEqual(computational.source, "basis_computational")
        self.assertEqual(computational.transform, "identity")
        self.assertEqual(experimental.source, "basis_experimental")
        self.assertEqual(experimental.transform, "qft")
        self.assertEqual(len(result.observable_comparisons), 255)
        self.assertGreater(
            result.comparison_metrics["observable_delta_max_abs_exact"],
            0.1,
        )


if __name__ == "__main__":
    unittest.main()
