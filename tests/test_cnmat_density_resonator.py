from __future__ import annotations

import math
import json
import threading
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from density.cnmat_resonator_model import density_matrix_to_cnmat_resonators
from quantum_population_osc_v9_resonator import MLXQuantumResonatorEngine
from qmw_temporal_crystal16_v1 import build_live_temporal_layer


class RecordingOSCClient:
    def __init__(self) -> None:
        self.messages = []

    def send_message(self, address, value) -> None:
        self.messages.append((address, value))


class CNMATDensityResonatorTests(unittest.TestCase):
    def test_four_qubit_model_has_256_complete_triples(self) -> None:
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0, 0] = 1.0
        frame = density_matrix_to_cnmat_resonators(rho, np.diag(np.arange(16)))

        self.assertEqual(frame.dimension, 16)
        self.assertEqual(frame.resonance_count, 256)
        self.assertEqual(len(frame.flat_triples()), 768)
        self.assertEqual(len(frame.triple_rows()), 16)
        self.assertTrue(all(len(row) == 48 for row in frame.triple_rows()))

    def test_energy_gaps_control_off_diagonal_frequencies(self) -> None:
        rho = np.full((3, 3), 1.0 / 3.0, dtype=np.complex128)
        energies = np.diag([0.0, 1.0, 4.0])
        frame = density_matrix_to_cnmat_resonators(
            rho,
            energies,
            minimum_frequency_hz=20.0,
            maximum_frequency_hz=4_000.0,
        )
        frequencies = frame.frequencies_hz.reshape(3, 3)

        self.assertTrue(math.isclose(frequencies[0, 2], 4_000.0))
        self.assertTrue(math.isclose(frequencies[0, 1], 1_000.0))
        self.assertTrue(math.isclose(frequencies[1, 2], 3_000.0))
        self.assertTrue(np.allclose(frequencies, frequencies.T))

    def test_density_is_rotated_into_energy_basis(self) -> None:
        rho = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128)
        hadamard = np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
        hamiltonian = hadamard @ np.diag([0.0, 2.0]) @ hadamard.T
        frame = density_matrix_to_cnmat_resonators(rho, hamiltonian)

        gains = frame.gains.reshape(2, 2)
        self.assertTrue(np.allclose(gains, np.full((2, 2), gains[0, 0])))

    def test_gain_is_bounded_and_stronger_relations_ring_longer(self) -> None:
        rho = np.diag([0.8, 0.2]).astype(np.complex128)
        frame = density_matrix_to_cnmat_resonators(
            rho,
            np.diag([0.0, 1.0]),
            total_gain=0.5,
        )
        gains = frame.gains.reshape(2, 2)
        decays = frame.decays_seconds.reshape(2, 2)

        self.assertTrue(math.isclose(float(np.linalg.norm(gains)), 0.5))
        self.assertGreater(gains[0, 0], gains[1, 1])
        self.assertGreater(decays[0, 0], decays[1, 1])
        self.assertEqual(gains[0, 1], 0.0)

    def test_invalid_shapes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            density_matrix_to_cnmat_resonators(np.eye(3), np.eye(2))

    def test_engine_publishes_bracketed_bounded_rows(self) -> None:
        engine = MLXQuantumResonatorEngine.__new__(MLXQuantumResonatorEngine)
        engine.cnmat_resonator_revision = 0
        engine.osc = RecordingOSCClient()
        engine.density_engine = type(
            "DensityEngineStub",
            (),
            {"hamiltonian": lambda self: np.diag(np.arange(16))},
        )()
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0, 0] = 1.0

        self.assertTrue(engine.send_cnmat_density_resonator_frame(rho))
        messages = engine.osc.messages
        self.assertEqual(len(messages), 18)
        self.assertEqual(messages[0][0], "/qmw/cnmat/density_resonator/begin")
        self.assertEqual(messages[-1], ("/qmw/cnmat/density_resonator/end", [1]))
        self.assertTrue(all(len(payload) == 50 for _, payload in messages[1:-1]))
        self.assertEqual([payload[1] for _, payload in messages[1:-1]], list(range(16)))

    def test_max_patch_routes_canonical_model_and_qtm_v1_pulses(self) -> None:
        root = Path(__file__).resolve().parent
        patch = json.loads(
            (root / "max" / "QMW_Density_CNMAT_Resonator_v1.maxpat").read_text(
                encoding="utf-8"
            )
        )
        texts = {
            item["box"].get("text")
            for item in patch["patcher"]["boxes"]
            if item["box"].get("text")
        }

        self.assertIn("udpreceive 7400", texts)
        self.assertIn("OSC-route /density_resonator", texts)
        self.assertIn("OSC-route /temporal-mechanics", texts)
        self.assertIn("OSC-route /density-clock", texts)
        self.assertIn("OSC-route /pulse", texts)
        self.assertIn("resonators~ smooth", texts)
        self.assertIn("click~", texts)

    def test_temporal_crystal_patch_routes_chronos_into_trigger_path(self) -> None:
        root = Path(__file__).resolve().parent
        patch = json.loads(
            (
                root
                / "max"
                / "QMW_Temporal_Crystal16_CNMAT_Resonator_v1.maxpat"
            ).read_text(encoding="utf-8")
        )
        boxes = {
            item["box"]["id"]: item["box"]
            for item in patch["patcher"]["boxes"]
        }
        texts = {
            item.get("text") for item in boxes.values() if item.get("text")
        }
        connections = {
            (
                tuple(item["patchline"]["source"]),
                tuple(item["patchline"]["destination"]),
            )
            for item in patch["patcher"]["lines"]
        }

        self.assertIn("OSC-route /time", texts)
        self.assertIn("OSC-route /tick /index /phase", texts)
        self.assertIn("trigger 0.45", texts)
        self.assertIn("o.pack /qmw/time/control/mode", texts)
        self.assertIn("udpsend 127.0.0.1 7402", texts)
        self.assertIn(
            "js qmw_temporal_crystal16_cnmat_resonator_v1.js",
            texts,
        )
        self.assertIn("OSC-route /state /bits /phase", texts)
        self.assertIn(
            "OSC-route /macrocycle_position /macrocycle_length",
            texts,
        )
        self.assertIn("OSC-route /count /event", texts)
        self.assertIn(
            (("chronos_route", 0), ("tick_dispatch", 0)),
            connections,
        )
        self.assertIn(
            (("tick_dispatch", 1), ("tick_trigger", 0)),
            connections,
        )
        self.assertIn(
            (("tick_trigger", 0), ("js", 0)),
            connections,
        )
        for mode_box in (
            "mode_observer",
            "mode_floquet",
            "mode_lfsr",
            "mode_pythagorean",
        ):
            self.assertIn(
                ((mode_box, 0), ("mode_pack", 0)),
                connections,
            )
        self.assertIn(
            (("mode_pack", 0), ("control_udp", 0)),
            connections,
        )
        self.assertIn(
            (("js", 1), ("click", 0)),
            connections,
        )
        self.assertEqual(boxes["gain_multislider"]["maxclass"], "multislider")
        self.assertEqual(boxes["gain_multislider"]["size"], 256)
        self.assertEqual(boxes["js"]["numinlets"], 3)
        self.assertEqual(boxes["js"]["numoutlets"], 5)
        self.assertIn(
            (("js", 3), ("gain_multislider", 0)),
            connections,
        )
        self.assertIn(
            (("manual_amp", 0), ("js", 0)),
            connections,
        )
        self.assertNotIn(
            (("manual_amp", 0), ("click", 0)),
            connections,
        )
        self.assertEqual(boxes["makeup"]["text"], "*~ 500.")
        self.assertEqual(boxes["safety_clip"]["text"], "clip~ -0.98 0.98")
        self.assertIn(
            (("resonators", 0), ("makeup", 0)),
            connections,
        )
        self.assertIn(
            (("makeup", 0), ("spectral_mix", 0)),
            connections,
        )
        self.assertIn(
            (("spectral_mix", 0), ("safety_clip", 0)),
            connections,
        )
        self.assertIn(
            (("safety_clip", 0), ("gain", 0)),
            connections,
        )
        self.assertIn(
            (("frequency_multiplier", 0), ("js", 2)),
            connections,
        )
        self.assertEqual(boxes["sinusoids"]["text"], "sinusoids~ bwe")
        self.assertIn(
            (("js", 4), ("sinusoids", 0)),
            connections,
        )
        self.assertIn(
            (("sinusoids", 0), ("sine_gain", 0)),
            connections,
        )
        self.assertIn(
            (("sine_gain", 0), ("spectral_mix", 1)),
            connections,
        )

        javascript = (
            root
            / "max"
            / "qmw_temporal_crystal16_cnmat_resonator_v1.js"
        ).read_text(encoding="utf-8")
        self.assertIn("outlets = 5;", javascript)
        self.assertIn("stagedGains = gainVector(pending);", javascript)
        self.assertIn("commitStagedModel();", javascript)
        self.assertIn("function scaleModelFrequencies", javascript)
        self.assertIn("scaled[index]", javascript)
        self.assertIn("function sinusoidModel", javascript)

    def test_engine_switches_temporal_mode_without_restart(self) -> None:
        engine = MLXQuantumResonatorEngine.__new__(MLXQuantumResonatorEngine)
        engine.temporal_crystal_mode = "observer"
        engine.temporal_crystal_rate = 2.0
        engine.temporal_layer = build_live_temporal_layer(
            "observer",
            rate_hz=2.0,
        )
        engine.density_engine = SimpleNamespace(
            temporal_layer=engine.temporal_layer
        )
        engine.density_state_lock = threading.RLock()
        engine.quiet = True
        acknowledgements = []
        engine.send_system_identity = (
            lambda force=False: acknowledgements.append(force)
        )

        selected = engine.set_temporal_crystal_mode("floquet")

        self.assertEqual(selected, "floquet")
        self.assertEqual(engine.temporal_crystal_mode, "floquet")
        self.assertIs(engine.temporal_layer, engine.density_engine.temporal_layer)
        self.assertEqual(acknowledgements, [True])
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0, 0] = 1.0
        self.assertEqual(
            engine.temporal_layer.step(
                rho,
                dt=0.5,
                revision=0,
            ).frame.protocol,
            "floquet_repeated_single_period_map",
        )

        with self.assertRaises(ValueError):
            engine.set_temporal_crystal_mode("not-a-mode")


if __name__ == "__main__":
    unittest.main()
