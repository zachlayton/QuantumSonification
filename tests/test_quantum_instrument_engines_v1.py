import math
import unittest

import numpy as np

from excitation.gauge_wavefunction_sources_v1 import AharonovBohmRingSource
from excitation.joint_particle_sources_v1 import IdenticalParticles1DSource
from excitation.native_quantum_instrument_osc_v1 import NativeQuantumInstrumentOSCAdapter
from excitation.quantum_instrument_registry_v1 import (
    QUANTUM_INSTRUMENT_NAMES,
    create_quantum_instrument,
)
from excitation.spinor_sources_v1 import EPRBellPairSource, SpinHalfPrecessionSource
from excitation.advanced_quantum_sources_v1 import (
    DiracHydrogenFineStructureSource,
    DiracStepKleinSource,
)
from excitation.wavefunction_sources_v1 import create_wavefunction_source


class QuantumInstrumentEngineTests(unittest.TestCase):
    class RecordingClient:
        def __init__(self):
            self.messages = []

        def send_message(self, address, value):
            self.messages.append((address, value))

    def test_spin_half_follows_exact_larmor_period(self):
        source = SpinHalfPrecessionSource()
        initial = source.frame(0.0)
        quarter = source.frame(0.25)
        self.assertAlmostEqual(quarter.bloch_vector[0], 0.0, places=10)
        self.assertAlmostEqual(quarter.bloch_vector[1], 1.0, places=10)
        final = source.frame(0.75)
        np.testing.assert_allclose(final.bloch_vector, initial.bloch_vector, atol=1e-10)
        self.assertAlmostEqual(final.norm, 1.0, places=12)

    def test_epr_local_precession_preserves_maximal_entanglement(self):
        source = EPRBellPairSource(bell_state="singlet")
        for dt in (0.0, 0.13, 0.47, 1.2):
            frame = source.frame(dt)
            self.assertAlmostEqual(frame.norm, 1.0, places=12)
            self.assertAlmostEqual(frame.concurrence, 1.0, places=10)
            self.assertAlmostEqual(frame.chsh_maximum, 2.0 * math.sqrt(2.0), places=10)
            np.testing.assert_allclose(frame.reduced_a, 0.5 * np.eye(2), atol=1e-10)
            np.testing.assert_allclose(frame.reduced_b, 0.5 * np.eye(2), atol=1e-10)
            self.assertAlmostEqual(
                np.linalg.norm(frame.conditional_a_given_b_x_plus), 1.0, places=10
            )
            self.assertAlmostEqual(
                np.linalg.norm(frame.conditional_b_given_a_x_plus), 1.0, places=10
            )

    def test_exchange_symmetry_and_fermion_coincidence_hole(self):
        boson = IdenticalParticles1DSource(statistics="boson", n_points=48).frame(0.1)
        fermion = IdenticalParticles1DSource(statistics="fermion", n_points=48).frame(0.1)
        self.assertAlmostEqual(boson.swap_expectation, 1.0, places=10)
        self.assertAlmostEqual(fermion.swap_expectation, -1.0, places=10)
        self.assertGreater(boson.coincidence_probability, 0.0)
        self.assertAlmostEqual(fermion.coincidence_probability, 0.0, places=12)
        for frame in (boson, fermion):
            dx = float(frame.coordinates[0][1] - frame.coordinates[0][0])
            self.assertAlmostEqual(frame.norm, 1.0, places=10)
            self.assertAlmostEqual(float(np.sum(frame.marginal_a) * dx), 1.0, places=10)
            self.assertAlmostEqual(float(np.sum(frame.marginal_b) * dx), 1.0, places=10)

    def test_aharonov_bohm_uses_gauge_covariant_momentum(self):
        first = AharonovBohmRingSource(
            n_points=64,
            flux_ratio=0.25,
            coefficients={0: 1.0},
        ).frame()
        gauge_shifted = AharonovBohmRingSource(
            n_points=64,
            flux_ratio=1.25,
            coefficients={1: 1.0},
        ).frame()
        np.testing.assert_allclose(first.probability, gauge_shifted.probability, atol=1e-12)
        np.testing.assert_allclose(
            first.probability_current[0], gauge_shifted.probability_current[0], atol=1e-12
        )
        np.testing.assert_allclose(first.energy_density, gauge_shifted.energy_density, atol=1e-12)
        self.assertAlmostEqual(first.metadata["mechanical_angular_momentum"], -0.25, places=10)

    def test_morse_is_a_real_asymmetric_split_step_potential(self):
        source = create_wavefunction_source("morse_potential", grid_shape=128)
        potential = source._potential(0.0)
        x = source.coordinates[0]
        equilibrium_index = int(np.argmin(np.abs(x)))
        self.assertAlmostEqual(float(potential[equilibrium_index]), 0.0, places=12)
        self.assertGreater(float(potential[0]), float(potential[-1]))
        frame = source.frame(0.05)
        self.assertAlmostEqual(frame.norm, 1.0, places=10)
        self.assertEqual(frame.metadata["potential"], "morse")

    def test_unified_registry_preserves_native_frame_types(self):
        for name in (
            "spin_1_2_precession",
            "identical_particles_fermion_boson",
            "quantum_entanglement_epr",
            "morse_potential",
            "aharonov_bohm_effect",
        ):
            self.assertIn(name, QUANTUM_INSTRUMENT_NAMES)
        self.assertEqual(create_quantum_instrument("spin_1_2_precession").frame().source, "spin_1_2_precession")
        self.assertEqual(
            create_quantum_instrument(
                "identical_particles_fermion_boson", n_points=16
            ).frame().exchange_symmetry,
            "boson",
        )

    def test_native_osc_adapter_exposes_spin_epr_and_joint_observables(self):
        client = self.RecordingClient()
        adapter = NativeQuantumInstrumentOSCAdapter((client,))
        adapter.publish(SpinHalfPrecessionSource().frame(0.1))
        adapter.publish(EPRBellPairSource().frame(0.1))
        adapter.publish(IdenticalParticles1DSource(n_points=24).frame(0.1))
        adapter.publish(create_quantum_instrument("landau_levels", grid_shape=16).frame(0.1))
        adapter.publish(DiracHydrogenFineStructureSource().frame(0.1))
        adapter.publish(DiracStepKleinSource(n_points=128, extent=40.0, packet_center=-10.0).frame(0.01))
        addresses = [address for address, _value in client.messages]
        self.assertIn("/qmw/instrument/spin/frame", addresses)
        self.assertIn("/qmw/instrument/epr/correlation_tensor", addresses)
        self.assertIn("/qmw/instrument/exchange/frame", addresses)
        self.assertIn("/qmw/instrument/exchange/pair", addresses)
        self.assertIn("/qmw/instrument/field/name", addresses)
        self.assertIn("/qmw/instrument/relativistic/level", addresses)
        self.assertIn("/qmw/instrument/dirac/sample", addresses)
        self.assertEqual(addresses[-1], "/qmw/instrument/dirac/end")


if __name__ == "__main__":
    unittest.main()
