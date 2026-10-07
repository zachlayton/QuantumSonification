"""Rate-invariant event quantization for directed Hilbert probability current."""

from __future__ import annotations

from dataclasses import dataclass
import math
from threading import RLock, Thread
from typing import Any, Callable

from qmw.bridge.qmw_4_4_frame import QMW44QuantumFrame


CONTROL_ADDRESS = "/qmw/resonant_interaction/v1/control/pluck_threshold"
OMEGA_CONTROL_ADDRESS = "/qmw/resonant_interaction/v1/control/interaction_omega_scale"
PERFORMANCE_RECORD_CONTROL_ADDRESS = "/qmw/resonant_interaction/v1/control/performance-record"
CONTROL_PORT = 17923
MIN_THRESHOLD = 0.005
MAX_THRESHOLD = 0.5
MIN_OMEGA_SCALE = 0.1
MAX_OMEGA_SCALE = 8.0


@dataclass(frozen=True)
class HilbertCurrentPluckV1:
    source: int
    destination: int
    current_magnitude: float
    transported_probability: float
    dominant_pauli: str | None
    dominant_contribution: float
    sequence: int


@dataclass(frozen=True)
class HilbertCurrentPluckFrameV1:
    revision: int
    time: float
    threshold: float
    accumulator_peak_fraction: float
    plucks: tuple[HilbertCurrentPluckV1, ...]
    provenance: str = "hilbert_current_probability_quantum_crossing_v1"


class HilbertCurrentPluckGateV1:
    """Integrate ``|J| dt`` per undirected edge and emit probability quanta.

    Sampling a fixed current trajectory more frequently changes neither the
    accumulated transported probability nor its long-run pluck count. The
    sub-threshold remainder is retained between frames and direction changes.
    """

    def __init__(self, threshold: float = 0.1, *, max_plucks_per_edge: int = 8) -> None:
        if not math.isfinite(float(threshold)) or threshold <= 0.0:
            raise ValueError("threshold must be finite and positive.")
        if int(max_plucks_per_edge) != max_plucks_per_edge or max_plucks_per_edge < 1:
            raise ValueError("max_plucks_per_edge must be a positive integer.")
        self._threshold = float(threshold)
        self.max_plucks_per_edge = int(max_plucks_per_edge)
        self._remainders: dict[tuple[int, int], float] = {}
        self._last_time: float | None = None
        self._lock = RLock()

    @property
    def threshold(self) -> float:
        with self._lock:
            return self._threshold

    @property
    def remainders(self) -> dict[tuple[int, int], float]:
        with self._lock:
            return dict(self._remainders)

    def reset(self) -> None:
        with self._lock:
            self._remainders.clear()
            self._last_time = None

    def set_threshold(self, threshold: float) -> float:
        """Set a new event quantum while preserving each edge's fractional phase."""

        value = float(threshold)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("threshold must be finite and positive.")
        with self._lock:
            ratio = value / self._threshold
            self._remainders = {
                edge: min(remainder * ratio, value * (1.0 - 1.0e-12))
                for edge, remainder in self._remainders.items()
            }
            self._threshold = value
            return value

    def observe(self, frame: QMW44QuantumFrame, dt: float) -> HilbertCurrentPluckFrameV1:
        if not isinstance(frame, QMW44QuantumFrame):
            raise ValueError("frame must be a QMW44QuantumFrame.")
        duration = float(dt)
        if not math.isfinite(duration) or duration <= 0.0:
            raise ValueError("dt must be finite and positive.")
        with self._lock:
            if self._last_time is not None and frame.time <= self._last_time:
                raise ValueError("Hilbert pluck frame time must increase.")
            plucks: list[HilbertCurrentPluckV1] = []
            sequence = 0
            for edge in frame.current_edges:
                key = tuple(sorted((edge.source, edge.destination)))
                total = self._remainders.get(key, 0.0) + edge.magnitude * duration
                count = min(
                    self.max_plucks_per_edge,
                    int((total + 1.0e-15) // self._threshold),
                )
                self._remainders[key] = max(0.0, total - count * self._threshold)
                for _ in range(count):
                    plucks.append(HilbertCurrentPluckV1(
                        source=edge.source,
                        destination=edge.destination,
                        current_magnitude=edge.magnitude,
                        transported_probability=self._threshold,
                        dominant_pauli=edge.dominant_pauli,
                        dominant_contribution=edge.dominant_contribution,
                        sequence=sequence,
                    ))
                    sequence += 1
            peak = max(self._remainders.values(), default=0.0) / self._threshold
            self._last_time = float(frame.time)
            return HilbertCurrentPluckFrameV1(
                revision=frame.revision,
                time=frame.time,
                threshold=self._threshold,
                accumulator_peak_fraction=float(min(max(peak, 0.0), 1.0)),
                plucks=tuple(plucks),
            )


class HilbertPluckOSCControlV1:
    """Receive live probability-quantum changes for one pluck authority.

    SuperCollider is only the controller. Validation and fractional-phase
    preservation remain in Python beside the authoritative accumulator.
    """

    def __init__(
        self,
        gate: HilbertCurrentPluckGateV1,
        *,
        host: str = "127.0.0.1",
        port: int = CONTROL_PORT,
        interaction_omega_setter: Callable[[float], float] | None = None,
        performance_recorder: Any | None = None,
        performance_saved_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        self.gate = gate
        self.interaction_omega_setter = interaction_omega_setter
        self.performance_recorder = performance_recorder
        self.performance_saved_callback = performance_saved_callback
        dispatcher = Dispatcher()
        dispatcher.map(CONTROL_ADDRESS, self._handle_threshold)
        if interaction_omega_setter is not None:
            dispatcher.map(OMEGA_CONTROL_ADDRESS, self._handle_interaction_omega)
        if performance_recorder is not None:
            dispatcher.map(
                PERFORMANCE_RECORD_CONTROL_ADDRESS,
                self._handle_performance_record,
            )
        self.server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
        self.server.daemon_threads = True
        self._thread: Thread | None = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    @staticmethod
    def validate_threshold(value: object) -> float:
        threshold = float(value)
        osc_tolerance = 1.0e-7
        if (
            not math.isfinite(threshold)
            or threshold < MIN_THRESHOLD - osc_tolerance
            or threshold > MAX_THRESHOLD + osc_tolerance
        ):
            raise ValueError(
                f"pluck threshold must be within [{MIN_THRESHOLD}, {MAX_THRESHOLD}]."
            )
        return min(max(threshold, MIN_THRESHOLD), MAX_THRESHOLD)

    def apply_threshold(self, value: object) -> float:
        threshold = self.validate_threshold(value)
        return self.gate.set_threshold(threshold)

    @staticmethod
    def validate_interaction_omega(value: object) -> float:
        scale = float(value)
        osc_tolerance = 1.0e-6
        if (
            not math.isfinite(scale)
            or scale < MIN_OMEGA_SCALE - osc_tolerance
            or scale > MAX_OMEGA_SCALE + osc_tolerance
        ):
            raise ValueError(
                f"interaction omega scale must be within "
                f"[{MIN_OMEGA_SCALE}, {MAX_OMEGA_SCALE}]."
            )
        return min(max(scale, MIN_OMEGA_SCALE), MAX_OMEGA_SCALE)

    def apply_interaction_omega(self, value: object) -> float:
        if self.interaction_omega_setter is None:
            raise ValueError("interaction omega control is unavailable.")
        return self.interaction_omega_setter(
            self.validate_interaction_omega(value)
        )

    def _handle_threshold(self, address: str, *values: object) -> None:
        try:
            if address != CONTROL_ADDRESS or len(values) != 1:
                raise ValueError("pluck-threshold OSC requires exactly one value.")
            threshold = self.apply_threshold(values[0])
            print(f"pluck threshold updated from GUI: {threshold:.6f}", flush=True)
        except (TypeError, ValueError) as error:
            print(f"rejected pluck-threshold OSC control: {error}", flush=True)

    def _handle_interaction_omega(self, address: str, *values: object) -> None:
        try:
            if address != OMEGA_CONTROL_ADDRESS or len(values) != 1:
                raise ValueError("interaction-omega OSC requires exactly one value.")
            scale = self.apply_interaction_omega(values[0])
            print(f"interaction omega updated from GUI: {scale:.4f}x", flush=True)
        except (TypeError, ValueError) as error:
            print(f"rejected interaction-omega OSC control: {error}", flush=True)

    def _handle_performance_record(self, address: str, *values: object) -> None:
        try:
            if address != PERFORMANCE_RECORD_CONTROL_ADDRESS or not values:
                raise ValueError("performance-record OSC requires an enabled flag")
            enabled = bool(int(values[0]))
            if enabled:
                if len(values) != 27:
                    raise ValueError(
                        "performance-record start requires take, name, WAV path, fundamental, "
                        "decay, tempo, and twenty pitch ratios"
                    )
                self.performance_recorder.start(
                    take_id=str(values[1]),
                    name=str(values[2]),
                    wav_path=str(values[3]),
                    fundamental_hz=float(values[4]),
                    decay_seconds=float(values[5]),
                    bpm=float(values[6]),
                    pitch_ratios=[float(value) for value in values[7:27]],
                )
                print(f"resonant performance recording started: {values[1]}", flush=True)
            else:
                if len(values) != 1:
                    raise ValueError("performance-record stop requires only the enabled flag")
                artifact = self.performance_recorder.stop()
                if self.performance_saved_callback is not None:
                    self.performance_saved_callback(artifact)
                print(
                    "resonant performance notation saved: %s"
                    % artifact["musicxml"],
                    flush=True,
                )
        except (TypeError, ValueError) as error:
            print(f"rejected performance-record OSC control: {error}", flush=True)

    def start(self) -> "HilbertPluckOSCControlV1":
        if self._thread is not None:
            raise RuntimeError("pluck OSC control server is already running.")
        self._thread = Thread(
            target=self.server.serve_forever,
            name="qmw-hilbert-pluck-control",
            daemon=True,
        )
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is not None:
            self.server.shutdown()
            self._thread.join(timeout=2.0)
            self._thread = None
        self.server.server_close()


__all__ = [
    "CONTROL_ADDRESS", "CONTROL_PORT", "HilbertCurrentPluckFrameV1",
    "HilbertCurrentPluckGateV1", "HilbertCurrentPluckV1",
    "HilbertPluckOSCControlV1", "MAX_OMEGA_SCALE", "MAX_THRESHOLD",
    "MIN_OMEGA_SCALE", "MIN_THRESHOLD", "OMEGA_CONTROL_ADDRESS",
]
