#!/usr/bin/env python3
"""Build the single canonical QMW Spat control-room entry point."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_6.maxpat"
SPAT_SOURCE = ROOT / "control_room_modules" / "QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat"
OUTPUT = ROOT / "QMW_SPAT_MASTER_CONTROL_ROOM.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def next_id(patcher: dict[str, Any]) -> str:
    values = [
        int(entry["box"]["id"][4:])
        for entry in patcher.get("boxes", [])
        if entry["box"].get("id", "").startswith("obj-")
        and entry["box"]["id"][4:].isdigit()
    ]
    return f"obj-{max(values, default=0) + 1}"


def add_box(patcher: dict[str, Any], **box: Any) -> str:
    identifier = next_id(patcher)
    box["id"] = identifier
    patcher.setdefault("boxes", []).append({"box": box})
    return identifier


def connect(
    patcher: dict[str, Any],
    source: str,
    outlet: int,
    destination: str,
    inlet: int = 0,
) -> None:
    patcher.setdefault("lines", []).append(
        {
            "patchline": {
                "source": [source, outlet],
                "destination": [destination, inlet],
            }
        }
    )


def build() -> dict[str, Any]:
    control = load(CONTROL_SOURCE)
    adapter_payload = load(SPAT_SOURCE)
    patcher = control["patcher"]

    adapters = [
        entry["box"]
        for entry in patcher.get("boxes", [])
        if entry["box"].get("name") == SPAT_SOURCE.name
    ]
    if len(adapters) != 1:
        raise RuntimeError("Expected exactly one v5.6 Spat adapter")
    adapter = adapters[0]
    adapter["patcher"] = deepcopy(adapter_payload["patcher"])
    adapter["patching_rect"] = [30.0, 1210.0, 980.0, 820.0]
    adapter["presentation"] = 1
    adapter["presentation_rect"] = [30.0, 1210.0, 980.0, 820.0]
    adapter["border"] = 1
    adapter.pop("hidden", None)

    # Give this stable entry point a durable title instead of another version number.
    for entry in patcher.get("boxes", []):
        box = entry["box"]
        if box.get("text") == "QMW CONTROL ROOM v5.6 · QUANTUM SIZE":
            box["text"] = "QMW SPAT MASTER CONTROL ROOM"
            box["presentation_rect"][2] = 860.0

    add_box(
        patcher,
        maxclass="comment",
        text="CANONICAL ENTRY POINT · Bloch sphere → spherical harmonics → Spat5 → modal reverb",
        patching_rect=[780.0, 28.0, 920.0, 24.0],
        presentation=1,
        presentation_rect=[780.0, 28.0, 920.0, 24.0],
        fontsize=14.0,
        textcolor=[0.95, 0.76, 0.11, 1.0],
        numinlets=1,
        numoutlets=0,
    )
    add_box(
        patcher,
        maxclass="comment",
        text="SPAT5 BINAURAL MASTER · sources are qmw_qubit_0 … qmw_qubit_3",
        patching_rect=[30.0, 1168.0, 720.0, 24.0],
        presentation=1,
        presentation_rect=[30.0, 1168.0, 720.0, 24.0],
        fontsize=15.0,
        fontface=1,
        textcolor=[0.72, 0.83, 0.96, 1.0],
        numinlets=1,
        numoutlets=0,
    )

    receivers: list[str] = []
    for index in range(4):
        receiver = add_box(
            patcher,
            maxclass="newobj",
            text=f"receive~ qmw_qubit_{index}",
            patching_rect=[1040.0, 1240.0 + index * 40.0, 165.0, 22.0],
            numinlets=0,
            numoutlets=1,
            outlettype=["signal"],
        )
        receivers.append(receiver)
        connect(patcher, receiver, 0, adapter["id"], index)

    trim = add_box(
        patcher,
        maxclass="flonum",
        patching_rect=[1040.0, 1445.0, 70.0, 22.0],
        presentation=1,
        presentation_rect=[1040.0, 1445.0, 70.0, 22.0],
        minimum=0.0,
        maximum=1.0,
        numinlets=1,
        numoutlets=2,
        outlettype=["", "bang"],
        parameter_enable=0,
    )
    trim_init = add_box(
        patcher,
        maxclass="newobj",
        text="loadmess 0.35",
        patching_rect=[1125.0, 1445.0, 100.0, 22.0],
        numinlets=1,
        numoutlets=1,
        outlettype=["float"],
    )
    trim_signal = add_box(
        patcher,
        maxclass="newobj",
        text="sig~ 0.35",
        patching_rect=[1040.0, 1480.0, 75.0, 22.0],
        numinlets=1,
        numoutlets=1,
        outlettype=["signal"],
    )
    connect(patcher, trim_init, 0, trim)
    connect(patcher, trim, 0, trim_signal)

    multipliers: list[str] = []
    meters: list[str] = []
    for channel, x in enumerate((1040.0, 1160.0)):
        multiplier = add_box(
            patcher,
            maxclass="newobj",
            text="*~ 0.35",
            patching_rect=[x, 1530.0, 75.0, 22.0],
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        )
        meter = add_box(
            patcher,
            maxclass="meter~",
            patching_rect=[x, 1570.0, 20.0, 120.0],
            presentation=1,
            presentation_rect=[x, 1570.0, 20.0, 120.0],
            numinlets=1,
            numoutlets=1,
            outlettype=["float"],
        )
        multipliers.append(multiplier)
        meters.append(meter)
        connect(patcher, adapter["id"], channel, multiplier)
        connect(patcher, trim_signal, 0, multiplier, 1)
        connect(patcher, multiplier, 0, meter)

    dac = add_box(
        patcher,
        maxclass="ezdac~",
        patching_rect=[1100.0, 1735.0, 48.0, 48.0],
        presentation=1,
        presentation_rect=[1100.0, 1735.0, 48.0, 48.0],
        numinlets=2,
        numoutlets=0,
    )
    connect(patcher, multipliers[0], 0, dac, 0)
    connect(patcher, multipliers[1], 0, dac, 1)
    add_box(
        patcher,
        maxclass="comment",
        text="OUTPUT TRIM",
        patching_rect=[1040.0, 1420.0, 110.0, 18.0],
        presentation=1,
        presentation_rect=[1040.0, 1420.0, 110.0, 18.0],
        numinlets=1,
        numoutlets=0,
    )
    add_box(
        patcher,
        maxclass="comment",
        text="DSP / BINAURAL OUT",
        patching_rect=[1040.0, 1790.0, 180.0, 18.0],
        presentation=1,
        presentation_rect=[1040.0, 1790.0, 180.0, 18.0],
        numinlets=1,
        numoutlets=0,
    )

    patcher["rect"] = [80.0, 60.0, 1960.0, 1120.0]
    patcher["openinpresentation"] = 1
    patcher["autosave"] = 0
    return control


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    adapters = [
        box for box in boxes.values() if box.get("name") == SPAT_SOURCE.name
    ]
    if len(adapters) != 1 or "patcher" not in adapters[0]:
        raise RuntimeError("Master must contain one embedded Spat adapter")
    adapter = adapters[0]
    if adapter.get("hidden") or not adapter.get("presentation"):
        raise RuntimeError("Master Spat adapter must be visible")
    receivers = {
        box.get("text") for box in boxes.values() if box.get("text", "").startswith("receive~ qmw_qubit_")
    }
    expected = {f"receive~ qmw_qubit_{index}" for index in range(4)}
    if not expected.issubset(receivers):
        raise RuntimeError("Master is missing one or more Spat source buses")
    adapter_lines = [
        line["patchline"]
        for line in patcher["lines"]
        if line["patchline"]["destination"][0] == adapter["id"]
    ]
    if {line["destination"][1] for line in adapter_lines} != {0, 1, 2, 3}:
        raise RuntimeError("Master does not feed all four Spat inputs")
    if not any(box.get("maxclass") == "ezdac~" for box in boxes.values()):
        raise RuntimeError("Master has no binaural hardware output")
    embedded_classes = {
        entry["box"].get("maxclass")
        for entry in adapter["patcher"].get("boxes", [])
    }
    if embedded_classes.intersection({"inlet~", "outlet~"}):
        raise RuntimeError("Embedded adapter contains invalid Max I/O classes")


def main() -> int:
    payload = build()
    validate(payload)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built canonical entry point: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
