#!/usr/bin/env python3
"""Build v5.5 with compensated, supercritical geometry feedback."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_4.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5_4.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5_4.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_5.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_5.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_5.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tune_feedback(code: str) -> str:
    parameter_anchor = "Param feedback_manual(0.78);"
    parameter_replacement = """Param feedback_manual(0.84);
Param feedback_slew_ms(180);"""
    if code.count(parameter_anchor) != 1:
        raise RuntimeError("Could not locate v5.4 feedback parameter")
    code = code.replace(parameter_anchor, parameter_replacement)

    history_anchor = "History diffusion_z(0.78);"
    history_replacement = """History diffusion_z(0.78);
History feedback_z(0.84);"""
    if code.count(history_anchor) != 1:
        raise RuntimeError("Could not locate v5.4 feedback history anchor")
    code = code.replace(history_anchor, history_replacement)

    feedback_anchor = """room_feedback = 0.48 + 0.49 * effective_decay;
// Manual feedback spans short ambience through long, near-Karplus ringing.
// Compact geometry contributes a small resonance lift, capped below unity.
feedback_trim = 0.25 + 0.90 * clamp(feedback_manual, 0, 1);
feedback_gain = clamp(room_feedback * feedback_trim + 0.055 * comb_mix, 0, 0.995);
feedback_gain = mix(feedback_gain, 0.999, fr);"""
    feedback_replacement = """room_feedback = 0.48 + 0.49 * effective_decay;
// v5.5 feedback is calibrated as a performance ratio: 1.0 compensates the
// damping/diffusion loss, below 1 decays, and above 1 slowly blooms.
feedback_seconds = max(feedback_slew_ms, 1) * 0.001;
feedback_coeff = 1 - exp(-1 / max(sr * feedback_seconds, 1));
feedback_z = feedback_z + feedback_coeff * (clamp(feedback_manual, 0, 1.15) - feedback_z);
loss_compensation = 1 + 0.13 * effective_absorb + 0.035 * diff_amount;
decay_bias = 0.22 * (effective_decay - 0.82);
feedback_gain = clamp((feedback_z + decay_bias) * loss_compensation + 0.018 * comb_mix, 0, 1.18);
feedback_gain = mix(feedback_gain, 0.999, fr);"""
    if code.count(feedback_anchor) != 1:
        raise RuntimeError("Could not locate v5.4 feedback mapping")
    return code.replace(feedback_anchor, feedback_replacement)


def build_surface() -> dict[str, Any]:
    surface = load(SURFACE_SOURCE)
    patcher = surface["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    by_id = {box["id"]: box for box in boxes}
    codeboxes = [box for box in boxes if box.get("maxclass") == "gen.codebox~"]
    if len(codeboxes) != 1:
        raise RuntimeError("Expected one geometry FDN")
    codeboxes[0]["code"] = tune_feedback(codeboxes[0]["code"])

    feedback_prepend = next(
        box for box in boxes if box.get("text") == "prepend feedback_manual"
    )
    upstream = [
        line["patchline"]["source"][0]
        for line in patcher.get("lines", [])
        if line["patchline"]["destination"] == [feedback_prepend["id"], 0]
    ]
    if len(upstream) != 1:
        raise RuntimeError("Could not locate visible feedback number")
    feedback_number = by_id[upstream[0]]
    feedback_number["maximum"] = 1.15

    for box in boxes:
        if box.get("text") == "loadmess 0.78":
            box["text"] = "loadmess 0.84"
        if box.get("text") == "FEEDBACK":
            box["text"] = "FB · 1=HOLD"
            if "presentation_rect" in box:
                box["presentation_rect"][2] = 80.0
        if box.get("text") == "QMW GEOMETRY REVERB v5.3":
            box["text"] = "QMW GEOMETRY REVERB v5.5"
    return surface


def main() -> int:
    control = load(CONTROL_SOURCE)
    rack = load(RACK_SOURCE)
    surface = build_surface()
    rack_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == RACK_SOURCE.name
    ]
    surface_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == SURFACE_SOURCE.name
    ]
    if len(rack_matches) != 1 or len(surface_matches) != 1:
        raise RuntimeError("Could not locate v5.4 embedded modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])
    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v5.4 · ANCHORED HARMONIC DRONE":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.5 · REGENERATIVE GEOMETRY"
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; v5.4 remains unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
