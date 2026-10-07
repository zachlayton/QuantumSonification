"""Low-dimensional OSC publication of GPE observables.

The adapter deliberately publishes summaries, regional transport, modal
amplitudes, and vortex topology—not the full complex field.  Field streaming
for visualization is a separate concern and must use its own explicit
transport contract.
"""

from __future__ import annotations

from typing import Any, Iterable, Protocol

import numpy as np

from qmw.gpe.modal_engine import GPEModalFrame
from qmw.gpe.vortices import GPEVortexFrame
from qmw.qmw_gpe import GPEState
from qmw.qmw_probability_flow import FlowFrame2D


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


class GPEOSCAdapter:
    """Publish revisioned, physically declared GPE observables over OSC."""

    ROOT = "/qmw/gpe"
    SCHEMA = "qmw.gpe.observables.osc.v1"

    def __init__(self, clients: Iterable[OSCClient] = ()) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.revision = 0

    @classmethod
    def from_udp(cls, host: str = "127.0.0.1", port: int = 17864) -> "GPEOSCAdapter":
        """Create a UDP publisher; ``pythonosc`` is imported only at runtime."""

        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),))

    def messages(
        self,
        state: GPEState,
        *,
        flow: FlowFrame2D | None = None,
        modal: GPEModalFrame | None = None,
        vortices: GPEVortexFrame | None = None,
    ) -> list[tuple[str, list[Any]]]:
        """Return one complete scalar-observable frame without publishing it."""

        revision = self.revision
        messages: list[tuple[str, list[Any]]] = [
            (f"{self.ROOT}/frame/begin", [revision, state.time, self.SCHEMA]),
            (f"{self.ROOT}/time", [revision, state.time]),
            (f"{self.ROOT}/density/mean", [revision, float(np.mean(state.density))]),
            (f"{self.ROOT}/density/max", [revision, float(np.max(state.density))]),
        ]
        if flow is not None:
            if not np.isclose(flow.time, state.time):
                raise ValueError("flow and GPE state must have the same observation time.")
            velocity = np.divide(
                flow.current, flow.density[None, ...],
                out=np.zeros_like(flow.current), where=flow.density[None, ...] > 1.0e-12,
            )
            speed = np.linalg.norm(velocity, axis=0)
            messages.extend([
                (f"{self.ROOT}/flow/x", [revision, float(np.mean(flow.current[0]))]),
                (f"{self.ROOT}/flow/y", [revision, float(np.mean(flow.current[1]))]),
                (f"{self.ROOT}/flow/speed", [revision, float(np.mean(speed))]),
            ])
            for index, (population, flux) in enumerate(zip(flow.region_population, flow.region_flux)):
                messages.extend([
                    (f"{self.ROOT}/region/{index}/population", [revision, float(population)]),
                    (f"{self.ROOT}/region/{index}/flux", [revision, float(flux)]),
                ])
        if modal is not None:
            if not np.isclose(modal.time, state.time):
                raise ValueError("modal frame and GPE state must have the same observation time.")
            for index, (amplitude, phase) in enumerate(zip(modal.amplitudes, modal.phases)):
                messages.extend([
                    (f"{self.ROOT}/mode/{index}/magnitude", [revision, float(abs(amplitude))]),
                    (f"{self.ROOT}/mode/{index}/phase", [revision, float(phase)]),
                ])
        if vortices is not None:
            messages.append((f"{self.ROOT}/vortex/count", [revision, len(vortices.vortices)]))
            for index, vortex in enumerate(vortices.vortices):
                messages.extend([
                    (f"{self.ROOT}/vortex/{index}/x", [revision, vortex.x]),
                    (f"{self.ROOT}/vortex/{index}/y", [revision, vortex.y]),
                    (f"{self.ROOT}/vortex/{index}/winding", [revision, vortex.winding]),
                ])
        messages.append((f"{self.ROOT}/frame/end", [revision]))
        return messages

    def publish(
        self,
        state: GPEState,
        *,
        flow: FlowFrame2D | None = None,
        modal: GPEModalFrame | None = None,
        vortices: GPEVortexFrame | None = None,
    ) -> int:
        """Publish one complete observables frame and return its revision."""

        published = self.revision
        for address, payload in self.messages(state, flow=flow, modal=modal, vortices=vortices):
            for client in self.clients:
                client.send_message(address, payload)
        self.revision += 1
        return published


__all__ = ["GPEOSCAdapter", "OSCClient"]
