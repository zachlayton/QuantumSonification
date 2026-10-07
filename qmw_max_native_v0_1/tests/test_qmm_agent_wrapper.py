from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.qmm" / "qmw.qmm.cpp"
HEADER = ROOT / "include" / "qmw" / "qmm.hpp"


class QmmWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wrapper = WRAPPER.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_public_object_and_complete_transaction_protocol(self) -> None:
        self.assertIn('class_new(\n        "qmw.qmm"', self.wrapper)
        for selector in (
            "hamiltonian_real",
            "hamiltonian_imag",
            "rho_real",
            "rho_imag",
            "operator_real",
            "operator_imag",
            "partial_real",
            "partial_imag",
            "commit",
        ):
            self.assertIn(f'"{selector}", A_GIMME', self.wrapper)
        self.assertIn("usage: commit revision", self.wrapper)

    def test_outputs_name_equation_terms_and_keep_units_visible(self) -> None:
        for selector in (
            "commutator_real",
            "commutator_imag",
            "derivative_real",
            "derivative_imag",
            "expectation_derivative",
            "metadata",
            "metrics",
        ):
            self.assertIn(f'"{selector}"', self.wrapper)
        for field in (
            "energy_unit",
            "time_unit",
            "operator_unit",
            "basis_id",
            "source_id",
            "provenance",
            "hbar_unit",
            "derivative_unit",
        ):
            self.assertIn(field, self.wrapper)

    def test_active_snapshot_is_read_only_and_revision_matched(self) -> None:
        self.assertIn("explicit commit(revision)", self.header)
        self.assertIn("const QmmSnapshot* active() const noexcept", self.header)
        self.assertIn("Failed transactions preserve", self.header)
        self.assertIn("partial_pair_incomplete", self.header)
        self.assertIn("revision_mismatch", self.header)

    def test_no_time_operator_evolution_measurement_clock_or_audio_surface(self) -> None:
        registrations = "\n".join(
            line for line in self.wrapper.splitlines() if "class_addmethod" in line
        )
        for forbidden in (
            '"evolve"',
            '"measure"',
            '"spectrum"',
            '"transition"',
            '"dsp64"',
            '"perform64"',
            '"time_operator"',
        ):
            self.assertNotIn(forbidden, registrations)
        lowered = self.wrapper.lower()
        for forbidden in ("clock_new", "random_device", "mt19937", "outlet_new(object, \"signal\")"):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
