from __future__ import annotations

import unittest

import numpy as np

from heisenberg_instrument_v1.clear_measurement_lab_v3 import (
    CELL_FREQUENCIES,
    OBSERVABLE,
    ClearMeasurementLab,
    contribution_matrix,
)
from heisenberg_instrument_v1.three_experiments import ExperimentMode


class _Client:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class ClearMeasurementLabTests(unittest.TestCase):
    def test_three_final_states_are_physically_distinct(self) -> None:
        lab = ClearMeasurementLab(_Client(), seed=7)
        coherent = lab.results.coherent.final_rho
        unread = lab.results.unread.final_rho
        recorded = lab.results.recorded.final_rho
        self.assertTrue(np.allclose(coherent, [[1, 0], [0, 0]]))
        self.assertTrue(np.allclose(unread, 0.5 * np.eye(2)))
        self.assertFalse(np.allclose(recorded, coherent))
        self.assertFalse(np.allclose(recorded, unread))
        self.assertAlmostEqual(np.trace(recorded @ recorded).real, 1.0)

    def test_contribution_cells_reconstruct_fixed_observable(self) -> None:
        lab = ClearMeasurementLab(_Client(), seed=7)
        for result in (lab.results.coherent, lab.results.unread, lab.results.recorded):
            cells = contribution_matrix(result.final_rho)
            self.assertAlmostEqual(np.sum(cells).imag, 0.0)
            self.assertAlmostEqual(
                np.sum(cells).real,
                np.trace(result.final_rho @ OBSERVABLE).real,
            )
            self.assertEqual(cells.shape, (2, 2))

    def test_every_mode_publishes_same_frequency_map_and_four_cells(self) -> None:
        client = _Client(); lab = ClearMeasurementLab(client, seed=7); lab.publish()
        messages = dict(client.messages)
        expected = CELL_FREQUENCIES.reshape(-1).tolist()
        for mode in ExperimentMode:
            prefix = f"/qmw/heisenberg_clear/{mode.value}/matrix"
            self.assertEqual(messages[f"{prefix}/frequency_hz"], expected)
            self.assertEqual(len(messages[f"{prefix}/real"]), 4)

    def test_mode_change_does_not_resample_recorded_outcome(self) -> None:
        lab = ClearMeasurementLab(_Client(), seed=11)
        before = lab.results.recorded.outcome
        lab.set_mode("unread")
        self.assertEqual(lab.results.recorded.outcome, before)


if __name__ == "__main__":
    unittest.main()
