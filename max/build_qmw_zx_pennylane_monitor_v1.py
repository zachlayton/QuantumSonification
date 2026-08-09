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


def line(source, outlet, destination, inlet=0):
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


CONTROL_LABELS = [
    "1  ZX phase (turns)",
    "2  <Z0> mapped to 0..1",
    "3  population entropy",
    "4  l1 coherence",
    "5  parameter gradient",
    "6  dominant probability",
]

boxes = [
    box(
        "title",
        "comment",
        [25, 18, 720, 25],
        text="QMW ZX / PennyLane Monitor — the Max side of the shared patch",
        fontsize=16,
    ),
    box(
        "help",
        "comment",
        [25, 50, 790, 38],
        text=(
            "Receives the same six normalized controls sent to VCV Rack. "
            "Python/PennyLane remains the semantic authority; Max is the visible "
            "patching and modulation laboratory."
        ),
    ),
    box(
        "udp_label",
        "comment",
        [25, 105, 160, 20],
        text="OSC input (UDP 7496)",
    ),
    box(
        "udp",
        "newobj",
        [25, 130, 118, 22],
        text="udpreceive 7496",
        numinlets=0,
        numoutlets=1,
    ),
    box(
        "route_fader",
        "newobj",
        [165, 130, 210, 22],
        text="OSC-route /qmw/zx/fader",
        numinlets=1,
        numoutlets=2,
    ),
    box(
        "route_ids",
        "newobj",
        [395, 130, 150, 22],
        text="route 1 2 3 4 5 6",
        numinlets=1,
        numoutlets=7,
    ),
    box(
        "signal_note",
        "comment",
        [25, 176, 780, 34],
        text=(
            "Each number is a control-rate projection of the current quantum "
            "state. Patch these outlets into scale, line~, mc.* or your own "
            "sonification modules."
        ),
    ),
]

lines = [
    line("udp", 0, "route_fader"),
    line("route_fader", 0, "route_ids"),
]

for index, label in enumerate(CONTROL_LABELS, start=1):
    y = 230 + ((index - 1) * 68)
    label_id = f"label_{index}"
    value_id = f"value_{index}"
    slider_id = f"slider_{index}"
    send_id = f"send_{index}"
    boxes.extend(
        [
            box(label_id, "comment", [25, y + 3, 230, 20], text=label),
            box(
                value_id,
                "flonum",
                [265, y, 100, 22],
                minimum=0.0,
                maximum=1.0,
                numinlets=1,
                numoutlets=2,
                outlettype=["", "bang"],
            ),
            box(
                slider_id,
                "slider",
                [385, y, 300, 22],
                floatoutput=1,
                min=0.0,
                size=1.0,
                numinlets=1,
                numoutlets=1,
                outlettype=["float"],
            ),
            box(
                send_id,
                "newobj",
                [705, y, 88, 22],
                text=f"s qmw.zx.{index}",
                numinlets=1,
                numoutlets=0,
            ),
        ]
    )
    lines.extend(
        [
            line("route_ids", index - 1, value_id),
            line(value_id, 0, slider_id),
            line(value_id, 0, send_id),
        ]
    )

boxes.append(
    box(
        "footer",
        "comment",
        [25, 655, 780, 42],
        text=(
            "Named sends: qmw.zx.1 … qmw.zx.6. The next faithful module layer "
            "will carry each logical ZX wire as four real channels "
            "[Re|0>, Im|0>, Re|1>, Im|1>]."
        ),
    )
)

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 5,
            "architecture": "x64",
            "modernui": 1,
        },
        "classnamespace": "box",
        "rect": [120, 80, 840, 730],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

(ROOT / "QMW_ZX_PennyLane_Monitor_v1.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n",
    encoding="utf-8",
)
