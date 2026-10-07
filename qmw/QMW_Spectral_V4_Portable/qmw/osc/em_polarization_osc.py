"""Transactional OSC publication of authoritative polarization frames."""

from __future__ import annotations

import math
from threading import Thread
from typing import Any, Callable, Iterable, Protocol

import numpy as np

from qmw.electromagnetic.polarization_state import PolarizationFrame
from qmw.electromagnetic.stokes import STOKES_S3_CONVENTION


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


class EMPolarizationOSCAdapter:
    """Publish one frame between revisioned begin/end markers.

    Jones and density matrices retain separate real and imaginary rails.  OSC
    consumers therefore receive the scientific state, not a flattened musical
    mapping.  Audio and visualization can subscribe to the same frame id.
    """

    PREFIX = "/qmw/em/polarization/v1"

    def __init__(self, clients: Iterable[OSCClient] = ()) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.frame_id = 0

    @classmethod
    def from_udp(cls, host: str = "127.0.0.1", port: int = 17720):
        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def _send(self, suffix: str, value: Any) -> None:
        address = f"{self.PREFIX}/{suffix}"
        for client in self.clients:
            client.send_message(address, value)

    def messages(self, frame: PolarizationFrame) -> list[tuple[str, Any]]:
        density = frame.density.matrix.reshape(-1)
        begin = [self.frame_id, frame.time]
        return [
            ("begin", begin),
            (
                "state",
                [
                    self.frame_id,
                    frame.time,
                    frame.z,
                    frame.carrier_phase,
                    frame.relative_phase,
                    frame.energy_proxy,
                    frame.poincare.polarization_kind,
                    frame.poincare.rotation_direction,
                ],
            ),
            ("jones_real", [self.frame_id, frame.jones.ex.real, frame.jones.ey.real]),
            ("jones_imag", [self.frame_id, frame.jones.ex.imag, frame.jones.ey.imag]),
            ("field_e", [self.frame_id, *frame.electric_field.tolist()]),
            ("field_b", [self.frame_id, *frame.magnetic_field.tolist()]),
            ("stokes", [self.frame_id, *frame.stokes.as_tuple()]),
            ("stokes_convention", [self.frame_id, STOKES_S3_CONVENTION]),
            ("poincare", [self.frame_id, *frame.poincare.vector()]),
            (
                "pauli",
                [self.frame_id, *frame.density.pauli_expectations],
            ),
            ("density_real", [self.frame_id, *np.real(density).tolist()]),
            ("density_imag", [self.frame_id, *np.imag(density).tolist()]),
            ("end", [self.frame_id, len(density)]),
        ]

    def publish(self, frame: PolarizationFrame) -> int:
        published_id = self.frame_id
        for suffix, value in self.messages(frame):
            self._send(suffix, value)
        self.frame_id += 1
        return published_id


class EMPolarizationOSCControlServer:
    """Receive atomic Jones-parameter controls without owning the physics.

    The callback is invoked only after all three values have been validated.
    A consumer therefore never sees an intermediate amplitude/phase state.
    ``pythonosc`` remains a runtime-only dependency.
    """

    CONTROL_ADDRESS = "/qmw/em/polarization/v1/control/state"

    def __init__(
        self,
        update_state: Callable[[float, float, float], None],
        *,
        host: str = "127.0.0.1",
        port: int = 17721,
    ) -> None:
        self.update_state = update_state
        self.host = str(host)
        self.port = int(port)
        self.last_error: str | None = None
        self._server: Any = None
        self._thread: Thread | None = None

    def handle_state(self, _address: str, *arguments: Any) -> bool:
        try:
            if len(arguments) != 3:
                raise ValueError("control/state requires amplitude_x amplitude_y delta")
            amplitude_x, amplitude_y, relative_phase = (
                float(value) for value in arguments
            )
            if not all(
                math.isfinite(value)
                for value in (amplitude_x, amplitude_y, relative_phase)
            ):
                raise ValueError("control/state values must be finite")
            if amplitude_x < 0.0 or amplitude_y < 0.0:
                raise ValueError("Jones amplitudes cannot be negative")
            if amplitude_x == 0.0 and amplitude_y == 0.0:
                raise ValueError("both Jones amplitudes cannot be zero")
            self.update_state(amplitude_x, amplitude_y, relative_phase)
            self.last_error = None
            return True
        except (TypeError, ValueError) as error:
            self.last_error = str(error)
            return False

    def start(self) -> None:
        if self._server is not None:
            return
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        dispatcher = Dispatcher()

        def dispatch_state(address: str, *arguments: Any) -> None:
            # python-osc treats a handler return value as a reply payload.
            # Validation remains observable through handle_state/last_error,
            # but the live control route is intentionally one-way; the next
            # complete authoritative state frame is its acknowledgement.
            self.handle_state(address, *arguments)

        dispatcher.map(self.CONTROL_ADDRESS, dispatch_state)
        self._server = ThreadingOSCUDPServer((self.host, self.port), dispatcher)
        self._thread = Thread(
            target=self._server.serve_forever,
            name="qmw-em-polarization-osc-control",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None


__all__ = [
    "EMPolarizationOSCAdapter",
    "EMPolarizationOSCControlServer",
    "OSCClient",
]
