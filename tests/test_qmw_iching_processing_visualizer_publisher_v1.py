import pathlib
import re
import unittest

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame, osc_messages
from qmw_iching_processing_visualizer_publisher_v1 import (
    build_and_publish_consultation,
    ConsultationService,
    osc_safe_arguments,
    publish_messages,
    signed_int32,
)


class FakeClient:
    def __init__(self): self.messages = []
    def send_message(self, address, arguments): self.messages.append((address, arguments))


class TestProcessingPublisher(unittest.TestCase):
    def test_processing_king_wen_lookup_is_a_complete_permutation(self):
        sketch = pathlib.Path(__file__).parent / "processing" / "QMW_IChing_Network_Visualizer_v1" / "QMW_IChing_Network_Visualizer_v1.pde"
        source = sketch.read_text(encoding="utf-8")
        body = re.search(r"KING_WEN_BINARY\s*=\s*\{(.*?)\};", source, re.S).group(1)
        binary_by_number = [int(value) for value in re.findall(r"\d+", body)]
        self.assertEqual(len(binary_by_number), 64)
        self.assertEqual(set(binary_by_number), set(range(64)))
        self.assertEqual(binary_by_number[0], 63)   # 1 Qian: all yang
        self.assertEqual(binary_by_number[1], 0)    # 2 Kun: all yin
        self.assertEqual(binary_by_number[28], 18)  # 29 Kan over Kan
        self.assertEqual(binary_by_number[29], 45)  # 30 Li over Li
        self.assertEqual(binary_by_number[63], 42)  # 64 Li over Kan

    def test_processing_ibm_comparison_uses_a_fresh_visible_seed(self):
        sketch = pathlib.Path(__file__).parent / "processing" / "QMW_IChing_Network_Visualizer_v1" / "QMW_IChing_Network_Visualizer_v1.pde"
        source = sketch.read_text(encoding="utf-8")
        request = re.search(
            r"void requestIBMComparison\(\)\s*\{(.*?)\n\}", source, re.S
        ).group(1)
        self.assertIn("System.nanoTime()", request)
        self.assertIn("ibmRequestCounter++", request)
        self.assertIn("request.add(ibmRequestSeed)", request)
        self.assertIn('"seed "+unsignedSeed(ibmActive.seed)', source)

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

    def test_consultation_cast_is_one_atomic_mirrored_frame(self):
        engine, visual = FakeClient(), FakeClient()
        frame, count = build_and_publish_consultation(
            depth=1, clients=[engine, visual], seed=42, revision=109
        )
        self.assertEqual(frame.revision, 109)
        self.assertEqual(count, len(engine.messages))
        self.assertEqual(engine.messages, visual.messages)
        self.assertTrue(engine.messages[0][0].endswith("/begin"))
        self.assertTrue(engine.messages[-1][0].endswith("/end"))
        revisions = {arguments[0] for _address, arguments in engine.messages}
        self.assertEqual(revisions, {109})

    def test_audio_callback_receives_the_same_frozen_frame(self):
        visual = FakeClient(); received = []
        frame, _count = build_and_publish_consultation(
            depth=1, clients=[visual], seed=42, revision=110,
            on_consultation=lambda frozen, laplacian: received.append(
                (frozen, laplacian.copy())
            ),
        )
        self.assertEqual(len(received), 1)
        self.assertIs(received[0][0], frame)
        self.assertEqual(received[0][1].shape, (64, 64))
        self.assertTrue((received[0][1] == received[0][1].conj().T).all())

    def test_service_acknowledges_and_publishes_requested_cast(self):
        visual = FakeClient()
        service = ConsultationService(depth=1, clients=[visual])
        service.handle_request("/qmw/iching/consult/request", 314)
        addresses = [address for address, _arguments in visual.messages]
        self.assertEqual(addresses[0], "/qmw/iching/consult/accepted")
        self.assertIn("/qmw/iching/network/begin", addresses)
        self.assertIn("/qmw/iching/network/end", addresses)
        self.assertEqual(addresses[-1], "/qmw/iching/consult/published")
        self.assertEqual(visual.messages[0][1], [314])


if __name__ == "__main__": unittest.main()
