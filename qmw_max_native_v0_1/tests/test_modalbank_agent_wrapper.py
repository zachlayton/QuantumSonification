import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.modalbank~" / "qmw.modalbank_tilde.cpp"


class ModalBankWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WRAPPER.read_text()

    def test_frequency_and_frequency_hz_selectors_are_registered(self):
        self.assertIn('"frequency", A_GIMME', self.source)
        self.assertIn('"frequency_hz", A_GIMME', self.source)
        self.assertIn("qmw_modalbank_frequency", self.source)

    def test_frequency_message_names_stable_mode_id_and_hz(self):
        self.assertIn("usage: frequency frequency_hz OR frequency mode_id frequency_hz", self.source)
        self.assertIn("argc != 1 && argc != 2", self.source)
        self.assertIn("const bool base_frequency = argc == 1", self.source)
        self.assertIn("std::numeric_limits<std::uint32_t>::max()", self.source)
        self.assertIn("std::isfinite(frequency_hz)", self.source)

    def test_frequency_update_is_applied_at_a_vector_boundary(self):
        self.assertIn("frequency_request_sequence_", self.source)
        self.assertIn("bank_.set_mode_frequency_hz(mode_id, frequency_hz)", self.source)
        self.assertIn("bank_.set_base_frequency_hz(frequency_hz)", self.source)
        self.assertIn('"frequency_queued"', self.source)
        self.assertIn('"vector_boundary"', self.source)

    def test_frequency_result_leaves_audio_thread_through_qelem(self):
        self.assertIn("qmw_modalbank_drain_status", self.source)
        self.assertIn("qelem_set(object->status_qelem)", self.source)
        self.assertIn('"frequency_applied"', self.source)
        self.assertIn('"frequency_rejected"', self.source)

    def test_frequencies_list_is_a_complete_auto_revisioned_frame(self):
        self.assertIn('"frequencies", A_GIMME', self.source)
        self.assertIn("qmw_modalbank_frequencies", self.source)
        self.assertIn("adapter->publish_frequencies", self.source)
        self.assertIn("published_revision_watermark + 1", self.source)
        self.assertIn('"simple_frequencies"', self.source)
        self.assertIn("object->staging = false", self.source)

    def test_frequencies_list_is_bounded_and_all_numeric(self):
        self.assertIn("argc < 1", self.source)
        self.assertIn("qmw::ModalBank::maximum_modes", self.source)
        self.assertIn("frequencies values must all be finite numbers", self.source)


if __name__ == "__main__":
    unittest.main()
