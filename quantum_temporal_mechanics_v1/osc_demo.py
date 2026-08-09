#!/usr/bin/env python3
"""Continuously scan a relational history and publish it to Max over OSC."""

from __future__ import annotations

import argparse
import math
import time

import numpy as np

from .core import FiniteQuantumClock, QuantumTemporalMechanics, build_history_state, density_matrix
from .osc_output import TemporalMechanicsOSCPublisher


def build_experiment(ticks: int):
    clock = FiniteQuantumClock(ticks, period=math.tau)
    hamiltonian = np.diag([0.0, 1.0])
    plus = np.array([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    quarter = np.array([1.0, -1j], dtype=np.complex128) / math.sqrt(2.0)
    mechanics = QuantumTemporalMechanics(clock, build_history_state(clock, plus, hamiltonian))
    first_effect = density_matrix(plus)
    second_effect = density_matrix(quarter)
    first = mechanics.event_time(first_effect, "phase_zero")
    second = mechanics.event_time(second_effect, "quarter_turn")
    return (
        mechanics,
        ((first_effect, first), (second_effect, second)),
        mechanics.duration(first, second),
        mechanics.diagnostics(hamiltonian),
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Stream quantum temporal mechanics to Max")
    result.add_argument("--host", default="127.0.0.1")
    result.add_argument("--port", type=int, default=7443)
    result.add_argument("--ticks", type=int, default=16)
    result.add_argument("--hz", type=float, default=8.0)
    result.add_argument("--cycles", type=int, default=0, help="0 runs until Ctrl-C")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.hz <= 0:
        raise SystemExit("--hz must be positive")
    mechanics, events, duration, diagnostics = build_experiment(args.ticks)
    publisher = TemporalMechanicsOSCPublisher(args.host, args.port)
    total_frames = None if args.cycles == 0 else args.cycles * args.ticks
    frame = 0
    deadline = time.monotonic()
    print(
        f"QTM v1 -> osc://{args.host}:{args.port} at {args.hz:g} Hz "
        f"({args.ticks} readings; Ctrl-C to stop)",
        flush=True,
    )
    try:
        while total_frames is None or frame < total_frames:
            publisher.publish_frame(frame, mechanics, frame % args.ticks, events, duration, diagnostics)
            frame += 1
            deadline += 1.0 / args.hz
            time.sleep(max(0.0, deadline - time.monotonic()))
    except KeyboardInterrupt:
        pass
    print(f"Stopped after {frame} frames", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
