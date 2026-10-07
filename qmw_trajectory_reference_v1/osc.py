"""Atomic, bounded OSC publication for granular trajectory controls."""

from __future__ import annotations

from time import monotonic, sleep
from typing import Any, Iterable, Protocol

import numpy as np

from .granular import GrainControlTrajectory
from .xy import QuantumTrajectory


OSC_ROOT = "/qmw/trajectory_grain/v1"
OSC_SCHEMA = "qmw.trajectory_grain.osc.v1"
OSC_PORT = 17905


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


def select_indices(time: np.ndarray, *, maximum_hz: float) -> np.ndarray:
    """Retain source frames without creating interpolated quantum data."""
    if not np.isfinite(float(maximum_hz)) or maximum_hz <= 0.0:
        raise ValueError("maximum_hz must be finite and positive.")
    values = np.asarray(time, dtype=float)
    selected = [0]
    interval = 1.0 / float(maximum_hz)
    last_time = float(values[0])
    for index, current in enumerate(values[1:], start=1):
        if current - last_time >= interval - 1.0e-12:
            selected.append(index)
            last_time = float(current)
    if selected[-1] != values.size - 1:
        selected.append(values.size - 1)
    return np.asarray(selected, dtype=int)


class TrajectoryGrainOSCPublisher:
    """Send current control observations as one finite OSC transaction.

    The default 60 Hz limit protects the receiver from a 2048-message burst.
    No messages are queued and no live QMW state is modified.
    """

    def __init__(self, clients: Iterable[OSCClient] = (), *, maximum_hz: float = 60.0) -> None:
        clients_tuple = tuple(client for client in clients if client is not None)
        if any(not hasattr(client, "send_message") for client in clients_tuple):
            raise TypeError("every OSC client must provide send_message(address, payload).")
        if not np.isfinite(float(maximum_hz)) or maximum_hz <= 0.0:
            raise ValueError("maximum_hz must be finite and positive.")
        self.clients = clients_tuple
        self.maximum_hz = float(maximum_hz)

    @classmethod
    def from_udp(
        cls,
        host: str = "127.0.0.1",
        port: int = OSC_PORT,
        **kwargs: Any,
    ) -> "TrajectoryGrainOSCPublisher":
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:  # pragma: no cover - depends on deployment
            raise RuntimeError("python-osc is required only for live UDP publication.") from exc
        return cls((SimpleUDPClient(str(host), int(port)),), **kwargs)

    def messages(
        self,
        trajectory: QuantumTrajectory,
        controls: GrainControlTrajectory,
        *,
        revision: int = 0,
    ) -> list[tuple[str, list[Any]]]:
        if not isinstance(trajectory, QuantumTrajectory) or not isinstance(controls, GrainControlTrajectory):
            raise TypeError("trajectory and controls must have their declared types.")
        if trajectory.samples != controls.samples or not np.array_equal(trajectory.time, controls.time):
            raise ValueError("trajectory and controls must share the identical time base.")
        if int(revision) != revision or revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        retained = select_indices(trajectory.time, maximum_hz=self.maximum_hz)
        result: list[tuple[str, list[Any]]] = [
            (f"{OSC_ROOT}/begin", [int(revision), OSC_SCHEMA, int(trajectory.samples), int(retained.size), float(self.maximum_hz)]),
        ]
        for index in retained:
            result.append((f"{OSC_ROOT}/frame", [
                int(revision), int(index), float(trajectory.time[index]),
                *[float(value) for value in trajectory.site_populations[index]],
                *[float(value) for value in trajectory.edge_current_left_to_right[index]],
            ]))
            result.append((f"{OSC_ROOT}/grain", [
                int(revision), int(index), float(controls.time[index]), float(controls.position[index]),
                float(controls.duration_ms[index]), float(controls.rate[index]), float(controls.amplitude[index]),
                float(controls.pan[index]), float(controls.density_hz[index]),
            ]))
        result.append((f"{OSC_ROOT}/end", [int(revision)]))
        return result

    def close(self) -> None:
        """Release UDP resources when the publisher created them.

        Generic recording clients normally have no close method.  python-osc
        clients currently retain their datagram socket as ``_sock``.
        """
        for client in self.clients:
            closer = getattr(client, "close", None)
            if callable(closer):
                closer()
                continue
            socket = getattr(client, "_sock", None)
            socket_closer = getattr(socket, "close", None)
            if callable(socket_closer):
                socket_closer()

    def publish(
        self,
        trajectory: QuantumTrajectory,
        controls: GrainControlTrajectory,
        *,
        revision: int = 0,
        speed: float = 1.0,
    ) -> int:
        """Publish controls in trajectory order; ``speed`` scales wall-clock time."""
        if not np.isfinite(float(speed)) or speed <= 0.0:
            raise ValueError("speed must be finite and positive.")
        messages = self.messages(trajectory, controls, revision=revision)
        start = monotonic()
        source_start = float(trajectory.time[0])
        for address, payload in messages:
            if address.endswith("/grain"):
                source_time = float(payload[2])
                target = (source_time - source_start) / float(speed)
                remaining = target - (monotonic() - start)
                if remaining > 0.0:
                    sleep(remaining)
            for client in self.clients:
                client.send_message(address, payload)
        return len(messages)
