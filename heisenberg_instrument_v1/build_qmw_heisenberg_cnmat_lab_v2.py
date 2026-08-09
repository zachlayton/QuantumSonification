"""Generate the CNMAT/SDIF Heisenberg laboratory Max 9 patch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def box(identifier, maxclass, rect, **values):
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def patch():
    boxes = [
        box("title", "comment", [25., 14., 1130., 28.], text="QMW HEISENBERG LAB v2 — CNMAT SPECTRAL / 16 × 16 TRANSITION FIELD", fontsize=17.),
        box("description", "comment", [25., 45., 1140., 42.], text="The same 256 ordered relations become bandwidth-enhanced partials, a shared-input resonator bank, and simultaneous 1TRC / 1RES SDIF frames. Measurement changes the excitation process, not merely the tuning."),
        box("udp", "newobj", [25., 100., 126., 22.], text="udpreceive 7400", numinlets=1, numoutlets=1, outlettype=[""]),
        box("route_qmw", "newobj", [170., 100., 104., 22.], text="OSC-route /qmw", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_h", "newobj", [292., 100., 145., 22.], text="OSC-route /heisenberg", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_active", "newobj", [455., 100., 125., 22.], text="OSC-route /active", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_meta", "newobj", [25., 140., 650., 22.], text="OSC-route /mode /outcome /disturbance /coherence_before /coherence_after /matrix", numinlets=1, numoutlets=7, outlettype=[""] * 7),
        box("route_matrix", "newobj", [25., 180., 810., 22.], text="OSC-route /begin /end /magnitude_normalized /frequency_hz /phase /pan /real /imag", numinlets=1, numoutlets=9, outlettype=[""] * 9),
        box("pre_begin", "newobj", [850., 180., 105., 22.], text="prepend begin", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_end", "newobj", [970., 180., 95., 22.], text="prepend end", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_mag", "newobj", [25., 218., 185., 22.], text="prepend magnitude_normalized", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_freq", "newobj", [225., 218., 150., 22.], text="prepend frequency_hz", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_phase", "newobj", [390., 218., 110., 22.], text="prepend phase", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_pan", "newobj", [515., 218., 100., 22.], text="prepend pan", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_mode", "newobj", [700., 140., 105., 22.], text="prepend mode", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_outcome", "newobj", [815., 140., 125., 22.], text="prepend outcome", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_disturbance", "newobj", [950., 140., 145., 22.], text="prepend disturbance", numinlets=1, numoutlets=1, outlettype=[""]),
        box("js", "newobj", [25., 265., 305., 22.], text="js qmw_heisenberg_cnmat_spectral_v2.js", numinlets=1, numoutlets=9, outlettype=[""] * 9),

        box("sin_l", "newobj", [25., 310., 105., 22.], text="sinusoids~ bwe", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("sin_r", "newobj", [145., 310., 105., 22.], text="sinusoids~ bwe", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("res_l", "newobj", [270., 310., 125., 22.], text="resonators~ smooth", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("res_r", "newobj", [410., 310., 125., 22.], text="resonators~ smooth", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("noise", "newobj", [555., 310., 52., 22.], text="noise~", numinlets=0, numoutlets=1, outlettype=["signal"]),
        box("noise_mul", "newobj", [555., 350., 42., 22.], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("control_route", "newobj", [640., 310., 285., 22.], text="route impulse noise_gain sin_gain res_gain", numinlets=1, numoutlets=5, outlettype=[""] * 5),
        box("noise_pack", "newobj", [700., 350., 92., 22.], text="pack 0. 80.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("noise_line", "newobj", [700., 382., 42., 22.], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("sin_pack", "newobj", [805., 350., 92., 22.], text="pack 0. 80.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("sin_line", "newobj", [805., 382., 42., 22.], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("res_pack", "newobj", [910., 350., 92., 22.], text="pack 0. 80.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("res_line", "newobj", [910., 382., 42., 22.], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("sin_l_gain", "newobj", [25., 400., 42., 22.], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sin_r_gain", "newobj", [145., 400., 42., 22.], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("res_l_gain", "newobj", [270., 400., 42., 22.], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("res_r_gain", "newobj", [410., 400., 42., 22.], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_l", "newobj", [25., 445., 42., 22.], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r", "newobj", [145., 445., 42., 22.], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_l", "newobj", [25., 485., 52., 22.], text="*~ 0.55", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [145., 485., 52., 22.], text="*~ 0.55", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("dac", "newobj", [25., 525., 52., 32.], text="ezdac~", numinlets=2, numoutlets=0),

        box("matrix", "jit.cellblock", [610., 430., 555., 350.], cols=16, rows=16, colhead=0, rowhead=0, numinlets=2, numoutlets=4, outlettype=[""] * 4),
        box("status", "message", [25., 580., 550., 42.], text="waiting for CNMAT Heisenberg field...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("sdif_label", "comment", [25., 638., 550., 20.], text="LIVE SDIF MEMORY — every active matrix is written as both sinusoidal tracks and resonances"),
        box("trc_buffer", "newobj", [25., 668., 205., 22.], text="SDIF-buffer qmw_heisenberg_trc", numinlets=1, numoutlets=1, outlettype=[""]),
        box("trc_poke", "newobj", [245., 668., 215., 22.], text="SDIF-listpoke qmw_heisenberg_trc", numinlets=1, numoutlets=0),
        box("res_buffer", "newobj", [25., 703., 205., 22.], text="SDIF-buffer qmw_heisenberg_res", numinlets=1, numoutlets=1, outlettype=[""]),
        box("res_poke", "newobj", [245., 703., 215., 22.], text="SDIF-listpoke qmw_heisenberg_res", numinlets=1, numoutlets=0),
        box("write_trc", "message", [25., 738., 250., 22.], text="write QMW_Heisenberg_1TRC.sdif", numinlets=2, numoutlets=1, outlettype=[""]),
        box("write_res", "message", [290., 738., 250., 22.], text="write QMW_Heisenberg_1RES.sdif", numinlets=2, numoutlets=1, outlettype=[""]),

        box("controls", "comment", [25., 790., 1140., 20.], text="ONE CONTROLLED COMPARISON — keep XZ0 fixed and change only the status of the intermediate measurement"),
        box("coherent", "message", [25., 820., 225., 22.], text="/qmw/heisenberg/mode coherent", numinlets=2, numoutlets=1, outlettype=[""]),
        box("unread", "message", [260., 820., 215., 22.], text="/qmw/heisenberg/mode unread", numinlets=2, numoutlets=1, outlettype=[""]),
        box("recorded", "message", [485., 820., 230., 22.], text="/qmw/heisenberg/mode recorded", numinlets=2, numoutlets=1, outlettype=[""]),
        box("record", "message", [725., 820., 195., 22.], text="/qmw/heisenberg/record 1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("test", "message", [940., 820., 72., 22.], text="test", numinlets=2, numoutlets=1, outlettype=[""]),
        box("resume", "message", [1022., 820., 72., 22.], text="resume", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_xz", "message", [25., 855., 220., 22.], text="/qmw/heisenberg/observable XZ0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_x", "message", [260., 855., 210., 22.], text="/qmw/heisenberg/observable X0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_y", "message", [485., 855., 210., 22.], text="/qmw/heisenberg/observable Y0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_z", "message", [710., 855., 210., 22.], text="/qmw/heisenberg/observable Z0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("send", "newobj", [940., 855., 160., 22.], text="udpsend 127.0.0.1 7412", numinlets=1, numoutlets=0),
        box("compare_label", "comment", [25., 890., 1140., 20.], text="AUTO COMPARE (4 seconds each): COHERENT = alternatives retained  →  UNREAD = coherence lost, no fact retained  →  RECORDED = one outcome conditions the future"),
        box("compare_toggle", "toggle", [25., 918., 24., 24.], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("compare_toggle_label", "comment", [55., 920., 118., 20.], text="run comparison"),
        box("compare_metro", "newobj", [180., 918., 78., 22.], text="metro 4000", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("compare_counter", "newobj", [270., 918., 82., 22.], text="counter 0 2", numinlets=5, numoutlets=4, outlettype=["int", "", "", "int"]),
        box("compare_select", "newobj", [365., 918., 62., 22.], text="sel 0 1 2", numinlets=1, numoutlets=4, outlettype=["bang", "bang", "bang", ""]),
        box("listen", "comment", [455., 910., 700., 38.], text="Listen for continuity → diffuse/noisy resonance → outcome-triggered strike. The point is the changed measurement context, not three arbitrary presets."),
    ]

    lines = [
        line("udp", 0, "route_qmw"), line("route_qmw", 0, "route_h"), line("route_h", 0, "route_active"), line("route_active", 0, "route_meta"),
        line("route_meta", 0, "pre_mode"), line("route_meta", 1, "pre_outcome"), line("route_meta", 2, "pre_disturbance"), line("route_meta", 5, "route_matrix"),
        line("route_matrix", 0, "pre_begin"), line("route_matrix", 1, "pre_end"), line("route_matrix", 2, "pre_mag"), line("route_matrix", 3, "pre_freq"), line("route_matrix", 4, "pre_phase"), line("route_matrix", 5, "pre_pan"),
        line("pre_begin", 0, "js"), line("pre_end", 0, "js"), line("pre_mag", 0, "js"), line("pre_freq", 0, "js"), line("pre_phase", 0, "js"), line("pre_pan", 0, "js"), line("pre_mode", 0, "js"), line("pre_outcome", 0, "js"), line("pre_disturbance", 0, "js"),
        line("js", 0, "sin_l"), line("js", 1, "sin_r"), line("js", 2, "res_l"), line("js", 3, "res_r"), line("js", 4, "control_route"), line("js", 5, "matrix"), line("js", 6, "status", 1), line("js", 7, "trc_poke"), line("js", 8, "res_poke"),
        line("noise", 0, "noise_mul"), line("noise_line", 0, "noise_mul", 1), line("noise_mul", 0, "res_l"), line("noise_mul", 0, "res_r"),
        line("control_route", 0, "res_l"), line("control_route", 0, "res_r"), line("control_route", 1, "noise_pack"), line("noise_pack", 0, "noise_line"), line("control_route", 2, "sin_pack"), line("sin_pack", 0, "sin_line"), line("control_route", 3, "res_pack"), line("res_pack", 0, "res_line"),
        line("sin_l", 0, "sin_l_gain"), line("sin_r", 0, "sin_r_gain"), line("sin_line", 0, "sin_l_gain", 1), line("sin_line", 0, "sin_r_gain", 1), line("res_l", 0, "res_l_gain"), line("res_r", 0, "res_r_gain"), line("res_line", 0, "res_l_gain", 1), line("res_line", 0, "res_r_gain", 1),
        line("sin_l_gain", 0, "sum_l"), line("res_l_gain", 0, "sum_l", 1), line("sin_r_gain", 0, "sum_r"), line("res_r_gain", 0, "sum_r", 1), line("sum_l", 0, "master_l"), line("sum_r", 0, "master_r"), line("master_l", 0, "dac"), line("master_r", 0, "dac", 1),
        line("write_trc", 0, "trc_buffer"), line("write_res", 0, "res_buffer"),
        line("coherent", 0, "send"), line("unread", 0, "send"), line("recorded", 0, "send"), line("record", 0, "send"), line("obs_xz", 0, "send"), line("obs_x", 0, "send"), line("obs_y", 0, "send"), line("obs_z", 0, "send"), line("test", 0, "js"), line("resume", 0, "js"),
        line("compare_toggle", 0, "compare_metro"), line("compare_metro", 0, "compare_counter"), line("compare_counter", 0, "compare_select"), line("compare_select", 0, "coherent"), line("compare_select", 1, "unread"), line("compare_select", 2, "recorded"),
    ]
    return {"patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box", "rect": [70., 35., 1200., 990.], "gridsize": [15., 15.],
        "boxes": boxes, "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_heisenberg_cnmat_spectral_v2.js", "type": "TEXT"},
            {"name": "sinusoids~.mxo", "type": "iLaX"},
            {"name": "resonators~.mxo", "type": "iLaX"},
            {"name": "SDIF-buffer.mxo", "type": "iLaX"},
            {"name": "SDIF-listpoke.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }}


def main() -> int:
    output = ROOT / "QMW_Heisenberg_Laboratory_v2_CNMAT.maxpat"
    output.write_text(json.dumps(patch(), indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
