#!/usr/bin/env python3
"""Build, rewrite, evaluate, and compile a small ZX modular patch."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from zx_modular_v1 import ZXDiagram, compile_modular_plan, fuse_spiders, linear_map


def build_phase_chain() -> ZXDiagram:
    diagram = ZXDiagram("phase_chain")
    diagram.add_boundary("in_0", "input", 0, label="dual-rail input")
    diagram.add_spider("z_alpha", "z", math.pi / 4.0)
    diagram.add_spider("z_beta", "z", math.pi / 3.0)
    diagram.add_boundary("out_0", "output", 0, label="dual-rail output")
    diagram.connect("wire_0", "in_0", "z_alpha")
    diagram.connect("wire_1", "z_alpha", "z_beta")
    diagram.connect("wire_2", "z_beta", "out_0")
    return diagram


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for the compiled modular patch plan",
    )
    args = parser.parse_args()

    original = build_phase_chain()
    report = fuse_spiders(original, "z_alpha", "z_beta")
    compiled = compile_modular_plan(report.diagram)

    summary = {
        "diagram": original.name,
        "before_shape": list(linear_map(original).shape),
        "after_shape": list(linear_map(report.diagram).shape),
        "rewrite": report.rule,
        "semantics_preserved": report.preserved,
        "absolute_error": report.absolute_error,
        "modules_before": len(original.nodes),
        "modules_after": len(report.diagram.nodes),
        "cables_after": len(report.diagram.edges),
        "combined_phase_radians": report.diagram.nodes["z_alpha"].phase,
    }
    print(json.dumps(summary, indent=2))

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(compiled.to_json() + "\n", encoding="utf-8")
        print(f"wrote {args.json_out}")
    else:
        print(compiled.to_json())


if __name__ == "__main__":
    main()
