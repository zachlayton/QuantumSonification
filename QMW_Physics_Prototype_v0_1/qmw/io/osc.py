"""Small OSC 1.0 transport, with one UDP bundle per physical frame."""
from __future__ import annotations
import socket
import struct
from qmw.core.frame import PhysicsFrame, SoundControlFrame


def _string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if b"\0" in encoded:
        raise ValueError("OSC strings cannot contain NUL")
    encoded += b"\0"
    return encoded + b"\0" * ((-len(encoded)) % 4)


def encode_message(address: str, arguments=()) -> bytes:
    if not address.startswith("/"):
        raise ValueError("OSC address must begin with /")
    tags, payloads = [], []
    for argument in arguments:
        if isinstance(argument, (int, bool)):
            tags.append("i")
            payloads.append(struct.pack(">i", int(argument)))
        elif isinstance(argument, float):
            tags.append("f")
            payloads.append(struct.pack(">f", argument))
        elif isinstance(argument, str):
            tags.append("s")
            payloads.append(_string(argument))
        elif isinstance(argument, bytes):
            tags.append("b")
            payloads.append(struct.pack(">i", len(argument)) + argument + b"\0" * ((-len(argument)) % 4))
        else:
            raise TypeError(f"Unsupported OSC argument: {type(argument).__name__}")
    return _string(address) + _string("," + "".join(tags)) + b"".join(payloads)


def encode_bundle(messages: list[bytes], timetag: int = 1) -> bytes:
    return b"#bundle\0" + struct.pack(">Q", timetag) + b"".join(
        struct.pack(">i", len(message)) + message for message in messages)


def _read_string(packet: bytes, offset: int):
    try:
        end = packet.index(b"\0", offset)
    except ValueError as error:
        raise ValueError("Truncated OSC string") from error
    value = packet[offset:end].decode("utf-8")
    next_offset = (end + 4) & ~3
    if next_offset > len(packet):
        raise ValueError("Truncated OSC string padding")
    return value, next_offset


def decode_packet(packet: bytes) -> list[tuple[str, list]]:
    """Decode a message or recursively flatten a bundle for receiver tests."""
    if packet.startswith(b"#bundle\0"):
        if len(packet) < 16:
            raise ValueError("Truncated OSC bundle")
        offset, messages = 16, []
        while offset < len(packet):
            if offset + 4 > len(packet):
                raise ValueError("Truncated OSC bundle element size")
            size = struct.unpack_from(">i", packet, offset)[0]
            offset += 4
            if size <= 0 or offset + size > len(packet):
                raise ValueError("Invalid OSC bundle element size")
            messages.extend(decode_packet(packet[offset:offset+size]))
            offset += size
        return messages
    address, offset = _read_string(packet, 0)
    if not address.startswith("/"):
        raise ValueError("Invalid OSC address")
    tags, offset = _read_string(packet, offset)
    if not tags.startswith(","):
        raise ValueError("OSC type tags missing")
    arguments = []
    for tag in tags[1:]:
        if tag in {"i", "f"}:
            if offset + 4 > len(packet):
                raise ValueError("Truncated OSC numeric argument")
            arguments.append(struct.unpack_from(">" + tag, packet, offset)[0])
            offset += 4
        elif tag == "s":
            argument, offset = _read_string(packet, offset)
            arguments.append(argument)
        elif tag == "b":
            if offset + 4 > len(packet):
                raise ValueError("Truncated OSC blob size")
            size = struct.unpack_from(">i", packet, offset)[0]
            offset += 4
            if size < 0 or offset + size > len(packet):
                raise ValueError("Invalid OSC blob size")
            arguments.append(packet[offset:offset+size])
            offset += size + ((-size) % 4)
        else:
            raise ValueError(f"Unsupported OSC tag: {tag}")
    if offset != len(packet):
        raise ValueError("OSC packet has trailing or truncated padding")
    return [(address, arguments)]


class OscPublisher:
    def __init__(self, host="127.0.0.1", port=17900):
        if not 1 <= port <= 65535:
            raise ValueError("UDP port must lie in [1,65535]")
        self.destination = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def publish(self, sound: SoundControlFrame, physics: PhysicsFrame | None = None):
        sequence = int(sound.sequence)
        messages = [encode_message("/qmw/v01/frame", [sequence, float(sound.t),
                          physics.model_id if physics is not None else "unspecified"])]
        messages.append(encode_message("/qmw/v01/meta", [sequence,
                          physics.provenance if physics is not None else "unspecified",
                          physics.schema_version if physics is not None else "qmw.physics/0.1",
                          sound.mapping_id]))
        for index, (hz, amplitude, decay, phase) in enumerate(zip(
                sound.frequency_hz, sound.amplitude, sound.decay_s, sound.phase)):
            messages.append(encode_message("/qmw/v01/voice", [sequence, index,
                float(hz), float(amplitude), float(decay), float(phase)]))
        for event in sound.events:
            messages.append(encode_message("/qmw/v01/pluck", [sequence, event.event_id,
                float(event.t), -1 if event.region is None else int(event.region),
                -1 if event.mode is None else int(event.mode), float(event.frequency_hz),
                float(event.amplitude), float(event.decay_s), float(event.pan)]))
        packet = encode_bundle(messages)
        if len(packet) > 65507:
            raise ValueError("Frame exceeds the UDP payload limit")
        self.socket.sendto(packet, self.destination)
        return len(packet)

    def close(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
