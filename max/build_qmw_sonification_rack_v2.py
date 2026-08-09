#!/usr/bin/env python3
"""Fork the stable sonification rack with four post-resonator qubit buses."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


MAX_ROOT = Path(__file__).resolve().parent
MODULE_ROOT = MAX_ROOT / "control_room_modules"
SOURCE_CONTROL_ROOM = MAX_ROOT / "QMW_Control_Room_v1.maxpat"
SOURCE_MODULE = MODULE_ROOT / "QMW_Sonification_Rack_Module_v1.maxpat"
OUTPUT = MODULE_ROOT / "QMW_Sonification_Rack_Module_v2.maxpat"


def load_preserved_v1_rack() -> dict[str, Any]:
    """Prefer the arranged v2 rack, then recover the preserved v1 layout."""
    if OUTPUT.is_file():
        current = json.loads(OUTPUT.read_text(encoding="utf-8"))
        current_patcher = current.get("patcher", {})
        presentation_count = sum(
            entry["box"].get("presentation") == 1
            for entry in current_patcher.get("boxes", [])
        )
        if current_patcher.get("openinpresentation") == 1 and presentation_count >= 25:
            return current
    if SOURCE_CONTROL_ROOM.is_file():
        control = json.loads(SOURCE_CONTROL_ROOM.read_text(encoding="utf-8"))
        candidates = [
            entry["box"]
            for entry in control["patcher"].get("boxes", [])
            if entry["box"].get("maxclass") == "bpatcher"
            and entry["box"].get("name") == SOURCE_MODULE.name
            and "patcher" in entry["box"]
        ]
        if len(candidates) == 1:
            embedded = deepcopy(candidates[0]["patcher"])
            if embedded.get("openinpresentation") == 1:
                return {"patcher": embedded}
    return json.loads(SOURCE_MODULE.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    payload = load_preserved_v1_rack()
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    by_id = {box["id"]: box for box in boxes}
    lines = patcher.setdefault("lines", [])

    router_box = next(
        box for box in boxes
        if str(box.get("text", "")).startswith(
            ("js qmw_density_field_to_resonator_local.js", "js qmw_density_field_to_resonator.js")
        )
    )
    router = router_box["id"]
    router_box["text"] = "js qmw_density_field_to_resonator_local.js"
    router_box.setdefault("saved_object_attributes", {})["filename"] = (
        "qmw_density_field_to_resonator_local.js"
    )
    voice_gains: dict[int, str] = {}
    for entry in lines:
        line = entry["patchline"]
        if line["source"][0] != router:
            continue
        voice = int(line["source"][1])
        gen_id = line["destination"][0]
        gain_lines = [
            candidate["patchline"] for candidate in lines
            if candidate["patchline"]["source"] == [gen_id, 0]
            and by_id[candidate["patchline"]["destination"][0]].get("text") == "*~ 1."
        ]
        if len(gain_lines) != 1:
            raise RuntimeError(f"Could not find post-resonator gain for q{voice}")
        voice_gains[voice] = gain_lines[0]["destination"][0]
    if set(voice_gains) != {0, 1, 2, 3}:
        raise RuntimeError(f"Expected q0..q3 voice gains; found {sorted(voice_gains)}")

    numeric_ids = [
        int(box["id"][4:]) for box in boxes
        if box["id"].startswith("obj-") and box["id"][4:].isdigit()
    ]
    next_id = max(numeric_ids, default=0) + 1
    for voice in range(4):
        existing = [
            box for box in boxes
            if box.get("text") == f"send~ qmw_qubit_{voice}"
        ]
        if len(existing) > 1:
            raise RuntimeError(f"Duplicate q{voice} audio buses in v2 rack")
        if existing:
            send_id = existing[0]["id"]
            if not any(
                line["patchline"]["source"] == [voice_gains[voice], 0]
                and line["patchline"]["destination"] == [send_id, 0]
                for line in lines
            ):
                lines.append(
                    {
                        "patchline": {
                            "source": [voice_gains[voice], 0],
                            "destination": [send_id, 0],
                        }
                    }
                )
            continue
        identifier = f"obj-{next_id}"
        next_id += 1
        send = {
            "id": identifier,
            "maxclass": "newobj",
            "text": f"send~ qmw_qubit_{voice}",
            "patching_rect": [900.0, 390.0 + voice * 32.0, 142.0, 22.0],
            "numinlets": 1,
            "numoutlets": 0,
        }
        patcher["boxes"].append({"box": send})
        lines.append(
            {
                "patchline": {
                    "source": [voice_gains[voice], 0],
                    "destination": [identifier, 0],
                }
            }
        )

    # Seed the four Gen resonators after the embedded rack loads. This avoids
    # an entirely silent DSP graph while the first OSC density frame is in
    # flight, and the visible message provides a deterministic diagnostic if
    # live routing is ever in doubt.
    seed_texts = {box.get("text", "") for box in boxes}
    required_seed_texts = {"test", "loadbang", "delay 250", "RESEED RESONATORS"}
    if not required_seed_texts.issubset(seed_texts):
        test_message_id = f"obj-{next_id}"
        next_id += 1
        loadbang_id = f"obj-{next_id}"
        next_id += 1
        delay_id = f"obj-{next_id}"
        next_id += 1
        comment_id = f"obj-{next_id}"
        next_id += 1
        for box in (
        {
            "id": test_message_id,
            "maxclass": "message",
            "text": "test",
            "patching_rect": [8.0, 10.0, 42.0, 22.0],
            "numinlets": 2,
            "numoutlets": 1,
            "outlettype": [""],
        },
        {
            "id": comment_id,
            "maxclass": "comment",
            "text": "RESEED RESONATORS",
            "patching_rect": [55.0, 11.0, 145.0, 20.0],
        },
        {
            "id": loadbang_id,
            "maxclass": "newobj",
            "text": "loadbang",
            "patching_rect": [1090.0, 390.0, 62.0, 22.0],
            "numinlets": 1,
            "numoutlets": 1,
            "outlettype": ["bang"],
        },
        {
            "id": delay_id,
            "maxclass": "newobj",
            "text": "delay 250",
            "patching_rect": [1160.0, 390.0, 70.0, 22.0],
            "numinlets": 2,
            "numoutlets": 1,
            "outlettype": ["bang"],
        },
        ):
            patcher["boxes"].append({"box": box})
        lines.extend(
            [
                {"patchline": {"source": [loadbang_id, 0], "destination": [delay_id, 0]}},
                {"patchline": {"source": [delay_id, 0], "destination": [test_message_id, 0]}},
                {"patchline": {"source": [test_message_id, 0], "destination": [router, 0]}},
            ]
        )

    title = next(
        (
            box for box in boxes
            if "SONIFICATION" in str(box.get("text", "")).upper()
            and box.get("maxclass") == "comment"
        ),
        None,
    )
    if title is not None:
        title["text"] = str(title.get("text", "")).replace("v1", "v2")
    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies[:] = [
        dependency for dependency in dependencies
        if dependency.get("name") not in {
            "qmw_density_field_to_resonator.js",
            "qmw_density_field_to_resonator_local.js",
        }
    ]
    dependencies.append(
        {
            "name": "qmw_density_field_to_resonator_local.js",
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    return payload


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    texts = [box.get("text", "") for box in boxes]
    for voice in range(4):
        if texts.count(f"send~ qmw_qubit_{voice}") != 1:
            raise RuntimeError(f"Missing unique q{voice} audio bus")
    for text in ("test", "loadbang", "delay 250", "RESEED RESONATORS"):
        if texts.count(text) != 1:
            raise RuntimeError(f"Missing resonator seed/diagnostic object {text!r}")
    presentation_boxes = [box for box in boxes if box.get("presentation") == 1]
    if patcher.get("openinpresentation") != 1 or len(presentation_boxes) < 25:
        raise RuntimeError("The preserved sonification presentation layout is missing")


def main() -> int:
    payload = build()
    validate(payload)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}; v1 rack was not modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
