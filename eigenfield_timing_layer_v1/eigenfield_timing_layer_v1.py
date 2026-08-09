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
    # Appended to preserve the positional order of every v1 timing control.
    event_clock: str = "internal"

    def __post_init__(self) -> None:
        clock = str(self.event_clock).lower()
        if clock not in ("internal", "grw", "hybrid"):
            raise ValueError("event_clock must be internal, grw, or hybrid")
        object.__setattr__(self, "event_clock", clock)


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


@dataclass(frozen=True)
class GRWEigenfieldComparison:
    """One GRW transition projected through the eigenfield channel."""

    event_id: int
    pre_probabilities: np.ndarray
    post_probabilities: np.ndarray
    probability_delta: np.ndarray
    strongest_mode: int
    strengthening: float
    total_variation: float
    excitation_amplitude: float
    audible: bool


def _normalized_density(matrix: np.ndarray) -> np.ndarray:
    state = np.asarray(matrix, dtype=np.complex128)
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("GRW density matrix must be square")
    if not np.all(np.isfinite(state)):
        raise ValueError("GRW density matrix must contain finite values")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 1e-15:
        raise ValueError("GRW density matrix must have positive trace")
    state /= trace
    values, vectors = np.linalg.eigh(state)
    if float(np.min(values)) < -1e-6:
        raise ValueError("GRW density matrix is not positive semidefinite")
    values = np.clip(values.real, 0.0, None)
    values /= max(float(np.sum(values)), 1e-15)
    return (vectors * values[None, :]) @ vectors.conj().T


def _project_modal_probabilities(
    rho: np.ndarray,
    channel_isometry: np.ndarray,
    environment_dimension: int,
    mode_count: int,
) -> np.ndarray:
    state = _normalized_density(rho)
    isometry = np.asarray(channel_isometry, dtype=np.complex128)
    environment = int(environment_dimension)
    if isometry.ndim != 2 or isometry.shape[1] != state.shape[0]:
        raise ValueError("channel isometry is incompatible with GRW rho")
    if environment < 1 or isometry.shape[0] != mode_count * environment:
        raise ValueError("channel isometry rows do not match modes x environment")
    lifted = isometry @ state @ isometry.conj().T
    tensor = lifted.reshape(mode_count, environment, mode_count, environment)
    modal = np.einsum("aebe->ab", tensor, optimize=True)
    probabilities = np.clip(np.real(np.diag(modal)), 0.0, None)
    return probabilities / max(float(np.sum(probabilities)), 1e-15)


def compare_grw_eigenfields(
    rho_after: np.ndarray,
    delta_rho: np.ndarray,
    channel_isometry: np.ndarray,
    environment_dimension: int,
    mode_count: int,
    *,
    event_id: int = 0,
    excitation_amplitude: float = 1.0,
    audible: bool = True,
) -> GRWEigenfieldComparison:
    """Project pre/post density matrices and identify the strongest gain."""
    after = _normalized_density(rho_after)
    delta = np.asarray(delta_rho, dtype=np.complex128)
    if delta.shape != after.shape:
        raise ValueError("delta_rho must have the same shape as rho_after")
    before = _normalized_density(after - delta)
    pre = _project_modal_probabilities(
        before, channel_isometry, environment_dimension, mode_count
    )
    post = _project_modal_probabilities(
        after, channel_isometry, environment_dimension, mode_count
    )
    change = post - pre
    strongest = int(np.argmax(change))
    return GRWEigenfieldComparison(
        event_id=int(event_id),
        pre_probabilities=pre,
        post_probabilities=post,
        probability_delta=change,
        strongest_mode=strongest,
        strengthening=max(0.0, float(change[strongest])),
        total_variation=float(0.5 * np.sum(np.abs(change))),
        excitation_amplitude=float(np.clip(excitation_amplitude, 0.0, 1.0)),
        audible=bool(audible),
    )


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
        self.channel_isometry: np.ndarray | None = None
        self.channel_environment_dimension = 1
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
        if "channel_isometry" in payload.files:
            isometry = np.asarray(
                payload["channel_isometry"], dtype=np.complex128
            )
            environment = int(
                np.asarray(
                    payload["channel_environment_dimension"]
                    if "channel_environment_dimension" in payload.files
                    else 1
                ).item()
            )
            if isometry.ndim != 2 or isometry.shape[0] != count * environment:
                raise ValueError(
                    "channel_isometry rows must equal mode count x environment"
                )
            self.channel_isometry = isometry
            self.channel_environment_dimension = environment
        else:
            self.channel_isometry = None
            self.channel_environment_dimension = 1

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
        self.last_grw_comparison: GRWEigenfieldComparison | None = None
        self.grw_fields: dict[str, tuple[Any, ...]] = {}

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
        grw_prefix = "/qmw/grw/sonification/"
        if address.startswith(grw_prefix):
            suffix = address[len(grw_prefix):]
            self._process_grw_field(suffix, args)
            return

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
        elif command == "event_clock":
            value = str(args[0]).lower() if args else "internal"
            self._set_config("event_clock", value)
            if value in ("internal", "hybrid"):
                self.next_event_time = time.perf_counter() + self._event_interval()
        else:
            raise ValueError(f"unknown control address {address}")

    @staticmethod
    def _complex_matrix(
        real_values: tuple[Any, ...], imag_values: tuple[Any, ...]
    ) -> np.ndarray:
        real = np.asarray(real_values, dtype=np.float64).reshape(-1)
        imag = np.asarray(imag_values, dtype=np.float64).reshape(-1)
        if real.size != imag.size:
            raise ValueError("GRW real/imaginary matrix lengths differ")
        dimension = int(round(math.sqrt(real.size)))
        if dimension * dimension != real.size:
            raise ValueError("GRW matrix payload is not square")
        return (real + 1j * imag).reshape(dimension, dimension)

    def _process_grw_field(
        self, suffix: str, args: tuple[Any, ...]
    ) -> None:
        matrix_fields = {
            "post/rho_real",
            "post/rho_imag",
            "delta/real",
            "delta/imag",
        }
        if suffix in matrix_fields:
            self.grw_fields[suffix] = args
            return
        if suffix != "event":
            return
        required = matrix_fields
        missing = required.difference(self.grw_fields)
        if missing:
            raise ValueError(f"GRW event missing matrix fields: {sorted(missing)}")
        if self.state.channel_isometry is None:
            raise ValueError(
                "GRW clock requires channel_isometry in the eigenfield NPZ"
            )

        rho_after = self._complex_matrix(
            self.grw_fields["post/rho_real"],
            self.grw_fields["post/rho_imag"],
        )
        delta_rho = self._complex_matrix(
            self.grw_fields["delta/real"],
            self.grw_fields["delta/imag"],
        )
        event_id = int(args[0]) if args else 0
        excitation = float(args[2]) if len(args) > 2 else 1.0
        audible = bool(int(args[9])) if len(args) > 9 else True
        comparison = compare_grw_eigenfields(
            rho_after,
            delta_rho,
            self.state.channel_isometry,
            self.state.channel_environment_dimension,
            len(self.state.points),
            event_id=event_id,
            excitation_amplitude=excitation,
            audible=audible,
        )
        self.last_grw_comparison = comparison
        self._publish_grw_comparison(comparison)
        self.grw_fields.clear()
        if (
            self.enabled
            and self.config.event_clock in ("grw", "hybrid")
            and comparison.audible
            and comparison.strengthening > 1e-15
        ):
            self.trigger_event(
                index=comparison.strongest_mode,
                source="grw",
                amplitude_override=comparison.excitation_amplitude,
                comparison=comparison,
            )

    def _publish_grw_comparison(
        self, comparison: GRWEigenfieldComparison
    ) -> None:
        prefix = "/eigenfield/time/grw"
        self.client.send_message(
            f"{prefix}/pre/probabilities",
            comparison.pre_probabilities.tolist(),
        )
        self.client.send_message(
            f"{prefix}/post/probabilities",
            comparison.post_probabilities.tolist(),
        )
        self.client.send_message(
            f"{prefix}/delta/probabilities",
            comparison.probability_delta.tolist(),
        )
        self.client.send_message(
            f"{prefix}/comparison",
            [
                comparison.event_id,
                comparison.strongest_mode,
                comparison.strengthening,
                comparison.pre_probabilities[comparison.strongest_mode],
                comparison.post_probabilities[comparison.strongest_mode],
                comparison.total_variation,
                comparison.excitation_amplitude,
                int(comparison.audible),
            ],
        )

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

    def trigger_event(
        self,
        index: int | None = None,
        *,
        source: str = "internal",
        amplitude_override: float | None = None,
        comparison: GRWEigenfieldComparison | None = None,
    ) -> int:
        if index is None:
            distribution = self._mode_distribution()
            index = int(self.rng.choice(len(distribution), p=distribution))
        if not 0 <= int(index) < len(self.state.points):
            raise ValueError("mode index is outside the eigenfield")
        index = int(index)
        point = self.state.points[index]
        env = self._envelope_for(point)
        if amplitude_override is not None:
            env["amp"] = float(np.clip(amplitude_override, 0.0, 1.0))
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
            "/eigenfield/time/event/source": source,
        }
        for address, value in values.items():
            self.client.send_message(address, value)

        # Compact event packet for OSC-route/unpack workflows.
        packet = [
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
        ]
        if comparison is not None:
            packet.extend(
                [
                    source,
                    comparison.event_id,
                    comparison.strengthening,
                    comparison.pre_probabilities[index],
                    comparison.post_probabilities[index],
                ]
            )
        self.client.send_message(
            "/eigenfield/time/event",
            packet,
        )
        return index

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
            "/eigenfield/time/state/event_clock":
                self.config.event_clock,
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
        print(f"  event clock: {self.config.event_clock}")
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

                if (
                    self.enabled
                    and self.config.event_clock in ("internal", "hybrid")
                    and now >= self.next_event_time
                ):
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
    parser.add_argument(
        "--event-clock",
        choices=("internal", "grw", "hybrid"),
        default="internal",
    )
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
        event_clock=args.event_clock,
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
