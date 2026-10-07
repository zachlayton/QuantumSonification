#!/usr/bin/env python3

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "qmw.flow" / "qmw.flow.cpp"


class FlowWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SOURCE.read_text(encoding="utf-8")

    def test_wrapper_protocol_is_explicit_and_atomic(self) -> None:
        required_selectors = {
            "rho_real",
            "rho_imag",
            "hamiltonian_real",
            "hamiltonian_imag",
            "commit",
            "bang",
            "clear",
        }
        registered = set(re.findall(
            r'class_addmethod\([^;]*?"([^"]+)"', self.text, re.DOTALL))
        self.assertTrue(required_selectors <= registered)
        self.assertIn('class_new(\n        "qmw.flow"', self.text)
        self.assertIn("metadata.index_orientation", self.text)
        self.assertIn("metadata.bit_order", self.text)
        self.assertIn("threshold", self.text)

    def test_wrapper_emits_flow_and_audit_metadata(self) -> None:
        for selector in (
            "population_derivative",
            "divergence",
            "current_row",
            "edge",
            "metrics",
            "metadata",
        ):
            self.assertIn(f'gensym("{selector}")', self.text)
        self.assertIn("component_phases_local_gauge_dependent", self.text)
        self.assertIn("transport_product_local_rephasing_invariant", self.text)

    def test_no_state_mutation_evolution_measurement_or_sound_mapping(self) -> None:
        registrations = "\n".join(
            line for line in self.text.splitlines() if "class_addmethod" in line)
        for forbidden in ("evolve", "measure", "trigger", "dsp64", "perform64"):
            self.assertNotIn(forbidden, registrations)


if __name__ == "__main__":
    unittest.main()
