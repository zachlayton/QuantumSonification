#!/usr/bin/env python3
"""Build the Max 9 OSC/Jitter evaluator for QuantumSonification Foundations."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: object) -> dict:
    payload = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


boxes = [
    box("title", "comment", [25, 15, 1050, 28], text="QMW QUANTUMSONIFICATION FOUNDATIONS EVALUATOR v1", fontsize=18.0),
    box("subtitle", "comment", [25, 45, 1120, 38], text="OSC 7474 · graph-density representability · tensor-relative negativity · invariant-subspace continuity", fontsize=12.0),
    box("udp", "newobj", [25, 92, 165, 22], text="udpreceive 7474 cnmat", numinlets=1, numoutlets=1, outlettype=[""]),
    box("osc", "newobj", [215, 92, 130, 22], text="OpenSoundControl", numinlets=1, numoutlets=3, outlettype=["", "", "OSCTimeTag"]),
    box("root", "newobj", [370, 92, 105, 22], text="OSC-route /qsf", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("domain", "newobj", [500, 92, 230, 22], text="OSC-route /graph /modal /status", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("graphroute", "newobj", [25, 138, 585, 22], text="OSC-route /dimension /rho_real /rho_abs /metrics /projection /negativity", numinlets=1, numoutlets=7, outlettype=["", "", "", "", "", "", ""]),
    box("modalroute", "newobj", [630, 138, 720, 22], text="OSC-route /count /eigenvalues /stable_ids /cluster_ids /overlap /angles /residuals /revision", numinlets=1, numoutlets=9, outlettype=["", "", "", "", "", "", "", "", ""]),
    box("pdim", "newobj", [25, 175, 120, 22], text="prepend graph_dimension", numinlets=1, numoutlets=1, outlettype=[""]),
    box("preal", "newobj", [155, 175, 120, 22], text="prepend graph_rho_real", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pabs", "newobj", [285, 175, 115, 22], text="prepend graph_rho_abs", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pcount", "newobj", [630, 175, 120, 22], text="prepend modal_count", numinlets=1, numoutlets=1, outlettype=[""]),
    box("peigen", "newobj", [760, 175, 145, 22], text="prepend modal_eigenvalues", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pstable", "newobj", [915, 175, 135, 22], text="prepend modal_stable_ids", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pcluster", "newobj", [1060, 175, 145, 22], text="prepend modal_cluster_ids", numinlets=1, numoutlets=1, outlettype=[""]),
    box("poverlap", "newobj", [630, 207, 135, 22], text="prepend modal_overlap", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pangles", "newobj", [775, 207, 125, 22], text="prepend modal_angles", numinlets=1, numoutlets=1, outlettype=[""]),
    box("presiduals", "newobj", [910, 207, 140, 22], text="prepend modal_residuals", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pstatus", "newobj", [1060, 207, 95, 22], text="prepend status", numinlets=1, numoutlets=1, outlettype=[""]),
    box("js", "newobj", [500, 245, 250, 22], text="js qmw_foundations_evaluator_v1.js", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("real_label", "comment", [25, 282, 350, 22], text="rho_G signed real part · blue negative / red positive", fontsize=12.0),
    box("abs_label", "comment", [390, 282, 320, 22], text="|rho_G| magnitude", fontsize=12.0),
    box("modal_label", "comment", [755, 282, 550, 22], text="modal rows: eigenvalue · stable ID · cluster ID · overlap · angle confidence · residual quality", fontsize=12.0),
    box("realview", "jit.pwindow", [25, 308, 335, 335], numinlets=1, numoutlets=2, outlettype=["jit_matrix", ""]),
    box("absview", "jit.pwindow", [390, 308, 335, 335], numinlets=1, numoutlets=2, outlettype=["jit_matrix", ""]),
    box("modalview", "jit.pwindow", [755, 308, 570, 230], numinlets=1, numoutlets=2, outlettype=["jit_matrix", ""]),
    box("graph_metrics_label", "comment", [25, 665, 700, 22], text="GRAPH METRICS: entropy · purity · rank · nullity · components", fontsize=13.0),
    box("graph_metrics", "multislider", [25, 690, 700, 70], size=5, setminmax=[0.0, 16.0], slidercolor=[0.15, 0.72, 0.92, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("projection_label", "comment", [25, 772, 700, 22], text="PROJECTION: Frobenius error · trace distance · imaginary residual · rank deficit", fontsize=13.0),
    box("projection", "multislider", [25, 797, 700, 70], size=4, setminmax=[0.0, 1.0], slidercolor=[0.95, 0.44, 0.24, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("negative_label", "comment", [25, 882, 155, 22], text="negativity"),
    box("negative", "flonum", [180, 882, 90, 22], minimum=0.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("revision_label", "comment", [755, 565, 95, 22], text="revision"),
    box("revision", "number", [850, 565, 80, 22], minimum=0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("eigen_label", "comment", [755, 610, 570, 22], text="eigenvalues"),
    box("eigen", "multislider", [755, 635, 570, 55], size=16, setminmax=[0.0, 16.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("overlap_label", "comment", [755, 705, 570, 22], text="per-mode cluster overlap confidence"),
    box("overlap", "multislider", [755, 730, 570, 55], size=16, setminmax=[0.0, 1.0], slidercolor=[0.30, 0.88, 0.48, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("residual_label", "comment", [755, 800, 570, 22], text="generalized eigenpair residuals (display range 0–1e-4)"),
    box("residual", "multislider", [755, 825, 570, 55], size=16, setminmax=[0.0, 0.0001], slidercolor=[0.92, 0.25, 0.30, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("status_label", "comment", [755, 895, 65, 22], text="status"),
    box("status", "message", [825, 895, 500, 22], text="waiting for /qsf OSC on UDP 7474", numinlets=2, numoutlets=1, outlettype=[""]),
    box("contract", "comment", [25, 930, 1300, 55], text="OSC contract: /qsf/graph/{dimension,rho_real,rho_abs,metrics,projection,negativity} · /qsf/modal/{count,eigenvalues,stable_ids,cluster_ids,overlap,angles,residuals,revision} · /qsf/status", fontsize=11.0),
]


lines = [
    line("udp", 0, "osc"), line("osc", 0, "root"), line("root", 0, "domain"),
    line("domain", 0, "graphroute"), line("domain", 1, "modalroute"), line("domain", 2, "pstatus"),
    line("graphroute", 0, "pdim"), line("graphroute", 1, "preal"), line("graphroute", 2, "pabs"),
    line("graphroute", 3, "graph_metrics"), line("graphroute", 4, "projection"), line("graphroute", 5, "negative"),
    line("modalroute", 0, "pcount"), line("modalroute", 1, "peigen"), line("modalroute", 1, "eigen"),
    line("modalroute", 2, "pstable"), line("modalroute", 3, "pcluster"),
    line("modalroute", 4, "poverlap"), line("modalroute", 4, "overlap"),
    line("modalroute", 5, "pangles"), line("modalroute", 6, "presiduals"), line("modalroute", 6, "residual"),
    line("modalroute", 7, "revision"),
    line("pdim", 0, "js"), line("preal", 0, "js"), line("pabs", 0, "js"),
    line("pcount", 0, "js"), line("peigen", 0, "js"), line("pstable", 0, "js"), line("pcluster", 0, "js"),
    line("poverlap", 0, "js"), line("pangles", 0, "js"), line("presiduals", 0, "js"), line("pstatus", 0, "js"),
    line("js", 0, "realview"), line("js", 1, "absview"), line("js", 2, "modalview"), line("js", 3, "status", 1),
]


patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [70, 45, 1370, 1020],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OpenSoundControl.mxo", "type": "iLaX"},
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_foundations_evaluator_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }
}


if __name__ == "__main__":
    output = ROOT / "QMW_QuantumSonification_Foundations_Evaluator_v1.maxpat"
    output.write_text(json.dumps(patcher, indent=2) + "\n", encoding="utf-8")
    print(output)
