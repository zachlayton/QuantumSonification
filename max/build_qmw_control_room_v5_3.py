#!/usr/bin/env python3
"""Build v5.3 with a geometry-aware feedback/comb performance section."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_2.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5_2.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5_2.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_3.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_3.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_3.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def next_id(patcher: dict[str, Any]) -> str:
    values = [
        int(entry["box"]["id"][4:])
        for entry in patcher.get("boxes", [])
        if entry["box"]["id"].startswith("obj-")
        and entry["box"]["id"][4:].isdigit()
    ]
    return f"obj-{max(values, default=0) + 1}"


def add_box(patcher: dict[str, Any], **box: Any) -> str:
    identifier = next_id(patcher)
    box["id"] = identifier
    patcher.setdefault("boxes", []).append({"box": box})
    return identifier


def connect(patcher: dict[str, Any], source: str, outlet: int, destination: str, inlet: int = 0) -> None:
    patcher.setdefault("lines", []).append(
        {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}
    )


def tune_fdn(code: str) -> str:
    parameter_anchor = "Param decay(0.82);\nParam diffusion(0.78);\nParam absorb(0.32);"
    parameter_replacement = """Param decay(0.82);
Param diffusion(0.78);
Param absorb(0.32);
// v5.3 performance controls. feedback_manual is a stable 0..1 gesture;
// comb_coupling turns small geometries into distinct Karplus delay voices.
Param feedback_manual(0.78);
Param comb_coupling(0.70);
Param comb_damping(0.30);"""
    if code.count(parameter_anchor) != 1:
        raise RuntimeError("Could not locate v5.2 FDN parameters")
    code = code.replace(parameter_anchor, parameter_replacement)

    size_anchor = "s = clamp(size, 0, 1);\nsize_scale = pow(2, (s * 3) - 1.5);"
    size_replacement = """s = clamp(size, 0, 1);
size_scale = pow(2, (s * 3) - 1.5);
small_space = pow(1 - s, 2);
comb_mix = clamp(comb_coupling, 0, 1) * small_space;"""
    if code.count(size_anchor) != 1:
        raise RuntimeError("Could not locate v5.2 size mapping")
    code = code.replace(size_anchor, size_replacement)

    absorb_anchor = """effective_absorb = clamp(
    absorb + surface_depth_z * (0.14 + 0.18 * shape_activity),
    0,
    0.94
);"""
    absorb_replacement = """// In compact spaces, damping becomes the loss term of the Karplus loop.
// Large spaces retain the established surface-absorption behavior.
effective_absorb = clamp(
    mix(absorb, clamp(comb_damping, 0, 1), comb_mix)
        + surface_depth_z * (0.14 + 0.18 * shape_activity),
    0,
    0.94
);"""
    if code.count(absorb_anchor) != 1:
        raise RuntimeError("Could not locate v5.2 absorption equation")
    code = code.replace(absorb_anchor, absorb_replacement)

    diffusion_anchor = "diff_amount = diffusion_z;"
    diffusion_replacement = """// Low diffusion exposes eight pitched comb paths in small-room mode.
diff_amount = diffusion_z * (1 - 0.82 * comb_mix);"""
    if code.count(diffusion_anchor) != 1:
        raise RuntimeError("Could not locate v5.2 diffusion equation")
    code = code.replace(diffusion_anchor, diffusion_replacement)

    feedback_anchor = """feedback = mix(0.48 + 0.49 * effective_decay, 0.999, fr);"""
    feedback_replacement = """room_feedback = 0.48 + 0.49 * effective_decay;
// Manual feedback spans short ambience through long, near-Karplus ringing.
// Compact geometry contributes a small resonance lift, capped below unity.
feedback_trim = 0.25 + 0.90 * clamp(feedback_manual, 0, 1);
feedback_gain = clamp(room_feedback * feedback_trim + 0.055 * comb_mix, 0, 0.995);
feedback_gain = mix(feedback_gain, 0.999, fr);"""
    if code.count(feedback_anchor) != 1:
        raise RuntimeError("Could not locate v5.2 feedback equation")
    code = code.replace(feedback_anchor, feedback_replacement)
    if code.count("feedback * n") != 8:
        raise RuntimeError("Could not locate all eight v5.2 feedback writes")
    return code.replace("feedback * n", "feedback_gain * n")


def add_control(
    patcher: dict[str, Any], gen_id: str, *, label: str, parameter: str,
    default: float, x: float, width: float = 62.0
) -> None:
    add_box(
        patcher, maxclass="comment", text=label,
        patching_rect=[x, 770.0, width + 16.0, 18.0],
        presentation=1, presentation_rect=[x, 18.0, width + 16.0, 18.0],
        textcolor=[0.72, 0.83, 0.96, 1.0], numinlets=1, numoutlets=0,
    )
    number = add_box(
        patcher, maxclass="flonum", format=6,
        patching_rect=[x, 792.0, width, 22.0],
        presentation=1, presentation_rect=[x, 39.0, width, 22.0],
        minimum=0.0, maximum=1.0, parameter_enable=0,
        numinlets=1, numoutlets=2, outlettype=["", "bang"],
    )
    initial = add_box(
        patcher, maxclass="newobj", text=f"loadmess {default}",
        patching_rect=[x, 824.0, 92.0, 22.0], numinlets=1, numoutlets=1,
        outlettype=["float"],
    )
    prepend = add_box(
        patcher, maxclass="newobj", text=f"prepend {parameter}",
        patching_rect=[x, 854.0, 145.0, 22.0], numinlets=1, numoutlets=1,
        outlettype=[""],
    )
    connect(patcher, initial, 0, number)
    connect(patcher, number, 0, prepend)
    connect(patcher, prepend, 0, gen_id)


def build_surface() -> dict[str, Any]:
    surface = load(SURFACE_SOURCE)
    patcher = surface["patcher"]
    codeboxes = [
        entry["box"] for entry in patcher.get("boxes", [])
        if entry["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 1:
        raise RuntimeError("Expected one surface FDN codebox")
    gen = codeboxes[0]
    gen["code"] = tune_fdn(gen["code"])
    for entry in patcher.get("boxes", []):
        box = entry["box"]
        if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v5.2 · LOCAL NOISE":
            box["text"] = "QMW GEOMETRY REVERB v5.3"
            box["presentation_rect"][2] = 440.0
        if box.get("text") == "20 field probes → compact FDN · four independently timed qbit grains":
            box["text"] = "20 probes · geometry FDN · qubit-resonated input"
            box["presentation_rect"][2] = 440.0
    add_control(patcher, gen["id"], label="FEEDBACK", parameter="feedback_manual", default=0.78, x=500.0, width=70.0)
    add_control(patcher, gen["id"], label="DAMPING", parameter="comb_damping", default=0.30, x=585.0, width=70.0)
    add_control(patcher, gen["id"], label="COMB", parameter="comb_coupling", default=0.70, x=670.0, width=70.0)
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
        raise RuntimeError("Could not locate v5.2 embedded modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])
    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v5.2 · LOCAL QUBIT NOISE":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.3 · GEOMETRY FEEDBACK"
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; v5.2 remains unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
