from __future__ import annotations

from typing import Any

from qmw.core.state_bus import StateBus
from qmw.core.state_frame import QuantumStateFrame
from qmw.projectors.granular import (
    GranularControl,
    QuantumGranularProjector,
)


class GranularOSCPublisher:
    """Publish live QMW granular controls from StateBus ticks."""

    def __init__(
        self,
        *,
        projector: QuantumGranularProjector | None = None,
        host: str = "127.0.0.1",
        port: int = 7405,
        address: str = "/qmw/grain",
        client: Any | None = None,
    ) -> None:
        self.projector = projector or QuantumGranularProjector()
        self.address = str(address)
        self.last_control: GranularControl | None = None

        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(str(host), int(port))
        self.client = client

    def publish_state(self, frame: QuantumStateFrame) -> GranularControl:
        control = self.projector.project_state(frame)
        self.last_control = control
        self.client.send_message(
            self.address,
            [
                control.index,
                control.time,
                control.position,
                control.duration_ms,
                control.rate,
                control.amplitude,
                control.pan,
                control.density_hz,
            ],
        )
        return control

    def close(self) -> None:
        sock = getattr(self.client, "_sock", None)
        if sock is not None:
            sock.close()


class LiveGranularBridge:
    """Subscribe a granular OSC publisher to a QMW StateBus."""

    def __init__(
        self,
        state_bus: StateBus,
        publisher: GranularOSCPublisher,
    ) -> None:
        self.state_bus = state_bus
        self.publisher = publisher
        self._callback = publisher.publish_state
        self.state_bus.subscribe(self._callback)

    @property
    def last_control(self) -> GranularControl | None:
        return self.publisher.last_control

    def close(self) -> None:
        self.state_bus.unsubscribe(self._callback)
        self.publisher.close()
