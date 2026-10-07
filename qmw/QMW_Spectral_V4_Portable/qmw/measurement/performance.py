"""Live, validated performance configuration for projective observation."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import RLock, Thread

import numpy as np

from qmw.quantum.pauli_basis import normalize_pauli_label, pauli_matrix
from .basis_motion import ProjectorBasisMotion
from .projector import ProjectorBank


MEASUREMENT_CONTROL_PORT = 17877
CONTROL_ROOT = "/qmw/measure/v1/control"
BANK_ADDRESS = f"{CONTROL_ROOT}/bank"
PAULI_ADDRESS = f"{CONTROL_ROOT}/pauli"
APERTURE_ADDRESS = f"{CONTROL_ROOT}/aperture"
APERTURE_RATE_ADDRESS = f"{CONTROL_ROOT}/aperture_rate"
GAUGE_FLUX_ADDRESS = f"{CONTROL_ROOT}/gauge_flux"
BANK_MODES = ("computational", "pauli", "hypercube")
APERTURE_MODES = ("off", "orbit", "sweep", "geodesic")


@dataclass(frozen=True)
class MeasurementPerformanceState:
    bank_mode: str = "computational"
    pauli_label: str = "XYXY"
    aperture_mode: str = "off"
    aperture_rate: float = 1.0
    gauge_flux: float = 0.0
    revision: int = 0


class PhysicalApertureMotion:
    """A physical PVM motion, explicitly distinct from a gauge-frame change."""

    def __init__(self, bank: ProjectorBank, generator: object, mode: str, rate: float) -> None:
        if mode not in APERTURE_MODES[1:]:
            raise ValueError("physical aperture mode must move the basis.")
        if not math.isfinite(float(rate)) or not 0.01 <= float(rate) <= 8.0:
            raise ValueError("aperture rate must lie in [0.01, 8].")
        self.bank = bank
        self.mode = mode
        self.rate = float(rate)
        self.motion = ProjectorBasisMotion(bank, generator)

    def _parameter(self, time: float) -> tuple[float, float]:
        phase = self.rate * float(time)
        if self.mode == "orbit":
            return phase, self.rate
        if self.mode == "sweep":
            return math.sin(phase), self.rate * math.cos(phase)
        # Smooth out-and-back motion along the same unitary geodesic.
        return 0.5 * (1.0 - math.cos(phase)), 0.5 * self.rate * math.sin(phase)

    def bank_at(self, time: float) -> ProjectorBank:
        parameter, _ = self._parameter(time)
        return self.motion.bank_at_parameter(parameter)

    def derivatives_at(self, time: float) -> tuple[np.ndarray, ...]:
        parameter, parameter_rate = self._parameter(time)
        return self.motion.derivatives_at_parameter(parameter, parameter_rate=parameter_rate)


def default_aperture_generator(dimension: int = 16) -> np.ndarray:
    if dimension != 16:
        raise ValueError("the current performance aperture is defined for four qubits.")
    return (
        0.58 * pauli_matrix("YIII")
        + 0.31 * pauli_matrix("IYII")
        + 0.19 * pauli_matrix("IIYI")
        + 0.11 * pauli_matrix("IIIY")
    )


class MeasurementPerformanceControl:
    """Thread-safe Python authority for bank, aperture, and physical flux."""

    def __init__(self, initial: MeasurementPerformanceState | None = None) -> None:
        self._state = initial or MeasurementPerformanceState()
        self._lock = RLock()

    def snapshot(self) -> MeasurementPerformanceState:
        with self._lock:
            return self._state

    def _update(self, **changes: object) -> MeasurementPerformanceState:
        with self._lock:
            self._state = replace(self._state, **changes, revision=self._state.revision + 1)
            return self._state

    def set_bank(self, value: object) -> MeasurementPerformanceState:
        mode = str(value).strip().lower()
        if mode not in BANK_MODES:
            raise ValueError(f"bank must be one of {BANK_MODES}.")
        return self._update(bank_mode=mode)

    def set_pauli(self, value: object) -> MeasurementPerformanceState:
        label = normalize_pauli_label(str(value))
        if len(label) != 4 or set(label) == {"I"}:
            raise ValueError("Pauli bank requires one non-identity four-qubit label.")
        return self._update(pauli_label=label)

    def set_aperture(self, value: object) -> MeasurementPerformanceState:
        mode = str(value).strip().lower()
        if mode not in APERTURE_MODES:
            raise ValueError(f"aperture must be one of {APERTURE_MODES}.")
        return self._update(aperture_mode=mode)

    def set_aperture_rate(self, value: object) -> MeasurementPerformanceState:
        rate = float(value)
        if not math.isfinite(rate) or not 0.01 <= rate <= 8.0:
            raise ValueError("aperture rate must lie in [0.01, 8].")
        return self._update(aperture_rate=rate)

    def set_gauge_flux(self, value: object) -> MeasurementPerformanceState:
        flux = float(value)
        if not math.isfinite(flux) or not -math.pi <= flux <= math.pi:
            raise ValueError("physical primary-loop flux must lie in [-pi, pi].")
        return self._update(gauge_flux=flux)


class MeasurementPerformanceOSCControl:
    def __init__(self, authority: MeasurementPerformanceControl, *, host: str = "127.0.0.1", port: int = MEASUREMENT_CONTROL_PORT) -> None:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        self.authority = authority
        dispatcher = Dispatcher()
        dispatcher.map(BANK_ADDRESS, self._handler, authority.set_bank)
        dispatcher.map(PAULI_ADDRESS, self._handler, authority.set_pauli)
        dispatcher.map(APERTURE_ADDRESS, self._handler, authority.set_aperture)
        dispatcher.map(APERTURE_RATE_ADDRESS, self._handler, authority.set_aperture_rate)
        dispatcher.map(GAUGE_FLUX_ADDRESS, self._handler, authority.set_gauge_flux)
        self.server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
        self.server.daemon_threads = True
        self._thread: Thread | None = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    @staticmethod
    def _handler(address: str, fixed_args: list[object], *values: object) -> None:
        try:
            if len(fixed_args) != 1 or not callable(fixed_args[0]):
                raise ValueError("measurement control setter is unavailable.")
            if len(values) != 1:
                raise ValueError("measurement control requires exactly one value.")
            state = fixed_args[0](values[0])
            print(
                f"measurement control {address}: bank={state.bank_mode} "
                f"aperture={state.aperture_mode}@{state.aperture_rate:.3f} "
                f"flux={state.gauge_flux:.4f}", flush=True,
            )
        except (TypeError, ValueError) as error:
            print(f"rejected measurement control {address}: {error}", flush=True)

    def start(self) -> "MeasurementPerformanceOSCControl":
        if self._thread is not None:
            raise RuntimeError("measurement OSC control server is already running.")
        self._thread = Thread(target=self.server.serve_forever, name="qmw-measurement-control", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is not None:
            self.server.shutdown()
            self._thread.join(timeout=2.0)
            self._thread = None
        self.server.server_close()


__all__ = [
    "APERTURE_ADDRESS", "APERTURE_MODES", "APERTURE_RATE_ADDRESS",
    "BANK_ADDRESS", "BANK_MODES", "CONTROL_ROOT", "GAUGE_FLUX_ADDRESS",
    "MEASUREMENT_CONTROL_PORT", "MeasurementPerformanceControl",
    "MeasurementPerformanceOSCControl", "MeasurementPerformanceState",
    "PAULI_ADDRESS", "PhysicalApertureMotion", "default_aperture_generator",
]
