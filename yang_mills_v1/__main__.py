"""Run a deterministic field experiment, optionally streaming to Max."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import time

from .engine import SU2Lattice
from .modal import ModalExcitationAdapter
from .osc import UDPClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=4)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--amplitude", type=float, default=0.6)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--dt", type=float, default=0.01, help="model time per integration step")
    parser.add_argument("--substeps", type=int, default=2)
    parser.add_argument("--steps", type=int, default=600, help="0 runs until interrupted")
    parser.add_argument("--coupling", type=float, default=0.5)
    parser.add_argument("--energy-scale", type=float, default=1.0)
    parser.add_argument("--smoothing", type=float, default=0.08, help="model-time seconds")
    parser.add_argument("--motion-scale", type=float, default=1.0)
    parser.add_argument("--osc", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7416)
    parser.add_argument("--fps", type=float, default=30, help="OSC observations per wall-clock second")
    parser.add_argument("--model-rate", type=float, default=1.0, help="model time per wall-clock second")
    parser.add_argument("--json", type=Path, help="new text manifest; existing files are never replaced")
    args = parser.parse_args()
    if (not math.isfinite(args.dt) or args.dt <= 0 or args.steps < 0 or args.substeps < 1
            or not math.isfinite(args.fps) or not 2 <= args.fps <= 120
            or not math.isfinite(args.model_rate) or args.model_rate <= 0
            or not 1 <= args.port <= 65535):
        parser.error("invalid timestep, steps, substeps, fps, model rate or port")
    if args.json and args.json.exists():
        parser.error("manifest exists; choose a new experiment filename")
    try:
        engine = SU2Lattice(args.size, beta=args.beta, amplitude=args.amplitude, seed=args.seed)
        adapter = ModalExcitationAdapter(coupling=args.coupling, energy_scale=args.energy_scale,
            smoothing_seconds=args.smoothing, motion_scale=args.motion_scale)
    except ValueError as error:
        parser.error(str(error))
    client = UDPClient(args.host, args.port) if args.osc else None
    revision = 0
    start = time.monotonic()
    next_observation = 0.0
    peak_drift = peak_gauss = 0.0
    field = engine.snapshot()
    frame = adapter.update(field)
    completed = 0
    try:
        if client:
            client.publish(frame, revision)
            revision += 1
            next_observation = args.model_rate / args.fps
        while args.steps == 0 or completed < args.steps:
            field = engine.step(args.dt, substeps=args.substeps)
            frame = adapter.update(field)
            completed += 1
            peak_drift = max(peak_drift, abs(field.relative_energy_drift))
            peak_gauss = max(peak_gauss, field.gauss_error)
            if client:
                remaining = start + field.time / args.model_rate - time.monotonic()
                if remaining > 0:
                    time.sleep(min(remaining, args.dt / args.model_rate))
                if field.time + 1e-12 >= next_observation:
                    client.publish(frame, revision)
                    revision += 1
                    interval = args.model_rate / args.fps
                    next_observation += (math.floor((field.time - next_observation) / interval) + 1) * interval
    except KeyboardInterrupt:
        pass
    finally:
        if client:
            # Release excitation on a clean stop. The Max receiver also has a
            # watchdog for crashes or lost datagrams.
            from dataclasses import replace
            import numpy as np
            client.publish(replace(frame, magnitudes=np.zeros(16), speeds=np.zeros(16)), revision)
            client.close()
    summary = {"protocol": "classical_su2_2plus1_v1", "parameters": {
        key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
        "completed_steps": completed, "initial_energy": engine.initial_energy,
        "peak_relative_energy_drift": peak_drift, "peak_gauss_error": peak_gauss,
        "final": {key: value for key, value in asdict(field).items()
                  if key not in ("electric_energy", "magnetic_energy", "wilson_trace")}}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        with args.json.open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, allow_nan=False)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
