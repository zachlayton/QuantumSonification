import json
import plistlib
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package" / "QMW-Native"
EXTERNALS = {
    name: (
        PACKAGE / "externals" / f"{name}.mxo",
        PACKAGE / "externals" / f"{name}.mxo" / "Contents" / "MacOS" / name,
    )
    for name in (
        "qmw.state",
        "qmw.hamiltonian",
        "qmw.pauli",
        "qmw.evolve",
        "qmw.observe",
        "qmw.uncertainty",
        "qmw.transition",
        "qmw.measure",
        "qmw.spectrum",
        "qmw.qmm",
        "qmw.flow",
        "qmw.resonator~",
        "qmw.interference~",
        "qmw.excite~",
        "qmw.lorentz~",
        "qmw.memory~",
        "qmw.modalbank~",
    )
}


class QmwNativePackageTests(unittest.TestCase):
    def test_package_manifest_and_help_patch_are_valid_json(self):
        manifest = json.loads((PACKAGE / "package-info.json").read_text())
        help_patch = json.loads((PACKAGE / "help" / "qmw.state.maxhelp").read_text())
        observe_help = json.loads(
            (PACKAGE / "help" / "qmw.observe.maxhelp").read_text()
        )
        self.assertEqual(manifest["name"], "QMW-Native")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(len(EXTERNALS), 17)
        object_texts = {
            item["box"].get("text")
            for item in help_patch["patcher"]["boxes"]
            if item["box"].get("maxclass") == "newobj"
        }
        self.assertIn("qmw.state 1", object_texts)
        self.assertIn("print qmw.rho", object_texts)
        self.assertIn("print qmw.metrics", object_texts)
        self.assertIn("print qmw.status", object_texts)

        observe_objects = {
            item["box"].get("text")
            for item in observe_help["patcher"]["boxes"]
            if item["box"].get("maxclass") == "newobj"
        }
        self.assertIn("qmw.state 1", observe_objects)
        self.assertIn("qmw.observe X 0 1", observe_objects)
        self.assertIn("qmw.observe Y 0 1", observe_objects)
        self.assertIn("qmw.observe Z 0 1", observe_objects)

        demo = json.loads(
            (PACKAGE / "patchers" / "QMW_Native_State_Demo_v0_1.maxpat").read_text()
        )
        observe_demo = json.loads(
            (PACKAGE / "patchers" / "QMW_Native_Observe_Demo_v0_1.maxpat").read_text()
        )
        catalog = json.loads(
            (PACKAGE / "patchers" / "QMW_Native_Object_Catalog_v0_1.maxpat").read_text()
        )
        self.assertEqual(demo["patcher"]["fileversion"], 1)
        self.assertEqual(observe_demo["patcher"]["fileversion"], 1)
        self.assertEqual(catalog["patcher"]["fileversion"], 1)

        catalog_objects = [
            item["box"].get("text", "").split(" ", 1)[0]
            for item in catalog["patcher"]["boxes"]
            if item["box"].get("maxclass") == "newobj"
        ]
        self.assertCountEqual(catalog_objects, EXTERNALS.keys())

    def test_bundle_metadata_matches_externals(self):
        for name, (bundle, _) in EXTERNALS.items():
            with self.subTest(name=name):
                with (bundle / "Contents" / "Info.plist").open("rb") as stream:
                    info = plistlib.load(stream)
                self.assertEqual(info["CFBundleExecutable"], name)
                self.assertEqual(info["CFBundlePackageType"], "iLaX")
                self.assertEqual(
                    (bundle / "Contents" / "PkgInfo").read_text(),
                    "iLaXmax2\n",
                )

    def test_built_externals_are_universal_signed_and_export_entry_point(self):
        for name, (bundle, binary) in EXTERNALS.items():
            with self.subTest(name=name):
                self.assertTrue(binary.is_file())
                description = subprocess.run(
                    ["file", str(binary)], check=True, capture_output=True, text=True
                ).stdout
                symbols = subprocess.run(
                    ["nm", "-gU", str(binary)], check=True, capture_output=True, text=True
                ).stdout
                subprocess.run(
                    ["codesign", "--verify", "--deep", "--strict", str(bundle)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("universal binary", description)
                self.assertIn("x86_64", description)
                self.assertIn("arm64", description)
                self.assertIn("_ext_main", symbols)

    def test_recorded_binary_checksums_match_package(self):
        subprocess.run(
            ["shasum", "-a", "256", "-c", str(ROOT / "BINARY_SHA256SUMS.txt")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_help_patch_exercises_atomic_and_rejection_paths(self):
        patcher = json.loads((PACKAGE / "help" / "qmw.state.maxhelp").read_text())["patcher"]
        messages = {
            item["box"].get("text", "")
            for item in patcher["boxes"]
            if item["box"].get("maxclass") == "message"
        }
        self.assertIn("real 1 1. 0. 0. 0.", messages)
        self.assertIn("imag 1 0. 0. 0. 0.", messages)
        self.assertIn("real 2 0.5 0. 0. 0.5", messages)
        self.assertIn("real 3 1.1 0. 0. -0.1", messages)
        self.assertIn("clear", messages)

    def test_observer_help_fans_one_state_revision_to_three_axes(self):
        patcher = json.loads(
            (PACKAGE / "help" / "qmw.observe.maxhelp").read_text()
        )["patcher"]
        edges = {
            (
                tuple(item["patchline"]["source"]),
                tuple(item["patchline"]["destination"]),
            )
            for item in patcher["lines"]
        }
        for observer in ("observe_x", "observe_y", "observe_z"):
            self.assertIn((("state", 0), (observer, 0)), edges)

        messages = {
            item["box"].get("text", "")
            for item in patcher["boxes"]
            if item["box"].get("maxclass") == "message"
        }
        self.assertIn("real 2 0.5 0.5 0.5 0.5", messages)
        self.assertIn("imag 2 0. 0. 0. 0.", messages)


if __name__ == "__main__":
    unittest.main()
