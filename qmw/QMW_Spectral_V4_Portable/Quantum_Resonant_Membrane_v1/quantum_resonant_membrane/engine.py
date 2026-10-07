"""Runnable backend joining density, terrain, flow, membrane, and OSC."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import queue
import signal
import threading
import time
from typing import Any

from .interference_timbre import InterferenceTimbrePolicy

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from .density_engine import DensityMatrixEngine
from .flow import QuantumMembraneFlow
from .geometry import build_icosphere_geometry
from .membrane import ResonantMembrane
from .osc import DEFAULT_CONTROL_PORT, DEFAULT_DATA_PORT, MembraneOSCPublisher, ROOT
from .temporal import BuresTemporalObserver
from .terrain import DensityTerrain


@dataclass(frozen=True)
class EngineFrame:
    density: Any
    temporal: Any
    terrain: Any
    flow: Any
    membrane: Any
    interference_control: Any
    reset_epoch: int = 0


class QuantumResonantMembraneEngine:
    """In-process engine, useful both to the CLI and to scientific tests."""

    def __init__(self, *, modes: int = 20, crossing_threshold: float = 0.003) -> None:
        self.density_engine = DensityMatrixEngine()
        self.temporal = BuresTemporalObserver()
        self.geometry = build_icosphere_geometry(subdivisions=1, modes=modes)
        self.terrain = DensityTerrain()
        self.flow = QuantumMembraneFlow(threshold=crossing_threshold)
        self.membrane = ResonantMembrane(self.geometry)
        # Neutral by default: this is an opt-in downstream timbre mapping, not
        # a change to the density/geometry/membrane authority chain.
        self.interference_policy = InterferenceTimbrePolicy(
            phase_spread_radians=0.45,
            depth=0.0,
        )
        self.reset_epoch = 0

    def set_interference_timbre(
        self,
        *,
        phase_offset_radians: float | None = None,
        phase_spread_radians: float | None = None,
        depth: float | None = None,
        slew_seconds: float | None = None,
        source_kind: str | None = None,
        coherence_row: int | None = None,
        coherence_column: int | None = None,
    ) -> None:
        """Commit a downstream timbre policy without touching physical state."""
        current = self.interference_policy
        self.interference_policy = replace(
            current,
            revision=current.revision + 1,
            phase_offset_radians=(current.phase_offset_radians
                if phase_offset_radians is None else float(phase_offset_radians)),
            phase_spread_radians=(current.phase_spread_radians
                if phase_spread_radians is None else float(phase_spread_radians)),
            depth=current.depth if depth is None else float(depth),
            slew_seconds=(current.slew_seconds
                if slew_seconds is None else float(slew_seconds)),
            source_kind=current.source_kind if source_kind is None else str(source_kind),
            coherence_row=current.coherence_row if coherence_row is None else int(coherence_row),
            coherence_column=(current.coherence_column
                if coherence_column is None else int(coherence_column)),
        )

    def reset(self) -> None:
        self.density_engine.reset()
        self.temporal.reset()
        self.terrain.reset()
        self.flow.reset()
        self.membrane.reset()
        self.reset_epoch += 1

    def prepare(self, mode: str) -> None:
        """Select a density preparation and reset all downstream observers."""
        self.density_engine.prepare(mode)
        self.temporal.reset()
        self.terrain.reset()
        self.flow.reset()
        self.membrane.reset()
        self.reset_epoch += 1

    def step(self, dt: float) -> EngineFrame:
        density = self.density_engine.step(dt)
        temporal = self.temporal.observe(density.rho)
        terrain = self.terrain.step(density.rho, time=density.time, dt=dt)
        flow = self.flow.observe(
            density.rho,
            density.hamiltonian,
            self.geometry,
            time=density.time,
            dt=dt,
        )
        membrane = self.membrane.step(terrain, flow, dt=dt)
        interference_control = self.interference_policy.resolve(density.rho)
        return EngineFrame(
            density,
            temporal,
            terrain,
            flow,
            membrane,
            interference_control,
            self.reset_epoch,
        )


class ControlServer:
    """Queue OSC controls so state mutation occurs only on the engine thread."""

    def __init__(self, host: str, port: int) -> None:
        self.commands: queue.SimpleQueue[tuple[str, tuple[object, ...]]] = queue.SimpleQueue()
        dispatcher = Dispatcher()

        def enqueue(address: str, *values: object) -> None:
            self.commands.put((address.rsplit("/", 1)[-1], values))

        dispatcher.map(f"{ROOT}/control/*", enqueue)
        self.server = ThreadingOSCUDPServer((host, port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1.0)


def _first_float(values: tuple[object, ...]) -> float:
    if not values:
        raise ValueError("control requires a value")
    return float(values[0])


def _apply_commands(
    engine: QuantumResonantMembraneEngine,
    controls: ControlServer,
) -> bool:
    running = True
    while True:
        try:
            name, values = controls.commands.get_nowait()
        except queue.Empty:
            break
        try:
            if name == "reset":
                engine.reset()
            elif name == "state":
                if not values:
                    raise ValueError("state control requires a preparation name")
                engine.prepare(str(values[0]))
            elif name == "freeze":
                engine.density_engine.set_config(freeze=bool(_first_float(values)))
            elif name in {
                "coupling",
                "drive",
                "dephasing_rate",
                "damping_rate",
                "depolarizing_rate",
            }:
                engine.density_engine.set_config(**{name: _first_float(values)})
            elif name in {"temporal_distance", "temporal-distance"}:
                engine.temporal.set_distance_per_pulse(_first_float(values))
            elif name in {"clock_scale", "clock-scale"}:
                engine.temporal.set_clock_scale(_first_float(values))
            elif name in {"geodesic_bending_depth", "geodesic-bending-depth"}:
                engine.temporal.set_geodesic_bending_depth(_first_float(values))
            elif name in {"event_threshold", "event-threshold"}:
                engine.flow.set_threshold(_first_float(values))
            elif name in {"interference_phase", "interference-phase"}:
                engine.set_interference_timbre(phase_offset_radians=_first_float(values))
            elif name in {"interference_spread", "interference-spread"}:
                engine.set_interference_timbre(phase_spread_radians=_first_float(values))
            elif name in {"interference_depth", "interference-depth"}:
                engine.set_interference_timbre(depth=_first_float(values))
            elif name in {"interference_slew", "interference-slew"}:
                engine.set_interference_timbre(slew_seconds=_first_float(values))
            elif name in {"interference_source", "interference-source"}:
                if not values:
                    raise ValueError("interference source requires manual or density_coherence")
                engine.set_interference_timbre(source_kind=str(values[0]))
            elif name in {"interference_pair", "interference-pair"}:
                if len(values) != 2:
                    raise ValueError("interference pair requires row and column")
                engine.set_interference_timbre(
                    coherence_row=int(values[0]),
                    coherence_column=int(values[1]),
                )
            elif name == "quit":
                running = False
            else:
                print(f"ignored unknown control: {name}")
        except (TypeError, ValueError) as error:
            print(f"rejected control {name}: {error}")
    return running


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--data-port", type=int, default=DEFAULT_DATA_PORT)
    parser.add_argument("--control-port", type=int, default=DEFAULT_CONTROL_PORT)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--modes", type=int, default=20)
    parser.add_argument("--crossing-threshold", type=float, default=0.003)
    parser.add_argument("--frames", type=int, default=0, help="zero runs until stopped")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.rate_hz <= 0.0:
        raise SystemExit("--rate-hz must be positive")
    engine = QuantumResonantMembraneEngine(
        modes=args.modes, crossing_threshold=args.crossing_threshold
    )
    publisher = MembraneOSCPublisher(SimpleUDPClient(args.host, args.data_port))
    controls = ControlServer(args.host, args.control_port)
    controls.start()
    stop = threading.Event()

    def request_stop(_signum: int, _frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    publisher.publish_geometry(engine.geometry)
    if not args.quiet:
        print(
            "Quantum Resonant Membrane v1 backend ready: "
            f"data udp://{args.host}:{args.data_port}, "
            f"controls udp://{args.host}:{args.control_port}, modes={args.modes}",
            flush=True,
        )
    period = 1.0 / args.rate_hz
    count = 0
    deadline = time.monotonic()
    try:
        running = True
        while running and not stop.is_set() and (args.frames == 0 or count < args.frames):
            running = _apply_commands(engine, controls)
            if not running:
                break
            frame = engine.step(period)
            publisher.publish_frame(
                frame.density,
                frame.temporal,
                frame.terrain,
                frame.flow,
                frame.membrane,
                interference_control=frame.interference_control,
                reset_epoch=frame.reset_epoch,
            )
            count += 1
            deadline += period
            time.sleep(max(0.0, deadline - time.monotonic()))
    finally:
        publisher.publish_unavailable()
        controls.close()
    if not args.quiet:
        print(f"backend stopped after {count} frames", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["EngineFrame", "QuantumResonantMembraneEngine", "main"]
