#!/usr/bin/env python3
"""Build the standalone QMW Quantum Temporal RTT v1 Max patch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Quantum_Temporal_RTT_v1.maxpat"


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source: str, outlet: int, destination: str, inlet: int = 0, order: int | None = None) -> dict[str, Any]:
    edge: dict[str, Any] = {"source": [source, outlet], "destination": [destination, inlet]}
    if order is not None:
        edge["order"] = order
    return {"patchline": edge}


boxes: list[dict[str, Any]] = [
    box("title", "comment", [25, 15, 940, 28], text="QMW QUANTUM TEMPORAL COMPOSITION · RTT RELATIONAL REALIZER v1", fontsize=17.0),
    box("concept", "comment", [25, 48, 1040, 42], text="OSC observations reconstruct independent signal-rate phases. RTT transforms each local phase; no bar/beat transport is present. rtt.clock~ is a confidence-controlled fallback only."),
    box("udp", "newobj", [25, 105, 145, 22], text="udpreceive 7442", numinlets=1, numoutlets=1, outlettype=["FullPacket"]),
    box("route", "newobj", [185, 105, 850, 22], text="OSC-route /qmw/temporal/v1/clock /qmw/temporal/v1/conditional/purity /qmw/temporal/v1/process/resonance /qmw/temporal/v1/process/memory /qmw/temporal/v1/process/spatial /qmw/temporal/v1/event /qmw/temporal/v1/branch /qmw/temporal/v1/snapshot/begin /qmw/temporal/v1/snapshot/end", numinlets=1, numoutlets=10, outlettype=[""] * 10),
    box("global_loadbang", "newobj", [940, 205, 65, 22], text="loadbang", numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("clock_unpack", "newobj", [25, 145, 105, 22], text="unpack f f f", numinlets=1, numoutlets=3, outlettype=["float"] * 3),
    box("clock_phase_label", "comment", [25, 174, 88, 20], text="clock phase"),
    box("clock_phase", "flonum", [115, 172, 76, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("confidence_label", "comment", [215, 174, 105, 20], text="clock confidence"),
    box("confidence", "flonum", [325, 172, 76, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("prob_label", "comment", [425, 174, 126, 20], text="conditional probability"),
    box("clock_probability", "flonum", [555, 172, 76, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("purity_label", "comment", [655, 174, 105, 20], text="conditional purity"),
    box("purity", "flonum", [765, 172, 76, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("clock_note", "comment", [325, 205, 570, 20], text="Clock confidence is diagnostic; each subsystem below owns an independent relational rtt.clock~."),
    box("event_send", "newobj", [855, 145, 155, 22], text="s qmw.temporal.event", numinlets=1, numoutlets=0),
    box("branch_send", "newobj", [855, 172, 160, 22], text="s qmw.temporal.branch", numinlets=1, numoutlets=0),
    box("dsp_toggle", "toggle", [25, 905, 26, 26], numinlets=1, numoutlets=1, outlettype=["int"]),
    box("dsp", "newobj", [60, 907, 52, 22], text="ezdac~", numinlets=2, numoutlets=0),
    box("dsp_note", "comment", [125, 908, 330, 20], text="Turn DSP on: RTT objects and phase reconstruction are signal-rate."),
    box("audio_receive", "newobj", [480, 905, 190, 22], text="receive~ qmw.temporal.audio", numinlets=0, numoutlets=1, outlettype=["signal"]),
    box("audio_gain", "newobj", [685, 905, 62, 22], text="*~ 0.7", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("midiout", "newobj", [920, 905, 60, 22], text="midiout", numinlets=1, numoutlets=0),
]

lines: list[dict[str, Any]] = [
    line("udp", 0, "route"),
    line("route", 0, "clock_unpack"),
    line("clock_unpack", 0, "clock_phase"),
    line("clock_unpack", 1, "confidence"),
    line("clock_unpack", 2, "clock_probability"),
    line("route", 1, "purity"),
    line("route", 5, "event_send"),
    line("route", 6, "branch_send"),
    line("dsp_toggle", 0, "dsp"),
    line("audio_receive", 0, "audio_gain"),
    line("audio_gain", 0, "dsp"),
    line("audio_gain", 0, "dsp", 1),
]


def add_lane(name: str, route_outlet: int, y: float, color: list[float], seed: int, notes: str) -> None:
    prefix = name
    title = name.upper()
    boxes.extend([
        box(f"{prefix}_panel", "panel", [20, y - 10, 1020, 188], bgcolor=color, border=1, numinlets=1, numoutlets=0),
        box(f"{prefix}_title", "comment", [30, y, 150, 22], text=f"{title} LOCAL TIME", fontsize=14.0),
        box(f"{prefix}_unpack", "newobj", [30, y + 30, 145, 22], text="unpack f f f f f", numinlets=1, numoutlets=5, outlettype=["float"] * 5),
        box(f"{prefix}_unwrap", "newobj", [190, y + 30, 235, 22], text=f"js qmw_relational_phase_unwrap_v1.js {name}", numinlets=1, numoutlets=2, outlettype=["float", "float"]),
        box(f"{prefix}_phase_value", "flonum", [440, y + 30, 72, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_bpm_value", "flonum", [525, y + 30, 72, 22], minimum=8.0, maximum=480.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_bpm_message", "newobj", [610, y + 30, 82, 22], text="prepend bpm", numinlets=1, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_clock", "newobj", [705, y + 30, 70, 22], text="rtt.clock~", numinlets=4, numoutlets=2, outlettype=["signal", "signal"]),
        box(f"{prefix}_loop", "newobj", [775, y + 30, 68, 22], text="rtt.loop~", numinlets=2, numoutlets=2, outlettype=["signal", "signal"]),
        box(f"{prefix}_binary", "newobj", [855, y + 30, 78, 22], text="rtt.binary~", numinlets=2, numoutlets=2, outlettype=["signal", "signal"]),
        box(f"{prefix}_rprob", "newobj", [945, y + 30, 78, 22], text="rtt.rprob~", numinlets=2, numoutlets=2, outlettype=["signal", "signal"]),
        box(f"{prefix}_corr_label", "comment", [30, y + 67, 70, 20], text="correlation"),
        box(f"{prefix}_corr", "flonum", [102, y + 65, 62, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_sal_label", "comment", [180, y + 67, 55, 20], text="salience"),
        box(f"{prefix}_sal", "flonum", [240, y + 65, 62, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_sal_map", "newobj", [315, y + 65, 210, 22], text="expr min(0.98, 0.25 + 0.75*$f1)", numinlets=1, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_sal_message", "newobj", [315, y + 90, 190, 22], text="prepend message probabilities", numinlets=1, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_drive_label", "comment", [375, y + 67, 88, 20], text="quantum drive"),
        box(f"{prefix}_drive", "flonum", [465, y + 65, 62, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box(f"{prefix}_scope", "live.scope~", [545, y + 65, 225, 42], numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_sequence", "newobj", [785, y + 70, 90, 22], text="rtt.sequence~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_makenote", "newobj", [890, y + 70, 132, 22], text="rtt.makenote~ @duration 320 @velocity 100", numinlets=5, numoutlets=3, outlettype=["", "", ""]),
        box(f"{prefix}_send", "newobj", [785, y + 105, 190, 22], text=f"s~ qmw.temporal.{name}.trigger", numinlets=1, numoutlets=0),
        box(f"{prefix}_edge", "newobj", [980, y + 105, 45, 22], text="edge~", numinlets=1, numoutlets=2, outlettype=["bang", "bang"]),
        box(f"{prefix}_indicator", "button", [1030, y + 104, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box(f"{prefix}_midiparse", "newobj", [650, y + 142, 112, 22], text="midiparse @hires 1", numinlets=1, numoutlets=8, outlettype=["", "", "", "int", "int", "", "int", ""]),
        box(f"{prefix}_note_unpack", "newobj", [775, y + 142, 68, 22], text="unpack i i", numinlets=1, numoutlets=2, outlettype=["int", "int"]),
        box(f"{prefix}_mtof", "newobj", [855, y + 142, 38, 22], text="mtof", numinlets=1, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_osc", "newobj", [905, y + 142, 48, 22], text="cycle~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_vel_norm", "newobj", [775, y + 168, 38, 22], text="/ 127.", numinlets=2, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_env_pack", "newobj", [823, y + 168, 68, 22], text="pack f 12", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_env", "newobj", [900, y + 168, 42, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_vca", "newobj", [952, y + 142, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_level", "newobj", [995, y + 142, 48, 22], text="*~ 0.12", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_audio_send", "newobj", [995, y + 168, 190, 22], text="send~ qmw.temporal.audio", numinlets=1, numoutlets=0),
        box(f"{prefix}_loop_init", "message", [30, y + 112, 170, 22], text="subdiv 16, steps 9", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_binary_init", "message", [210, y + 112, 150, 22], text=f"steps 9, seed {seed}", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_rprob_init", "message", [370, y + 112, 270, 22], text="output input, message probabilities 0.75", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_clock_init", "message", [30, y + 142, 245, 22], text="transportstate 1, barlength 1, bpm 60", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_notes", "message", [555, y + 118, 210, 22], text=notes, numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_notes_load", "newobj", [555, y + 145, 70, 22], text="loadbang", numinlets=1, numoutlets=1, outlettype=["bang"]),
    ])
    lines.extend([
        line("route", route_outlet, f"{prefix}_unpack"),
        line(f"{prefix}_unpack", 0, f"{prefix}_unwrap"),
        line(f"{prefix}_unpack", 2, f"{prefix}_corr"),
        line(f"{prefix}_unpack", 3, f"{prefix}_sal"),
        line(f"{prefix}_unpack", 3, f"{prefix}_sal_map"),
        line(f"{prefix}_sal_map", 0, f"{prefix}_sal_message"),
        line(f"{prefix}_unpack", 4, f"{prefix}_drive"),
        line(f"{prefix}_unwrap", 0, f"{prefix}_phase_value"),
        line(f"{prefix}_unwrap", 1, f"{prefix}_bpm_value"),
        line(f"{prefix}_unwrap", 1, f"{prefix}_bpm_message"),
        line(f"{prefix}_bpm_message", 0, f"{prefix}_clock"),
        line(f"{prefix}_clock_init", 0, f"{prefix}_clock"),
        line(f"{prefix}_clock", 0, f"{prefix}_loop"),
        line(f"{prefix}_clock", 0, f"{prefix}_scope"),
        line(f"{prefix}_loop", 1, f"{prefix}_binary"),
        line(f"{prefix}_binary", 1, f"{prefix}_rprob"),
        line(f"{prefix}_sal_message", 0, f"{prefix}_rprob"),
        line(f"{prefix}_rprob", 0, f"{prefix}_sequence"),
        line(f"{prefix}_rprob", 0, f"{prefix}_send"),
        line(f"{prefix}_rprob", 0, f"{prefix}_edge"),
        line(f"{prefix}_edge", 0, f"{prefix}_indicator"),
        line(f"{prefix}_sequence", 0, f"{prefix}_makenote"),
        line(f"{prefix}_rprob", 0, f"{prefix}_makenote", 1),
        line(f"{prefix}_makenote", 2, "midiout"),
        line(f"{prefix}_makenote", 2, f"{prefix}_midiparse"),
        line(f"{prefix}_midiparse", 0, f"{prefix}_note_unpack"),
        line(f"{prefix}_note_unpack", 0, f"{prefix}_mtof"),
        line(f"{prefix}_mtof", 0, f"{prefix}_osc"),
        line(f"{prefix}_note_unpack", 1, f"{prefix}_vel_norm"),
        line(f"{prefix}_vel_norm", 0, f"{prefix}_env_pack"),
        line(f"{prefix}_env_pack", 0, f"{prefix}_env"),
        line(f"{prefix}_osc", 0, f"{prefix}_vca"),
        line(f"{prefix}_env", 0, f"{prefix}_vca", 1),
        line(f"{prefix}_vca", 0, f"{prefix}_level"),
        line(f"{prefix}_level", 0, f"{prefix}_audio_send"),
        line("global_loadbang", 0, f"{prefix}_clock_init"),
        line("global_loadbang", 0, f"{prefix}_loop_init"),
        line("global_loadbang", 0, f"{prefix}_binary_init"),
        line("global_loadbang", 0, f"{prefix}_rprob_init"),
        line(f"{prefix}_loop_init", 0, f"{prefix}_loop"),
        line(f"{prefix}_binary_init", 0, f"{prefix}_binary"),
        line(f"{prefix}_rprob_init", 0, f"{prefix}_rprob"),
        line(f"{prefix}_notes_load", 0, f"{prefix}_notes"),
        line(f"{prefix}_notes", 0, f"{prefix}_sequence", 1),
    ])


add_lane("resonance", 2, 270, [0.12, 0.20, 0.27, 0.72], 179, "0 2 7 5 9 12 7 14, low 36, high 60, offset 36, stepsize 1")
add_lane("memory", 3, 470, [0.24, 0.16, 0.28, 0.72], 271, "0 3 7 10 5 12 8 15, low 48, high 72, offset 48, stepsize 1")
add_lane("spatial", 4, 670, [0.14, 0.27, 0.22, 0.72], 431, "0 5 9 14 7 12 16 19, low 60, high 84, offset 60, stepsize 1")

patch = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [60, 60, 1080, 960],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_relational_phase_unwrap_v1.js", "type": "TEXT"},
            {"name": "rtt.clock~.mxo", "type": "iLaX"},
            {"name": "rtt.loop~.mxo", "type": "iLaX"},
            {"name": "rtt.binary~.mxo", "type": "iLaX"},
            {"name": "rtt.rprob~.mxo", "type": "iLaX"},
            {"name": "rtt.sequence~.mxo", "type": "iLaX"},
            {"name": "rtt.makenote~.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

OUTPUT.write_text(json.dumps(patch, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
