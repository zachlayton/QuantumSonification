from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from density.density_spectral_wavetable import (
    density_matrix_to_spectral_wavetable,
)
from quantum_population_osc_v9_resonator import MLXQuantumResonatorEngine


ROOT = Path(__file__).resolve().parent


class RecordingOSCClient:
    def __init__(self) -> None:
        self.messages = []

    def send_message(self, address, value) -> None:
        self.messages.append((address, value))


class DensitySpectralWavetableTests(unittest.TestCase):
    def test_basis_state_produces_bounded_periodic_table(self) -> None:
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0, 0] = 1.0
        frame = density_matrix_to_spectral_wavetable(
            rho,
            np.diag(np.arange(16)),
        )

        self.assertEqual(frame.sample_count, 256)
        self.assertEqual(frame.harmonic_count, 16)
        self.assertEqual(frame.reference_index, 0)
        self.assertTrue(np.all(np.isfinite(frame.samples)))
        self.assertAlmostEqual(float(np.mean(frame.samples)), 0.0, places=12)
        self.assertAlmostEqual(float(np.max(np.abs(frame.samples))), 0.95)
        self.assertAlmostEqual(frame.harmonic_amplitudes[0], 1.0)
        self.assertTrue(
            np.allclose(frame.harmonic_amplitudes[1:], 0.0)
        )

    def test_coherence_phase_changes_waveform_with_fixed_populations(self) -> None:
        plus = np.array([1.0, 1.0], dtype=np.complex128) / np.sqrt(2.0)
        quadrature = np.array([1.0, 1.0j], dtype=np.complex128) / np.sqrt(2.0)
        plus_frame = density_matrix_to_spectral_wavetable(
            np.outer(plus, plus.conj()),
            np.diag([0.0, 1.0]),
        )
        quadrature_frame = density_matrix_to_spectral_wavetable(
            np.outer(quadrature, quadrature.conj()),
            np.diag([0.0, 1.0]),
        )

        self.assertTrue(
            np.allclose(
                plus_frame.harmonic_amplitudes,
                quadrature_frame.harmonic_amplitudes,
            )
        )
        self.assertFalse(
            np.allclose(plus_frame.samples, quadrature_frame.samples)
        )

    def test_engine_publishes_atomic_four_chunk_table(self) -> None:
        engine = MLXQuantumResonatorEngine.__new__(MLXQuantumResonatorEngine)
        engine.density_wavetable_revision = 0
        engine.osc = RecordingOSCClient()
        engine.density_engine = type(
            "DensityEngineStub",
            (),
            {"hamiltonian": lambda self: np.diag(np.arange(16))},
        )()
        rho = np.zeros((16, 16), dtype=np.complex128)
        rho[0, 0] = 1.0

        self.assertTrue(engine.send_density_spectral_wavetable_frame(rho))
        messages = engine.osc.messages
        self.assertEqual(len(messages), 7)
        self.assertEqual(
            messages[0],
            ("/qmw/density/wavetable/begin", [1, 256, 16, 0]),
        )
        chunks = messages[1:5]
        self.assertTrue(
            all(address == "/qmw/density/wavetable/chunk" for address, _ in chunks)
        )
        self.assertEqual([payload[1] for _, payload in chunks], [0, 1, 2, 3])
        self.assertTrue(all(len(payload) == 67 for _, payload in chunks))
        self.assertEqual(
            messages[-1],
            ("/qmw/density/wavetable/end", [1]),
        )

    def test_max_patch_uses_click_latched_double_buffer_voice(self) -> None:
        patch = json.loads(
            (
                ROOT
                / "max"
                / "QMW_Temporal_Crystal16_Spectral_Wavetable_v1.maxpat"
            ).read_text(encoding="utf-8")
        )["patcher"]
        boxes = {
            item["box"]["id"]: item["box"]
            for item in patch["boxes"]
        }
        connections = {
            (
                tuple(item["patchline"]["source"]),
                tuple(item["patchline"]["destination"]),
            )
            for item in patch["lines"]
        }

        self.assertEqual(boxes["waveform"]["size"], 256)
        self.assertEqual(boxes["harmonics"]["size"], 16)
        self.assertEqual(boxes["wave_a"]["text"], "wave~ qmw_tc_wave_A")
        self.assertEqual(boxes["wave_b"]["text"], "wave~ qmw_tc_wave_B")
        self.assertEqual(
            boxes["mode_pack"]["text"],
            "o.pack /qmw/time/control/mode",
        )
        self.assertIn(
            (("tick_dispatch", 1), ("receiver", 1)),
            connections,
        )
        self.assertIn(
            (("receiver", 1), ("xfade_pack", 0)),
            connections,
        )
        self.assertIn(
            (("wave_a_gain", 0), ("wave_sum", 0)),
            connections,
        )
        self.assertIn(
            (("wave_b_gain", 0), ("wave_sum", 1)),
            connections,
        )

        javascript = (
            ROOT
            / "max"
            / "qmw_temporal_crystal16_spectral_wavetable_v1.js"
        ).read_text(encoding="utf-8")
        self.assertIn("qmw_tc_wave_A", javascript)
        self.assertIn("qmw_tc_wave_B", javascript)
        self.assertIn("function commit()", javascript)


if __name__ == "__main__":
    unittest.main()
