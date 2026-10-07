from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.transition" / "qmw.transition.cpp"
HEADER = ROOT / "include" / "qmw" / "transition.hpp"


class TransitionWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wrapper = WRAPPER.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_public_class_and_complete_revision_inputs_are_registered(self) -> None:
        self.assertIn('class_new(\n        "qmw.transition"', self.wrapper)
        for selector in (
            "rho_real",
            "rho_imag",
            "hamiltonian_real",
            "hamiltonian_imag",
            "operator_real",
            "operator_imag",
            "context",
        ):
            self.assertIn(f'"{selector}", A_GIMME', self.wrapper)

    def test_outputs_preserve_scientific_names_and_provenance(self) -> None:
        for selector in (
            "energies",
            "rho_energy_real",
            "rho_energy_imag",
            "operator_energy_real",
            "operator_energy_imag",
            "diagnostic_activity",
            "degenerate_group",
            "edge",
            "transition",
            "metadata",
            "metrics",
        ):
            self.assertIn(f'"{selector}"', self.wrapper)
        self.assertIn("operator_metadata.source_id", self.wrapper)
        self.assertIn("operator_metadata.provenance", self.wrapper)
        self.assertIn("diagnostic_not_physical_rate", self.wrapper)

    def test_object_has_no_event_measurement_evolution_or_audio_methods(self) -> None:
        registrations = "\n".join(
            line for line in self.wrapper.splitlines() if "class_addmethod" in line
        )
        for forbidden in ("trigger", "schedule", "measure", "evolve", "dsp64", "perform64"):
            self.assertNotIn(forbidden, registrations)

    def test_active_frame_is_an_immutable_read_only_snapshot(self) -> None:
        self.assertIn("const TransitionContext context", self.header)
        self.assertIn("const TransitionUnits units", self.header)
        self.assertIn("const std::vector<TransitionEdge> edges", self.header)
        self.assertIn("const TransitionFrame* active() const noexcept", self.header)


if __name__ == "__main__":
    unittest.main()
