from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

import numpy as np

from quantum_temporal_composition_v2.core import (
    CorrelationDifferentiationClockSystem,
    EdgeClock,
    TemporalV2Config,
)
from quantum_temporal_composition_v2.osc_output import CorrelationClockOSCPublisher
from quantum_temporal_composition_v2.density_correlation_clock import (
    DensityCorrelationClockSystem,
    pairwise_mutual_information,
)
from quantum_temporal_composition_v2.density_correlation_osc import (
    decode_density_payload,
)


class CorrelationClockTests(unittest.TestCase):
    def test_sampling_without_change_does_not_make_time(self):
        edge = EdgeClock("a:b", 0.1, 0.001)
        for _ in range(200):
            _, ticks = edge.sample(0.5, 4)
            self.assertEqual(ticks, [])
        self.assertEqual(edge.edge_time, 0)

    def test_correlation_and_differentiation_are_distinct_ticks(self):
        edge = EdgeClock("a:b", 0.1, 0.0)
        edge.sample(0.2, 4)
        _, correlate = edge.sample(0.35, 4)
        _, differentiate = edge.sample(0.10, 4)
        self.assertEqual(correlate[0][0], "correlate")
        self.assertEqual(differentiate[0][0], "differentiate")
        self.assertEqual(edge.edge_time, 3)

    def test_deterministic_system_advances_relational_time(self):
        config = TemporalV2Config(osc_enabled=False, log_path=None, seed=9)
        first = CorrelationDifferentiationClockSystem(config).run(80, realtime=False)
        second = CorrelationDifferentiationClockSystem(config).run(80, realtime=False)
        first_ticks = [(t.edge, t.kind, t.midi) for s in first for t in s.ticks]
        second_ticks = [(t.edge, t.kind, t.midi) for s in second for t in s.ticks]
        self.assertEqual(first_ticks, second_ticks)
        self.assertGreater(first[-1].relational_time, 0)
        self.assertEqual(first[-1].relational_time, len(first_ticks))

    def test_jsonl_contains_relations_and_ticks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clock.jsonl"
            config = TemporalV2Config(osc_enabled=False, log_path=str(path))
            CorrelationDifferentiationClockSystem(config).run(12, realtime=False)
            text = path.read_text()
            self.assertIn('"relations"', text)
            self.assertIn('"relational_time"', text)

    def test_osc_tick_contract(self):
        class Client:
            def __init__(self): self.messages = []
            def send_message(self, address, value): self.messages.append((address, value))

        client = Client()
        publisher = CorrelationClockOSCPublisher(
            "127.0.0.1", 1, client=client
        )
        config = TemporalV2Config(
            osc_enabled=False, log_path=None, change_quantum=0.01
        )
        system = CorrelationDifferentiationClockSystem(
            config, publisher=publisher
        )
        system.run(8, realtime=False)
        addresses = [address for address, _ in client.messages]
        self.assertIn("/qmw/temporal/v2/relation", addresses)
        self.assertIn("/qmw/temporal/v2/tick", addresses)

    def test_live_density_pair_correlation(self):
        product = np.zeros((4, 4), dtype=np.complex128)
        product[0, 0] = 1.0
        bell = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128)
        bell /= np.linalg.norm(bell)
        bell_rho = np.outer(bell, bell.conj())
        self.assertAlmostEqual(pairwise_mutual_information(product, 0, 1), 0.0)
        self.assertAlmostEqual(pairwise_mutual_information(bell_rho, 0, 1), 1.0)

    def test_live_density_change_creates_correlation_tick(self):
        config = TemporalV2Config(change_quantum=0.1, log_path=None)
        clock = DensityCorrelationClockSystem(config)
        product = np.zeros((4, 4), dtype=np.complex128)
        product[0, 0] = 1.0
        bell = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128)
        bell /= np.linalg.norm(bell)
        clock.update(product, 0)
        snapshot = clock.update(np.outer(bell, bell.conj()), 1)
        self.assertTrue(snapshot.ticks)
        self.assertTrue(all(tick.kind == "correlate" for tick in snapshot.ticks))

    def test_conductor_density_payload_decoder(self):
        rho = np.eye(4, dtype=np.complex128) / 4.0
        flat = rho.reshape(-1)
        raw = np.empty(flat.size * 2)
        raw[0::2] = flat.real
        raw[1::2] = flat.imag
        revision, decoded = decode_density_payload([7, 4, *raw.tolist()])
        self.assertEqual(revision, 7)
        self.assertTrue(np.allclose(decoded, rho))

    def test_max_patch_drives_audio_envelopes_directly_from_ticks(self):
        path = (
            Path(__file__).parent
            / "max"
            / "QMW_Correlation_Differentiation_Clock_v2.maxpat"
        )
        patcher = json.loads(path.read_text())["patcher"]
        boxes = {item["box"]["id"]: item["box"] for item in patcher["boxes"]}
        connections = {
            (tuple(item["patchline"]["source"]), tuple(item["patchline"]["destination"]))
            for item in patcher["lines"]
        }
        object_text = " ".join(str(box.get("text", "")) for box in boxes.values())
        self.assertIn("OSC-route", object_text)
        self.assertNotIn("oscparse", object_text)
        self.assertNotIn("wrap~", object_text)
        self.assertNotIn("send~ qmw.cordiff.audio", object_text)
        self.assertNotIn("receive~ qmw.cordiff.audio", object_text)
        self.assertEqual(
            boxes["quantum_prepend"]["text"],
            "prepend /qmw/temporal/v2/control/change-quantum",
        )
        self.assertEqual(boxes["quantum_udp"]["text"], "udpsend 127.0.0.1 7444")
        self.assertEqual(boxes["quantum_osc"]["text"], "OpenSoundControl")
        self.assertIn(
            (("quantum_packet_trigger", 1), ("quantum_osc", 0)),
            connections,
        )
        self.assertIn(
            (("quantum_packet_trigger", 0), ("quantum_osc", 0)),
            connections,
        )
        self.assertIn(
            (("route", 4), ("config_monitor", 1)),
            connections,
        )
        for kind in ("correlate", "differentiate"):
            self.assertIn("0.", boxes[f"{kind}_env_message"]["text"])
            self.assertIn(
                ((f"{kind}_trigger", 0), (f"{kind}_env_message", 0)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_env_message", 0), (f"{kind}_env", 0)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_env", 0), (f"{kind}_vca", 1)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_vca", 0), ("audio_level", 0)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_unpack", 9), (f"{kind}_vel_clip", 0)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_vel_sig", 0), (f"{kind}_makenote", 1)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_dur_sig", 0), (f"{kind}_makenote", 2)),
                connections,
            )
            self.assertIn(
                ((f"{kind}_click", 0), (f"{kind}_makenote", 4)),
                connections,
            )
            self.assertNotIn(
                ((f"{kind}_click", 0), (f"{kind}_makenote", 1)),
                connections,
            )


if __name__ == "__main__":
    unittest.main()
