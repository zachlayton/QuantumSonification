from __future__ import annotations

import unittest

from heisenberg_instrument_v1.build_qmw_heisenberg_qmb_lab_v4 import build


class QMBHeisenbergLabV4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = build()
        patcher = self.document["patcher"]
        self.boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
        self.lines = {
            (
                entry["patchline"]["source"][0],
                entry["patchline"]["source"][1],
                entry["patchline"]["destination"][0],
                entry["patchline"]["destination"][1],
            )
            for entry in patcher["lines"]
        }

    def test_legacy_renderer_remains_connected(self) -> None:
        self.assertEqual(
            self.boxes["renderer"]["text"],
            "js qmw_heisenberg_clear_renderer_v3.js",
        )
        for source in ("pre_begin", "pre_end", "pre_real", "pre_mag", "pre_freq", "pre_pan"):
            self.assertIn((source, 0, "renderer", 0), self.lines)

    def test_complete_matrix_frame_reaches_qmb_adapter(self) -> None:
        self.assertEqual(
            self.boxes["qmb_adapter"]["text"],
            "js qmb_heisenberg_adapter_v1.js",
        )
        for source in (
            "pre_begin",
            "pre_end",
            "pre_real",
            "pre_imag",
            "pre_mag",
            "pre_phase",
            "pre_freq",
            "pre_pan",
        ):
            self.assertIn((source, 0, "qmb_adapter", 0), self.lines)

    def test_commit_is_visible_and_complex_matrix_is_split_for_parity(self) -> None:
        self.assertIn(("qmb_adapter", 0, "qmb_unpack", 0), self.lines)
        self.assertIn(("qmb_unpack", 0, "qmb_real", 0), self.lines)
        self.assertIn(("qmb_unpack", 1, "qmb_imag", 0), self.lines)
        self.assertIn(("qmb_adapter", 5, "qmb_commit", 1), self.lines)


if __name__ == "__main__":
    unittest.main()
