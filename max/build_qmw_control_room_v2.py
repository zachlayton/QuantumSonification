#!/usr/bin/env python3
"""Fork the working Control Room v1 into a non-destructive v2 instrument."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MAX_ROOT = Path(__file__).resolve().parent
MODULE_ROOT = MAX_ROOT / "control_room_modules"
SOURCE = MAX_ROOT / "QMW_Control_Room_v1.maxpat"
SURFACE_V2 = MODULE_ROOT / "QMW_Realtime_Surface_Reverb_v2.maxpat"
SONIFICATION_V2 = MODULE_ROOT / "QMW_Sonification_Rack_Module_v2.maxpat"
OUTPUT = MAX_ROOT / "QMW_Control_Room_v2.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_control_room() -> dict[str, Any]:
    if not SOURCE.is_file():
        raise RuntimeError(f"Stable Control Room v1 is missing: {SOURCE}")
    if not SURFACE_V2.is_file():
        raise RuntimeError(
            "Build QMW_Realtime_Surface_Reverb_v2.maxpat before the Control Room"
        )
    if not SONIFICATION_V2.is_file():
        raise RuntimeError(
            "Build QMW_Sonification_Rack_Module_v2.maxpat before the Control Room"
        )

    payload = load(SOURCE)
    surface = load(SURFACE_V2)
    sonification = load(SONIFICATION_V2)
    patcher = payload["patcher"]
    patcher["rect"] = [34.0, 80.0, 1920.0, 1220.0]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]

    title = next(box for box in boxes if box.get("text") == "QMW CONTROL ROOM v1")
    title["text"] = "QMW CONTROL ROOM v2"
    subtitle = next(
        box for box in boxes
        if str(box.get("text", "")).startswith("One OSC hub")
    )
    subtitle["text"] = (
        "One OSC hub · quantum telemetry · sonification · quantum rhythm matrix"
    )
    heading = next(
        (
            box for box in boxes
            if box.get("text") == "REALTIME IMPLICIT SURFACE REVERB"
        ),
        None,
    )
    if heading is not None:
        heading["text"] = "REALTIME SURFACE REVERB + QUANTUM RHYTHM MATRIX"

    surface_boxes = [
        box for box in boxes
        if box.get("maxclass") == "bpatcher"
        and box.get("name") == "QMW_Realtime_Surface_Reverb_v1.maxpat"
    ]
    if len(surface_boxes) != 1:
        raise RuntimeError(
            f"Expected one v1 surface bpatcher; found {len(surface_boxes)}"
        )
    surface_box = surface_boxes[0]
    surface_box["name"] = SURFACE_V2.name
    surface_box["embed"] = 1
    surface_box["patcher"] = surface["patcher"]
    surface_box["patching_rect"][3] = 730.0
    presentation_rect = surface_box.setdefault(
        "presentation_rect", list(surface_box["patching_rect"])
    )
    presentation_rect[2] = max(float(presentation_rect[2]), 780.0)
    presentation_rect[3] = 735.0
    surface_box["enablevscroll"] = 1

    sonification_boxes = [
        box for box in boxes
        if box.get("maxclass") == "bpatcher"
        and box.get("name") == "QMW_Sonification_Rack_Module_v1.maxpat"
    ]
    if len(sonification_boxes) != 1:
        raise RuntimeError(
            f"Expected one v1 sonification bpatcher; found {len(sonification_boxes)}"
        )
    sonification_box = sonification_boxes[0]
    sonification_box["name"] = SONIFICATION_V2.name
    sonification_box["embed"] = 1
    sonification_box["patcher"] = sonification["patcher"]

    if heading is None:
        numeric_ids = [
            int(box["id"][4:])
            for box in boxes
            if box["id"].startswith("obj-") and box["id"][4:].isdigit()
        ]
        heading = {
            "id": f"obj-{max(numeric_ids, default=0) + 1}",
            "maxclass": "comment",
            "text": "REALTIME SURFACE REVERB + QUANTUM RHYTHM MATRIX",
            "fontsize": 16.0,
            "fontface": 1,
            "patching_rect": [1205.0, 420.0, 550.0, 24.0],
            "presentation": 1,
            "presentation_rect": [
                float(presentation_rect[0]),
                max(395.0, float(presentation_rect[1]) - 25.0),
                550.0,
                24.0,
            ],
        }
        patcher["boxes"].append({"box": heading})

    footer = next(
        box for box in boxes
        if str(box.get("text", "")).startswith(
            "Start quantumsonification_conductor.py normally"
        )
    )
    footer["text"] = (
        "v2 preserves Control Room v1. Grain envelopes run in Max; Python supplies "
        "quantum telemetry and optional /qmw/event/resonance triggers."
    )
    footer["patching_rect"][1] = 1190.0
    if "presentation_rect" in footer:
        footer["presentation_rect"][1] = 1190.0

    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies[:] = [
        dependency for dependency in dependencies
        if dependency.get("name") not in {
            "QMW_Realtime_Surface_Reverb_v1.maxpat",
            "QMW_Sonification_Rack_Module_v1.maxpat",
        }
    ]
    dependencies.append(
        {
            "name": SURFACE_V2.name,
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        }
    )
    dependencies.append(
        {
            "name": SONIFICATION_V2.name,
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        }
    )
    return payload


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    texts = [box.get("text", "") for box in boxes]
    if "QMW CONTROL ROOM v2" not in texts:
        raise RuntimeError("Control Room v2 title is missing")
    surfaces = [
        box for box in boxes
        if box.get("maxclass") == "bpatcher"
        and box.get("name") == SURFACE_V2.name
    ]
    if len(surfaces) != 1 or "patcher" not in surfaces[0]:
        raise RuntimeError("The embedded v2 surface module is missing")
    embedded_texts = [
        entry["box"].get("text", "")
        for entry in surfaces[0]["patcher"].get("boxes", [])
    ]
    if "js qmw_resonance_grain_scheduler_v2.js" not in embedded_texts:
        raise RuntimeError("The embedded resonance-grain scheduler is missing")
    sonification = [
        box for box in boxes
        if box.get("maxclass") == "bpatcher"
        and box.get("name") == SONIFICATION_V2.name
    ]
    if len(sonification) != 1 or "patcher" not in sonification[0]:
        raise RuntimeError("The embedded v2 sonification rack is missing")
    embedded_sonification_texts = [
        entry["box"].get("text", "")
        for entry in sonification[0]["patcher"].get("boxes", [])
    ]
    for voice in range(4):
        if embedded_sonification_texts.count(f"send~ qmw_qubit_{voice}") != 1:
            raise RuntimeError(
                f"The embedded v2 rack is missing qbit audio bus {voice}"
            )


def main() -> int:
    payload = build_control_room()
    validate(payload)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}; v1 was not modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
