"""Optional OSC publication for QMW temporal descriptors.

The existing population/density-matrix server remains authoritative for
`rho_real` and `rho_imag`.  This adapter publishes clock, protocol, Kairos, and
Aion descriptors on the established QMW output port 7400.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping

try:
    from .qmw_temporal_core16_v1 import ClockFrame
except ImportError:  # pragma: no cover
    from qmw_temporal_core16_v1 import ClockFrame


@dataclass(frozen=True)
class OSCMessage:
    address: str
    arguments: tuple[Any, ...]


def _number(value: Any) -> float | int:
    if isinstance(value, Fraction):
        return float(value)
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return float(value)


def frame_messages(frame: ClockFrame) -> tuple[OSCMessage, ...]:
    messages: list[OSCMessage] = [
        OSCMessage("/qmw/time/revision", (int(frame.revision),)),
        OSCMessage("/qmw/time/protocol", (str(frame.protocol),)),
        OSCMessage("/qmw/time/chronos/tick", (int(frame.tick),)),
        OSCMessage("/qmw/time/chronos/sim_time", (float(frame.simulation_time),)),
    ]

    basis = frame.clock.get("basis", {})
    if isinstance(basis, Mapping):
        for key in ("index", "page", "cycle"):
            if key in basis:
                messages.append(
                    OSCMessage(f"/qmw/time/chronos/{key}", (int(basis[key]),))
                )
        if "phase_radians" in basis:
            messages.append(
                OSCMessage(
                    "/qmw/time/chronos/phase",
                    (float(basis["phase_radians"]),),
                )
            )

    lfsr = frame.clock.get("lfsr")
    if isinstance(lfsr, Mapping):
        for key in ("state", "output_bit", "orbit_index", "decimation"):
            if key in lfsr and lfsr[key] is not None:
                messages.append(
                    OSCMessage(f"/qmw/time/lfsr/{key}", (int(lfsr[key]),))
                )
        if lfsr.get("phase_radians") is not None:
            messages.append(
                OSCMessage(
                    "/qmw/time/lfsr/phase",
                    (float(lfsr["phase_radians"]),),
                )
            )
        bits = lfsr.get("bits_q0_first")
        if bits is not None:
            messages.append(
                OSCMessage(
                    "/qmw/time/lfsr/bits",
                    tuple(int(bit) for bit in bits),
                )
            )

    spqt = frame.clock.get("spqt")
    if isinstance(spqt, Mapping):
        if "macrocycle_position" in spqt:
            messages.append(
                OSCMessage(
                    "/qmw/time/spqt/macrocycle_position",
                    (int(spqt["macrocycle_position"]),),
                )
            )
        if "macrocycle_length" in spqt:
            messages.append(
                OSCMessage(
                    "/qmw/time/spqt/macrocycle_length",
                    (int(spqt["macrocycle_length"]),),
                )
            )
        for ratio in spqt.get("ratios", ()):
            if not isinstance(ratio, Mapping):
                continue
            label = str(ratio.get("label", "unnamed")).replace(":", "_")
            base = f"/qmw/time/spqt/{label}"
            messages.extend(
                [
                    OSCMessage(
                        f"{base}/ratio",
                        (int(ratio["p"]), int(ratio["q"])),
                    ),
                    OSCMessage(
                        f"{base}/position",
                        (int(ratio["position"]),),
                    ),
                    OSCMessage(
                        f"{base}/phase",
                        (float(ratio["phase_radians"]),),
                    ),
                    OSCMessage(
                        f"{base}/phasor",
                        (float(ratio["cosine"]), float(ratio["sine"])),
                    ),
                ]
            )

    messages.append(OSCMessage("/qmw/time/kairos/count", (len(frame.events),)))
    for event in frame.events:
        messages.append(
            OSCMessage(
                "/qmw/time/kairos/event",
                (
                    str(event.get("kind", "event")),
                    float(event.get("value", 0.0)),
                    float(event.get("threshold", 0.0)),
                ),
            )
        )
    return tuple(messages)


def aion_messages(summary: Mapping[str, Any]) -> tuple[OSCMessage, ...]:
    keys = (
        "target_frequency",
        "target_bin_frequency",
        "target_amplitude",
        "dominant_frequency",
        "dominant_amplitude",
        "locking_error",
        "peak_to_background",
        "samples",
    )
    messages = [
        OSCMessage("/qmw/time/aion/protocol", (str(summary.get("protocol", "")),))
    ]
    for key in keys:
        if key in summary:
            messages.append(
                OSCMessage(f"/qmw/time/aion/{key}", (_number(summary[key]),))
            )
    messages.append(
        OSCMessage(
            "/qmw/time/aion/establishes_time_crystal",
            (int(bool(summary.get("establishes_time_crystal", False))),),
        )
    )
    return tuple(messages)


class TemporalOSCPublisher:
    """Thin optional python-osc sender; pure message generation is testable."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7400):
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "TemporalOSCPublisher requires the optional 'python-osc' package"
            ) from exc
        self.host = str(host)
        self.port = int(port)
        self._client = SimpleUDPClient(self.host, self.port)

    def send_messages(self, messages: Iterable[OSCMessage]) -> None:
        for message in messages:
            arguments: Any
            if len(message.arguments) == 1:
                arguments = message.arguments[0]
            else:
                arguments = list(message.arguments)
            self._client.send_message(message.address, arguments)

    def publish_frame(self, frame: ClockFrame) -> None:
        self.send_messages(frame_messages(frame))

    def publish_aion(self, summary: Mapping[str, Any]) -> None:
        self.send_messages(aion_messages(summary))

