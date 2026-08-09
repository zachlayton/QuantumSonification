from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from density.density_matrix_engine_4q import DensityMatrixEngine
from qmw_temporal_crystal16_v1 import (
    FloquetEvolver,
    FloquetTimeCrystal16,
    LiveTemporalLayer16,
    build_live_temporal_layer,
)
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
    density_from_state,
)


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, arguments: object) -> None:
        self.messages.append((address, arguments))


class LiveTemporalLayerTests(unittest.TestCase):
    def test_observer_advances_clock_without_claiming_a_revision(self) -> None:
        rho = density_from_state(computational_basis_state(0))
        layer = LiveTemporalLayer16()

        update = layer.step(rho, dt=0.125, revision=7)

        self.assertFalse(update.mutated)
        self.assertEqual(update.frame.revision, 7)
        self.assertEqual(update.frame.tick, 1)
        self.assertAlmostEqual(update.frame.simulation_time, 0.125)
        self.assertTrue(np.allclose(update.frame.rho, rho))
        self.assertEqual(
            update.frame.metadata["canonical_state_owner"],
            "density.DensityMatrixEngine",
        )

    def test_floquet_update_predicts_one_canonical_revision(self) -> None:
        model = FloquetTimeCrystal16()
        rho = model.product_density(0)
        layer = LiveTemporalLayer16(evolver=FloquetEvolver(model))

        update = layer.step(rho, dt=1.0, revision=11)

        self.assertTrue(update.mutated)
        self.assertEqual(update.frame.revision, 12)
        self.assertEqual(
            update.frame.protocol,
            "floquet_repeated_single_period_map",
        )
        self.assertTrue(np.allclose(update.frame.rho, model.step_density(rho)))

    def test_fixed_rate_is_independent_of_engine_frame_rate(self) -> None:
        rho = density_from_state(computational_basis_state(0))
        layer = LiveTemporalLayer16(rate_hz=2.0)

        for _ in range(4):
            self.assertEqual(
                layer.advance(rho, dt=0.1, revision=5),
                (),
            )
        updates = layer.advance(rho, dt=0.1, revision=5)

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].frame.tick, 1)
        self.assertAlmostEqual(updates[0].frame.simulation_time, 0.5)

    def test_mode_factory_builds_each_live_protocol(self) -> None:
        expected = {
            "observer": "observer_no_state_mutation",
            "floquet": "floquet_repeated_single_period_map",
            "lfsr": "programmed_maximal_lfsr_permutation",
            "pythagorean": "programmed_pythagorean_hamiltonian_drive",
        }
        rho = density_from_state(
            np.ones(16, dtype=np.complex128) / 4.0
        )
        for mode, protocol in expected.items():
            with self.subTest(mode=mode):
                layer = build_live_temporal_layer(mode, rate_hz=2.0)
                updates = layer.advance(rho, dt=0.5, revision=3)
                self.assertEqual(len(updates), 1)
                self.assertEqual(updates[0].frame.protocol, protocol)

    def test_reuses_existing_osc_client(self) -> None:
        rho = density_from_state(computational_basis_state(0))
        layer = LiveTemporalLayer16()
        update = layer.step(rho, dt=0.25, revision=3)
        client = RecordingClient()

        layer.publish_frame(client, update.frame)

        messages = dict(client.messages)
        self.assertEqual(messages["/qmw/time/revision"], 3)
        self.assertEqual(messages["/qmw/time/chronos/tick"], 1)
        self.assertEqual(
            messages["/qmw/time/protocol"],
            "observer_no_state_mutation",
        )

    def test_live_density_engine_hook_records_temporal_frame(self) -> None:
        layer = LiveTemporalLayer16()
        with (
            patch(
                "qmw_circuit_bridge.SimpleUDPClient",
                return_value=RecordingClient(),
            ),
            patch.object(LiveTemporalLayer16, "publish_frame"),
        ):
            engine = DensityMatrixEngine(
                enable_circuit_bridge_control=False,
                osc_telemetry_hz=0,
                temporal_layer=layer,
            )
            rho = engine.step(0.01)

        temporal = engine.circuit_state["temporal"]
        self.assertEqual(rho.shape, (16, 16))
        self.assertEqual(temporal["revision"], engine.state_revision)
        self.assertEqual(temporal["tick"], 1)
        self.assertEqual(
            temporal["protocol"],
            "observer_no_state_mutation",
        )
        self.assertFalse(temporal["metadata"]["mutated"])


if __name__ == "__main__":
    unittest.main()
