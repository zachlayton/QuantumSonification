"""Atomic low-dimensional OSC publication of synchronized GPE FieldFrames."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from qmw.gpe.field_frame import FieldFrame

from .gpe_osc import OSCClient


class GPEFieldFrameOSCAdapter:
    """Publish observables from one FieldFrame without sending the full field."""

    ROOT = "/qmw/gpe/field_frame"
    SCHEMA = "qmw.gpe.field_frame.osc.v2"

    def __init__(self, clients: Iterable[OSCClient] = (), *, mode_count: int = 16) -> None:
        if int(mode_count) != mode_count or mode_count < 1:
            raise ValueError("mode_count must be a positive integer.")
        self.clients = tuple(client for client in clients if client is not None)
        self.mode_count = int(mode_count)
        self.revision = 0

    @classmethod
    def from_udp(cls, host: str = "127.0.0.1", port: int = 17864, *, mode_count: int = 16) -> "GPEFieldFrameOSCAdapter":
        """Create an adapter that emits atomic FieldFrame summaries over UDP."""

        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),), mode_count=mode_count)

    def _mode_indices(self, frame: FieldFrame) -> np.ndarray:
        squared_wavenumber = sum(axis**2 for axis in frame.mode_wavenumbers)
        return np.argsort(squared_wavenumber.ravel(), kind="stable")[: min(self.mode_count, frame.mode_power.size)]

    def messages(self, frame: FieldFrame, *, phase: float | None = None) -> list[tuple[str, list[Any]]]:
        """Return an ordered OSC transaction for one complete physical frame."""

        revision = self.revision
        messages: list[tuple[str, list[Any]]] = [
            (f"{self.ROOT}/begin", [revision, frame.time, self.SCHEMA]),
            (f"{self.ROOT}/norm", [revision, frame.norm]),
            (f"{self.ROOT}/energy", [revision, frame.total_energy]),
            (f"{self.ROOT}/parseval_error", [revision, frame.parseval_error]),
            (f"{self.ROOT}/reconstruction_error", [revision, frame.reconstruction_error]),
        ]
        if phase is not None:
            phase_value = float(phase)
            if not np.isfinite(phase_value):
                raise ValueError("phase must be finite when supplied with a FieldFrame OSC transaction.")
            messages.append((f"{self.ROOT}/phase", [revision, phase_value]))
        if frame.flow.continuity_linf is not None:
            messages.append((f"{self.ROOT}/continuity_linf", [revision, frame.flow.continuity_linf]))
        for index, (population, flux) in enumerate(zip(frame.region_population, frame.region_flux)):
            messages.append((f"{self.ROOT}/region/{index}", [revision, float(population), float(flux)]))
        flat_power = frame.mode_power.ravel()
        flat_phase = frame.mode_phase.ravel()
        flat_velocity = frame.mode_phase_velocity.ravel()
        flat_wavenumbers = [axis.ravel() for axis in frame.mode_wavenumbers]
        for lane, index in enumerate(self._mode_indices(frame)):
            messages.append((
                f"{self.ROOT}/mode/{lane}",
                [revision, int(index), float(flat_power[index]), float(flat_phase[index]), float(flat_velocity[index]),
                 *(float(axis[index]) for axis in flat_wavenumbers)],
            ))
        if frame.geometry_modes is not None:
            geometry = frame.geometry_modes
            messages.append((
                f"{self.ROOT}/geometry_mode_summary",
                [revision, geometry.modal_probability, geometry.unprojected_probability, geometry.reconstruction_error],
            ))
            for lane in range(min(self.mode_count, geometry.power.size)):
                eigenvalue = float("nan") if geometry.eigenvalues is None else float(geometry.eigenvalues[lane])
                messages.append((
                    f"{self.ROOT}/geometry_mode/{lane}",
                    [revision, lane, eigenvalue, float(geometry.power[lane]), float(geometry.phase[lane]),
                     float(geometry.phase_velocity[lane])],
                ))
        messages.append((f"{self.ROOT}/end", [revision]))
        return messages

    def publish(self, frame: FieldFrame, *, phase: float | None = None) -> int:
        """Publish one atomic transaction and return its revision."""

        revision = self.revision
        for address, payload in self.messages(frame, phase=phase):
            for client in self.clients:
                client.send_message(address, payload)
        self.revision += 1
        return revision


__all__ = ["GPEFieldFrameOSCAdapter"]
