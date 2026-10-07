"""Command-line launcher for the live Max Basis Laboratory v3 service."""

from __future__ import annotations

import argparse
from pathlib import Path

from .osc_service import BasisLaboratoryOSCService, BasisServiceConfig


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Serve paired computational/experimental Full4Q tomography "
            "transactions for QMW_Pauli_Basis_Laboratory_v3.maxpat."
        )
    )
    parser.add_argument(
        "--preset",
        choices=("bell", "ghz", "weave"),
        default="ghz",
    )
    parser.add_argument(
        "--basis",
        choices=("identity", "hadamard", "qft", "inverse_qft", "hamiltonian"),
        default="qft",
    )
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7435)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7436)
    parser.add_argument("--packet-delay-ms", type=float, default=2.0)
    parser.add_argument("--save-dir", type=Path)
    parser.add_argument("--run-on-start", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    config = BasisServiceConfig(
        preset=args.preset,
        basis=args.basis,
        shots=args.shots,
        seed=args.seed,
    )
    try:
        service = BasisLaboratoryOSCService(
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
                f"Cannot open UDP control port {args.control_port}: it is "
                "already in use. Stop the earlier v3 service or choose "
                "another --control-port."
            )
            return 2
        raise

    print(
        f"QMW Basis v3 controls: udp://{args.control_host}:{args.control_port}"
    )
    print(f"QMW Basis v3 data out: udp://{args.out_host}:{args.out_port}")
    print(
        f"Ready v3: preset={config.preset} basis={config.basis} "
        f"shots={config.shots} seed={config.seed}"
    )
    if args.run_on_start:
        service.request_run(config)
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping QMW Pauli Basis Laboratory v3")
    finally:
        service.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
