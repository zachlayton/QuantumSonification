"""Minimal stdlib OSC 1.0 UDP client for streaming modal data to Sonic Pi."""

from __future__ import annotations

import socket
import struct
from typing import Iterable, Union

OSCArgument = Union[bool, int, float, str]


def _osc_string(value: str) -> bytes:
    encoded = value.encode("utf-8") + b"\x00"
    return encoded + b"\x00" * ((-len(encoded)) % 4)


def encode_osc_message(address: str, arguments: Iterable[OSCArgument]) -> bytes:
    if not address.startswith("/"):
        raise ValueError("OSC address must start with '/'")
    tags = [","]
    payload = []
    for argument in arguments:
        if isinstance(argument, bool):
            tags.append("i")
            payload.append(struct.pack(">i", int(argument)))
        elif isinstance(argument, int):
            tags.append("i")
            payload.append(struct.pack(">i", argument))
        elif isinstance(argument, float):
            tags.append("f")
            payload.append(struct.pack(">f", argument))
        elif isinstance(argument, str):
            tags.append("s")
            payload.append(_osc_string(argument))
        else:
            raise TypeError(f"Unsupported OSC argument: {type(argument).__name__}")
    return _osc_string(address) + _osc_string("".join(tags)) + b"".join(payload)


class SonicPiOSCClient:
    """Sends UDP OSC messages to a Sonic Pi instance's OSC-in server.

    Sonic Pi listens for incoming OSC cues on port 4560 by default once
    "Enable OSC Server" is turned on in its IO preferences; a live_loop can
    then `sync` to any address this client sends.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 4560) -> None:
        self.host = host
        self.port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, address: str, arguments: Iterable[OSCArgument] = ()) -> None:
        self._socket.sendto(
            encode_osc_message(address, list(arguments)), (self.host, self.port)
        )

    def close(self) -> None:
        self._socket.close()

    def __enter__(self) -> "SonicPiOSCClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
