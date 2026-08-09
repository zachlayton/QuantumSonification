#!/usr/bin/env python3
"""Live OSC bridge for emergent_geometry_engine_v1.

Control input defaults to UDP 7430; descriptor output defaults to UDP 7431.
All OSC callbacks enqueue commands so MLX arrays are mutated only on the
simulation thread.
"""

from __future__ import annotations

import argparse
import queue
import signal
import threading
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import mlx.core as mx
import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

if __package__:
    from .emergent_geometry_engine_v1 import (
        EmergentGeometryEngine,
        GeometryParameters,
        PRESETS,
    )
else:  # Direct-script compatibility.
    from emergent_geometry_engine_v1 import (
        EmergentGeometryEngine,
        GeometryParameters,
        PRESETS,
    )


class EmergentGeometryOSC:
    def __init__(
        self,
        host: str,
        control_port: int,
        out_host: str,
        out_port: int,
        size: int,
        preset: str,
        seed: int,
        rate: float,
        iterations: int,
        output_dir: Path,
    ) -> None:
        self.host = host
        self.control_port = control_port
        self.out_host = out_host
        self.out_port = out_port
        self.size = size
        self.preset_name = preset
        self.seed = seed
        self.rate = max(0.1, rate)
        self.iterations = max(1, iterations)
        self.output_dir = output_dir
        self.geometry_parameters = GeometryParameters()

        self.engine = self._make_engine(PRESETS[preset])
        self.client = SimpleUDPClient(out_host, out_port)
        self.commands: queue.SimpleQueue[tuple[str, tuple[Any, ...]]] = queue.SimpleQueue()
        self.alive = True
        self.enabled = True
        self.frame = 0

        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._enqueue)
        self.server = ThreadingOSCUDPServer((host, control_port), dispatcher)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )

    def _make_engine(self, morphogen: Any) -> EmergentGeometryEngine:
        return EmergentGeometryEngine(
            size=self.size,
            morphogen=morphogen,
            geometry=self.geometry_parameters,
            seed=self.seed,
            seed_count=14,
            seed_radius=4,
        )

    def _enqueue(self, address: str, *args: Any) -> None:
        self.commands.put((address, tuple(args)))

    @staticmethod
    def _number(args: tuple[Any, ...], name: str) -> float:
        if not args:
            raise ValueError(f"{name} requires a value")
        return float(args[0])

    def _set_morphogen(self, name: str, value: float) -> None:
        if name in {"feed", "kill"} and not 0.0 <= value <= 0.2:
            raise ValueError(f"{name} must be between 0 and 0.2")
        if name in {"diffusion_u", "diffusion_v", "dt"} and value <= 0:
            raise ValueError(f"{name} must be positive")
        self.engine.field.parameters = replace(
            self.engine.field.parameters, **{name: value}
        )

    def _set_geometry(self, name: str, value: float) -> None:
        if name == "smoothing":
            value = float(np.clip(value, 0.0, 0.999))
        self.geometry_parameters = replace(
            self.engine.surface.parameters, **{name: value}
        )
        self.engine.surface.parameters = self.geometry_parameters

    def _reset(self, use_preset: bool = False) -> None:
        morphogen = (
            PRESETS[self.preset_name]
            if use_preset
            else self.engine.field.parameters
        )
        self.engine = self._make_engine(morphogen)
        self.frame = 0

    def _perturb(self, args: tuple[Any, ...]) -> None:
        if len(args) < 4:
            raise ValueError("perturb requires x y radius amount")

        x = float(np.clip(float(args[0]), 0.0, 1.0))
        y = float(np.clip(float(args[1]), 0.0, 1.0))
        radius = float(np.clip(float(args[2]), 0.002, 0.5)) * self.size
        amount = float(np.clip(float(args[3]), -1.0, 1.0))

        u = np.asarray(self.engine.field.u, dtype=np.float32)
        v = np.asarray(self.engine.field.v, dtype=np.float32)
        yy, xx = np.ogrid[: self.size, : self.size]
        cx, cy = x * (self.size - 1), y * (self.size - 1)
        sigma = max(1.0, radius * 0.45)
        env = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma**2))
        env = env.astype(np.float32)

        v = np.clip(v + amount * env, 0.0, 1.0)
        u = np.clip(u - 0.55 * amount * env, 0.0, 1.0)
        self.engine.field.u = mx.array(u)
        self.engine.field.v = mx.array(v)
        mx.eval(self.engine.field.u, self.engine.field.v)
        self.engine.surface.update_from_fields(
            self.engine.field.u, self.engine.field.v
        )

    @staticmethod
    def _safe_name(raw: str) -> str:
        name = "".join(c for c in raw if c.isalnum() or c in "-_")
        return name or "emergent_geometry_export"

    def _export(self, args: tuple[Any, ...]) -> None:
        name = self._safe_name(str(args[0])) if args else (
            f"emergent_geometry_step_{self.engine.step_count}"
        )
        prefix = self.output_dir / name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine.save_state(prefix.with_suffix(".npz"))
        self.engine.save_descriptors(prefix.with_suffix(".json"))
        self.engine.surface.export_obj(prefix.with_suffix(".obj"))
        self.engine.save_pngs(prefix)
        self.client.send_message("/emergent/state/exported", str(prefix))
        print(f"exported {prefix}")

    def _process(self, address: str, args: tuple[Any, ...]) -> None:
        prefix = "/emergent/control/"
        if not address.startswith(prefix):
            return
        command = address[len(prefix):]

        if command == "run":
            self.enabled = bool(float(args[0])) if args else True
        elif command == "rate":
            self.rate = max(0.1, self._number(args, command))
        elif command == "iterations":
            self.iterations = max(1, int(self._number(args, command)))
        elif command in {"feed", "kill", "diffusion_u", "diffusion_v", "dt"}:
            self._set_morphogen(command, self._number(args, command))
        elif command in {"growth_gain", "edge_gain", "smoothing"}:
            self._set_geometry(command, self._number(args, command))
        elif command == "preset":
            if not args or str(args[0]) not in PRESETS:
                raise ValueError(f"preset must be one of: {', '.join(sorted(PRESETS))}")
            self.preset_name = str(args[0])
            self._reset(use_preset=True)
        elif command == "seed":
            self.seed = int(self._number(args, command))
            self._reset()
        elif command == "reset":
            self._reset()
        elif command == "perturb":
            self._perturb(args)
        elif command == "export":
            self._export(args)
        elif command == "status":
            self.send_all()
        elif command == "quit":
            self.alive = False
        else:
            raise ValueError(f"unknown OSC command: {address}")

        self.send_state()

    def drain_commands(self) -> None:
        while True:
            try:
                address, args = self.commands.get_nowait()
            except queue.Empty:
                break
            try:
                self._process(address, args)
            except (TypeError, ValueError) as exc:
                print(f"OSC error: {exc}")
                self.client.send_message("/emergent/error", str(exc))

    def send_state(self) -> None:
        p = self.engine.field.parameters
        values = {
            "/emergent/state/running": int(self.enabled),
            "/emergent/state/preset": self.preset_name,
            "/emergent/state/feed": p.feed,
            "/emergent/state/kill": p.kill,
            "/emergent/state/rate": self.rate,
            "/emergent/state/iterations": self.iterations,
            "/emergent/state/step": self.engine.step_count,
            "/emergent/state/frame": self.frame,
        }
        for address, value in values.items():
            self.client.send_message(address, value)

    def send_descriptors(self) -> None:
        d = self.engine.descriptors()
        values = {
            "/emergent/geometry/surface_area": d["surface_area"],
            "/emergent/geometry/mean_height": d["mean_height"],
            "/emergent/geometry/height_variance": d["height_variance"],
            "/emergent/geometry/mean_curvature": d["mean_abs_curvature"],
            "/emergent/geometry/curvature_variance": d["curvature_variance"],
            "/emergent/geometry/pattern_entropy": d["pattern_entropy"],
            "/emergent/geometry/anisotropy": d["anisotropy"],
            "/emergent/geometry/growth_velocity": d["growth_velocity"],
            "/emergent/morphogen/u/mean": d["morphogen_u_mean"],
            "/emergent/morphogen/v/mean": d["morphogen_v_mean"],
            "/emergent/morphogen/v/max": d["morphogen_v_max"],
            "/emergent/state/step": d["step"],
            "/emergent/state/frame": self.frame,
        }
        for address, value in values.items():
            self.client.send_message(address, value)

    def send_all(self) -> None:
        self.send_state()
        self.send_descriptors()

    def run(self) -> None:
        self.server_thread.start()
        self.send_state()
        print("Emergent Geometry OSC Bridge v1")
        print(f"  input:  udp://{self.host}:{self.control_port}")
        print(f"  output: udp://{self.out_host}:{self.out_port}")
        print(f"  preset: {self.preset_name}")
        print(f"  field:  {self.size} x {self.size}")
        print(f"  rate:   {self.rate} Hz, {self.iterations} iterations/update")

        next_tick = time.perf_counter()
        try:
            while self.alive:
                self.drain_commands()
                if self.enabled:
                    self.engine.step(self.iterations)
                    self.frame += 1
                    self.send_descriptors()

                next_tick += 1.0 / self.rate
                delay = next_tick - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_tick = time.perf_counter()
        finally:
            self.server.shutdown()
            self.server.server_close()
            print("Emergent Geometry OSC Bridge stopped.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7430)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7431)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="labyrinth")
    parser.add_argument("--size", type=int, default=192)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--rate", type=float, default=20.0)
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/emergent_geometry_live"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    bridge = EmergentGeometryOSC(
        host=args.host,
        control_port=args.control_port,
        out_host=args.out_host,
        out_port=args.out_port,
        size=args.size,
        preset=args.preset,
        seed=args.seed,
        rate=args.rate,
        iterations=args.iterations,
        output_dir=args.output_dir,
    )

    def stop(_signum: int, _frame: Any) -> None:
        bridge.alive = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    bridge.run()


if __name__ == "__main__":
    main()
