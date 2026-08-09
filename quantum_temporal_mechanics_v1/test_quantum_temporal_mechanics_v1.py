from __future__ import annotations

import math
import unittest

import numpy as np

from quantum_temporal_mechanics_v1.core import (
    FiniteQuantumClock,
    QuantumTemporalMechanics,
    build_history_state,
    density_matrix,
)
from quantum_temporal_mechanics_v1.osc_demo import build_experiment
from quantum_temporal_mechanics_v1.osc_output import TemporalMechanicsOSCPublisher
from quantum_temporal_mechanics_v1.density_clock import DensityMatrixClock
from quantum_temporal_mechanics_v1.density_clock_osc import decode_density_payload


class QuantumTemporalMechanicsTests(unittest.TestCase):
    def setUp(self):
        self.clock = FiniteQuantumClock(16, math.tau)
        self.hamiltonian = np.diag([0.0, 1.0])
        self.plus = np.array([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
        history = build_history_state(self.clock, self.plus, self.hamiltonian)
        self.mechanics = QuantumTemporalMechanics(self.clock, history)

    def test_clock_povm_is_complete_and_conditionals_are_normalized(self):
        diagnostics = self.mechanics.diagnostics(self.hamiltonian)
        self.assertLess(diagnostics.clock_effect_completeness_error, 1e-12)
        for reading in self.mechanics.readings():
            self.assertAlmostEqual(float(np.trace(reading.conditional_state).real), 1.0)
        self.assertAlmostEqual(sum(r.probability for r in self.mechanics.readings()), 1.0)

    def test_history_recovers_schrodinger_relations(self):
        diagnostics = self.mechanics.diagnostics(self.hamiltonian)
        self.assertGreater(diagnostics.mean_transition_fidelity, 1.0 - 1e-10)
        self.assertGreater(diagnostics.closure_fidelity, 1.0 - 1e-10)

    def test_periodic_clock_exposes_incompatible_system_closure(self):
        incompatible_hamiltonian = np.diag([0.0, 0.7])
        history = build_history_state(self.clock, self.plus, incompatible_hamiltonian)
        mechanics = QuantumTemporalMechanics(self.clock, history)
        diagnostics = mechanics.diagnostics(incompatible_hamiltonian)
        self.assertGreater(diagnostics.mean_transition_fidelity, 1.0 - 1e-10)
        self.assertLess(diagnostics.closure_fidelity, 0.8)

    def test_event_time_and_duration_are_operational_distributions(self):
        plus_effect = density_matrix(self.plus)
        quarter = np.array([1.0, -1j], dtype=np.complex128) / math.sqrt(2.0)
        first = self.mechanics.event_time(plus_effect, "zero")
        second = self.mechanics.event_time(density_matrix(quarter), "quarter")
        duration = self.mechanics.duration(first, second)
        self.assertAlmostEqual(sum(first.tick_distribution), 1.0)
        self.assertAlmostEqual(sum(duration.lag_distribution), 1.0)
        self.assertEqual(duration.forward_ticks, 4)
        self.assertAlmostEqual(duration.duration, math.pi / 2.0)

    def test_clock_origin_shift_preserves_duration(self):
        plus_effect = density_matrix(self.plus)
        quarter = np.array([1.0, -1j], dtype=np.complex128) / math.sqrt(2.0)
        baseline = self.mechanics.duration(
            self.mechanics.event_time(plus_effect, "a"),
            self.mechanics.event_time(density_matrix(quarter), "b"),
        )
        shifted = self.mechanics.translated_frame(3)
        shifted_duration = shifted.duration(
            shifted.event_time(plus_effect, "a"),
            shifted.event_time(density_matrix(quarter), "b"),
        )
        self.assertTrue(np.allclose(baseline.lag_distribution, shifted_duration.lag_distribution))

    def test_nonphysical_event_effect_is_rejected(self):
        with self.assertRaises(ValueError):
            self.mechanics.event_time(2.0 * np.eye(2))

    def test_osc_frame_contract_without_network(self):
        class Client:
            def __init__(self):
                self.messages = []

            def send_message(self, address, values):
                self.messages.append((address, values))

        mechanics, events, duration, diagnostics = build_experiment(16)
        client = Client()
        publisher = TemporalMechanicsOSCPublisher(client=client)
        publisher.publish_frame(7, mechanics, 3, events, duration, diagnostics)
        addresses = [address for address, _ in client.messages]
        root = "/qmw/temporal-mechanics/v1"
        self.assertEqual(addresses[0], f"{root}/frame/begin")
        self.assertIn(f"{root}/clock", addresses)
        self.assertIn(f"{root}/state/populations", addresses)
        self.assertIn(f"{root}/event", addresses)
        self.assertIn(f"{root}/duration", addresses)
        self.assertEqual(addresses[-1], f"{root}/frame/end")

    def test_density_clock_stops_for_a_stationary_density_matrix(self):
        clock = DensityMatrixClock(distance_per_pulse=0.1)
        rho = density_matrix(np.array([1.0, 0.0]))
        first = clock.update(rho, 1)
        second = clock.update(rho, 2)
        self.assertEqual(first.pulses, 0)
        self.assertEqual(second.pulses, 0)
        self.assertEqual(second.record_index, 0)
        self.assertAlmostEqual(second.delta_bures, 0.0)

    def test_density_displacement_generates_intrinsic_clock_records(self):
        clock = DensityMatrixClock(
            distance_per_pulse=0.2,
            max_pulses_per_update=16,
            mode="fixed",
        )
        clock.update(density_matrix(np.array([1.0, 0.0])), 1)
        reading = clock.update(density_matrix(np.array([0.0, 1.0])), 2)
        self.assertGreater(reading.delta_bures, 1.5)
        self.assertEqual(reading.pulses, 7)
        self.assertEqual(reading.record_index, 7)

    def test_density_osc_payload_round_trip(self):
        rho = np.array([[0.75, 0.0 + 0.25j], [0.0 - 0.25j, 0.25]])
        flat = rho.reshape(-1)
        values = [9, 2]
        for value in flat:
            values.extend([value.real, value.imag])
        revision, decoded = decode_density_payload(values)
        self.assertEqual(revision, 9)
        self.assertTrue(np.allclose(decoded, rho))

    def test_density_clock_repairs_small_negative_eigenvalue(self):
        clock = DensityMatrixClock(distance_per_pulse=0.1)
        almost_physical = np.diag([1.000001, -0.000001])
        reading = clock.update(almost_physical, 3)
        self.assertGreater(reading.negativity, 0.0)
        self.assertGreater(reading.projection_error, 0.0)
        self.assertEqual(reading.pulses, 0)

    def test_density_clock_distance_can_change_without_reset(self):
        clock = DensityMatrixClock(distance_per_pulse=0.1)
        clock.record_index = 12
        self.assertEqual(clock.set_distance_per_pulse(2.0), 2.0)
        self.assertEqual(clock.distance_per_pulse, 2.0)
        self.assertEqual(clock.record_index, 12)
        with self.assertRaises(ValueError):
            clock.set_distance_per_pulse(0.0)

    def test_poisson_mode_randomizes_record_distance_reproducibly(self):
        first = DensityMatrixClock(distance_per_pulse=2.0, mode="poisson", seed=7)
        second = DensityMatrixClock(distance_per_pulse=2.0, mode="poisson", seed=7)
        self.assertAlmostEqual(first.next_record_distance, second.next_record_distance)
        self.assertNotAlmostEqual(first.next_record_distance, 2.0)
        old_distance = first.next_record_distance
        first.set_distance_per_pulse(2.0)
        self.assertNotAlmostEqual(first.next_record_distance, old_distance)
        self.assertEqual(first.set_mode("fixed"), "fixed")
        self.assertEqual(first.next_record_distance, 2.0)

    def test_coherence_flux_can_compress_record_spacing(self):
        clock = DensityMatrixClock(
            distance_per_pulse=100.0,
            mode="fixed",
            coherence_depth=1.0,
        )

        def phase_state(phase):
            ket = np.array([1.0, np.exp(1j * phase)]) / math.sqrt(2.0)
            return density_matrix(ket)

        clock.update(phase_state(0.0), 1)
        baseline = clock.update(phase_state(0.001), 2)
        burst = clock.update(phase_state(math.pi / 2.0), 3)
        self.assertAlmostEqual(baseline.coherence_gain, 1.0, places=6)
        self.assertGreater(burst.coherence_gain, 1.0)
        self.assertGreater(burst.hazard_increment, burst.delta_bures)
        self.assertEqual(clock.set_coherence_depth(0.0), 0.0)
        with self.assertRaises(ValueError):
            clock.set_coherence_depth(1.1)


if __name__ == "__main__":
    unittest.main()
