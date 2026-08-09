from __future__ import annotations

import unittest

from heisenberg_instrument_v2.build_qmw_heisenberg_rings_matrix_instrument_v2 import (
    main_patch,
    voice_patch,
)


def wiring(document: dict) -> set[tuple[str, int, str, int]]:
    return {
        (
            entry["patchline"]["source"][0],
            entry["patchline"]["source"][1],
            entry["patchline"]["destination"][0],
            entry["patchline"]["destination"][1],
        )
        for entry in document["patcher"]["lines"]
    }


class RingsMatrixInstrumentTests(unittest.TestCase):
    def test_main_patch_uses_sixteen_voice_poly_and_separate_memory(self) -> None:
        document = main_patch()
        boxes = {entry["box"]["id"]: entry["box"] for entry in document["patcher"]["boxes"]}

        self.assertEqual(boxes["poly"]["text"], "poly~ qmb_heisenberg_rings_voice_v2 16")
        self.assertEqual(
            boxes["poke"]["text"],
            "jit.poke~ qmb_heisenberg_rings_memory 2 0",
        )
        self.assertIn("qmb_heisenberg_rings_memory", boxes["mem_matrix"]["text"])
        self.assertNotIn("contributions", boxes["poke"]["text"])
        self.assertEqual(boxes["retry_udp"]["text"], "port 7400")
        self.assertIn(("retry_udp", 0, "udp", 0), wiring(document))
        self.assertEqual(boxes["phase_send"]["text"], "udpsend 127.0.0.1 7421")
        self.assertIn("/qmw/bridge/observable/phase", boxes["phase_prepend"]["text"])
        self.assertIn(("phase_norm", 0, "phase_clip", 0), wiring(document))
        self.assertEqual(boxes["phase_depth_prepend"]["text"], "prepend phase_depth")
        self.assertIn(("phase_depth_prepend", 0, "controller", 0), wiring(document))
        self.assertIn(("xz", 0, "phase_send", 0), wiring(document))
        self.assertIn(("y0", 0, "phase_send", 0), wiring(document))
        self.assertIn(("four_observable", 0, "phase_send", 0), wiring(document))
        self.assertIn("/qmw/bridge/output_hz", boxes["rate_prepend"]["text"])
        self.assertIn("/qmw/bridge/smoothing_ms", boxes["smooth_prepend"]["text"])
        self.assertIn("/qmw/bridge/clock/timing quantum", boxes["clock_quantum"]["text"])
        self.assertIn("/qmw/bridge/clock/timing rate", boxes["clock_rate"]["text"])
        self.assertIn("/qmw/bridge/clock/distance", boxes["distance_prepend"]["text"])
        self.assertIn("/qmw/bridge/clock/process poisson", boxes["clock_poisson"]["text"])
        self.assertIn("/qmw/bridge/clock/coherence_depth", boxes["coherence_prepend"]["text"])
        self.assertIn(("clock_quantum", 0, "phase_send", 0), wiring(document))
        self.assertIn(("distance_prepend", 0, "phase_send", 0), wiring(document))
        self.assertIn(("coherence_prepend", 0, "phase_send", 0), wiring(document))
        for qubit in range(4):
            self.assertIn(
                f"/qmw/bridge/observable/phase/q{qubit}",
                boxes[f"q{qubit}_prepend"]["text"],
            )
        self.assertIn(("morph_prepend", 0, "controller", 0), wiring(document))
        self.assertIn(("map_example_1", 0, "controller", 0), wiring(document))
        self.assertIn(("map_clear", 0, "controller", 0), wiring(document))
        self.assertIn(("cell_example_1", 0, "controller", 0), wiring(document))
        self.assertIn(("cell_clear", 0, "controller", 0), wiring(document))

    def test_commit_reaches_controller_after_all_matrix_routes(self) -> None:
        lines = wiring(main_patch())
        for tag in ("tag_c", "tag_m", "tag_p", "tag_f", "tag_pan"):
            self.assertIn((tag, 0, "controller", 0), lines)
        self.assertIn(("adapter", 5, "controller", 0), lines)
        self.assertIn(("adapter", 6, "adapter_status", 1), lines)
        self.assertIn(("controller", 1, "poly_router", 0), lines)
        self.assertIn(("poly_router", 0, "poly", 0), lines)

    def test_each_poly_voice_contains_one_monophonic_rings_body(self) -> None:
        document = voice_patch()
        boxes = {entry["box"]["id"]: entry["box"] for entry in document["patcher"]["boxes"]}
        lines = wiring(document)

        self.assertEqual(boxes["rings"]["text"], "vb.mi.rngs~")
        self.assertEqual(boxes["polyphony"]["text"], "polyphony 1")
        self.assertIn(("peek", 0, "exc_amp", 0), lines)
        self.assertIn(("exc_amp", 0, "rings", 0), lines)
        self.assertIn(("struct_target", 0, "struct", 0), lines)
        self.assertIn(("amp_target", 0, "amp_sig", 0), lines)
        self.assertIn(("struct", 0, "rings", 2), lines)
        self.assertIn(("bright", 0, "rings", 3), lines)
        self.assertIn(("damp", 0, "rings", 4), lines)
        self.assertIn(("pos", 0, "rings", 5), lines)


if __name__ == "__main__":
    unittest.main()
