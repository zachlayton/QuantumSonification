"""Live, downstream rendering controls for the temporal-memory observer.

This module owns only the observer configuration used for *future* temporal
frames.  It cannot mutate a QuantumFrame, its density matrix, or QMW's event
and measurement authorities.
"""

from __future__ import annotations

from dataclasses import replace
import math
from threading import RLock, Thread

from .engine import TemporalMemoryConfig


QMW_TEMPORAL_MEMORY_CONTROL_PORT = 17885
QMW_TEMPORAL_MEMORY_CONTROL_ROOT = "/qmw/temporal_memory/v1/control"
QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS = (
    f"{QMW_TEMPORAL_MEMORY_CONTROL_ROOT}/base_delay_seconds"
)
QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS = (
    f"{QMW_TEMPORAL_MEMORY_CONTROL_ROOT}/ratio_preset"
)
QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS = (
    f"{QMW_TEMPORAL_MEMORY_CONTROL_ROOT}/phase_warp"
)
QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS = (
    f"{QMW_TEMPORAL_MEMORY_CONTROL_ROOT}/feedback_amount"
)
QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS = (
    f"{QMW_TEMPORAL_MEMORY_CONTROL_ROOT}/diffusion"
)
MIN_BASE_DELAY_SECONDS = 0.020
# The largest declared ratio is 3:2 and phase warp can add 40%.  At the
# 2.5-second base limit, a line therefore reaches 5.25 seconds; the receiver
# reserves a 5.5-second DelayC buffer for that explicit maximum.
MAX_BASE_DELAY_SECONDS = 2.500
MAX_PHASE_WARP = 0.40
MAX_FEEDBACK_AMOUNT = 0.42

# These are declared musical ratio fields, not quantum clocks.  All retain a
# maximum 3:2 multiplier, so the 2.5-second base-delay bound remains inside
# the receiver's 5.5-second DelayC allocation even at maximum phase warp.
RATIO_PRESETS: dict[str, tuple[float, ...]] = {
    "rational": TemporalMemoryConfig().metric_ratios,
    "cluster": (
        0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10,
        1.125, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45,
    ),
    "odd": (
        1.0, 9 / 8, 7 / 6, 5 / 4, 4 / 3, 11 / 8, 7 / 5, 3 / 2,
        13 / 12, 8 / 7, 6 / 5, 9 / 7, 7 / 6, 11 / 9, 5 / 4, 13 / 10,
    ),
    "cascade": (
        0.50, 0.56, 0.63, 0.71, 0.79, 0.89, 1.00, 1.06,
        1.12, 1.19, 1.26, 1.33, 1.38, 1.42, 1.46, 1.50,
    ),
}


class TemporalMemoryControl:
    """Thread-safe owner of one bounded, downstream delay-rendering policy."""

    def __init__(self, initial: TemporalMemoryConfig | None = None) -> None:
        self._config = initial or TemporalMemoryConfig()
        self._ratio_preset = "rational"
        self._lock = RLock()

    def snapshot(self) -> TemporalMemoryConfig:
        """Return the immutable policy to use for the next observer frame."""

        with self._lock:
            return self._config

    @property
    def ratio_preset(self) -> str:
        with self._lock:
            return self._ratio_preset

    @staticmethod
    def validate_base_delay_seconds(value: object) -> float:
        delay = float(value)
        # OSC single-precision values may fall microscopically outside a
        # displayed endpoint.  Clamp only that transport-rounding tolerance.
        tolerance = 1.0e-6
        if (
            not math.isfinite(delay)
            or delay < MIN_BASE_DELAY_SECONDS - tolerance
            or delay > MAX_BASE_DELAY_SECONDS + tolerance
        ):
            raise ValueError(
                "temporal base delay must be within "
                f"[{MIN_BASE_DELAY_SECONDS}, {MAX_BASE_DELAY_SECONDS}] seconds."
            )
        return min(max(delay, MIN_BASE_DELAY_SECONDS), MAX_BASE_DELAY_SECONDS)

    def set_base_delay_seconds(self, value: object) -> TemporalMemoryConfig:
        """Replace only the base delay for subsequent read-only frames."""

        delay = self.validate_base_delay_seconds(value)
        with self._lock:
            self._config = replace(self._config, base_delay_seconds=delay)
            return self._config

    @staticmethod
    def _bounded(name: str, value: object, lower: float, upper: float) -> float:
        result = float(value)
        tolerance = 1.0e-6
        if not math.isfinite(result) or result < lower - tolerance or result > upper + tolerance:
            raise ValueError(f"{name} must be within [{lower}, {upper}].")
        return min(max(result, lower), upper)

    def set_ratio_preset(self, value: object) -> TemporalMemoryConfig:
        name = str(value).strip().lower()
        if name not in RATIO_PRESETS:
            raise ValueError(f"temporal ratio preset must be one of {tuple(RATIO_PRESETS)}.")
        with self._lock:
            self._ratio_preset = name
            self._config = replace(self._config, metric_ratios=RATIO_PRESETS[name])
            return self._config

    def set_phase_warp(self, value: object) -> TemporalMemoryConfig:
        amount = self._bounded("temporal phase warp", value, 0.0, MAX_PHASE_WARP)
        with self._lock:
            self._config = replace(self._config, phase_delay_depth=amount)
            return self._config

    def set_feedback_amount(self, value: object) -> TemporalMemoryConfig:
        amount = self._bounded("temporal feedback amount", value, 0.0, MAX_FEEDBACK_AMOUNT)
        with self._lock:
            self._config = replace(self._config, cross_feedback_cap=amount)
            return self._config

    def set_diffusion(self, value: object) -> TemporalMemoryConfig:
        amount = self._bounded("temporal diffusion", value, 0.0, 1.0)
        with self._lock:
            self._config = replace(self._config, feedback_diffusion=amount)
            return self._config


class TemporalMemoryOSCControl:
    """Receive bounded temporal-field mapping controls from SuperCollider."""

    def __init__(
        self,
        control: TemporalMemoryControl,
        *,
        host: str = "127.0.0.1",
        port: int = QMW_TEMPORAL_MEMORY_CONTROL_PORT,
    ) -> None:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        self.control = control
        dispatcher = Dispatcher()
        dispatcher.map(QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS, self._handle_base_delay)
        dispatcher.map(QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS, self._handle_ratio_preset)
        dispatcher.map(QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS, self._handle_phase_warp)
        dispatcher.map(QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS, self._handle_feedback_amount)
        dispatcher.map(QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS, self._handle_diffusion)
        self.server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
        self.server.daemon_threads = True
        self._thread: Thread | None = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    def apply_base_delay_seconds(self, value: object) -> TemporalMemoryConfig:
        return self.control.set_base_delay_seconds(value)

    def _apply_one(self, address: str, values: tuple[object, ...], expected: str, setter, label: str) -> None:
        try:
            if address != expected or len(values) != 1:
                raise ValueError(f"{label} OSC requires exactly one value.")
            config = setter(values[0])
            print(f"temporal-memory {label} updated from mixer: {values[0]}", flush=True)
            return config
        except (TypeError, ValueError) as error:
            print(f"rejected temporal-memory OSC control: {error}", flush=True)

    def _handle_base_delay(self, address: str, *values: object) -> None:
        try:
            if address != QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS or len(values) != 1:
                raise ValueError("temporal base-delay OSC requires exactly one value.")
            config = self.apply_base_delay_seconds(values[0])
            print(
                "temporal-memory base delay updated from mixer: %.1f ms"
                % (config.base_delay_seconds * 1000.0),
                flush=True,
            )
        except (TypeError, ValueError) as error:
            print(f"rejected temporal-memory OSC control: {error}", flush=True)

    def _handle_ratio_preset(self, address: str, *values: object) -> None:
        self._apply_one(address, values, QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS,
            self.control.set_ratio_preset, "ratio preset")

    def _handle_phase_warp(self, address: str, *values: object) -> None:
        self._apply_one(address, values, QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS,
            self.control.set_phase_warp, "phase warp")

    def _handle_feedback_amount(self, address: str, *values: object) -> None:
        self._apply_one(address, values, QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS,
            self.control.set_feedback_amount, "feedback amount")

    def _handle_diffusion(self, address: str, *values: object) -> None:
        self._apply_one(address, values, QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS,
            self.control.set_diffusion, "diffusion")

    def start(self) -> "TemporalMemoryOSCControl":
        if self._thread is not None:
            raise RuntimeError("temporal-memory OSC control server is already running.")
        self._thread = Thread(
            target=self.server.serve_forever,
            name="qmw-temporal-memory-control",
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
    "MAX_BASE_DELAY_SECONDS", "MAX_FEEDBACK_AMOUNT", "MAX_PHASE_WARP",
    "MIN_BASE_DELAY_SECONDS", "RATIO_PRESETS",
    "QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS",
    "QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS",
    "QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS",
    "QMW_TEMPORAL_MEMORY_CONTROL_PORT", "QMW_TEMPORAL_MEMORY_CONTROL_ROOT",
    "QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS",
    "QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS",
    "TemporalMemoryControl", "TemporalMemoryOSCControl",
]
