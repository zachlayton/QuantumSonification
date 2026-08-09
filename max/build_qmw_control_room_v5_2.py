#!/usr/bin/env python3
"""Build v5.2 with independent per-qubit noise amplitude and monitoring."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_1.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5_1.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5_1.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_2.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_2.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_2.maxpat"


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


def connect(
    patcher: dict[str, Any], source: str, outlet: int,
    destination: str, inlet: int = 0
) -> None:
    patcher.setdefault("lines", []).append(
        {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}
    )


def ordered_voices(patcher: dict[str, Any]) -> list[dict[str, Any]]:
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    by_id = {box["id"]: box for box in boxes}
    router = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_density_field_to_resonator_local.js"
    )
    voices: list[dict[str, Any] | None] = [None, None, None, None]
    for line in patcher.get("lines", []):
        edge = line["patchline"]
        if edge["source"][0] != router or edge["source"][1] not in range(4):
            continue
        candidate = by_id.get(edge["destination"][0])
        if candidate and candidate.get("maxclass") == "gen.codebox~":
            voices[edge["source"][1]] = candidate
    if any(voice is None for voice in voices):
        raise RuntimeError("Could not resolve four ordered voices")
    return [voice for voice in voices if voice is not None]


def tune_code(code: str) -> str:
    old_parameter = "Param noise_amount(0.28);"
    new_parameters = "Param noise_master(0.28);\nParam noise_voice_trim(1);"
    if code.count(old_parameter) != 1:
        raise RuntimeError("Missing v5.1 global noise parameter")
    code = code.replace(old_parameter, new_parameters)
    old_level = """noise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))
    * clamp(quantum_noise_variation, 0, 1)
    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));"""
    new_level = """noise_level = (
    clamp(noise_floor, 0, 0.25)
    + 0.25 * clamp(noise_master, 0, 1) * clamp(noise_voice_trim, 0, 2)
        * clamp(quantum_noise_variation, 0, 1)
) * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));"""
    if code.count(old_level) != 1:
        raise RuntimeError("Missing v5.1 noise equation")
    return code.replace(old_level, new_level)


def build_rack() -> dict[str, Any]:
    rack = load(RACK_SOURCE)
    patcher = rack["patcher"]
    voices = ordered_voices(patcher)
    for voice in voices:
        voice["code"] = tune_code(voice["code"])

    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    engine = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_four_qubit_event_engine_v1.js"
    )
    noise_route = next(
        box["id"] for box in boxes
        if str(box.get("text", "")).startswith("route noise_amount noise_floor")
    )
    by_id = {box["id"]: box for box in boxes}

    # The first outlet formerly prepended `noise_amount` to every voice.
    # Remove only those fan-out paths and replace them with a safety master.
    first_outlet_destinations = {
        line["patchline"]["destination"][0]
        for line in patcher.get("lines", [])
        if line["patchline"]["source"] == [noise_route, 0]
    }
    noise_amount_prepends = {
        identifier for identifier in first_outlet_destinations
        if by_id.get(identifier, {}).get("text") == "prepend noise_amount"
    }
    patcher["lines"] = [
        line for line in patcher.get("lines", [])
        if not (
            line["patchline"]["source"] == [noise_route, 0]
            or line["patchline"]["source"][0] in noise_amount_prepends
        )
    ]
    master_prepend = add_box(
        patcher, maxclass="newobj", text="prepend noise_master",
        patching_rect=[1055.0, 630.0, 142.0, 22.0],
        numinlets=1, numoutlets=1, outlettype=[""],
    )
    connect(patcher, noise_route, 0, master_prepend)
    for voice in voices:
        connect(patcher, master_prepend, 0, voice["id"])

    add_box(
        patcher, maxclass="comment", text="QUBIT NOISE LEVEL",
        patching_rect=[1300.0, 520.0, 150.0, 20.0],
        presentation=1, presentation_rect=[305.0, 64.0, 150.0, 20.0],
        numinlets=1, numoutlets=0,
    )
    add_box(
        patcher, maxclass="comment", text="Q0       Q1       Q2       Q3",
        patching_rect=[1300.0, 545.0, 250.0, 20.0],
        presentation=1, presentation_rect=[305.0, 85.0, 250.0, 20.0],
        numinlets=1, numoutlets=0,
    )
    add_box(
        patcher, maxclass="comment", text="PER-VOICE TRIM",
        patching_rect=[1300.0, 610.0, 150.0, 20.0],
        presentation=1, presentation_rect=[305.0, 164.0, 150.0, 20.0],
        numinlets=1, numoutlets=0,
    )

    for index, voice in enumerate(voices):
        x = 310.0 + 64.0 * index
        monitor_route = add_box(
            patcher, maxclass="newobj", text="route quantum_noise_variation",
            patching_rect=[1300.0 + 130.0 * index, 565.0, 125.0, 22.0],
            numinlets=2, numoutlets=2, outlettype=["", ""],
        )
        monitor = add_box(
            patcher, maxclass="flonum", format=6,
            patching_rect=[1300.0 + 130.0 * index, 590.0, 58.0, 22.0],
            presentation=1, presentation_rect=[x, 105.0, 58.0, 22.0],
            minimum=0.0, maximum=1.0, ignoreclick=1, parameter_enable=0,
            numinlets=1, numoutlets=2, outlettype=["", "bang"],
        )
        connect(patcher, engine, index, monitor_route)
        connect(patcher, monitor_route, 0, monitor)

        trim = add_box(
            patcher, maxclass="flonum", format=6,
            patching_rect=[1300.0 + 130.0 * index, 640.0, 58.0, 22.0],
            presentation=1, presentation_rect=[x, 184.0, 58.0, 22.0],
            minimum=0.0, maximum=2.0, parameter_enable=0,
            numinlets=1, numoutlets=2, outlettype=["", "bang"],
        )
        initial = add_box(
            patcher, maxclass="newobj", text="loadmess 1.",
            patching_rect=[1365.0 + 130.0 * index, 640.0, 76.0, 22.0],
            numinlets=1, numoutlets=1, outlettype=["float"],
        )
        prepend = add_box(
            patcher, maxclass="newobj", text="prepend noise_voice_trim",
            patching_rect=[1300.0 + 130.0 * index, 670.0, 150.0, 22.0],
            numinlets=1, numoutlets=1, outlettype=[""],
        )
        connect(patcher, initial, 0, trim)
        connect(patcher, trim, 0, prepend)
        connect(patcher, prepend, 0, voice["id"])
    return rack


def build_surface() -> dict[str, Any]:
    surface = load(SURFACE_SOURCE)
    for entry in surface["patcher"].get("boxes", []):
        box = entry["box"]
        if box.get("text") == "NOISE AMOUNT":
            box["text"] = "NOISE MASTER"
        if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v5.1 · QUBIT EVENTS":
            box["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v5.2 · LOCAL NOISE"
    return surface


def main() -> int:
    control = load(CONTROL_SOURCE)
    rack = build_rack()
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
        raise RuntimeError("Could not locate v5.1 modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])
    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v5.1 · QUBIT TIMING AUTHORITY":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.2 · LOCAL QUBIT NOISE"

    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; earlier versions remain unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
