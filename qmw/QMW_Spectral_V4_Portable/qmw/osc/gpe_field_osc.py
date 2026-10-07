"""Revisioned full-complex-field OSC transport for visualization only.

The normal GPE OSC adapter deliberately sends scalar observables. This
separate channel transports the complete field in bounded chunks so visualizers
can reconstruct it without asking audio receivers to accept large packets.
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from qmw.osc.gpe_osc import OSCClient
from qmw.qmw_gpe import GPEState


class GPEFieldOSCAdapter:
    """Publish a complete ``psi`` frame as atomic real/imaginary chunks."""

    ROOT = "/qmw/gpe/field"
    SCHEMA = "qmw.gpe.field.osc.v1"

    def __init__(self, clients: Iterable[OSCClient] = (), *, chunk_size: int = 128) -> None:
        if int(chunk_size) < 1:
            raise ValueError("chunk_size must be positive.")
        self.clients = tuple(client for client in clients if client is not None)
        self.chunk_size = int(chunk_size)
        self.revision = 0

    @classmethod
    def from_udp(cls, host: str = "127.0.0.1", port: int = 17865, **kwargs: Any) -> "GPEFieldOSCAdapter":
        """Create a visualization publisher; import ``pythonosc`` only at runtime."""
        from pythonosc.udp_client import SimpleUDPClient
        return cls((SimpleUDPClient(host, int(port)),), **kwargs)

    def messages(self, state: GPEState) -> list[tuple[str, list[Any]]]:
        revision = self.revision
        flat = np.ravel(state.psi)
        chunks = int(np.ceil(flat.size / self.chunk_size))
        messages: list[tuple[str, list[Any]]] = [
            (f"{self.ROOT}/frame/begin", [revision, float(state.time), self.SCHEMA]),
            (f"{self.ROOT}/shape", [revision, *state.psi.shape]),
            (f"{self.ROOT}/chunks", [revision, chunks, self.chunk_size]),
        ]
        for index, start in enumerate(range(0, flat.size, self.chunk_size)):
            segment = flat[start:start + self.chunk_size]
            messages.extend([
                (f"{self.ROOT}/psi/real", [revision, index, *np.real(segment).tolist()]),
                (f"{self.ROOT}/psi/imag", [revision, index, *np.imag(segment).tolist()]),
            ])
        messages.append((f"{self.ROOT}/frame/end", [revision]))
        return messages

    def publish(self, state: GPEState) -> int:
        revision = self.revision
        for address, payload in self.messages(state):
            for client in self.clients:
                client.send_message(address, payload)
        self.revision += 1
        return revision


def reconstruct_gpe_field(messages: Iterable[tuple[str, list[Any]]]) -> tuple[int, float, np.ndarray]:
    """Reconstruct one complete field transport frame; reject partial frames."""
    revision: int | None = None
    time: float | None = None
    shape: tuple[int, ...] | None = None
    chunks: int | None = None
    real: dict[int, list[float]] = {}
    imag: dict[int, list[float]] = {}
    ended = False
    for address, payload in messages:
        if address.endswith("/frame/begin"):
            revision, time = int(payload[0]), float(payload[1])
        elif address.endswith("/shape"):
            shape = tuple(int(value) for value in payload[1:])
        elif address.endswith("/chunks"):
            chunks = int(payload[1])
        elif address.endswith("/psi/real"):
            real[int(payload[1])] = [float(value) for value in payload[2:]]
        elif address.endswith("/psi/imag"):
            imag[int(payload[1])] = [float(value) for value in payload[2:]]
        elif address.endswith("/frame/end"):
            ended = revision is not None and int(payload[0]) == revision
    if revision is None or time is None or shape is None or chunks is None or not ended:
        raise ValueError("a complete begin/shape/chunks/end field frame is required.")
    if set(real) != set(range(chunks)) or set(imag) != set(range(chunks)):
        raise ValueError("field frame is missing real or imaginary chunks.")
    values = np.concatenate([np.asarray(real[i]) + 1j * np.asarray(imag[i]) for i in range(chunks)])
    if values.size != int(np.prod(shape)):
        raise ValueError("field chunks do not match declared shape.")
    return revision, time, values.reshape(shape)


__all__ = ["GPEFieldOSCAdapter", "reconstruct_gpe_field"]
