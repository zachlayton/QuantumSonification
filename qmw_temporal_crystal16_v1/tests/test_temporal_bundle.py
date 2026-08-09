from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qmw_debruijn_clock4_v1 import DeBruijnClock4
from qmw_floquet_time_crystal16_v1 import (
    FloquetIsingConfig,
    FloquetTimeCrystal16,
)
from qmw_lfsr_clock4_v1 import LFSRClock4
from qmw_subharmonic_pythagorean_quantum_time_v1 import (
    PythagoreanHamiltonianCoupler,
    SubharmonicPythagoreanClock,
    TemporalRatio,
    combined_return_ticks,
    pythagorean_comma,
)
from qmw_temporal_core16_v1 import (
    DIM,
    X,
    Z,
    computational_basis_state,
    density_from_state,
    expectation,
    operator_on_qubit,
    purity,
    validate_density_matrix,
)
from qmw_temporal_engine16_v1 import (
    FloquetEvolver,
    LFSRPermutationEvolver,
    PythagoreanEvolver,
    TemporalEngine16,
)
from qmw_temporal_osc16_v1 import frame_messages


class CoreTests(unittest.TestCase):
    def test_q0_is_least_significant_bit(self) -> None:
        zero = computational_basis_state(0)
        self.assertEqual(int(np.argmax(operator_on_qubit(X, 0) @ zero)), 1)
        self.assertEqual(int(np.argmax(operator_on_qubit(X, 3) @ zero)), 8)

    def test_density_validation(self) -> None:
        rho = density_from_state(computational_basis_state(5))
        report = validate_density_matrix(rho)
        self.assertTrue(report.valid)
        self.assertAlmostEqual(purity(rho), 1.0)


class LFSRTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lfsr = LFSRClock4(seed=1)

    def test_maximal_cycle_and_fixed_zero(self) -> None:
        self.assertEqual(len(self.lfsr.orbit()), 15)
        self.assertEqual(set(self.lfsr.orbit()), set(range(1, 16)))
        self.assertEqual(self.lfsr.step_state_once(0), 0)

    def test_permutation_unitarity_and_order(self) -> None:
        permutation = self.lfsr.permutation_matrix()
        identity = np.eye(DIM)
        self.assertTrue(np.allclose(permutation.conj().T @ permutation, identity))
        self.assertTrue(np.allclose(np.linalg.matrix_power(permutation, 15), identity))
        for exponent in range(1, 15):
            self.assertFalse(
                np.allclose(np.linalg.matrix_power(permutation, exponent), identity)
            )

    def test_density_invariants(self) -> None:
        psi = np.arange(1, DIM + 1, dtype=np.complex128)
        psi = psi / np.linalg.norm(psi)
        rho = density_from_state(psi)
        moved = self.lfsr.apply_to_density(rho)
        self.assertTrue(validate_density_matrix(moved).valid)
        self.assertAlmostEqual(purity(rho), purity(moved))
        self.assertTrue(
            np.allclose(np.linalg.eigvalsh(rho), np.linalg.eigvalsh(moved))
        )

    def test_120_coherences_form_eight_orbits(self) -> None:
        orbits = self.lfsr.coherence_orbits()
        self.assertEqual(len(orbits), 8)
        self.assertEqual([len(orbit) for orbit in orbits], [15] * 8)
        self.assertEqual(sum(len(orbit) for orbit in orbits), 120)

    def test_joint_clock_system_unitary(self) -> None:
        joint = self.lfsr.joint_clock_system_unitary(
            np.eye(DIM),
            operator_on_qubit(X, 0),
        )
        self.assertEqual(joint.shape, (256, 256))
        self.assertTrue(np.allclose(joint.conj().T @ joint, np.eye(256)))


class DeBruijnTests(unittest.TestCase):
    def test_full_sixteen_state_cycle(self) -> None:
        clock = DeBruijnClock4()
        self.assertEqual(len(clock.orbit), 16)
        self.assertEqual(set(clock.orbit), set(range(16)))
        self.assertTrue(
            np.allclose(
                np.linalg.matrix_power(clock.permutation_matrix(), 16),
                np.eye(16),
            )
        )


class SPQTTests(unittest.TestCase):
    def test_three_two_phase_orbit(self) -> None:
        ratio = TemporalRatio(3, 2, "fifth")
        self.assertEqual([ratio.position(k) for k in range(4)], [0, 2, 1, 0])
        self.assertEqual(ratio.frequency_ratio.numerator, 2)
        self.assertEqual(ratio.frequency_ratio.denominator, 3)

    def test_nested_return(self) -> None:
        ratio = TemporalRatio(3, 2, "fifth")
        clock = SubharmonicPythagoreanClock(
            (ratio,),
            include_basis_clock=16,
            include_lfsr_period=15,
        )
        self.assertEqual(clock.macrocycle_length, 240)
        self.assertEqual(combined_return_ticks(16, 15), 240)

    def test_pythagorean_comma_exact(self) -> None:
        self.assertEqual(
            pythagorean_comma().numerator,
            531441,
        )
        self.assertEqual(
            pythagorean_comma().denominator,
            524288,
        )

    def test_hamiltonian_coupler_is_hermitian(self) -> None:
        ratio = TemporalRatio(3, 2, "fifth")
        clock = SubharmonicPythagoreanClock(
            (ratio,),
            include_basis_clock=None,
        )
        coupler = PythagoreanHamiltonianCoupler(
            np.zeros((16, 16), dtype=np.complex128),
            {"fifth": operator_on_qubit(Z, 0)},
            quadrature_operators={"fifth": operator_on_qubit(X, 0)},
        )
        hamiltonian = coupler.hamiltonian(clock.snapshot())
        self.assertTrue(np.allclose(hamiltonian, hamiltonian.conj().T))


class FloquetTests(unittest.TestCase):
    def test_repeated_map_and_period_doubling(self) -> None:
        model = FloquetTimeCrystal16(FloquetIsingConfig(pulse_error=0.0))
        trajectory = model.run(64)
        expected = np.asarray([1.0, -1.0] * 32)
        self.assertTrue(np.allclose(trajectory.magnetization_z[:-1], expected))
        diagnostics = model.subharmonic_diagnostics(trajectory)
        self.assertAlmostEqual(diagnostics.target_frequency, 0.5)
        self.assertAlmostEqual(diagnostics.target_amplitude, 1.0, places=9)
        self.assertAlmostEqual(diagnostics.dominant_frequency, 0.5, places=9)
        self.assertGreater(diagnostics.peak_to_background, 1e8)

    def test_floquet_unitary_and_pi_pairing(self) -> None:
        model = FloquetTimeCrystal16()
        unitary = model.floquet_unitary
        self.assertTrue(np.allclose(unitary.conj().T @ unitary, np.eye(16)))
        pairing = model.quasienergy_pairing()
        self.assertGreater(pairing.normalized_pairing_score, 0.999999)


class EngineTests(unittest.TestCase):
    def test_single_writer_revision_and_history(self) -> None:
        model = FloquetTimeCrystal16()
        engine = TemporalEngine16(
            model.product_density(0),
            evolver=FloquetEvolver(model),
            lfsr_clock=LFSRClock4(),
            dt=1.0,
        )
        frames = engine.run(8)
        self.assertEqual(engine.state.revision, 8)
        self.assertEqual(len(engine.history), 9)
        self.assertEqual(frames[-1].tick, 8)
        self.assertEqual(
            frames[-1].protocol,
            "floquet_repeated_single_period_map",
        )
        addresses = {message.address for message in frame_messages(frames[-1])}
        self.assertIn("/qmw/time/revision", addresses)
        self.assertIn("/qmw/time/lfsr/state", addresses)

    def test_lfsr_programmed_protocol_is_explicit(self) -> None:
        lfsr = LFSRClock4()
        rho = density_from_state(computational_basis_state(1))
        engine = TemporalEngine16(
            rho,
            evolver=LFSRPermutationEvolver(lfsr),
            lfsr_clock=lfsr,
        )
        frame = engine.step()
        self.assertEqual(
            frame.protocol,
            "programmed_maximal_lfsr_permutation",
        )
        self.assertFalse(bool(frame.metadata["emergent"]))

    def test_pythagorean_programmed_protocol_is_explicit(self) -> None:
        ratio = TemporalRatio(3, 2, "fifth")
        spqt = SubharmonicPythagoreanClock(
            (ratio,),
            include_basis_clock=16,
        )
        coupler = PythagoreanHamiltonianCoupler(
            np.zeros((16, 16), dtype=np.complex128),
            {"fifth": operator_on_qubit(X, 0)},
        )
        engine = TemporalEngine16(
            density_from_state(computational_basis_state(0)),
            evolver=PythagoreanEvolver(coupler),
            spqt_clock=spqt,
        )
        frame = engine.step()
        self.assertEqual(
            frame.protocol,
            "programmed_pythagorean_hamiltonian_drive",
        )
        self.assertFalse(bool(frame.metadata["emergent"]))


if __name__ == "__main__":
    unittest.main()
