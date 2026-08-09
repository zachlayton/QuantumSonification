from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def box(identifier, maxclass, rect, **values):
    data = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    data.update(values)
    return {"box": data}


boxes = [
    box("title", "comment", [25, 15, 650, 24], text="QMW Born Transition Catalog — persistent comparison view", fontsize=16),
    box("help", "comment", [25, 43, 760, 34], text="Connect the outlet after OSC-route /born to this inlet. Table values are exact; aligned sliders show normalized log-frequency, probability, and duration."),
    box("in", "inlet", [25, 88, 30, 30], numinlets=0, numoutlets=1, outlettype=[""]),
    box("route", "newobj", [75, 92, 255, 22], text="OSC-route /catalog /active_index /transition", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("catalog_route", "newobj", [75, 126, 190, 22], text="OSC-route /begin /row /end", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("begin", "newobj", [75, 160, 84, 22], text="prepend begin", numinlets=1, numoutlets=1, outlettype=[""]),
    box("row", "newobj", [170, 160, 76, 22], text="prepend row", numinlets=1, numoutlets=1, outlettype=[""]),
    box("end", "newobj", [257, 160, 78, 22], text="prepend end", numinlets=1, numoutlets=1, outlettype=[""]),
    box("active", "newobj", [345, 126, 90, 22], text="prepend active", numinlets=1, numoutlets=1, outlettype=[""]),
    box("js", "newobj", [75, 198, 235, 22], text="js qmw_born_transition_catalog_v1.js", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
    box("status", "message", [325, 198, 460, 22], text="waiting for catalog...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("table", "jit.cellblock", [25, 240, 930, 330], cols=9, rows=15, colhead=0, rowhead=0, numinlets=2, numoutlets=4, outlettype=["", "", "", ""]),
    box("freq_label", "comment", [25, 588, 145, 20], text="log audio frequency"),
    box("freq", "multislider", [175, 584, 780, 42], size=14, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("prob_label", "comment", [25, 640, 145, 20], text="relative probability"),
    box("prob", "multislider", [175, 636, 780, 42], size=14, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("dur_label", "comment", [25, 692, 145, 20], text="relative duration"),
    box("dur", "multislider", [175, 688, 780, 42], size=14, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("menu_label", "comment", [25, 757, 115, 20], text="isotope preset"),
    box("menu", "umenu", [140, 754, 170, 22], items=["H-1", ",", "H-2", ",", "H-3", ",", "He-3+", ",", "He-4+", ",", "Li-6++", ",", "Li-7++"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
    box("prepend_species", "newobj", [330, 754, 240, 22], text="prepend /qmw/excitation/born/species", numinlets=1, numoutlets=1, outlettype=[""]),
    box("send", "newobj", [590, 754, 155, 22], text="udpsend 127.0.0.1 7402", numinlets=1, numoutlets=0),
    box("isotope_note", "comment", [25, 790, 900, 34], text="H-3 is radioactive, but this engine models electronic E1 transitions only—not beta decay. Higher-Z ions are the presets with substantially faster electronic dynamics."),
]


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


lines = [
    line("in", 0, "route"),
    line("route", 0, "catalog_route"),
    line("catalog_route", 0, "begin"),
    line("catalog_route", 1, "row"),
    line("catalog_route", 2, "end"),
    line("route", 1, "active"),
    line("begin", 0, "js"),
    line("row", 0, "js"),
    line("end", 0, "js"),
    line("active", 0, "js"),
    line("js", 0, "table"),
    line("js", 1, "freq"),
    line("js", 2, "prob"),
    line("js", 3, "dur"),
    line("js", 4, "status", 1),
    line("menu", 1, "prepend_species"),
    line("prepend_species", 0, "send"),
]

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [120, 80, 1000, 850],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_born_transition_catalog_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }
}

(ROOT / "QMW_Born_Transition_Catalog_v1.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n",
    encoding="utf-8",
)
