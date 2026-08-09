#!/usr/bin/env python3
"""Build v5.4 with anchored, slowly deforming harmonic partials."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_3.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5_3.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5_3.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_4.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_4.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_4.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tune_voice(code: str) -> str:
    parameter_anchor = "Param phase_smooth_ms(4000);\nParam magnitude_smooth_ms(2500);"
    parameter_replacement = """Param phase_smooth_ms(4000);
Param magnitude_smooth_ms(2500);
// v5.4: preserve a recognizable harmonic body while quantum gaps deform it.
Param harmonic_smooth_ms(12000);
Param harmonic_deform(0.22);
Param root_anchor(0.14);"""
    if code.count(parameter_anchor) != 1:
        raise RuntimeError("Could not locate v5.3 smoothing parameters")
    code = code.replace(parameter_anchor, parameter_replacement)

    history_anchor = "History sm15(0);"
    histories = "\n".join(
        [history_anchor, ""]
        + [f"History sh{index}({index + 1});" for index in range(16)]
    )
    if code.count(history_anchor) != 1:
        raise RuntimeError("Could not locate v5.3 magnitude histories")
    code = code.replace(history_anchor, histories)

    root_anchor = "tm0 = clamp(m0, 0, 1);"
    if code.count(root_anchor) != 1:
        raise RuntimeError("Could not locate v5.3 root magnitude")
    code = code.replace(
        root_anchor,
        "// The fundamental remains audible even when quantum m0 approaches zero.\n"
        "tm0 = clamp(max(m0, root_anchor), 0, 1);",
    )

    spectral_anchor = "bright = clamp(brightness + ent * 0.18 + (quantum_brightness - 0.5) * 0.55, 0, 1);"
    if code.count(spectral_anchor) != 1:
        raise RuntimeError("Could not locate v5.3 spectral oscillator section")

    lines = [
        "// Persistent partial identities: h0 is always the true fundamental.",
        "// Quantum gap ratios bend integer harmonics by at most one octave before",
        "// depth scaling, then glide in log-frequency space without slot swaps.",
        "harm_ms = max(harmonic_smooth_ms, 10);",
        "harm_step = 1 - exp(-1 / (harm_ms * 0.001 * samplerate));",
        "harm_depth = clamp(harmonic_deform, 0, 1);",
        "th0 = 1;",
    ]
    for index in range(1, 16):
        base = index + 1
        lines.append(
            f"th{index} = {base} * exp(clamp(log(max(h{index}, 0.01) / {base}), -0.69314718, 0.69314718) * harm_depth);"
        )
    for index in range(16):
        lines.append(
            f"sh{index} = exp(log(max(sh{index}, 0.01)) + harm_step * (log(max(th{index}, 0.01)) - log(max(sh{index}, 0.01))));"
        )
    smoothing = "\n".join(lines) + "\n\n"
    code = code.replace(spectral_anchor, smoothing + spectral_anchor)

    # From the oscillator onward, only persistent smoothed ratios may set pitch.
    prefix, suffix = code.split(spectral_anchor, 1)
    suffix = re.sub(r"\bh(1[0-5]|[0-9])\b", r"sh\1", suffix)
    return prefix + spectral_anchor + suffix


def build_rack() -> dict[str, Any]:
    rack = load(RACK_SOURCE)
    codeboxes = [
        entry["box"] for entry in rack["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 4:
        raise RuntimeError("Expected four resonator voices")
    for voice in codeboxes:
        voice["code"] = tune_voice(voice["code"])
    return rack


def main() -> int:
    control = load(CONTROL_SOURCE)
    rack = build_rack()
    surface = load(SURFACE_SOURCE)
    rack_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == RACK_SOURCE.name
    ]
    surface_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == SURFACE_SOURCE.name
    ]
    if len(rack_matches) != 1 or len(surface_matches) != 1:
        raise RuntimeError("Could not locate v5.3 embedded modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])
    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v5.3 · GEOMETRY FEEDBACK":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.4 · ANCHORED HARMONIC DRONE"
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; v5.3 remains unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
