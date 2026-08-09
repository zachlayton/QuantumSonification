#!/usr/bin/env python3
"""Add a fixed-gain local-reader monitor path to the V3/V4 QAC patches."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PATCHES = (
    ROOT / "QMW_QAC_Wavetable_Circuit_Designer_v3.maxpat",
    ROOT / "QMW_QAC_Wavetable_Circuit_Designer_v4_QFT.maxpat",
)


for path in PATCHES:
    document = json.loads(path.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    ids = {entry["box"]["id"] for entry in patcher["boxes"]}
    if "local_monitor_gain" not in ids:
        patcher["boxes"].append({
            "box": {
                "id": "local_monitor_gain",
                "maxclass": "newobj",
                "numinlets": 2,
                "numoutlets": 1,
                "outlettype": ["signal"],
                "patching_rect": [20.0, 1185.0, 62.0, 22.0],
                "text": "*~ 0.12",
            }
        })
        for source, destination in (
            (["v3_local_wave", 0], ["local_monitor_gain", 0]),
            (["local_monitor_gain", 0], ["dac", 0]),
            (["local_monitor_gain", 0], ["dac", 1]),
        ):
            patcher["lines"].append({
                "patchline": {"source": source, "destination": destination}
            })
    path.write_text(json.dumps(document, indent="\t") + "\n", encoding="utf-8")
    print(f"updated {path.name}")
