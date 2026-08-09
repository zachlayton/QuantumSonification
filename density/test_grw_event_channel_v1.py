import math
import unittest
from types import SimpleNamespace

import numpy as np

from density.grw_event_channel_v1 import (
    GRWConfig,
    GRWEventChannel,
    apply_outcome,
    four_qubit_kraus,
    ghz_density,
    outcome_probabilities,
    strength_to_width,
    width_to_strength,
)


def ket_density(index: int) -> np.ndarray:
    psi = np.zeros(16, dtype=complex)
    psi[index] = 1.0
    return np.outer(psi, psi.conj())


class GRWEventChannelTests(unittest.TestCase):
    def test_kraus_completeness_in_xyz_bases(self):
        identity = np.eye(16)
        for basis in "XYZ":
            for qubit in range(4):
                for strength in (0.0, 0.2, 0.75, 1.0):
                    operators = four_qubit_kraus(qubit, strength, basis)
                    completeness = sum(k.conj().T @ k for k in operators)
                    np.testing.assert_allclose(completeness, identity, atol=1e-13)

    def test_probabilities_sum_to_one(self):
        rho = ghz_density()
        for basis in "XYZ":
            probabilities = outcome_probabilities(rho, four_qubit_kraus(2, 0.61, basis))
            self.assertAlmostEqual(float(np.sum(probabilities)), 1.0, places=13)
            self.assertTrue(np.all(probabilities >= 0.0))

    def test_post_hit_is_density_matrix(self):
        channel = GRWEventChannel(GRWConfig(seed=9))
        event = channel.apply_hit(ghz_density(), revision_before=7, basis="Y", strength=0.73)
        np.testing.assert_allclose(event.rho_after, event.rho_after.conj().T, atol=1e-13)
        self.assertAlmostEqual(float(np.trace(event.rho_after).real), 1.0, places=13)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(event.rho_after))), -1e-12)
        np.testing.assert_allclose(event.delta_rho, event.rho_after - event.rho_before)
        self.assertEqual(event.revision_before, 7)
        self.assertEqual(event.revision_after, 8)

    def test_strength_zero_is_identity_and_one_is_projective(self):
        rho = ghz_density()
        channel = GRWEventChannel(GRWConfig(seed=11))
        identity_hit = channel.apply_hit(
            rho, revision_before=0, qubit=0, outcome=0, strength=0.0
        )
        np.testing.assert_allclose(identity_hit.rho_after, rho, atol=1e-13)

        projective = channel.apply_hit(
            rho, revision_before=1, qubit=0, outcome=0, strength=1.0
        )
        np.testing.assert_allclose(projective.rho_after, ket_density(0), atol=1e-13)
        self.assertAlmostEqual(projective.coherence_after, 0.0, places=13)

    def test_localized_state_has_inaudible_zero_salience_hit(self):
        channel = GRWEventChannel(GRWConfig(seed=12, salience_floor=0.002))
        event = channel.apply_hit(
            ket_density(0), revision_before=0, qubit=1, outcome=0, strength=1.0
        )
        self.assertAlmostEqual(event.trace_distance, 0.0, places=13)
        self.assertFalse(event.audible)

    def test_strong_local_hit_suppresses_global_ghz_coherence(self):
        channel = GRWEventChannel(GRWConfig(seed=4))
        event = channel.apply_hit(
            ghz_density(), revision_before=0, qubit=3, outcome=1, strength=1.0
        )
        self.assertGreater(event.coherence_before, 0.99)
        self.assertAlmostEqual(event.coherence_after, 0.0, places=13)
        self.assertGreater(event.trace_distance, 0.70)

    def test_seeded_scheduled_runs_are_reproducible(self):
        config = GRWConfig(enabled=True, rate_hz=3.0, width=0.6, seed=82)
        first = GRWEventChannel(config)
        second = GRWEventChannel(config)
        result_a = first.advance(ghz_density(), 2.0, revision=0, basis="Y")
        result_b = second.advance(ghz_density(), 2.0, revision=0, basis="Y")
        history_a = [(e.logical_time, e.qubit, e.outcome) for e in result_a.events]
        history_b = [(e.logical_time, e.qubit, e.outcome) for e in result_b.events]
        self.assertEqual(history_a, history_b)
        np.testing.assert_allclose(result_a.rho, result_b.rho)
        self.assertGreater(len(history_a), 1)  # multiple events in one processing frame

    def test_waiting_times_follow_total_constituent_rate(self):
        config = GRWConfig(enabled=True, rate_hz=2.0, constituent_scale=1.5, seed=6)
        channel = GRWEventChannel(config)
        samples = channel.sample_waiting_time(60_000)
        expected_mean = 1.0 / (4.0 * 2.0 * 1.5)
        self.assertAlmostEqual(float(np.mean(samples)), expected_mean, delta=0.002)

    def test_width_strength_mapping_round_trips(self):
        for strength in (0.02, 0.2, 0.5, 0.9, 0.999):
            self.assertAlmostEqual(
                width_to_strength(strength_to_width(strength)),
                strength,
                places=12,
            )

    def test_trajectory_average_matches_unconditioned_channel(self):
        rho = ghz_density()
        operators = four_qubit_kraus(0, 0.47, "X")
        expected = sum(k @ rho @ k.conj().T for k in operators)
        probabilities = outcome_probabilities(rho, operators)
        rng = np.random.default_rng(101)
        accumulated = np.zeros_like(rho)
        trials = 12_000
        for outcome in rng.choice(2, size=trials, p=probabilities):
            accumulated += apply_outcome(rho, operators[int(outcome)])[0]
        np.testing.assert_allclose(accumulated / trials, expected, atol=0.012)

    def test_basis_rotation_equivalence(self):
        # |++++> localized in X is equivalent to |0000> localized in Z.
        plus = np.ones(16, dtype=complex) / 4.0
        rho_plus = np.outer(plus, plus.conj())
        channel = GRWEventChannel(GRWConfig(seed=5))
        x_event = channel.apply_hit(
            rho_plus, revision_before=0, qubit=0, outcome=0, basis="X", strength=1.0
        )
        z_event = channel.apply_hit(
            ket_density(0), revision_before=1, qubit=0, outcome=0, basis="Z", strength=1.0
        )
        self.assertAlmostEqual(x_event.trace_distance, z_event.trace_distance, places=12)


class _RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class _ObserverBridge:
    def __init__(self):
        self.client = _RecordingClient()
        self.seen_rho = None
        self.circuit = SimpleNamespace(to_openqasm2_lines=lambda: [])
        self.registry_circuit = SimpleNamespace(active_measurement_bases=lambda: [])

    def apply_due_circuit_column(self, rho, _dt):
        return rho, None, []

    def update_and_send(self, rho, *_args):
        self.seen_rho = rho.copy()
        return {}


class GRWAuthoritativeEngineIntegrationTests(unittest.TestCase):
    def test_downstream_observer_receives_post_grw_authoritative_state(self):
        from density.density_matrix_engine_4q import DensityMatrixEngine

        config = GRWConfig(
            enabled=True,
            rate_hz=1.0,
            width=0.1,
            basis_source="Z",
            seed=44,
        )
        engine = DensityMatrixEngine(
            enable_circuit_bridge_control=False,
            grw_config=config,
        )
        old_socket = getattr(engine.qmw_bridge.client, "_sock", None)
        if old_socket is not None:
            old_socket.close()
        engine.qmw_bridge = _ObserverBridge()
        engine.rho = ghz_density()
        revision_before = engine.state_revision
        engine.grw.next_event_time = engine.logical_time + 0.01

        result = engine.step(0.02)

        self.assertIs(result, engine.rho)
        self.assertIsNotNone(engine.last_grw_event)
        self.assertEqual(engine.last_event_type, "spontaneous_localization")
        self.assertGreater(engine.state_revision, revision_before)
        np.testing.assert_allclose(engine.qmw_bridge.seen_rho, engine.rho)
        self.assertEqual(engine.circuit_state["revision"], engine.state_revision)
        self.assertEqual(engine.circuit_state["grw"]["events_this_frame"][0]["event_id"], 1)
        addresses = {address for address, _value in engine.qmw_bridge.client.messages}
        self.assertIn("/quantum/event/type", addresses)
        self.assertIn("/quantum/grw/event/salience", addresses)

    def test_live_controls_reconfigure_the_authoritative_channel(self):
        from density.density_matrix_engine_4q import DensityMatrixEngine

        engine = DensityMatrixEngine(enable_circuit_bridge_control=False)
        old_socket = getattr(engine.qmw_bridge.client, "_sock", None)
        if old_socket is not None:
            old_socket.close()
        engine.qmw_bridge = _ObserverBridge()

        engine._osc_grw_enabled("/quantum/grw/enabled", 1)
        engine._osc_grw_rate_hz("/quantum/grw/rate_hz", 2.5)
        engine._osc_grw_strength("/quantum/grw/strength", 0.8)
        engine._osc_grw_basis("/quantum/grw/basis", "Y")
        engine._osc_grw_seed("/quantum/grw/seed", 91)

        self.assertTrue(engine.grw.config.enabled)
        self.assertEqual(engine.grw.config.rate_hz, 2.5)
        self.assertAlmostEqual(engine.grw.config.strength, 0.8, places=12)
        self.assertEqual(engine.grw.config.basis_source, "Y")
        self.assertEqual(engine.grw.config.seed, 91)
        addresses = {address for address, _value in engine.qmw_bridge.client.messages}
        self.assertIn("/quantum/grw/strength", addresses)
        self.assertIn("/quantum/grw/next_event_ms", addresses)


if __name__ == "__main__":
    unittest.main()
