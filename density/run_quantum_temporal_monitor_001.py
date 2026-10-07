"""Run and export the QMW driven-qubit monitored-trajectory experiment 001."""

from __future__ import annotations

import argparse
from pathlib import Path

from density.quantum_temporal_monitor_v1 import (
    DrivenQubitExperimentConfig,
    FixedResonator,
    export_driven_qubit_experiment,
    run_driven_qubit_experiment,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a seeded driven-qubit jump trajectory, preserve its event timing, "
            "compute P_N and four factorial cumulants, and export fixed-resonator comparisons."
        )
    )
    parser.add_argument("--output", type=Path, required=True, help="New or existing output directory.")
    parser.add_argument("--duration-s", type=float, default=10.0)
    parser.add_argument("--dt-s", type=float, default=0.0005)
    parser.add_argument("--rabi-hz", type=float, default=3.0)
    parser.add_argument("--decay-rate-hz", type=float, default=4.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--counting-window-s", type=float, default=0.5)
    parser.add_argument("--sample-rate-hz", type=int, default=12_000)
    parser.add_argument("--resonator-frequency-hz", type=float, default=440.0)
    parser.add_argument("--resonator-decay-s", type=float, default=0.35)
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Export event schedules and visualization without rendering WAV files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DrivenQubitExperimentConfig(
        duration_s=args.duration_s,
        dt_s=args.dt_s,
        rabi_hz=args.rabi_hz,
        decay_rate_hz=args.decay_rate_hz,
        seed=args.seed,
        counting_window_s=args.counting_window_s,
    )
    result = run_driven_qubit_experiment(config)
    resonator = FixedResonator(
        frequency_hz=args.resonator_frequency_hz,
        decay_s=args.resonator_decay_s,
        sample_rate_hz=args.sample_rate_hz,
    )
    manifest = export_driven_qubit_experiment(
        result,
        args.output,
        time_scales=(1.0, 10.0, 100.0),
        render_audio=not args.no_audio,
        resonator=resonator,
    )
    print(f"events={len(result.events)}")
    print(f"factorial_cumulants={result.statistics.factorial_cumulants.tolist()}")
    print(f"manifest={manifest}")
    if not args.no_audio:
        print("audio=1x,10x,100x fixed-resonator WAV files; audition not performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
