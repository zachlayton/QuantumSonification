"""Registry-driven v4 comparison with explicit stochastic reporting."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .core import (
    DEFAULT_TRANSFORMS,
    RepresentationExperiment,
    SamplingPolicy,
    save_experiment_result,
)
from .protocols import ClassicalShadowTomography, FullPauliTomography
from .transforms import (
    EpistropheBasis,
    FloquetOperator,
    GroverAmplifiedBasis,
    complete_graph_adjacency,
    cycle_graph_adjacency,
    path_graph_adjacency,
    transverse_ising_hamiltonian,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Identity with a registered v4 transform, reporting exact "
            "and sampled Pauli landscapes separately."
        )
    )
    parser.add_argument(
        "--operator",
        choices=DEFAULT_TRANSFORMS.names(),
        default="graph_laplacian",
    )
    parser.add_argument(
        "--protocol",
        choices=("full_pauli", "classical_shadows"),
        default="full_pauli",
    )
    parser.add_argument(
        "--sampling",
        choices=("fixed", "resample", "sequence"),
        default="fixed",
    )
    parser.add_argument(
        "--resample",
        action="store_true",
        help="shortcut for --sampling resample",
    )
    parser.add_argument(
        "--preset",
        choices=("bell", "ghz", "weave"),
        default="ghz",
    )
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument(
        "--graph",
        choices=("cycle", "path", "complete"),
        default="cycle",
    )
    parser.add_argument("--normalized-graph", action="store_true")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--period", type=float, default=1.0)
    parser.add_argument("--marked", default="0")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--list-operators", action="store_true")
    return parser


def _graph_adjacency(name: str, dimension: int = 16):
    return {
        "cycle": cycle_graph_adjacency,
        "path": path_graph_adjacency,
        "complete": complete_graph_adjacency,
    }[name](dimension)


def _create_operator(args: argparse.Namespace):
    if args.operator == "graph_laplacian":
        return DEFAULT_TRANSFORMS.create(
            args.operator,
            adjacency=_graph_adjacency(args.graph),
            normalized=args.normalized_graph,
            graph_name=f"{args.graph}_16",
        )
    if args.operator == "floquet":
        return FloquetOperator.from_hamiltonian(
            transverse_ising_hamiltonian(4),
            period=args.period,
            steps=args.steps,
        )
    if args.operator == "grover_amplified":
        marked = [
            int(value.strip())
            for value in args.marked.split(",")
            if value.strip()
        ]
        return GroverAmplifiedBasis(marked, iterations=args.steps)
    if args.operator == "epistrophe":
        shift = np.roll(np.eye(16, dtype=complex), 1, axis=0)
        return EpistropheBasis(
            shift,
            returns=args.steps,
            definition="cyclic_shift_demo",
        )
    return DEFAULT_TRANSFORMS.create(args.operator)


def _sampling_policy(args: argparse.Namespace) -> SamplingPolicy:
    mode = "resample" if args.resample else args.sampling
    if mode == "resample":
        return SamplingPolicy.resample()
    if mode == "sequence":
        return SamplingPolicy.sequence(args.seed)
    return SamplingPolicy.fixed(args.seed)


def _measurement(args: argparse.Namespace):
    policy = _sampling_policy(args)
    if args.protocol == "classical_shadows":
        return ClassicalShadowTomography(sampling=policy)
    return FullPauliTomography(sampling=policy)


def _print_changes(result, *, top: int) -> None:
    exact = sorted(
        result.observable_comparisons,
        key=lambda item: abs(item.exact_delta),
        reverse=True,
    )
    sampled = sorted(
        result.observable_comparisons,
        key=lambda item: abs(item.estimated_delta),
        reverse=True,
    )
    if top:
        print("Largest exact Pauli-landscape changes:")
        for item in exact[:top]:
            print(
                f"  {item.label}  {item.reference_exact:+.6f} -> "
                f"{item.experimental_exact:+.6f}  "
                f"delta={item.exact_delta:+.6f}"
            )
        print("Largest sampled Pauli-landscape changes:")
        for item in sampled[:top]:
            print(
                f"  {item.label}  {item.reference_estimate:+.6f} -> "
                f"{item.experimental_estimate:+.6f}  "
                f"delta={item.estimated_delta:+.6f}"
            )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.list_operators:
        print("QMW Representation Laboratory v4 operators:")
        for item in DEFAULT_TRANSFORMS.describe():
            parameters = ", ".join(item["parameters"]) or "none"
            print(
                f"  {item['name']:<18} kind={item['kind']:<13} "
                f"parameters={parameters}"
            )
        return 0
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    if args.top < 0:
        raise SystemExit("--top must not be negative")

    operator = _create_operator(args)
    measurement = _measurement(args)
    result = RepresentationExperiment(
        experimental=operator,
        measurement=measurement,
    ).run(
        preset=args.preset,
        shots=args.shots,
        seed=None if measurement.sampling_policy.mode.value == "resample" else args.seed,
    )
    if args.output is not None:
        print(f"Saved {save_experiment_result(result, args.output).resolve()}")

    print(
        f"QMW Representation Laboratory v4: {args.preset} "
        f"identity ↔ {operator.name}"
    )
    print(
        f"Protocol: {result.measurement_protocol['name']} · "
        f"shots={args.shots} ({result.measurement_protocol['shot_semantics']})"
    )
    print(
        f"Sampling: {result.sampling_mode} · resolved seed={result.seed}"
    )
    if operator.name == "graph_laplacian":
        metadata = result.experimental_transform
        print(
            f"Graph: {metadata['graph_name']} · "
            f"{metadata['node_count']} nodes · "
            f"{metadata['edge_count']} edges · "
            f"spectral gap={metadata['spectral_gap']:.6f}"
        )
    metrics = result.comparison_metrics
    print(
        "Exact observable change: "
        f"rms={metrics['observable_delta_rms_exact']:.6f} "
        f"max={metrics['observable_delta_max_abs_exact']:.6f}"
    )
    print(
        "Sampled observable change: "
        f"rms={metrics['observable_delta_rms_estimated']:.6f} "
        f"max={metrics['observable_delta_max_abs_estimated']:.6f}"
    )
    print(
        "Tomography error: "
        f"reference rms={metrics['reference_tomography_error_rms']:.6f} · "
        f"experimental rms="
        f"{metrics['experimental_tomography_error_rms']:.6f}"
    )
    _print_changes(result, top=args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
