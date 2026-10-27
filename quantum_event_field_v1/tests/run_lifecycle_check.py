"""Run the real SC addon against an OSC protocol stub (no audio device).

SCSYNTH encodes many command names as integer IDs; translate the two observed
commands to strings so sclang can inspect them. Reply to /sync from the same
UDP port. SynthDefs/audio are checked separately with the real scsynth NRT.

Usage: python tests/run_lifecycle_check.py [path-to-sclang-or-wrapper]
"""
from pathlib import Path
import os
import socket
import struct
import subprocess
import sys
import threading


def osc_string(value: str) -> bytes:
    data = value.encode() + b"\0"
    return data + b"\0" * (-len(data) % 4)


def unpack_string(data: bytes) -> tuple[str, int]:
    end = data.index(b"\0")
    return data[:end].decode(), (end + 4) & ~3


def translate(data: bytes, reply) -> bytes | None:
    if data.startswith(b"#bundle\0"):
        result, offset = bytearray(data[:16]), 16
        while offset < len(data):
            size = struct.unpack_from(">i", data, offset)[0]
            offset += 4
            message = translate(data[offset:offset + size], reply)
            offset += size
            if message:
                result += struct.pack(">i", len(message)) + message
        return bytes(result) if len(result) > 16 else None
    if data[0] == 0:
        command = struct.unpack_from(">i", data)[0]
        name = {9: "/s_new", 11: "/n_free"}.get(command)
        return osc_string(name) + data[4:] if name else None
    name, offset = unpack_string(data)
    if name == "/sync":
        reply(osc_string("/synced") + data[offset:])
    return None


def main() -> int:
    stop = threading.Event()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.settimeout(0.1)

        def serve():
            while not stop.is_set():
                try:
                    data, address = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                packet = translate(data, lambda message: sock.sendto(message, address))
                if packet:
                    sock.sendto(packet, address)

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        env = dict(os.environ, QMW_TEST_PORT=str(sock.getsockname()[1]))
        executable = sys.argv[1] if len(sys.argv) > 1 else "sclang"
        try:
            completed = subprocess.run(
                [executable, "-D", str(Path(__file__).with_name("LifecycleCheck.scd"))],
                env=env, timeout=20, check=False,
            )
            return completed.returncode
        finally:
            stop.set()
            thread.join(timeout=1)


if __name__ == "__main__":
    raise SystemExit(main())
