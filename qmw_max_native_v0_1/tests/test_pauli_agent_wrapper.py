import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "source" / "qmw.pauli" / "qmw.pauli.cpp").read_text()


class PauliWrapperContractTests(unittest.TestCase):
    def test_public_protocol_is_atomic_and_revisioned(self):
        self.assertIn('"qmw.pauli"', SOURCE)
        for selector in ("identity", "local", "product", "bang", "assist"):
            self.assertIn(f'"{selector}"', SOURCE)
        self.assertIn("stale_revision", (ROOT / "src" / "pauli.cpp").read_text())

    def test_outputs_are_operator_consumer_compatible(self):
        self.assertIn('gensym("operator_real")', SOURCE)
        self.assertIn('gensym("operator_imag")', SOURCE)
        self.assertIn('gensym("metadata")', SOURCE)
        self.assertIn('gensym("factor")', SOURCE)
        self.assertIn('gensym("metrics")', SOURCE)

    def test_basis_units_and_provenance_are_explicit(self):
        header = (ROOT / "include" / "qmw" / "pauli.hpp").read_text()
        for value in ("computational_q0_lsb", "dimensionless", "source_id", "provenance"):
            self.assertIn(value, header)
        self.assertIn('gensym("q0_lsb")', SOURCE)
        self.assertIn('gensym("row_major")', SOURCE)

    def test_object_has_no_state_measurement_evolution_or_audio_authority(self):
        registrations = SOURCE.split('extern "C" void C74_EXPORT ext_main', 1)[1]
        for forbidden in ("measure", "evolve", "dsp64", "event", "rho_real"):
            self.assertNotIn(f'"{forbidden}"', registrations)


if __name__ == "__main__":
    unittest.main()
