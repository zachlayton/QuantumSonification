import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "qmw.spectrum" / "qmw.spectrum.cpp"


class SpectrumWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_wrapper_exposes_revision_locked_inputs_and_framed_output(self):
        self.assertIn('"qmw.spectrum"', self.source)
        for token in (
            '"rho_real"',
            '"rho_imag"',
            '"hamiltonian_real"',
            '"hamiltonian_imag"',
            '"waiting_revision_pair"',
            '"frame_begin"',
            '"accepted"',
        ):
            self.assertIn(token, self.source)

    def test_wrapper_exports_full_spectral_payload_and_provenance(self):
        for token in (
            '"energy_eigenvalues"',
            '"energy_eigenvectors_real"',
            '"energy_eigenvectors_imag"',
            '"density_eigenvalues"',
            '"rho_energy_real"',
            '"rho_energy_imag"',
            '"energy_populations"',
            '"basis_overlap"',
            '"metrics"',
            '"provenance"',
            '"energy_degeneracy"',
            '"density_degeneracy"',
        ):
            self.assertIn(token, self.source)

    def test_wrapper_has_no_state_mutation_or_synthesis_surface(self):
        self.assertNotIn("qmw.state", self.source)
        self.assertNotIn("dsp_setup", self.source)
        self.assertNotIn("class_dspinit", self.source)
        self.assertNotIn('"measure"', self.source)
        self.assertNotIn('"evolve"', self.source)

    def test_metadata_is_explicit_at_construction(self):
        self.assertIn("[energy_unit] [basis_id] [source_id] [provenance]", self.source)
        self.assertIn('"computational_q0_lsb"', self.source)
        self.assertIn("provenance.density_unit", self.source)


if __name__ == "__main__":
    unittest.main()
