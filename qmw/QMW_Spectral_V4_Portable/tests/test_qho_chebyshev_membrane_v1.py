from __future__ import annotations

import math
from pathlib import Path
import unittest

import numpy as np

from qmw.performance.qho_chebyshev import (
    CalibrationMode,
    ChebyshevExcitationSettingsV1,
    ExcitationMode,
    duration_calibration_gain,
    observe_qho_chebyshev,
)
from qmw.qho.schema import OscillatorFrame


ROOT = Path(__file__).resolve().parents[1]
SC = (
    ROOT
    / "Quantum_Resonant_Membrane_v1"
    / "supercollider"
    / "QMWResonantInteractionAddonV1.scd"
)
QRM = (
    ROOT
    / "Quantum_Resonant_Membrane_v1"
    / "supercollider"
    / "QuantumResonantMembraneV1.scd"
)


def frame_from_state(state: np.ndarray) -> OscillatorFrame:
    rho = np.outer(state, state.conj())
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
        purity=1.0,
        coherence_l1=float(np.sum(np.abs(rho)) - 1.0),
        rho=rho,
    )


class QHOChebyshevMappingTests(unittest.TestCase):
    def test_population_square_roots_become_harmonic_amplitudes(self) -> None:
        state = np.zeros(16, dtype=np.complex128)
        state[0] = 0.5
        state[1] = 0.5j
        state[2] = math.sqrt(0.5)
        descriptor = observe_qho_chebyshev(
            frame_from_state(state),
            ChebyshevExcitationSettingsV1(
                order=16,
                coherence_depth=0.0,
                calibration_mode=CalibrationMode.PHYSICAL,
            ),
        )
        np.testing.assert_allclose(
            descriptor.amplitudes[:3] ** 2,
            [0.25, 0.25, 0.5],
            atol=1e-12,
        )

    def test_adjacent_coherence_reconstructs_pure_state_relative_phase(self) -> None:
        phases = np.array([0.0, 0.3, -0.7])
        state = np.zeros(16, dtype=np.complex128)
        state[:3] = np.exp(1j * phases) / math.sqrt(3.0)
        descriptor = observe_qho_chebyshev(frame_from_state(state))
        np.testing.assert_allclose(
            descriptor.relative_phases[:3], phases, atol=1e-12
        )
        np.testing.assert_allclose(
            descriptor.coherence_reliability[:2], 1.0, atol=1e-12
        )

    def test_zero_coherence_has_no_phase_authority(self) -> None:
        rho = np.diag(np.full(16, 1.0 / 16.0)).astype(np.complex128)
        frame = frame_from_state(np.eye(16, dtype=np.complex128)[0])
        frame = OscillatorFrame(**{**frame.__dict__, "rho": rho, "populations": np.diag(rho).real})
        descriptor = observe_qho_chebyshev(frame)
        np.testing.assert_allclose(descriptor.coherence_reliability, 0.0)
        np.testing.assert_allclose(descriptor.relative_phases, 0.0)

    def test_energy_mode_renormalizes_truncated_order(self) -> None:
        state = np.ones(16, dtype=np.complex128) / 4.0
        descriptor = observe_qho_chebyshev(
            frame_from_state(state),
            ChebyshevExcitationSettingsV1(
                order=4, calibration_mode=CalibrationMode.ENERGY
            ),
        )
        self.assertAlmostEqual(float(np.sum(descriptor.amplitudes**2)), 1.0)
        self.assertAlmostEqual(descriptor.active_population, 0.25)
        np.testing.assert_allclose(descriptor.amplitudes[4:], 0.0)

    def test_physical_and_energy_duration_calibrations_are_distinct(self) -> None:
        long_impact = ChebyshevExcitationSettingsV1(
            excitation_mode=ExcitationMode.IMPACT,
            calibration_mode=CalibrationMode.PHYSICAL,
            contact_seconds=0.048,
        )
        long_actuator = ChebyshevExcitationSettingsV1(
            excitation_mode=ExcitationMode.ACTUATOR,
            calibration_mode=CalibrationMode.PHYSICAL,
            contact_seconds=0.048,
        )
        long_energy = ChebyshevExcitationSettingsV1(
            calibration_mode=CalibrationMode.ENERGY,
            contact_seconds=0.048,
        )
        self.assertAlmostEqual(duration_calibration_gain(long_impact), 0.25)
        self.assertAlmostEqual(duration_calibration_gain(long_actuator), 1.0)
        self.assertAlmostEqual(duration_calibration_gain(long_energy), 0.5)

    def test_supercollider_contract_has_bypass_controls_and_coherence_transport(self) -> None:
        source = SC.read_text(encoding="utf-8")
        for token in (
            "qmw.qho.osc.v1.2",
            "~qriChebControlBus",
            "qhoCoherenceMagnitudeBus",
            "qhoCoherencePhaseBus",
            "~qriQHOBasisPopulationBus",
            "~qriQHOMatrixPowerBus",
            "~qriQHOMatrixPhaseBus",
            "~qriParsevalControlBus",
            "/basis/qft/populations",
            "/basis/hadamard/populations",
            "/matrix-spectrum/power",
            "/matrix-spectrum/phase",
            "QHO PARSEVAL MEMBRANE EXCITER",
            "FIXED RMS / BASIS TIMBRE",
            "PURITY -> ENERGY",
            "PHYSICAL impulse / peak",
            "ENERGY Parseval L2",
            "~qriAuditionChebyshev",
        ):
            self.assertIn(token, source)
        preset = QRM.read_text(encoding="utf-8")
        for token in (
            "chebGain:",
            "chebMode:",
            "chebCalibration:",
            "chebContactSeconds:",
            "chebIncidence:",
            "chebOrder:",
            "chebCoherenceDepth:",
            "parsevalMode:",
            "parsevalBasis:",
            "parsevalTargetRMS:",
            "~qriPushChebControls",
            "~qriPushParsevalControls",
        ):
            self.assertIn(token, preset)


if __name__ == "__main__":
    unittest.main()
