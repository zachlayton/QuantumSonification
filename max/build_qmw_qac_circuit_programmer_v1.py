#!/usr/bin/env python3
"""Build the native Max QAC/QASM circuit programmer."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
QAC_MAX = PROJECT / "qac_quantumsonification_bridge_v1" / "max"
OUTPUT = ROOT / "QMW_QAC_Circuit_Programmer_v1.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def main() -> int:
    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [80.0, 80.0, 900.0, 600.0],
        "openinpresentation": 1,
        "gridsize": [15.0, 15.0],
        "boxes": [
            box("panel", "panel", [10.0, 10.0, 820.0, 520.0], presentation=1, presentation_rect=[10.0,10.0,820.0,520.0], bgcolor=[0.055,0.075,0.105,1.0]),
            box("title", "comment", [25.0, 18.0, 700.0, 24.0], text="QMW QAC/QASM CIRCUIT PROGRAMMER v1", fontsize=18.0, presentation=1, presentation_rect=[25.0,18.0,700.0,24.0], textcolor=[0.9,0.93,0.97,1.0]),
            box("ui", "jsui", [25.0, 55.0, 780.0, 390.0], filename="qmw_qac_circuit_programmer_v1.js", jsarguments=["qmw_qac_circuit_programmer_v1.js"], presentation=1, presentation_rect=[25.0,55.0,780.0,390.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
            box("status_label", "comment", [25.0, 458.0, 70.0, 20.0], text="STATUS", presentation=1, presentation_rect=[25.0,458.0,70.0,20.0], textcolor=[0.51,0.81,1.0,1.0]),
            box("status", "message", [95.0, 455.0, 520.0, 24.0], text="ready", presentation=1, presentation_rect=[95.0,455.0,520.0,24.0]),
            box("qac", "newobj", [25.0, 490.0, 235.0, 22.0], text="och.microqiskit qc 4 4 sim 1024 1", numinlets=1, numoutlets=2, outlettype=["", ""]),
            box("tee", "newobj", [280.0, 490.0, 40.0, 22.0], text="t l l", numinlets=1, numoutlets=2, outlettype=["", ""]),
            box("sender", "newobj", [340.0, 490.0, 235.0, 22.0], text="qac_quantumsonification_sender_v1", numinlets=1, numoutlets=1, outlettype=[""]),
            box("qac_print", "newobj", [590.0, 490.0, 95.0, 22.0], text="print QAC_OUT", numinlets=1, numoutlets=0),
            box("tx_print", "newobj", [700.0, 490.0, 136.0, 22.0], text="print QAC_BRIDGE_TX", numinlets=1, numoutlets=0),
        ],
        "lines": [
            line("ui",0,"qac"), line("ui",1,"status"), line("qac",0,"tee"),
            line("tee",1,"qac_print"), line("tee",0,"sender"), line("sender",0,"tx_print"),
        ],
        "dependency_cache": [
            {"name":"qmw_qac_circuit_programmer_v1.js","bootpath":str(ROOT),"patcherrelativepath":".","type":"TEXT","implicit":1},
            {"name":"qac_quantumsonification_sender_v1.maxpat","bootpath":str(ROOT),"patcherrelativepath":".","type":"JSON","implicit":1},
            {"name":"qac_qasm_sender_v1.js","bootpath":str(ROOT),"patcherrelativepath":".","type":"TEXT","implicit":1},
        ],
    }
    OUTPUT.write_text(json.dumps({"patcher": patcher}, indent=4) + "\n", encoding="utf-8")
    (ROOT / "qac_quantumsonification_sender_v1.maxpat").write_text(
        (QAC_MAX / "qac_quantumsonification_sender_v1.maxpat").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (ROOT / "qac_qasm_sender_v1.js").write_text(
        (QAC_MAX / "qac_qasm_sender_v1.js").read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(f"Built {OUTPUT.name} with colocated QAC sender dependencies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
