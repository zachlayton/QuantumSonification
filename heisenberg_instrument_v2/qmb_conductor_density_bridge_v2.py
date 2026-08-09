#!/usr/bin/env python3
"""Bridge the live conductor density field into transactional 16x16 QMB frames.

Run the conductor on UDP 7421, this bridge listens there, and the existing Max
Rings instrument continues listening on UDP 7400.  By default, a density-matrix
clock turns accumulated quantum-state displacement into musical commits.  A
fixed wall-clock rate remains available for comparison.
"""

from __future__ import annotations

import argparse
import math
import threading
import time
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from quantum_temporal_mechanics_v1.density_clock import DensityClockReading, DensityMatrixClock


DIMENSION = 16
CELL_COUNT = DIMENSION * DIMENSION


@dataclass(frozen=True)
class BridgeConfig:
    output_hz: float = 6.0
    timing_mode: str = "quantum"
    temporal_distance: float = 0.025
    temporal_process: str = "poisson"
    coherence_depth: float = 0.35
    base_frequency_hz: float = 55.0
    maximum_frequency_hz: float = 12_000.0
    diagonal_anchor_hz: float = 27.5


class ConductorDensityQMBBridge:
    def __init__(self, client: SimpleUDPClient, config: BridgeConfig | None = None) -> None:
        self.client = client
        self.config = config or BridgeConfig()
        self.lock = threading.RLock()
        self.real: list[float] | None = None
        self.imag: list[float] | None = None
        self.harmonics = [float(index + 1) for index in range(DIMENSION)]
        self.revision = 0
        self.last_publish_time = -math.inf
        self.observable_enabled = True
        self.observable_tilt_radians = math.pi / 4.0
        self.observable_phase_radians = 0.0
        self.observable_phase_offsets = [0.0, 0.25 * math.tau, 0.5 * math.tau, 0.75 * math.tau]
        self.observable_weights = [1.0, 0.78, 0.58, 0.42]
        self.four_qubit_weights = [1.0, 0.78, 0.58, 0.42]
        self.output_hz = float(self.config.output_hz)
        self.timing_mode = self._validate_timing_mode(self.config.timing_mode)
        self.temporal_clock = DensityMatrixClock(
            distance_per_pulse=self.config.temporal_distance,
            mode=self.config.temporal_process,
            coherence_depth=self.config.coherence_depth,
        )
        self.source_revision = 0
        self.last_clock_reading: DensityClockReading | None = None
        self.smoothing_ms = 180.0
        self.smoothed_real: list[float] | None = None
        self.smoothed_imag: list[float] | None = None
        self.last_grid_time: float | None = None

    @staticmethod
    def _vector(values: Iterable[object], expected: int | None = None) -> list[float] | None:
        flattened = list(values)
        if len(flattened) == 1 and isinstance(flattened[0], (list, tuple)):
            flattened = list(flattened[0])
        try:
            result = [float(value) for value in flattened]
        except (TypeError, ValueError):
            return None
        if expected is not None and len(result) != expected:
            return None
        if not all(math.isfinite(value) for value in result):
            return None
        return result

    def accept_real(self, *values: object) -> None:
        vector = self._vector(values, CELL_COUNT)
        if vector is not None:
            with self.lock:
                self.real = vector

    def accept_imag(self, *values: object, now: float | None = None) -> bool:
        vector = self._vector(values, CELL_COUNT)
        if vector is None:
            return False
        with self.lock:
            self.imag = vector
            return self.publish_if_due(time.monotonic() if now is None else now)

    def accept_harmonics(self, *values: object) -> None:
        vector = self._vector(values)
        if vector:
            positive = [value for value in vector if value > 0.0]
            if positive:
                with self.lock:
                    self.harmonics = positive[:DIMENSION]

    def accept_grid(self, *values: object, now: float | None = None) -> bool:
        """Accept 256 interleaved [density, phase/pi, occupancy] triples."""
        vector = self._vector(values, CELL_COUNT * 3)
        if vector is None:
            return False
        real: list[float] = []
        imag: list[float] = []
        for index in range(CELL_COUNT):
            magnitude = max(0.0, vector[3 * index])
            phase = math.pi * vector[3 * index + 1]
            real.append(magnitude * math.cos(phase))
            imag.append(magnitude * math.sin(phase))
        timestamp = time.monotonic() if now is None else now
        with self.lock:
            self.source_revision += 1
            try:
                rho = np.asarray(real, dtype=np.float64).reshape(DIMENSION, DIMENSION)
                rho = rho + 1j * np.asarray(imag, dtype=np.float64).reshape(DIMENSION, DIMENSION)
                self.last_clock_reading = self.temporal_clock.update(rho, self.source_revision)
            except ValueError:
                # A malformed/non-positive source matrix cannot advance intrinsic time.
                self.last_clock_reading = None

            if self.smoothed_real is None or self.smoothed_imag is None or self.smoothing_ms <= 0.0:
                self.smoothed_real = real
                self.smoothed_imag = imag
            else:
                dt = max(0.0, timestamp - (self.last_grid_time or timestamp))
                tau = self.smoothing_ms * 0.001
                alpha = 1.0 - math.exp(-dt / max(tau, 1.0e-9))
                self.smoothed_real = [
                    previous + alpha * (current - previous)
                    for previous, current in zip(self.smoothed_real, real)
                ]
                self.smoothed_imag = [
                    previous + alpha * (current - previous)
                    for previous, current in zip(self.smoothed_imag, imag)
                ]
            self.last_grid_time = timestamp
            self.real = list(self.smoothed_real)
            self.imag = list(self.smoothed_imag)
            if self.timing_mode == "rate":
                return self.publish_if_due(timestamp)
            if self.last_clock_reading is None:
                return False
            # Seed Max with a playable state, then let density displacement clock it.
            initialize = self.revision == 0 and self.temporal_clock.previous is not None
            if not initialize and self.last_clock_reading.pulses <= 0:
                return False
            return self.publish_if_due(timestamp, force=True)

    def set_observable_phase(self, normalized: object) -> bool:
        value = max(0.0, min(1.0, float(normalized)))
        with self.lock:
            self.observable_phase_radians = math.tau * value
            return self.publish_if_due(time.monotonic(), force=True)

    def set_observable_phase_radians(self, radians: object) -> bool:
        with self.lock:
            self.observable_phase_radians = float(radians) % math.tau
            return self.publish_if_due(time.monotonic(), force=True)

    def set_observable_phase_offset(self, qubit: int, normalized: object) -> bool:
        value = max(0.0, min(1.0, float(normalized)))
        with self.lock:
            self.observable_phase_offsets[int(qubit)] = math.tau * value
            return self.publish_if_due(time.monotonic(), force=True)

    def set_observable_enabled(self, enabled: object) -> bool:
        with self.lock:
            self.observable_enabled = bool(int(float(enabled)))
            return self.publish_if_due(time.monotonic(), force=True)

    def set_observable(self, name: object) -> bool:
        selected = str(name).strip().upper()
        with self.lock:
            if selected == "FOUR":
                self.observable_weights = list(self.four_qubit_weights)
                self.observable_tilt_radians = math.pi / 4.0
            elif selected not in {"X0", "Y0", "Z0", "XZ0"}:
                raise ValueError("observable must be X0, Y0, Z0, XZ0, or FOUR")
            else:
                self.observable_weights = [1.0, 0.0, 0.0, 0.0]
                self.observable_phase_offsets[0] = 0.0
                if selected == "Z0":
                    self.observable_tilt_radians = 0.0
                    self.observable_phase_radians = 0.0
                elif selected == "X0":
                    self.observable_tilt_radians = math.pi / 2.0
                    self.observable_phase_radians = 0.0
                elif selected == "Y0":
                    self.observable_tilt_radians = math.pi / 2.0
                    self.observable_phase_radians = math.pi / 2.0
                else:
                    self.observable_tilt_radians = math.pi / 4.0
                    self.observable_phase_radians = 0.0
            return self.publish_if_due(time.monotonic(), force=True)

    def set_output_hz(self, value: object) -> None:
        with self.lock:
            self.output_hz = max(0.25, min(30.0, float(value)))

    @staticmethod
    def _validate_timing_mode(value: object) -> str:
        selected = str(value).strip().lower()
        if selected not in {"quantum", "rate"}:
            raise ValueError("timing mode must be 'quantum' or 'rate'")
        return selected

    def set_timing_mode(self, value: object) -> None:
        selected = self._validate_timing_mode(value)
        with self.lock:
            if selected == self.timing_mode:
                return
            self.timing_mode = selected
            if selected == "quantum":
                self.temporal_clock = DensityMatrixClock(
                    distance_per_pulse=self.temporal_clock.distance_per_pulse,
                    mode=self.temporal_clock.mode,
                    coherence_depth=self.temporal_clock.coherence_depth,
                )
                self.last_clock_reading = None

    def set_temporal_distance(self, value: object) -> None:
        with self.lock:
            self.temporal_clock.set_distance_per_pulse(float(value))

    def set_temporal_process(self, value: object) -> None:
        with self.lock:
            self.temporal_clock.set_mode(str(value))

    def set_coherence_depth(self, value: object) -> None:
        with self.lock:
            self.temporal_clock.set_coherence_depth(float(value))

    def set_smoothing_ms(self, value: object) -> None:
        with self.lock:
            self.smoothing_ms = max(0.0, min(5_000.0, float(value)))

    def publish_if_due(self, now: float, force: bool = False) -> bool:
        interval = 1.0 / self.output_hz
        if self.real is None or self.imag is None:
            return False
        if not force and now - self.last_publish_time < interval:
            return False
        self.last_publish_time = now
        self.revision += 1

        real = list(self.real)
        imag = list(self.imag)
        if self.observable_enabled:
            real, imag = self._apply_phase_observable(real, imag)
        magnitude = [math.hypot(re, im) for re, im in zip(real, imag)]
        phase_floor = max(magnitude, default=0.0) * 1.0e-8
        phase = [
            math.atan2(im, re) if mag > phase_floor else 0.0
            for re, im, mag in zip(real, imag, magnitude)
        ]
        frequency = self._frequency_matrix()
        pan = self._pan_matrix()

        prefix = "/qmw/heisenberg/active/matrix"
        self.client.send_message(f"{prefix}/begin", [self.revision, DIMENSION])
        self.client.send_message(f"{prefix}/real", real)
        self.client.send_message(f"{prefix}/imag", imag)
        self.client.send_message(f"{prefix}/magnitude", magnitude)
        self.client.send_message(f"{prefix}/phase", phase)
        self.client.send_message(f"{prefix}/frequency_hz", frequency)
        self.client.send_message(f"{prefix}/pan", pan)
        self.client.send_message(f"{prefix}/end", self.revision)
        return True

    def _apply_phase_observable(
        self, real: list[float], imag: list[float]
    ) -> tuple[list[float], list[float]]:
        """Return rho[m,n] A[n,m] for a four-qubit phase observable."""
        theta = self.observable_tilt_radians
        weight_sum = max(sum(abs(weight) for weight in self.observable_weights), 1.0e-12)
        diagonal = math.cos(theta) / weight_sum
        transverse = math.sin(theta) / weight_sum
        output_real = [0.0] * CELL_COUNT
        output_imag = [0.0] * CELL_COUNT
        for row in range(DIMENSION):
            # The four Zq terms share the diagonal.
            diagonal_index = row * DIMENSION + row
            z_sum = sum(
                weight * (1.0 if ((row >> qubit) & 1) == 0 else -1.0)
                for qubit, weight in enumerate(self.observable_weights)
            )
            output_real[diagonal_index] = real[diagonal_index] * diagonal * z_sum
            output_imag[diagonal_index] = imag[diagonal_index] * diagonal * z_sum

            # Each equatorial term connects basis states differing at q.
            for qubit, weight in enumerate(self.observable_weights):
                column = row ^ (1 << qubit)
                index = row * DIMENSION + column
                phi = self.observable_phase_radians + self.observable_phase_offsets[qubit]
                angle = phi if ((row >> qubit) & 1) == 0 else -phi
                multiplier_real = transverse * weight * math.cos(angle)
                multiplier_imag = transverse * weight * math.sin(angle)
                output_real[index] = real[index] * multiplier_real - imag[index] * multiplier_imag
                output_imag[index] = real[index] * multiplier_imag + imag[index] * multiplier_real
        return output_real, output_imag

    def _frequency_matrix(self) -> list[float]:
        ratios = self.harmonics or [1.0]
        result: list[float] = []
        for row in range(DIMENSION):
            for column in range(DIMENSION):
                if row == column:
                    value = self.config.diagonal_anchor_hz * 2.0 ** (row / DIMENSION)
                else:
                    separation = abs(column - row) - 1
                    ratio = ratios[separation % len(ratios)]
                    value = self.config.base_frequency_hz * ratio
                result.append(min(self.config.maximum_frequency_hz, max(20.0, value)))
        return result

    @staticmethod
    def _pan_matrix() -> list[float]:
        return [
            (column - row) / float(DIMENSION - 1)
            for row in range(DIMENSION)
            for column in range(DIMENSION)
        ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=7421)
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=7400)
    parser.add_argument("--output-hz", type=float, default=6.0)
    parser.add_argument("--timing-mode", choices=("quantum", "rate"), default="quantum")
    parser.add_argument("--temporal-distance", type=float, default=0.025)
    parser.add_argument("--temporal-process", choices=("poisson", "fixed"), default="poisson")
    parser.add_argument("--coherence-depth", type=float, default=0.35)
    args = parser.parse_args()

    bridge = ConductorDensityQMBBridge(
        SimpleUDPClient(args.output_host, args.output_port),
        BridgeConfig(
            output_hz=args.output_hz,
            timing_mode=args.timing_mode,
            temporal_distance=args.temporal_distance,
            temporal_process=args.temporal_process,
            coherence_depth=args.coherence_depth,
        ),
    )
    dispatcher = Dispatcher()
    def accept_imag(_address: str, *values: object) -> None:
        bridge.accept_imag(*values)

    def accept_grid(_address: str, *values: object) -> None:
        bridge.accept_grid(*values)

    dispatcher.map("/qmw/density_field/real", lambda _address, *v: bridge.accept_real(*v))
    dispatcher.map("/qmw/density_field/imag", accept_imag)
    dispatcher.map(
        "/qmw/conductor/eigenfield/grid/16",
        accept_grid,
    )
    dispatcher.map(
        "/qmw/density_field/harmonics",
        lambda _address, *v: bridge.accept_harmonics(*v),
    )
    dispatcher.map(
        "/qmw/bridge/observable/phase",
        lambda _address, value: bridge.set_observable_phase(value),
    )
    dispatcher.map(
        "/qmw/bridge/observable/phase_rad",
        lambda _address, value: bridge.set_observable_phase_radians(value),
    )
    for qubit in range(4):
        dispatcher.map(
            f"/qmw/bridge/observable/phase/q{qubit}",
            lambda _address, value, q=qubit: bridge.set_observable_phase_offset(q, value),
        )
    dispatcher.map(
        "/qmw/bridge/observable/enabled",
        lambda _address, value: bridge.set_observable_enabled(value),
    )
    dispatcher.map(
        "/qmw/bridge/observable",
        lambda _address, value: bridge.set_observable(value),
    )
    dispatcher.map(
        "/qmw/heisenberg/observable",
        lambda _address, value: bridge.set_observable(value),
    )
    dispatcher.map(
        "/qmw/bridge/output_hz",
        lambda _address, value: bridge.set_output_hz(value),
    )
    dispatcher.map(
        "/qmw/bridge/smoothing_ms",
        lambda _address, value: bridge.set_smoothing_ms(value),
    )
    dispatcher.map(
        "/qmw/bridge/clock/timing",
        lambda _address, value: bridge.set_timing_mode(value),
    )
    dispatcher.map(
        "/qmw/bridge/clock/distance",
        lambda _address, value: bridge.set_temporal_distance(value),
    )
    dispatcher.map(
        "/qmw/bridge/clock/process",
        lambda _address, value: bridge.set_temporal_process(value),
    )
    dispatcher.map(
        "/qmw/bridge/clock/coherence_depth",
        lambda _address, value: bridge.set_coherence_depth(value),
    )
    server = ThreadingOSCUDPServer((args.listen_host, args.listen_port), dispatcher)
    print(
        "QMB conductor bridge: "
        f"density udp/{args.listen_port} -> matrix udp/{args.output_port}; "
        f"timing={args.timing_mode} process={args.temporal_process} "
        f"distance={args.temporal_distance:g} (rate fallback={args.output_hz:g} Hz)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
