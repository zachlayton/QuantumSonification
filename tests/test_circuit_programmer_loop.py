from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"


class CircuitProgrammerLoopTests(unittest.TestCase):
    def test_refreshed_programmer_contains_bounded_loop_transport(self) -> None:
        source = (MAX / "qmw_qac_circuit_programmer_recursive_v3_3.js").read_text(
            encoding="utf-8"
        )
        for token in (
            "new Task(loopTick, this)",
            "activeCol = (activeCol + 1) % COLS",
            "loopIntervalMs = Math.max(30, Math.min(4000",
            "loopTask.repeat()",
            "loopTask.cancel()",
            'loopRunning ? "STOP LOOP" : "LOOP " + loopIntervalMs',
        ):
            self.assertIn(token, source)

    def test_v5_embeds_the_loop_enabled_cache_busted_programmer(self) -> None:
        instrument = json.loads(
            (MAX / "QMW_Complete_CPS_Flow_Instrument_v5.maxpat").read_text(
                encoding="utf-8"
            )
        )["patcher"]
        boxes = {entry["box"]["id"]: entry["box"] for entry in instrument["boxes"]}
        self.assertEqual(
            boxes["programmer"]["name"],
            "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat",
        )
        programmer = json.loads(
            (MAX / boxes["programmer"]["name"]).read_text(encoding="utf-8")
        )["patcher"]
        programmer_boxes = {
            entry["box"]["id"]: entry["box"] for entry in programmer["boxes"]
        }
        self.assertEqual(
            programmer_boxes["ui"]["filename"],
            "qmw_qac_circuit_programmer_recursive_v3_3.js",
        )


if __name__ == "__main__":
    unittest.main()
