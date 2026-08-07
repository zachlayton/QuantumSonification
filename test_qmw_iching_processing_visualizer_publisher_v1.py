import unittest

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame, osc_messages
from qmw_iching_processing_visualizer_publisher_v1 import (
    osc_safe_arguments,
    publish_messages,
    signed_int32,
)


class FakeClient:
    def __init__(self): self.messages = []
    def send_message(self, address, arguments): self.messages.append((address, arguments))


class TestProcessingPublisher(unittest.TestCase):
    def test_signed_int32_encoding(self):
        self.assertEqual(signed_int32(0xFFFFFFFF), -1)
        self.assertEqual(signed_int32(0x80000000), -2147483648)
        self.assertEqual(signed_int32(42), 42)

    def test_mirror_is_ordered_and_identical(self):
        frame, rho, *_ = build_control_frame(seed=42, depth=1, revision=108)
        source = list(osc_messages(frame, rho)); engine = FakeClient(); visual = FakeClient()
        count = publish_messages(source, [engine, visual])
        self.assertEqual(count, len(source))
        self.assertEqual(engine.messages, visual.messages)
        self.assertTrue(engine.messages[0][0].endswith("/begin"))
        self.assertTrue(engine.messages[-1][0].endswith("/end"))
        self.assertTrue(all(args[0] == 108 for _address, args in engine.messages))

    def test_oversize_seed_is_osc_safe(self):
        args = osc_safe_arguments([108, 0xFFFFFFFF, 64, 4])
        self.assertEqual(args, [108, -1, 64, 4])


if __name__ == "__main__": unittest.main()
