from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "source" / "qmw.memory~" / "qmw.memory_tilde.cpp"
HEADER = ROOT / "include" / "qmw" / "memory.hpp"


class MemoryWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wrapper = WRAPPER.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_public_object_is_explicit_dual_rail_signal_memory(self):
        self.assertIn('"qmw.memory~"', self.wrapper)
        self.assertIn("dsp_setup(&object->object, 2)", self.wrapper)
        self.assertEqual(
            self.wrapper.count(
                'outlet_new(reinterpret_cast<t_object*>(object), "signal")'
            ),
            2,
        )
        self.assertIn("input_count < 2", self.wrapper)
        self.assertIn("output_count < 2", self.wrapper)
        self.assertIn("signal memory only", self.header)

    def test_capacity_and_controls_are_declared_in_samples(self):
        for token in (
            "max_delay_samples",
            '"delay_i"',
            '"delay_q"',
            '"delays"',
            '"feedback"',
            '"wet"',
            '"dry"',
            '"mix"',
            '"headroom"',
            '"interpolation"',
            '"mute"',
            '"reset"',
            '"clear"',
        ):
            self.assertIn(token, self.wrapper)
        self.assertIn("nearest|linear", self.wrapper)
        self.assertIn("minimum_delay_samples", self.wrapper)
        self.assertIn("maximum_feedback_magnitude", self.wrapper)

    def test_controls_are_applied_only_at_vector_boundaries(self):
        self.assertIn("while (commands_.pop(command))", self.wrapper)
        self.assertLess(
            self.wrapper.index("while (commands_.pop(command))"),
            self.wrapper.index("memory_.process_block("),
        )
        self.assertIn("std::array<Value, Capacity>", self.wrapper)
        self.assertIn("std::atomic<std::size_t>", self.wrapper)
        self.assertNotIn("std::mutex", self.wrapper)

    def test_rejection_status_leaves_audio_thread_via_qelem(self):
        self.assertIn("rejected_nonfinite_samples", self.wrapper)
        self.assertIn("qelem_set(object->status_qelem)", self.wrapper)
        self.assertIn("qmw_memory_drain_status", self.wrapper)
        self.assertIn("pending_rejected_samples_", self.wrapper)

    def test_object_has_no_quantum_event_or_resonator_authority(self):
        for forbidden in (
            '#include "qmw/state.hpp"',
            '#include "qmw/revisioned_state.hpp"',
            '#include "qmw/excite.hpp"',
            '#include "qmw/resonator.hpp"',
            '"event"',
            "rho_",
            "frequency_hz",
            "pole_radius",
        ):
            self.assertNotIn(forbidden, self.wrapper)


if __name__ == "__main__":
    unittest.main()
