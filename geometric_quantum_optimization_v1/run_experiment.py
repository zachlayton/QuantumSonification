"""Run, export, and optionally replay the three-condition experiment over OSC."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiment import run_comparison
from .osc_publisher import GeometricOptimizationOSCPublisher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spsa-steps", type=int, default=60)
    parser.add_argument("--feedback-steps", type=int, default=60)
    parser.add_argument("--natural-steps", type=int, default=24)
    parser.add_argument("--feedback-mix", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=731)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/geometric_quantum_optimization_v2.json"),
    )
    parser.add_argument("--osc", action="store_true")
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=17430)
    parser.add_argument(
        "--osc-trace",
        choices=("spsa", "acoustic_feedback_spsa", "quantum_natural_gradient", "all"),
        default="all",
    )
    parser.add_argument("--gesture-seconds", type=float, default=0.0)
    parser.add_argument("--step-pause", type=float, default=0.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_comparison(
        steps_spsa=args.spsa_steps,
        steps_feedback=args.feedback_steps,
        steps_natural_gradient=args.natural_steps,
        seed=args.seed,
        layers=args.layers,
        feedback_mix=args.feedback_mix,
    )
    output = result.export_json(args.output)
    for trace in result.traces:
        final = trace.final
        print(
            f"{trace.optimizer:26s} objective={final.objective:.6f} "
            f"approximation={final.approximation_ratio:.6f} "
            f"optimal_mass={final.optimum_probability:.6f} "
            f"geodesic={final.cumulative_geodesic:.6f} "
            f"evaluations={final.model_evaluations}"
        )
    print(f"wrote {output}")
    if args.osc:
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:
            raise SystemExit("python-osc is required for --osc") from exc
        publisher = GeometricOptimizationOSCPublisher(
            SimpleUDPClient(args.osc_host, args.osc_port)
        )
        publisher.publish_problem(result.problem)
        for trace in result.traces:
            if args.osc_trace in ("all", trace.optimizer):
                publisher.publish_trace(
                    trace,
                    gesture_seconds=args.gesture_seconds,
                    step_pause=args.step_pause,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
