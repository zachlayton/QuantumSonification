import socket
import unittest
from qmw.io import encode_message, encode_bundle, decode_packet, OscPublisher
from qmw.sound import SonificationPolicy
from tests.test_sound import sound_fixture


class OscTests(unittest.TestCase):
    def test_wire_bytes_types_padding_and_nested_bundle(self):
        message = encode_message("/x", [3, .5, "abc", b"ab"])
        self.assertEqual(message[:16], b"/x\x00\x00,ifsb\x00\x00\x00\x00\x00\x00\x03")
        packet = encode_bundle([encode_bundle([message])])
        self.assertEqual(decode_packet(packet), [("/x", [3, .5, "abc", b"ab"])])
        with self.assertRaises(ValueError):
            decode_packet(packet[:-1])

    def test_real_udp_frame_and_pluck_round_trip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("127.0.0.1", 0))
            receiver.settimeout(2)
            frame = sound_fixture()
            sound = SonificationPolicy().map(frame)
            with OscPublisher(port=receiver.getsockname()[1]) as publisher:
                publisher.publish(sound, frame)
                packet, _ = receiver.recvfrom(65535)
            messages = decode_packet(packet)
            self.assertEqual(messages[0][0], "/qmw/v01/frame")
            self.assertEqual(messages[0][1][0], 7)
            self.assertEqual(messages[0][1][2], "schrodinger_1d")
            voices = [args for address, args in messages if address.endswith("/voice")]
            self.assertEqual(len(voices), 16)
            pluck = [args for address, args in messages if address.endswith("/pluck")][0]
            self.assertEqual(pluck[1], sound.events[0].event_id)
            self.assertEqual(pluck[3:5], [2, -1])
            self.assertAlmostEqual(pluck[5], 330)


if __name__ == "__main__":
    unittest.main()
