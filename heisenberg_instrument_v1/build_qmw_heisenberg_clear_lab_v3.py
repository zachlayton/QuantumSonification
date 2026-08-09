#!/usr/bin/env python3
"""Build the clear one-qubit Heisenberg measurement laboratory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def build() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [25., 14., 1100., 28.], text="QMW HEISENBERG MEASUREMENT LAB v3 — ONE QUBIT / FOUR AUDIBLE CELLS", fontsize=18.),
        box("thesis", "comment", [25., 45., 1110., 42.], text="One question only: how does an intermediate measurement alter the later state? Preparation, later evolution, observable A=(X+Z)/√2, frequencies, gain, panning, and CNMAT renderer remain identical in all three cases."),
        box("pipeline", "comment", [25., 92., 1100., 25.], text="|0〉  →  Ry(π/2)  →  [NO MEASUREMENT / UNREAD Z / RECORDED Z]  →  Ry(−π/2)  →  same observable A", fontsize=14.),
        box("coherent_text", "comment", [25., 128., 350., 52.], text="COHERENT\nNo intermediate observation. The two alternatives remain available to interfere."),
        box("unread_text", "comment", [395., 128., 350., 52.], text="UNREAD\nA Z observation occurs, but its result is discarded. Coherence is lost; no single result remains."),
        box("recorded_text", "comment", [765., 128., 350., 52.], text="RECORDED\nOne Z result is retained. The later state is pure but conditioned on that particular result."),
        box("udp", "newobj", [25., 195., 126., 22.], text="udpreceive 7420", numinlets=1, numoutlets=1, outlettype=[""]),
        box("route_qmw", "newobj", [165., 195., 104., 22.], text="OSC-route /qmw", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_h", "newobj", [285., 195., 185., 22.], text="OSC-route /heisenberg_clear", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_active", "newobj", [485., 195., 125., 22.], text="OSC-route /active", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_meta", "newobj", [25., 235., 865., 22.], text="OSC-route /mode /outcome /final_probabilities /bloch /purity /coherence /disturbance /expectation /matrix", numinlets=1, numoutlets=10, outlettype=[""] * 10),
        box("route_matrix", "newobj", [25., 275., 720., 22.], text="OSC-route /begin /end /real /imag /magnitude /phase /frequency_hz /pan", numinlets=1, numoutlets=9, outlettype=[""] * 9),
        box("pre_mode", "newobj", [910., 235., 105., 22.], text="prepend mode", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_outcome", "newobj", [1025., 235., 120., 22.], text="prepend outcome", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_probs", "newobj", [760., 275., 175., 22.], text="prepend final_probabilities", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_purity", "newobj", [950., 275., 105., 22.], text="prepend purity", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_coherence", "newobj", [1065., 275., 135., 22.], text="prepend coherence", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_expect", "newobj", [950., 310., 130., 22.], text="prepend expectation", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_begin", "newobj", [25., 312., 105., 22.], text="prepend begin", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_end", "newobj", [140., 312., 95., 22.], text="prepend end", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_real", "newobj", [245., 312., 95., 22.], text="prepend real", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_mag", "newobj", [350., 312., 125., 22.], text="prepend magnitude", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_freq", "newobj", [485., 312., 145., 22.], text="prepend frequency_hz", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_pan", "newobj", [640., 312., 95., 22.], text="prepend pan", numinlets=1, numoutlets=1, outlettype=[""]),
        box("renderer", "newobj", [25., 360., 290., 22.], text="js qmw_heisenberg_clear_renderer_v3.js", numinlets=1, numoutlets=4, outlettype=[""] * 4),
        box("sin_l", "newobj", [25., 405., 105., 22.], text="sinusoids~ bwe", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("sin_r", "newobj", [150., 405., 105., 22.], text="sinusoids~ bwe", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("gain_l", "newobj", [25., 445., 52., 22.], text="*~ 0.65", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_r", "newobj", [150., 445., 52., 22.], text="*~ 0.65", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [225., 425., 18., 60.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [252., 425., 18., 60.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [290., 425., 52., 52.], numinlets=2, numoutlets=0),
        box("matrix_label", "comment", [395., 355., 340., 20.], text="C[m,n] = ρ[m,n] A[n,m] — real contribution"),
        box("matrix", "jit.cellblock", [395., 380., 350., 220.], cols=2, rows=2, colhead=1, rowhead=1, numinlets=2, numoutlets=4, outlettype=[""] * 4),
        box("cell_legend", "comment", [765., 365., 385., 86.], text="CELL MEANING\n(0,0) population of |0〉 — 110 Hz\n(0,1) and (1,0) coherence — 440 Hz, opposite sides\n(1,1) population of |1〉 — 165 Hz"),
        box("status", "message", [765., 465., 385., 68.], text="waiting for one-qubit state...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("bloch_label", "comment", [765., 550., 165., 20.], text="final Bloch vector x / y / z"),
        box("bloch", "multislider", [765., 575., 385., 42.], size=3, setminmax=[-1., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("prob_label", "comment", [765., 630., 220., 20.], text="final probabilities P(0), P(1)"),
        box("prob_view", "multislider", [765., 655., 385., 42.], size=2, setminmax=[0., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("controls", "comment", [25., 625., 680., 22.], text="CHANGE ONLY THE INTERMEDIATE MEASUREMENT PROTOCOL", fontsize=14.),
        box("coherent", "message", [25., 660., 245., 22.], text="/qmw/heisenberg_clear/mode coherent", numinlets=2, numoutlets=1, outlettype=[""]),
        box("unread", "message", [25., 695., 235., 22.], text="/qmw/heisenberg_clear/mode unread", numinlets=2, numoutlets=1, outlettype=[""]),
        box("recorded", "message", [25., 730., 250., 22.], text="/qmw/heisenberg_clear/mode recorded", numinlets=2, numoutlets=1, outlettype=[""]),
        box("record", "message", [295., 730., 215., 22.], text="/qmw/heisenberg_clear/record 1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("send", "newobj", [530., 730., 160., 22.], text="udpsend 127.0.0.1 7421", numinlets=1, numoutlets=0),
        box("compare_toggle", "toggle", [25., 780., 24., 24.], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("compare_label", "comment", [58., 783., 170., 20.], text="slow comparison (6 sec)"),
        box("compare_metro", "newobj", [240., 780., 82., 22.], text="metro 6000", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("compare_counter", "newobj", [335., 780., 82., 22.], text="counter 0 2", numinlets=5, numoutlets=4, outlettype=["int", "", "", "int"]),
        box("compare_sel", "newobj", [430., 780., 62., 22.], text="sel 0 1 2", numinlets=1, numoutlets=4, outlettype=["bang", "bang", "bang", ""]),
        box("rule", "comment", [25., 830., 1125., 38.], text="AUDITION RULE: do not interpret timbral presets—there are none. The two CNMAT banks receive the same four cell frequencies and the same mapping in every case. What changes is only the density matrix produced by the measurement protocol."),
    ]
    lines = [
        line("udp", 0, "route_qmw"), line("route_qmw", 0, "route_h"), line("route_h", 0, "route_active"), line("route_active", 0, "route_meta"), line("route_meta", 8, "route_matrix"),
        line("route_meta", 0, "pre_mode"), line("route_meta", 1, "pre_outcome"), line("route_meta", 2, "pre_probs"), line("route_meta", 2, "prob_view"), line("route_meta", 3, "bloch"), line("route_meta", 4, "pre_purity"), line("route_meta", 5, "pre_coherence"), line("route_meta", 7, "pre_expect"),
        line("route_matrix", 0, "pre_begin"), line("route_matrix", 1, "pre_end"), line("route_matrix", 2, "pre_real"), line("route_matrix", 4, "pre_mag"), line("route_matrix", 6, "pre_freq"), line("route_matrix", 7, "pre_pan"),
        line("pre_mode", 0, "renderer"), line("pre_outcome", 0, "renderer"), line("pre_probs", 0, "renderer"), line("pre_purity", 0, "renderer"), line("pre_coherence", 0, "renderer"), line("pre_expect", 0, "renderer"), line("pre_begin", 0, "renderer"), line("pre_end", 0, "renderer"), line("pre_real", 0, "renderer"), line("pre_mag", 0, "renderer"), line("pre_freq", 0, "renderer"), line("pre_pan", 0, "renderer"),
        line("renderer", 0, "sin_l"), line("renderer", 1, "sin_r"), line("renderer", 2, "matrix"), line("renderer", 3, "status", 1), line("sin_l", 0, "gain_l"), line("sin_r", 0, "gain_r"), line("gain_l", 0, "meter_l"), line("gain_r", 0, "meter_r"), line("gain_l", 0, "dac"), line("gain_r", 0, "dac", 1),
        line("coherent", 0, "send"), line("unread", 0, "send"), line("recorded", 0, "send"), line("record", 0, "send"), line("compare_toggle", 0, "compare_metro"), line("compare_metro", 0, "compare_counter"), line("compare_counter", 0, "compare_sel"), line("compare_sel", 0, "coherent"), line("compare_sel", 1, "unread"), line("compare_sel", 2, "recorded"),
    ]
    return {"patcher": {"fileversion": 1, "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1}, "classnamespace": "box", "rect": [55., 30., 1200., 910.], "boxes": boxes, "lines": lines, "dependency_cache": [{"name": "OSC-route.mxo", "type": "iLaX"}, {"name": "sinusoids~.mxo", "type": "iLaX"}, {"name": "qmw_heisenberg_clear_renderer_v3.js", "type": "TEXT"}], "autosave": 0}}


def validate(document: dict[str, Any]) -> None:
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    if len(boxes) != len(patcher["boxes"]): raise RuntimeError("duplicate identifiers")
    for entry in patcher["lines"]:
        source, outlet = entry["patchline"]["source"]; destination, inlet = entry["patchline"]["destination"]
        if source not in boxes or destination not in boxes: raise RuntimeError(f"dangling line {source}->{destination}")
        if outlet >= boxes[source].get("numoutlets", 0) or inlet >= boxes[destination].get("numinlets", 0): raise RuntimeError(f"invalid line {source}[{outlet}]->{destination}[{inlet}]")


def main() -> int:
    document = build(); validate(document)
    output = ROOT / "QMW_Heisenberg_Measurement_Lab_v3_Clear.maxpat"
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
