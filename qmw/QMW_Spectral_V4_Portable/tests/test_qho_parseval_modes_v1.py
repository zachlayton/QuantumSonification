from __future__ import annotations

import math
import unittest

import numpy as np

from qmw.qho.live_osc import LiveQHOEngine, QHOFramePublisher, SCHEMA
from qmw.qho.parseval import harmonic_amplitudes_for_rms, observe_qho_parseval
from qmw.qho.schema import OscillatorFrame


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, payload: object) -> None:
        self.messages.append((address, payload))


def frame_from_rho(rho: np.ndarray) -> OscillatorFrame:
    populations = np.real(np.diag(rho))
    return OscillatorFrame(
        time=0.0,
        dimension=16,
        populations=populations,
        mean_n=float(np.dot(np.arange(16), populations)),
        mean_energy=0.0,
        x=0.0,
        p=0.0,
        var_x=0.5,
        var_p=0.5,
        backend="test",
        purity=float(np.trace(rho @ rho).real),
        coherence_l1=float(np.sum(np.abs(rho)) - 1.0),
        rho=rho,
    )


class QHOParsevalModeTests(unittest.TestCase):
    def test_every_analysis_basis_is_a_probability_distribution(self) -> None:
        state = np.zeros(16, dtype=np.complex128)
        state[:4] = np.exp(1j * np.array([0.0, 0.2, -0.7, 1.1])) / 2.0
        descriptor = observe_qho_parseval(frame_from_rho(np.outer(state, state.conj())))
        for basis in descriptor.basis_names:
            probabilities = descriptor.probabilities(basis)
            self.assertAlmostEqual(float(np.sum(probabilities)), 1.0, places=12)
            self.assertGreaterEqual(float(np.min(probabilities)), 0.0)

    def test_rotated_basis_reveals_coherence_with_fixed_total_power(self) -> None:
        plus = np.zeros(16, dtype=np.complex128)
        minus = np.zeros(16, dtype=np.complex128)
        plus[:2] = [1.0, 1.0]
        minus[:2] = [1.0, -1.0]
        plus /= math.sqrt(2.0)
        minus /= math.sqrt(2.0)
        plus_descriptor = observe_qho_parseval(
            frame_from_rho(np.outer(plus, plus.conj()))
        )
        minus_descriptor = observe_qho_parseval(
            frame_from_rho(np.outer(minus, minus.conj()))
        )
        np.testing.assert_allclose(
            plus_descriptor.probabilities("fock"),
            minus_descriptor.probabilities("fock"),
            atol=1.0e-12,
        )
        self.assertGreater(
            float(np.max(np.abs(
                plus_descriptor.probabilities("hadamard")
                - minus_descriptor.probabilities("hadamard")
            ))),
            0.05,
        )

    def test_unitary_matrix_spectrum_preserves_purity(self) -> None:
        pure = np.zeros(16, dtype=np.complex128)
        pure[:3] = [0.5, 0.5j, math.sqrt(0.5)]
        pure_rho = np.outer(pure, pure.conj())
        mixed_rho = np.eye(16, dtype=np.complex128) / 16.0
        for rho, expected in ((pure_rho, 1.0), (mixed_rho, 1.0 / 16.0)):
            descriptor = observe_qho_parseval(frame_from_rho(rho))
            self.assertAlmostEqual(descriptor.purity, expected, places=12)
            self.assertAlmostEqual(descriptor.matrix_power_sum, expected, places=12)
            self.assertLess(descriptor.parseval_residual, 1.0e-12)

    def test_fixed_rms_and_purity_energy_policies_are_distinct(self) -> None:
        shares = np.array([0.05, 0.01, 0.0])
        target = 0.2
        fixed = harmonic_amplitudes_for_rms(shares, target, normalize=True)
        purity = harmonic_amplitudes_for_rms(shares, target, normalize=False)
        self.assertAlmostEqual(0.5 * float(np.sum(fixed**2)), target**2)
        self.assertAlmostEqual(
            0.5 * float(np.sum(purity**2)), target**2 * float(np.sum(shares))
        )

    def test_v12_osc_transaction_carries_bases_and_parseval_diagnostics(self) -> None:
        frame, parameters = LiveQHOEngine().step(0.125)
        client = RecordingClient()
        revision = QHOFramePublisher(client).publish(frame, parameters)
        self.assertEqual(revision, 1)
        self.assertEqual(client.messages[0][1][2], SCHEMA)
        self.assertEqual(SCHEMA, "qmw.qho.osc.v1.2")
        payloads = dict(client.messages)
        for address in (
            "/qmw/qho/v1/basis/qft/populations",
            "/qmw/qho/v1/basis/hadamard/populations",
            "/qmw/qho/v1/matrix-spectrum/power",
            "/qmw/qho/v1/matrix-spectrum/phase",
        ):
            self.assertEqual(len(payloads[address]), 17)
        self.assertEqual(len(payloads["/qmw/qho/v1/parseval"]), 5)
        self.assertEqual(client.messages[-1], ("/qmw/qho/v1/frame/end", 1))


if __name__ == "__main__":
    unittest.main()
