#!/usr/bin/env python3
"""Build the clockless Max realization of the QMW v2 relational clock."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Correlation_Differentiation_Clock_v2.maxpat"


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


boxes = [
    box("title", "comment", [25, 15, 960, 28], text="QMW CORRELATION / DIFFERENTIATION CLOCK v2", fontsize=18.0),
    box("principle", "comment", [25, 48, 1000, 40], text="No metro · no phasor · no rtt.clock~. Max receives ticks only when accumulated relational change crosses a quantum."),
    box("udp", "newobj", [25, 100, 145, 22], text="udpreceive 7442", numinlets=1, numoutlets=1, outlettype=["FullPacket"]),
    box("route", "newobj", [185, 100, 820, 22], text="OSC-route /qmw/temporal/v2/tick /qmw/temporal/v2/relation /qmw/temporal/v2/condition /qmw/temporal/v2/snapshot/end /qmw/temporal/v2/config", numinlets=1, numoutlets=6, outlettype=[""] * 6),
    box("router", "newobj", [25, 142, 235, 22], text="js qmw_correlation_tick_router_v2.js", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
    box("tick_monitor", "message", [280, 142, 720, 22], text="waiting for a relational tick...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("relation_monitor", "message", [280, 174, 720, 22], text="waiting for relation samples...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("condition_monitor", "message", [280, 206, 400, 22], text="waiting for conditional state...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("config_monitor", "message", [700, 235, 300, 22], text="change quantum not yet acknowledged", numinlets=2, numoutlets=1, outlettype=[""]),
    box("snapshot_unpack", "newobj", [700, 206, 90, 22], text="unpack i i i", numinlets=1, numoutlets=3, outlettype=["int"] * 3),
    box("time_label", "comment", [805, 208, 105, 20], text="RELATIONAL TIME"),
    box("time_number", "number", [915, 205, 75, 24], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("dsp_toggle", "toggle", [25, 715, 26, 26], numinlets=1, numoutlets=1, outlettype=["int"]),
    box("dsp", "newobj", [60, 717, 52, 22], text="ezdac~", numinlets=2, numoutlets=0),
    box("audio_level", "newobj", [635, 715, 62, 22], text="*~ 0.28", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("midiout", "newobj", [915, 715, 60, 22], text="midiout", numinlets=1, numoutlets=0),
    box("quantum_label", "comment", [25, 760, 150, 22], text="CHANGE QUANTUM", fontsize=13.0),
    box("quantum_number", "flonum", [175, 758, 90, 24], minimum=0.000001, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("quantum_default", "newobj", [275, 758, 92, 22], text="loadmess 0.005", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("quantum_prepend", "newobj", [375, 758, 420, 22], text="prepend /qmw/temporal/v2/control/change-quantum", numinlets=1, numoutlets=1, outlettype=[""]),
    box("quantum_packet_trigger", "newobj", [805, 758, 42, 22], text="t b l", numinlets=1, numoutlets=2, outlettype=["bang", ""]),
    box("quantum_osc", "newobj", [858, 758, 120, 22], text="OpenSoundControl", numinlets=1, numoutlets=3, outlettype=["", "", "OSCTimeTag"]),
    box("quantum_udp", "newobj", [858, 790, 142, 22], text="udpsend 127.0.0.1 7444", numinlets=1, numoutlets=0),
]

lines = [
    line("udp", 0, "route"),
    line("route", 0, "router"),
    line("router", 2, "tick_monitor", 1),
    line("route", 1, "relation_monitor", 1),
    line("route", 2, "condition_monitor", 1),
    line("route", 3, "snapshot_unpack"),
    line("route", 4, "config_monitor", 1),
    line("snapshot_unpack", 1, "time_number"),
    line("dsp_toggle", 0, "dsp"),
    line("audio_level", 0, "dsp"),
    line("audio_level", 0, "dsp", 1),
    line("quantum_default", 0, "quantum_number"),
    line("quantum_number", 0, "quantum_prepend"),
    line("quantum_prepend", 0, "quantum_packet_trigger"),
    line("quantum_packet_trigger", 1, "quantum_osc"),
    line("quantum_packet_trigger", 0, "quantum_osc"),
    line("quantum_osc", 0, "quantum_udp"),
]


def add_tick_lane(kind: str, router_outlet: int, y: float, color: list[float], waveform: str) -> None:
    prefix = kind
    boxes.extend([
        box(f"{prefix}_panel", "panel", [20, y - 10, 980, 205], bgcolor=color, border=1, numinlets=1, numoutlets=0),
        box(f"{prefix}_title", "comment", [35, y, 260, 24], text=f"{kind.upper()} TICKS", fontsize=16.0),
        box(f"{prefix}_trigger", "newobj", [35, y + 34, 42, 22], text="t b l", numinlets=1, numoutlets=2, outlettype=["bang", ""]),
        box(f"{prefix}_flash", "button", [88, y + 33, 28, 28], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box(f"{prefix}_counter", "newobj", [128, y + 36, 55, 22], text="counter", numinlets=5, numoutlets=4, outlettype=["int", "", "", "int"]),
        box(f"{prefix}_count", "number", [195, y + 34, 72, 24], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_unpack", "newobj", [35, y + 72, 330, 22], text="unpack s s s i i f f f i i f", numinlets=1, numoutlets=11, outlettype=["", "", "", "int", "int", "float", "float", "float", "int", "int", "float"]),
        box(f"{prefix}_edge", "message", [380, y + 72, 205, 22], text="edge", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_corr", "flonum", [600, y + 72, 72, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_diff", "flonum", [685, y + 72, 82, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_strength", "flonum", [780, y + 72, 72, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_note_sig", "newobj", [35, y + 110, 42, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_click", "newobj", [88, y + 110, 42, 22], text="click~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_vel_sig", "newobj", [142, y + 110, 42, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_dur_sig", "newobj", [195, y + 110, 42, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_vel_clip", "newobj", [142, y + 143, 72, 22], text="clip 0 127", numinlets=3, numoutlets=1, outlettype=["int"]),
        box(f"{prefix}_makenote", "newobj", [255, y + 110, 105, 22], text="rtt.makenote~ @noteoff 1", numinlets=5, numoutlets=3, outlettype=["", "", ""]),
        box(f"{prefix}_mtof", "newobj", [375, y + 110, 38, 22], text="mtof", numinlets=1, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_osc", "newobj", [425, y + 110, 52, 22], text=waveform, numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_env_message", "message", [545, y + 110, 148, 22], text=("0.82 5, 0. 360 5" if kind == "correlate" else "0.68 3, 0. 150 3"), numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_env", "newobj", [850, y + 110, 42, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_vca", "newobj", [905, y + 110, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_manual", "button", [875, y + 33, 28, 28], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box(f"{prefix}_manual_label", "comment", [910, y + 37, 65, 20], text="test tick"),
        box(f"{prefix}_note_default", "newobj", [35, y + 168, 72, 22], text=f"loadmess {60 if kind == 'correlate' else 66}", numinlets=1, numoutlets=1, outlettype=["int"]),
        box(f"{prefix}_vel_default", "newobj", [118, y + 168, 78, 22], text="loadmess 100", numinlets=1, numoutlets=1, outlettype=["int"]),
        box(f"{prefix}_dur_default", "newobj", [208, y + 168, 78, 22], text="loadmess 320", numinlets=1, numoutlets=1, outlettype=["int"]),
    ])
    lines.extend([
        line("router", router_outlet, f"{prefix}_trigger"),
        line(f"{prefix}_trigger", 1, f"{prefix}_unpack"),
        line(f"{prefix}_trigger", 0, f"{prefix}_flash"),
        line(f"{prefix}_trigger", 0, f"{prefix}_counter"),
        line(f"{prefix}_trigger", 0, f"{prefix}_click"),
        line(f"{prefix}_trigger", 0, f"{prefix}_env_message"),
        line(f"{prefix}_manual", 0, f"{prefix}_click"),
        line(f"{prefix}_manual", 0, f"{prefix}_env_message"),
        line(f"{prefix}_counter", 0, f"{prefix}_count"),
        line(f"{prefix}_unpack", 1, f"{prefix}_edge", 1),
        line(f"{prefix}_unpack", 5, f"{prefix}_corr"),
        line(f"{prefix}_unpack", 6, f"{prefix}_diff"),
        line(f"{prefix}_unpack", 7, f"{prefix}_strength"),
        line(f"{prefix}_unpack", 8, f"{prefix}_note_sig"),
        line(f"{prefix}_unpack", 8, f"{prefix}_mtof"),
        line(f"{prefix}_unpack", 9, f"{prefix}_vel_clip"),
        line(f"{prefix}_unpack", 10, f"{prefix}_dur_sig"),
        line(f"{prefix}_note_sig", 0, f"{prefix}_makenote"),
        line(f"{prefix}_vel_clip", 0, f"{prefix}_vel_sig"),
        line(f"{prefix}_vel_sig", 0, f"{prefix}_makenote", 1),
        line(f"{prefix}_dur_sig", 0, f"{prefix}_makenote", 2),
        line(f"{prefix}_click", 0, f"{prefix}_makenote", 4),
        line(f"{prefix}_makenote", 2, "midiout"),
        line(f"{prefix}_mtof", 0, f"{prefix}_osc"),
        line(f"{prefix}_env_message", 0, f"{prefix}_env"),
        line(f"{prefix}_osc", 0, f"{prefix}_vca"),
        line(f"{prefix}_env", 0, f"{prefix}_vca", 1),
        line(f"{prefix}_vca", 0, "audio_level"),
        line(f"{prefix}_note_default", 0, f"{prefix}_note_sig"),
        line(f"{prefix}_note_default", 0, f"{prefix}_mtof"),
        line(f"{prefix}_vel_default", 0, f"{prefix}_vel_clip"),
        line(f"{prefix}_dur_default", 0, f"{prefix}_dur_sig"),
    ])


add_tick_lane("correlate", 0, 270, [0.10, 0.28, 0.24, 0.75], "cycle~")
add_tick_lane("differentiate", 1, 500, [0.30, 0.13, 0.20, 0.75], "tri~")

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [70, 60, 1040, 840],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "OpenSoundControl.mxo", "type": "iLaX"},
            {"name": "qmw_correlation_tick_router_v2.js", "type": "TEXT"},
            {"name": "rtt.makenote~.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

OUTPUT.write_text(json.dumps(patcher, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
