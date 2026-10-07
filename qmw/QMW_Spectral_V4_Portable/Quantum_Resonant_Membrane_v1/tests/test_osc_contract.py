from __future__ import annotations

import unittest

import numpy as np

from quantum_resonant_membrane.engine import QuantumResonantMembraneEngine
from quantum_resonant_membrane.interference_timbre import (
    InterferenceTimbreControl,
    InterferenceTimbreProjector,
)
from quantum_resonant_membrane.osc import MembraneOSCPublisher, ROOT, SCHEMA


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class OSCContractTests(unittest.TestCase):
    def test_atomic_revision_and_crossing_provenance(self) -> None:
        engine = QuantumResonantMembraneEngine(
            modes=20, crossing_threshold=1.0e-7
        )
        frame = engine.step(1.0 / 30.0)
        client = RecordingClient()
        publisher = MembraneOSCPublisher(client)
        revision = publisher.publish_frame(
            frame.density,
            frame.temporal,
            frame.terrain,
            frame.flow,
            frame.membrane,
            reset_epoch=frame.reset_epoch,
        )
        self.assertEqual(revision, 1)
        addresses = [address for address, _ in client.messages]
        self.assertEqual(addresses[0], f"{ROOT}/frame/begin")
        self.assertEqual(addresses[-1], f"{ROOT}/frame/end")
        begin = client.messages[0][1]
        end = client.messages[-1][1]
        self.assertEqual(begin[0], end[0])
        self.assertEqual(begin[2], SCHEMA)
        self.assertEqual(begin[6], 0)
        self.assertIn(f"{ROOT}/density/rho_real", addresses)
        self.assertIn(f"{ROOT}/density/rho_imag", addresses)
        self.assertIn(f"{ROOT}/density/preparation", addresses)
        self.assertIn(f"{ROOT}/temporal/global", addresses)
        self.assertIn(f"{ROOT}/field/global", addresses)
        self.assertIn(f"{ROOT}/field/frequency_offsets", addresses)
        self.assertIn(f"{ROOT}/field/susceptibility", addresses)
        self.assertIn(f"{ROOT}/field/damping", addresses)
        self.assertIn(f"{ROOT}/field/quality_factor", addresses)
        self.assertIn(f"{ROOT}/field/intermodal_coupling", addresses)
        self.assertIn(f"{ROOT}/event/global", addresses)
        self.assertIn(f"{ROOT}/timbre/interference", addresses)
        self.assertIn(f"{ROOT}/timbre/gain_factors", addresses)
        self.assertIn(f"{ROOT}/timbre/output_amplitudes", addresses)
        event_global = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/event/global"
        )
        self.assertEqual(event_global[4], frame.flow.event_bus.threshold)
        self.assertEqual(
            event_global[5], frame.flow.event_bus.accumulator_peak_fraction
        )
        preparation = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/density/preparation"
        )
        self.assertEqual(preparation[1], "localized")
        self.assertIn("localized", preparation[2])
        rho_real = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/density/rho_real"
        )
        rho_imag = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/density/rho_imag"
        )
        self.assertEqual(len(rho_real), 17)
        self.assertEqual(len(rho_imag), 17)
        interference = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/timbre/interference"
        )
        factors = next(
            payload for address, payload in client.messages
            if address == f"{ROOT}/timbre/gain_factors"
        )
        self.assertEqual(interference[0], revision)
        self.assertEqual(interference[1], frame.interference_control.revision)
        self.assertEqual(interference[4], 0.0)  # neutral opt-in default
        self.assertEqual(len(factors), 21)
        self.assertEqual(factors[0], revision)
        self.assertTrue(all(value == 1.0 for value in factors[1:]))
        for address, payload in client.messages[1:-1]:
            if address.endswith("/available") or address.endswith("/geometry/end"):
                continue
            self.assertEqual(payload[0], revision, address)
        for address, payload in client.messages:
            if address == f"{ROOT}/crossing":
                self.assertEqual(payload[11], "quantum_probability_unitary")
            if address == f"{ROOT}/event/crossing":
                self.assertGreater(payload[4], 0.0)
                self.assertEqual(payload[9], "quantum_probability_unitary")

    def test_reset_epoch_marks_the_first_post_reset_frame(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        self.assertEqual(engine.step(1.0 / 30.0).reset_epoch, 0)
        engine.reset()
        frame = engine.step(1.0 / 30.0)
        self.assertEqual(frame.reset_epoch, 1)
        client = RecordingClient()
        MembraneOSCPublisher(client).publish_frame(
            frame.density,
            frame.temporal,
            frame.terrain,
            frame.flow,
            frame.membrane,
            reset_epoch=frame.reset_epoch,
        )
        self.assertEqual(client.messages[0][1][6], 1)

    def test_state_preparation_is_a_transactional_engine_reset(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        engine.prepare("squeezed")
        frame = engine.step(0.0)
        self.assertEqual(frame.reset_epoch, 1)
        self.assertEqual(frame.density.preparation_mode, "squeezed")

    def test_interference_controls_are_downstream_and_revisioned(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        before = engine.step(0.0)
        rho_before = before.density.rho.copy()
        engine.set_interference_timbre(
            phase_offset_radians=0.3,
            phase_spread_radians=0.6,
            depth=0.9,
            slew_seconds=0.12,
            source_kind="manual",
        )
        after = engine.step(0.0)
        self.assertEqual(after.interference_control.revision, 1)
        self.assertAlmostEqual(after.interference_control.phase_radians, 0.3)
        self.assertAlmostEqual(after.interference_control.depth, 0.9)
        self.assertEqual(after.interference_control.phase_source, "designed_control")
        self.assertTrue((after.density.rho == rho_before).all())

    def test_density_coherence_source_reads_full_rho_without_mutating_it(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        engine.prepare("coherent")
        engine.set_interference_timbre(
            source_kind="density_coherence",
            coherence_row=0,
            coherence_column=1,
            depth=1.0,
        )
        frame = engine.step(0.0)
        self.assertEqual(frame.interference_control.phase_source, "rho[0,1]")
        self.assertGreater(frame.interference_control.depth, 0.0)
        self.assertIn("density_coherence", frame.interference_control.provenance)

    def test_portable_projector_preserves_power_and_names_cancellation(self) -> None:
        projector = InterferenceTimbreProjector()
        alternating = projector.process(
            base_amplitudes=[0.5] * 4,
            mode_ids=("M1", "M2", "M3", "M4"),
            source_id="test",
            source_revision=1,
            control=InterferenceTimbreControl(
                phase_spread_radians=np.pi,
                depth=1.0,
            ),
        )
        self.assertAlmostEqual(alternating.output_power, alternating.base_power)
        self.assertEqual(alternating.output_amplitudes[1], 0.0)
        cancelled = projector.process(
            base_amplitudes=[0.5] * 4,
            mode_ids=("M1", "M2", "M3", "M4"),
            source_id="test",
            source_revision=2,
            control=InterferenceTimbreControl(phase_radians=np.pi, depth=1.0),
        )
        self.assertTrue(cancelled.complete_cancellation)
        self.assertTrue(np.all(cancelled.output_amplitudes == 0.0))

    def test_geometry_packet_is_complete(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        client = RecordingClient()
        MembraneOSCPublisher(client).publish_geometry(engine.geometry)
        addresses = [address for address, _ in client.messages]
        self.assertEqual(addresses.count(f"{ROOT}/geometry/vertex"), 42)
        self.assertEqual(addresses.count(f"{ROOT}/geometry/face"), 80)
        self.assertEqual(addresses[0], f"{ROOT}/geometry/begin")
        self.assertEqual(addresses[-1], f"{ROOT}/geometry/end")


if __name__ == "__main__":
    unittest.main()
