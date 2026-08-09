"""Launch the registry-driven v5 transform service."""

from __future__ import annotations

import argparse

from .osc_service import (
    TRANSFORM_NAMES,
    RepresentationLiveConfig,
    RepresentationV5OSCService,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve the integrated registry-driven v5 Max laboratory."
    )
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7445)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7436)
    parser.add_argument("--packet-delay-ms", type=float, default=1.0)
    parser.add_argument(
        "--transform",
        choices=TRANSFORM_NAMES,
        default="hamiltonian",
    )
    parser.add_argument("--coupling", type=float, default=0.7)
    parser.add_argument("--transverse-field", type=float, default=0.45)
    parser.add_argument("--longitudinal-field", type=float, default=0.13)
    parser.add_argument("--evolution-time", type=float, default=1.0)
    parser.add_argument("--boundary", choices=("open", "periodic"), default="open")
    parser.add_argument("--preset", choices=("bell", "ghz", "weave"), default="ghz")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument(
        "--sampling",
        choices=("fixed", "resample", "sequence"),
        default="fixed",
    )
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument(
        "--graph",
        choices=("cycle", "path", "complete"),
        default="cycle",
    )
    parser.add_argument("--normalized-graph", action="store_true")
    parser.add_argument("--marked-state", type=int, default=0)
    parser.add_argument("--steps", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = RepresentationLiveConfig(
        transform=args.transform,
        coupling=args.coupling,
        transverse_field=args.transverse_field,
        longitudinal_field=args.longitudinal_field,
        evolution_time=args.evolution_time,
        boundary=args.boundary,
        preset=args.preset,
        shots=args.shots,
        sampling=args.sampling,
        seed=args.seed,
        graph=args.graph,
        normalized_graph=args.normalized_graph,
        marked_state=args.marked_state,
        steps=args.steps,
    ).validate()
    try:
        service = RepresentationV5OSCService(
            control_host=args.control_host,
            control_port=args.control_port,
            output_host=args.out_host,
            output_port=args.out_port,
            packet_delay_ms=args.packet_delay_ms,
            config=config,
        )
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98):
            print(f"UDP control port {args.control_port} is already in use.")
            return 2
        raise
    print(
        f"QMW v5 transform controls: "
        f"udp://{args.control_host}:{args.control_port}"
    )
    print(f"QMW v5 output: udp://{args.out_host}:{args.out_port}")
    print("Registry transforms: identity, hadamard, qft, inverse_qft,")
    print("  hamiltonian, graph_laplacian, floquet, grover_amplified, epistrophe")
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping QMW v5 representation service")
    finally:
        service.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
