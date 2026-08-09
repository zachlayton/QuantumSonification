#!/usr/bin/env python3
"""Generate the dependency-light Max 9 QPE Synthesizer patch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def build() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [28, 18, 900, 30], text="QMW QPE SYNTHESIZER v1 — LISTEN TO PHASE COLLAPSE", fontsize=18),
        box("subtitle", "comment", [28, 50, 1010, 38], text="A trial-state superposition enters finite-register Quantum Phase Estimation. Each clock pulse measures one phase bin and voices the collapsed eigenstate."),
        box("run_label", "comment", [28, 105, 80, 20], text="RUN SHOTS"),
        box("run", "toggle", [110, 102, 24, 24], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("metro", "newobj", [145, 103, 78, 22], text="metro 240", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("manual", "button", [235, 102, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box("manual_label", "comment", [266, 105, 88, 20], text="single shot"),
        box("tempo_label", "comment", [370, 105, 85, 20], text="interval ms"),
        box("tempo", "number", [455, 102, 70, 22], minimum=40, maximum=2000, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("bits_label", "comment", [560, 105, 115, 20], text="estimation qubits"),
        box("bits", "number", [680, 102, 60, 22], minimum=2, maximum=10, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("bits_pre", "newobj", [750, 102, 112, 22], text="prepend precision", numinlets=1, numoutlets=1, outlettype=[""]),
        box("phase_title", "comment", [28, 157, 460, 24], text="UNITARY EIGENPHASES  φj", fontsize=14),
        box("phases", "multislider", [28, 187, 480, 105], size=4, setminmax=[0.0, 1.0], setstyle=1, spacing=8, numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("phases_pre", "newobj", [28, 300, 112, 22], text="prepend setphases", numinlets=1, numoutlets=1, outlettype=[""]),
        box("weight_title", "comment", [540, 157, 460, 24], text="TRIAL-STATE BORN WEIGHTS  |cj|²", fontsize=14),
        box("weights", "multislider", [540, 187, 480, 105], size=4, setminmax=[0.0, 1.0], setstyle=1, spacing=8, numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("weights_pre", "newobj", [540, 300, 120, 22], text="prepend setweights", numinlets=1, numoutlets=1, outlettype=[""]),
        box("mapping", "comment", [28, 352, 210, 24], text="PHASE → PITCH MAPPING", fontsize=14),
        box("root_label", "comment", [28, 390, 75, 20], text="root Hz"),
        box("root", "flonum", [105, 387, 75, 22], minimum=20.0, maximum=440.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("root_pre", "newobj", [190, 387, 88, 22], text="prepend root", numinlets=1, numoutlets=1, outlettype=[""]),
        box("span_label", "comment", [305, 390, 95, 20], text="span octaves"),
        box("span", "flonum", [405, 387, 70, 22], minimum=0.5, maximum=7.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("span_pre", "newobj", [485, 387, 88, 22], text="prepend span", numinlets=1, numoutlets=1, outlettype=[""]),
        box("dist_title", "comment", [610, 352, 410, 24], text="CONDITIONAL PHASE-REGISTER DISTRIBUTION", fontsize=14),
        box("distribution", "multislider", [610, 382, 410, 85], size=1024, setminmax=[0.0, 1.0], setstyle=1, numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("js", "newobj", [28, 448, 150, 22], text="js qpe_controller.js", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
        box("freq_smooth", "newobj", [28, 490, 82, 22], text="pack f 12", numinlets=2, numoutlets=1, outlettype=[""]),
        box("freq_line", "newobj", [28, 520, 42, 22], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("osc1", "newobj", [28, 558, 88, 22], text="cycle~ 110.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ratio", "newobj", [135, 490, 54, 22], text="* 2.01", numinlets=2, numoutlets=1, outlettype=[""]),
        box("ratio_smooth", "newobj", [135, 520, 82, 22], text="pack f 12", numinlets=2, numoutlets=1, outlettype=[""]),
        box("ratio_line", "newobj", [135, 550, 42, 22], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("osc2", "newobj", [135, 580, 88, 22], text="cycle~ 220.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("osc2_gain", "newobj", [135, 615, 42, 22], text="*~ 0.28", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mix", "newobj", [65, 650, 38, 22], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("env_message", "message", [260, 490, 150, 22], text="$1 7, 0. 360 7", numinlets=2, numoutlets=1, outlettype=[""]),
        box("env", "newobj", [260, 520, 42, 22], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("amp", "newobj", [65, 686, 38, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("pan_l", "newobj", [335, 600, 160, 22], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pan_r", "newobj", [505, 600, 160, 22], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("left", "newobj", [260, 686, 38, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("right", "newobj", [370, 686, 38, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain", "live.gain~", [480, 650, 130, 72], numinlets=2, numoutlets=5, outlettype=["signal", "signal", "", "float", "list"]),
        box("dac", "newobj", [650, 686, 72, 22], text="ezdac~", numinlets=2, numoutlets=0),
        box("status", "comment", [28, 752, 992, 38], text="READY", fontsize=12),
        box("load", "newobj", [880, 102, 60, 22], text="loadbang", numinlets=1, numoutlets=1, outlettype=["bang"]),
        box("defaults", "message", [880, 130, 165, 22], text="240 5 55. 4.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("unpack", "newobj", [880, 158, 150, 22], text="unpack i i f f", numinlets=1, numoutlets=4, outlettype=["int", "int", "float", "float"]),
        box("phase_default", "message", [880, 188, 158, 22], text="0.125 0.301 0.547 0.823", numinlets=2, numoutlets=1, outlettype=[""]),
        box("weight_default", "message", [880, 218, 158, 22], text="0.42 0.27 0.20 0.11", numinlets=2, numoutlets=1, outlettype=[""]),
    ]
    lines = [
        line("run", 0, "metro"), line("tempo", 0, "metro", 1), line("metro", 0, "js"), line("manual", 0, "js"),
        line("bits", 0, "bits_pre"), line("bits_pre", 0, "js"), line("phases", 0, "phases_pre"), line("phases_pre", 0, "js"),
        line("weights", 0, "weights_pre"), line("weights_pre", 0, "js"), line("root", 0, "root_pre"), line("root_pre", 0, "js"),
        line("span", 0, "span_pre"), line("span_pre", 0, "js"), line("js", 0, "freq_smooth"), line("freq_smooth", 0, "freq_line"),
        line("freq_line", 0, "osc1"), line("js", 0, "ratio"), line("ratio", 0, "ratio_smooth"), line("ratio_smooth", 0, "ratio_line"),
        line("ratio_line", 0, "osc2"), line("osc2", 0, "osc2_gain"), line("osc1", 0, "mix"), line("osc2_gain", 0, "mix", 1),
        line("js", 1, "env_message"), line("env_message", 0, "env"), line("mix", 0, "amp"), line("env", 0, "amp", 1),
        line("js", 2, "distribution"), line("js", 3, "status"), line("js", 4, "pan_l"), line("js", 4, "pan_r"),
        line("amp", 0, "left"), line("pan_l", 0, "left", 1), line("amp", 0, "right"), line("pan_r", 0, "right", 1),
        line("left", 0, "gain"), line("right", 0, "gain", 1), line("gain", 0, "dac"), line("gain", 1, "dac", 1),
        line("load", 0, "defaults"), line("defaults", 0, "unpack"), line("unpack", 0, "tempo"), line("unpack", 1, "bits"),
        line("unpack", 2, "root"), line("unpack", 3, "span"), line("load", 0, "phase_default"), line("phase_default", 0, "phases"),
        line("load", 0, "weight_default"), line("weight_default", 0, "weights"), line("load", 0, "js"),
    ]
    return {"patcher": {"fileversion": 1, "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1}, "classnamespace": "box", "rect": [80, 60, 1080, 830], "gridsize": [15.0, 15.0], "boxes": boxes, "lines": lines, "dependency_cache": [{"name": "qpe_controller.js", "type": "TEXT", "implicit": 1}], "autosave": 0}}


if __name__ == "__main__":
    target = ROOT / "QMW_QPE_Synthesizer_v1.maxpat"
    target.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"wrote {target}")
