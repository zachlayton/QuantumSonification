#!/usr/bin/env python3
"""Add a visible NONE/QFT/IQFT OSC selector to the V4 circuit designer."""

import json
from pathlib import Path


PATH = Path(__file__).resolve().parent / "QMW_QAC_Wavetable_Circuit_Designer_v4_QFT.maxpat"
document = json.loads(PATH.read_text(encoding="utf-8"))
patcher = document["patcher"]
ids = {entry["box"]["id"] for entry in patcher["boxes"]}

if "qft_selector_label" not in ids:
    boxes = [
        {
            "id": "qft_selector_label", "maxclass": "comment",
            "text": "POST-CIRCUIT TRANSFORM",
            "patching_rect": [900.0, 455.0, 190.0, 20.0],
            "presentation": 1,
            "presentation_rect": [900.0, 455.0, 190.0, 20.0],
        },
        {
            "id": "qft_none", "maxclass": "message", "text": "none",
            "patching_rect": [900.0, 480.0, 55.0, 22.0],
            "presentation": 1,
            "presentation_rect": [900.0, 480.0, 55.0, 22.0],
            "numinlets": 2, "numoutlets": 1, "outlettype": [""],
        },
        {
            "id": "qft_qft", "maxclass": "message", "text": "qft",
            "patching_rect": [960.0, 480.0, 55.0, 22.0],
            "presentation": 1,
            "presentation_rect": [960.0, 480.0, 55.0, 22.0],
            "numinlets": 2, "numoutlets": 1, "outlettype": [""],
        },
        {
            "id": "qft_iqft", "maxclass": "message", "text": "iqft",
            "patching_rect": [1020.0, 480.0, 55.0, 22.0],
            "presentation": 1,
            "presentation_rect": [1020.0, 480.0, 55.0, 22.0],
            "numinlets": 2, "numoutlets": 1, "outlettype": [""],
        },
        {
            "id": "qft_pack", "maxclass": "newobj",
            "text": "o.pack /qmw/wavetable/transform",
            "patching_rect": [900.0, 515.0, 220.0, 22.0],
            "numinlets": 1, "numoutlets": 1, "outlettype": ["FullPacket"],
        },
        {
            "id": "qft_udp", "maxclass": "newobj",
            "text": "udpsend 127.0.0.1 7411",
            "patching_rect": [900.0, 550.0, 165.0, 22.0],
            "numinlets": 1, "numoutlets": 0,
        },
        {
            "id": "qft_default", "maxclass": "newobj", "text": "loadmess qft",
            "patching_rect": [1080.0, 480.0, 85.0, 22.0],
            "numinlets": 1, "numoutlets": 1, "outlettype": [""],
        },
        {
            "id": "qft_active", "maxclass": "message", "text": "ACTIVE: QFT",
            "patching_rect": [900.0, 580.0, 180.0, 22.0],
            "presentation": 1,
            "presentation_rect": [900.0, 510.0, 180.0, 22.0],
            "numinlets": 2, "numoutlets": 1, "outlettype": [""],
        },
        {
            "id": "qft_active_prepend", "maxclass": "newobj",
            "text": "prepend set ACTIVE:",
            "patching_rect": [1080.0, 550.0, 135.0, 22.0],
            "numinlets": 1, "numoutlets": 1, "outlettype": [""],
        },
    ]
    patcher["boxes"].extend({"box": box} for box in boxes)
    lines = []
    for source in ("qft_none", "qft_qft", "qft_iqft", "qft_default"):
        lines.extend([
            {"patchline": {"source": [source, 0], "destination": ["qft_pack", 0]}},
            {"patchline": {"source": [source, 0], "destination": ["qft_active_prepend", 0]}},
        ])
    lines.extend([
        {"patchline": {"source": ["qft_pack", 0], "destination": ["qft_udp", 0]}},
        {"patchline": {"source": ["qft_active_prepend", 0], "destination": ["qft_active", 0]}},
    ])
    patcher["lines"].extend(lines)

PATH.write_text(json.dumps(document, indent="\t") + "\n", encoding="utf-8")
print(f"updated {PATH.name}")
