"""UDP OSC client that treats transient send-buffer pressure as packet loss."""

from __future__ import annotations

import errno
import socket

from pythonosc.udp_client import SimpleUDPClient


_TRANSIENT_SEND_ERRORS = {
    errno.EAGAIN,
    errno.EWOULDBLOCK,
    errno.ENOBUFS,
}


class ResilientSimpleUDPClient(SimpleUDPClient):
    """Keep a real-time OSC producer alive when a UDP datagram must be dropped."""

    def __init__(self, *args, send_buffer_bytes: int = 1_048_576, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropped_packets = 0
        try:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buffer_bytes)
        except OSError:
            # The platform may cap or reject the requested buffer size.
            pass

    def send(self, content) -> None:
        try:
            super().send(content)
        except OSError as exc:
            if exc.errno not in _TRANSIENT_SEND_ERRORS:
                raise
            self.dropped_packets += 1
