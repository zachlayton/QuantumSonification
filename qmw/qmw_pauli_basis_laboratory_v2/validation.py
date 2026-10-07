"""Validation and observable comparison for QMW basis operators.

Run from the repository root:

    python -m qmw_pauli_basis_laboratory_v2.validation
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from full4q_tomography_v1 import PAULI_LABELS

from .basis_operator import BasisOperator, validate_density_matrix
from .bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
    transverse_ising_hamiltonian,
)
from .laboratory import density_from_preset, run_basis_laboratory
from .observables import pauli_expectation, pauli_matrix


@dataclass(frozen=True)
class BasisValidation:
    basis: str
    dimension: int
    unitary_error: float
    trace_error: float
    hermitian_error: float
    minimum_eigenvalue: float
    spectrum_error: float
    covariance_error: float
    pullback_error: float
    passed: bool


def validate_basis_operator(
    basis: BasisOperator,
    rho: np.ndarray,
    *,
    tolerance: float = 1e-9,
) -> BasisValidation:
    """Check invariants and both observable-coordinate identities."""
    canonical = validate_density_matrix(rho)
    dimension = canonical.shape[0]
    unitary = basis.checked_unitary(dimension)
    transformed = basis.transform(canonical)
    identity = np.eye(dimension, dtype=complex)

    covariance_errors: list[float] = []
    pullback_errors: list[float] = []
    labels = (
        PAULI_LABELS
        if dimension == 16
        else ("I" * int(np.log2(dimension)),)
    )
    for label in labels:
        observable = pauli_matrix(label)
        canonical_expectation = pauli_expectation(canonical, label)
        covariant = basis.transform_observable(observable)
        covariant_expectation = complex(np.trace(transformed @ covariant))
        covariance_errors.append(
            abs(covariant_expectation - canonical_expectation)
        )

        transformed_expectation = pauli_expectation(transformed, label)
        pulled_back = basis.pullback_observable(observable)
        pulled_back_expectation = complex(np.trace(canonical @ pulled_back))
        pullback_errors.append(
            abs(pulled_back_expectation - transformed_expectation)
        )

    unitary_error = float(
        np.linalg.norm(unitary @ unitary.conj().T - identity)
    )
    trace_error = float(abs(np.trace(transformed) - 1.0))
    hermitian_error = float(
        np.linalg.norm(transformed - transformed.conj().T)
    )
    minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(transformed)))
    spectrum_error = float(
        np.max(
            np.abs(
                np.sort(np.linalg.eigvalsh(canonical))
                - np.sort(np.linalg.eigvalsh(transformed))
            )
        )
    )
    covariance_error = float(max(covariance_errors, default=0.0))
    pullback_error = float(max(pullback_errors, default=0.0))
    passed = (
        unitary_error <= tolerance
        and trace_error <= tolerance
        and hermitian_error <= tolerance
        and minimum_eigenvalue >= -tolerance
        and spectrum_error <= tolerance
        and covariance_error <= tolerance
        and pullback_error <= tolerance
    )
    return BasisValidation(
        basis=basis.name,
        dimension=dimension,
        unitary_error=unitary_error,
        trace_error=trace_error,
        hermitian_error=hermitian_error,
        minimum_eigenvalue=minimum_eigenvalue,
        spectrum_error=spectrum_error,
        covariance_error=covariance_error,
        pullback_error=pullback_error,
        passed=passed,
    )


def initial_basis_operators() -> list[BasisOperator]:
    hamiltonian = transverse_ising_hamiltonian(4)
    return [
        IdentityBasis(),
        HadamardBasis(),
        QFTBasis(),
        HamiltonianEigenbasis(hamiltonian),
    ]


def build_validation_report(
    *,
    preset: str = "ghz",
    shots: int = 1024,
    seed: int = 23,
    operators: list[BasisOperator] | None = None,
) -> dict[str, Any]:
    canonical = density_from_preset(preset)
    selected = initial_basis_operators() if operators is None else operators
    reports: list[dict[str, Any]] = []
    for basis in selected:
        invariant_report = validate_basis_operator(basis, canonical)
        comparison = run_basis_laboratory(
            basis,
            rho=canonical,
            preset=preset,
            shots=shots,
            seed=seed,
        )
        changed = sorted(
            comparison.observable_comparisons,
            key=lambda item: abs(item.exact_delta),
            reverse=True,
        )[:8]
        reports.append(
            {
                "basis": basis.metadata(16),
                "invariants": asdict(invariant_report),
                "tomography": {
                    key: float(value)
                    for key, value in comparison.comparison_metrics.items()
                },
                "largest_observable_changes": [
                    {
                        "label": item.label,
                        "computational": item.computational_exact,
                        "experimental": item.experimental_exact,
                        "delta": item.exact_delta,
                    }
                    for item in changed
                ],
            }
        )
    return {
        "schema": "qmw.pauli_basis_laboratory.validation.v2",
        "preset": preset,
        "shots_per_setting": shots,
        "seed": seed,
        "all_invariants_passed": all(
            report["invariants"]["passed"] for report in reports
        ),
        "reports": reports,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate QMW BasisOperator invariants and compare Full4Q Pauli "
            "observables across representations."
        )
    )
    parser.add_argument(
        "--preset",
        choices=("bell", "ghz", "weave"),
        default="ghz",
    )
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    report = build_validation_report(
        preset=args.preset,
        shots=args.shots,
        seed=args.seed,
    )
    rendered = json.dumps(report, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.output.resolve()}")
    else:
        print(rendered)
    return 0 if report["all_invariants_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
