"""Revisioned OSC observer stream for the coupled-oscillator V2 model.

This module publishes scientific frames only. It contains no synthesis or
perceptual mapping.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import math
import threading
import time
from typing import Any

import numpy as np

from .backends.numpy_coupled import NumPyCoupledOscillatorBackend
from .coupled_model import CoupledOscillatorSpec
from .coupled_schema import CoupledOscillatorFrame
from .coupled_states import product_coherent_state, product_fock_state
from .geodesic_clock import BuresGeodesicClock, GeodesicClockReading
from quantum_temporal_mechanics_v1.density_clock import (
    DensityClockReading,
    DensityMatrixClock,
)


OUTPUT_PORT = 17840
CONTROL_PORT = 17841
SCHEMA = "qmw.qho.coupled.osc.v2.1"
STATE_NAMES = ("single_a", "single_b", "fock_product", "coherent_product")


@dataclass(frozen=True)
class LiveCoupledParameters:
    state_name: str = "single_a"
    dimension_a: int = 4
    dimension_b: int = 4
    omega_a: float = 1.0
    omega_b: float = 1.0
    coupling: float = 0.2
    fock_a: int = 1
    fock_b: int = 0
    alpha_a_real: float = 0.8
    alpha_a_imag: float = 0.0
    alpha_b_real: float = 0.0
    alpha_b_imag: float = 0.0

    def oscillator_spec(self) -> CoupledOscillatorSpec:
        return CoupledOscillatorSpec(
            dimension_a=self.dimension_a,
            dimension_b=self.dimension_b,
            omega_a=self.omega_a,
            omega_b=self.omega_b,
            coupling=self.coupling,
        )


class LiveCoupledEngine:
    """Thread-safe owner of one prepared state and its model time."""

    def __init__(self, parameters: LiveCoupledParameters | None = None) -> None:
        self._lock = threading.RLock()
        self._parameters = parameters or LiveCoupledParameters()
        self._model_time = 0.0
        self._running = True
        self._quit = False
        self._temporal_distance = 0.025
        self._temporal_mode = "poisson"
        self._coherence_depth = 0.35
        self._temporal_clock = self._new_temporal_clock()
        self._temporal_reading: DensityClockReading | None = None
        self._geodesic_distance = 0.025
        self._geodesic_bending_depth = 1.0
        self._geodesic_clock_scale = 1.0
        self._geodesic_mode = "fixed"
        self._geodesic_clock = self._new_geodesic_clock()
        self._geodesic_reading: GeodesicClockReading | None = None
        self._source_revision = 0

    def _new_temporal_clock(self) -> DensityMatrixClock:
        return DensityMatrixClock(
            distance_per_pulse=self._temporal_distance,
            mode=self._temporal_mode,
            seed=23,
            coherence_depth=self._coherence_depth,
        )

    def _reset_temporal_clock(self) -> None:
        self._temporal_clock = self._new_temporal_clock()
        self._temporal_reading = None
        self._geodesic_clock = self._new_geodesic_clock()
        self._geodesic_reading = None
        self._source_revision = 0

    def _new_geodesic_clock(self) -> BuresGeodesicClock:
        return BuresGeodesicClock(
            distance_per_pulse=self._geodesic_distance,
            bending_depth=self._geodesic_bending_depth,
            clock_scale=self._geodesic_clock_scale,
            mode=self._geodesic_mode,
            seed=23,
        )

    @property
    def should_quit(self) -> bool:
        with self._lock:
            return self._quit

    @property
    def parameters(self) -> LiveCoupledParameters:
        with self._lock:
            return self._parameters

    @property
    def temporal_reading(self) -> DensityClockReading | None:
        with self._lock:
            return self._temporal_reading

    @property
    def geodesic_reading(self) -> GeodesicClockReading | None:
        with self._lock:
            return self._geodesic_reading

    @property
    def temporal_config(self) -> dict[str, float | str]:
        with self._lock:
            return {
                "distance_per_pulse": self._temporal_distance,
                "mode": self._temporal_mode,
                "coherence_depth": self._coherence_depth,
            }

    @property
    def geodesic_config(self) -> dict[str, float | str]:
        with self._lock:
            return {
                "distance_per_pulse": self._geodesic_distance,
                "bending_depth": self._geodesic_bending_depth,
                "clock_scale": self._geodesic_clock_scale,
                "mode": self._geodesic_mode,
                "normalization": "triangle_defect_over_two_segment_length_squared",
            }

    @staticmethod
    def _initial_state(parameters: LiveCoupledParameters) -> np.ndarray:
        dimensions = (parameters.dimension_a, parameters.dimension_b)
        if parameters.state_name == "single_a":
            return product_fock_state(1, 0, *dimensions)
        if parameters.state_name == "single_b":
            return product_fock_state(0, 1, *dimensions)
        if parameters.state_name == "fock_product":
            return product_fock_state(
                parameters.fock_a, parameters.fock_b, *dimensions
            )
        if parameters.state_name == "coherent_product":
            return product_coherent_state(
                parameters.alpha_a_real + 1j * parameters.alpha_a_imag,
                parameters.alpha_b_real + 1j * parameters.alpha_b_imag,
                *dimensions,
            )
        raise ValueError(f"unsupported state name: {parameters.state_name}")

    def step(self, dt: float) -> tuple[CoupledOscillatorFrame, LiveCoupledParameters]:
        if not np.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        with self._lock:
            if self._running:
                self._model_time += float(dt)
            parameters = self._parameters
            model_time = self._model_time
            initial = self._initial_state(parameters)
            backend = NumPyCoupledOscillatorBackend(parameters.oscillator_spec())
            frame = backend.run(initial, time=model_time, include_rho=True)
            if frame.rho is None:
                raise RuntimeError("QMW temporal clock requires the authoritative rho")
            self._temporal_reading = self._temporal_clock.update(
                frame.rho, self._source_revision
            )
            self._geodesic_reading = self._geodesic_clock.update(
                frame.rho, self._source_revision
            )
            self._source_revision += 1
            return frame, parameters

    def apply_control(self, address: str, *arguments: Any) -> None:
        with self._lock:
            parameters = self._parameters
            reset_time = False
            if address == "/qmw/qho/v2/control/state":
                name = str(arguments[0]).lower()
                if name not in STATE_NAMES:
                    raise ValueError(f"state must be one of {STATE_NAMES}")
                parameters = replace(parameters, state_name=name)
                reset_time = True
            elif address == "/qmw/qho/v2/control/fock":
                n_a, n_b = int(arguments[0]), int(arguments[1])
                if not 0 <= n_a < parameters.dimension_a:
                    raise ValueError("mode-a Fock level lies outside its cutoff")
                if not 0 <= n_b < parameters.dimension_b:
                    raise ValueError("mode-b Fock level lies outside its cutoff")
                parameters = replace(parameters, fock_a=n_a, fock_b=n_b)
                reset_time = True
            elif address == "/qmw/qho/v2/control/alpha":
                values = tuple(float(value) for value in arguments[:4])
                if len(values) != 4 or not np.isfinite(values).all():
                    raise ValueError("two complex coherent amplitudes are required")
                parameters = replace(
                    parameters,
                    alpha_a_real=values[0],
                    alpha_a_imag=values[1],
                    alpha_b_real=values[2],
                    alpha_b_imag=values[3],
                )
                reset_time = True
            elif address == "/qmw/qho/v2/control/omega":
                omega_a, omega_b = float(arguments[0]), float(arguments[1])
                if not np.isfinite([omega_a, omega_b]).all() or min(
                    omega_a, omega_b
                ) <= 0.0:
                    raise ValueError("mode frequencies must be finite and positive")
                parameters = replace(
                    parameters, omega_a=omega_a, omega_b=omega_b
                )
                reset_time = True
            elif address == "/qmw/qho/v2/control/coupling":
                coupling = float(arguments[0])
                if not np.isfinite(coupling):
                    raise ValueError("coupling must be finite")
                parameters = replace(parameters, coupling=coupling)
                reset_time = True
            elif address == "/qmw/qho/v2/control/temporal-distance":
                distance = self._temporal_clock.set_distance_per_pulse(
                    float(arguments[0])
                )
                self._temporal_distance = distance
            elif address == "/qmw/qho/v2/control/temporal-mode":
                mode = self._temporal_clock.set_mode(str(arguments[0]))
                self._temporal_mode = mode
            elif address == "/qmw/qho/v2/control/coherence-depth":
                depth = self._temporal_clock.set_coherence_depth(
                    float(arguments[0])
                )
                self._coherence_depth = depth
            elif address == "/qmw/qho/v2/control/geodesic-distance":
                distance = self._geodesic_clock.set_distance_per_pulse(
                    float(arguments[0])
                )
                self._geodesic_distance = distance
            elif address == "/qmw/qho/v2/control/geodesic-bending-depth":
                depth = self._geodesic_clock.set_bending_depth(float(arguments[0]))
                self._geodesic_bending_depth = depth
            elif address == "/qmw/qho/v2/control/geodesic-clock-scale":
                scale = self._geodesic_clock.set_clock_scale(float(arguments[0]))
                self._geodesic_clock_scale = scale
            elif address == "/qmw/qho/v2/control/geodesic-mode":
                mode = self._geodesic_clock.set_mode(str(arguments[0]))
                self._geodesic_mode = mode
            elif address == "/qmw/qho/v2/control/running":
                self._running = bool(int(arguments[0]))
            elif address == "/qmw/qho/v2/control/reset":
                reset_time = True
            elif address == "/qmw/qho/v2/control/quit":
                self._quit = True
            else:
                raise ValueError(f"unsupported OSC control: {address}")
            self._parameters = parameters
            if reset_time:
                self._model_time = 0.0
                self._reset_temporal_clock()


class CoupledFramePublisher:
    """Publish one atomic, revisioned coupled-oscillator frame."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.revision = 0

    def publish(
        self,
        frame: CoupledOscillatorFrame,
        parameters: LiveCoupledParameters,
        temporal: DensityClockReading | None = None,
        geodesic: GeodesicClockReading | None = None,
    ) -> int:
        self.revision += 1
        revision = self.revision
        self.client.send_message(
            "/qmw/qho/v2/frame/begin", [revision, float(frame.time), SCHEMA]
        )
        self.client.send_message(
            "/qmw/qho/v2/populations/joint",
            [revision, *frame.joint_populations.reshape(-1).astype(float).tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v2/populations/a",
            [revision, *frame.populations_a.astype(float).tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v2/populations/b",
            [revision, *frame.populations_b.astype(float).tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v2/observables",
            [
                revision,
                frame.mean_n_a,
                frame.mean_n_b,
                frame.mean_total_n,
                frame.mean_energy,
                float(np.real(frame.exchange_coherence)),
                float(np.imag(frame.exchange_coherence)),
                frame.global_purity,
                frame.local_purity_a,
                frame.local_purity_b,
                frame.reduced_entropy_a,
                frame.reduced_entropy_b,
            ],
        )
        self.client.send_message(
            "/qmw/qho/v2/parameters",
            [
                revision,
                parameters.state_name,
                parameters.omega_a,
                parameters.omega_b,
                parameters.coupling,
                parameters.fock_a,
                parameters.fock_b,
            ],
        )
        self.client.send_message("/qmw/qho/v2/frame/end", revision)
        if temporal is not None:
            self.client.send_message(
                "/qmw/qho/v2/temporal/state",
                [
                    temporal.source_revision,
                    temporal.record_index,
                    temporal.intrinsic_time,
                    temporal.delta_bures,
                    temporal.remainder,
                    temporal.phase,
                    temporal.coherence,
                    temporal.purity,
                    temporal.population_flux,
                    temporal.coherence_flux,
                    temporal.coherence_flux_ema,
                    temporal.coherence_gain,
                    temporal.hazard_increment,
                    temporal.negativity,
                    temporal.projection_error,
                    temporal.next_record_distance,
                    temporal.pulses,
                ],
            )
            first_record = temporal.record_index - temporal.pulses + 1
            for record in range(first_record, temporal.record_index + 1):
                self.client.send_message(
                    "/qmw/qho/v2/temporal/pulse",
                    [
                        record,
                        temporal.intrinsic_time,
                        temporal.delta_bures,
                        temporal.phase,
                        temporal.coherence,
                        temporal.population_flux,
                        temporal.coherence_flux,
                        temporal.purity,
                        temporal.coherence_gain,
                        temporal.hazard_increment,
                    ],
                )
        if geodesic is not None:
            self.client.send_message(
                "/qmw/qho/v2/geodesic/state",
                [
                    geodesic.source_revision,
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
                    geodesic.bending_increment,
                    geodesic.next_record_distance,
                ],
            )
            first_record = geodesic.record_index - geodesic.pulses + 1
            for record in range(first_record, geodesic.record_index + 1):
                self.client.send_message(
                    "/qmw/qho/v2/geodesic/pulse",
                    [
                        record,
                        geodesic.intrinsic_length,
                        geodesic.weighted_time,
                        geodesic.delta_bures,
                        geodesic.triangle_defect,
                        geodesic.normalized_bending,
                    ],
                )
        return revision


def _install_controls(engine: LiveCoupledEngine):
    from pythonosc.dispatcher import Dispatcher

    dispatcher = Dispatcher()

    def apply(address: str, *arguments: Any) -> None:
        try:
            engine.apply_control(address, *arguments)
        except (IndexError, TypeError, ValueError) as exc:
            print(f"QHO V2 control rejected {address}: {exc}", flush=True)

    for suffix in (
        "state",
        "fock",
        "alpha",
        "omega",
        "coupling",
        "temporal-distance",
        "temporal-mode",
        "coherence-depth",
        "geodesic-distance",
        "geodesic-bending-depth",
        "geodesic-clock-scale",
        "geodesic-mode",
        "running",
        "reset",
        "quit",
    ):
        dispatcher.map(f"/qmw/qho/v2/control/{suffix}", apply)
    return dispatcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Live QMW coupled-QHO observer")
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=OUTPUT_PORT)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=CONTROL_PORT)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    args = parser.parse_args()
    if not math.isfinite(args.rate_hz) or args.rate_hz <= 0.0:
        parser.error("--rate-hz must be finite and positive")

    from pythonosc.osc_server import ThreadingOSCUDPServer

    engine = LiveCoupledEngine()
    publisher = CoupledFramePublisher(host=args.output_host, port=args.output_port)
    server = ThreadingOSCUDPServer(
        (args.control_host, args.control_port), _install_controls(engine)
    )
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    period = 1.0 / args.rate_hz
    previous = time.monotonic()
    print(
        f"QMW coupled QHO V2: frames -> {args.output_host}:{args.output_port}; "
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
                engine.temporal_reading,
                engine.geodesic_reading,
            )
            time.sleep(max(0.0, period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
