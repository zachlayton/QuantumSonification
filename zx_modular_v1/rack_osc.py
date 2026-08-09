"""Control-rate PennyLane state descriptors for VCV Rack via OSCelot."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Collection, Sequence

import numpy as np


@dataclass(frozen=True)
class OSCelotControl:
    control_id: int
    label: str
    value: float
    kind: str = "fader"

    def __post_init__(self) -> None:
        if int(self.control_id) < 1:
            raise ValueError("OSCelot control ids begin at one")
        if self.kind not in {"fader", "button"}:
            raise ValueError("OSCelot controls must be faders or buttons")
        if not math.isfinite(float(self.value)):
            raise ValueError("OSCelot control values must be finite")
        if not 0.0 <= float(self.value) <= 1.0:
            raise ValueError("OSCelot control values must be in 0..1")


@dataclass(frozen=True)
class PennyLaneRackFrame:
    phase_radians: float
    expectation_z0: float
    population_entropy: float
    coherence_l1: float
    dominant_probability: float
    parameter_gradient: float
    controls: tuple[OSCelotControl, ...]

    def osc_messages(
        self,
        *,
        prefix: str = "/qmw/zx",
        control_ids: Collection[int] | None = None,
    ) -> list[tuple[str, list[float]]]:
        base = prefix.rstrip("/")
        selected = None if control_ids is None else {int(value) for value in control_ids}
        return [
            (
                f"{base}/{control.kind}",
                [int(control.control_id), float(control.value)],
            )
            for control in self.controls
            if selected is None or control.control_id in selected
        ]


def _unit_bipolar(value: float) -> float:
    return float(np.clip(0.5 + 0.5 * value, 0.0, 1.0))


def rack_frame_from_state(
    statevector: Sequence[complex],
    *,
    phase_radians: float,
    parameter_gradient: float = 0.0,
) -> PennyLaneRackFrame:
    """Reduce a PennyLane statevector to stable 0..1 OSCelot controls.

    The state is interpreted in PennyLane's declared-wire matrix order, where
    the first wire is the most-significant tensor axis.
    """
    state = np.asarray(statevector, dtype=np.complex128).reshape(-1)
    dimension = len(state)
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("statevector length must be a power of two")
    norm = float(np.linalg.norm(state))
    if not np.isclose(norm, 1.0, atol=1e-9):
        raise ValueError(f"statevector must be normalized; norm is {norm}")
    if not math.isfinite(float(phase_radians)):
        raise ValueError("phase_radians must be finite")
    if not math.isfinite(float(parameter_gradient)):
        raise ValueError("parameter_gradient must be finite")

    probabilities = np.abs(state) ** 2
    half = dimension // 2
    expectation_z0 = float(
        np.sum(probabilities[:half]) - np.sum(probabilities[half:])
    )
    nonzero = probabilities[probabilities > 1e-15]
    entropy = float(
        -np.sum(nonzero * np.log2(nonzero)) / math.log2(dimension)
    )
    coherence = float(
        ((np.sum(np.abs(state)) ** 2) - 1.0) / (dimension - 1)
    )
    dominant = float(np.max(probabilities))
    phase_turn = (float(phase_radians) / (2.0 * math.pi)) % 1.0
    gradient_control = _unit_bipolar(math.tanh(float(parameter_gradient)))

    controls = (
        OSCelotControl(1, "ZX phase · turns", phase_turn),
        OSCelotControl(2, "PennyLane <Z0>", _unit_bipolar(expectation_z0)),
        OSCelotControl(3, "population entropy", float(np.clip(entropy, 0.0, 1.0))),
        OSCelotControl(4, "l1 coherence", float(np.clip(coherence, 0.0, 1.0))),
        OSCelotControl(5, "parameter gradient", gradient_control),
        OSCelotControl(6, "dominant probability", dominant),
    )
    return PennyLaneRackFrame(
        phase_radians=float(phase_radians),
        expectation_z0=expectation_z0,
        population_entropy=entropy,
        coherence_l1=coherence,
        dominant_probability=dominant,
        parameter_gradient=float(parameter_gradient),
        controls=controls,
    )


class OSCelotPublisher:
    """Publish one control-rate frame to an OSCelot receiver in Rack."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7000,
        *,
        prefix: str = "",
    ) -> None:
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:
            raise ModuleNotFoundError("python-osc is required for live Rack output") from exc
        self.client = SimpleUDPClient(str(host), int(port))
        self.prefix = str(prefix)

    def publish(
        self,
        frame: PennyLaneRackFrame,
        *,
        control_ids: Collection[int] | None = None,
    ) -> None:
        for address, arguments in frame.osc_messages(
            prefix=self.prefix,
            control_ids=control_ids,
        ):
            self.client.send_message(address, arguments)
