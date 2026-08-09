#!/usr/bin/env python3
"""Build QMW_Full4Q_Tomography_81_v1.maxpat."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Full4Q_Tomography_81_v1.maxpat"


def box(
    box_id: str,
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    **attributes: object,
) -> dict:
    value: dict[str, object] = {
        "id": box_id,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        value["text"] = text
    value.update(attributes)
    return {"box": value}


def line(source: str, outlet: int, destination: str, inlet: int) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


boxes = [
    box(
        "title",
        "comment",
        [28.0, 18.0, 920.0, 34.0],
        text="QMW · FULL FOUR-QUBIT TOMOGRAPHY · LOCAL ↔ IBM INSTRUMENT v2",
        fontsize=20.0,
        textcolor=[0.12, 0.82, 0.92, 1.0],
    ),
    box(
        "subtitle",
        "comment",
        [30.0, 54.0, 1180.0, 38.0],
        text=(
            "3⁴ X/Y/Z measurement settings × 2⁴ basis bins × 256 shots = "
            "20,736 events per source. Preserve LOCAL and IBM simultaneously, "
            "then crossfade the complete score."
        ),
        fontsize=13.0,
    ),
    box(
        "launch",
        "comment",
        [30.0, 94.0, 1280.0, 24.0],
        text=(
            "Start Python from workshop_lightweight:  "
            "/Users/zlayton/miniconda3/envs/music/bin/python "
            "qmw_full4q_tomography_osc_v1.py --save-dir "
            "/Users/zlayton/QuantumSonification/full4q_tomography_v1/runs"
        ),
        fontsize=11.0,
        textcolor=[0.7, 0.72, 0.76, 1.0],
    ),
    box("ghz", "message", [30.0, 132.0, 130.0, 24.0], text="ghz none 256 23"),
    box("ghzqft", "message", [170.0, 132.0, 130.0, 24.0], text="ghz qft 256 23"),
    box("bell", "message", [310.0, 132.0, 130.0, 24.0], text="bell none 256 23"),
    box("weave", "message", [450.0, 132.0, 140.0, 24.0], text="weave none 256 23"),
    box(
        "runlabel",
        "comment",
        [30.0, 160.0, 550.0, 22.0],
        text="Edit any message as preset  transform  shots  seed, then click it.",
        fontsize=11.0,
    ),
    box(
        "opack_run",
        "newobj",
        [612.0, 132.0, 194.0, 24.0],
        text="o.pack /qmw/tomography/run",
    ),
    box(
        "udpsend",
        "newobj",
        [822.0, 132.0, 160.0, 24.0],
        text="udpsend 127.0.0.1 7425",
    ),
    box("pingbutton", "button", [1000.0, 132.0, 24.0, 24.0]),
    box(
        "opack_ping",
        "newobj",
        [1034.0, 132.0, 196.0, 24.0],
        text="o.pack /qmw/tomography/ping",
    ),
    box(
        "pinglabel",
        "comment",
        [995.0, 158.0, 240.0, 20.0],
        text="ping Python service",
        fontsize=10.0,
    ),
    box(
        "status",
        "message",
        [30.0, 188.0, 1200.0, 26.0],
        text="Start the Python service, then choose a score above.",
    ),
    box(
        "heatlabel",
        "comment",
        [30.0, 226.0, 560.0, 24.0],
        text="THE 81-SETTING SCORE · each row is one XXXX…ZZZZ setting; 16 basis bins across",
        fontsize=12.0,
        textcolor=[0.9, 0.72, 0.22, 1.0],
    ),
    box(
        "heatmap",
        "jit.pwindow",
        [30.0, 254.0, 560.0, 390.0],
        sync=1,
    ),
    box(
        "selectlabel",
        "comment",
        [625.0, 226.0, 185.0, 24.0],
        text="SETTING POSITION (0–80)",
        fontsize=12.0,
        textcolor=[0.9, 0.72, 0.22, 1.0],
    ),
    box(
        "select",
        "flonum",
        [625.0, 254.0, 72.0, 24.0],
        minimum=0.0,
        maximum=80.0,
        valueof=0.0,
    ),
    box("prepend_select", "newobj", [712.0, 254.0, 96.0, 24.0], text="prepend select"),
    box(
        "mixlabel",
        "comment",
        [820.0, 226.0, 420.0, 24.0],
        text="LOCAL  ←  COMPLETE-DATA CROSSFADE  →  IBM",
        fontsize=12.0,
        textcolor=[0.12, 0.82, 0.92, 1.0],
    ),
    box(
        "mix",
        "flonum",
        [820.0, 254.0, 92.0, 24.0],
        minimum=0.0,
        maximum=1.0,
        valueof=0.0,
    ),
    box(
        "prepend_xfade",
        "newobj",
        [926.0, 254.0, 106.0, 24.0],
        text="prepend xfade",
    ),
    box(
        "mixhelp",
        "comment",
        [1044.0, 254.0, 285.0, 24.0],
        text="0.000 = local     1.000 = IBM",
        fontsize=11.0,
    ),
    box(
        "histlabel",
        "comment",
        [625.0, 292.0, 500.0, 22.0],
        text="Interpolated setting: 16 measured basis-state probabilities",
        fontsize=11.0,
    ),
    box(
        "histogram",
        "multislider",
        [625.0, 318.0, 755.0, 140.0],
        size=16,
        setstyle=1,
        setminmax=[0.0, 1.0],
        slidercolor=[0.12, 0.82, 0.92, 1.0],
        bgcolor=[0.08, 0.09, 0.12, 1.0],
    ),
    box(
        "paulilabel",
        "comment",
        [625.0, 476.0, 740.0, 22.0],
        text="THE 255 NON-IDENTITY PAULI COEFFICIENTS · IIXY…ZZZZ",
        fontsize=11.0,
        textcolor=[0.9, 0.72, 0.22, 1.0],
    ),
    box(
        "paulis",
        "multislider",
        [625.0, 502.0, 755.0, 142.0],
        size=255,
        setstyle=1,
        setminmax=[-1.0, 1.0],
        slidercolor=[0.78, 0.32, 0.88, 1.0],
        bgcolor=[0.08, 0.09, 0.12, 1.0],
    ),
    box(
        "shelllabel",
        "comment",
        [625.0, 662.0, 680.0, 22.0],
        text="CORRELATION-WEIGHT SHELLS · weights 0–4 contain 1, 12, 54, 108, 81 terms",
        fontsize=11.0,
        textcolor=[0.9, 0.72, 0.22, 1.0],
    ),
    box(
        "shells",
        "multislider",
        [625.0, 688.0, 500.0, 96.0],
        size=5,
        setstyle=1,
        setminmax=[0.0, 1.0],
        slidercolor=[0.96, 0.56, 0.18, 1.0],
        bgcolor=[0.08, 0.09, 0.12, 1.0],
    ),
    box(
        "audiolabel",
        "comment",
        [30.0, 664.0, 520.0, 22.0],
        text="SONIFY THE CONTINUOUS ROW MORPH · 16 probabilities become harmonic amplitudes",
        fontsize=11.0,
        textcolor=[0.9, 0.72, 0.22, 1.0],
    ),
    box(
        "buffer",
        "newobj",
        [30.0, 694.0, 248.0, 24.0],
        text="buffer~ qmw_full4q_setting @samps 256",
    ),
    box("frequency", "flonum", [30.0, 736.0, 76.0, 24.0], valueof=110.0),
    box("phasor", "newobj", [122.0, 736.0, 72.0, 24.0], text="phasor~ 110."),
    box(
        "wave",
        "newobj",
        [212.0, 736.0, 184.0, 24.0],
        text="wave~ qmw_full4q_setting",
    ),
    box("gain", "newobj", [412.0, 736.0, 58.0, 24.0], text="*~ 0.12"),
    box("dac", "newobj", [490.0, 728.0, 52.0, 36.0], text="ezdac~"),
    box(
        "warning",
        "comment",
        [30.0, 782.0, 520.0, 22.0],
        text=(
            "SOURCE MEMORY · reload the latest saved datasets without rerunning either source."
        ),
        fontsize=11.0,
    ),
    box(
        "replay_local",
        "message",
        [30.0, 810.0, 118.0, 24.0],
        text="local",
    ),
    box(
        "replay_ibm",
        "message",
        [160.0, 810.0, 118.0, 24.0],
        text="ibm",
    ),
    box(
        "opack_replay",
        "newobj",
        [290.0, 810.0, 220.0, 24.0],
        text="o.pack /qmw/tomography/replay",
    ),
    box(
        "replay_help",
        "comment",
        [520.0, 810.0, 390.0, 24.0],
        text="LOAD LAST LOCAL / LOAD LAST IBM",
        fontsize=11.0,
    ),
    box("load_frequency", "newobj", [30.0, 842.0, 86.0, 24.0], text="loadmess 110."),
    box("load_select", "newobj", [130.0, 842.0, 78.0, 24.0], text="loadmess 0."),
    box("load_mix", "newobj", [220.0, 842.0, 78.0, 24.0], text="loadmess 0."),
    box(
        "receiver",
        "newobj",
        [1160.0, 688.0, 214.0, 24.0],
        text="js qmw_full4q_tomography_receiver_v1.js",
    ),
    box(
        "udpreceive",
        "newobj",
        [30.0, 900.0, 140.0, 24.0],
        text="udpreceive 7426",
        hidden=1,
    ),
    box(
        "route",
        "newobj",
        [184.0, 900.0, 1080.0, 24.0],
        text=(
            "o.route /qmw/tomography/begin /qmw/tomography/setting "
            "/qmw/tomography/pauli /qmw/tomography/shell "
            "/qmw/tomography/metrics /qmw/tomography/end "
            "/qmw/tomography/status /qmw/tomography/error "
            "/qmw/tomography/xfade /qmw/tomography/select"
        ),
        hidden=1,
    ),
]

prepend_names = (
    "begin",
    "setting",
    "pauli",
    "shell",
    "metrics",
    "end",
    "status",
    "error",
)
for index, name in enumerate(prepend_names):
    boxes.append(
        box(
            f"prepend_{name}",
            "newobj",
            [184.0 + 110.0 * index, 938.0, 100.0, 24.0],
            text=f"prepend {name}",
            hidden=1,
        )
    )

lines = [
    line("ghz", 0, "opack_run", 0),
    line("ghzqft", 0, "opack_run", 0),
    line("bell", 0, "opack_run", 0),
    line("weave", 0, "opack_run", 0),
    line("opack_run", 0, "udpsend", 0),
    line("pingbutton", 0, "opack_ping", 0),
    line("opack_ping", 0, "udpsend", 0),
    line("select", 0, "prepend_select", 0),
    line("prepend_select", 0, "receiver", 0),
    line("mix", 0, "prepend_xfade", 0),
    line("prepend_xfade", 0, "receiver", 0),
    line("replay_local", 0, "opack_replay", 0),
    line("replay_ibm", 0, "opack_replay", 0),
    line("opack_replay", 0, "udpsend", 0),
    line("receiver", 0, "heatmap", 0),
    line("receiver", 1, "histogram", 0),
    line("receiver", 2, "paulis", 0),
    line("receiver", 3, "shells", 0),
    line("receiver", 4, "status", 0),
    line("frequency", 0, "phasor", 0),
    line("phasor", 0, "wave", 0),
    line("wave", 0, "gain", 0),
    line("gain", 0, "dac", 0),
    line("gain", 0, "dac", 1),
    line("load_frequency", 0, "frequency", 0),
    line("load_select", 0, "select", 0),
    line("load_mix", 0, "mix", 0),
    line("udpreceive", 0, "route", 0),
]
for index, name in enumerate(prepend_names):
    lines.append(line("route", index, f"prepend_{name}", 0))
    lines.append(line(f"prepend_{name}", 0, "receiver", 0))
lines.append(line("route", len(prepend_names), "mix", 0))
lines.append(line("route", len(prepend_names) + 1, "select", 0))

patch = {
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 8,
            "architecture": "x64",
            "modernui": 1,
        },
        "classnamespace": "box",
        "rect": [40.0, 50.0, 1440.0, 900.0],
        "bglocked": 0,
        "openinpresentation": 0,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {
                "name": "qmw_full4q_tomography_receiver_v1.js",
                "type": "TEXT",
                "implicit": 1,
            },
            {"name": "o.pack.mxo", "type": "iLaX", "implicit": 1},
            {"name": "o.route.mxo", "type": "iLaX", "implicit": 1},
        ],
        "autosave": 0,
    }
}

OUTPUT.write_text(json.dumps(patch, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT}")
