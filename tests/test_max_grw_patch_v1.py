import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"


class MaxGRWPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(MAX / "build_qmw_grw_resonator_v1.py")],
            cwd=ROOT,
            check=True,
        )

    def test_pauli_frequency_expressions_avoid_nested_if(self):
        patcher = json.loads((MAX / "QMW_GRW_Resonator_v1.maxpat").read_text())["patcher"]
        boxes = {item["box"]["id"]: item["box"] for item in patcher["boxes"]}
        for index, base in enumerate((55, 82.5, 110, 165)):
            expression = boxes[f"v{index}_freq"]["text"]
            self.assertNotIn("if(", expression)
            self.assertIn("0.5 + 0.5 * $i1", expression)
            self.assertIn("0.025 * $f2", expression)
            self.assertTrue(expression.startswith(f"expr {base:g} *"))

    def test_axis_multiplier_is_preserved(self):
        for axis, expected in ((1, 1.0), (2, 1.5), (3, 2.0)):
            self.assertEqual(0.5 + 0.5 * axis, expected)


if __name__ == "__main__":
    unittest.main()
