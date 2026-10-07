"""Live OSC adapter for the canonical QHO model.

The adapter publishes validated scientific frames. It does not synthesize
audio or place perceptual mappings inside the physics layer.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import math
import threading
import time
from typing import Any

import numpy as np

from .backends.numpy_bosonic import NumPyBosonicBackend
from .evolution import LindbladEnvironment
from .model import OscillatorSpec
from .parseval import observe_qho_parseval
from .schema import OscillatorFrame
from .states import (
    coherent_state,
    fock_state,
    squeezed_vacuum,
    thermal_state,
    vacuum_state,
)


OUTPUT_PORT = 17830
CONTROL_PORT = 17831
SCHEMA = "qmw.qho.osc.v1.2"
STATE_NAMES = ("vacuum", "fock", "coherent", "thermal", "squeezed")


@dataclass(frozen=True)
class LiveQHOParameters:
    state_name: str = "coherent"
    omega: float = 1.0
    fock_level: int = 3
    alpha_real: float = 0.9
    alpha_imag: float = 0.0
    thermal_mean_n: float = 1.5
    squeeze_r: float = 0.55
    squeeze_phase: float = 0.0
    dephasing_rate: float = 0.0
    damping_rate: float = 0.0
    bath_mean_n: float = 0.0


class LiveQHOEngine:
    """Thread-safe state preparation and monotonic model-time owner."""

    def __init__(self, parameters: LiveQHOParameters | None = None) -> None:
        self._lock = threading.RLock()
        self._parameters = parameters or LiveQHOParameters()
        self._model_time = 0.0
        self._running = True
        self._quit = False

    @property
    def should_quit(self) -> bool:
        with self._lock:
            return self._quit

    @property
    def parameters(self) -> LiveQHOParameters:
        with self._lock:
            return self._parameters

    def _initial_state(self, parameters: LiveQHOParameters) -> np.ndarray:
        name = parameters.state_name
        if name == "vacuum":
            return vacuum_state(16)
        if name == "fock":
            return fock_state(parameters.fock_level, 16)
        if name == "coherent":
            return coherent_state(
                parameters.alpha_real + 1j * parameters.alpha_imag,
                16,
            )
        if name == "thermal":
            return thermal_state(parameters.thermal_mean_n, 16)
        if name == "squeezed":
            zeta = parameters.squeeze_r * np.exp(1j * parameters.squeeze_phase)
            return squeezed_vacuum(zeta, 16)
        raise ValueError(f"unsupported state name: {name}")

    def step(self, dt: float) -> tuple[OscillatorFrame, LiveQHOParameters]:
        if not np.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        with self._lock:
            if self._running:
                self._model_time += float(dt)
            parameters = self._parameters
            model_time = self._model_time
            initial = self._initial_state(parameters)
        backend = NumPyBosonicBackend(
            OscillatorSpec(dimension=16, omega=parameters.omega)
        )
        return (
            backend.run(
                initial,
                time=model_time,
                include_rho=True,
                environment=LindbladEnvironment(
                    dephasing_rate=parameters.dephasing_rate,
                    damping_rate=parameters.damping_rate,
                    bath_mean_n=parameters.bath_mean_n,
                ),
            ),
            parameters,
        )

    def apply_control(self, address: str, *arguments: Any) -> None:
        with self._lock:
            parameters = self._parameters
            reset_time = False
            if address == "/qmw/qho/v1/control/prepare":
                if len(arguments) != 7:
                    raise ValueError("prepare requires state, fock, alpha Re/Im, thermal, squeeze r/phase")
                name = str(arguments[0]).lower()
                fock = int(arguments[1])
                real, imag = float(arguments[2]), float(arguments[3])
                thermal = float(arguments[4])
                radius, phase = float(arguments[5]), float(arguments[6])
                if name not in STATE_NAMES:
                    raise ValueError(f"state must be one of {STATE_NAMES}")
                if not 0 <= fock < 16:
                    raise ValueError("fock level must be in [0, 15]")
                if not np.isfinite([real, imag, thermal, radius, phase]).all():
                    raise ValueError("QHO preparation parameters must be finite")
                if thermal < 0.0 or radius < 0.0:
                    raise ValueError("thermal occupation and squeeze radius must be nonnegative")
                parameters = replace(
                    parameters, state_name=name, fock_level=fock,
                    alpha_real=real, alpha_imag=imag, thermal_mean_n=thermal,
                    squeeze_r=radius, squeeze_phase=phase,
                )
                reset_time = True
            elif address == "/qmw/qho/v1/control/state":
                name = str(arguments[0]).lower()
                if name not in STATE_NAMES:
                    raise ValueError(f"state must be one of {STATE_NAMES}")
                parameters = replace(parameters, state_name=name)
                reset_time = True
            elif address == "/qmw/qho/v1/control/fock":
                level = int(arguments[0])
                if not 0 <= level < 16:
                    raise ValueError("fock level must be in [0, 15]")
                parameters = replace(parameters, fock_level=level)
                reset_time = True
            elif address == "/qmw/qho/v1/control/alpha":
                real, imag = float(arguments[0]), float(arguments[1])
                if not np.isfinite([real, imag]).all():
                    raise ValueError("alpha must be finite")
                parameters = replace(parameters, alpha_real=real, alpha_imag=imag)
                reset_time = True
            elif address == "/qmw/qho/v1/control/thermal":
                mean_n = float(arguments[0])
                if not np.isfinite(mean_n) or mean_n < 0.0:
                    raise ValueError("thermal mean n must be finite and nonnegative")
                parameters = replace(parameters, thermal_mean_n=mean_n)
                reset_time = True
            elif address == "/qmw/qho/v1/control/squeeze":
                radius, phase = float(arguments[0]), float(arguments[1])
                if not np.isfinite([radius, phase]).all() or radius < 0.0:
                    raise ValueError("squeeze radius/phase are invalid")
                parameters = replace(
                    parameters,
                    squeeze_r=radius,
                    squeeze_phase=phase,
                )
                reset_time = True
            elif address == "/qmw/qho/v1/control/omega":
                omega = float(arguments[0])
                if not np.isfinite(omega) or omega <= 0.0:
                    raise ValueError("omega must be finite and positive")
                parameters = replace(parameters, omega=omega)
            elif address == "/qmw/qho/v1/control/dephasing":
                rate = float(arguments[0])
                if not np.isfinite(rate) or rate < 0.0:
                    raise ValueError("dephasing rate must be finite and nonnegative")
                parameters = replace(parameters, dephasing_rate=rate)
                reset_time = True
            elif address == "/qmw/qho/v1/control/damping":
                rate = float(arguments[0])
                if not np.isfinite(rate) or rate < 0.0:
                    raise ValueError("damping rate must be finite and nonnegative")
                parameters = replace(parameters, damping_rate=rate)
                reset_time = True
            elif address == "/qmw/qho/v1/control/bath":
                mean_n = float(arguments[0])
                if not np.isfinite(mean_n) or mean_n < 0.0:
                    raise ValueError("bath occupation must be finite and nonnegative")
                parameters = replace(parameters, bath_mean_n=mean_n)
                reset_time = True
            elif address == "/qmw/qho/v1/control/running":
                self._running = bool(int(arguments[0]))
            elif address == "/qmw/qho/v1/control/reset":
                reset_time = True
            elif address == "/qmw/qho/v1/control/quit":
                self._quit = True
            else:
                raise ValueError(f"unsupported OSC control: {address}")
            self._parameters = parameters
            if reset_time:
                self._model_time = 0.0


class QHOFramePublisher:
    """Publish one revisioned, atomic semantic frame."""

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

    @staticmethod
    def _coherence_band(
        rho: np.ndarray,
        distance: int,
    ) -> tuple[list[float], list[float]]:
        values = np.diag(rho, k=distance)
        return (
            np.abs(values).astype(float).tolist(),
            np.angle(values).astype(float).tolist(),
        )

    def publish(self, frame: OscillatorFrame, parameters: LiveQHOParameters) -> int:
        if frame.rho is None:
            raise ValueError("live publication requires a density matrix")
        self.revision += 1
        revision = self.revision
        parseval = observe_qho_parseval(frame)
        magnitude1, phase1 = self._coherence_band(frame.rho, 1)
        magnitude2, phase2 = self._coherence_band(frame.rho, 2)
        self.client.send_message(
            "/qmw/qho/v1/frame/begin",
            [revision, float(frame.time), SCHEMA],
        )
        self.client.send_message(
            "/qmw/qho/v1/populations",
            [revision, *np.asarray(frame.populations, dtype=float).tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v1/coherence/1/magnitude",
            [revision, *magnitude1],
        )
        self.client.send_message(
            "/qmw/qho/v1/coherence/1/phase",
            [revision, *phase1],
        )
        self.client.send_message(
            "/qmw/qho/v1/coherence/2/magnitude",
            [revision, *magnitude2],
        )
        self.client.send_message(
            "/qmw/qho/v1/coherence/2/phase",
            [revision, *phase2],
        )
        self.client.send_message(
            "/qmw/qho/v1/basis/qft/populations",
            [revision, *parseval.probabilities("qft").tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v1/basis/hadamard/populations",
            [revision, *parseval.probabilities("hadamard").tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v1/matrix-spectrum/power",
            [revision, *parseval.matrix_power_bins.tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v1/matrix-spectrum/phase",
            [revision, *parseval.matrix_phase_bins.tolist()],
        )
        self.client.send_message(
            "/qmw/qho/v1/parseval",
            [
                revision, parseval.trace, parseval.purity,
                parseval.matrix_power_sum, parseval.parseval_residual,
            ],
        )
        self.client.send_message(
            "/qmw/qho/v1/observables",
            [
                revision,
                frame.mean_n,
                frame.mean_energy,
                frame.x,
                frame.p,
                frame.var_x,
                frame.var_p,
                frame.purity,
                frame.coherence_l1,
                parameters.omega,
            ],
        )
        self.client.send_message(
            "/qmw/qho/v1/environment",
            [
                revision,
                parameters.dephasing_rate,
                parameters.damping_rate,
                parameters.bath_mean_n,
            ],
        )
        self.client.send_message(
            "/qmw/qho/v1/state",
            [revision, parameters.state_name, parameters.fock_level],
        )
        self.client.send_message(
            "/qmw/qho/v1/parameters",
            [
                revision, parameters.alpha_real, parameters.alpha_imag,
                parameters.thermal_mean_n, parameters.squeeze_r,
                parameters.squeeze_phase, parameters.omega,
            ],
        )
        self.client.send_message("/qmw/qho/v1/frame/end", revision)
        return revision


def _install_controls(engine: LiveQHOEngine):
    from pythonosc.dispatcher import Dispatcher

    dispatcher = Dispatcher()

    def apply(address: str, *arguments: Any) -> None:
        try:
            engine.apply_control(address, *arguments)
        except (IndexError, TypeError, ValueError) as exc:
            print(f"QHO control rejected {address}: {exc}", flush=True)

    for suffix in (
        "state",
        "prepare",
        "fock",
        "alpha",
        "thermal",
        "squeeze",
        "omega",
        "dephasing",
        "damping",
        "bath",
        "running",
        "reset",
        "quit",
    ):
        dispatcher.map(f"/qmw/qho/v1/control/{suffix}", apply)
    return dispatcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Live QMW QHO OSC frame publisher")
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=OUTPUT_PORT)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=CONTROL_PORT)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    args = parser.parse_args()
    if not math.isfinite(args.rate_hz) or args.rate_hz <= 0.0:
        parser.error("--rate-hz must be finite and positive")

    from pythonosc.osc_server import ThreadingOSCUDPServer

    engine = LiveQHOEngine()
    publisher = QHOFramePublisher(host=args.output_host, port=args.output_port)
    server = ThreadingOSCUDPServer(
        (args.control_host, args.control_port),
        _install_controls(engine),
    )
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    period = 1.0 / args.rate_hz
    previous = time.monotonic()
    print(
        f"QMW QHO live model: frames -> {args.output_host}:{args.output_port}; "
        f"controls <- {args.control_host}:{args.control_port}",
        flush=True,
    )
    try:
        while not engine.should_quit:
            started = time.monotonic()
            dt = started - previous
            previous = started
            frame, parameters = engine.step(dt)
            publisher.publish(frame, parameters)
            time.sleep(max(0.0, period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
