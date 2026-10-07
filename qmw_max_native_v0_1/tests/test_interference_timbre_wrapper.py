from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.modalbank~" / "qmw.modalbank_tilde.cpp"


class InterferenceTimbreWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = WRAPPER.read_text(encoding="utf-8")

    def test_interference_controls_are_registered(self) -> None:
        self.assertIn('"interference", A_GIMME', self.source)
        self.assertIn('"interference_off", A_GIMME', self.source)
        self.assertIn("qmw_modalbank_interference", self.source)

    def test_control_is_applied_on_the_audio_vector_boundary(self) -> None:
        self.assertIn("interference_request_sequence_", self.source)
        self.assertIn("bank_.set_interference_timbre", self.source)
        self.assertIn("bank_.clear_interference_timbre", self.source)
        self.assertIn('"interference_queued"', self.source)
        self.assertIn('"interference_applied"', self.source)

    def test_contract_names_all_four_performance_parameters(self) -> None:
        self.assertIn(
            "usage: interference phase_radians spread_radians depth slew_seconds",
            self.source,
        )
        self.assertIn("depth >= 0.0 && depth <= 1.0", self.source)
        self.assertIn("slew_seconds >= 0.0", self.source)


if __name__ == "__main__":
    unittest.main()
