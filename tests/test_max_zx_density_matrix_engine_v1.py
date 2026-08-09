from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from density.density_state_injection import qac_lsb_to_engine_density
from quantum_population_osc_v9_resonator import MLXQuantumResonatorEngine


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "max" / "QMW_ZX_Density_Matrix_Engine_v1.maxpat"
SCRIPT = ROOT / "max" / "qmw_zx_density_matrix_engine_v1.js"


class MaxZXDensityMatrixEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        patcher = json.loads(PATCH.read_text(encoding="utf-8"))["patcher"]
        cls.boxes = {
            item["box"]["id"]: item["box"]
            for item in patcher["boxes"]
        }
        cls.lines = patcher["lines"]
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_receives_dedicated_atomic_density_protocol(self) -> None:
        self.assertEqual(self.boxes["udp"]["text"], "udpreceive 7498")
        routes = self.boxes["routes"]["text"]
        for path in (
            "begin",
            "meta",
            "probabilities",
            "row",
            "bloch",
            "end",
            "error",
            "commit_sent",
        ):
            self.assertIn(f"/qmw/zx/density/{path}", routes)
        for path in ("verified", "live", "error"):
            self.assertIn(f"/qmw/zx/pauli/{path}", routes)
        self.assertIn("/qmw/zx/pauli/score_verified", routes)
        self.assertIn("/qmw/zx/pauli/active", routes)
        self.assertIn("/qmw/zx/euler/result", routes)

    def test_reconstructor_requires_every_row_before_commit(self) -> None:
        self.assertIn("function configureDimension(dimension)", self.script)
        self.assertIn("var MAX_DIMENSION = 256;", self.script)
        self.assertIn("args.length < 2 + 2 * DIMENSION", self.script)
        self.assertIn("function allRowsPresent()", self.script)
        self.assertIn("if (!allRowsPresent())", self.script)
        self.assertIn("for (var rowIndex = 0; rowIndex < DIMENSION", self.script)
        self.assertIn("commitFrame(String(args[1]))", self.script)

    def test_exposes_matrix_buses_and_mc_instrument(self) -> None:
        texts = {
            box.get("text", "")
            for box in self.boxes.values()
        }
        for text in (
            "s qmw.zx.rho.complex.matrix",
            "s qmw.zx.rho.real.matrix",
            "s qmw.zx.rho.imag.matrix",
            "s qmw.zx.rho.magnitude.matrix",
            "s qmw.zx.rho.phase.matrix",
            "mc.cycle~ @chans 16",
            "mc.mixdown~ 2 @autogain 1",
            "ezdac~",
        ):
            self.assertIn(text, texts)
        self.assertIn('messnamed("qmw.zx.density.real"', self.script)
        self.assertIn('messnamed("qmw.zx.density.imag"', self.script)

    def test_active_pauli_is_published_and_recomputed_per_matrix(self) -> None:
        self.assertIn("function pauli_verified()", self.script)
        self.assertIn("function pauli_live()", self.script)
        self.assertIn("function pauli_score_verified()", self.script)
        self.assertIn("function pauli_active()", self.script)
        self.assertIn("function euler_result()", self.script)
        self.assertIn("function publishActivePauliFromMatrix()", self.script)
        self.assertIn('messnamed("qmw.zx.pauli.expectation"', self.script)
        self.assertIn("publishActivePauliFromMatrix();", self.script)
        self.assertIn('messnamed("qmw.euler.theta"', self.script)
        self.assertIn('messnamed("qmw.euler.gamma"', self.script)
        self.assertIn('"qmw.euler.pi_result"', self.script)
        self.assertIn('"qmw.euler.theta_pi"', self.script)
        self.assertIn('"qmw.euler.zx_scalar_phase_pi"', self.script)

    def test_dynamic_density_dimension_reaches_max_ui(self) -> None:
        self.assertEqual(
            self.boxes["density_dimension_receive"]["text"],
            "r qmw.zx.density.dimension",
        )
        self.assertEqual(
            self.boxes["population_size"]["text"],
            "prepend size",
        )
        self.assertIn(
            'messnamed("qmw.zx.density.dimension", DIMENSION)',
            self.script,
        )
        self.assertIn(
            'messnamed("qmw.zx.density.qubits", QUBITS)',
            self.script,
        )
        self.assertIn("if (DIMENSION !== 16", self.script)

    def test_visible_euler_panel_separates_metadata_and_angles(self) -> None:
        self.assertEqual(
            self.boxes["euler_receive"]["text"],
            "r qmw.euler.result",
        )
        self.assertEqual(
            self.boxes["euler_unpack"]["text"],
            "unpack i s i s f f f f f i f",
        )
        self.assertEqual(
            self.boxes["euler_theta_pi_receive"]["text"],
            "r qmw.euler.theta_pi",
        )
        self.assertEqual(
            self.boxes["euler_scalar_pi_receive"]["text"],
            "r qmw.euler.zx_scalar_phase_pi",
        )
        for identifier in (
            "euler_request",
            "euler_source",
            "euler_qubit",
            "euler_basis",
            "euler_theta",
            "euler_theta_pi",
            "euler_phi",
            "euler_phi_pi",
            "euler_lambda",
            "euler_lambda_pi",
            "euler_gamma",
            "euler_gamma_pi",
            "euler_scalar",
            "euler_scalar_pi",
            "euler_verified",
            "euler_error",
        ):
            self.assertIn(identifier, self.boxes)

    def test_resonator_publishes_complete_evolving_matrix(self) -> None:
        class Capture:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, value) -> None:
                self.messages.append((address, value))

        engine = MLXQuantumResonatorEngine.__new__(MLXQuantumResonatorEngine)
        engine.zx_density_matrix_osc = Capture()
        engine.zx_density_matrix_revision = 0
        engine.step_count = 42
        state = np.zeros(16, dtype=np.complex128)
        state[1] = 1.0
        rho_lsb = np.outer(state, state.conj())
        rho_engine = qac_lsb_to_engine_density(rho_lsb)

        self.assertTrue(engine.send_zx_density_matrix_frame(rho_engine))
        messages = engine.zx_density_matrix_osc.messages
        addresses = [address for address, _payload in messages]
        self.assertEqual(addresses.count("/qmw/zx/density/row"), 16)
        self.assertEqual(addresses.count("/qmw/zx/density/bloch"), 4)
        self.assertEqual(addresses[0], "/qmw/zx/density/begin")
        self.assertEqual(addresses[-1], "/qmw/zx/density/end")
        self.assertEqual(messages[0][1][1], "engine_evolution")
        probabilities = next(
            payload
            for address, payload in messages
            if address == "/qmw/zx/density/probabilities"
        )
        self.assertAlmostEqual(probabilities[2], 1.0)
        first_row = next(
            payload
            for address, payload in messages
            if address == "/qmw/zx/density/row"
        )
        self.assertEqual(len(first_row), 34)


if __name__ == "__main__":
    unittest.main()
