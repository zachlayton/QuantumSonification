"""Revisioned OSC observer for the authoritative QMW scalar field V3."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import math
from pathlib import Path
import threading
import time
from typing import Any

import numpy as np

from .backends.gaussian import GaussianScalarFieldBackend
from .gaussian import (
    GaussianFieldState,
    coherent_mode_state,
    localized_displacement_state,
    squeezed_mode_state,
    thermal_state,
    vacuum_state,
)
from .model import ScalarFieldModel, ScalarFieldSpec
from .performance import FieldPerformanceRecorder
from .schema import ScalarFieldFrame
from .sonification import gaussian_harmonic_descriptor
from .gaussian_temporal import (
    GaussianFieldTemporalEngine,
    GaussianFieldTemporalFrame,
)


OUTPUT_PORT = 17850
CONTROL_PORT = 17851
SCHEMA = "qmw.scalar_field.osc.v3"
OSC_VERSION = 3
OSC_ROOT = "/qmw/qft/v3"
STATE_NAMES = ("localized", "coherent", "squeezed", "thermal", "vacuum")
DEFAULT_PERFORMANCE_DIRECTORY = Path(__file__).resolve().parent / "recordings"


@dataclass(frozen=True)
class LiveScalarFieldParameters:
    state_name: str = "localized"
    sites: int = 8
    mass: float = 0.6
    lattice_spacing: float = 1.0
    propagation_speed: float = 1.0
    localized_site: int = 4
    localized_amplitude: float = 1.0
    mode_index: int = 0
    displacement_real: float = 0.8
    displacement_imag: float = 0.0
    squeezing_magnitude: float = 0.5
    squeezing_phase: float = 0.0
    temperature: float = 0.8

    def field_spec(self) -> ScalarFieldSpec:
        return ScalarFieldSpec(
            sites=self.sites,
            mass=self.mass,
            lattice_spacing=self.lattice_spacing,
            propagation_speed=self.propagation_speed,
        )


class LiveScalarFieldEngine:
    def __init__(
        self,
        parameters: LiveScalarFieldParameters | None = None,
        *,
        osc_version: int = OSC_VERSION,
    ) -> None:
        self._lock = threading.RLock()
        self._parameters = parameters or LiveScalarFieldParameters()
        self._osc_version = int(osc_version)
        if self._osc_version < 1:
            raise ValueError("OSC version must be positive")
        self._osc_root = f"/qmw/qft/v{self._osc_version}"
        self._model_time = 0.0
        self._running = True
        self._quit = False
        self._temporal_distance = 0.025
        self._temporal_mode = "poisson"
        self._clock_scale = 1.0
        self._geodesic_bending_depth = 0.6
        self._temporal_engine = self._new_temporal_engine()
        self._temporal_frame: GaussianFieldTemporalFrame | None = None
        self._temporal_rebase_pending = False
        self._source_revision = 0
        self._performance_recorder = FieldPerformanceRecorder(
            DEFAULT_PERFORMANCE_DIRECTORY, version=self._osc_version
        )
        self._performance_artifact: dict[str, Any] | None = None

    def _new_temporal_engine(self) -> GaussianFieldTemporalEngine:
        return GaussianFieldTemporalEngine(
            self._parameters.sites,
            hbar=self._parameters.field_spec().hbar,
            distance_per_pulse=self._temporal_distance,
            mode=self._temporal_mode,
            seed=23,
            clock_scale=self._clock_scale,
            geodesic_bending_depth=self._geodesic_bending_depth,
        )

    def _reset_temporal_engine(self) -> None:
        self._temporal_engine = self._new_temporal_engine()
        self._temporal_frame = None
        self._temporal_rebase_pending = False
        self._source_revision = 0

    @property
    def should_quit(self) -> bool:
        with self._lock:
            return self._quit

    @property
    def parameters(self) -> LiveScalarFieldParameters:
        with self._lock:
            return self._parameters

    @property
    def temporal_frame(self) -> GaussianFieldTemporalFrame | None:
        with self._lock:
            return self._temporal_frame

    @property
    def osc_root(self) -> str:
        return self._osc_root

    @property
    def temporal_config(self) -> dict[str, float | str]:
        with self._lock:
            return {
                "distance_per_pulse": self._temporal_distance,
                "mode": self._temporal_mode,
                "clock_scale": self._clock_scale,
                "geodesic_bending_depth": self._geodesic_bending_depth,
            }

    def consume_performance_artifact(self) -> dict[str, Any] | None:
        with self._lock:
            artifact = self._performance_artifact
            self._performance_artifact = None
            return artifact

    @staticmethod
    def _initial_state(
        parameters: LiveScalarFieldParameters, model: ScalarFieldModel
    ) -> GaussianFieldState:
        sites = parameters.sites
        mode = parameters.mode_index
        if parameters.state_name == "localized":
            field = np.zeros(sites)
            momentum = np.zeros(sites)
            field[parameters.localized_site] = (
                parameters.localized_amplitude * parameters.displacement_real
            )
            momentum[parameters.localized_site] = (
                parameters.localized_amplitude * parameters.displacement_imag
            )
            return localized_displacement_state(
                model, mean_phi=field, mean_pi=momentum
            )
        if parameters.state_name == "coherent":
            alpha = np.zeros(sites, dtype=complex)
            alpha[mode] = (
                parameters.displacement_real
                + 1j * parameters.displacement_imag
            )
            return coherent_mode_state(model, alpha)
        if parameters.state_name == "squeezed":
            squeezing = np.zeros(sites, dtype=complex)
            squeezing[mode] = parameters.squeezing_magnitude * np.exp(
                1j * parameters.squeezing_phase
            )
            return squeezed_mode_state(model, squeezing)
        if parameters.state_name == "thermal":
            return thermal_state(model, parameters.temperature)
        if parameters.state_name == "vacuum":
            return vacuum_state(model)
        raise ValueError(f"unsupported state: {parameters.state_name}")

    def step(self, dt: float) -> tuple[ScalarFieldFrame, LiveScalarFieldParameters]:
        if not np.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        with self._lock:
            if self._running:
                self._model_time += float(dt)
            parameters = self._parameters
            model = ScalarFieldModel.from_spec(parameters.field_spec())
            initial = self._initial_state(parameters, model)
            frame = GaussianScalarFieldBackend(parameters.field_spec()).run(
                initial, time=self._model_time
            )
            if self._temporal_rebase_pending:
                self._temporal_engine.rebase(frame)
                self._temporal_rebase_pending = False
            self._temporal_frame = self._temporal_engine.update(
                frame, self._source_revision
            )
            self._performance_recorder.capture(
                frame, self._temporal_frame, model, float(dt)
            )
            self._source_revision += 1
            return frame, parameters

    def apply_control(self, address: str, *arguments: Any) -> None:
        with self._lock:
            parameters = self._parameters
            reset_time = False
            reset_temporal = False
            rebase_temporal = False
            if address == f"{self._osc_root}/control/state":
                state = str(arguments[0]).lower()
                if state not in STATE_NAMES:
                    raise ValueError(f"state must be one of {STATE_NAMES}")
                parameters = replace(parameters, state_name=state)
                reset_time = True
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/localized":
                site, amplitude = int(arguments[0]), float(arguments[1])
                if not 0 <= site < parameters.sites:
                    raise ValueError("localized site lies outside the lattice")
                if not np.isfinite(amplitude):
                    raise ValueError("localized amplitude must be finite")
                parameters = replace(
                    parameters,
                    localized_site=site,
                    localized_amplitude=amplitude,
                )
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/mode":
                mode = int(arguments[0])
                if not 0 <= mode < parameters.sites:
                    raise ValueError("mode lies outside the field spectrum")
                parameters = replace(parameters, mode_index=mode)
                rebase_temporal = True
            elif address in {
                f"{self._osc_root}/control/displacement",
                f"{self._osc_root}/control/alpha",
            }:
                real, imaginary = float(arguments[0]), float(arguments[1])
                if not np.isfinite([real, imaginary]).all():
                    raise ValueError("coherent displacement must be finite")
                parameters = replace(
                    parameters,
                    displacement_real=real,
                    displacement_imag=imaginary,
                )
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/squeezing":
                magnitude = float(arguments[0])
                phase = (
                    float(arguments[1])
                    if len(arguments) > 1
                    else parameters.squeezing_phase
                )
                if not np.isfinite([magnitude, phase]).all():
                    raise ValueError("squeezing magnitude and phase must be finite")
                if not 0.0 <= magnitude <= 1.5:
                    raise ValueError("squeezing magnitude must lie in [0, 1.5]")
                # Phase is periodic. OSC transports slider values as float32,
                # so an endpoint intended as pi can arrive slightly above it.
                phase = (phase + math.pi) % math.tau - math.pi
                parameters = replace(
                    parameters,
                    squeezing_magnitude=magnitude,
                    squeezing_phase=phase,
                )
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/temperature":
                temperature = float(arguments[0])
                if not np.isfinite(temperature) or temperature <= 0.0:
                    raise ValueError("temperature must be positive")
                parameters = replace(parameters, temperature=temperature)
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/field":
                mass, speed = float(arguments[0]), float(arguments[1])
                if not np.isfinite([mass, speed]).all() or min(mass, speed) <= 0.0:
                    raise ValueError("mass and propagation speed must be positive")
                parameters = replace(
                    parameters, mass=mass, propagation_speed=speed
                )
                rebase_temporal = True
            elif address == f"{self._osc_root}/control/temporal-distance":
                self._temporal_distance = self._temporal_engine.set_distance_per_pulse(
                    float(arguments[0])
                )
            elif address == f"{self._osc_root}/control/temporal-mode":
                self._temporal_mode = self._temporal_engine.set_mode(
                    str(arguments[0])
                )
            elif address == f"{self._osc_root}/control/clock-scale":
                self._clock_scale = self._temporal_engine.set_clock_scale(
                    float(arguments[0])
                )
            elif address == f"{self._osc_root}/control/geodesic-bending-depth":
                self._geodesic_bending_depth = (
                    self._temporal_engine.set_geodesic_bending_depth(
                        float(arguments[0])
                    )
                )
            elif address == f"{self._osc_root}/control/performance-record":
                enabled = bool(int(arguments[0]))
                if enabled:
                    self._performance_recorder.start(
                        field_time=self._model_time,
                        take_id=str(arguments[1]),
                        name=str(arguments[2]),
                        fundamental_hz=float(arguments[3]),
                        pitch_mode=int(arguments[4]),
                        decay_seconds=float(arguments[5]),
                        pitch_deviation_cents=(
                            float(arguments[6]) if len(arguments) > 6 else 0.0
                        ),
                    )
                elif self._performance_recorder.active:
                    self._performance_artifact = self._performance_recorder.stop()
            elif address == f"{self._osc_root}/control/performance-config":
                self._performance_recorder.configure(
                    fundamental_hz=float(arguments[0]),
                    pitch_mode=int(arguments[1]),
                    decay_seconds=float(arguments[2]),
                    pitch_deviation_cents=(
                        float(arguments[3]) if len(arguments) > 3 else 0.0
                    ),
                )
            elif address == f"{self._osc_root}/control/running":
                self._running = bool(int(arguments[0]))
            elif address == f"{self._osc_root}/control/reset":
                reset_time = True
                reset_temporal = True
            elif address == f"{self._osc_root}/control/quit":
                self._quit = True
            else:
                raise ValueError(f"unsupported OSC control: {address}")
            self._parameters = parameters
            if reset_time:
                self._model_time = 0.0
            if rebase_temporal and not reset_temporal:
                self._temporal_rebase_pending = True
            # Live edits remain part of the measured Gaussian trajectory.
            # Clearing the observer for every OSC slider value made gestures
            # silent by discarding the previous frame and pulse remainder.
            if reset_temporal:
                self._reset_temporal_engine()


class _FanoutOSCClient:
    def __init__(self, *clients: Any) -> None:
        self.clients = clients

    def send_message(self, address: str, values: Any) -> None:
        for client in self.clients:
            client.send_message(address, values)


class ScalarFieldFramePublisher:
    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
        osc_version: int = OSC_VERSION,
        chunk_correlations: bool | None = None,
        max_temporal_pulses_per_frame: int = 8,
        max_audible_pulses_per_second: float = 48.0,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.revision = 0
        self.osc_version = int(osc_version)
        self.osc_root = f"/qmw/qft/v{self.osc_version}"
        self.schema = f"qmw.scalar_field.osc.v{self.osc_version}"
        self.chunk_correlations = (
            self.osc_version >= 5
            if chunk_correlations is None
            else bool(chunk_correlations)
        )
        if int(max_temporal_pulses_per_frame) < 1:
            raise ValueError("max_temporal_pulses_per_frame must be positive")
        if (
            not math.isfinite(max_audible_pulses_per_second)
            or max_audible_pulses_per_second <= 0.0
        ):
            raise ValueError("max_audible_pulses_per_second must be positive")
        # This is a downstream OSC/audio budget. Scientific clock readings
        # retain every Bures-distance crossing; only excess audible events are
        # coalesced before they can flood SuperCollider.
        self.max_temporal_pulses_per_frame = int(max_temporal_pulses_per_frame)
        self.max_audible_pulses_per_second = float(max_audible_pulses_per_second)
        self._audible_pulse_tokens = float(self.max_temporal_pulses_per_frame)
        self._audible_pulse_time = time.monotonic()
        self._temporal_site_cursor = 0
        self._geodesic_site_cursor = 0

    def _bounded_pulse_records(
        self, readings: tuple[Any, ...], *, cursor_name: str, limit: int
    ) -> list[tuple[int, int]]:
        """Choose audible pulse records fairly without changing clock state."""
        count = len(readings)
        if count == 0:
            return []
        emitted = [0] * count
        selected: list[tuple[int, int]] = []
        cursor = int(getattr(self, cursor_name)) % count
        while len(selected) < limit:
            chosen = None
            for offset in range(count):
                index = (cursor + offset) % count
                if emitted[index] < int(readings[index].pulses):
                    chosen = index
                    break
            if chosen is None:
                break
            reading = readings[chosen]
            first_record = int(reading.record_index) - int(reading.pulses) + 1
            selected.append((chosen, first_record + emitted[chosen]))
            emitted[chosen] += 1
            cursor = (chosen + 1) % count
        setattr(self, cursor_name, cursor)
        return selected

    def _available_audible_pulses(self) -> int:
        """Return the shared sound-trigger budget without touching field data."""
        now = time.monotonic()
        elapsed = max(0.0, now - self._audible_pulse_time)
        self._audible_pulse_time = now
        self._audible_pulse_tokens = min(
            float(self.max_temporal_pulses_per_frame),
            self._audible_pulse_tokens
            + elapsed * self.max_audible_pulses_per_second,
        )
        return int(self._audible_pulse_tokens)

    def _consume_audible_pulses(self, count: int) -> None:
        self._audible_pulse_tokens = max(0.0, self._audible_pulse_tokens - count)

    def publish_performance_saved(self, artifact: dict[str, Any]) -> None:
        self.client.send_message(
            f"{self.osc_root}/performance/saved",
            [
                int(artifact["event_count"]),
                str(artifact["musicxml"]),
                str(artifact["event_json"]),
            ],
        )

    def publish(
        self,
        frame: ScalarFieldFrame,
        parameters: LiveScalarFieldParameters,
        temporal: GaussianFieldTemporalFrame | None = None,
        temporal_config: dict[str, float | str] | None = None,
    ) -> int:
        self.revision += 1
        revision = self.revision
        self.client.send_message(
            f"{self.osc_root}/frame/begin", [revision, frame.time, self.schema]
        )
        for suffix, values in (
            ("phi", frame.mean_phi),
            ("pi", frame.mean_pi),
            ("energy", frame.local_energy_density),
            ("occupations", frame.mode_occupations),
            ("frequencies", frame.frequencies),
        ):
            self.client.send_message(
                f"{self.osc_root}/{suffix}",
                [revision, *np.asarray(values, dtype=float).tolist()],
            )
        correlation = np.asarray(frame.connected_field_correlator, dtype=float)
        if self.chunk_correlations:
            for row, values in enumerate(correlation):
                self.client.send_message(
                    f"{self.osc_root}/correlation/row",
                    [revision, row, *values.tolist()],
                )
        else:
            self.client.send_message(
                f"{self.osc_root}/correlation",
                [revision, *correlation.reshape(-1).tolist()],
            )
        self.client.send_message(
            f"{self.osc_root}/global", [revision, frame.mean_energy, frame.purity]
        )
        self.client.send_message(
            f"{self.osc_root}/parameters",
            [
                revision,
                parameters.state_name,
                parameters.mass,
                parameters.propagation_speed,
                parameters.localized_site,
                parameters.localized_amplitude,
                parameters.mode_index,
                parameters.displacement_real,
                parameters.displacement_imag,
                parameters.squeezing_magnitude,
                parameters.squeezing_phase,
                parameters.temperature,
            ],
        )
        self.client.send_message(f"{self.osc_root}/frame/end", revision)
        if temporal is not None:
            global_clock = temporal.global_clock
            self.client.send_message(
                f"{self.osc_root}/temporal/global",
                [
                    global_clock.source_revision,
                    global_clock.record_index,
                    global_clock.intrinsic_time,
                    global_clock.delta_bures,
                    global_clock.scaled_increment,
                    global_clock.remainder,
                    global_clock.next_record_distance,
                    global_clock.pulses,
                    temporal.aggregate_kind,
                ],
            )
            if temporal_config is not None:
                # This is an acknowledgement of the live temporal-engine
                # configuration, not an additional physical observable.  It
                # lets a receiving interface distinguish a Bures-driven clock
                # from a local performance adapter which is currently
                # bypassing that clock.
                self.client.send_message(
                    f"{self.osc_root}/temporal/config",
                    [
                        global_clock.source_revision,
                        float(temporal_config["distance_per_pulse"]),
                        float(temporal_config["clock_scale"]),
                        float(temporal_config["geodesic_bending_depth"]),
                        str(temporal_config["mode"]),
                    ],
                )
            descriptors = []
            for site_clock in temporal.site_clocks:
                descriptor = gaussian_harmonic_descriptor(
                    site_clock,
                    mass=parameters.mass,
                    propagation_speed=parameters.propagation_speed,
                    lattice_spacing=parameters.lattice_spacing,
                )
                self.client.send_message(
                    f"{self.osc_root}/temporal/site",
                    [
                        site_clock.source_revision,
                        site_clock.site,
                        site_clock.record_index,
                        site_clock.intrinsic_time,
                        site_clock.delta_bures,
                        site_clock.scaled_increment,
                        site_clock.remainder,
                        site_clock.next_record_distance,
                        site_clock.pulses,
                        site_clock.mean_phi,
                        site_clock.mean_pi,
                        site_clock.local_energy,
                        site_clock.variance_phi,
                        site_clock.variance_pi,
                        site_clock.covariance_phi_pi,
                        descriptor.x,
                        descriptor.y,
                        descriptor.z,
                        descriptor.purity,
                        descriptor.covariance_correlation,
                        descriptor.entropy_control,
                    ],
                )
                descriptors.append(descriptor)
            # Both clock domains share one audio budget. Reserve part of a
            # burst for geodesic events when both domains have crossings, so
            # the ordinary Bures clock cannot starve phase-geometry hearing.
            available_pulses = self._available_audible_pulses()
            geodesic_waiting = any(
                int(clock.pulses) > 0 for clock in temporal.geodesic_site_clocks
            )
            temporal_limit = (
                (available_pulses + 1) // 2 if geodesic_waiting else available_pulses
            )
            temporal_records = self._bounded_pulse_records(
                temporal.site_clocks,
                cursor_name="_temporal_site_cursor",
                limit=temporal_limit,
            )
            self._consume_audible_pulses(len(temporal_records))
            for index, record in temporal_records:
                site_clock = temporal.site_clocks[index]
                descriptor = descriptors[index]
                self.client.send_message(
                    f"{self.osc_root}/temporal/pulse",
                    [
                        record, site_clock.site, site_clock.intrinsic_time,
                        site_clock.delta_bures, site_clock.scaled_increment,
                        site_clock.mean_phi, site_clock.mean_pi,
                        site_clock.local_energy, descriptor.x, descriptor.y,
                        descriptor.z, descriptor.purity,
                        descriptor.covariance_correlation,
                        descriptor.entropy_control,
                    ],
                )
            for site_clock, geodesic in zip(
                temporal.site_clocks, temporal.geodesic_site_clocks
            ):
                descriptor = gaussian_harmonic_descriptor(
                    site_clock,
                    mass=parameters.mass,
                    propagation_speed=parameters.propagation_speed,
                    lattice_spacing=parameters.lattice_spacing,
                )
                self.client.send_message(
                    f"{self.osc_root}/geodesic/site",
                    [
                        geodesic.source_revision,
                        geodesic.site,
                        geodesic.record_index,
                        geodesic.intrinsic_length,
                        geodesic.weighted_time,
                        geodesic.delta_bures,
                        geodesic.chord_bures,
                        geodesic.triangle_defect,
                        geodesic.normalized_bending,
                        geodesic.weighted_increment,
                        geodesic.remainder,
                        geodesic.pulses,
                    ],
                )
            geodesic_records = self._bounded_pulse_records(
                temporal.geodesic_site_clocks,
                cursor_name="_geodesic_site_cursor",
                limit=self._available_audible_pulses(),
            )
            self._consume_audible_pulses(len(geodesic_records))
            for index, record in geodesic_records:
                geodesic = temporal.geodesic_site_clocks[index]
                site_clock = temporal.site_clocks[index]
                descriptor = gaussian_harmonic_descriptor(
                    site_clock, mass=parameters.mass,
                    propagation_speed=parameters.propagation_speed,
                    lattice_spacing=parameters.lattice_spacing,
                )
                self.client.send_message(
                    f"{self.osc_root}/geodesic/pulse",
                    [
                        record, geodesic.site, geodesic.intrinsic_length,
                        geodesic.delta_bures, geodesic.weighted_increment,
                        site_clock.mean_phi, site_clock.mean_pi,
                        site_clock.local_energy, descriptor.x, descriptor.y,
                        descriptor.z, descriptor.purity,
                        descriptor.covariance_correlation,
                        descriptor.entropy_control,
                    ],
                )
        return revision


def _install_controls(engine: LiveScalarFieldEngine):
    from pythonosc.dispatcher import Dispatcher

    dispatcher = Dispatcher()

    def apply(address: str, *arguments: Any) -> None:
        try:
            engine.apply_control(address, *arguments)
        except (IndexError, TypeError, ValueError) as exc:
            print(
                f"QFT V{engine._osc_version} control rejected {address}: {exc}",
                flush=True,
            )

    for suffix in (
        "state",
        "localized",
        "mode",
        "alpha",
        "displacement",
        "squeezing",
        "temperature",
        "field",
        "temporal-distance",
        "temporal-mode",
        "clock-scale",
        "geodesic-bending-depth",
        "performance-record",
        "performance-config",
        "running",
        "reset",
        "quit",
    ):
        dispatcher.map(f"{engine.osc_root}/control/{suffix}", apply)
    return dispatcher


def main(
    *,
    default_sites: int = 8,
    osc_version: int = OSC_VERSION,
    default_output_port: int = OUTPUT_PORT,
    default_control_port: int = CONTROL_PORT,
    selectable_sites: tuple[int, ...] | None = None,
    physical_length: float | None = None,
) -> None:
    parser = argparse.ArgumentParser(
        description=f"Live QMW scalar field V{osc_version} ({default_sites} sites)"
    )
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=default_output_port)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=default_control_port)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--monitor-host", default=None)
    parser.add_argument("--monitor-port", type=int, default=None)
    if selectable_sites is not None:
        parser.add_argument(
            "--sites",
            type=int,
            choices=selectable_sites,
            default=default_sites,
            help="lattice resolution at fixed physical length",
        )
    args = parser.parse_args()
    if not math.isfinite(args.rate_hz) or args.rate_hz <= 0.0:
        parser.error("--rate-hz must be finite and positive")

    from pythonosc.osc_server import ThreadingOSCUDPServer

    sites = int(getattr(args, "sites", default_sites))
    lattice_spacing = 1.0
    if physical_length is not None:
        if not math.isfinite(physical_length) or physical_length <= 0:
            parser.error("physical length must be finite and positive")
        lattice_spacing = float(physical_length) / sites
    engine = LiveScalarFieldEngine(
        LiveScalarFieldParameters(
            sites=sites,
            localized_site=sites // 2,
            lattice_spacing=lattice_spacing,
        ),
        osc_version=osc_version,
    )
    publisher = ScalarFieldFramePublisher(
        host=args.output_host, port=args.output_port, osc_version=osc_version
    )
    if args.monitor_port is not None:
        from pythonosc.udp_client import SimpleUDPClient

        monitor = SimpleUDPClient(args.monitor_host or "127.0.0.1", args.monitor_port)
        publisher = ScalarFieldFramePublisher(
            client=_FanoutOSCClient(publisher.client, monitor),
            osc_version=osc_version,
        )
    server = ThreadingOSCUDPServer(
        (args.control_host, args.control_port), _install_controls(engine)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    period = 1.0 / args.rate_hz
    previous = time.monotonic()
    print(
        f"QMW scalar field V{osc_version} ({sites} sites, "
        f"a={lattice_spacing:g}): "
        f"frames -> {args.output_host}:{args.output_port}; "
        f"controls <- {args.control_host}:{args.control_port}",
        flush=True,
    )
    try:
        while not engine.should_quit:
            started = time.monotonic()
            dt = started - previous
            previous = started
            frame, parameters = engine.step(dt)
            publisher.publish(
                frame,
                parameters,
                engine.temporal_frame,
                engine.temporal_config,
            )
            performance_artifact = engine.consume_performance_artifact()
            if performance_artifact is not None:
                publisher.publish_performance_saved(performance_artifact)
            time.sleep(max(0.0, period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
