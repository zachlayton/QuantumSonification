#!/usr/bin/env python3
"""Build v4: quantum modal noise -> resonator output -> geometry reverb."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v3_Drone.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v3_Drone.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v4.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v4.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v4.maxpat"


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


def connect(patcher: dict[str, Any], source: str, destination: str, inlet: int = 0) -> None:
    patcher.setdefault("lines", []).append(
        {"patchline": {"source": [source, 0], "destination": [destination, inlet]}}
    )


def modal_declarations() -> str:
    lines = [
        "Param noise_resonator_mix(0.45);",
        "Param noise_amount(0.28);",
        "Param noise_floor(0);",
        "Param noise_color(0.72);",
        "Param noise_decay_ms(45);",
        "Param noise_spectral_amount(0.75);",
        "Param noise_spectral_gain(2.5);",
        "Param noise_spectral_base_hz(55);",
        "Param noise_spectral_q(7);",
        "History modal_noise_lp(0);",
    ]
    for index in range(16):
        lines.append(f"History nb{index}(0); History nl{index}(0);")
    return "\n".join(lines)


def modal_processing() -> str:
    lines = [
        "raw_modal_noise = noise();",
        "noise_color_coeff = exp(-1 / (max(noise_decay_ms, 0.1) * 0.001 * samplerate));",
        "modal_noise_lp = raw_modal_noise + noise_color_coeff * (modal_noise_lp - raw_modal_noise);",
        "colored_modal_noise = mix(modal_noise_lp, raw_modal_noise, clamp(noise_color, 0, 1));",
        "noise_level = clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1);",
        "noise_input = colored_modal_noise * noise_level;",
        "modal_q_eff = clamp(noise_spectral_q * 4 * mix(0.72, 1.45, pur), 2, 120);",
    ]
    for index in range(16):
        lines.extend(
            [
                f"nf{index} = clamp(freq * max(h{index}, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);",
                f"ng{index} = tan(3.141592653589793 * nf{index} / samplerate);",
                f"na{index} = 1 / (1 + ng{index} * (ng{index} + 1 / modal_q_eff));",
                f"nv{index} = na{index} * (nb{index} + ng{index} * (noise_input - nl{index}));",
                f"nlv{index} = nl{index} + ng{index} * nv{index};",
                f"nb{index} = 2 * nv{index} - nb{index};",
                f"nl{index} = 2 * nlv{index} - nl{index};",
            ]
        )
    modal_sum = " +\n    ".join(f"e{i} * nv{i}" for i in range(16))
    lines.extend(
        [
            "modal_noise = (\n    " + modal_sum + "\n) / sqrt(16);",
            "modal_noise = tanh(modal_noise * clamp(noise_spectral_gain, 0, 8));",
            "modal_noise = mix(colored_modal_noise * noise_level, modal_noise, clamp(noise_spectral_amount, 0, 1));",
        ]
    )
    return "\n".join(lines)


def tune_rack(rack: dict[str, Any]) -> None:
    patcher = rack["patcher"]
    codeboxes = [
        entry["box"]
        for entry in patcher.get("boxes", [])
        if entry["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 4:
        raise RuntimeError(f"Expected four resonators; found {len(codeboxes)}")
    for box in codeboxes:
        code = box["code"]
        marker = "Param output_ceiling(0.85);"
        if code.count(marker) != 1:
            raise RuntimeError("Cannot locate v4 modal parameter insertion point")
        code = code.replace(marker, marker + "\n" + modal_declarations())
        signal_marker = "voice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = partials;"
        if code.count(signal_marker) != 1:
            raise RuntimeError("Cannot locate v4 signal blend insertion point")
        code = code.replace(
            signal_marker,
            modal_processing()
            + "\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\n"
            + "sig = mix(partials, modal_noise, clamp(noise_resonator_mix, 0, 1));",
        )
        box["code"] = code

    blend = add_box(
        patcher,
        maxclass="flonum",
        patching_rect=[900.0, 525.0, 60.0, 22.0],
        presentation=1,
        presentation_rect=[310.0, 148.0, 60.0, 22.0],
        format=6,
        parameter_enable=0,
        minimum=0.0,
        maximum=1.0,
        numinlets=1,
        numoutlets=2,
        outlettype=["", "bang"],
    )
    label = add_box(
        patcher,
        maxclass="comment",
        text="NOISE→RESONATOR",
        patching_rect=[900.0, 500.0, 150.0, 20.0],
        presentation=1,
        presentation_rect=[300.0, 125.0, 150.0, 20.0],
        numinlets=1,
        numoutlets=0,
    )
    del label
    initial = add_box(
        patcher,
        maxclass="newobj",
        text="loadmess 0.45",
        patching_rect=[970.0, 525.0, 94.0, 22.0],
        numinlets=1,
        numoutlets=1,
        outlettype=["float"],
    )
    prepend = add_box(
        patcher,
        maxclass="newobj",
        text="prepend noise_resonator_mix",
        patching_rect=[1075.0, 525.0, 180.0, 22.0],
        numinlets=1,
        numoutlets=1,
        outlettype=[""],
    )
    connect(patcher, initial, blend)
    connect(patcher, blend, prepend)
    for box in codeboxes:
        connect(patcher, prepend, box["id"])

    noise_receive = add_box(
        patcher,
        maxclass="newobj",
        text="r qmw.resonator.noise",
        patching_rect=[900.0, 565.0, 145.0, 22.0],
        numinlets=0,
        numoutlets=1,
        outlettype=[""],
    )
    noise_route = add_box(
        patcher,
        maxclass="newobj",
        text=(
            "route noise_amount noise_floor noise_color noise_decay_ms "
            "noise_spectral_amount noise_spectral_gain "
            "noise_spectral_base_hz noise_spectral_q"
        ),
        patching_rect=[1055.0, 565.0, 670.0, 22.0],
        numinlets=1,
        numoutlets=9,
        outlettype=["", "", "", "", "", "", "", "", ""],
    )
    connect(patcher, noise_receive, noise_route)
    parameter_names = (
        "noise_amount", "noise_floor", "noise_color", "noise_decay_ms",
        "noise_spectral_amount", "noise_spectral_gain",
        "noise_spectral_base_hz", "noise_spectral_q",
    )
    for outlet, name in enumerate(parameter_names):
        parameter_prepend = add_box(
            patcher,
            maxclass="newobj",
            text=f"prepend {name}",
            patching_rect=[1055.0 + outlet * 82.0, 600.0, 80.0, 22.0],
            numinlets=1,
            numoutlets=1,
            outlettype=[""],
        )
        patcher.setdefault("lines", []).append(
            {
                "patchline": {
                    "source": [noise_route, outlet],
                    "destination": [parameter_prepend, 0],
                }
            }
        )
        for codebox in codeboxes:
            connect(patcher, parameter_prepend, codebox["id"])


def make_surface_v4(surface_patcher: dict[str, Any]) -> dict[str, Any]:
    surface = {"patcher": deepcopy(surface_patcher)}
    codeboxes = [
        entry["box"]
        for entry in surface["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 1:
        raise RuntimeError("Expected one geometry FDN")
    code = codeboxes[0]["code"]
    original = "excite = (input_signal + internal_noise) * (1 - fr) * 0.42;"
    replacement = "// v4: noise is resonated upstream; the FDN receives only the serial input.\nexcite = input_signal * (1 - fr) * 0.42;"
    if code.count(original) != 1:
        raise RuntimeError("Cannot locate parallel FDN noise mix")
    codeboxes[0]["code"] = code.replace(original, replacement)
    noise_send = add_box(
        surface["patcher"],
        maxclass="newobj",
        text="s qmw.resonator.noise",
        patching_rect=[2660.0, 1375.0, 155.0, 22.0],
        numinlets=1,
        numoutlets=0,
    )
    noise_prepend_ids = [
        entry["box"]["id"]
        for entry in surface["patcher"].get("boxes", [])
        if str(entry["box"].get("text", "")).startswith("prepend noise_")
    ]
    if len(noise_prepend_ids) < 8:
        raise RuntimeError(
            f"Expected the complete noise control panel; found {len(noise_prepend_ids)} controls"
        )
    for identifier in noise_prepend_ids:
        connect(surface["patcher"], identifier, noise_send)
    for entry in surface["patcher"].get("boxes", []):
        box = entry["box"]
        if box.get("text") == "loadmess 0.008":
            box["text"] = "loadmess 0"
        if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v3":
            box["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v4 · SERIAL EXCITATION"
    return surface


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    rack = load(RACK_SOURCE)
    control = load(CONTROL_SOURCE)
    tune_rack(rack)

    rack_boxes = [
        entry["box"]
        for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "bpatcher"
        and entry["box"].get("name") == RACK_SOURCE.name
    ]
    if len(rack_boxes) != 1:
        raise RuntimeError("Expected one v3 Drone rack")
    rack_boxes[0]["name"] = RACK_OUTPUT.name
    rack_boxes[0]["patcher"] = deepcopy(rack["patcher"])

    surface_boxes = [
        entry["box"]
        for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("maxclass") == "bpatcher"
        and entry["box"].get("name") == "QMW_Realtime_Surface_Reverb_v3.maxpat"
    ]
    if len(surface_boxes) != 1:
        raise RuntimeError("Expected one v3 surface reverb")
    surface = make_surface_v4(surface_boxes[0]["patcher"])
    surface_boxes[0]["name"] = SURFACE_OUTPUT.name
    surface_boxes[0]["patcher"] = deepcopy(surface["patcher"])

    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v3 · DRONE A/B":
            entry["box"]["text"] = "QMW CONTROL ROOM v4 · SERIAL QUANTUM NOISE"
    return control, rack, surface


def main() -> int:
    control, rack, surface = build()
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; v3 and v3 Drone remain unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
