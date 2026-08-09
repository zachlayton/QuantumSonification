import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"


class MaxNativeQuantumInstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(MAX / "build_qmw_native_quantum_instruments_v1.py")],
            cwd=ROOT,
            check=True,
        )
        cls.patcher = json.loads(
            (MAX / "QMW_Native_Quantum_Instruments_v1.maxpat").read_text()
        )["patcher"]
        cls.boxes = {item["box"]["id"]: item["box"] for item in cls.patcher["boxes"]}
        cls.links = {
            (tuple(item["patchline"]["source"]), tuple(item["patchline"]["destination"]))
            for item in cls.patcher["lines"]
        }

    def test_dedicated_native_port_and_root_routes(self):
        self.assertEqual(self.boxes["udp"]["text"], "udpreceive 7482")
        self.assertEqual(self.boxes["root"]["text"], "OSC-route /qmw/instrument")
        self.assertEqual(self.boxes["families"]["text"], "OSC-route /spin /epr /exchange /field /relativistic /dirac /control")
        self.assertIn((("udp", 0), ("root", 0)), self.links)

    def test_umenu_controls_persistent_python_engine(self):
        self.assertEqual(self.boxes["control_send"]["text"], "udpsend 127.0.0.1 7483")
        self.assertEqual(
            self.boxes["control_format"]["text"],
            "o.pack /qmw/instrument/control/select",
        )
        self.assertIn((("source_menu", 1), ("control_format", 0)), self.links)
        self.assertIn((("control_format", 0), ("control_send", 0)), self.links)
        self.assertIn((("control_route", 0), ("selected_prepend", 0)), self.links)
        self.assertIn("all_native", self.boxes["source_menu"]["items"])
        self.assertNotIn("all", self.boxes["source_menu"]["items"])

    def test_spin_frame_reaches_bloch_and_probability_views(self):
        self.assertIn((("families", 0), ("spin_route", 0)), self.links)
        self.assertIn((("spin_unpack", 12), ("spin_bloch_pack", 0)), self.links)
        self.assertIn((("spin_unpack", 16), ("spin_prob_pack", 1)), self.links)
        self.assertIn((("spin_unpack", 4), ("spin_energy", 0)), self.links)
        self.assertIn((("spin_unpack", 5), ("spin_phase", 0)), self.links)
        self.assertIn((("spin_route", 1), ("spin_real", 0)), self.links)
        self.assertIn((("spin_route", 2), ("spin_imag", 0)), self.links)

    def test_epr_and_exchange_observables_are_connected(self):
        self.assertIn((("epr_unpack", 3), ("concurrence", 0)), self.links)
        self.assertIn((("epr_unpack", 4), ("chsh", 0)), self.links)
        self.assertIn((("epr_unpack", 11), ("epr_a_pack", 0)), self.links)
        self.assertIn((("epr_unpack", 14), ("epr_b_pack", 0)), self.links)
        self.assertIn((("epr_route", 1), ("epr_corr", 0)), self.links)
        self.assertIn((("epr_route", 2), ("epr_real", 0)), self.links)
        self.assertIn((("epr_route", 3), ("epr_imag", 0)), self.links)
        self.assertIn((("exchange_unpack", 4), ("swap", 0)), self.links)
        self.assertIn((("exchange_unpack", 5), ("coincidence", 0)), self.links)

    def test_external_field_summary_is_connected(self):
        self.assertIn((("families", 3), ("field_route", 0)), self.links)
        self.assertIn((("field_unpack", 4), ("field_desc_pack", 0)), self.links)
        self.assertIn((("field_unpack", 16), ("field_obs_pack", 0)), self.links)
        self.assertIn("landau_levels", self.boxes["source_menu"]["items"])
        self.assertIn("hydrogen_zeeman", self.boxes["source_menu"]["items"])
        self.assertIn("hydrogen_stark", self.boxes["source_menu"]["items"])

    def test_helium_shell_and_relativistic_modes_are_selectable(self):
        items = self.boxes["source_menu"]["items"]
        self.assertIn("helium_variational_two_electron", items)
        self.assertIn("delta_function_shell", items)
        self.assertIn("dirac_hydrogen_fine_structure", items)
        self.assertIn("dirac_step_klein", items)
        self.assertIn((("families", 4), ("rel_route", 0)), self.links)
        self.assertIn((("families", 5), ("dirac_route", 0)), self.links)
        self.assertIn((("rel_unpack", 4), ("rel_split", 0)), self.links)
        self.assertIn((("dirac_unpack", 4), ("dirac_lr_pack", 0)), self.links)


if __name__ == "__main__":
    unittest.main()
