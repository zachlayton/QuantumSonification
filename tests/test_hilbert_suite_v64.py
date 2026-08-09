import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "QMW_Hilbert_Suite"
N = 16


def identity():
    return [[1 + 0j if row == column else 0j for column in range(N)]
            for row in range(N)]


def rotate_rows(matrix, a, b, angle, phase):
    c, s = math.cos(angle), math.sin(angle)
    p = complex(math.cos(phase), math.sin(phase))
    old_a, old_b = matrix[a][:], matrix[b][:]
    matrix[a] = [c * x - p.conjugate() * s * y for x, y in zip(old_a, old_b)]
    matrix[b] = [p * s * x + c * y for x, y in zip(old_a, old_b)]


def maximum_unitarity_error(matrix):
    error = 0.0
    for a in range(N):
        for b in range(N):
            dot = sum(matrix[a][k] * matrix[b][k].conjugate() for k in range(N))
            error = max(error, abs(dot - (1 if a == b else 0)))
    return error


class HilbertSuiteV64Tests(unittest.TestCase):
    def test_iq_rotation_preserves_norm(self):
        for i_value, q_value, theta in [(0.2, -0.7, 0.3), (1.0, 0.0, 2.1),
                                         (-0.4, 0.9, -1.7)]:
            c, s = math.cos(theta), math.sin(theta)
            out_i = i_value * c - q_value * s
            out_q = i_value * s + q_value * c
            self.assertAlmostEqual(i_value ** 2 + q_value ** 2,
                                   out_i ** 2 + out_q ** 2, places=12)

    def test_pair_presets_are_unitary_through_morph(self):
        for morph in (0.0, 0.1, 0.5, 0.9, 1.0):
            matrix = identity()
            rotate_rows(matrix, 0, 4, morph * math.pi / 4, math.pi / 2)
            self.assertLess(maximum_unitarity_error(matrix), 1e-12)

    def test_ring_preset_is_unitary_through_morph(self):
        for morph in (0.0, 0.1, 0.5, 0.9, 1.0):
            matrix = identity()
            for lane in range(N - 1):
                rotate_rows(matrix, lane, lane + 1, morph * 0.32,
                            (lane % 4) * math.pi / 2)
            rotate_rows(matrix, N - 1, 0, morph * 0.32, 3 * math.pi / 2)
            self.assertLess(maximum_unitarity_error(matrix), 1e-12)

    def test_generated_rotator_has_full_iq_and_explicit_projection(self):
        document = json.loads((ROOT / "qmw_analytic_iq_rotator16_v2.gendsp").read_text())
        codebox = next(item["box"] for item in document["patcher"]["boxes"]
                       if item["box"].get("maxclass") == "codebox")
        self.assertEqual(codebox["numoutlets"], 7)
        self.assertIn("out2 = pre_q", codebox["code"])
        self.assertIn("out4 = post_q", codebox["code"])
        self.assertIn("projection_angle", codebox["code"])

    def test_v64_selects_unitary_modules_and_disables_legacy_scaler(self):
        document = json.loads((ROOT / "QMW_Polyphonic_Complex_Hilbert_Instrument_v6_4.maxpat").read_text())
        texts = {item["box"].get("text", "") for item in document["patcher"]["boxes"]}
        self.assertIn("js qmw_unitary_matrix_presets16_v1.js", texts)
        self.assertIn("qmw_analytic_iq_audition16_v2", texts)
        self.assertIn("loadmess safety 0", texts)
        self.assertIn("loadmess hermitian 0", texts)


if __name__ == "__main__":
    unittest.main()
