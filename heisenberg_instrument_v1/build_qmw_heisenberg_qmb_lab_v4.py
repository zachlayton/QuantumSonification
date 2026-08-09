#!/usr/bin/env python3
"""Build the Heisenberg lab with a side-by-side Quantum Matrix Bus adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .build_qmw_heisenberg_clear_lab_v3 import (
        box,
        build as build_v3,
        line,
        validate,
    )
except ImportError:  # Allow direct execution from this directory.
    from build_qmw_heisenberg_clear_lab_v3 import box, build as build_v3, line, validate


ROOT = Path(__file__).resolve().parent


def build() -> dict[str, Any]:
    document = build_v3()
    patcher = document["patcher"]
    patcher["rect"] = [40.0, 30.0, 1660.0, 910.0]
    boxes = patcher["boxes"]
    lines = patcher["lines"]

    for entry in boxes:
        current = entry["box"]
        if current["id"] == "title":
            current["text"] = "QMW HEISENBERG MEASUREMENT LAB v4 — LEGACY AUDIO + QUANTUM MATRIX BUS"

    boxes.extend([
        box("pre_imag", "newobj", [1180., 245., 95., 22.], text="prepend imag", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_phase", "newobj", [1285., 245., 105., 22.], text="prepend phase", numinlets=1, numoutlets=1, outlettype=[""]),
        box("qmb_panel", "panel", [1170., 14., 465., 850.], bgcolor=[0.08, 0.11, 0.14, 1.0], border=2, numinlets=1, numoutlets=0),
        box("qmb_title", "comment", [1190., 28., 420., 28.], text="QUANTUM MATRIX BUS — LIVE COMPATIBILITY PATH", fontsize=15., textcolor=[0.45, 0.86, 1.0, 1.0]),
        box("qmb_note", "comment", [1190., 62., 410., 60.], text="The legacy renderer remains audible. QMB receives the same transactional frame, validates every field, fills an inactive Jitter bank, then commits the complete revision.", textcolor=[0.88, 0.92, 0.95, 1.0]),
        box("qmb_selftest", "message", [1190., 130., 72., 22.], text="selftest", numinlets=2, numoutlets=1, outlettype=[""]),
        box("qmb_selftest_note", "comment", [1275., 132., 325., 20.], text="local 2×2 test; Python engine not required", textcolor=[0.75, 0.8, 0.84, 1.0]),
        box("qmb_adapter", "newobj", [1190., 175., 270., 22.], text="js qmb_heisenberg_adapter_v1.js", numinlets=1, numoutlets=7, outlettype=[""] * 7),
        box("qmb_unpack", "newobj", [1190., 225., 78., 22.], text="jit.unpack 2", numinlets=1, numoutlets=2, outlettype=["jit_matrix", "jit_matrix"]),
        box("qmb_real_label", "comment", [1190., 262., 180., 20.], text="QMB contribution — REAL", textcolor=[0.45, 0.86, 1.0, 1.0]),
        box("qmb_real", "jit.cellblock", [1190., 285., 195., 150.], cols=2, rows=2, colhead=1, rowhead=1, numinlets=2, numoutlets=4, outlettype=[""] * 4),
        box("qmb_imag_label", "comment", [1410., 262., 190., 20.], text="QMB contribution — IMAG", textcolor=[0.45, 0.86, 1.0, 1.0]),
        box("qmb_imag", "jit.cellblock", [1410., 285., 195., 150.], cols=2, rows=2, colhead=1, rowhead=1, numinlets=2, numoutlets=4, outlettype=[""] * 4),
        box("qmb_mag_label", "comment", [1190., 455., 180., 20.], text="QMB magnitude matrix", textcolor=[0.45, 0.86, 1.0, 1.0]),
        box("qmb_mag", "jit.cellblock", [1190., 478., 195., 150.], cols=2, rows=2, colhead=1, rowhead=1, numinlets=2, numoutlets=4, outlettype=[""] * 4),
        box("qmb_commit_label", "comment", [1410., 455., 180., 20.], text="ATOMIC COMMIT", textcolor=[0.45, 0.86, 1.0, 1.0]),
        box("qmb_commit", "message", [1410., 478., 195., 55.], text="waiting for QMB frame...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("qmb_diag", "newobj", [1410., 550., 185., 22.], text="print QMB_HEISENBERG", numinlets=1, numoutlets=0),
        box("qmb_rule", "comment", [1190., 655., 410., 90.], text="COMMIT RULE\nMatrix outlets announce candidate references. The commit outlet fires last. Downstream QMB consumers must react to commit, so a partial or rejected frame can never become active.", textcolor=[0.88, 0.92, 0.95, 1.0]),
        box("qmb_legacy_note", "comment", [1190., 770., 410., 55.], text="Comparison: the original real-contribution cellblock remains at center-left. It and the QMB REAL table should agree for every committed frame.", textcolor=[0.75, 0.8, 0.84, 1.0]),
    ])

    lines.extend([
        line("route_matrix", 3, "pre_imag"),
        line("route_matrix", 5, "pre_phase"),
        line("pre_begin", 0, "qmb_adapter"),
        line("pre_end", 0, "qmb_adapter"),
        line("pre_real", 0, "qmb_adapter"),
        line("pre_imag", 0, "qmb_adapter"),
        line("pre_mag", 0, "qmb_adapter"),
        line("pre_phase", 0, "qmb_adapter"),
        line("pre_freq", 0, "qmb_adapter"),
        line("pre_pan", 0, "qmb_adapter"),
        line("qmb_selftest", 0, "qmb_adapter"),
        line("qmb_adapter", 0, "qmb_unpack"),
        line("qmb_unpack", 0, "qmb_real"),
        line("qmb_unpack", 1, "qmb_imag"),
        line("qmb_adapter", 1, "qmb_mag"),
        line("qmb_adapter", 5, "qmb_commit", 1),
        line("qmb_adapter", 6, "qmb_diag"),
    ])

    patcher["dependency_cache"].append({"name": "qmb_heisenberg_adapter_v1.js", "type": "TEXT"})
    return document


def main() -> int:
    document = build()
    validate(document)
    output = ROOT / "QMW_Heisenberg_Measurement_Lab_v4_QMB.maxpat"
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
