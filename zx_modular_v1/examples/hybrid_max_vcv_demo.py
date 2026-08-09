#!/usr/bin/env python3
"""Compile one PennyLane circuit into synchronized Max and VCV host plans."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pennylane as qml

from zx_modular_v1 import compile_hybrid_max_vcv_plan, pennylane_to_modular


def circuit(theta: float) -> None:
    qml.RY(theta, wires=0)
    qml.CNOT(wires=[0, 1])
    qml.RZ(theta / 2.0, wires=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=math.pi / 3.0)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    imported = pennylane_to_modular(
        circuit,
        args.theta,
        name="hybrid_entangled_phase",
    )
    hybrid = compile_hybrid_max_vcv_plan(imported.import_report.diagram)
    summary = {
        "revision": hybrid.revision,
        "semantics_verified": imported.import_report.verified,
        "semantic_modules": len(hybrid.semantic_plan.modules),
        "max_modules": len(hybrid.max_plan.modules),
        "vcv_modules": len(hybrid.vcv_plan.modules),
        "four_channel_wire": ["Re(0)", "Im(0)", "Re(1)", "Im(1)"],
        "authority": hybrid.synchronization["semantic_authority"],
    }
    print(json.dumps(summary, indent=2))
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(hybrid.to_json() + "\n", encoding="utf-8")
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
