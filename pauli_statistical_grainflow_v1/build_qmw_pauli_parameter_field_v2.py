#!/usr/bin/env python3
"""Build the 24-slot Pauli parameter-field Grainflow instrument."""

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
        box("title", "comment", [20., 14., 1160., 28.], text="QMW PAULI PARAMETER-FIELD GRAINFLOW v2 — 6 STREAMS × 4 GRAINS", fontsize=18.),
        box("subtitle", "comment", [20., 45., 1150., 38.], text="Twenty-four stable slots preserve stream and grain identity. Statistics determines occupation; the energy shell determines rate; coherence and entropy determine temporal order versus randomized lookup."),
        box("source", "newobj", [20., 95., 390., 22.], text="buffer~ qmw_pauli_source CP_Bubbling_Pasta_Sauce.wav", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("rates_buf", "newobj", [20., 128., 290., 22.], text="buffer~ qmw_pauli_rates @samps 25", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("delays_buf", "newobj", [325., 128., 290., 22.], text="buffer~ qmw_pauli_delays @samps 25", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("windows_buf", "newobj", [630., 128., 300., 22.], text="buffer~ qmw_pauli_windows @samps 25", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("clock", "flonum", [20., 180., 72., 22.], minimum=0.1, maximum=100., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("clock_label", "comment", [100., 183., 72., 20.], text="clock Hz"),
        box("clock_sig", "newobj", [180., 180., 88., 22.], text="phasor~ 7.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("scan", "flonum", [290., 180., 72., 22.], minimum=-4., maximum=4., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("scan_label", "comment", [370., 183., 65., 20.], text="scan Hz"),
        box("scan_sig", "newobj", [445., 180., 88., 22.], text="phasor~ 0.1", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("scalar_rate", "newobj", [550., 180., 62., 22.], text="sig~ 1.", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("enable", "toggle", [635., 179., 24., 24.], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("enable_label", "comment", [667., 183., 62., 20.], text="enable"),
        box("mode", "umenu", [750., 180., 205., 22.], items=["0 scalar", ",", "1 deterministic slots", ",", "2 random lookup"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("mode_pre", "newobj", [970., 180., 92., 22.], text="prepend mode", numinlets=1, numoutlets=1, outlettype=[""]),
        box("grain", "newobj", [20., 225., 330., 22.], text="grainflow~ qmw_pauli_source 24 grainflow.Hanning.aif", numinlets=4, numoutlets=9, outlettype=["multichannelsignal", "list"] + ["multichannelsignal"] * 7),
        box("amp_mc", "newobj", [370., 225., 135., 22.], text="mc.sig~ 0. @chans 24", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("amp_smooth", "newobj", [520., 225., 115., 22.], text="mc.slide~ 80 80", numinlets=3, numoutlets=1, outlettype=["multichannelsignal"]),
        box("pan", "newobj", [20., 265., 190., 22.], text="grainflow.util.stereoPan~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("unpack", "newobj", [20., 305., 92., 22.], text="mc.unpack~ 2", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("gain_l", "newobj", [20., 342., 55., 22.], text="*~ 0.24", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_r", "newobj", [125., 342., 55., 22.], text="*~ 0.24", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("dac", "ezdac~", [220., 325., 52., 52.], numinlets=2, numoutlets=0),
        box("metadata", "message", [370., 265., 650., 22.], text="grain metadata", numinlets=2, numoutlets=1, outlettype=[""]),
        box("writer", "newobj", [20., 405., 275., 22.], text="js qmw_pauli_parameter_field_v2.js", numinlets=1, numoutlets=8, outlettype=[""] * 8),
        box("status", "message", [315., 405., 755., 42.], text="waiting for Pauli field...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("preset", "umenu", [20., 465., 135., 22.], items=["normal", ",", "sodium_d1", ",", "sodium_d2"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("preset_pre", "newobj", [165., 465., 102., 22.], text="prepend preset", numinlets=1, numoutlets=1, outlettype=[""]),
        box("stats", "umenu", [285., 465., 120., 22.], items=["fermion", ",", "boson", ",", "classical"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("stats_pre", "newobj", [415., 465., 115., 22.], text="prepend statistics", numinlets=1, numoutlets=1, outlettype=[""]),
        box("particles", "number", [550., 465., 55., 22.], minimum=0, maximum=16, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("particles_pre", "newobj", [615., 465., 110., 22.], text="prepend particles", numinlets=1, numoutlets=1, outlettype=[""]),
        box("resample", "button", [745., 464., 24., 24.], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box("resample_label", "comment", [777., 468., 155., 20.], text="sample occupation"),
        box("field", "flonum", [20., 505., 65., 22.], minimum=0., maximum=20., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("field_pre", "newobj", [95., 505., 88., 22.], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""]),
        box("center", "flonum", [200., 505., 65., 22.], minimum=-20., maximum=20., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("center_pre", "newobj", [275., 505., 95., 22.], text="prepend center", numinlets=1, numoutlets=1, outlettype=[""]),
        box("width", "flonum", [390., 505., 65., 22.], minimum=0., maximum=40., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("width_pre", "newobj", [465., 505., 92., 22.], text="prepend width", numinlets=1, numoutlets=1, outlettype=[""]),
        box("entropy", "flonum", [580., 505., 65., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("entropy_pre", "newobj", [655., 505., 102., 22.], text="prepend entropy", numinlets=1, numoutlets=1, outlettype=[""]),
        box("coherence", "flonum", [780., 505., 65., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("coherence_pre", "newobj", [855., 505., 112., 22.], text="prepend coherence", numinlets=1, numoutlets=1, outlettype=[""]),
        box("occupation", "multislider", [20., 555., 1050., 42.], size=6, setminmax=[0., 8.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("rate_label", "comment", [20., 620., 340., 20.], text="24 RATE SLOTS — stream energy plus within-stream deviation"),
        box("rate_view", "multislider", [20., 642., 500., 48.], size=24, setminmax=[0.125, 8.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("delay_label", "comment", [550., 620., 300., 20.], text="24 DELAY SLOTS — shell phase positions"),
        box("delay_view", "multislider", [550., 642., 500., 48.], size=24, setminmax=[-5588., 0.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("window_label", "comment", [20., 710., 300., 20.], text="24 WINDOW-OFFSET SLOTS"),
        box("window_view", "multislider", [20., 732., 500., 48.], size=24, setminmax=[0., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("amp_label", "comment", [550., 710., 330., 20.], text="24 AMPLITUDE SLOTS — occupation weights"),
        box("amp_view", "multislider", [550., 732., 500., 48.], size=24, setminmax=[0., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),
    ]
    # Declarative defaults keep the generated patch compact and inspectable.
    defaults = [("clock", "7."), ("scan", "0.1"), ("enable", "1"), ("mode", "1"), ("preset", "0"), ("stats", "0"), ("particles", "2"), ("field", "1."), ("center", "0."), ("width", "4."), ("entropy", "0.25"), ("coherence", "0.8")]
    for index, (target, value) in enumerate(defaults):
        boxes.append(box("init_" + target, "newobj", [20. + index * 86., 820., 80., 22.], text="loadmess " + value, numinlets=1, numoutlets=1, outlettype=[""]))

    lines = [
        line("clock", 0, "clock_sig"), line("scan", 0, "scan_sig"), line("clock_sig", 0, "grain", 0), line("scan_sig", 0, "grain", 1), line("scalar_rate", 0, "grain", 2), line("amp_mc", 0, "amp_smooth"), line("amp_smooth", 0, "grain", 3), line("enable", 0, "grain"),
        line("grain", 0, "pan"), line("grain", 2, "pan", 1), line("grain", 1, "metadata", 1), line("pan", 0, "unpack"), line("unpack", 0, "gain_l"), line("unpack", 1, "gain_r"), line("gain_l", 0, "dac"), line("gain_r", 0, "dac", 1),
        line("mode", 0, "mode_pre"), line("mode_pre", 0, "writer"), line("preset", 1, "preset_pre"), line("preset_pre", 0, "writer"), line("stats", 1, "stats_pre"), line("stats_pre", 0, "writer"), line("particles", 0, "particles_pre"), line("particles_pre", 0, "writer"), line("resample", 0, "writer"),
        line("field", 0, "field_pre"), line("field_pre", 0, "writer"), line("center", 0, "center_pre"), line("center_pre", 0, "writer"), line("width", 0, "width_pre"), line("width_pre", 0, "writer"), line("entropy", 0, "entropy_pre"), line("entropy_pre", 0, "writer"), line("coherence", 0, "coherence_pre"), line("coherence_pre", 0, "writer"),
        line("writer", 0, "rate_view"), line("writer", 1, "delay_view"), line("writer", 2, "window_view"), line("writer", 3, "amp_view"), line("writer", 4, "amp_mc"), line("writer", 5, "grain"), line("writer", 6, "occupation"), line("writer", 7, "status", 1),
    ]
    for target, _value in defaults:
        lines.append(line("init_" + target, 0, target))

    return {"patcher": {"fileversion": 1, "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1}, "classnamespace": "box", "rect": [55., 35., 1110., 900.], "boxes": boxes, "lines": lines, "dependency_cache": [
        {"name": "CP_Bubbling_Pasta_Sauce.wav", "type": "WAVE"}, {"name": "grainflow.Hanning.aif", "type": "AIFF"}, {"name": "grainflow~.mxo", "type": "iLaX"}, {"name": "grainflow.util.stereoPan~.maxpat", "type": "JSON"}, {"name": "qmw_pauli_parameter_field_v2.js", "type": "TEXT"}], "autosave": 0}}


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
    output = ROOT / "QMW_Pauli_Parameter_Field_Grainflow_v2.maxpat"
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
