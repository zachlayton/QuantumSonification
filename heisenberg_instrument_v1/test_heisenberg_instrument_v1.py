from __future__ import annotations

import unittest

import numpy as np

from heisenberg_instrument_v1 import (
    ExperimentMode,
    computational_projectors,
    run_experiment,
    run_three_experiments,
    transition_matrix_frame,
)
from heisenberg_instrument_v1.heisenberg_lab_v1 import HeisenbergLab


HADAMARD = np.asarray([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
PAULI_X = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
PAULI_Z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)


def pure_density(state: np.ndarray) -> np.ndarray:
    vector = np.asarray(state, dtype=np.complex128)
    return np.outer(vector, vector.conj())


class ThreeExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rho_zero = pure_density(np.asarray([1.0, 0.0]))
        self.projectors = computational_projectors(2)

    def test_coherent_unread_and_recorded_are_distinct_processes(self) -> None:
        results = run_three_experiments(
            self.rho_zero,
            HADAMARD,
            HADAMARD,
            self.projectors,
            recorded_outcome=0,
        )

        self.assertAlmostEqual(results.coherent.final_rho[0, 0].real, 1.0)
        self.assertTrue(
            np.allclose(results.unread.final_rho, 0.5 * np.eye(2), atol=1e-10)
        )
        expected_recorded = pure_density(HADAMARD[:, 0])
        self.assertTrue(
            np.allclose(results.recorded.final_rho, expected_recorded, atol=1e-10)
        )
        self.assertEqual(results.recorded.outcome, 0)
        self.assertGreater(results.unread.measurement_disturbance, 0.0)
        self.assertAlmostEqual(results.unread.coherence_after, 0.0)

    def test_unread_case_equals_ensemble_of_recorded_cases(self) -> None:
        unread = run_experiment(
            self.rho_zero,
            HADAMARD,
            HADAMARD,
            self.projectors,
            ExperimentMode.UNREAD,
        )
        recorded = [
            run_experiment(
                self.rho_zero,
                HADAMARD,
                HADAMARD,
                self.projectors,
                ExperimentMode.RECORDED,
                outcome=outcome,
            )
            for outcome in range(2)
        ]
        ensemble = sum(
            unread.outcome_probabilities[index] * result.final_rho
            for index, result in enumerate(recorded)
        )
        self.assertTrue(np.allclose(ensemble, unread.final_rho, atol=1e-10))

    def test_all_results_remain_physical(self) -> None:
        results = run_three_experiments(
            self.rho_zero,
            HADAMARD,
            PAULI_X,
            self.projectors,
            recorded_outcome=1,
        )
        for result in (results.coherent, results.unread, results.recorded):
            self.assertTrue(
                np.allclose(result.final_rho, result.final_rho.conj().T, atol=1e-10)
            )
            self.assertAlmostEqual(np.trace(result.final_rho).real, 1.0)
            self.assertGreaterEqual(np.min(np.linalg.eigvalsh(result.final_rho)), -1e-10)


class TransitionMatrixTests(unittest.TestCase):
    def test_contributions_reconstruct_expectation(self) -> None:
        plus = HADAMARD @ np.asarray([1.0, 0.0], dtype=np.complex128)
        frame = transition_matrix_frame(
            pure_density(plus),
            PAULI_Z,
            PAULI_X,
        )
        self.assertLess(frame.reconstruction_error, 1.0e-10)
        self.assertAlmostEqual(np.sum(frame.contributions).real, 1.0)

    def test_four_qubit_frame_is_sixteen_by_sixteen(self) -> None:
        dimension = 16
        state = np.zeros(dimension, dtype=np.complex128)
        state[0] = 1.0 / np.sqrt(2.0)
        state[-1] = 1.0 / np.sqrt(2.0)
        rho = pure_density(state)
        energies = np.arange(dimension, dtype=np.float64)
        hamiltonian = np.diag(energies)
        observable = np.kron(
            np.kron(np.kron(PAULI_X, np.eye(2)), np.eye(2)), np.eye(2)
        )

        frame = transition_matrix_frame(rho, hamiltonian, observable)
        payloads = frame.osc_payloads()

        self.assertEqual(frame.contributions.shape, (16, 16))
        self.assertEqual(len(payloads["magnitude"]), 256)
        self.assertEqual(len(payloads["frequency_hz"]), 256)
        self.assertTrue(np.all(frame.audio_frequencies_hz > 0.0))
        self.assertLess(frame.reconstruction_error, 1.0e-10)

    def test_one_global_scale_preserves_gap_ratios(self) -> None:
        rho = pure_density(np.asarray([1.0, 0.0, 0.0], dtype=np.complex128))
        hamiltonian = np.diag([0.0, 1.0, 3.0])
        observable = np.ones((3, 3), dtype=np.complex128)
        frame = transition_matrix_frame(
            rho,
            hamiltonian,
            observable,
            base_frequency_hz=100.0,
        )
        self.assertAlmostEqual(frame.audio_frequencies_hz[1, 0], 100.0)
        self.assertAlmostEqual(frame.audio_frequencies_hz[2, 0], 300.0)


class _CollectingOSCClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class OSCContractTests(unittest.TestCase):
    def test_lab_publishes_complete_active_256_cell_frame(self) -> None:
        client = _CollectingOSCClient()
        lab = HeisenbergLab(client, seed=7)
        lab.publish()
        messages = dict(client.messages)

        self.assertEqual(messages["/qmw/heisenberg/active/mode"], "coherent")
        self.assertEqual(
            len(messages["/qmw/heisenberg/active/matrix/magnitude"]), 256
        )
        self.assertEqual(
            len(messages["/qmw/heisenberg/active/matrix/frequency_hz"]), 256
        )
        self.assertLess(
            messages["/qmw/heisenberg/active/matrix/reconstruction_error"],
            1.0e-10,
        )
        self.assertIn("/qmw/heisenberg/active/matrix/begin", messages)
        self.assertIn("/qmw/heisenberg/active/matrix/end", messages)

    def test_default_tilted_observable_gives_three_audible_distinct_fields(self) -> None:
        lab = HeisenbergLab(_CollectingOSCClient(), seed=7)

        self.assertEqual(lab.observable_name, "XZ0")
        fields = [
            lab.frames[mode].contributions
            for mode in (
                ExperimentMode.COHERENT,
                ExperimentMode.UNREAD,
                ExperimentMode.RECORDED,
            )
        ]
        for field in fields:
            self.assertGreater(np.max(np.abs(field)), 1.0e-6)
        self.assertFalse(np.allclose(fields[0], fields[1]))
        self.assertFalse(np.allclose(fields[1], fields[2]))
        self.assertFalse(np.allclose(fields[0], fields[2]))

    def test_lab_mode_and_observable_controls_rebuild_active_frame(self) -> None:
        client = _CollectingOSCClient()
        lab = HeisenbergLab(client, seed=11)
        outcome_before = lab.results.recorded.outcome
        lab.set_mode("unread")
        lab.set_observable("Z0")
        messages = dict(client.messages)
        self.assertEqual(messages["/qmw/heisenberg/active/mode"], "unread")
        self.assertEqual(messages["/qmw/heisenberg/observable"], "Z0")
        self.assertEqual(lab.results.recorded.outcome, outcome_before)


if __name__ == "__main__":
    unittest.main()
