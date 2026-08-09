#!/usr/bin/env python3
"""Build v5: four local reduced-state performers with correlation coupling."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v4.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v4.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v4.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5.maxpat"
EVENT_JS = "qmw_four_qubit_event_engine_v1.js"


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


def voice_codeboxes(patcher: dict[str, Any]) -> list[dict[str, Any]]:
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    router = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_density_field_to_resonator_local.js"
    )
    by_id = {box["id"]: box for box in boxes}
    voices: list[dict[str, Any] | None] = [None, None, None, None]
    for line in patcher.get("lines", []):
        edge = line["patchline"]
        if edge["source"][0] == router and 0 <= edge["source"][1] < 4:
            candidate = by_id.get(edge["destination"][0])
            if candidate and candidate.get("maxclass") == "gen.codebox~":
                voices[edge["source"][1]] = candidate
    if any(box is None for box in voices):
        raise RuntimeError("Could not resolve all four ordered resonator voices")
    return [box for box in voices if box is not None]


def tune_gen(code: str) -> str:
    parameter_marker = "Param noise_spectral_q(7);"
    additions = """
Param quantum_pulse(0);
Param quantum_noise_variation(0.25);
Param quantum_brightness(0.5);
Param quantum_event_decay_ms(1200);
History quantum_pulse_z(0);
History quantum_event_env(0);
""".strip()
    if code.count(parameter_marker) != 1:
        raise RuntimeError("Missing v4 quantum parameter insertion point")
    code = code.replace(parameter_marker, parameter_marker + "\n" + additions)

    noise_marker = "noise_level = clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1);"
    event_code = """
quantum_trigger = (quantum_pulse > 0.5) * (quantum_pulse_z <= 0.5);
quantum_pulse_z = quantum_pulse;
quantum_decay_coeff = exp(-1 / (max(quantum_event_decay_ms, 1) * 0.001 * samplerate));
quantum_event_env = quantum_trigger + (1 - quantum_trigger) * quantum_event_env * quantum_decay_coeff;
noise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))
    * clamp(quantum_noise_variation, 0, 1)
    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));
""".strip()
    if code.count(noise_marker) != 1:
        raise RuntimeError("Missing v4 noise-level insertion point")
    code = code.replace(noise_marker, event_code)

    brightness_marker = "bright = clamp(brightness + ent * 0.25, 0, 1);"
    brightness_code = (
        "bright = clamp(brightness + ent * 0.18 "
        "+ (quantum_brightness - 0.5) * 0.55, 0, 1);"
    )
    if code.count(brightness_marker) != 1:
        raise RuntimeError("Missing v4 brightness insertion point")
    return code.replace(brightness_marker, brightness_code)


def build_rack() -> dict[str, Any]:
    rack = load(RACK_SOURCE)
    patcher = rack["patcher"]
    voices = voice_codeboxes(patcher)
    for voice in voices:
        voice["code"] = tune_gen(voice["code"])

    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    density_router = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_density_field_to_resonator_local.js"
    )
    speed_prepend = next(box["id"] for box in boxes if box.get("text") == "prepend speed")
    phase_prepend = next(box["id"] for box in boxes if box.get("text") == "prepend phase")
    patcher["lines"] = [
        line for line in patcher.get("lines", [])
        if not (
            line["patchline"]["destination"] == [density_router, 2]
            and line["patchline"]["source"][0] == speed_prepend
        )
        and not (
            line["patchline"]["destination"] == [density_router, 1]
            and line["patchline"]["source"][0] == phase_prepend
        )
    ]

    spin_router = next(
        box["id"] for box in boxes if box.get("text") == "OSC-route /q0 /q1 /q2 /q3"
    )
    engine = add_box(
        patcher,
        maxclass="newobj", text=f"js {EVENT_JS}",
        patching_rect=[900.0, 650.0, 225.0, 22.0],
        numinlets=6, numoutlets=4, outlettype=["", "", "", ""],
        saved_object_attributes={"filename": EVENT_JS, "parameter_enable": 0},
    )
    for voice in range(4):
        connect(patcher, spin_router, voice, engine, voice)
        connect(patcher, engine, voice, voices[voice]["id"])

    clock_toggle = add_box(
        patcher, maxclass="toggle", patching_rect=[900.0, 685.0, 24.0, 24.0],
        numinlets=1, numoutlets=1, outlettype=["int"], parameter_enable=0,
    )
    clock_load = add_box(
        patcher, maxclass="newobj", text="loadmess 1",
        patching_rect=[930.0, 685.0, 72.0, 22.0],
        numinlets=1, numoutlets=1, outlettype=["int"],
    )
    clock = add_box(
        patcher, maxclass="newobj", text="qmetro 25",
        patching_rect=[1010.0, 685.0, 72.0, 22.0],
        numinlets=2, numoutlets=1, outlettype=["bang"],
    )
    connect(patcher, clock_load, 0, clock_toggle)
    connect(patcher, clock_toggle, 0, clock)
    connect(patcher, clock, 0, engine, 4)

    correlation_receive = add_box(
        patcher, maxclass="newobj", text="r qmw.pauli.correlations",
        patching_rect=[1090.0, 685.0, 165.0, 22.0],
        numinlets=0, numoutlets=1, outlettype=[""],
    )
    connect(patcher, correlation_receive, 0, engine, 5)

    for voice in range(4):
        route = add_box(
            patcher, maxclass="newobj", text="route quantum_pulse",
            patching_rect=[900.0 + voice * 125.0, 725.0, 120.0, 22.0],
            numinlets=2, numoutlets=2, outlettype=["", ""],
        )
        select = add_box(
            patcher, maxclass="newobj", text="sel 1",
            patching_rect=[900.0 + voice * 125.0, 752.0, 38.0, 22.0],
            numinlets=1, numoutlets=2, outlettype=["bang", ""],
        )
        indicator = add_box(
            patcher, maxclass="button",
            patching_rect=[945.0 + voice * 125.0, 752.0, 24.0, 24.0],
            presentation=1,
            presentation_rect=[35.0 + voice * 66.0, 88.0, 20.0, 20.0],
            numinlets=1, numoutlets=1, outlettype=["bang"],
        )
        connect(patcher, engine, voice, route)
        connect(patcher, route, 0, select)
        connect(patcher, select, 0, indicator)

    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies[:] = [entry for entry in dependencies if entry.get("name") != EVENT_JS]
    dependencies.append(
        {
            "name": EVENT_JS, "bootpath": str(ROOT),
            "patcherrelativepath": ".", "type": "TEXT", "implicit": 1,
        }
    )
    return rack


def main() -> int:
    control = load(CONTROL_SOURCE)
    rack = build_rack()
    surface = load(SURFACE_SOURCE)
    for entry in surface["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v4 · SERIAL EXCITATION":
            entry["box"]["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v5 · FOUR-QUBIT FIELD"

    rack_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == RACK_SOURCE.name
    ]
    surface_matches = [
        entry["box"] for entry in control["patcher"].get("boxes", [])
        if entry["box"].get("name") == SURFACE_SOURCE.name
    ]
    if len(rack_matches) != 1 or len(surface_matches) != 1:
        raise RuntimeError("Could not locate v4 embedded modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])

    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v4 · SERIAL QUANTUM NOISE":
            entry["box"]["text"] = "QMW CONTROL ROOM v5 · FOUR-QUBIT POLYPHONY"

    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; v3/v4 remain unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
