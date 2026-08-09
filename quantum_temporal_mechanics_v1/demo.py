#!/usr/bin/env python3
"""Small reproducible experiment for quantum temporal mechanics v1."""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from .core import FiniteQuantumClock, QuantumTemporalMechanics, build_history_state


def run(ticks: int = 16) -> dict:
    clock = FiniteQuantumClock(ticks, period=math.tau)
    hamiltonian = np.diag([0.0, 1.0])
    plus = np.array([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    history = build_history_state(clock, plus, hamiltonian)
    mechanics = QuantumTemporalMechanics(clock, history)

    plus_effect = np.outer(plus, plus.conj())
    minus_i = np.array([1.0, -1j], dtype=np.complex128) / math.sqrt(2.0)
    quarter_turn_effect = np.outer(minus_i, minus_i.conj())
    first = mechanics.event_time(plus_effect, "phase-zero record")
    second = mechanics.event_time(quarter_turn_effect, "quarter-turn record")
    duration = mechanics.duration(first, second)
    diagnostics = mechanics.diagnostics(hamiltonian)
    return {
        "clock": {"ticks": ticks, "period": clock.period, "resolution": clock.resolution},
        "events": [first.to_dict(), second.to_dict()],
        "duration": duration.to_dict(),
        "diagnostics": diagnostics.to_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Operational quantum temporal mechanics demo")
    parser.add_argument("--ticks", type=int, default=16)
    args = parser.parse_args()
    print(json.dumps(run(args.ticks), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
