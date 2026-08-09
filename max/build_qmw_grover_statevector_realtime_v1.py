from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SURFACE_SOURCE = ROOT / "control_room_modules/QMW_Realtime_Surface_Reverb_v3.maxpat"
SURFACE_LOCAL_NAME = "QMW_Realtime_Surface_Reverb_Grover_v1.maxpat"


def box(identifier, maxclass, rect, **values):
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0, order=None):
    data = {"source": [source, outlet], "destination": [destination, inlet]}
    if order is not None:
        data["order"] = order
    return {"patchline": data}


voice_boxes = [
    box("in", "newobj", [20, 20, 42, 22], text="in 1", numinlets=0, numoutlets=1),
    box("route", "newobj", [75, 20, 72, 22], text="route mode", numinlets=1, numoutlets=2),
    box("unpack", "newobj", [20, 60, 185, 22], text="unpack f f f f", numinlets=1, numoutlets=4),
    box("freq_pack", "newobj", [20, 98, 68, 22], text="pack f f", numinlets=2, numoutlets=1),
    box("freq_line", "newobj", [20, 132, 48, 22], text="line~", numinlets=2, numoutlets=1),
    box("osc", "newobj", [20, 166, 58, 22], text="cycle~", numinlets=2, numoutlets=1),
    box("gain_pack", "newobj", [100, 98, 68, 22], text="pack f f", numinlets=2, numoutlets=1),
    box("gain_line", "newobj", [100, 132, 48, 22], text="line~", numinlets=2, numoutlets=1),
    box("amp", "newobj", [90, 166, 38, 22], text="*~", numinlets=2, numoutlets=1),
    box("pan_l", "newobj", [180, 98, 145, 22], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1),
    box("pan_r", "newobj", [335, 98, 145, 22], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1),
    box("pan_l_pack", "newobj", [180, 132, 68, 22], text="pack f f", numinlets=2, numoutlets=1),
    box("pan_r_pack", "newobj", [335, 132, 68, 22], text="pack f f", numinlets=2, numoutlets=1),
    box("pan_l_line", "newobj", [180, 166, 48, 22], text="line~", numinlets=2, numoutlets=1),
    box("pan_r_line", "newobj", [335, 166, 48, 22], text="line~", numinlets=2, numoutlets=1),
    box("left", "newobj", [90, 205, 38, 22], text="*~", numinlets=2, numoutlets=1),
    box("right", "newobj", [145, 205, 38, 22], text="*~", numinlets=2, numoutlets=1),
    box("out_l", "newobj", [90, 245, 52, 22], text="out~ 1", numinlets=1, numoutlets=0),
    box("out_r", "newobj", [150, 245, 52, 22], text="out~ 2", numinlets=1, numoutlets=0),
]

voice_lines = [
    line("in", 0, "route"), line("route", 0, "unpack"),
    line("unpack", 3, "freq_pack", 1), line("unpack", 3, "gain_pack", 1),
    line("unpack", 3, "pan_l_pack", 1), line("unpack", 3, "pan_r_pack", 1),
    line("unpack", 0, "freq_pack", 0), line("freq_pack", 0, "freq_line"), line("freq_line", 0, "osc"),
    line("unpack", 1, "gain_pack", 0), line("gain_pack", 0, "gain_line"),
    line("osc", 0, "amp"), line("gain_line", 0, "amp", 1),
    line("unpack", 2, "pan_l"), line("unpack", 2, "pan_r"),
    line("pan_l", 0, "pan_l_pack"), line("pan_r", 0, "pan_r_pack"),
    line("pan_l_pack", 0, "pan_l_line"), line("pan_r_pack", 0, "pan_r_line"),
    line("amp", 0, "left"), line("pan_l_line", 0, "left", 1),
    line("amp", 0, "right"), line("pan_r_line", 0, "right", 1),
    line("left", 0, "out_l"), line("right", 0, "out_r"),
]

voice = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box", "rect": [100, 100, 510, 300],
        "boxes": voice_boxes, "lines": voice_lines, "autosave": 0,
    }
}


host_boxes = [
    box("title", "comment", [25, 15, 920, 26], text="QMW GROVER STATEVECTOR — LITERAL REALTIME SONIFICATION", fontsize=17, fontface=1),
    box("subtitle", "comment", [25, 43, 1100, 40], text="65,536 complex amplitudes evolve exactly. Max hears measured oracle and diffusion frames; no closed-form trajectory drives the sound."),
    box("udp", "newobj", [25, 95, 118, 22], text="udpreceive 7493", numinlets=0, numoutlets=1),
    box("root", "newobj", [155, 95, 245, 22], text="OSC-route /qmw/grover/statevector", numinlets=1, numoutlets=2),
    box("route", "newobj", [415, 95, 290, 22], text="OSC-route /frame /modes /found /state", numinlets=1, numoutlets=5),
    box("pre_frame", "newobj", [415, 132, 92, 22], text="prepend frame"),
    box("pre_modes", "newobj", [515, 132, 92, 22], text="prepend modes"),
    box("pre_found", "newobj", [615, 132, 92, 22], text="prepend found"),
    box("pre_state", "newobj", [715, 132, 92, 22], text="prepend state"),
    box("dispatch", "newobj", [415, 170, 255, 22], text="js qmw_grover_statevector_dispatch_v1.js", numinlets=1, numoutlets=5, outlettype=["", "", "float", "", "int"]),
    box("status", "message", [25, 132, 375, 22], text="waiting for exact statevector stream...", numinlets=2, numoutlets=1),
    box("prob_label", "comment", [25, 175, 155, 20], text="MARKED PROBABILITY"),
    box("prob", "flonum", [180, 175, 130, 22], format=6, numinlets=1, numoutlets=2),
    box("meter", "newobj", [320, 175, 80, 22], text="scale 0. 1. 0 127", numinlets=6, numoutlets=1),
    box("prob_slider", "slider", [25, 205, 375, 20], size=128, min=0.0, mult=1.0, numinlets=1, numoutlets=1),
    box("poly", "newobj", [415, 215, 385, 22], text="poly~ qmw_grover_walsh_mode_voice_v1.maxpat 64 @steal 0", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
    box("send_l", "newobj", [415, 255, 145, 22], text="send~ qmw_spectral_L"),
    box("send_r", "newobj", [570, 255, 145, 22], text="send~ qmw_spectral_R"),
    # Max's bpatcher loader does not reliably resolve a path containing a
    # subdirectory here.  The builder places an identical generated copy next
    # to this host patch and loads it by sibling filename instead.
    box("surface", "bpatcher", [25, 265, 760, 490], name=SURFACE_LOCAL_NAME, numinlets=0, numoutlets=0),
    box("surface_ctl", "newobj", [815, 215, 142, 22], text="s qmw.surface.control", numinlets=1, numoutlets=0),
    box("wet_l", "newobj", [815, 265, 145, 22], text="receive~ qmw_surface_L"),
    box("wet_r", "newobj", [970, 265, 145, 22], text="receive~ qmw_surface_R"),
    box("ringmod", "newobj", [815, 305, 265, 22], text="abl.dsp.ringmod~ @frequency 7. @mix 0.8", numinlets=2, numoutlets=2, outlettype=["signal", "signal"]),
    box("tides", "newobj", [815, 345, 250, 22], text="abl.dsp.tides~ @rate 0.18 @tides 0.7 @mix 0.7", numinlets=5, numoutlets=2, outlettype=["signal", "signal"]),
    box("modal_l", "newobj", [815, 385, 235, 22], text="abl.dsp.modalresonator~ 84 0.7 @decay 0.75 @damping 0.28", numinlets=3, numoutlets=1, outlettype=["signal"]),
    box("modal_r", "newobj", [1060, 385, 235, 22], text="abl.dsp.modalresonator~ 91 0.7 @decay 0.75 @damping 0.28", numinlets=3, numoutlets=1, outlettype=["signal"]),
    box("prism", "newobj", [815, 425, 280, 22], text="abl.dsp.prism~ @decay 0.86 @size 0.72 @mix 1.", numinlets=4, numoutlets=2, outlettype=["signal", "signal"]),
    box("event_sel", "newobj", [1120, 215, 62, 22], text="sel 1 0", numinlets=1, numoutlets=3),
    box("found_trigger", "newobj", [1120, 250, 70, 22], text="t b b b", numinlets=1, numoutlets=3),
    box("freeze", "message", [1200, 250, 62, 22], text="freeze 1"),
    box("unfreeze", "message", [1200, 280, 62, 22], text="freeze 0"),
    box("moving_down", "message", [1120, 315, 70, 22], text="0. 700"),
    box("held_up", "message", [1200, 315, 70, 22], text="1. 700"),
    box("moving_up", "message", [1120, 345, 70, 22], text="1. 80"),
    box("held_down", "message", [1200, 345, 70, 22], text="0. 80"),
    box("moving_gain", "newobj", [1120, 385, 48, 22], text="line~"),
    box("held_gain", "newobj", [1200, 385, 48, 22], text="line~"),
    box("move_l", "newobj", [815, 465, 38, 22], text="*~"),
    box("move_r", "newobj", [860, 465, 38, 22], text="*~"),
    box("hold_l", "newobj", [925, 465, 38, 22], text="*~"),
    box("hold_r", "newobj", [970, 465, 38, 22], text="*~"),
    box("sum_l", "newobj", [815, 505, 38, 22], text="+~"),
    box("sum_r", "newobj", [870, 505, 38, 22], text="+~"),
    box("wet_scale_l", "newobj", [815, 540, 55, 22], text="*~ 0.7"),
    box("wet_scale_r", "newobj", [880, 540, 55, 22], text="*~ 0.7"),
    box("dry_l", "newobj", [950, 540, 55, 22], text="*~ 0.3"),
    box("dry_r", "newobj", [1015, 540, 55, 22], text="*~ 0.3"),
    box("final_l", "newobj", [815, 575, 38, 22], text="+~"),
    box("final_r", "newobj", [870, 575, 38, 22], text="+~"),
    box(
        "gain",
        "live.gain~",
        [950, 575, 95, 125],
        numinlets=2,
        numoutlets=5,
        outlettype=["signal", "signal", "", "float", "list"],
        parameter_enable=1,
        saved_attribute_attributes={
            "valueof": {
                "parameter_initial": [-9.0],
                "parameter_initial_enable": 1,
                "parameter_longname": "Grover statevector output",
                "parameter_mmax": 6.0,
                "parameter_mmin": -70.0,
                "parameter_modmode": 0,
                "parameter_shortname": "Grover output",
                "parameter_type": 0,
                "parameter_unitstyle": 4,
            }
        },
        varname="grover_statevector_output",
    ),
    box("dac", "newobj", [965, 720, 68, 22], text="ezdac~", numinlets=2, numoutlets=0),
    box("init", "newobj", [1080, 575, 190, 22], text="loadmess 0.7 0.7 0.8", numinlets=0, numoutlets=1),
    box("init_unpack", "newobj", [1080, 610, 95, 22], text="unpack f f f"),
    box("init_wet", "message", [1080, 645, 88, 22], text="dry_wet $1"),
    box("init_deform", "message", [1175, 645, 72, 22], text="deform $1"),
    box("init_ring", "message", [1255, 645, 52, 22], text="mix $1"),
    box("command", "comment", [815, 760, 495, 42], text="Run: python feedback/grover_statevector_osc_v1.py\nDefault target 57893 = |1110001000100101>, exact 16-qubit evolution. Add --backend mlx for Metal."),
]

host_lines = [
    line("udp", 0, "root"), line("root", 0, "route"),
    line("route", 0, "pre_frame"), line("route", 1, "pre_modes"), line("route", 2, "pre_found"), line("route", 3, "pre_state"),
    line("pre_frame", 0, "dispatch"), line("pre_modes", 0, "dispatch"), line("pre_found", 0, "dispatch"), line("pre_state", 0, "dispatch"),
    line("dispatch", 0, "poly"), line("dispatch", 1, "status", 1), line("dispatch", 2, "prob"), line("dispatch", 2, "meter"), line("meter", 0, "prob_slider"),
    line("dispatch", 3, "surface_ctl"), line("dispatch", 4, "event_sel"),
    line("poly", 0, "send_l"), line("poly", 1, "send_r"),
    line("wet_l", 0, "ringmod", 0), line("wet_r", 0, "ringmod", 1),
    line("ringmod", 0, "tides", 0), line("ringmod", 1, "tides", 1),
    line("tides", 0, "modal_l"), line("tides", 1, "modal_r"),
    line("modal_l", 0, "prism", 0), line("modal_r", 0, "prism", 1),
    line("event_sel", 0, "found_trigger"), line("event_sel", 1, "unfreeze"),
    line("found_trigger", 0, "freeze"), line("found_trigger", 1, "moving_down"), line("found_trigger", 2, "held_up"), line("freeze", 0, "prism"),
    line("unfreeze", 0, "prism"), line("event_sel", 1, "moving_up"), line("event_sel", 1, "held_down"),
    line("moving_down", 0, "moving_gain"), line("moving_up", 0, "moving_gain"), line("held_up", 0, "held_gain"), line("held_down", 0, "held_gain"),
    line("modal_l", 0, "move_l"), line("modal_r", 0, "move_r"), line("moving_gain", 0, "move_l", 1), line("moving_gain", 0, "move_r", 1),
    line("prism", 0, "hold_l"), line("prism", 1, "hold_r"), line("held_gain", 0, "hold_l", 1), line("held_gain", 0, "hold_r", 1),
    line("move_l", 0, "sum_l"), line("hold_l", 0, "sum_l", 1), line("move_r", 0, "sum_r"), line("hold_r", 0, "sum_r", 1),
    line("sum_l", 0, "wet_scale_l"), line("sum_r", 0, "wet_scale_r"), line("poly", 0, "dry_l"), line("poly", 1, "dry_r"),
    line("wet_scale_l", 0, "final_l"), line("dry_l", 0, "final_l", 1), line("wet_scale_r", 0, "final_r"), line("dry_r", 0, "final_r", 1),
    line("final_l", 0, "gain", 0), line("final_r", 0, "gain", 1), line("gain", 0, "dac"), line("gain", 1, "dac", 1),
    line("init", 0, "init_unpack"), line("init_unpack", 0, "init_wet"), line("init_unpack", 1, "init_deform"), line("init_unpack", 2, "init_ring"),
    line("init_wet", 0, "surface_ctl"), line("init_deform", 0, "surface_ctl"), line("init_ring", 0, "ringmod"),
]

host = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box", "rect": [45, 45, 1340, 840],
        "boxes": host_boxes, "lines": host_lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_grover_statevector_dispatch_v1.js", "type": "TEXT"},
            {"name": "qmw_grover_walsh_mode_voice_v1.maxpat", "type": "JSON"},
            {"name": SURFACE_LOCAL_NAME, "type": "JSON"},
            {"name": "abl.dsp.ringmod~.mxo", "type": "iLaX"},
            {"name": "abl.dsp.tides~.mxo", "type": "iLaX"},
            {"name": "abl.dsp.prism~.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

if not SURFACE_SOURCE.is_file():
    raise FileNotFoundError(f"missing surface-reverb source patch: {SURFACE_SOURCE}")
(ROOT / SURFACE_LOCAL_NAME).write_text(SURFACE_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
(ROOT / "qmw_grover_walsh_mode_voice_v1.maxpat").write_text(json.dumps(voice, indent=2) + "\n")
host_json = json.dumps(host, indent=2) + "\n"
(ROOT / "QMW_Grover_Statevector_Realtime_v1.maxpat").write_text(host_json)
# A distinct filename avoids Max focusing a cached, already-open document.
(ROOT / "QMW_Grover_Statevector_Realtime_v1_1.maxpat").write_text(host_json)
(ROOT / "QMW_Grover_Statevector_Realtime_v1_2.maxpat").write_text(host_json)
