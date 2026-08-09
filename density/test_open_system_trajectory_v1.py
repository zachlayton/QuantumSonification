import unittest

import numpy as np

from density.open_system_trajectory_v1 import (
    OpenSystemTrajectoryInstrument,
    amplitude_damping_kraus,
    dephasing_kraus,
)


def embed_local(operator: np.ndarray, qubit: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(2, dtype=np.complex128)
    for index in range(4):
        result = np.kron(result, operator if index == qubit else identity)
    return result


class OpenSystemTrajectoryTests(unittest.TestCase):
    def test_amplitude_jump_moves_the_matching_configuration_bit(self):
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[8, 8] = 1.0  # q0=1, all other bits zero
        instrument = OpenSystemTrajectoryInstrument(seed=5)
        event = instrument.apply_local(
            rho,
            amplitude_damping_kraus(1.0),
            channel="amplitude_damping",
            qubit=0,
            configuration=8,
            logical_time=0.25,
        )
        self.assertEqual(event.outcome, 1)
        self.assertTrue(event.jumped)
        self.assertEqual(event.configuration_after, 0)
        self.assertAlmostEqual(float(event.rho_after[0, 0].real), 1.0)

    def test_trajectory_average_reconstructs_the_density_channel(self):
        ket = np.zeros(16, dtype=np.complex128)
        ket[0] = np.sqrt(0.35)
        ket[8] = np.sqrt(0.65) * np.exp(0.4j)
        rho = np.outer(ket, ket.conj())
        local_kraus = amplitude_damping_kraus(0.31)
        full_kraus = tuple(embed_local(operator, 0) for operator in local_kraus)
        expected = sum(operator @ rho @ operator.conj().T for operator in full_kraus)

        instrument = OpenSystemTrajectoryInstrument(seed=91)
        config_rng = np.random.default_rng(92)
        populations = np.real(np.diag(rho))
        accumulated = np.zeros_like(rho)
        trials = 16_000
        for _ in range(trials):
            configuration = int(config_rng.choice(16, p=populations))
            event = instrument.apply_local(
                rho,
                local_kraus,
                channel="amplitude_damping",
                qubit=0,
                configuration=configuration,
                logical_time=0.0,
            )
            accumulated += event.rho_after
        np.testing.assert_allclose(accumulated / trials, expected, atol=0.012)

    def test_dephasing_jump_changes_phase_without_changing_configuration(self):
        ket = np.ones(16, dtype=np.complex128) / 4.0
        rho = np.outer(ket, ket.conj())
        instrument = OpenSystemTrajectoryInstrument(seed=2)
        event = instrument.apply_local(
            rho,
            dephasing_kraus(1.0),
            channel="dephasing",
            qubit=2,
            configuration=7,
            logical_time=0.0,
        )
        self.assertEqual(event.outcome, 1)
        self.assertTrue(event.jumped)
        self.assertEqual(event.configuration_after, 7)
        self.assertGreater(float(np.linalg.norm(event.delta_rho)), 0.0)


if __name__ == "__main__":
    unittest.main()
