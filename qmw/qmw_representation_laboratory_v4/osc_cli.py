"""Launch the v4 Hamiltonian preview/commit OSC service."""

from __future__ import annotations

import argparse

from .osc import HamiltonianLiveConfig, HamiltonianOSCService


def _parser(label: str = "v4") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            f"Serve live {label} Hamiltonian transform controls for Max "
            "using the v4 representation engine."
        )
    )
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7445)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7436)
    parser.add_argument("--packet-delay-ms", type=float, default=1.0)
    parser.add_argument("--coupling", type=float, default=0.7)
    parser.add_argument("--transverse-field", type=float, default=0.45)
    parser.add_argument("--longitudinal-field", type=float, default=0.13)
    parser.add_argument("--evolution-time", type=float, default=1.0)
    parser.add_argument(
        "--mode",
        choices=("eigenbasis", "evolution"),
        default="eigenbasis",
    )
    parser.add_argument(
        "--boundary",
        choices=("open", "periodic"),
        default="open",
    )
    parser.add_argument(
        "--preset",
        choices=("bell", "ghz", "weave"),
        default="ghz",
    )
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument(
        "--sampling",
        choices=("fixed", "resample", "sequence"),
        default="fixed",
    )
    parser.add_argument("--seed", type=int, default=23)
    return parser


def main(
    argv: list[str] | None = None,
    *,
    label: str = "v4",
) -> int:
    args = _parser(label).parse_args(argv)
    config = HamiltonianLiveConfig(
        coupling=args.coupling,
        transverse_field=args.transverse_field,
        longitudinal_field=args.longitudinal_field,
        evolution_time=args.evolution_time,
        mode=args.mode,
        boundary=args.boundary,
        preset=args.preset,
        shots=args.shots,
        sampling=args.sampling,
        seed=args.seed,
    ).validate()
    try:
        service = HamiltonianOSCService(
            control_host=args.control_host,
            control_port=args.control_port,
            output_host=args.out_host,
            output_port=args.out_port,
            packet_delay_ms=args.packet_delay_ms,
            config=config,
        )
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98):
            print(
                f"UDP control port {args.control_port} is already in use."
            )
            return 2
        raise
    print(
        f"QMW {label} Hamiltonian controls: "
        f"udp://{args.control_host}:{args.control_port}"
    )
    print(f"QMW {label} output: udp://{args.out_host}:{args.out_port}")
    print(
        "Atomic messages: "
        "/qmw/v4/hamiltonian/preview and "
        "/qmw/v4/hamiltonian/commit"
    )
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print(f"\nStopping QMW {label} Hamiltonian service")
    finally:
        service.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
