#!/usr/bin/env python3
"""Restore native 2d.wave~ readers and their rows messages in V3/V4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PATCHES = (
    (ROOT / "QMW_QAC_Wavetable_Circuit_Designer_v3.maxpat", "qmw_v3_local", "qmw_v3_ibm"),
    (ROOT / "QMW_QAC_Wavetable_Circuit_Designer_v4_QFT.maxpat", "qmw_v4_local", "qmw_v4_ibm"),
)


for path, local_buffer, ibm_buffer in PATCHES:
    document = json.loads(path.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["two_d"]["text"] = "2d.wave~ qmw_wavetable"
    boxes["v3_local_wave"]["text"] = f"2d.wave~ {local_buffer}"
    boxes["v3_ibm_wave"]["text"] = f"2d.wave~ {ibm_buffer}"
    for box_id in ("two_d", "v3_local_wave", "v3_ibm_wave"):
        boxes[box_id]["numinlets"] = 4

    connections = {
        (tuple(line["patchline"]["source"]), tuple(line["patchline"]["destination"]))
        for line in patcher["lines"]
    }
    for destination in ("two_d", "v3_local_wave", "v3_ibm_wave"):
        edge = (("rows", 0), (destination, 0))
        if edge not in connections:
            patcher["lines"].append({
                "patchline": {
                    "source": ["rows", 0],
                    "destination": [destination, 0],
                }
            })

    path.write_text(json.dumps(document, indent="\t") + "\n", encoding="utf-8")
    print(f"restored native 2d.wave~ in {path.name}")
