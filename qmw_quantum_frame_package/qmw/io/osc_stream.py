from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import Iterable, Sequence, Union

import numpy as np

OSCArg = Union[int, float, str]


def _pad4(data: bytes) -> bytes:
    return data + (b"\x00" * ((4 - len(data) % 4) % 4))


def _osc_string(s: str) -> bytes:
    return _pad4(s.encode("utf-8") + b"\x00")


def encode_osc_message(address: str, args: Sequence[OSCArg]) -> bytes:
    if not address.startswith("/"):
        raise ValueError("OSC address must begin with '/'")

    tags = ","
    payload = bytearray()

    for arg in args:
        if isinstance(arg, (np.integer, int)) and not isinstance(arg, bool):
            tags += "i"
            payload.extend(struct.pack(">i", int(arg)))
        elif isinstance(arg, (np.floating, float)):
            tags += "f"
            payload.extend(struct.pack(">f", float(arg)))
        elif isinstance(arg, str):
            tags += "s"
            payload.extend(_osc_string(arg))
        else:
            raise TypeError(f"Unsupported OSC type: {type(arg).__name__}")

    return _osc_string(address) + _osc_string(tags) + bytes(payload)


@dataclass
class OSCSender:
    host: str = "127.0.0.1"
    port: int = 7405

    def __post_init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, address: str, *args: OSCArg) -> None:
        packet = encode_osc_message(address, args)
        self._sock.sendto(packet, (self.host, self.port))

    def close(self) -> None:
        self._sock.close()


def stream_quantum_grains(
    frame,
    grain,
    host: str = "127.0.0.1",
    port: int = 7405,
    speed: float = 1.0,
    loop: bool = False,
    send_raw_frame: bool = True,
):
    """
    Stream one QuantumFrame in wall-clock time.

    speed=1 uses the frame's physical/simulation time spacing.
    speed=2 plays the trajectory twice as fast.
    """
    if speed <= 0:
        raise ValueError("speed must be > 0")

    sender = OSCSender(host, port)

    try:
        while True:
            wall0 = time.perf_counter()
            t0 = float(frame.t[0])

            for i, sim_t in enumerate(frame.t):
                target = (float(sim_t) - t0) / speed
                now = time.perf_counter() - wall0
                if target > now:
                    time.sleep(target - now)

                sender.send(
                    "/qmw/grain",
                    int(i),
                    float(sim_t),
                    float(grain.position[i]),
                    float(grain.duration_ms[i]),
                    float(grain.rate[i]),
                    float(grain.amplitude[i]),
                    float(grain.pan[i]),
                    float(grain.density_hz[i]),
                )

                if send_raw_frame:
                    p = frame.observables["site_populations"][i]
                    j = frame.observables["edge_currents"][i]
                    sender.send(
                        "/qmw/frame",
                        int(i),
                        float(sim_t),
                        *[float(x) for x in p],
                        *[float(x) for x in j],
                    )

            sender.send("/qmw/end", int(frame.samples))
            if not loop:
                break
    finally:
        sender.close()
