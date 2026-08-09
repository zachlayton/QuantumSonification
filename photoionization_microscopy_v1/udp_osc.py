"""Small standard-library OSC 1.0 UDP client for QMW local streams."""

from __future__ import annotations

import socket
import struct
from typing import Any


def _osc_string(value: str) -> bytes:
    encoded = value.encode("utf-8") + b"\x00"
    return encoded + b"\x00" * ((-len(encoded)) % 4)


def encode_osc_message(address: str, value: Any) -> bytes:
    if not address.startswith("/"):
        raise ValueError("OSC address must start with '/'")
    arguments = value if isinstance(value, (list, tuple)) else [value]
    tags = [","]
    payload = []
    for argument in arguments:
        if isinstance(argument, str):
            tags.append("s")
            payload.append(_osc_string(argument))
        elif isinstance(argument, bool):
            tags.append("i")
            payload.append(struct.pack(">i", int(argument)))
        elif isinstance(argument, int):
            tags.append("i")
            payload.append(struct.pack(">i", argument))
        elif isinstance(argument, float):
            tags.append("f")
            payload.append(struct.pack(">f", argument))
        else:
            raise TypeError(f"Unsupported OSC argument: {type(argument).__name__}")
    return _osc_string(address) + _osc_string("".join(tags)) + b"".join(payload)


class UDPOSCClient:
    def __init__(self, host: str, port: int) -> None:
        self.target = (host, int(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, address: str, value: Any) -> None:
        self.socket.sendto(encode_osc_message(address, value), self.target)

    def close(self) -> None:
        self.socket.close()
