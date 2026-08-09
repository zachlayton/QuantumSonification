from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from maxpylang_pilot_v1.build_qmw_maxpylang_modal_bank_v1 import (
    OUTPUT,
    build_document,
)


class MaxPyLangPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(Path(OUTPUT).read_text(encoding="utf-8"))
        self.patcher = self.document["patcher"]

    def test_checked_in_patch_has_expected_graph(self) -> None:
        boxes = self.patcher["boxes"]
        lines = self.patcher["lines"]
        self.assertEqual(len(boxes), 16)
        self.assertEqual(len(lines), 14)
        self.assertEqual(self.patcher["appversion"]["major"], 9)
        self.assertFalse(
            any(line["patchline"].get("midpoints") == [None] for line in lines)
        )

        texts = [entry["box"].get("text", "") for entry in boxes]
        self.assertIn("QMW MAXPYLANG MODAL BANK v1", texts)
        self.assertEqual(sum(text.startswith("cycle~ ") for text in texts), 4)
        self.assertIn("ezdac~", texts)

    @unittest.skipUnless(
        importlib.util.find_spec("maxpylang") is not None,
        "MaxPyLang is an optional pilot dependency",
    )
    def test_checked_in_patch_matches_maxpylang_build(self) -> None:
        self.assertEqual(build_document(), self.document)


if __name__ == "__main__":
    unittest.main()
