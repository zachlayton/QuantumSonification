import errno
import unittest

from quantum_oscilloscope.resilient_udp import ResilientSimpleUDPClient


class _Datagram:
    dgram = b"osc"


class _Socket:
    def __init__(self, error):
        self.error = error

    def sendto(self, *_args):
        raise self.error


class ResilientUDPTests(unittest.TestCase):
    def client_with_error(self, error):
        client = ResilientSimpleUDPClient.__new__(ResilientSimpleUDPClient)
        client._sock = _Socket(error)
        client._address = "127.0.0.1"
        client._port = 7400
        client.dropped_packets = 0
        return client

    def test_transient_buffer_pressure_drops_packet(self):
        client = self.client_with_error(BlockingIOError(errno.EAGAIN, "busy"))
        client.send(_Datagram())
        self.assertEqual(client.dropped_packets, 1)

    def test_non_transient_socket_error_is_not_hidden(self):
        client = self.client_with_error(OSError(errno.EHOSTUNREACH, "unreachable"))
        with self.assertRaises(OSError):
            client.send(_Datagram())


if __name__ == "__main__":
    unittest.main()
