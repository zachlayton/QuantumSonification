from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Density_CNMAT_Resonator_v1.maxpat"


def box(identifier, maxclass, rect, **values):
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0):
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


boxes = [
    box("title", "comment", [25, 18, 850, 24], text="QMW Density Matrix → CNMAT Resonant Body v1", fontsize=17),
    box("subtitle", "comment", [25, 48, 930, 38], text="The canonical engine tunes 256 CNMAT resonances on UDP 7400. QTM v1 density-clock pulses on the same QMW bus excite the stored body independently."),
    box("engine_label", "comment", [25, 100, 250, 20], text="MODEL — canonical QMW engine"),
    box("engine_udp", "newobj", [25, 126, 112, 22], text="udpreceive 7400", numinlets=1, numoutlets=1, outlettype=[""]),
    box("engine_qmw", "newobj", [150, 126, 104, 22], text="OSC-route /qmw", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("engine_cnmat", "newobj", [267, 126, 118, 22], text="OSC-route /cnmat", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("engine_density", "newobj", [398, 126, 190, 22], text="OSC-route /density_resonator", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("engine_route", "newobj", [601, 126, 216, 22], text="OSC-route /begin /row /end /trigger", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
    box("prepend_begin", "newobj", [560, 166, 92, 22], text="prepend begin", numinlets=1, numoutlets=1, outlettype=[""]),
    box("prepend_row", "newobj", [662, 166, 82, 22], text="prepend row", numinlets=1, numoutlets=1, outlettype=[""]),
    box("prepend_end", "newobj", [754, 166, 82, 22], text="prepend end", numinlets=1, numoutlets=1, outlettype=[""]),
    box("prepend_trigger", "newobj", [846, 166, 100, 22], text="prepend trigger", numinlets=1, numoutlets=1, outlettype=[""]),
    box("qtm_label", "comment", [25, 214, 300, 20], text="TRIGGER — QTM v1 intrinsic density clock"),
    box("qtm_mechanics", "newobj", [267, 240, 188, 22], text="OSC-route /temporal-mechanics", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("qtm_v1", "newobj", [468, 240, 92, 22], text="OSC-route /v1", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("qtm_clock", "newobj", [573, 240, 146, 22], text="OSC-route /density-clock", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("qtm_pulse", "newobj", [732, 240, 102, 22], text="OSC-route /pulse", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("qtm_note", "comment", [25, 241, 220, 20], text="arrives on the engine's UDP 7400 bus"),
    box("js", "newobj", [350, 320, 260, 22], text="js qmw_cnmat_density_resonator_v1.js", numinlets=2, numoutlets=3, outlettype=["", "", ""]),
    box("status", "message", [350, 356, 460, 22], text="waiting for complete density-resonator frame...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("test_button", "button", [25, 319, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("test_message", "message", [60, 320, 34, 22], text="test", numinlets=2, numoutlets=1, outlettype=[""]),
    box("test_note", "comment", [105, 321, 185, 20], text="local model + impulse test"),
    box("manual_button", "button", [25, 375, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("manual_amp", "message", [60, 376, 38, 22], text="0.7", numinlets=2, numoutlets=1, outlettype=[""]),
    box("manual_note", "comment", [108, 377, 182, 20], text="independent manual impulse"),
    box("click", "newobj", [475, 416, 42, 22], text="click~", numinlets=1, numoutlets=1, outlettype=["signal"]),
    box("resonators", "newobj", [384, 462, 156, 22], text="resonators~ smooth", numinlets=1, numoutlets=2, outlettype=["signal", "list"]),
    box("clear", "message", [565, 430, 40, 22], text="clear", numinlets=2, numoutlets=1, outlettype=[""]),
    box("squelch", "message", [615, 430, 54, 22], text="squelch", numinlets=2, numoutlets=1, outlettype=[""]),
    box("gain", "live.gain~", [409, 516, 96, 125], numinlets=2, numoutlets=5, outlettype=["signal", "signal", "", "float", "list"], parameter_enable=1),
    box("dac", "newobj", [418, 674, 78, 22], text="ezdac~", numinlets=2, numoutlets=0),
    box("architecture", "comment", [25, 735, 930, 45], text="Tuning does not excite the bank. A complete begin/row/end frame replaces the model atomically; engine events, QTM resonance relations, and the manual button are independent impulse sources."),
]

lines = [
    line("engine_udp", 0, "engine_qmw"),
    line("engine_qmw", 0, "engine_cnmat"),
    line("engine_cnmat", 0, "engine_density"),
    line("engine_density", 0, "engine_route"),
    line("engine_route", 0, "prepend_begin"),
    line("engine_route", 1, "prepend_row"),
    line("engine_route", 2, "prepend_end"),
    line("engine_route", 3, "prepend_trigger"),
    line("prepend_begin", 0, "js", 0),
    line("prepend_row", 0, "js", 0),
    line("prepend_end", 0, "js", 0),
    line("prepend_trigger", 0, "js", 0),
    line("engine_qmw", 0, "qtm_mechanics"),
    line("qtm_mechanics", 0, "qtm_v1"),
    line("qtm_v1", 0, "qtm_clock"),
    line("qtm_clock", 0, "qtm_pulse"),
    line("qtm_pulse", 0, "js", 1),
    line("test_button", 0, "test_message"),
    line("test_message", 0, "js", 0),
    line("manual_button", 0, "manual_amp"),
    line("manual_amp", 0, "click"),
    line("js", 0, "resonators"),
    line("js", 1, "click"),
    line("js", 2, "status", 1),
    line("click", 0, "resonators"),
    line("clear", 0, "resonators"),
    line("squelch", 0, "resonators"),
    line("resonators", 0, "gain", 0),
    line("resonators", 0, "gain", 1),
    line("gain", 0, "dac", 0),
    line("gain", 1, "dac", 1),
]

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [120, 80, 1000, 810],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "resonators~.mxo", "type": "iLaX"},
            {"name": "qmw_cnmat_density_resonator_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }
}

OUTPUT.write_text(json.dumps(patcher, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
