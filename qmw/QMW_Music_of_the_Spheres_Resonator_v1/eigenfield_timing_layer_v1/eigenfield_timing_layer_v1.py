#!/usr/bin/env python3
"""Eigenfield Timing Layer v1.

Turns quantum-weighted geometric modes into:
- a continuously updated point-density cloud,
- probabilistic mode excitation events,
- amplitude-envelope parameters,
- OSC streams for Max/MSP visualization and synthesis.

Input
-----
An NPZ exported by quantum_eigenfield_engine_v1.py containing at least:

    geometric_eigenvalues
    mode_probabilities
    mode_amplitudes

Optional:
    spatial_eigenfield
    developmental_drive

Timing concept
--------------
Each geometric mode is a point. Its quantum probability acts as event density,
while eigenvalue spacing, phase, and participation shape the event duration,
attack, decay, and temporal regularity.

Default ports
-------------
OSC output:  7440
OSC control: 7441

Dependencies
------------
numpy
python-osc
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from pathlib import Path
import argparse
import json
import math
import queue
import signal
import threading
import time
from typing import Any

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


@dataclass(frozen=True)
class TimingConfig:
    control_rate_hz: float = 60.0
    event_rate_hz: float = 8.0
    density_gain: float = 1.0
    probability_floor: float = 0.0
    duration_min_ms: float = 35.0
    duration_max_ms: float = 1800.0
    attack_min_ms: float = 2.0
    attack_max_ms: float = 250.0
    release_min_ms: float = 20.0
    release_max_ms: float = 2400.0
    amplitude_gamma: float = 0.70
    phase_jitter_ms: float = 30.0
    spacing_duration_gain: float = 0.65
    entropy_irregularity: float = 0.75
    cloud_rate_divider: int = 6
    seed: int = 23


@dataclass
class ModePoint:
    index: int
    eigenvalue: float
    frequency_hz: float
    decay_seconds: float
    damping_rate: float
    material_weight: float
    eigenvalue_norm: float
    log_eigenvalue_norm: float
    probability: float
    amplitude: float
    phase: float
    spacing: float
    spacing_norm: float
    cloud_x: float
    cloud_y: float
    cloud_z: float


class EigenfieldState:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.modified_time = 0.0
        self.eigenvalues = np.array([], dtype=np.float64)
        self.probabilities = np.array([], dtype=np.float64)
        self.amplitudes = np.array([], dtype=np.complex128)
        self.frequencies_hz = np.array([], dtype=np.float64)
        self.decay_times_seconds = np.array([], dtype=np.float64)
        self.t60_seconds = np.array([], dtype=np.float64)
        self.damping_rates = np.array([], dtype=np.float64)
        self.material_weights = np.array([], dtype=np.float64)
        self.material_model = "spectral_geometry"
        self.points: list[ModePoint] = []
        self.entropy_bits = 0.0
        self.effective_participation = 0.0
        self.load(force=True)

    def load(self, force: bool = False) -> bool:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        modified = self.path.stat().st_mtime
        if not force and modified <= self.modified_time:
            return False

        payload = np.load(self.path)
        eigenvalue_key = (
            "geometric_eigenvalues"
            if "geometric_eigenvalues" in payload.files
            else "eigenvalues" if "eigenvalues" in payload.files else None
        )
        required = {"mode_probabilities", "mode_amplitudes"}
        missing = required.difference(payload.files)
        if eigenvalue_key is None:
            missing.add("geometric_eigenvalues/eigenvalues")
        if missing:
            raise ValueError(f"eigenfield NPZ missing keys: {sorted(missing)}")

        eigenvalues = np.asarray(
            payload[eigenvalue_key], dtype=np.float64
        ).reshape(-1)
        probabilities = np.asarray(
            payload["mode_probabilities"], dtype=np.float64
        ).reshape(-1)
        amplitudes = np.asarray(
            payload["mode_amplitudes"], dtype=np.complex128
        ).reshape(-1)

        count = min(len(eigenvalues), len(probabilities), len(amplitudes))
        if count < 1:
            raise ValueError("eigenfield contains no modes")

        self.eigenvalues = np.maximum(eigenvalues[:count], 0.0)
        probabilities = np.maximum(probabilities[:count], 0.0)
        self.probabilities = probabilities / max(
            float(np.sum(probabilities)), 1e-15
        )
        self.amplitudes = amplitudes[:count]
        model_key = (
            "material_model"
            if "material_model" in payload.files
            else "model" if "model" in payload.files else None
        )
        if model_key is not None:
            self.material_model = str(np.asarray(payload[model_key]).item())

        def optional_modes(name: str, default: float) -> np.ndarray:
            if name not in payload.files:
                return np.full(count, default, dtype=np.float64)
            values = np.asarray(payload[name], dtype=np.float64).reshape(-1)
            if len(values) < count:
                raise ValueError(
                    f"eigenfield field {name!r} has {len(values)} values; "
                    f"expected at least {count}"
                )
            return values[:count]

        self.frequencies_hz = optional_modes("frequencies_hz", 0.0)
        self.decay_times_seconds = optional_modes(
            "decay_times_seconds", 0.0
        )
        self.damping_rates = optional_modes("damping_rates", 0.0)
        self.t60_seconds = optional_modes("t60_seconds", 0.0)
        if not np.any(self.t60_seconds > 0.0):
            self.t60_seconds = np.log(1000.0) * self.decay_times_seconds
        self.material_weights = optional_modes("mode_weights", 1.0)

        self.entropy_bits = float(
            -np.sum(
                self.probabilities
                * np.log2(np.maximum(self.probabilities, 1e-15))
            )
        )
        self.effective_participation = float(
            1.0 / max(np.sum(self.probabilities**2), 1e-15)
        )
        self.points = self._build_points()
        self.modified_time = modified
        return True

    @staticmethod
    def _normalize(values: np.ndarray) -> np.ndarray:
        lo = float(np.min(values))
        hi = float(np.max(values))
        if hi - lo < 1e-15:
            return np.zeros_like(values)
        return (values - lo) / (hi - lo)

    def _build_points(self) -> list[ModePoint]:
        eigen_norm = self._normalize(self.eigenvalues)
        log_norm = self._normalize(np.log1p(self.eigenvalues))
        spacing = np.diff(
            self.eigenvalues,
            append=self.eigenvalues[-1]
            + (
                np.median(np.diff(self.eigenvalues))
                if len(self.eigenvalues) > 1
                else 1.0
            ),
        )
        spacing = np.maximum(spacing, 0.0)
        spacing_norm = self._normalize(spacing)
        magnitude = np.abs(self.amplitudes)
        magnitude /= max(float(np.max(magnitude)), 1e-15)
        phase = np.angle(self.amplitudes)

        points: list[ModePoint] = []
        for i in range(len(self.eigenvalues)):
            # x: intrinsic scale, y: probability density, z: complex phase.
            x = 2.0 * log_norm[i] - 1.0
            y = 2.0 * self.probabilities[i] - 1.0
            z = phase[i] / np.pi
            points.append(
                ModePoint(
                    index=i,
                    eigenvalue=float(self.eigenvalues[i]),
                    frequency_hz=float(self.frequencies_hz[i]),
                    decay_seconds=float(self.decay_times_seconds[i]),
                    damping_rate=float(self.damping_rates[i]),
                    material_weight=float(self.material_weights[i]),
                    eigenvalue_norm=float(eigen_norm[i]),
                    log_eigenvalue_norm=float(log_norm[i]),
                    probability=float(self.probabilities[i]),
                    amplitude=float(magnitude[i]),
                    phase=float(phase[i]),
                    spacing=float(spacing[i]),
                    spacing_norm=float(spacing_norm[i]),
                    cloud_x=float(x),
                    cloud_y=float(y),
                    cloud_z=float(z),
                )
            )
        return points


class EigenfieldTimingLayer:
    def __init__(
        self,
        state_path: Path,
        out_host: str,
        out_port: int,
        control_host: str,
        control_port: int,
        config: TimingConfig,
        watch_file: bool = True,
    ) -> None:
        self.state = EigenfieldState(state_path)
        self.client = SimpleUDPClient(out_host, out_port)
        self.config = config
        self.watch_file = watch_file
        self.rng = np.random.default_rng(config.seed)

        self.enabled = True
        self.alive = True
        self.frame = 0
        self.event_count = 0
        self.next_event_time = time.perf_counter()

        self.commands: queue.SimpleQueue[
            tuple[str, tuple[Any, ...]]
        ] = queue.SimpleQueue()
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._enqueue)
        self.server = ThreadingOSCUDPServer(
            (control_host, control_port), dispatcher
        )
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )

    def _enqueue(self, address: str, *args: Any) -> None:
        self.commands.put((address, tuple(args)))

    def _set_config(self, name: str, value: float) -> None:
        if not hasattr(self.config, name):
            raise ValueError(f"unknown timing parameter {name}")
        self.config = replace(self.config, **{name: value})

    def _process_command(
        self, address: str, args: tuple[Any, ...]
    ) -> None:
        prefix = "/eigenfield/time/control/"
        if not address.startswith(prefix):
            return
        command = address[len(prefix):]

        if command == "run":
            self.enabled = bool(float(args[0])) if args else True
        elif command == "reload":
            self.state.load(force=True)
            self.send_cloud()
        elif command == "status":
            self.send_state()
            self.send_cloud()
        elif command == "quit":
            self.alive = False
        elif command == "event_rate":
            self._set_config(
                "event_rate_hz", max(0.01, float(args[0]))
            )
        elif command == "density_gain":
            self._set_config(
                "density_gain", max(0.0, float(args[0]))
            )
        elif command == "duration_min_ms":
            self._set_config(
                "duration_min_ms", max(1.0, float(args[0]))
            )
        elif command == "duration_max_ms":
            self._set_config(
                "duration_max_ms", max(1.0, float(args[0]))
            )
        elif command == "phase_jitter_ms":
            self._set_config(
                "phase_jitter_ms", max(0.0, float(args[0]))
            )
        elif command == "amplitude_gamma":
            self._set_config(
                "amplitude_gamma", max(0.05, float(args[0]))
            )
        else:
            raise ValueError(f"unknown control address {address}")

    def drain_commands(self) -> None:
        while True:
            try:
                address, args = self.commands.get_nowait()
            except queue.Empty:
                return
            try:
                self._process_command(address, args)
            except Exception as exc:
                print(f"OSC control error: {exc}")
                self.client.send_message("/eigenfield/time/error", str(exc))

    def _mode_distribution(self) -> np.ndarray:
        p = np.maximum(
            self.state.probabilities,
            self.config.probability_floor,
        )
        exponent = max(0.05, self.config.density_gain)
        p = p**exponent
        return p / max(float(np.sum(p)), 1e-15)

    def _event_interval(self) -> float:
        max_entropy = math.log2(max(len(self.state.points), 2))
        entropy_norm = self.state.entropy_bits / max(max_entropy, 1e-12)
        irregularity = (
            self.config.entropy_irregularity * entropy_norm
        )
        base = 1.0 / max(self.config.event_rate_hz, 0.01)
        log_jitter = self.rng.normal(0.0, 0.35 * irregularity)
        return max(0.001, base * math.exp(log_jitter))

    def _envelope_for(self, point: ModePoint) -> dict[str, float]:
        cfg = self.config

        probability_amp = point.probability ** cfg.amplitude_gamma
        amplitude = float(
            np.clip(probability_amp * point.amplitude, 0.0, 1.0)
        )

        # Closely spaced modes sustain longer; isolated modes become shorter,
        # more articulated events.
        spacing_factor = 1.0 - point.spacing_norm
        duration_position = (
            cfg.spacing_duration_gain * spacing_factor
            + (1.0 - cfg.spacing_duration_gain) * point.probability
        )
        duration_ms = cfg.duration_min_ms + duration_position * (
            cfg.duration_max_ms - cfg.duration_min_ms
        )

        attack_position = (
            0.60 * point.eigenvalue_norm
            + 0.40 * (1.0 - point.probability)
        )
        attack_ms = cfg.attack_min_ms + attack_position * (
            cfg.attack_max_ms - cfg.attack_min_ms
        )

        release_position = (
            0.55 * spacing_factor
            + 0.45 * point.probability
        )
        release_ms = cfg.release_min_ms + release_position * (
            cfg.release_max_ms - cfg.release_min_ms
        )

        sustain = float(
            np.clip(
                0.15 + 0.75 * point.probability
                + 0.10 * point.amplitude,
                0.0,
                1.0,
            )
        )

        phase_offset = point.phase / (2.0 * np.pi)
        jitter_ms = (
            cfg.phase_jitter_ms
            * math.sin(point.phase)
            * (0.25 + 0.75 * point.probability)
        )

        return {
            "amp": amplitude,
            "attack_ms": float(attack_ms),
            "duration_ms": float(duration_ms),
            "release_ms": float(release_ms),
            "sustain": sustain,
            "phase_offset": float(phase_offset),
            "jitter_ms": float(jitter_ms),
        }

    def trigger_event(self) -> None:
        distribution = self._mode_distribution()
        index = int(self.rng.choice(len(distribution), p=distribution))
        point = self.state.points[index]
        env = self._envelope_for(point)
        self.event_count += 1

        prefix = f"/eigenfield/time/mode/{index}"
        values = {
            f"{prefix}/trig": 1,
            f"{prefix}/eigenvalue": point.eigenvalue,
            f"{prefix}/frequency_hz": point.frequency_hz,
            f"{prefix}/decay_seconds": point.decay_seconds,
            f"{prefix}/material_weight": point.material_weight,
            f"{prefix}/probability": point.probability,
            f"{prefix}/phase": point.phase,
            f"{prefix}/spacing": point.spacing,
            f"{prefix}/amp": env["amp"],
            f"{prefix}/attack_ms": env["attack_ms"],
            f"{prefix}/duration_ms": env["duration_ms"],
            f"{prefix}/release_ms": env["release_ms"],
            f"{prefix}/sustain": env["sustain"],
            f"{prefix}/jitter_ms": env["jitter_ms"],
            "/eigenfield/time/event/mode": index,
            "/eigenfield/time/event/count": self.event_count,
        }
        for address, value in values.items():
            self.client.send_message(address, value)

        # Compact event packet for OSC-route/unpack workflows.
        self.client.send_message(
            "/eigenfield/time/event",
            [
                index,
                point.eigenvalue,
                point.probability,
                point.phase,
                env["amp"],
                env["attack_ms"],
                env["duration_ms"],
                env["release_ms"],
                env["sustain"],
                env["jitter_ms"],
                point.frequency_hz,
                point.decay_seconds,
                point.material_weight,
                point.damping_rate,
            ],
        )

    def send_cloud(self) -> None:
        points = self.state.points
        self.client.send_message(
            "/eigenfield/cloud/count", len(points)
        )
        self.client.send_message(
            "/eigenfield/cloud/x", [p.cloud_x for p in points]
        )
        self.client.send_message(
            "/eigenfield/cloud/y", [p.cloud_y for p in points]
        )
        self.client.send_message(
            "/eigenfield/cloud/z", [p.cloud_z for p in points]
        )
        self.client.send_message(
            "/eigenfield/cloud/eigenvalues",
            [p.eigenvalue for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/frequencies_hz",
            [p.frequency_hz for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/decay_seconds",
            [p.decay_seconds for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/t60_seconds",
            self.state.t60_seconds.tolist(),
        )
        self.client.send_message(
            "/eigenfield/cloud/damping_rates",
            [p.damping_rate for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/material_weights",
            [p.material_weight for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/probabilities",
            [p.probability for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/amplitudes",
            [p.amplitude for p in points],
        )
        self.client.send_message(
            "/eigenfield/cloud/phases",
            [p.phase for p in points],
        )

    def send_state(self) -> None:
        values = {
            "/eigenfield/time/state/running": int(self.enabled),
            "/eigenfield/time/state/frame": self.frame,
            "/eigenfield/time/state/events": self.event_count,
            "/eigenfield/time/state/event_rate":
                self.config.event_rate_hz,
            "/eigenfield/time/state/entropy_bits":
                self.state.entropy_bits,
            "/eigenfield/time/state/participation":
                self.state.effective_participation,
            "/eigenfield/time/state/mode_count":
                len(self.state.points),
            "/eigenfield/time/state/material_model":
                self.state.material_model,
        }
        for address, value in values.items():
            self.client.send_message(address, value)

    def run(self) -> None:
        self.server_thread.start()
        self.send_state()
        self.send_cloud()

        print("Eigenfield Timing Layer v1")
        print(f"  eigenfield:  {self.state.path}")
        print(f"  modes:       {len(self.state.points)}")
        print(f"  event rate:  {self.config.event_rate_hz:.3f} Hz")
        print(f"  entropy:     {self.state.entropy_bits:.5f} bits")

        next_control_tick = time.perf_counter()
        try:
            while self.alive:
                now = time.perf_counter()
                self.drain_commands()

                if self.watch_file:
                    try:
                        changed = self.state.load(force=False)
                        if changed:
                            self.send_cloud()
                            self.send_state()
                    except Exception as exc:
                        self.client.send_message(
                            "/eigenfield/time/error", str(exc)
                        )

                if self.enabled and now >= self.next_event_time:
                    self.trigger_event()
                    self.next_event_time = now + self._event_interval()

                if (
                    self.frame
                    % max(1, self.config.cloud_rate_divider)
                    == 0
                ):
                    self.send_cloud()
                    self.send_state()

                self.frame += 1
                next_control_tick += (
                    1.0 / max(self.config.control_rate_hz, 1.0)
                )
                delay = next_control_tick - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_control_tick = time.perf_counter()
        finally:
            self.server.shutdown()
            self.server.server_close()
            print("Eigenfield Timing Layer stopped.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eigenfield", type=Path)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7440)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7441)
    parser.add_argument("--event-rate", type=float, default=8.0)
    parser.add_argument("--control-rate", type=float, default=60.0)
    parser.add_argument("--density-gain", type=float, default=1.0)
    parser.add_argument("--duration-min", type=float, default=35.0)
    parser.add_argument("--duration-max", type=float, default=1800.0)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--no-watch", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = TimingConfig(
        control_rate_hz=args.control_rate,
        event_rate_hz=args.event_rate,
        density_gain=args.density_gain,
        duration_min_ms=args.duration_min,
        duration_max_ms=args.duration_max,
        seed=args.seed,
    )
    layer = EigenfieldTimingLayer(
        state_path=args.eigenfield,
        out_host=args.out_host,
        out_port=args.out_port,
        control_host=args.control_host,
        control_port=args.control_port,
        config=config,
        watch_file=not args.no_watch,
    )

    def stop(_signum: int, _frame: Any) -> None:
        layer.alive = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    layer.run()


if __name__ == "__main__":
    main()
