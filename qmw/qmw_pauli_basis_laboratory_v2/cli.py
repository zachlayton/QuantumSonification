"""Command-line runner for one Pauli Basis Laboratory comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

from .bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
    transverse_ising_hamiltonian,
)
from .laboratory import run_basis_laboratory, save_laboratory_result


def _basis_from_name(name: str):
    if name == "identity":
        return IdentityBasis()
    if name == "hadamard":
        return HadamardBasis()
    if name == "qft":
        return QFTBasis()
    if name == "hamiltonian":
        return HamiltonianEigenbasis(transverse_ising_hamiltonian(4))
    raise ValueError(f"unknown basis {name!r}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare computational and experimental representations through "
            "the unchanged 81-setting Full4Q tomography pipeline."
        )
    )
    parser.add_argument(
        "--basis",
        choices=("identity", "hadamard", "qft", "hamiltonian"),
        default="qft",
    )
    parser.add_argument(
        "--preset",
        choices=("bell", "ghz", "weave"),
        default="ghz",
    )
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--top", type=int, default=8)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    if args.top < 0:
        raise SystemExit("--top must not be negative")

    basis = _basis_from_name(args.basis)
    result = run_basis_laboratory(
        basis,
        preset=args.preset,
        shots=args.shots,
        seed=args.seed,
    )
    if args.output is not None:
        path = save_laboratory_result(result, args.output)
        print(f"Saved {path.resolve()}")

    print(
        f"QMW Pauli Basis Laboratory v2: {args.preset} "
        f"identity ↔ {basis.name}"
    )
    print(
        f"Each side: 81 settings, 255 variable Pauli terms, "
        f"{81 * args.shots} shots"
    )
    metrics = result.comparison_metrics
    print(
        "Exact observable change: "
        f"rms={metrics['observable_delta_rms_exact']:.6f} "
        f"max={metrics['observable_delta_max_abs_exact']:.6f}"
    )
    print(
        "Experimental tomography error: "
        f"rms={metrics['experimental_tomography_error_rms']:.6f} "
        f"max={metrics['experimental_tomography_error_max_abs']:.6f}"
    )
    changed = sorted(
        result.observable_comparisons,
        key=lambda item: abs(item.exact_delta),
        reverse=True,
    )
    if args.top:
        print("Largest exact Pauli-landscape changes:")
    for item in changed[: args.top]:
        print(
            f"  {item.label}  {item.computational_exact:+.6f} -> "
            f"{item.experimental_exact:+.6f}  "
            f"delta={item.exact_delta:+.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
