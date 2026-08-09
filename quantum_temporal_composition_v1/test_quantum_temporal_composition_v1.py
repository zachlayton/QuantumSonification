from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from quantum_temporal_composition_v1.core import PageWoottersEstimator, QuantumTemporalCompositionSystem, TemporalConfig
from quantum_temporal_composition_v1.osc_output import OSCPublisher
from quantum_temporal_composition_v1.quantum_sources import DensityFileSource, DeterministicFallbackSource, ExistingEngineSource


class QuantumTemporalCompositionV1Tests(unittest.TestCase):
    def test_page_wootters_condition_is_normalized(self):
        rho, _ = DeterministicFallbackSource(3).read(7, 0.1)
        phase, confidence, probability, conditional = PageWoottersEstimator(2).estimate(rho)
        self.assertTrue(0 <= phase < math.tau)
        self.assertTrue(0 <= confidence <= 1)
        self.assertGreater(probability, 0)
        self.assertEqual(conditional.shape, (2, 2))
        self.assertAlmostEqual(float(np.trace(conditional).real), 1.0)

    def test_deterministic_run_and_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshots.jsonl"
            config = TemporalConfig(seed=9, osc_enabled=False, log_path=str(path), branch_tracking=True, branch_threshold=0.0)
            first = QuantumTemporalCompositionSystem(config).run(8, realtime=False)
            second = QuantumTemporalCompositionSystem(TemporalConfig(**{**config.__dict__, "log_path": None})).run(8, realtime=False)
            self.assertEqual([s.events for s in first], [s.events for s in second])
            self.assertTrue(first[-1].branches)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 8)
            self.assertIn("processes", rows[-1])

    def test_density_npz_source(self):
        with tempfile.TemporaryDirectory() as directory:
            rho, _ = DeterministicFallbackSource().read(2, 0.1)
            path = Path(directory) / "rho.npz"
            np.savez(path, rho=rho)
            loaded, name = DensityFileSource(path).read(0, 0.1)
            self.assertTrue(np.allclose(loaded, rho))
            self.assertTrue(name.startswith("density-file:"))

    def test_existing_engine_source_accepts_density_step(self):
        rho, _ = DeterministicFallbackSource().read(1, 0.1)
        class Engine:
            def step(self, dt): return rho
        loaded, name = ExistingEngineSource(Engine()).read(0, 0.1)
        self.assertTrue(np.allclose(loaded, rho))
        self.assertEqual(name, "existing-engine:Engine")

    def test_osc_contract_without_network(self):
        class Client:
            def __init__(self): self.messages = []
            def send_message(self, address, args): self.messages.append((address, args))
        client = Client()
        publisher = OSCPublisher("127.0.0.1", 1, client=client)
        config = TemporalConfig(seed=2, osc_enabled=True, log_path=None)
        QuantumTemporalCompositionSystem(config, publisher=publisher).run(1, realtime=False)
        addresses = [address for address, _ in client.messages]
        self.assertEqual(addresses[0], "/qmw/temporal/v1/snapshot/begin")
        self.assertIn("/qmw/temporal/v1/clock", addresses)
        self.assertEqual(addresses[-1], "/qmw/temporal/v1/snapshot/end")


if __name__ == "__main__":
    unittest.main()
