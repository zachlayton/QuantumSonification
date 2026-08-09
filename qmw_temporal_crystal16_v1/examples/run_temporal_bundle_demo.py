#!/usr/bin/env python3
"""Run the QMW temporal bundle without OSC or MLX dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qmw_debruijn_clock4_v1 import DeBruijnClock4
from qmw_floquet_time_crystal16_v1 import (
    FloquetIsingConfig,
    FloquetTimeCrystal16,
)
from qmw_lfsr_clock4_v1 import LFSRClock4
from qmw_subharmonic_pythagorean_quantum_time_v1 import (
    SubharmonicPythagoreanClock,
    combined_return_ticks,
    pythagorean_comma,
    pythagorean_comma_cents,
)
from qmw_temporal_engine16_v1 import FloquetEvolver, TemporalEngine16


def json_ready(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return f"{value.numerator}/{value.denominator}"
    return value


def run_demo(periods: int, pulse_error: float) -> dict[str, Any]:
    lfsr = LFSRClock4(seed=1)
    debruijn = DeBruijnClock4()
    spqt = SubharmonicPythagoreanClock(include_lfsr_period=15)

    floquet = FloquetTimeCrystal16(
        FloquetIsingConfig(pulse_error=float(pulse_error))
    )
    floquet_report = floquet.report(periods=periods)
    rigidity = floquet.rigidity_sweep(
        (-0.10, -0.05, 0.0, 0.05, 0.10),
        periods=periods,
    )

    engine = TemporalEngine16(
        floquet.product_density(0),
        evolver=FloquetEvolver(floquet),
        dt=1.0,
        lfsr_clock=lfsr,
        spqt_clock=spqt,
        history_capacity=max(240, periods + 1),
    )
    frames = engine.run(periods)
    aion = engine.aion_order_summary(
        floquet.magnetization_operator,
        target_frequency=0.5,
    )

    return {
        "bundle": "qmw_temporal_crystal16_v1",
        "canonical_density_shape": [16, 16],
        "lfsr": lfsr.structural_report(),
        "lfsr_nonzero_orbit": list(lfsr.orbit()),
        "debruijn16_orbit": list(debruijn.orbit),
        "score_lfsr_return_ticks": combined_return_ticks(16, 15),
        "spqt_macrocycle_with_default_ratios_and_lfsr": spqt.macrocycle_length,
        "pythagorean_comma": str(pythagorean_comma()),
        "pythagorean_comma_cents": pythagorean_comma_cents(),
        "floquet": floquet_report,
        "rigidity_sweep": rigidity,
        "engine": {
            "revision": engine.state.revision,
            "history_frames": len(engine.history),
            "last_protocol": frames[-1].protocol,
            "aion": aion,
        },
        "claim_boundary": {
            "lfsr": "programmed finite-state recurrence",
            "spqt": "programmed rational phase geometry",
            "floquet": floquet.scientific_status,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--periods", type=int, default=64)
    parser.add_argument("--pulse-error", type=float, default=0.03)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    report = json_ready(run_demo(args.periods, args.pulse_error))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.json is not None:
        args.json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
