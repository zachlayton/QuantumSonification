from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


updater = load_module(
    "platonic_noise_updater",
    HERE / "update_qmw_platonic_noise_excitation_v1.py",
)
FORK = HERE.parent / "qmw_platonic_geometry_reverb_noise_excitation_v1"


def load_builder():
    return load_module("platonic_noise_builder", FORK / updater.BUILDER)


class PlatonicNoiseExcitationUpdateTests(unittest.TestCase):
    def test_integrated_fork_is_already_updated(self) -> None:
        planned = updater.preflight(FORK)
        changed = [path for path, (_, did_change) in planned.items() if did_change]
        self.assertEqual(changed, [])

    def test_replacement_is_idempotent_when_anchor_is_retained(self) -> None:
        replacement = updater.Replacement(
            "History apz4(0);",
            "History apz4(0);\nHistory onset_fast(0);",
            "retained-prefix fixture",
        )
        once, first_applied = updater.replace_once(
            "History apz4(0);", replacement
        )
        twice, second_applied = updater.replace_once(once, replacement)
        self.assertTrue(first_applied)
        self.assertFalse(second_applied)
        self.assertEqual(once, twice)

    def test_generator_and_checked_in_outputs_match(self) -> None:
        builder = load_builder()
        solids, _ = builder.build_tables()
        expected = {
            updater.GENEXPR: builder.make_genexpr(solids),
            updater.CONTROLLER: builder.make_controller(),
            updater.README: builder.make_readme(solids),
        }
        for name, generated in expected.items():
            checked_in = (FORK / name).read_text(encoding="utf-8")
            self.assertEqual(generated, checked_in, name)

    def test_noise_excitation_contract(self) -> None:
        gen = (FORK / updater.GENEXPR).read_text(encoding="utf-8")
        self.assertEqual(gen.count("Delay dl"), 20)
        self.assertEqual(gen.count(".write("), 20)
        self.assertIn("Param noise_amount(0.22);", gen)
        self.assertIn("onset_fast_samples = max(0.0015 * sr, 1);", gen)
        self.assertIn("onset_slow_samples = max(0.035 * sr, 1);", gen)
        self.assertIn("noise_cut_hz = min(", gen)
        self.assertIn("x = excitation;", gen)
        self.assertLess(gen.index("x = excitation;"), gen.index("a1d = x"))

    def test_max_patch_embeds_forked_dsp_and_controls(self) -> None:
        payload = json.loads(
            (FORK / "QMW_Platonic_Noise_Excitation_v1.maxpat").read_text(
                encoding="utf-8"
            )
        )
        boxes = [item["box"] for item in payload["patcher"]["boxes"]]
        codebox = next(box for box in boxes if box.get("id") == "obj-1")
        self.assertEqual(
            codebox["code"],
            (FORK / updater.GENEXPR).read_text(encoding="utf-8"),
        )
        messages = {box.get("text") for box in boxes}
        self.assertIn("noise_amount 0.22", messages)
        self.assertIn("noise_floor 0", messages)
        controller_lines = [
            line["patchline"]
            for line in payload["patcher"]["lines"]
            if str(line["patchline"]["source"][0]).startswith("obj-noise-")
        ]
        self.assertEqual(len(controller_lines), 6)


if __name__ == "__main__":
    unittest.main()
