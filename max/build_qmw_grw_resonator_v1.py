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


boxes = [
    box("title", "comment", [25, 15, 820, 25], text="QMW GRW Resonator v1 — four committed-state branches", fontsize=16),
    box("subtitle", "comment", [25, 44, 1080, 36], text="trace distance → amplitude | coherence loss → bandwidth/grains | qubit → branch | Pauli delta → orientation | rho+ → persistent condition"),
    box("udp", "newobj", [25, 92, 115, 22], text="udpreceive 7400", numinlets=0, numoutlets=1, outlettype=[""]),
    box("route_root", "newobj", [155, 92, 245, 22], text="OSC-route /qmw/grw/sonification", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("route", "newobj", [415, 92, 535, 22], text="OSC-route /event /post/branch_levels /post/population /post/rho_magnitude /pauli", numinlets=1, numoutlets=6, outlettype=["", "", "", "", "", ""]),
    box("pre_event", "newobj", [415, 128, 95, 22], text="prepend event", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pre_levels", "newobj", [520, 128, 145, 22], text="prepend branch_levels", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pre_pop", "newobj", [675, 128, 120, 22], text="prepend population", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pre_rho", "newobj", [805, 128, 145, 22], text="prepend rho_magnitude", numinlets=1, numoutlets=1, outlettype=[""]),
    box("pre_pauli", "newobj", [960, 128, 95, 22], text="prepend pauli", numinlets=1, numoutlets=1, outlettype=[""]),
    box("js", "newobj", [415, 168, 220, 22], text="js qmw_grw_sonification_v1.js", numinlets=1, numoutlets=8, outlettype=["", "", "", "", "", "", "", ""]),
    box("status", "message", [650, 168, 445, 22], text="waiting for a committed GRW event...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("pop_label", "comment", [25, 660, 160, 20], text="rho+ populations"),
    box("population", "multislider", [180, 650, 650, 58], size=16, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("levels_label", "comment", [25, 727, 160, 20], text="rho+ branch levels"),
    box("levels", "multislider", [180, 718, 650, 58], size=4, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("gain", "gain~", [930, 620, 45, 130], numinlets=2, numoutlets=2, outlettype=["signal", "int"]),
    box("dac", "newobj", [920, 780, 65, 22], text="ezdac~", numinlets=2, numoutlets=0),
]

lines = [
    line("udp", 0, "route_root"),
    line("route_root", 0, "route"),
    line("route", 0, "pre_event"),
    line("route", 1, "pre_levels"),
    line("route", 2, "pre_pop"),
    line("route", 3, "pre_rho"),
    line("route", 4, "pre_pauli"),
    line("pre_event", 0, "js"),
    line("pre_levels", 0, "js"),
    line("pre_pop", 0, "js"),
    line("pre_rho", 0, "js"),
    line("pre_pauli", 0, "js"),
    line("js", 4, "levels"),
    line("js", 5, "population"),
    line("js", 7, "status", 1),
    line("gain", 0, "dac", 0),
    line("gain", 0, "dac", 1),
]

base_frequencies = [55.0, 82.5, 110.0, 165.0]
for index, base in enumerate(base_frequencies):
    x = 25 + index * 275
    prefix = f"v{index}"
    boxes.extend([
        box(f"{prefix}_label", "comment", [x, 220, 245, 20], text=f"branch {index}  |  base {base:g} Hz"),
        box(f"{prefix}_unpack", "newobj", [x, 248, 165, 22], text="unpack f f f i f f", numinlets=1, numoutlets=6, outlettype=["float", "float", "float", "int", "float", "float"]),
        box(f"{prefix}_amp_delta", "newobj", [x, 282, 72, 22], text="pak f f", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_amp_expr", "newobj", [x, 314, 145, 22], text="expr $f1*(1.+abs($f2))", numinlets=2, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_trigger", "newobj", [x, 346, 45, 22], text="t b f", numinlets=1, numoutlets=2, outlettype=["bang", "float"]),
        box(f"{prefix}_click", "newobj", [x, 382, 45, 22], text="click~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_amp_sig", "newobj", [x + 58, 382, 45, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_hit_mul", "newobj", [x, 420, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_axis_sign", "newobj", [x + 150, 282, 72, 22], text="pak i f", numinlets=2, numoutlets=1, outlettype=[""]),
        # Pauli axes 1/2/3 map to the exact multipliers 1/1.5/2.  Writing
        # that linear relation directly avoids Max's fragile nested-if parser.
        box(f"{prefix}_freq", "newobj", [x + 150, 314, 245, 22], text=f"expr {base:g} * (0.5 + 0.5 * $i1) * (1. + 0.025 * $f2)", numinlets=2, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_bw_grain", "newobj", [x + 150, 346, 72, 22], text="pak f f", numinlets=2, numoutlets=1, outlettype=[""]),
        box(f"{prefix}_q", "newobj", [x + 150, 378, 185, 22], text="expr 5.+((1.-$f1)*195.)+($f2*20.)", numinlets=2, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_reson", "newobj", [x, 458, 155, 22], text=f"reson~ {base:g} 1. 120.", numinlets=4, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_post_unpack", "newobj", [x, 492, 90, 22], text="unpack f f f f", numinlets=1, numoutlets=4, outlettype=["float"] * 4),
        # The legacy held chord is silent by default. The separate cloud-grain
        # patch now renders the continuing field as 5 ms micro-events.
        box(f"{prefix}_post_scale", "newobj", [x + 98, 492, 48, 22], text="* 0.", numinlets=2, numoutlets=1, outlettype=["float"]),
        box(f"{prefix}_post_sig", "newobj", [x + 154, 492, 45, 22], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_cycle", "newobj", [x, 526, 78, 22], text=f"cycle~ {base:g}", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_post_mul", "newobj", [x + 88, 526, 35, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box(f"{prefix}_sum", "newobj", [x, 562, 35, 22], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
    ])
    lines.extend([
        line("js", index, f"{prefix}_unpack"),
        line(f"{prefix}_unpack", 5, f"{prefix}_amp_delta", 1),
        line(f"{prefix}_unpack", 0, f"{prefix}_amp_delta", 0),
        line(f"{prefix}_amp_delta", 0, f"{prefix}_amp_expr"),
        line(f"{prefix}_amp_expr", 0, f"{prefix}_trigger"),
        line(f"{prefix}_trigger", 0, f"{prefix}_click"),
        line(f"{prefix}_trigger", 1, f"{prefix}_amp_sig"),
        line(f"{prefix}_click", 0, f"{prefix}_hit_mul"),
        line(f"{prefix}_amp_sig", 0, f"{prefix}_hit_mul", 1),
        line(f"{prefix}_unpack", 3, f"{prefix}_axis_sign", 0),
        line(f"{prefix}_unpack", 4, f"{prefix}_axis_sign", 1),
        line(f"{prefix}_axis_sign", 0, f"{prefix}_freq"),
        line(f"{prefix}_freq", 0, f"{prefix}_reson", 1),
        line(f"{prefix}_unpack", 1, f"{prefix}_bw_grain", 0),
        line(f"{prefix}_unpack", 2, f"{prefix}_bw_grain", 1),
        line(f"{prefix}_bw_grain", 0, f"{prefix}_q"),
        line(f"{prefix}_q", 0, f"{prefix}_reson", 3),
        line(f"{prefix}_hit_mul", 0, f"{prefix}_reson", 0),
        line("js", 4, f"{prefix}_post_unpack"),
        line(f"{prefix}_post_unpack", index, f"{prefix}_post_scale"),
        line(f"{prefix}_post_scale", 0, f"{prefix}_post_sig"),
        line(f"{prefix}_cycle", 0, f"{prefix}_post_mul"),
        line(f"{prefix}_post_sig", 0, f"{prefix}_post_mul", 1),
        line(f"{prefix}_reson", 0, f"{prefix}_sum", 0),
        line(f"{prefix}_post_mul", 0, f"{prefix}_sum", 1),
        line(f"{prefix}_sum", 0, "gain", 0),
    ])


patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [60, 50, 1160, 850],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_grw_sonification_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }
}

patch_json = json.dumps(patcher, indent=2) + "\n"
(ROOT / "QMW_GRW_Resonator_v1.maxpat").write_text(patch_json, encoding="utf-8")
# Distinct name forces Max to load the corrected generated patch rather than
# focusing an older in-memory document.
(ROOT / "QMW_GRW_Resonator_v1_1.maxpat").write_text(patch_json, encoding="utf-8")
