#!/usr/bin/env python3
"""Build the 16-body Heisenberg/QMB/wavetable/Rings instrument."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def new(identifier: str, text: str, rect: list[float], ins: int, outs: int, types: list[str] | None = None) -> dict[str, Any]:
    return box(identifier, "newobj", rect, text=text, numinlets=ins, numoutlets=outs, outlettype=types or [""] * outs)


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def voice_patch() -> dict[str, Any]:
    boxes = [
        new("in", "in 1", [30., 30., 35., 22.], 1, 1),
        new("route", "route params", [30., 65., 85., 22.], 1, 2),
        new("unpack", "unpack f f f f f f i", [95., 100., 145., 22.], 1, 7),
        new("mtof", "mtof", [95., 140., 38., 22.], 1, 1),
        new("rate", "* 0.5", [95., 175., 45., 22.], 2, 1),
        new("phasor", "phasor~ 55", [95., 210., 72., 22.], 2, 1, ["signal"]),
        new("wave_recv", "r qmb.heisenberg.rings.wave", [190., 175., 185., 22.], 0, 1),
        new("peek", "jit.peek~ qmb_heisenberg_rings_wave_a 1 0 @interp 1 @normalize 1", [190., 210., 390., 22.], 1, 2, ["signal", ""]),
        new("amp_target", "pack f 180.", [330., 65., 78., 22.], 2, 1),
        new("amp_sig", "line~ 0.1", [330., 100., 62., 22.], 2, 1, ["signal"]),
        new("exc_amp", "*~", [190., 250., 35., 22.], 2, 1, ["signal"]),
        new("note_msg", "prepend note", [95., 320., 82., 22.], 1, 1),
        new("model_msg", "prepend model", [400., 100., 90., 22.], 1, 1),
        box("polyphony", "message", [500., 100., 78., 22.], text="polyphony 1", numinlets=2, numoutlets=1, outlettype=[""]),
        new("load", "loadbang", [500., 65., 60., 22.], 1, 1),
        new("struct_target", "pack f 180.", [190., 285., 78., 22.], 2, 1),
        new("bright_target", "pack f 180.", [275., 285., 78., 22.], 2, 1),
        new("damp_target", "pack f 180.", [360., 285., 78., 22.], 2, 1),
        new("pos_target", "pack f 180.", [445., 285., 78., 22.], 2, 1),
        new("struct", "line~ 0.4", [190., 320., 62., 22.], 2, 1, ["signal"]),
        new("bright", "line~ 0.5", [255., 320., 62., 22.], 2, 1, ["signal"]),
        new("damp", "line~ 0.7", [320., 320., 62., 22.], 2, 1, ["signal"]),
        new("pos", "line~ 0.5", [385., 320., 62., 22.], 2, 1, ["signal"]),
        new("rings", "vb.mi.rngs~", [190., 370., 360., 24.], 8, 2, ["signal", "signal"]),
        new("gain_l", "*~ 0.32", [190., 420., 58., 22.], 2, 1, ["signal"]),
        new("gain_r", "*~ 0.32", [320., 420., 58., 22.], 2, 1, ["signal"]),
        new("out_l", "out~ 1", [190., 460., 48., 22.], 1, 0),
        new("out_r", "out~ 2", [320., 460., 48., 22.], 1, 0),
    ]
    lines = [
        line("in", 0, "route"), line("route", 0, "unpack"),
        line("unpack", 0, "mtof"), line("unpack", 0, "note_msg"), line("mtof", 0, "rate"), line("rate", 0, "phasor"),
        line("wave_recv", 0, "peek"), line("phasor", 0, "peek"),
        line("peek", 0, "exc_amp"), line("unpack", 5, "amp_target"), line("amp_target", 0, "amp_sig"), line("amp_sig", 0, "exc_amp", 1),
        line("unpack", 1, "struct_target"), line("struct_target", 0, "struct"),
        line("unpack", 2, "bright_target"), line("bright_target", 0, "bright"),
        line("unpack", 3, "damp_target"), line("damp_target", 0, "damp"),
        line("unpack", 4, "pos_target"), line("pos_target", 0, "pos"),
        line("unpack", 6, "model_msg"), line("load", 0, "polyphony"),
        line("exc_amp", 0, "rings"), line("note_msg", 0, "rings"), line("model_msg", 0, "rings"), line("polyphony", 0, "rings"),
        line("struct", 0, "rings", 2), line("bright", 0, "rings", 3), line("damp", 0, "rings", 4), line("pos", 0, "rings", 5),
        line("rings", 0, "gain_l"), line("rings", 1, "gain_r"), line("gain_l", 0, "out_l"), line("gain_r", 0, "out_r"),
    ]
    return patcher([25., 25., 620., 520.], boxes, lines, [
        {"name": "vb.mi.rngs~.mxo", "type": "iLaX"}
    ])


def main_patch() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [30., 20., 1100., 32.], text="QMW HEISENBERG — 16-BODY COMPLEX MATRIX RINGS INSTRUMENT v1", fontsize=20., fontface=1),
        box("concept", "comment", [30., 58., 1130., 42.], text="Each matrix row is one vb.mi.rngs~ body. Its sixteen complex relationships determine pitch, structure, brightness, damping, position, excitation, and wavetable phase."),
        new("udp", "udpreceive 7400", [30., 120., 120., 22.], 1, 1),
        box("retry_udp", "message", [930., 120., 78., 22.], text="port 7400", numinlets=2, numoutlets=1, outlettype=[""]),
        box("retry_udp_label", "comment", [1015., 121., 145., 34.], text="RETRY UDP 7400 after conflict"),
        new("route_qmw", "OSC-route /qmw", [165., 120., 105., 22.], 1, 2),
        new("route_h", "OSC-route /heisenberg", [285., 120., 145., 22.], 1, 2),
        new("route_active", "OSC-route /active", [445., 120., 125., 22.], 1, 2),
        new("route_meta", "OSC-route /matrix /mode /outcome /disturbance", [585., 120., 330., 22.], 1, 5),
        new("route_matrix", "OSC-route /begin /end /real /imag /magnitude /phase /frequency_hz /pan", [30., 165., 650., 22.], 1, 9),
        new("pre_begin", "prepend begin", [30., 205., 95., 22.], 1, 1),
        new("pre_end", "prepend end", [130., 205., 85., 22.], 1, 1),
        new("pre_real", "prepend real", [220., 205., 90., 22.], 1, 1),
        new("pre_imag", "prepend imag", [315., 205., 90., 22.], 1, 1),
        new("pre_mag", "prepend magnitude", [410., 205., 125., 22.], 1, 1),
        new("pre_phase", "prepend phase", [540., 205., 100., 22.], 1, 1),
        new("pre_freq", "prepend frequency_hz", [645., 205., 145., 22.], 1, 1),
        new("pre_pan", "prepend pan", [795., 205., 90., 22.], 1, 1),
        new("adapter", "js qmb_heisenberg_adapter_v1.js", [30., 255., 245., 22.], 1, 7),
        new("tag_c", "prepend contributions", [300., 250., 135., 22.], 1, 1),
        new("tag_m", "prepend magnitude", [445., 250., 125., 22.], 1, 1),
        new("tag_p", "prepend phase", [580., 250., 100., 22.], 1, 1),
        new("tag_f", "prepend frequency_hz", [690., 250., 145., 22.], 1, 1),
        new("tag_pan", "prepend pan", [845., 250., 90., 22.], 1, 1),
        new("controller", "js qmb_heisenberg_rings_controller_v1.js", [300., 300., 285., 22.], 1, 3),
        new("wave_route", "route jit_matrix", [300., 345., 100., 22.], 1, 2),
        new("wave_name", "prepend matrix_name", [300., 380., 130., 22.], 1, 1),
        new("wave_send", "s qmb.heisenberg.rings.wave", [300., 415., 185., 22.], 1, 0),
        new("poly_router", "js qmb_heisenberg_rings_poly_router_v1.js", [610., 345., 270., 22.], 1, 1),
        new("poly", "poly~ qmb_heisenberg_rings_voice_v1 16", [610., 390., 260., 22.], 1, 2, ["signal", "signal"]),
        new("master_l", "*~ 0.85", [610., 445., 58., 22.], 2, 1, ["signal"]),
        new("master_r", "*~ 0.85", [745., 445., 58., 22.], 2, 1, ["signal"]),
        new("lim_l", "clip~ -0.95 0.95", [610., 480., 105., 22.], 1, 1, ["signal"]),
        new("lim_r", "clip~ -0.95 0.95", [745., 480., 105., 22.], 1, 1, ["signal"]),
        box("meter_l", "meter~", [825., 435., 18., 65.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [850., 435., 18., 65.], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [900., 440., 50., 50.], numinlets=2, numoutlets=0),
        new("sum", "+~", [610., 530., 35., 22.], 2, 1, ["signal"]),
        new("memory_gain", "*~ 0.5", [610., 565., 55., 22.], 2, 1, ["signal"]),
        new("mem_matrix", "jit.matrix qmb_heisenberg_rings_memory 1 float32 256 64", [700., 565., 330., 22.], 1, 2),
        new("x_phase", "phasor~ 172.265625", [610., 610., 112., 22.], 2, 1, ["signal"]),
        new("x_scale", "*~ 255.", [610., 645., 58., 22.], 2, 1, ["signal"]),
        new("y_phase", "phasor~ 0.05", [750., 610., 85., 22.], 2, 1, ["signal"]),
        new("y_scale", "*~ 63.", [750., 645., 52., 22.], 2, 1, ["signal"]),
        new("poke", "jit.poke~ qmb_heisenberg_rings_memory 2 0", [610., 690., 280., 22.], 3, 1),
        box("memory_note", "comment", [610., 725., 420., 42.], text="jit.poke~ writes the resulting acoustic output into a separate 256×64 performance memory. The canonical quantum matrices are never overwritten."),
        new("diag_adapter", "print QMB_RINGS_ADAPTER", [30., 305., 175., 22.], 1, 0),
        box("adapter_status", "message", [30., 340., 245., 48.], text="adapter: waiting for /matrix/begin...", numinlets=2, numoutlets=1, outlettype=[""]),
        new("diag_music", "print QMB_RINGS_MUSIC", [300., 455., 165., 22.], 1, 0),
        box("status", "message", [300., 490., 280., 48.], text="waiting for musical matrix commit...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("controls_label", "comment", [30., 585., 430., 22.], text="HEISENBERG CONTROLS — publisher listens on UDP 7412", fontface=1),
        box("coherent", "message", [30., 620., 250., 22.], text="/qmw/heisenberg/mode coherent", numinlets=2, numoutlets=1, outlettype=[""]),
        box("unread", "message", [30., 655., 240., 22.], text="/qmw/heisenberg/mode unread", numinlets=2, numoutlets=1, outlettype=[""]),
        box("recorded", "message", [30., 690., 255., 22.], text="/qmw/heisenberg/mode recorded", numinlets=2, numoutlets=1, outlettype=[""]),
        box("record", "message", [300., 690., 215., 22.], text="/qmw/heisenberg/record 1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xz", "message", [300., 620., 250., 22.], text="/qmw/heisenberg/observable XZ0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("y0", "message", [300., 655., 245., 22.], text="/qmw/heisenberg/observable Y0", numinlets=2, numoutlets=1, outlettype=[""]),
        new("send", "udpsend 127.0.0.1 7412", [30., 740., 165., 22.], 1, 0),
        box("phase_label", "comment", [610., 790., 500., 22.], text="LIVE PHASE OBSERVABLE — normalized 0…1 maps to 0…2π radians", fontface=1),
        box("phase_norm", "flonum", [610., 825., 90., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        new("phase_clip", "clip 0. 1.", [710., 825., 70., 22.], 3, 1),
        new("phase_prepend", "prepend /qmw/bridge/observable/phase", [790., 825., 255., 22.], 1, 1),
        new("phase_send", "udpsend 127.0.0.1 7421", [610., 860., 165., 22.], 1, 0),
        box("phase_0", "message", [790., 860., 38., 22.], text="0.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("phase_y", "message", [835., 860., 42., 22.], text="0.25", numinlets=2, numoutlets=1, outlettype=[""]),
        box("phase_pi", "message", [884., 860., 38., 22.], text="0.5", numinlets=2, numoutlets=1, outlettype=[""]),
        box("phase_minus_y", "message", [929., 860., 42., 22.], text="0.75", numinlets=2, numoutlets=1, outlettype=[""]),
        box("phase_tau", "message", [978., 860., 32., 22.], text="1.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("four_observable", "message", [1020., 860., 180., 22.], text="/qmw/bridge/observable FOUR", numinlets=2, numoutlets=1, outlettype=[""]),
        box("rate_label", "comment", [610., 895., 175., 22.], text="MUSICAL COMMIT RATE (Hz)"),
        box("rate_hz", "flonum", [790., 895., 70., 22.], minimum=0.25, maximum=30.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        new("rate_prepend", "prepend /qmw/bridge/output_hz", [870., 895., 220., 22.], 1, 1),
        box("smooth_label", "comment", [610., 930., 175., 22.], text="COMPLEX SMOOTHING (ms)"),
        box("smooth_ms", "flonum", [790., 930., 70., 22.], minimum=0.0, maximum=5000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        new("smooth_prepend", "prepend /qmw/bridge/smoothing_ms", [870., 930., 235., 22.], 1, 1),
        box("qubit_phase_label", "comment", [610., 965., 500., 22.], text="QUBIT PHASE OFFSETS — normalized turns (defaults: 0, .25, .5, .75)"),
        box("q0_phase", "flonum", [610., 1000., 58., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("q1_phase", "flonum", [735., 1000., 58., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("q2_phase", "flonum", [860., 1000., 58., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("q3_phase", "flonum", [985., 1000., 58., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("q0_label", "comment", [675., 1001., 24., 22.], text="q0"),
        box("q1_label", "comment", [800., 1001., 24., 22.], text="q1"),
        box("q2_label", "comment", [925., 1001., 24., 22.], text="q2"),
        box("q3_label", "comment", [1050., 1001., 24., 22.], text="q3"),
        new("q0_prepend", "prepend /qmw/bridge/observable/phase/q0", [610., 1035., 280., 22.], 1, 1),
        new("q1_prepend", "prepend /qmw/bridge/observable/phase/q1", [610., 1065., 280., 22.], 1, 1),
        new("q2_prepend", "prepend /qmw/bridge/observable/phase/q2", [900., 1035., 280., 22.], 1, 1),
        new("q3_prepend", "prepend /qmw/bridge/observable/phase/q3", [900., 1065., 280., 22.], 1, 1),
        box("morph_label", "comment", [30., 1100., 360., 22.], text="VOICE MAPPING CROSSFADE — relational 0 ←→ component 1", fontface=1),
        box("mapping_morph", "flonum", [400., 1100., 70., 22.], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        new("morph_prepend", "prepend mapping_morph", [480., 1100., 155., 22.], 1, 1),
        box("morph_rel", "message", [650., 1100., 32., 22.], text="0.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("morph_mid", "message", [690., 1100., 38., 22.], text="0.5", numinlets=2, numoutlets=1, outlettype=[""]),
        box("morph_comp", "message", [736., 1100., 32., 22.], text="1.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("voice_map_label", "comment", [30., 1140., 760., 22.], text="PER-VOICE MAP — voice_map <1…16 | 0=all> <destination> <source> <amount -1…1>", fontface=1),
        box("map_example_1", "message", [30., 1175., 235., 22.], text="voice_map 1 brightness real 1.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("map_example_2", "message", [275., 1175., 275., 22.], text="voice_map 1 damping magnitude -0.5", numinlets=2, numoutlets=1, outlettype=[""]),
        box("map_example_3", "message", [560., 1175., 255., 22.], text="voice_map 7 structure phase 0.4", numinlets=2, numoutlets=1, outlettype=[""]),
        box("map_example_all", "message", [825., 1175., 260., 22.], text="voice_map 0 position imag 0.6", numinlets=2, numoutlets=1, outlettype=[""]),
        box("map_clear", "message", [30., 1210., 135., 22.], text="voice_map_clear 0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("map_sources", "comment", [180., 1210., 900., 22.], text="sources: magnitude real imag phase frequency pan     destinations: structure brightness damping position"),
        box("cell_map_label", "comment", [30., 1250., 850., 22.], text="RAW REALTIME CELL MAP — cell_map <voice> <destination> <list> <column 1…16> <amount>", fontface=1),
        box("cell_example_1", "message", [30., 1285., 270., 22.], text="cell_map 1 brightness real 4 1.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("cell_example_2", "message", [310., 1285., 300., 22.], text="cell_map 2 damping magnitude 9 0.7", numinlets=2, numoutlets=1, outlettype=[""]),
        box("cell_example_3", "message", [620., 1285., 280., 22.], text="cell_map 7 structure imag 12 -0.5", numinlets=2, numoutlets=1, outlettype=[""]),
        box("cell_example_all", "message", [910., 1285., 270., 22.], text="cell_map 0 position phase 8 0.4", numinlets=2, numoutlets=1, outlettype=[""]),
        box("cell_clear", "message", [30., 1320., 130., 22.], text="cell_map_clear 0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("run_note", "comment", [30., 790., 540., 70.], text="Static proof: run heisenberg_lab_v1. Live motion: run quantumsonification_conductor.py on 7421 plus qmb_conductor_density_bridge_v1. Max continues to receive committed matrices on 7400."),
    ]
    lines = [
        line("retry_udp", 0, "udp"), line("udp", 0, "route_qmw"), line("route_qmw", 0, "route_h"), line("route_h", 0, "route_active"), line("route_active", 0, "route_meta"), line("route_meta", 0, "route_matrix"),
        line("route_matrix", 0, "pre_begin"), line("route_matrix", 1, "pre_end"), line("route_matrix", 2, "pre_real"), line("route_matrix", 3, "pre_imag"), line("route_matrix", 4, "pre_mag"), line("route_matrix", 5, "pre_phase"), line("route_matrix", 6, "pre_freq"), line("route_matrix", 7, "pre_pan"),
        *[line(name, 0, "adapter") for name in ("pre_begin", "pre_end", "pre_real", "pre_imag", "pre_mag", "pre_phase", "pre_freq", "pre_pan")],
        line("adapter", 0, "tag_c"), line("adapter", 1, "tag_m"), line("adapter", 2, "tag_p"), line("adapter", 3, "tag_f"), line("adapter", 4, "tag_pan"), line("adapter", 5, "controller"), line("adapter", 6, "diag_adapter"), line("adapter", 6, "adapter_status", 1),
        line("tag_c", 0, "controller"), line("tag_m", 0, "controller"), line("tag_p", 0, "controller"), line("tag_f", 0, "controller"), line("tag_pan", 0, "controller"),
        line("controller", 0, "wave_route"), line("wave_route", 0, "wave_name"), line("wave_name", 0, "wave_send"),
        line("controller", 1, "poly_router"), line("poly_router", 0, "poly"), line("controller", 2, "diag_music"), line("controller", 2, "status", 1),
        line("poly", 0, "master_l"), line("poly", 1, "master_r"), line("master_l", 0, "lim_l"), line("master_r", 0, "lim_r"),
        line("lim_l", 0, "meter_l"), line("lim_r", 0, "meter_r"), line("lim_l", 0, "dac"), line("lim_r", 0, "dac", 1),
        line("lim_l", 0, "sum"), line("lim_r", 0, "sum", 1), line("sum", 0, "memory_gain"), line("memory_gain", 0, "poke"),
        line("x_phase", 0, "x_scale"), line("x_scale", 0, "poke", 1), line("y_phase", 0, "y_scale"), line("y_scale", 0, "poke", 2),
        *[line(name, 0, "send") for name in ("coherent", "unread", "recorded", "record", "xz", "y0")],
        line("xz", 0, "phase_send"), line("y0", 0, "phase_send"), line("four_observable", 0, "phase_send"),
        line("phase_norm", 0, "phase_clip"), line("phase_clip", 0, "phase_prepend"), line("phase_prepend", 0, "phase_send"),
        *[line(name, 0, "phase_norm") for name in ("phase_0", "phase_y", "phase_pi", "phase_minus_y", "phase_tau")],
        line("rate_hz", 0, "rate_prepend"), line("rate_prepend", 0, "phase_send"),
        line("smooth_ms", 0, "smooth_prepend"), line("smooth_prepend", 0, "phase_send"),
        line("q0_phase", 0, "q0_prepend"), line("q0_prepend", 0, "phase_send"),
        line("q1_phase", 0, "q1_prepend"), line("q1_prepend", 0, "phase_send"),
        line("q2_phase", 0, "q2_prepend"), line("q2_prepend", 0, "phase_send"),
        line("q3_phase", 0, "q3_prepend"), line("q3_prepend", 0, "phase_send"),
        line("mapping_morph", 0, "morph_prepend"), line("morph_prepend", 0, "controller"),
        *[line(name, 0, "mapping_morph") for name in ("morph_rel", "morph_mid", "morph_comp")],
        *[line(name, 0, "controller") for name in ("map_example_1", "map_example_2", "map_example_3", "map_example_all", "map_clear")],
        *[line(name, 0, "controller") for name in ("cell_example_1", "cell_example_2", "cell_example_3", "cell_example_all", "cell_clear")],
    ]
    dependencies = [
        {"name": "OSC-route.mxo", "type": "iLaX"},
        {"name": "qmb_heisenberg_adapter_v1.js", "type": "TEXT"},
        {"name": "qmb_heisenberg_rings_controller_v1.js", "type": "TEXT"},
        {"name": "qmb_heisenberg_rings_poly_router_v1.js", "type": "TEXT"},
        {"name": "qmb_heisenberg_rings_voice_v1.maxpat", "type": "JSON"},
    ]
    return patcher([45., 40., 1210., 1380.], boxes, lines, dependencies)


def patcher(rect: list[float], boxes: list[dict[str, Any]], lines: list[dict[str, Any]], dependencies: list[dict[str, str]]) -> dict[str, Any]:
    return {"patcher": {"fileversion": 1, "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1}, "classnamespace": "box", "rect": rect, "boxes": boxes, "lines": lines, "dependency_cache": dependencies, "autosave": 0}}


def validate(document: dict[str, Any]) -> None:
    p = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in p["boxes"]}
    if len(boxes) != len(p["boxes"]):
        raise RuntimeError("duplicate box identifier")
    for entry in p["lines"]:
        source, outlet = entry["patchline"]["source"]
        destination, inlet = entry["patchline"]["destination"]
        if source not in boxes or destination not in boxes:
            raise RuntimeError(f"dangling patchline {source}->{destination}")
        if outlet >= boxes[source].get("numoutlets", 0) or inlet >= boxes[destination].get("numinlets", 0):
            raise RuntimeError(f"invalid patchline {source}[{outlet}]->{destination}[{inlet}]")


def main() -> int:
    voice = voice_patch()
    instrument = main_patch()
    validate(voice)
    validate(instrument)
    (ROOT / "qmb_heisenberg_rings_voice_v1.maxpat").write_text(json.dumps(voice, indent=2) + "\n", encoding="utf-8")
    (ROOT / "QMW_Heisenberg_Rings_Matrix_Instrument_v1.maxpat").write_text(json.dumps(instrument, indent=2) + "\n", encoding="utf-8")
    print("generated qmb_heisenberg_rings_voice_v1.maxpat")
    print("generated QMW_Heisenberg_Rings_Matrix_Instrument_v1.maxpat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
