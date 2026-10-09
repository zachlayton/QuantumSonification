"""Dedicated atomic OSC excitation frames. No writes to density-field routes."""
from __future__ import annotations

import math
import socket
import struct
from .modal import ModalExcitationFrame

PREFIX = "/qmw/yang_mills/v1"


def frame_messages(frame: ModalExcitationFrame, revision: int) -> list[tuple[str, list]]:
    if isinstance(revision, bool) or not isinstance(revision, int) or not 0 <= revision < 2**31:
        raise ValueError("revision must be a nonnegative OSC int32")
    field = frame.field
    return [
        (f"{PREFIX}/begin", [revision, frame.time, 16]),
        (f"{PREFIX}/magnitude", [revision, *frame.magnitudes.tolist()]),
        (f"{PREFIX}/speed", [revision, *frame.speeds.tolist()]),
        (f"{PREFIX}/diagnostics", [revision, field.total_energy,
            field.relative_energy_drift, field.gauss_error,
            field.unitarity_error, field.determinant_error]),
        (f"{PREFIX}/end", [revision]),
    ]


def _string(value: str) -> bytes:
    raw = value.encode("utf-8") + b"\0"
    return raw + b"\0" * (-len(raw) % 4)


def encode_message(address: str, values: list) -> bytes:
    tags, payload = ",", b""
    for value in values:
        if isinstance(value, int):
            tags += "i"
            payload += struct.pack(">i", value)
        else:
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("OSC values must be finite")
            tags += "f"
            payload += struct.pack(">f", number)
    return _string(address) + _string(tags) + payload


def encode_bundle(messages: list[tuple[str, list]]) -> bytes:
    result = b"#bundle\0" + struct.pack(">Q", 1)  # immediate
    for address, values in messages:
        message = encode_message(address, values)
        result += struct.pack(">i", len(message)) + message
    if len(result) > 1400:
        raise ValueError("excitation bundle exceeds the bounded UDP payload")
    return result


class UDPClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 7416) -> None:
        self.destination = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def publish(self, frame: ModalExcitationFrame, revision: int) -> None:
        self.socket.sendto(encode_bundle(frame_messages(frame, revision)), self.destination)

    def close(self) -> None:
        self.socket.close()
