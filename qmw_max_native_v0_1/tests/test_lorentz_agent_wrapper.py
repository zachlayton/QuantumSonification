from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.lorentz~" / "qmw.lorentz_tilde.cpp"
HEADER = ROOT / "include" / "qmw" / "lorentz.hpp"


class LorentzWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wrapper = WRAPPER.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_public_object_and_signal_shape_are_explicit(self):
        self.assertIn('"qmw.lorentz~"', self.wrapper)
        self.assertIn("dsp_setup(&object->object, 3)", self.wrapper)
        self.assertEqual(
            self.wrapper.count('outlet_new(reinterpret_cast<t_object*>(object), "signal")'),
            4,
        )
        self.assertIn("input_count < 3", self.wrapper)
        self.assertIn("output_count < 4", self.wrapper)

    def test_controls_are_complete_records_applied_at_vector_boundary(self):
        for selector in (
            '"model"',
            '"charge"',
            '"electric"',
            '"magnetic"',
            '"mapping"',
            '"mute"',
            '"reset"',
        ):
            self.assertIn(selector, self.wrapper)
        self.assertIn("while (commands_.pop(command))", self.wrapper)
        self.assertLess(
            self.wrapper.index("while (commands_.pop(command))"),
            self.wrapper.index("model_.process_block("),
        )
        self.assertIn("std::array<Value, Capacity>", self.wrapper)
        self.assertNotIn("std::mutex", self.wrapper)

    def test_effective_model_declaration_is_mandatory_and_rejects_newtons(self):
        self.assertIn("argc < 7 || argc > 9", self.wrapper)
        for token in (
            "charge_unit",
            "electric_unit",
            "velocity_unit",
            "magnetic_unit",
            "force_unit",
            "source_id",
            "provenance",
            "effective_analogue",
            'value == "N"',
            'value == "newton"',
            "physical Newton units require a separate named calibration adapter",
        ):
            self.assertIn(token, self.wrapper)

    def test_equation_and_nonphysical_mapping_are_separate(self):
        self.assertIn(
            "F_model=q_model*(E_model+cross(v_model,B_model))",
            self.wrapper,
        )
        self.assertIn(
            "signal=headroom*F_model/max(force_reference,norm(F_model))",
            self.wrapper,
        )
        self.assertIn("requested_force_reference", self.wrapper)
        self.assertIn("requested_headroom", self.wrapper)
        self.assertIn(
            "signal = headroom * model_force / max(force_reference, |model_force|)",
            self.header,
        )
        self.assertIn("sonification mapping", self.header)
        self.assertIn("never infers SI units", self.header)

    def test_wrapper_has_no_quantum_state_or_event_authority(self):
        self.assertNotIn('#include "qmw/state.hpp"', self.wrapper)
        self.assertNotIn('#include "qmw/revisioned_state.hpp"', self.wrapper)
        self.assertNotIn('"event"', self.wrapper)
        self.assertNotIn("rho_", self.wrapper)


if __name__ == "__main__":
    unittest.main()
