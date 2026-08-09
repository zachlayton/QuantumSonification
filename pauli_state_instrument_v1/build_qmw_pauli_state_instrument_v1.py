#!/usr/bin/env python3
"""Generate the Max 9 Pauli State Instrument v1 and its addressed voice."""

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


def wrap(boxes: list[dict[str, Any]], lines: list[dict[str, Any]], rect: list[float], dependencies: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": rect,
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "autosave": 0,
    }
    if dependencies:
        data["dependency_cache"] = dependencies
    return {"patcher": data}


def build_voice() -> dict[str, Any]:
    boxes = [
        box("in", "newobj", [20.0, 25.0, 34.0, 22.0], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route", "newobj", [70.0, 25.0, 330.0, 22.0], text="route carrier shift side raw index gain pan", numinlets=1, numoutlets=8, outlettype=["", "", "", "", "", "", "", ""]),
        box("carrier_pack", "newobj", [35.0, 68.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("carrier_line", "newobj", [35.0, 98.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("shift_pack", "newobj", [125.0, 68.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("shift_line", "newobj", [125.0, 98.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("side_l_expr", "newobj", [215.0, 68.0, 125.0, 22.0], text="expr (1.-$f1)*0.5", numinlets=1, numoutlets=1, outlettype=[""]),
        box("side_u_expr", "newobj", [350.0, 68.0, 125.0, 22.0], text="expr (1.+$f1)*0.5", numinlets=1, numoutlets=1, outlettype=[""]),
        box("side_l_pack", "newobj", [235.0, 98.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("side_u_pack", "newobj", [370.0, 98.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("side_l_line", "newobj", [235.0, 128.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("side_u_line", "newobj", [370.0, 128.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("carrier_cos", "newobj", [35.0, 160.0, 105.0, 22.0], text="cycle~ 220. 0.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("carrier_sin", "newobj", [150.0, 160.0, 105.0, 22.0], text="cycle~ 220. 0.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mod_cos", "newobj", [35.0, 197.0, 98.0, 22.0], text="cycle~ 30. 0.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mod_sin", "newobj", [150.0, 197.0, 105.0, 22.0], text="cycle~ 30. 0.25", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("index_cycles", "newobj", [500.0, 310.0, 132.0, 22.0], text="expr $f1/6.28318530718", numinlets=1, numoutlets=1, outlettype=[""]),
        box("index_pack", "newobj", [500.0, 340.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("index_line", "newobj", [500.0, 370.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("phase_mod", "newobj", [285.0, 197.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("phase_quadrature", "newobj", [335.0, 197.0, 72.0, 22.0], text="+~ 0.25", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ring_cos", "newobj", [70.0, 235.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ring_sin", "newobj", [175.0, 235.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("lower", "newobj", [75.0, 273.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("upper", "newobj", [180.0, 273.0, 36.0, 22.0], text="-~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("lower_select", "newobj", [75.0, 310.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("upper_select", "newobj", [180.0, 310.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("selected", "newobj", [130.0, 347.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("raw_ssb_expr", "newobj", [485.0, 205.0, 92.0, 22.0], text="expr 1.-$f1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("raw_ssb_pack", "newobj", [485.0, 235.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("raw_ssb_line", "newobj", [485.0, 265.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("raw_pack", "newobj", [590.0, 235.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("raw_line", "newobj", [590.0, 265.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("raw_scaled", "newobj", [270.0, 310.0, 92.0, 22.0], text="*~ 1.41421356", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ssb_mix", "newobj", [105.0, 382.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("raw_mix", "newobj", [210.0, 382.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("topology_mix", "newobj", [155.0, 417.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_pack", "newobj", [500.0, 68.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("gain_line", "newobj", [500.0, 98.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("gain", "newobj", [155.0, 452.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("pan_l_expr", "newobj", [590.0, 68.0, 150.0, 22.0], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pan_r_expr", "newobj", [590.0, 98.0, 150.0, 22.0], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pan_l_pack", "newobj", [590.0, 128.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("pan_r_pack", "newobj", [670.0, 128.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("pan_l_line", "newobj", [590.0, 158.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("pan_r_line", "newobj", [670.0, 158.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("left", "newobj", [115.0, 490.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("right", "newobj", [205.0, 490.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("out_l", "newobj", [115.0, 528.0, 48.0, 22.0], text="out~ 1", numinlets=1, numoutlets=0),
        box("out_r", "newobj", [205.0, 528.0, 48.0, 22.0], text="out~ 2", numinlets=1, numoutlets=0),
    ]
    lines = [
        line("in", 0, "route"),
        line("route", 0, "carrier_pack"), line("carrier_pack", 0, "carrier_line"),
        line("carrier_line", 0, "carrier_cos"), line("carrier_line", 0, "carrier_sin"),
        line("route", 1, "shift_pack"), line("shift_pack", 0, "shift_line"),
        line("shift_line", 0, "mod_cos"), line("shift_line", 0, "mod_sin"),
        line("route", 4, "index_cycles"), line("index_cycles", 0, "index_pack"),
        line("index_pack", 0, "index_line"), line("mod_sin", 0, "phase_mod", 0),
        line("index_line", 0, "phase_mod", 1), line("phase_mod", 0, "carrier_cos", 1),
        line("phase_mod", 0, "phase_quadrature", 0), line("phase_quadrature", 0, "carrier_sin", 1),
        line("route", 2, "side_l_expr"), line("route", 2, "side_u_expr"),
        line("side_l_expr", 0, "side_l_pack"), line("side_u_expr", 0, "side_u_pack"),
        line("side_l_pack", 0, "side_l_line"), line("side_u_pack", 0, "side_u_line"),
        line("carrier_cos", 0, "ring_cos", 0), line("mod_cos", 0, "ring_cos", 1),
        line("carrier_sin", 0, "ring_sin", 0), line("mod_sin", 0, "ring_sin", 1),
        line("ring_cos", 0, "lower", 0), line("ring_sin", 0, "lower", 1),
        line("ring_cos", 0, "upper", 0), line("ring_sin", 0, "upper", 1),
        line("lower", 0, "lower_select", 0), line("side_l_line", 0, "lower_select", 1),
        line("upper", 0, "upper_select", 0), line("side_u_line", 0, "upper_select", 1),
        line("lower_select", 0, "selected", 0), line("upper_select", 0, "selected", 1),
        line("route", 3, "raw_ssb_expr"), line("route", 3, "raw_pack"),
        line("raw_ssb_expr", 0, "raw_ssb_pack"), line("raw_ssb_pack", 0, "raw_ssb_line"),
        line("raw_pack", 0, "raw_line"), line("ring_cos", 0, "raw_scaled"),
        line("selected", 0, "ssb_mix", 0), line("raw_ssb_line", 0, "ssb_mix", 1),
        line("raw_scaled", 0, "raw_mix", 0), line("raw_line", 0, "raw_mix", 1),
        line("ssb_mix", 0, "topology_mix", 0), line("raw_mix", 0, "topology_mix", 1),
        line("route", 5, "gain_pack"), line("gain_pack", 0, "gain_line"),
        line("topology_mix", 0, "gain", 0), line("gain_line", 0, "gain", 1),
        line("route", 6, "pan_l_expr"), line("route", 6, "pan_r_expr"),
        line("pan_l_expr", 0, "pan_l_pack"), line("pan_r_expr", 0, "pan_r_pack"),
        line("pan_l_pack", 0, "pan_l_line"), line("pan_r_pack", 0, "pan_r_line"),
        line("gain", 0, "left", 0), line("pan_l_line", 0, "left", 1),
        line("gain", 0, "right", 0), line("pan_r_line", 0, "right", 1),
        line("left", 0, "out_l"), line("right", 0, "out_r"),
    ]
    return wrap(boxes, lines, [100.0, 100.0, 780.0, 590.0])


def build_instrument() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [28.0, 18.0, 780.0, 28.0], text="QMW PAULI STATE INSTRUMENT v1 — THE COMPLETE ADDRESS", fontsize=18.0),
        box("subtitle", "comment", [28.0, 49.0, 1010.0, 38.0], text="Six 2p states are individually addressed by (n,l,m_l,m_s). Every line is produced by quadrature carrier x state-modulator multiplication, with one selected sideband per occupied address."),
        box("ledger_title", "comment", [28.0, 100.0, 360.0, 22.0], text="FERMIONIC STATE LEDGER — click an address to toggle it", fontsize=14.0),
        box("state0", "message", [28.0, 135.0, 150.0, 22.0], text="toggle 0", annotation="(2,1,-1,down)", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label0", "comment", [28.0, 159.0, 150.0, 20.0], text="(2,1,-1,down)"),
        box("state1", "message", [188.0, 135.0, 150.0, 22.0], text="toggle 1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label1", "comment", [188.0, 159.0, 150.0, 20.0], text="(2,1,-1,up)"),
        box("state2", "message", [348.0, 135.0, 150.0, 22.0], text="toggle 2", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label2", "comment", [348.0, 159.0, 150.0, 20.0], text="(2,1,0,down)"),
        box("state3", "message", [508.0, 135.0, 150.0, 22.0], text="toggle 3", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label3", "comment", [508.0, 159.0, 150.0, 20.0], text="(2,1,0,up)"),
        box("state4", "message", [668.0, 135.0, 150.0, 22.0], text="toggle 4", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label4", "comment", [668.0, 159.0, 150.0, 20.0], text="(2,1,1,down)"),
        box("state5", "message", [828.0, 135.0, 150.0, 22.0], text="toggle 5", numinlets=2, numoutlets=1, outlettype=[""]),
        box("label5", "comment", [828.0, 159.0, 150.0, 20.0], text="(2,1,1,up)"),
        box("fill", "message", [28.0, 195.0, 78.0, 22.0], text="fill", numinlets=2, numoutlets=1, outlettype=[""]),
        box("clear", "message", [116.0, 195.0, 78.0, 22.0], text="clear", numinlets=2, numoutlets=1, outlettype=[""]),
        box("exclude", "message", [204.0, 195.0, 105.0, 22.0], text="occupy 0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("exclude_note", "comment", [320.0, 196.0, 350.0, 20.0], text="attempt duplicate occupation after filling the shell"),
        box("occupancy", "multislider", [680.0, 192.0, 298.0, 36.0], size=6, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("field_label", "comment", [28.0, 253.0, 120.0, 20.0], text="magnetic field B"),
        box("field", "flonum", [150.0, 250.0, 80.0, 22.0], minimum=0.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("field_pre", "newobj", [240.0, 250.0, 90.0, 22.0], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""]),
        box("base_label", "comment", [350.0, 253.0, 90.0, 20.0], text="base Hz"),
        box("base", "flonum", [430.0, 250.0, 80.0, 22.0], minimum=30.0, maximum=8000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("base_pre", "newobj", [520.0, 250.0, 88.0, 22.0], text="prepend base", numinlets=1, numoutlets=1, outlettype=[""]),
        box("orb_label", "comment", [628.0, 253.0, 96.0, 20.0], text="orbital Hz"),
        box("orb", "flonum", [718.0, 250.0, 72.0, 22.0], minimum=0.0, maximum=1000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("orb_pre", "newobj", [800.0, 250.0, 98.0, 22.0], text="prepend orbital", numinlets=1, numoutlets=1, outlettype=[""]),
        box("zee_label", "comment", [28.0, 291.0, 120.0, 20.0], text="audible Zeeman Hz/T"),
        box("zee", "flonum", [150.0, 288.0, 80.0, 22.0], minimum=0.0, maximum=1000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("zee_pre", "newobj", [240.0, 288.0, 102.0, 22.0], text="prepend zeeman", numinlets=1, numoutlets=1, outlettype=[""]),
        box("raw_label", "comment", [370.0, 291.0, 115.0, 20.0], text="raw RM blend"),
        box("raw", "flonum", [480.0, 288.0, 80.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("raw_pre", "newobj", [570.0, 288.0, 88.0, 22.0], text="prepend raw", numinlets=1, numoutlets=1, outlettype=[""]),
        box("index_label", "comment", [675.0, 291.0, 80.0, 20.0], text="FM index"),
        box("index", "flonum", [750.0, 288.0, 70.0, 22.0], minimum=0.0, maximum=12.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("index_pre", "newobj", [830.0, 288.0, 98.0, 22.0], text="prepend index", numinlets=1, numoutlets=1, outlettype=[""]),
        box("spin_title", "comment", [28.0, 338.0, 500.0, 22.0], text="SPINOR INTERFERENCE — 2pi changes sign; 4pi returns", fontsize=14.0),
        box("rotate_label", "comment", [28.0, 376.0, 110.0, 20.0], text="rotation degrees"),
        box("rotate", "flonum", [140.0, 373.0, 90.0, 22.0], minimum=0.0, maximum=720.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("rotate_pre", "newobj", [240.0, 373.0, 98.0, 22.0], text="prepend rotate", numinlets=1, numoutlets=1, outlettype=[""]),
        box("rotate_sweep", "message", [350.0, 373.0, 138.0, 22.0], text="0., 720. 16000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("rotate_line", "newobj", [500.0, 373.0, 38.0, 22.0], text="line", numinlets=2, numoutlets=1, outlettype=[""]),
        box("spin_note", "comment", [560.0, 367.0, 418.0, 36.0], text="110 Hz reference-interference tone: full at 0 deg, silent at 360 deg, restored at 720 deg."),
        box("anti_title", "comment", [28.0, 425.0, 500.0, 22.0], text="ANTISYMMETRIC TWO-FERMION NORM", fontsize=14.0),
        box("overlap_label", "comment", [28.0, 463.0, 110.0, 20.0], text="state overlap"),
        box("overlap", "flonum", [140.0, 460.0, 90.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("overlap_pre", "newobj", [240.0, 460.0, 105.0, 22.0], text="prepend overlap", numinlets=1, numoutlets=1, outlettype=[""]),
        box("overlap_sweep", "message", [360.0, 460.0, 125.0, 22.0], text="0., 1. 10000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("overlap_line", "newobj", [500.0, 460.0, 38.0, 22.0], text="line", numinlets=2, numoutlets=1, outlettype=[""]),
        box("anti_note", "comment", [560.0, 454.0, 418.0, 36.0], text="330 Hz Slater-wedge tone: amplitude sqrt(1-|overlap|^2); identical one-particle states force silence."),
        box("controller", "newobj", [28.0, 520.0, 258.0, 22.0], text="js qmw_pauli_state_controller_v1.js", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
        box("status", "message", [305.0, 520.0, 673.0, 22.0], text="initializing complete-state ledger...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("poly", "newobj", [28.0, 575.0, 285.0, 22.0], text="poly~ qmw_pauli_state_voice_v1 6 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("spin_amp_pack", "newobj", [335.0, 575.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("spin_amp_line", "newobj", [420.0, 575.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("spin_osc", "newobj", [475.0, 575.0, 72.0, 22.0], text="cycle~ 110.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("spin_gain", "newobj", [560.0, 575.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("anti_amp_pack", "newobj", [620.0, 575.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("anti_amp_line", "newobj", [705.0, 575.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("anti_osc", "newobj", [760.0, 575.0, 72.0, 22.0], text="cycle~ 330.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("anti_gain", "newobj", [845.0, 575.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_l1", "newobj", [130.0, 625.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_l2", "newobj", [180.0, 625.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r1", "newobj", [255.0, 625.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r2", "newobj", [305.0, 625.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_label", "comment", [380.0, 628.0, 90.0, 20.0], text="master"),
        box("master", "flonum", [445.0, 625.0, 72.0, 22.0], minimum=0.0, maximum=0.5, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("master_pack", "newobj", [530.0, 625.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("master_line", "newobj", [615.0, 625.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("master_l", "newobj", [180.0, 670.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [305.0, 670.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("clip_l", "newobj", [180.0, 707.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("clip_r", "newobj", [305.0, 707.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [420.0, 675.0, 18.0, 70.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [450.0, 675.0, 18.0, 70.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [500.0, 685.0, 52.0, 52.0], numinlets=2, numoutlets=0),
        box("footer", "comment", [590.0, 680.0, 388.0, 60.0], text="Each shell voice is a true quadrature SSB ring modulator. The factor m_l + 2m_s controls its signed displacement from the carrier."),
        box("init_fill", "newobj", [28.0, 755.0, 82.0, 22.0], text="loadmess fill", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_field", "newobj", [120.0, 755.0, 88.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_base", "newobj", [218.0, 755.0, 98.0, 22.0], text="loadmess 220.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_orb", "newobj", [326.0, 755.0, 92.0, 22.0], text="loadmess 24.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_zee", "newobj", [428.0, 755.0, 92.0, 22.0], text="loadmess 30.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_raw", "newobj", [530.0, 755.0, 88.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_index", "newobj", [628.0, 755.0, 88.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_rotate", "newobj", [726.0, 755.0, 88.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_overlap", "newobj", [824.0, 755.0, 88.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_master", "newobj", [922.0, 755.0, 96.0, 22.0], text="loadmess 0.16", numinlets=1, numoutlets=1, outlettype=[""]),
    ]
    lines = []
    for state in range(6):
        lines.append(line(f"state{state}", 0, "controller"))
    lines += [
        line("fill", 0, "controller"), line("clear", 0, "controller"), line("exclude", 0, "controller"),
        line("field", 0, "field_pre"), line("field_pre", 0, "controller"),
        line("base", 0, "base_pre"), line("base_pre", 0, "controller"),
        line("orb", 0, "orb_pre"), line("orb_pre", 0, "controller"),
        line("zee", 0, "zee_pre"), line("zee_pre", 0, "controller"),
        line("raw", 0, "raw_pre"), line("raw_pre", 0, "controller"),
        line("index", 0, "index_pre"), line("index_pre", 0, "controller"),
        line("rotate", 0, "rotate_pre"), line("rotate_pre", 0, "controller"),
        line("rotate_sweep", 0, "rotate_line"), line("rotate_line", 0, "rotate"),
        line("overlap", 0, "overlap_pre"), line("overlap_pre", 0, "controller"),
        line("overlap_sweep", 0, "overlap_line"), line("overlap_line", 0, "overlap"),
        line("controller", 0, "poly"), line("controller", 1, "occupancy"),
        line("controller", 2, "spin_amp_pack"), line("spin_amp_pack", 0, "spin_amp_line"),
        line("spin_osc", 0, "spin_gain", 0), line("spin_amp_line", 0, "spin_gain", 1),
        line("controller", 3, "anti_amp_pack"), line("anti_amp_pack", 0, "anti_amp_line"),
        line("anti_osc", 0, "anti_gain", 0), line("anti_amp_line", 0, "anti_gain", 1),
        line("controller", 4, "status", 1),
        line("poly", 0, "sum_l1", 0), line("spin_gain", 0, "sum_l1", 1), line("sum_l1", 0, "sum_l2", 0), line("anti_gain", 0, "sum_l2", 1),
        line("poly", 1, "sum_r1", 0), line("spin_gain", 0, "sum_r1", 1), line("sum_r1", 0, "sum_r2", 0), line("anti_gain", 0, "sum_r2", 1),
        line("master", 0, "master_pack"), line("master_pack", 0, "master_line"),
        line("sum_l2", 0, "master_l", 0), line("master_line", 0, "master_l", 1),
        line("sum_r2", 0, "master_r", 0), line("master_line", 0, "master_r", 1),
        line("master_l", 0, "clip_l"), line("master_r", 0, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"),
        line("clip_l", 0, "dac", 0), line("clip_r", 0, "dac", 1),
        line("init_fill", 0, "controller"), line("init_field", 0, "field"), line("init_base", 0, "base"),
        line("init_orb", 0, "orb"), line("init_zee", 0, "zee"), line("init_raw", 0, "raw"), line("init_index", 0, "index"), line("init_rotate", 0, "rotate"),
        line("init_overlap", 0, "overlap"), line("init_master", 0, "master"),
    ]
    return wrap(
        boxes,
        lines,
        [70.0, 40.0, 1040.0, 815.0],
        [
            {"name": "qmw_pauli_state_controller_v1.js", "type": "TEXT"},
            {"name": "qmw_pauli_state_voice_v1.maxpat", "type": "JSON"},
        ],
    )


def validate(payload: dict[str, Any], required_text: str) -> None:
    patcher = payload["patcher"]
    identifiers = {entry["box"]["id"] for entry in patcher["boxes"]}
    if len(identifiers) != len(patcher["boxes"]):
        raise RuntimeError("duplicate Max identifiers")
    for entry in patcher["lines"]:
        source = entry["patchline"]["source"][0]
        destination = entry["patchline"]["destination"][0]
        if source not in identifiers or destination not in identifiers:
            raise RuntimeError(f"dangling line {source} -> {destination}")
    texts = {entry["box"].get("text", "") for entry in patcher["boxes"]}
    if not any(text.startswith(required_text) for text in texts):
        raise RuntimeError(f"missing required object {required_text}")


def validate_ring_voice(payload: dict[str, Any]) -> None:
    validate(payload, "cycle~")
    texts = [entry["box"].get("text", "") for entry in payload["patcher"]["boxes"]]
    if texts.count("*~") < 7 or "+~" not in texts or "-~" not in texts:
        raise RuntimeError("voice is missing quadrature ring products or its sideband matrix")
    if "route carrier shift side raw index gain pan" not in texts:
        raise RuntimeError("voice is not controlled by a signed modulation displacement")
    if "expr $f1/6.28318530718" not in texts or "+~ 0.25" not in texts:
        raise RuntimeError("voice is missing FM-index phase scaling or quadrature phase restoration")


def main() -> None:
    voice = build_voice()
    instrument = build_instrument()
    validate_ring_voice(voice)
    validate(instrument, "poly~ qmw_pauli_state_voice_v1")
    (ROOT / "qmw_pauli_state_voice_v1.maxpat").write_text(json.dumps(voice, indent=2) + "\n", encoding="utf-8")
    (ROOT / "QMW_Pauli_State_Instrument_v1.maxpat").write_text(json.dumps(instrument, indent=2) + "\n", encoding="utf-8")
    print("generated QMW_Pauli_State_Instrument_v1.maxpat and qmw_pauli_state_voice_v1.maxpat")


if __name__ == "__main__":
    main()
