#!/usr/bin/env python3
"""Build v5.1 with one timing authority: four reduced-qubit event streams."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_1.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_1.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_1.maxpat"


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


def build_rack() -> dict[str, Any]:
    rack = load(RACK_SOURCE)
    patcher = rack["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    engine = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_four_qubit_event_engine_v1.js"
    )
    event_send = add_box(
        patcher, maxclass="newobj", text="s qmw.qubit.grain.trigger",
        patching_rect=[1430.0, 790.0, 175.0, 22.0],
        numinlets=1, numoutlets=0,
    )
    for voice in range(4):
        route = add_box(
            patcher, maxclass="newobj", text="route quantum_pulse",
            patching_rect=[900.0 + 130.0 * voice, 790.0, 120.0, 22.0],
            numinlets=2, numoutlets=2, outlettype=["", ""],
        )
        select = add_box(
            patcher, maxclass="newobj", text="sel 1",
            patching_rect=[900.0 + 130.0 * voice, 820.0, 38.0, 22.0],
            numinlets=1, numoutlets=2, outlettype=["bang", ""],
        )
        message = add_box(
            patcher, maxclass="message", text=f"trigger 1. 900 {voice}",
            patching_rect=[945.0 + 130.0 * voice, 820.0, 120.0, 22.0],
            numinlets=2, numoutlets=1, outlettype=[""],
        )
        connect(patcher, engine, voice, route)
        connect(patcher, route, 0, select)
        connect(patcher, select, 0, message)
        connect(patcher, message, 0, event_send)
    return rack


def build_surface() -> dict[str, Any]:
    surface = load(SURFACE_SOURCE)
    patcher = surface["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    by_id = {box["id"]: box for box in boxes}
    scheduler = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_resonance_grain_scheduler_v3.js"
    )
    metro = next(box["id"] for box in boxes if box.get("text") == "metro 50")
    rate_prepends = {
        box["id"] for box in boxes
        if str(box.get("text", "")).startswith("prepend local_rate")
    }
    patcher["lines"] = [
        line for line in patcher.get("lines", [])
        if not (
            line["patchline"]["destination"] == [scheduler, 0]
            and (
                line["patchline"]["source"][0] == metro
                or line["patchline"]["source"][0] in rate_prepends
            )
        )
    ]

    # Remove the obsolete rate controls from presentation without deleting
    # their saved data, making rollback and comparison straightforward.
    legacy_labels = {"Q0 Hz", "Q1 Hz", "Q2 Hz", "Q3 Hz"}
    hidden_ids: set[str] = set()
    for box in boxes:
        if box.get("text") in legacy_labels:
            box["presentation"] = 0
            hidden_ids.add(box["id"])
    for label_id in hidden_ids:
        label = by_id[label_id]
        rect = label.get("presentation_rect", [])
        if len(rect) < 2:
            continue
        for box in boxes:
            candidate = box.get("presentation_rect", [])
            if (
                box.get("maxclass") == "flonum" and len(candidate) >= 2
                and abs(candidate[0] - rect[0]) < 2
                and 15 <= candidate[1] - rect[1] <= 30
            ):
                box["presentation"] = 0

    trigger_receive = add_box(
        patcher, maxclass="newobj", text="r qmw.qubit.grain.trigger",
        patching_rect=[1780.0, 305.0, 180.0, 22.0],
        numinlets=0, numoutlets=1, outlettype=[""],
    )
    connect(patcher, trigger_receive, 0, scheduler)

    for box in boxes:
        if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v5 · FOUR-QUBIT FIELD":
            box["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v5.1 · QUBIT EVENTS"
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
        raise RuntimeError("Could not locate v5 modules")
    rack_matches[0]["name"] = RACK_OUTPUT.name
    rack_matches[0]["patcher"] = deepcopy(rack["patcher"])
    surface_matches[0]["name"] = SURFACE_OUTPUT.name
    surface_matches[0]["patcher"] = deepcopy(surface["patcher"])
    for entry in control["patcher"].get("boxes", []):
        if entry["box"].get("text") == "QMW CONTROL ROOM v5 · FOUR-QUBIT POLYPHONY":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.1 · QUBIT TIMING AUTHORITY"

    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    print(f"Built {CONTROL_OUTPUT.name}; earlier versions remain unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
