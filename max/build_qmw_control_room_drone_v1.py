#!/usr/bin/env python3
"""Build an A/B drone-continuity variant without modifying stable v3."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v3.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v3.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v3_Drone.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v3_Drone.maxpat"

TUNING = {
    "Param attack_ms(12);": "Param attack_ms(350);",
    "Param slow_decay_ms(900);": "Param slow_decay_ms(3500);",
    "Param fast_decay_ms(70);": "Param fast_decay_ms(900);",
    "Param phase_smooth_ms(100);": "Param phase_smooth_ms(4000);",
    "Param magnitude_smooth_ms(100);": "Param magnitude_smooth_ms(2500);",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tune_rack(rack: dict[str, Any]) -> None:
    codeboxes = [
        entry["box"]
        for entry in rack["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 4:
        raise RuntimeError(f"Expected four resonators; found {len(codeboxes)}")
    for box in codeboxes:
        code = box.get("code", "")
        for original, replacement in TUNING.items():
            if code.count(original) != 1:
                raise RuntimeError(f"Missing unique Gen parameter: {original}")
            code = code.replace(original, replacement)
        box["code"] = code

    for entry in rack["patcher"].get("boxes", []):
        box = entry["box"]
        text = str(box.get("text", ""))
        if "SONIFICATION RACK" in text.upper():
            box["text"] = text + " · DRONE CONTINUITY"
        if text.startswith("amp 0.2\nattack_ms 12"):
            box["text"] = (
                "amp 0.2\nattack_ms 350\nslow_decay_ms 3500\n"
                "fast_decay_ms 900\nmagnitude_smooth_ms 2500\n"
                "phase_smooth_ms 4000\nbrightness 0.65\nmix_voices 4"
            )


def embed_drone_rack(control: dict[str, Any], rack: dict[str, Any]) -> None:
    matches = [
        entry["box"]
        for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "bpatcher"
        and entry["box"].get("name") == RACK_SOURCE.name
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one embedded rack; found {len(matches)}")
    box = matches[0]
    box["name"] = RACK_OUTPUT.name
    box["embed"] = 1
    box["patcher"] = deepcopy(rack["patcher"])

    for entry in control["patcher"].get("boxes", []):
        title = entry["box"]
        if title.get("text") == "QMW CONTROL ROOM v3":
            title["text"] = "QMW CONTROL ROOM v3 · DRONE A/B"


def main() -> int:
    rack = load(RACK_SOURCE)
    control = load(CONTROL_SOURCE)
    tune_rack(rack)
    embed_drone_rack(control, rack)
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name} without modifying stable v3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
