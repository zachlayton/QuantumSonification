#!/usr/bin/env python3
"""PennyLane circuit -> PyZX graph -> QMW modular plan demonstration."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pennylane as qml

from zx_modular_v1 import pennylane_to_modular


def bell_phase_circuit(theta: float) -> None:
    qml.Hadamard(0)
    qml.CNOT(wires=[0, 1])
    qml.RZ(theta, wires=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=math.pi / 3.0)
    parser.add_argument("--simplify", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    result = pennylane_to_modular(
        bell_phase_circuit,
        args.theta,
        name="pennylane_bell_phase",
        simplify=args.simplify,
    )
    report = result.import_report
    summary = {
        "pennylane_version": qml.__version__,
        "pyzx_vertices_before": result.vertices_before_simplification,
        "pyzx_vertices_after": result.vertices_after_simplification,
        "zx_semantics_verified": report.verified,
        "absolute_error": report.absolute_error,
        "input_wire_to_qmw_boundary": report.input_wire_to_boundary,
        "output_wire_to_qmw_boundary": report.output_wire_to_boundary,
        "rack_modules": len(result.patch_plan.modules),
        "rack_cables": len(result.patch_plan.cables),
        "global_scalar": {
            "real": report.diagram.scalar.real,
            "imag": report.diagram.scalar.imag,
        },
    }
    print(json.dumps(summary, indent=2))

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            result.patch_plan.to_json() + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
