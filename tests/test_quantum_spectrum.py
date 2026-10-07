from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

import numpy as np

from qmw.core import (
    QMWEigenTracker,
    QuantumDataBus,
    QuantumStateFrame,
    analyze_quantum_spectrum,
)
from qmw.spectral_analysis_v4 import format_spectral_report


class QuantumSpectrumTests(unittest.TestCase):
    def test_reconstructs_density_and_hamiltonian_and_energy_bridge(self) -> None:
        state = np.array([1.0, 1.0j], dtype=np.complex128) / np.sqrt(2.0)
        rho = np.outer(state, state.conj())
        hamiltonian = np.array([[0.0, 0.4], [0.4, 1.0]], dtype=np.complex128)
        spectrum = analyze_quantum_spectrum(rho, hamiltonian)
        np.testing.assert_allclose(
            spectrum.density_eigenvectors
            @ np.diag(spectrum.density_eigenvalues)
            @ spectrum.density_eigenvectors.conj().T,
            rho,
            atol=1e-10,
        )
        np.testing.assert_allclose(
            spectrum.energy_eigenvectors
            @ np.diag(spectrum.energy_eigenvalues)
            @ spectrum.energy_eigenvectors.conj().T,
            hamiltonian,
            atol=1e-10,
        )
        np.testing.assert_allclose(
            np.diag(spectrum.rho_in_energy_basis).real,
            spectrum.energy_populations,
            atol=1e-10,
        )
        np.testing.assert_allclose(
            spectrum.basis_overlap @ spectrum.density_eigenvalues,
            spectrum.energy_populations,
            atol=1e-10,
        )
        self.assertAlmostEqual(spectrum.purity, 1.0)
        self.assertAlmostEqual(spectrum.entropy, 0.0)
        self.assertAlmostEqual(spectrum.participation_rank, 1.0)

    def test_maximally_mixed_state_has_expected_statistics(self) -> None:
        rho = np.eye(4, dtype=np.complex128) / 4.0
        spectrum = analyze_quantum_spectrum(rho, np.diag([0.0, 2.0, 5.0, 9.0]))
        np.testing.assert_allclose(spectrum.density_eigenvalues, 0.25)
        np.testing.assert_allclose(spectrum.energy_populations, 0.25)
        self.assertAlmostEqual(spectrum.purity, 0.25)
        self.assertAlmostEqual(spectrum.entropy, np.log(4.0))
        self.assertAlmostEqual(spectrum.participation_rank, 4.0)

    def test_unitary_invariance_and_noncommuting_diagnostic(self) -> None:
        rho = np.diag([0.75, 0.25]).astype(np.complex128)
        unitary = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / np.sqrt(2.0)
        transformed = unitary @ rho @ unitary.conj().T
        hamiltonian = np.diag([0.0, 1.0])
        original = analyze_quantum_spectrum(rho, hamiltonian)
        rotated = analyze_quantum_spectrum(transformed, hamiltonian)
        np.testing.assert_allclose(
            original.density_eigenvalues, rotated.density_eigenvalues, atol=1e-10
        )
        self.assertAlmostEqual(original.purity, rotated.purity)
        self.assertAlmostEqual(original.entropy, rotated.entropy)
        self.assertGreater(rotated.commutator_norm, 0.0)

    def test_observer_attaches_without_mutating_quantum_inputs(self) -> None:
        rho = np.diag([0.7, 0.3]).astype(np.complex128)
        hamiltonian = np.diag([0.0, 1.0]).astype(np.complex128)
        frame = QuantumStateFrame(t=0.0, dt=0.1, rho=rho.copy(), hamiltonian=hamiltonian.copy())
        bus = QuantumDataBus()
        bus.publish_state(frame)
        self.assertIsNotNone(frame.spectrum)
        np.testing.assert_array_equal(frame.rho, rho)
        np.testing.assert_array_equal(frame.hamiltonian, hamiltonian)
        self.assertIn("spectral_energy_populations", frame.arrays)
        self.assertIn("spectral_purity", frame.observables)
        self.assertEqual(len(bus.spectral_trace.records), 1)
        self.assertEqual(bus.spectral_trace.latest.t, 0.0)

    def test_trace_records_every_published_valid_frame(self) -> None:
        bus = QuantumDataBus()
        for step, population in enumerate((0.2, 0.5, 0.8)):
            bus.publish_state(
                QuantumStateFrame(
                    t=step * 0.25,
                    dt=0.25,
                    rho=np.diag([population, 1.0 - population]).astype(np.complex128),
                    hamiltonian=np.diag([0.0, 1.0]),
                    source_name="trace fixture",
                )
            )
        self.assertEqual([record.index for record in bus.spectral_trace.records], [0, 1, 2])
        times, purity = bus.spectral_trace.scalar_series("spectral_purity")
        np.testing.assert_allclose(times, [0.0, 0.25, 0.5])
        np.testing.assert_allclose(purity, [0.68, 0.5, 0.68])

    def test_opt_in_text_logger_writes_each_complete_step(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "spectral_trace.txt"
            bus = QuantumDataBus()
            bus.enable_spectral_text_log(str(path))
            bus.publish_state(
                QuantumStateFrame(
                    t=1.25,
                    dt=0.125,
                    rho=np.diag([0.25, 0.75]).astype(np.complex128),
                    hamiltonian=np.diag([3.0, 8.0]),
                    source_name="logger fixture",
                )
            )
            text = path.read_text(encoding="utf-8")
        self.assertIn("QMW Spectral Analysis V4 numerical trace", text)
        self.assertIn("step=0 t=1.25 dt=0.125", text)
        self.assertIn("energy=[3,8]", text)
        self.assertIn("population=[0.25,0.75]", text)
        self.assertIn("density_lambda=[0.25,0.75]", text)

    def test_tracker_preserves_identity_across_a_sorted_crossing(self) -> None:
        tracker = QMWEigenTracker()
        tracker.track(np.array([-1.0, 1.0]), np.eye(2, dtype=np.complex128))
        # The second sorted eigensystem has exchanged basis-vector columns.
        tracked = tracker.track(
            np.array([-0.5, 0.5]),
            np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
        )
        np.testing.assert_array_equal(tracked.permutation, [1, 0])
        np.testing.assert_allclose(tracked.eigenvectors, np.eye(2), atol=1e-10)

    def test_invalid_density_is_rejected_and_report_exposes_v4_contract(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            analyze_quantum_spectrum(np.diag([1.2, -0.2]), np.eye(2))
        spectrum = analyze_quantum_spectrum(np.diag([1.0, 0.0]), np.diag([0.0, 1.0]))
        report = format_spectral_report(spectrum)
        self.assertIn("Spectral Analysis V4", report)
        self.assertIn("rho_E = V_H", report)
        self.assertIn("independent ordering", report)
        self.assertIn("          1", report)


if __name__ == "__main__":
    unittest.main()
