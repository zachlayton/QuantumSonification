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


voice_boxes = [
    # poly~ voices require in/out~ objects. Ordinary inlet/outlet objects make
    # an abstraction, but do not expose MSP signal outlets on the poly~ host.
    box("in", "newobj", [25, 25, 42, 22], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
    box("route", "newobj", [70, 29, 72, 22], text="route grain", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("grain_trigger", "newobj", [155, 29, 52, 22], text="t l l", numinlets=1, numoutlets=2, outlettype=["list", "list"]),
    box("ack", "newobj", [220, 29, 105, 22], text="prepend received", numinlets=1, numoutlets=1, outlettype=[""]),
    box("out_ack", "newobj", [335, 29, 42, 22], text="out 1", numinlets=1, numoutlets=0),
    box("unpack", "newobj", [25, 70, 245, 22], text="unpack f f f f f f f f f f", numinlets=1, numoutlets=10, outlettype=["float"] * 10),
    box("energy_freq", "newobj", [25, 112, 145, 22], text="expr 70.*pow(102.857,$f1)", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("cycle", "newobj", [25, 150, 55, 22], text="cycle~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("phase", "newobj", [185, 112, 105, 22], text="expr ($f1+1.)*0.5", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("amp_sig", "newobj", [95, 150, 45, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
    box("tonal_amp", "newobj", [25, 188, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("decay_store", "newobj", [310, 112, 40, 22], text="f 5.", numinlets=2, numoutlets=1, outlettype=["float"]),
    box("x_trigger", "newobj", [365, 112, 45, 22], text="t b f", numinlets=1, numoutlets=2, outlettype=["bang", "float"]),
    box("env_message", "message", [310, 150, 100, 22], text="1., 0. $1", numinlets=2, numoutlets=1, outlettype=[""]),
    box("env", "newobj", [310, 188, 45, 22], text="line~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("enveloped", "newobj", [80, 226, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("left_gain", "newobj", [365, 150, 150, 22], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("right_gain", "newobj", [525, 150, 150, 22], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("left_sig", "newobj", [365, 188, 45, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
    box("right_sig", "newobj", [525, 188, 45, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
    box("left", "newobj", [80, 264, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("right", "newobj", [150, 264, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("out_left", "newobj", [80, 308, 52, 22], text="out~ 1", numinlets=1, numoutlets=0),
    box("out_right", "newobj", [150, 308, 52, 22], text="out~ 2", numinlets=1, numoutlets=0),
]

voice_lines = [
    line("in", 0, "route"), line("route", 0, "grain_trigger"),
    line("grain_trigger", 0, "unpack"), line("grain_trigger", 1, "ack"), line("ack", 0, "out_ack"),
    line("unpack", 8, "energy_freq"), line("energy_freq", 0, "cycle", 0),
    line("unpack", 4, "phase"), line("phase", 0, "cycle", 1),
    line("unpack", 3, "amp_sig"), line("cycle", 0, "tonal_amp", 0),
    line("amp_sig", 0, "tonal_amp", 1),
    line("unpack", 9, "decay_store", 1), line("unpack", 0, "x_trigger"),
    line("x_trigger", 0, "decay_store", 0), line("decay_store", 0, "env_message"),
    line("env_message", 0, "env"), line("tonal_amp", 0, "enveloped", 0),
    line("env", 0, "enveloped", 1),
    line("x_trigger", 1, "left_gain"), line("x_trigger", 1, "right_gain"),
    line("left_gain", 0, "left_sig"), line("right_gain", 0, "right_sig"),
    line("enveloped", 0, "left", 0), line("left_sig", 0, "left", 1),
    line("enveloped", 0, "right", 0), line("right_sig", 0, "right", 1),
    line("left", 0, "out_left"), line("right", 0, "out_right"),
]

voice_patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [90, 90, 720, 380],
        "boxes": voice_boxes,
        "lines": voice_lines,
        "autosave": 0,
    }
}

host_boxes = [
    box("title", "comment", [25, 15, 850, 25], text="QMW 3D Wavefunction Cloud Grains v1 — no sustained chord", fontsize=16),
    box("subtitle", "comment", [25, 44, 900, 35], text="Every probability sample becomes a self-contained grain: default 0.25 ms attack + 5 ms decay."),
    # The main density/GRW engine owns Max port 7400.  The cloud has a
    # dedicated receiver so its high-rate grain stream cannot contend with it.
    box("udp", "newobj", [25, 92, 115, 22], text="udpreceive 7480", numinlets=0, numoutlets=1, outlettype=[""]),
    box("root", "newobj", [155, 92, 240, 22], text="OSC-route /qmw/wavefunction/cloud", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("route", "newobj", [410, 92, 180, 22], text="OSC-route /grain /frame /end", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("dispatch", "newobj", [410, 132, 250, 22], text="js qmw_wavefunction_cloud_dispatch_v1.js", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("poly", "newobj", [410, 182, 380, 22], text="poly~ qmw_wavefunction_cloud_grain_voice_v1.maxpat 64 @steal 1", numinlets=1, numoutlets=3, outlettype=["signal", "signal", ""]),
    # live.gain~ has two real signal inputs/outputs. gain~ is mono; its second
    # inlet is a level-control inlet and cannot receive the right audio channel.
    box(
        "gain",
        "live.gain~",
        [810, 170, 96, 140],
        numinlets=2,
        numoutlets=5,
        outlettype=["signal", "signal", "", "float", "list"],
        parameter_enable=1,
        saved_attribute_attributes={
            "valueof": {
                "parameter_initial": [-12.0],
                "parameter_initial_enable": 1,
                "parameter_longname": "Wavefunction cloud output",
                "parameter_mmax": 6.0,
                "parameter_mmin": -70.0,
                "parameter_modmode": 0,
                "parameter_shortname": "cloud output",
                "parameter_type": 0,
                "parameter_unitstyle": 4,
            }
        },
        varname="wavefunction_cloud_output",
    ),
    box("pre_meter_l", "newobj", [700, 220, 70, 22], text="meter~", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("pre_meter_r", "newobj", [700, 250, 70, 22], text="meter~", numinlets=1, numoutlets=1, outlettype=["float"]),
    box("dac", "newobj", [800, 335, 65, 22], text="ezdac~", numinlets=2, numoutlets=0),
    box("dsp_on", "newobj", [885, 335, 75, 22], text="loadmess 1", numinlets=0, numoutlets=1, outlettype=["int"]),
    box("test_label", "comment", [25, 182, 175, 22], text="Click to test poly~ locally:"),
    box(
        "test_grain",
        "message",
        [25, 207, 360, 22],
        text="target 1, grain -0.2 0. 0. 0.8 0. 0. 0. 0. 0.4 80.",
        numinlets=2,
        numoutlets=1,
        outlettype=[""],
    ),
    box("meter_note", "comment", [665, 280, 135, 35], text="poly~ signal meters\n(before output gain)"),
    box("direct_label", "comment", [25, 252, 250, 22], text="DIRECT AUDIO TEST (bypasses poly~):"),
    box("direct_toggle", "toggle", [278, 252, 24, 24], numinlets=1, numoutlets=1, outlettype=["int"]),
    box("direct_cycle", "newobj", [310, 252, 70, 22], text="cycle~ 220", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("direct_amp", "newobj", [390, 252, 52, 22], text="*~ 0.08", numinlets=2, numoutlets=1, outlettype=["signal"]),
    box("direct_note", "comment", [25, 280, 430, 35], text="Toggle on: a steady 220 Hz tone proves DSP, output gain, and audio device."),
    box("unmute", "newobj", [410, 215, 100, 22], text="loadmess mute 0 0", numinlets=0, numoutlets=1, outlettype=[""]),
    box("voice_ack", "message", [520, 215, 270, 22], text="waiting for poly~ voice acknowledgement...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("ack_note", "comment", [520, 240, 275, 22], text="Changes to 'received ...' when a voice loads and routes a grain."),
    box("status", "message", [25, 132, 350, 22], text="waiting for 5 ms cloud grains...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("note", "comment", [25, 390, 900, 50], text="Start: python examples/wavefunction_cloud_osc_v1.py --source schrodinger_packet_3d --grid 32 --fps 30 --grains 16 --decay-ms 5"),
]

host_lines = [
    line("udp", 0, "root"), line("root", 0, "route"),
    line("route", 0, "dispatch"), line("dispatch", 0, "poly"),
    line("dispatch", 1, "status", 1),
    line("poly", 0, "gain", 0), line("poly", 1, "gain", 1),
    line("poly", 0, "pre_meter_l", 0), line("poly", 1, "pre_meter_r", 0),
    line("gain", 0, "dac", 0), line("gain", 1, "dac", 1),
    line("dsp_on", 0, "dac", 0), line("test_grain", 0, "poly", 0),
    line("direct_cycle", 0, "direct_amp", 0), line("direct_toggle", 0, "direct_amp", 1),
    line("direct_amp", 0, "gain", 0), line("direct_amp", 0, "gain", 1),
    line("unmute", 0, "poly", 0), line("poly", 2, "voice_ack", 1),
]

host_patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [80, 70, 960, 500],
        "boxes": host_boxes,
        "lines": host_lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_wavefunction_cloud_dispatch_v1.js", "type": "TEXT"},
            {"name": "qmw_wavefunction_cloud_grain_voice_v1.maxpat", "type": "JSON"},
        ],
        "autosave": 0,
    }
}

(ROOT / "qmw_wavefunction_cloud_grain_voice_v1.maxpat").write_text(
    json.dumps(voice_patcher, indent=2) + "\n", encoding="utf-8"
)
host_json = json.dumps(host_patcher, indent=2) + "\n"
(ROOT / "QMW_Wavefunction_Cloud_Grains_v1.maxpat").write_text(host_json, encoding="utf-8")
# A distinct filename forces Max to load the regenerated patch instead of
# focusing an older in-memory document with the same path.
(ROOT / "QMW_Wavefunction_Cloud_Grains_v1_1.maxpat").write_text(host_json, encoding="utf-8")
(ROOT / "QMW_Wavefunction_Cloud_Grains_v1_2.maxpat").write_text(host_json, encoding="utf-8")
(ROOT / "QMW_Wavefunction_Cloud_Grains_v1_3.maxpat").write_text(host_json, encoding="utf-8")
