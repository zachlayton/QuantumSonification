"""Command-line entry point for the local full-four-qubit instrument."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .engine import simulate_tomography
from .osc_service import (
    ServiceConfig,
    TomographyOSCPublisher,
    TomographyOSCService,
    save_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate and publish all 81 four-qubit X/Y/Z settings."
    )
    parser.add_argument("--preset", choices=("bell", "ghz", "weave"), default="ghz")
    parser.add_argument("--transform", choices=("none", "qft", "iqft"), default="none")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7425)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7426)
    parser.add_argument("--packet-delay-ms", type=float, default=2.0)
    parser.add_argument(
        "--save-dir",
        type=Path,
        help="Save every completed run as JSON in this directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="For --once, save the complete JSON dataset to this path.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run, publish, optionally save, and exit instead of serving controls.",
    )
    parser.add_argument(
        "--run-on-start",
        action="store_true",
        help="Also execute the configured run as soon as the service starts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = ServiceConfig(args.preset, args.transform, args.shots, args.seed)
    if args.once:
        result = simulate_tomography(
            preset=args.preset,
            transform=args.transform,
            shots=args.shots,
            seed=args.seed,
        )
        if args.output:
            save_result(result, args.output)
            print(f"Saved {args.output}")
        revision = int(time.time() * 1000) % 2_000_000_000
        TomographyOSCPublisher(
            args.out_host, args.out_port, args.packet_delay_ms
        ).publish(result, revision)
        print(
            f"Published revision {revision}: 81 settings, 255 Pauli terms, "
            f"{result.total_shots} shots"
        )
        return 0

    try:
        service = TomographyOSCService(
            control_host=args.control_host,
            control_port=args.control_port,
            output_host=args.out_host,
            output_port=args.out_port,
            packet_delay_ms=args.packet_delay_ms,
            config=config,
            save_directory=args.save_dir,
        )
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98):
            print(
                f"Cannot open UDP control port {args.control_port}: it is already "
                "in use. Stop the earlier Full4Q service or choose another "
                "--control-port."
            )
            return 2
        raise
    print(f"Full4Q controls: udp://{args.control_host}:{args.control_port}")
    print(f"Full4Q data out: udp://{args.out_host}:{args.out_port}")
    print(
        f"Ready: preset={args.preset} transform={args.transform} "
        f"shots={args.shots} seed={args.seed}"
    )
    if args.run_on_start:
        service.request_run(config)
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Full4Q tomography service")
    finally:
        service.shutdown()
    return 0
