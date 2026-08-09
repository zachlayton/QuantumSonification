#!/usr/bin/env python3
"""Build the eight-voice field-directed Grainflow parameter-buffer lab."""

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
        box("title", "comment", [20., 14., 1100., 28.], text="QMW FIELD-DIRECTED GRAINFLOW — 8-VOICE PARAMETER FIELDS v1", fontsize=18.),
        box("subtitle", "comment", [20., 45., 1100., 38.], text="Each grain voice reads a stable slot from named rate, traversal-delay, and window-offset buffers. Amplitude is an eight-channel signal field. Mode 1 preserves assignments; mode 2 samples the same fields statistically."),
        box("source", "newobj", [20., 95., 390., 22.], text="buffer~ qmw_fdg_source CP_Bubbling_Pasta_Sauce.wav", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("rates_buf", "newobj", [20., 128., 285., 22.], text="buffer~ qmw_fdg_rates @samps 9", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("delays_buf", "newobj", [320., 128., 285., 22.], text="buffer~ qmw_fdg_delays @samps 9", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("windows_buf", "newobj", [620., 128., 295., 22.], text="buffer~ qmw_fdg_windows @samps 9", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),

        box("clock_label", "comment", [20., 178., 85., 20.], text="grain clock"),
        box("clock", "flonum", [108., 175., 72., 22.], minimum=0.1, maximum=100., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("clock_sig", "newobj", [190., 175., 82., 22.], text="phasor~ 8.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("scan_label", "comment", [300., 178., 78., 20.], text="source scan"),
        box("scan", "flonum", [380., 175., 72., 22.], minimum=-4., maximum=4., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("scan_sig", "newobj", [462., 175., 82., 22.], text="phasor~ 0.12", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("enable", "toggle", [570., 174., 24., 24.], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("enable_label", "comment", [602., 178., 72., 20.], text="granulator"),
        box("mode_label", "comment", [700., 178., 45., 20.], text="mode"),
        box("mode", "umenu", [748., 175., 215., 22.], items=["0 scalar", ",", "1 deterministic field", ",", "2 random field lookup"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("mode_pre", "newobj", [975., 175., 92., 22.], text="prepend mode", numinlets=1, numoutlets=1, outlettype=[""]),

        box("grain", "newobj", [20., 225., 320., 22.], text="grainflow~ qmw_fdg_source 8 grainflow.Hanning.aif", numinlets=4, numoutlets=9, outlettype=["multichannelsignal", "list"] + ["multichannelsignal"] * 7),
        box("scalar_rate", "newobj", [635., 225., 62., 22.], text="sig~ 1.", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("amp_mc", "newobj", [365., 225., 128., 22.], text="mc.sig~ 0. @chans 8", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("amp_smooth", "newobj", [505., 225., 115., 22.], text="mc.slide~ 80 80", numinlets=3, numoutlets=1, outlettype=["multichannelsignal"]),
        box("pan", "newobj", [20., 265., 190., 22.], text="grainflow.util.stereoPan~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("unpack", "newobj", [20., 305., 92., 22.], text="mc.unpack~ 2", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("gain_l", "newobj", [20., 345., 55., 22.], text="*~ 0.28", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_r", "newobj", [125., 345., 55., 22.], text="*~ 0.28", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [205., 325., 18., 55.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [232., 325., 18., 55.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [275., 325., 52., 52.], numinlets=2, numoutlets=0),
        box("metadata", "message", [365., 265., 610., 22.], text="grain metadata", numinlets=2, numoutlets=1, outlettype=[""]),

        box("field_title", "comment", [20., 410., 920., 22.], text="QUANTUM FIELD INPUT — local controls and /qmw/density_field OSC drive the same writer", fontsize=14.),
        box("mag_label", "comment", [20., 447., 72., 20.], text="magnitude"),
        box("mag", "flonum", [95., 444., 72., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("mag_pre", "newobj", [175., 444., 112., 22.], text="prepend magnitude", numinlets=1, numoutlets=1, outlettype=[""]),
        box("phase_label", "comment", [310., 447., 48., 20.], text="phase"),
        box("phase", "flonum", [360., 444., 72., 22.], minimum=-6.2832, maximum=6.2832, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("phase_pre", "newobj", [440., 444., 92., 22.], text="prepend phase", numinlets=1, numoutlets=1, outlettype=[""]),
        box("purity_label", "comment", [555., 447., 48., 20.], text="purity"),
        box("purity", "flonum", [605., 444., 72., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("purity_pre", "newobj", [685., 444., 92., 22.], text="prepend purity", numinlets=1, numoutlets=1, outlettype=[""]),
        box("entropy_label", "comment", [800., 447., 55., 20.], text="entropy"),
        box("entropy", "flonum", [858., 444., 72., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("entropy_pre", "newobj", [938., 444., 102., 22.], text="prepend entropy", numinlets=1, numoutlets=1, outlettype=[""]),
        box("coherence_label", "comment", [20., 482., 72., 20.], text="coherence"),
        box("coherence", "flonum", [95., 479., 72., 22.], minimum=0., maximum=1., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("coherence_pre", "newobj", [175., 479., 112., 22.], text="prepend coherence", numinlets=1, numoutlets=1, outlettype=[""]),
        box("duration_label", "comment", [310., 482., 120., 20.], text="source duration ms"),
        box("duration", "flonum", [430., 479., 90., 22.], minimum=10., maximum=600000., numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("duration_pre", "newobj", [530., 479., 110., 22.], text="prepend duration", numinlets=1, numoutlets=1, outlettype=[""]),
        box("test", "message", [665., 479., 42., 22.], text="test", numinlets=2, numoutlets=1, outlettype=[""]),
        box("writer", "newobj", [730., 479., 270., 22.], text="js qmw_fdg_parameter_field_v1.js", numinlets=1, numoutlets=7, outlettype=[""] * 7),
        box("status", "message", [20., 520., 1020., 42.], text="waiting for parameter field...", numinlets=2, numoutlets=1, outlettype=[""]),

        box("rate_label", "comment", [20., 580., 250., 20.], text="RATE FIELD — signed gap → playback ratio"),
        box("rate_view", "multislider", [20., 603., 500., 48.], size=8, setminmax=[-4., 4.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("delay_label", "comment", [550., 580., 350., 20.], text="DELAY FIELD — phase → temporal offset (ms)"),
        box("delay_view", "multislider", [550., 603., 500., 48.], size=8, setminmax=[-60000., 0.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("window_label", "comment", [20., 670., 360., 20.], text="WINDOW-OFFSET FIELD — relational voice position"),
        box("window_view", "multislider", [20., 693., 500., 48.], size=8, setminmax=[0., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("amp_label", "comment", [550., 670., 300., 20.], text="AMPLITUDE FIELD — normalized quantum weight"),
        box("amp_view", "multislider", [550., 693., 500., 48.], size=8, setminmax=[0., 1.], numinlets=1, numoutlets=2, outlettype=["", ""]),

        box("osc", "newobj", [20., 775., 126., 22.], text="udpreceive 7400", numinlets=1, numoutlets=1, outlettype=[""]),
        box("route_qmw", "newobj", [160., 775., 104., 22.], text="OSC-route /qmw", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_density", "newobj", [280., 775., 145., 22.], text="OSC-route /density_field", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_fields", "newobj", [440., 775., 510., 22.], text="OSC-route /magnitude /phase /purity /entropy /coherence", numinlets=1, numoutlets=6, outlettype=[""] * 6),
        box("osc_note", "comment", [20., 810., 1030., 36.], text="Mode 1 reads table slot i for grain voice i. Mode 2 randomly samples the table while entropy sets rate, delay, and offset random depth. Observable envelope families belong in a later env2D atlas; Grainflow's windowBuffer is specifically the window-offset table."),

        box("init_clock", "newobj", [20., 865., 85., 22.], text="loadmess 8.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_scan", "newobj", [115., 865., 95., 22.], text="loadmess 0.12", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_enable", "newobj", [220., 865., 85., 22.], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_mode", "newobj", [315., 865., 85., 22.], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_mag", "newobj", [410., 865., 95., 22.], text="loadmess 0.55", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_phase", "newobj", [515., 865., 85., 22.], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_purity", "newobj", [610., 865., 95., 22.], text="loadmess 0.8", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_entropy", "newobj", [715., 865., 95., 22.], text="loadmess 0.2", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_coherence", "newobj", [820., 865., 95., 22.], text="loadmess 0.8", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_duration", "newobj", [925., 865., 115., 22.], text="loadmess 5587.528", numinlets=1, numoutlets=1, outlettype=[""]),
    ]

    lines = [
        line("clock", 0, "clock_sig"), line("scan", 0, "scan_sig"), line("clock_sig", 0, "grain", 0), line("scan_sig", 0, "grain", 1),
        line("scalar_rate", 0, "grain", 2), line("amp_mc", 0, "amp_smooth"), line("amp_smooth", 0, "grain", 3), line("enable", 0, "grain"), line("grain", 0, "pan", 0), line("grain", 2, "pan", 1), line("grain", 1, "metadata", 1),
        line("pan", 0, "unpack"), line("unpack", 0, "gain_l"), line("unpack", 1, "gain_r"), line("gain_l", 0, "meter_l"), line("gain_r", 0, "meter_r"), line("gain_l", 0, "dac"), line("gain_r", 0, "dac", 1),
        line("mode", 0, "mode_pre"), line("mode_pre", 0, "writer"),
        line("mag", 0, "mag_pre"), line("mag_pre", 0, "writer"), line("phase", 0, "phase_pre"), line("phase_pre", 0, "writer"), line("purity", 0, "purity_pre"), line("purity_pre", 0, "writer"), line("entropy", 0, "entropy_pre"), line("entropy_pre", 0, "writer"), line("coherence", 0, "coherence_pre"), line("coherence_pre", 0, "writer"), line("duration", 0, "duration_pre"), line("duration_pre", 0, "writer"), line("test", 0, "writer"),
        line("writer", 0, "rate_view"), line("writer", 1, "delay_view"), line("writer", 2, "window_view"), line("writer", 3, "amp_view"), line("writer", 4, "amp_mc"), line("writer", 5, "grain"), line("writer", 6, "status", 1),
        line("osc", 0, "route_qmw"), line("route_qmw", 0, "route_density"), line("route_density", 0, "route_fields"), line("route_fields", 0, "mag_pre"), line("route_fields", 1, "phase_pre"), line("route_fields", 2, "purity_pre"), line("route_fields", 3, "entropy_pre"), line("route_fields", 4, "coherence_pre"),
        line("init_clock", 0, "clock"), line("init_scan", 0, "scan"), line("init_enable", 0, "enable"), line("init_mode", 0, "mode"), line("init_mag", 0, "mag"), line("init_phase", 0, "phase"), line("init_purity", 0, "purity"), line("init_entropy", 0, "entropy"), line("init_coherence", 0, "coherence"), line("init_duration", 0, "duration"),
    ]

    return {"patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box", "rect": [65., 35., 1100., 930.], "gridsize": [15., 15.],
        "boxes": boxes, "lines": lines,
        "dependency_cache": [
            {"name": "CP_Bubbling_Pasta_Sauce.wav", "type": "WAVE"},
            {"name": "grainflow~.mxo", "type": "iLaX"},
            {"name": "grainflow.util.stereoPan~.maxpat", "type": "JSON"},
            {"name": "grainflow.Hanning.aif", "type": "AIFF"},
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_fdg_parameter_field_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }}


def validate(document: dict[str, Any]) -> None:
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    if len(boxes) != len(patcher["boxes"]):
        raise RuntimeError("duplicate box identifiers")
    for entry in patcher["lines"]:
        source, source_outlet = entry["patchline"]["source"]
        destination, destination_inlet = entry["patchline"]["destination"]
        if source not in boxes or destination not in boxes:
            raise RuntimeError(f"dangling connection {source} -> {destination}")
        if source_outlet >= boxes[source].get("numoutlets", 0):
            raise RuntimeError(f"invalid outlet {source}[{source_outlet}]")
        if destination_inlet >= boxes[destination].get("numinlets", 0):
            raise RuntimeError(f"invalid inlet {destination}[{destination_inlet}]")
    texts = {entry["box"].get("text", "") for entry in patcher["boxes"]}
    required = {
        "buffer~ qmw_fdg_rates @samps 9",
        "buffer~ qmw_fdg_delays @samps 9",
        "buffer~ qmw_fdg_windows @samps 9",
        "grainflow~ qmw_fdg_source 8 grainflow.Hanning.aif",
        "mc.sig~ 0. @chans 8",
        "js qmw_fdg_parameter_field_v1.js",
    }
    if not required.issubset(texts):
        raise RuntimeError(f"missing field objects: {sorted(required - texts)}")


def main() -> int:
    document = build()
    validate(document)
    output = ROOT / "QMW_Field_Directed_Parameter_Buffers_v1.maxpat"
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
