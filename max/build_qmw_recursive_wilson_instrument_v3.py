#!/usr/bin/env python3
"""Build the recursive Wilson QAC programmer and six-voice MPE Max patch."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROGRAMMER_SOURCE = ROOT / "QMW_QAC_Circuit_Programmer_v2.maxpat"
PROGRAMMER_OUTPUT = ROOT / "QMW_QAC_Circuit_Programmer_Recursive_v3.maxpat"
SENDER_SOURCE = ROOT / "qac_quantumsonification_sender_v1.maxpat"
SENDER_OUTPUT = ROOT / "qac_quantumsonification_sender_recursive_v3.maxpat"
INSTRUMENT_OUTPUT = ROOT / "QMW_Recursive_Wilson_Circuit_Instrument_v3.maxpat"
REFRESHED_JS = ROOT / "qmw_qac_circuit_programmer_recursive_v3_3.js"
REFRESHED_PROGRAMMER = ROOT / "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat"
REFRESHED_INSTRUMENT = ROOT / "QMW_Recursive_Wilson_Circuit_Instrument_v3_3.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def build_sender():
    document = json.loads(SENDER_SOURCE.read_text(encoding="utf-8"))
    for entry in document["patcher"]["boxes"]:
        item = entry["box"]
        if item.get("id") == "udp":
            item["text"] = "udpsend 127.0.0.1 7403"
        elif item.get("id") == "comment-port":
            item["text"] = "QAC seed circuit → recursive Wilson host :7403"
    SENDER_OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")


def build_programmer():
    document = json.loads(PROGRAMMER_SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["title"]["text"] = "QMW CIRCUIT PROGRAMMER · RECURSIVE WILSON v3"
    boxes["ui"].update(
        filename="qmw_qac_circuit_programmer_recursive_v3.js",
        jsarguments=["qmw_qac_circuit_programmer_recursive_v3.js"],
        numoutlets=7,
        outlettype=["", "", "", "", "", "", ""],
    )
    boxes["sender"]["text"] = "qac_quantumsonification_sender_recursive_v3"
    boxes["gate_udp"]["text"] = "udpsend 127.0.0.1 7403"
    boxes["gate_pack"]["text"] = "o.pack /qmw/qac/gate"

    controls = (
        ("next", 3, "/qmw/recursive/next", 25.0),
        ("start", 4, "/qmw/recursive/start", 205.0),
        ("stop", 5, "/qmw/recursive/stop", 385.0),
        ("reset", 6, "/qmw/recursive/reset", 565.0),
    )
    for name, outlet, address, x in controls:
        pack_id = name + "_pack"
        patcher["boxes"].append(box(pack_id, "newobj", [x, 610.0, 160.0, 22.0], text="o.pack " + address, numinlets=1, numoutlets=1, outlettype=["FullPacket"]))
        patcher["lines"].append(line("ui", outlet, pack_id))
        patcher["lines"].append(line(pack_id, 0, "gate_udp"))

    patcher["rect"] = [80.0, 80.0, 900.0, 680.0]
    dependencies = [entry for entry in patcher.get("dependency_cache", []) if entry.get("name") not in {
        "qmw_qac_circuit_programmer_v2.js", "qac_quantumsonification_sender_v1.maxpat"
    }]
    dependencies.extend([
        {"name": "qmw_qac_circuit_programmer_recursive_v3.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1},
        {"name": "qmw_qac_circuit_programmer_v2.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1},
        {"name": "qac_quantumsonification_sender_recursive_v3.maxpat", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "JSON", "implicit": 1},
    ])
    patcher["dependency_cache"] = dependencies
    PROGRAMMER_OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")


def build_instrument():
    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [70.0, 70.0, 1480.0, 850.0],
        "openinpresentation": 1,
        "gridsize": [15.0, 15.0],
        "boxes": [],
        "lines": [],
        "dependency_cache": [],
        "autosave": 0,
    }
    b = patcher["boxes"]
    l = patcher["lines"]
    b.extend([
        box("title", "comment", [20.0, 15.0, 1200.0, 30.0], text="QMW · RECURSIVE WILSON HEXANY CIRCUIT INSTRUMENT v3", fontsize=20.0),
        box("instructions", "comment", [20.0, 48.0, 1380.0, 42.0], text="Run examples/qmw_recursive_wilson_instrument_v3.py · choose the same MPE MIDI output below · pitch-bend range ±2 · RESEED changes the recursive grammar; INTERVENE changes the live state", fontsize=12.0),
        box("programmer", "bpatcher", [20.0, 95.0, 865.0, 675.0], name=PROGRAMMER_OUTPUT.name, numinlets=0, numoutlets=0),
        box("controls_label", "comment", [910.0, 95.0, 420.0, 20.0], text="RECURSION FIELD", fontsize=14.0),
        box("temp_label", "comment", [910.0, 125.0, 110.0, 20.0], text="temperature 0–2"),
        box("temp", "flonum", [1030.0, 124.0, 70.0, 22.0], valueof=0.65, minimum=0.0, maximum=2.0),
        box("temp_pack", "newobj", [1110.0, 124.0, 205.0, 22.0], text="o.pack /qmw/recursive/temperature"),
        box("seed_label", "comment", [910.0, 157.0, 110.0, 20.0], text="random seed"),
        box("seed", "number", [1030.0, 156.0, 70.0, 22.0], valueof=23, minimum=0),
        box("seed_pack", "newobj", [1110.0, 156.0, 175.0, 22.0], text="o.pack /qmw/recursive/seed"),
        box("depth_label", "comment", [910.0, 189.0, 110.0, 20.0], text="max depth 1–256"),
        box("depth", "number", [1030.0, 188.0, 70.0, 22.0], valueof=32, minimum=1, maximum=256),
        box("depth_pack", "newobj", [1110.0, 188.0, 190.0, 22.0], text="o.pack /qmw/recursive/max_depth"),
        box("interval_label", "comment", [910.0, 221.0, 110.0, 20.0], text="interval ms"),
        box("interval", "number", [1030.0, 220.0, 70.0, 22.0], valueof=240, minimum=30),
        box("interval_pack", "newobj", [1110.0, 220.0, 195.0, 22.0], text="o.pack /qmw/recursive/interval_ms"),
        box("control_udp", "newobj", [1320.0, 172.0, 150.0, 22.0], text="udpsend 127.0.0.1 7403"),
        box("receive_label", "comment", [910.0, 268.0, 470.0, 20.0], text="HEXANY STATE · six vertices of the 2)4 1-3-5-7 CPS", fontsize=14.0),
        box("receive", "newobj", [910.0, 298.0, 105.0, 22.0], text="udpreceive 7410"),
        box("route_qmw", "newobj", [1030.0, 298.0, 115.0, 22.0], text="OSC-route /qmw"),
        box("route_domain", "newobj", [1160.0, 298.0, 175.0, 22.0], text="OSC-route /recursive /circuit"),
        box("route_recursive", "newobj", [910.0, 332.0, 440.0, 22.0], text="OSC-route /wilson_note /status /error /running /seed_accepted"),
        box("note_unpack", "newobj", [910.0, 372.0, 510.0, 22.0], text="unpack i i i i i i f f f i i i i i"),
        box("status", "message", [910.0, 410.0, 510.0, 22.0], text="generation · shell probability · entropy · temperature · depth · seed · revision · gates"),
        box("error", "message", [910.0, 442.0, 510.0, 22.0], text="no recursive errors"),
        box("running", "toggle", [1360.0, 332.0, 24.0, 24.0]),
        box("running_label", "comment", [1390.0, 334.0, 70.0, 20.0], text="running"),
        box("midi_label", "comment", [910.0, 490.0, 490.0, 20.0], text="MPE OUTPUT · channels 2–7; phase is timbral CC74", fontsize=14.0),
        box("makenote", "newobj", [910.0, 530.0, 150.0, 22.0], text="makenote 64 120 2"),
        box("noteout", "newobj", [910.0, 570.0, 80.0, 22.0], text="noteout 1"),
        box("xbendout", "newobj", [1080.0, 530.0, 75.0, 22.0], text="xbendout"),
        box("midiout", "newobj", [1080.0, 570.0, 80.0, 22.0], text="midiout"),
        box("ctlout", "newobj", [1190.0, 530.0, 85.0, 22.0], text="ctlout 74"),
        box("midi_note", "comment", [910.0, 615.0, 510.0, 56.0], text="Pitch = exact Wilson product ratio via MIDI note + 14-bit bend.\nVelocity = √(conditional probability). CC74 = relative quantum phase.\nThe exchange recursion preserves the weight-two Hexany shell."),
        box("print", "newobj", [910.0, 700.0, 165.0, 22.0], text="print QMW_RECURSIVE_WILSON"),
        box("default_temp", "newobj", [20.0, 790.0, 95.0, 22.0], text="loadmess 0.65", hidden=1),
        box("default_seed", "newobj", [125.0, 790.0, 90.0, 22.0], text="loadmess 23", hidden=1),
        box("default_depth", "newobj", [225.0, 790.0, 90.0, 22.0], text="loadmess 32", hidden=1),
        box("default_interval", "newobj", [325.0, 790.0, 100.0, 22.0], text="loadmess 240", hidden=1),
    ])
    for source, pack in (("temp", "temp_pack"), ("seed", "seed_pack"), ("depth", "depth_pack"), ("interval", "interval_pack")):
        l.extend([line(source, 0, pack), line(pack, 0, "control_udp")])
    l.extend([
        line("default_temp", 0, "temp"), line("default_seed", 0, "seed"),
        line("default_depth", 0, "depth"), line("default_interval", 0, "interval"),
        line("receive", 0, "route_qmw"), line("route_qmw", 0, "route_domain"),
        line("route_domain", 0, "route_recursive"),
        line("route_recursive", 0, "note_unpack"), line("route_recursive", 1, "status"),
        line("route_recursive", 2, "error"), line("route_recursive", 3, "running"),
        line("route_recursive", 0, "print"), line("route_recursive", 1, "print"),
        line("note_unpack", 3, "makenote", 0), line("note_unpack", 4, "makenote", 1),
        line("note_unpack", 5, "makenote", 2), line("note_unpack", 13, "makenote", 3),
        line("makenote", 0, "noteout", 0), line("makenote", 1, "noteout", 1),
        line("note_unpack", 13, "noteout", 2),
        line("note_unpack", 11, "xbendout", 0), line("note_unpack", 13, "xbendout", 1),
        line("xbendout", 0, "midiout"),
        line("note_unpack", 12, "ctlout", 0), line("note_unpack", 13, "ctlout", 2),
    ])
    # The instrument opens in Presentation Mode, so every front-panel object
    # must explicitly opt in and carry a presentation rectangle.  Without
    # this, Max correctly loads the patch but presents an empty surface.
    for entry in b:
        item = entry["box"]
        item["presentation"] = 1
        item["presentation_rect"] = copy.deepcopy(item["patching_rect"])
    patcher["dependency_cache"] = [
        {"name": PROGRAMMER_OUTPUT.name, "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "JSON", "implicit": 1},
        {"name": "OSC-route.mxo", "type": "iLaX"},
        {"name": "o.pack.mxo", "type": "iLaX"},
    ]
    INSTRUMENT_OUTPUT.write_text(json.dumps({"patcher": patcher}, indent=4) + "\n", encoding="utf-8")


def build_refreshed_names():
    """Emit cache-busting names for Max sessions that already loaded v3."""
    source_js = ROOT / "qmw_qac_circuit_programmer_recursive_v3.js"
    base_js = (ROOT / "qmw_qac_circuit_programmer_v1.js").read_text(encoding="utf-8")
    extension_js = source_js.read_text(encoding="utf-8")
    extension_js = extension_js.replace(
        'include("qmw_qac_circuit_programmer_v1.js");',
        '// v1 implementation is flattened above; no asynchronous include',
    )
    REFRESHED_JS.write_text(base_js + "\n\n" + extension_js, encoding="utf-8")

    programmer = json.loads(PROGRAMMER_OUTPUT.read_text(encoding="utf-8"))
    ppatcher = programmer["patcher"]
    for entry in ppatcher["boxes"]:
        item = entry["box"]
        if item.get("id") == "title":
            item["text"] = "QMW CIRCUIT PROGRAMMER · RECURSIVE WILSON v3.3"
        elif item.get("id") == "ui":
            item["filename"] = REFRESHED_JS.name
            item["jsarguments"] = [REFRESHED_JS.name]
    for dependency in ppatcher.get("dependency_cache", []):
        if dependency.get("name") == "qmw_qac_circuit_programmer_recursive_v3.js":
            dependency["name"] = REFRESHED_JS.name
    REFRESHED_PROGRAMMER.write_text(json.dumps(programmer, indent=4) + "\n", encoding="utf-8")

    instrument = json.loads(INSTRUMENT_OUTPUT.read_text(encoding="utf-8"))
    ipatcher = instrument["patcher"]
    for entry in ipatcher["boxes"]:
        item = entry["box"]
        if item.get("id") == "title":
            item["text"] = "QMW · RECURSIVE WILSON HEXANY CIRCUIT INSTRUMENT v3.3"
        elif item.get("id") == "programmer":
            item["name"] = REFRESHED_PROGRAMMER.name
    for dependency in ipatcher.get("dependency_cache", []):
        if dependency.get("name") == PROGRAMMER_OUTPUT.name:
            dependency["name"] = REFRESHED_PROGRAMMER.name
    REFRESHED_INSTRUMENT.write_text(json.dumps(instrument, indent=4) + "\n", encoding="utf-8")


def main():
    build_sender()
    build_programmer()
    build_instrument()
    build_refreshed_names()
    print("Built recursive Wilson v3/v3.3 sender, programmer, and instrument")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
