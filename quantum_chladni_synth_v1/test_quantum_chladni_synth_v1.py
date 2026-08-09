from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from quantum_chladni_synth_v1.quantum_chladni_controller_v1 import (
    QuantumChladniController,
    exact_density_frame,
    load_modal_profile,
    modal_eigenphases,
    qpe_condition_modal_distribution,
)


HERE = Path(__file__).resolve().parent


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class QuantumChladniTests(unittest.TestCase):
    def test_exact_density_is_physical(self) -> None:
        rho = exact_density_frame(0.73, 0.82)
        self.assertEqual(rho.shape, (16, 16))
        np.testing.assert_allclose(rho, rho.conj().T, atol=1e-12)
        self.assertAlmostEqual(float(np.trace(rho).real), 1.0)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(rho))), -1e-12)

    def test_modal_profile_retains_real_eigenbasis(self) -> None:
        profile = load_modal_profile(mode_count=24, visual_samples=96)
        self.assertEqual(profile.eigenvectors.shape, (96, 24))
        self.assertEqual(profile.vertices.shape, (96, 3))
        self.assertTrue(np.all(profile.frequencies_hz > 0.0))

    def test_frame_and_geometry_protocol_are_complete(self) -> None:
        profile = load_modal_profile(mode_count=12, visual_samples=64)
        client = RecordingClient()
        controller = QuantumChladniController(profile, client)
        frame = controller.frame()
        controller.publish(frame)
        controller.publish_geometry()
        addresses = [address for address, _value in client.messages]
        self.assertEqual(addresses.count("/qmw/chladni/mode"), 12)
        self.assertEqual(addresses.count("/qmw/chladni/geometry/vertex"), 64)
        self.assertAlmostEqual(float(np.sum(frame.probabilities)), 1.0)
        self.assertEqual(frame.qpe_bits, 5)
        self.assertEqual(len(frame.qpe_bitstring), 5)
        self.assertEqual(frame.qpe_dominant_mode, int(np.argmax(frame.probabilities)))
        self.assertEqual(frame.basis_populations.shape, (16,))
        self.assertEqual(frame.basis_phases.shape, (16,))
        self.assertAlmostEqual(float(np.sum(frame.basis_populations)), 1.0)
        self.assertTrue(np.all((frame.basis_populations >= 0) & (frame.basis_populations <= 1)))
        self.assertIn("/qmw/chladni/populations", addresses)
        self.assertEqual(addresses[-1], "/qmw/chladni/geometry/end")

    def test_qpe_conditions_the_modal_superposition(self) -> None:
        eigenvalues = np.array([1.0, 1.02, 2.0, 4.0])
        phases = modal_eigenphases(eigenvalues)
        self.assertTrue(np.all(np.diff(phases) > 0.0))
        conditioned = qpe_condition_modal_distribution(
            np.array([0.4, 0.3, 0.2, 0.1]),
            eigenvalues,
            5,
            np.random.default_rng(7),
        )
        self.assertAlmostEqual(float(np.sum(conditioned.posterior)), 1.0)
        self.assertEqual(len(conditioned.posterior), len(eigenvalues))
        self.assertGreaterEqual(conditioned.measured_integer, 0)
        self.assertLess(conditioned.measured_integer, 32)

    def test_generated_patch_is_jitter_first(self) -> None:
        patch = json.loads(
            (HERE / "max" / "QMW_Quantum_Chladni_Synth_v1_5.maxpat").read_text(
                encoding="utf-8"
            )
        )
        texts = {
            entry["box"].get("text", "")
            for entry in patch["patcher"]["boxes"]
        }
        for required in (
            "jit.matrix qchladni_modes 6 float32 24 1",
            "jit.spill @plane 0 @listlength 24",
            "jit.la.mult",
            "jit.normalize",
            "jit.slide @slide_up 5 @slide_down 5",
            "jit.bfg 1 float32 @basis noise.gradient",
            "OSC-route /qmw",
            "OSC-route /chladni",
            "OSC-route /temporal-mechanics/v1/density-clock",
            "prepend temporal_pulse",
            "prepend populations",
            "udpreceive 7400",
            "o.pack /qmw/chladni/control/run",
            "o.pack /qmw/chladni/control/entanglement",
            "o.pack /qmw/chladni/control/geometry",
            "o.pack /qmw/chladni/control/qpe-bits",
            "loadmess demo",
            "t b 1",
            "speedlim 140",
        ):
            self.assertIn(required, texts)
        self.assertNotIn("oscparse", texts)
        self.assertNotIn("list trim", texts)
        self.assertNotIn("adc~ 1 2", texts)
        self.assertNotIn("click~", texts)
        self.assertTrue(any(text.startswith("resonators~ smooth 110.") for text in texts))
        router_source = (
            HERE / "max" / "qmw_quantum_chladni_router_v1.js"
        ).read_text(encoding="utf-8")
        self.assertIn("(1.0 - quantumDepth) * materialGain", router_source)
        self.assertIn("contrastExponent = 10.0", router_source)
        self.assertIn("selectedDecay", router_source)
        self.assertIn("function temporal_pulse", router_source)
        self.assertIn("TEMPORAL STRIKE", router_source)
        self.assertIn("outlets = 25", router_source)
        self.assertIn("new Task(temporal_voice_strike", router_source)
        self.assertIn("energyCompensation", router_source)
        self.assertIn("hasCompleteQuantumFrame()", router_source)
        self.assertIn("spatialDimensionsMatch()", router_source)
        self.assertIn("if (spatialDimensionsMatch()) outlet(6", router_source)
        self.assertNotIn("setcell2d(index, 0, data)", router_source)

    def test_supercollider_frontend_uses_qpe_and_eigenvector_coupling(self) -> None:
        source = (
            HERE
            / "supercollider"
            / "qmw_qpe_chladni_resonator_v1.scd"
        ).read_text(encoding="utf-8")
        for required in (
            "SynthDef(\\qmwQPEChladni24",
            "Ringz.ar",
            'OSCdef(\\qpeChladniBegin',
            'OSCdef(\\qpeChladniGeometryVertex',
            "~qpeChladniPosterior[index].max(0.0).sqrt",
            "base[index] * strikeModes[index] * leftModes[index]",
            '"/qmw/chladni/control/qpe-bits"',
            "s.bind",
        ):
            self.assertIn(required, source)

    def test_quantum_populations_morph_over_time(self) -> None:
        profile = load_modal_profile(mode_count=24, visual_samples=96)
        controller = QuantumChladniController(profile, RecordingClient())
        first = controller.frame()
        later = [controller.frame() for _ in range(7)][-1]
        difference = float(np.max(np.abs(later.probabilities - first.probabilities)))
        self.assertGreater(difference, 0.005)

    def test_density_is_forwarded_to_temporal_machine(self) -> None:
        profile = load_modal_profile(mode_count=12, visual_samples=64)
        temporal = RecordingClient()
        controller = QuantumChladniController(
            profile, RecordingClient(), temporal_client=temporal
        )
        controller.frame()
        address, payload = temporal.messages[-1]
        self.assertEqual(address, "/qmw/temporal/source/density")
        self.assertEqual(len(payload), 2 + 2 * 16 * 16)


if __name__ == "__main__":
    unittest.main()
