#!/usr/bin/env python3
"""Build a workshop copy combining the QAC designer and wavetable oscillator."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OSCILLATOR = ROOT / "QMW_QAC_Wavetable_Oscillator_v1.maxpat"
SOURCE_UI = ROOT / "qmw_qac_circuit_programmer_v1.js"
WORKSHOP_UI = ROOT / "qmw_qac_wavetable_designer_v1.js"
OUTPUT = ROOT / "QMW_QAC_Wavetable_Circuit_Designer_v1.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def main() -> int:
    # The QAC simulator shot count does not control IBM Runtime, but keeping it
    # at 256 makes the workshop UI and Python bridge tell one consistent story.
    WORKSHOP_UI.write_text(
        SOURCE_UI.read_text(encoding="utf-8").replace(
            'outlet(0, "Simulator", "sim", "qc", 1024);',
            'outlet(0, "Simulator", "sim", "qc", 256);',
        ),
        encoding="utf-8",
    )

    document = json.loads(OSCILLATOR.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    patcher["rect"] = [60.0, 50.0, 1040.0, 940.0]

    remove_ids = {"bell", "getqasm"}
    patcher["boxes"] = [entry for entry in patcher["boxes"] if entry["box"]["id"] not in remove_ids]
    patcher["lines"] = [
        entry for entry in patcher["lines"]
        if entry["patchline"]["source"][0] not in remove_ids
        and entry["patchline"]["destination"][0] not in remove_ids
    ]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["panel"]["patching_rect"] = [10.0, 10.0, 980.0, 875.0]
    boxes["panel"]["presentation_rect"] = [10.0, 10.0, 980.0, 875.0]
    boxes["title"]["text"] = "QAC CIRCUIT DESIGNER → LOCAL / IBM → 256-POINT WAVETABLE"
    boxes["instructions"]["text"] = (
        "Design locally and press SEND QASM. Python bridge mode determines local-only or one confirmed IBM hardware job."
    )

    shift_ids = {
        "udp", "oroute", "rawprint", "print", "loader", "buffer", "display",
        "freq", "freqlabel", "phasor", "wave", "gain", "dac", "statuslabel", "status",
        "corr_unpack", "xx", "yy", "zz", "corr_label",
    }
    for identifier in shift_ids:
        item = boxes[identifier]
        item["patching_rect"][1] += 330.0
        if "presentation_rect" in item:
            item["presentation_rect"][1] += 330.0

    boxes["qac"]["patching_rect"] = [28.0, 835.0, 235.0, 22.0]
    boxes["qac"]["text"] = "och.microqiskit qc 4 4 sim 256 1"
    boxes["sender"]["patching_rect"] = [285.0, 835.0, 180.0, 22.0]
    boxes["sendstatus"]["patching_rect"] = [485.0, 835.0, 360.0, 22.0]
    boxes["sendstatus"]["presentation_rect"] = [500.0, 812.0, 440.0, 24.0]

    # Reuse the original visible buffer for both the ordinary wavetable and
    # the four-row Pauli surface. Keeping one symbol avoids a hidden second
    # buffer disagreeing with 2d.wave~ in the workshop patch.
    boxes["buffer"]["text"] = "buffer~ qmw_wavetable @samps 1024 @channels 1"

    # Replace the one-dimensional Gen reader with a four-row 2d.wave~ surface.
    boxes["oroute"]["text"] += " /qmw/wavetable/pauli15 /qmw/wavetable/surface_file"
    boxes["oroute"]["numoutlets"] = 7
    patcher["boxes"] = [entry for entry in patcher["boxes"] if entry["box"]["id"] != "wave"]
    patcher["lines"] = [
        entry for entry in patcher["lines"]
        if entry["patchline"]["source"][0] != "wave"
        and entry["patchline"]["destination"][0] != "wave"
        and not (
            entry["patchline"]["source"] == ["oroute", 4]
            and entry["patchline"]["destination"][0] == "print"
        )
    ]
    boxes["phasor"]["text"] = "phasor~ 110."

    patcher["boxes"].extend(
        [
            box(
                "designer",
                "jsui",
                [28.0, 100.0, 780.0, 390.0],
                filename="qmw_qac_wavetable_designer_v1.js",
                jsarguments=["qmw_qac_wavetable_designer_v1.js"],
                numinlets=1,
                numoutlets=2,
                outlettype=["", ""],
                presentation=1,
                presentation_rect=[28.0, 100.0, 780.0, 390.0],
            ),
            box(
                "designer_status_label", "comment", [820.0, 110.0, 120.0, 20.0],
                text="DESIGNER STATUS", presentation=1,
                presentation_rect=[820.0, 110.0, 120.0, 20.0],
                textcolor=[0.34, 0.78, 1.0, 1.0],
            ),
            box(
                "designer_status", "message", [820.0, 138.0, 140.0, 70.0],
                text="ready", presentation=1,
                presentation_rect=[820.0, 138.0, 140.0, 70.0],
            ),
            box(
                "safety", "comment", [820.0, 230.0, 140.0, 180.0],
                text="LOCAL MODE:\nSEND freely.\n\nBOTH MODE:\nEvery SEND QASM creates an IBM job. Submit deliberately, then stop the bridge.",
                presentation=1, presentation_rect=[820.0, 230.0, 140.0, 180.0],
                textcolor=[1.0, 0.68, 0.3, 1.0],
            ),
            box(
                "pauli_label", "comment", [28.0, 505.0, 880.0, 20.0],
                text="PAULI-15 EXPECTATIONS   XI YI ZI | IX IY IZ | XX XY XZ YX YY YZ ZX ZY ZZ",
                presentation=1, presentation_rect=[28.0, 505.0, 880.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
            box(
                "pauli_display", "multislider", [28.0, 530.0, 880.0, 90.0],
                size=15, setminmax=[-1.0, 1.0], style=1,
                presentation=1, presentation_rect=[28.0, 530.0, 880.0, 90.0],
                bgcolor=[0.08, 0.1, 0.14, 1.0],
                slidercolor=[0.95, 0.55, 0.25, 1.0],
            ),
            box("pauli_slice", "newobj", [600.0, 895.0, 62.0, 22.0], text="zl.slice 1"),
            box("surface_loader", "newobj", [600.0, 865.0, 220.0, 22.0], text="js qmw_pauli_surface_receiver_v1.js", numinlets=1, numoutlets=2),
            box("morph", "flonum", [220.0, 855.0, 75.0, 22.0], value=1.0, presentation=1, presentation_rect=[220.0, 855.0, 75.0, 22.0]),
            box("morph_label", "comment", [300.0, 855.0, 190.0, 20.0], text="spectral view: 0=direct  .33=shifted  .67=stretched  1=reversed", presentation=1, presentation_rect=[300.0, 855.0, 390.0, 20.0], textcolor=[0.51,0.81,1.0,1.0]),
            box("morph_sig", "newobj", [220.0, 885.0, 75.0, 22.0], text="pack 0. 30"),
            box("morph_line", "newobj", [300.0, 885.0, 42.0, 22.0], text="line~"),
            box("morph_clip", "newobj", [347.0, 885.0, 75.0, 22.0], text="clip~ 0. 1."),
            box("two_d", "newobj", [280.0, 885.0, 185.0, 22.0], text="2d.wave~ qmw_wavetable", numinlets=4, numoutlets=1, outlettype=["signal"]),
            box("rows", "message", [480.0, 885.0, 65.0, 22.0], text="rows 4"),
            box("rows_load", "newobj", [550.0, 885.0, 60.0, 22.0], text="loadbang"),
            box("surface_replace", "newobj", [830.0, 865.0, 105.0, 22.0], text="prepend replace"),
            box("surface_slice", "newobj", [830.0, 835.0, 62.0, 22.0], text="zl.slice 1"),
        ]
    )
    patcher["lines"].extend(
        [
            line("designer", 0, "qac"),
            line("designer", 1, "designer_status"),
            line("oroute", 4, "surface_loader"),
            line("oroute", 4, "pauli_slice"),
            line("pauli_slice", 1, "pauli_display"),
            line("oroute", 5, "surface_slice"),
            line("surface_slice", 1, "surface_replace"),
            line("oroute", 6, "print"),
            line("surface_loader", 0, "status"),
            line("surface_loader", 1, "buffer"),
            line("surface_loader", 1, "rows"),
            line("surface_replace", 0, "buffer"),
            line("freq", 0, "phasor"),
            line("phasor", 0, "two_d", 0),
            line("morph", 0, "morph_sig"),
            line("morph_sig", 0, "morph_line"),
            line("morph_line", 0, "morph_clip"),
            line("morph_clip", 0, "two_d", 1),
            line("rows_load", 0, "rows"),
            line("rows", 0, "two_d"),
            line("two_d", 0, "gain"),
        ]
    )
    patcher["dependency_cache"].append(
        {
            "name": "qmw_qac_wavetable_designer_v1.js",
            "bootpath": str(ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    patcher["dependency_cache"].append(
        {"name": "qmw_pauli_surface_receiver_v1.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1}
    )
    OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
