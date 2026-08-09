#!/usr/bin/env python3
"""Build the sounding six-voice Wilson Hexany Phase 3 Max instrument."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VOICE = ROOT / "qmw_wilson_hexany_voice_phase3.maxpat"
INSTRUMENT = ROOT / "QMW_Wilson_Hexany_Instrument_Phase3.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0, order=None):
    value = {"source": [source, outlet], "destination": [destination, inlet]}
    if order is not None:
        value["order"] = order
    return {"patchline": value}


def document(boxes, lines, rect, dependencies=None, presentation=False):
    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": rect,
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": dependencies or [],
        "autosave": 0,
    }
    if presentation:
        patcher["openinpresentation"] = 1
        for entry in boxes:
            item = entry["box"]
            item["presentation"] = 1
            item["presentation_rect"] = copy.deepcopy(item["patching_rect"])
    return {"patcher": patcher}


def build_voice():
    b = [
        box("in", "newobj", [25, 20, 40, 22], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route", "newobj", [75, 20, 112, 22], text="route accent mute", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("unpack", "newobj", [210, 20, 205, 22], text="unpack f f f f f", numinlets=1, numoutlets=5, outlettype=["float"] * 5),
        box("freq_msg", "message", [25, 75, 62, 22], text="$1 35"),
        box("freq_line", "newobj", [95, 75, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("fund", "newobj", [150, 75, 50, 22], text="cycle~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("double", "newobj", [25, 110, 42, 22], text="* 2."),
        box("double_msg", "message", [75, 110, 62, 22], text="$1 35"),
        box("double_line", "newobj", [145, 110, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("partial", "newobj", [200, 110, 50, 22], text="cycle~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("phase_norm", "newobj", [270, 110, 210, 22], text="expr (($f1 / 6.2831853) + 1.) % 1."),
        box("phase_msg", "message", [490, 110, 62, 22], text="$1 60"),
        box("phase_line", "newobj", [560, 110, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("coh_amp", "newobj", [270, 145, 150, 22], text="expr 0.06 + 0.24*$f1"),
        box("coh_msg", "message", [430, 145, 70, 22], text="$1 100"),
        box("coh_line", "newobj", [510, 145, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("partial_amp", "newobj", [200, 180, 36, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mix", "newobj", [150, 215, 36, 22], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("activation_clip", "newobj", [270, 215, 72, 22], text="clip 0. 1."),
        box("activation_sqrt", "newobj", [350, 215, 78, 22], text="expr sqrt($f1)"),
        box("activation_msg", "message", [438, 215, 70, 22], text="$1 80"),
        box("activation_line", "newobj", [518, 215, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("accent_msg", "message", [25, 250, 105, 22], text="$1 3, 0 450 3"),
        box("accent_line", "newobj", [140, 250, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("env_add", "newobj", [200, 250, 36, 22], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("env_clip", "newobj", [245, 250, 72, 22], text="clip~ 0. 1."),
        box("voiced", "newobj", [150, 285, 36, 22], text="*~ 0.12", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("pan_msg", "message", [340, 285, 72, 22], text="$1 120"),
        box("pan_line", "newobj", [422, 285, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("left_gain", "newobj", [340, 320, 190, 22], text="expr~ sqrt((1.-$v1)*0.5)"),
        box("right_gain", "newobj", [540, 320, 190, 22], text="expr~ sqrt((1.+$v1)*0.5)"),
        box("left", "newobj", [150, 355, 36, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("right", "newobj", [210, 355, 36, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("out_l", "newobj", [150, 400, 52, 22], text="out~ 1", numinlets=1, numoutlets=0),
        box("out_r", "newobj", [210, 400, 52, 22], text="out~ 2", numinlets=1, numoutlets=0),
        box("thispoly", "newobj", [25, 400, 62, 22], text="thispoly~", numinlets=2, numoutlets=3, outlettype=["int", "int", "int"]),
    ]
    l = [
        line("in", 0, "route"), line("route", 2, "unpack"), line("route", 0, "accent_msg"), line("route", 1, "thispoly"),
        line("unpack", 0, "freq_msg"), line("freq_msg", 0, "freq_line"), line("freq_line", 0, "fund"),
        line("unpack", 0, "double"), line("double", 0, "double_msg"), line("double_msg", 0, "double_line"), line("double_line", 0, "partial"),
        line("unpack", 2, "phase_norm"), line("phase_norm", 0, "phase_msg"), line("phase_msg", 0, "phase_line"), line("phase_line", 0, "partial", 1),
        line("unpack", 3, "coh_amp"), line("coh_amp", 0, "coh_msg"), line("coh_msg", 0, "coh_line"), line("partial", 0, "partial_amp"), line("coh_line", 0, "partial_amp", 1),
        line("fund", 0, "mix"), line("partial_amp", 0, "mix", 1),
        line("unpack", 1, "activation_clip"), line("activation_clip", 0, "activation_sqrt"), line("activation_sqrt", 0, "activation_msg"), line("activation_msg", 0, "activation_line"),
        line("accent_msg", 0, "accent_line"), line("activation_line", 0, "env_add"), line("accent_line", 0, "env_add", 1), line("env_add", 0, "env_clip"),
        line("mix", 0, "voiced"), line("env_clip", 0, "voiced", 1),
        line("unpack", 4, "pan_msg"), line("pan_msg", 0, "pan_line"), line("pan_line", 0, "left_gain"), line("pan_line", 0, "right_gain"),
        line("voiced", 0, "left"), line("left_gain", 0, "left", 1), line("voiced", 0, "right"), line("right_gain", 0, "right", 1),
        line("left", 0, "out_l"), line("right", 0, "out_r"),
    ]
    VOICE.write_text(json.dumps(document(b, l, [80, 80, 780, 470]), indent=2) + "\n", encoding="utf-8")


def build_instrument():
    b = [
        box("title", "comment", [25, 18, 1130, 30], text="QMW · WILSON HEXANY INSTRUMENT · PHASE 3", fontsize=21),
        box("subtitle", "comment", [25, 50, 1150, 38], text="Six exact 2)4 · 1–3–5–7 voices. Probability drives energy, relative phase drives spectral color and space, Johnson-flow creates accents; complement exchanges particle and hole."),
        box("rx_label", "comment", [25, 105, 360, 20], text="AUTHORITATIVE CPS STATE · UDP 7420", fontsize=14),
        box("udp", "newobj", [25, 135, 110, 22], text="udpreceive 7420", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route_qmw", "newobj", [145, 135, 110, 22], text="OSC-route /qmw"),
        box("route_wilson", "newobj", [265, 135, 125, 22], text="OSC-route /wilson"),
        box("route_cps", "newobj", [400, 135, 105, 22], text="OSC-route /cps"),
        box("route_messages", "newobj", [515, 135, 630, 22], text="OSC-route /definition /edge /frame /vertex /end /measurement /flow /status"),
        box("pre_definition", "newobj", [25, 180, 120, 22], text="prepend definition"),
        box("pre_edge", "newobj", [155, 180, 90, 22], text="prepend edge"),
        box("pre_frame", "newobj", [255, 180, 95, 22], text="prepend frame"),
        box("pre_vertex", "newobj", [360, 180, 100, 22], text="prepend vertex"),
        box("pre_end", "newobj", [470, 180, 85, 22], text="prepend end"),
        box("pre_measurement", "newobj", [565, 180, 135, 22], text="prepend measurement"),
        box("pre_flow", "newobj", [710, 180, 85, 22], text="prepend flow"),
        box("pre_status", "newobj", [805, 180, 95, 22], text="prepend status"),
        box("dispatch", "newobj", [25, 225, 250, 22], text="js qmw_wilson_hexany_phase3.js", numinlets=1, numoutlets=3, outlettype=["", "list", ""]),
        box("poly", "newobj", [25, 270, 390, 22], text="poly~ qmw_wilson_hexany_voice_phase3.maxpat 6 @steal 0", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("activation_label", "comment", [445, 224, 450, 20], text="AUDITORY ACTIVATION · attack + post-release persistence"),
        box("activation", "multislider", [445, 252, 450, 85], size=6, setminmax=[0.0, 1.0], orientation=0, slidercolor=[0.32, 0.75, 1.0, 1.0]),
        box("status", "message", [445, 350, 700, 22], text="waiting for CPS frame …", numinlets=2, numoutlets=1, outlettype=[""]),
        box("gain", "live.gain~", [25, 320, 105, 150], numinlets=2, numoutlets=5, outlettype=["signal", "signal", "", "float", "list"], parameter_enable=1,
            saved_attribute_attributes={"valueof": {"parameter_initial": [-12.0], "parameter_initial_enable": 1, "parameter_longname": "Wilson Hexany output", "parameter_mmax": 6.0, "parameter_mmin": -70.0, "parameter_shortname": "Hexany output", "parameter_type": 0, "parameter_unitstyle": 4}}),
        box("clip_l", "newobj", [155, 350, 85, 22], text="clip~ -0.95 0.95"),
        box("clip_r", "newobj", [155, 390, 85, 22], text="clip~ -0.95 0.95"),
        box("meter_l", "newobj", [255, 350, 65, 22], text="meter~"),
        box("meter_r", "newobj", [255, 390, 65, 22], text="meter~"),
        box("dac", "newobj", [335, 370, 65, 22], text="ezdac~"),
        box("dsp_on", "newobj", [335, 410, 72, 22], text="loadmess 1", hidden=1),
        box("controls_label", "comment", [445, 405, 540, 22], text="COMPOSITIONAL NAVIGATION", fontsize=14),
        box("start", "message", [445, 440, 55, 22], text="start"),
        box("start_pack", "newobj", [445, 470, 175, 22], text="o.pack /qmw/recursive/start"),
        box("stop", "message", [510, 440, 50, 22], text="stop"),
        box("stop_pack", "newobj", [630, 470, 170, 22], text="o.pack /qmw/recursive/stop"),
        box("next", "message", [570, 440, 50, 22], text="next"),
        box("next_pack", "newobj", [810, 470, 170, 22], text="o.pack /qmw/recursive/next"),
        box("reset", "message", [630, 440, 50, 22], text="reset"),
        box("reset_pack", "newobj", [990, 470, 175, 22], text="o.pack /qmw/recursive/reset"),
        box("complement", "message", [690, 440, 95, 22], text="complement"),
        box("probe", "message", [795, 440, 105, 22], text="seed Hexany"),
        box("complement_pack", "newobj", [445, 510, 230, 22], text="o.pack /qmw/wilson/cps/complement"),
        box("probe_pack", "newobj", [685, 510, 200, 22], text="o.pack /qmw/wilson/cps/probe"),
        box("control_udp", "newobj", [995, 550, 165, 22], text="udpsend 127.0.0.1 7433"),
        box("temp_label", "comment", [445, 555, 82, 20], text="temperature"),
        box("temperature", "flonum", [535, 553, 65, 22], minimum=0.0, maximum=2.0),
        box("temp_pack", "newobj", [610, 553, 205, 22], text="o.pack /qmw/recursive/temperature"),
        box("interval_label", "comment", [445, 590, 75, 20], text="interval ms"),
        box("interval", "number", [535, 588, 65, 22], minimum=30, maximum=5000),
        box("interval_pack", "newobj", [610, 588, 205, 22], text="o.pack /qmw/recursive/interval_ms"),
        box("transpose_label", "comment", [445, 625, 125, 20], text="temporary anchor ±48 st"),
        box("transpose", "flonum", [575, 623, 65, 22], minimum=-48.0, maximum=48.0),
        box("pre_transpose", "newobj", [650, 623, 120, 22], text="prepend transpose"),
        box("test", "message", [800, 623, 80, 22], text="local test"),
        box("test_msg", "message", [890, 623, 45, 22], text="test"),
        box("load_temp", "newobj", [25, 650, 90, 22], text="loadmess 0.65", hidden=1),
        box("load_interval", "newobj", [125, 650, 95, 22], text="loadmess 240", hidden=1),
        box("load_transpose", "newobj", [230, 650, 80, 22], text="loadmess 0", hidden=1),
        box("note", "comment", [25, 690, 1130, 48], text="Start examples/qmw_wilson_hexany_phase3.py. The same revisioned CPS packets drive this sound field and the Processing Hexany geometry on UDP 7411. The temporary anchor transposes without changing Wilson interval identity."),
    ]
    l = [
        line("udp", 0, "route_qmw"), line("route_qmw", 0, "route_wilson"), line("route_wilson", 0, "route_cps"), line("route_cps", 0, "route_messages"),
    ]
    prefixes = ["definition", "edge", "frame", "vertex", "end", "measurement", "flow", "status"]
    for outlet, name in enumerate(prefixes):
        l.extend([line("route_messages", outlet, "pre_" + name), line("pre_" + name, 0, "dispatch")])
    l.extend([
        line("dispatch", 0, "poly"), line("dispatch", 1, "activation"), line("dispatch", 2, "status", 1),
        line("poly", 0, "gain"), line("poly", 1, "gain", 1), line("gain", 0, "clip_l"), line("gain", 1, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"), line("clip_l", 0, "dac"), line("clip_r", 0, "dac", 1), line("dsp_on", 0, "dac"),
        line("start", 0, "start_pack"), line("stop", 0, "stop_pack"), line("next", 0, "next_pack"), line("reset", 0, "reset_pack"), line("complement", 0, "complement_pack"), line("probe", 0, "probe_pack"),
        line("temperature", 0, "temp_pack"), line("interval", 0, "interval_pack"),
        line("start_pack", 0, "control_udp"), line("stop_pack", 0, "control_udp"), line("next_pack", 0, "control_udp"), line("reset_pack", 0, "control_udp"), line("complement_pack", 0, "control_udp"), line("probe_pack", 0, "control_udp"), line("temp_pack", 0, "control_udp"), line("interval_pack", 0, "control_udp"),
        line("transpose", 0, "pre_transpose"), line("pre_transpose", 0, "dispatch"), line("test", 0, "test_msg"), line("test_msg", 0, "dispatch"),
        line("load_temp", 0, "temperature"), line("load_interval", 0, "interval"), line("load_transpose", 0, "transpose"),
    ])
    deps = [
        {"name": "qmw_wilson_hexany_phase3.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1},
        {"name": VOICE.name, "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "JSON", "implicit": 1},
        {"name": "OSC-route.mxo", "type": "iLaX"}, {"name": "o.pack.mxo", "type": "iLaX"},
    ]
    INSTRUMENT.write_text(json.dumps(document(b, l, [70, 70, 1200, 780], deps, True), indent=2) + "\n", encoding="utf-8")


def main():
    build_voice()
    build_instrument()
    print(f"Built {VOICE.name} and {INSTRUMENT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
