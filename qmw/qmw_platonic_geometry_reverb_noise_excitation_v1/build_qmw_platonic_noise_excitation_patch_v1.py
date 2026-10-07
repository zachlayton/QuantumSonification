#!/usr/bin/env python3
"""Fork the Platonic Max test patch with embedded noise-excitation DSP."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
SOURCE_PATCH = WORKSPACE / "reverb" / "platonic" / "platonic_test1.maxpat"
GENEXPR = HERE / "qmw_platonic_geometry_reverb_v1.genexpr"
OUTPUT_PATCH = HERE / "QMW_Platonic_Noise_Excitation_v1.maxpat"

CONTROL_MESSAGES = (
    ("noise_amount 0.22", 310.0),
    ("noise_decay_ms 22", 338.0),
    ("onset_threshold 0.012", 366.0),
    ("onset_sensitivity 10", 394.0),
    ("noise_color 0.72", 422.0),
    ("noise_floor 0", 450.0),
)


def message_box(identifier: str, text: str, y: float) -> dict[str, object]:
    return {
        "box": {
            "id": identifier,
            "maxclass": "message",
            "numinlets": 2,
            "numoutlets": 1,
            "outlettype": [""],
            "patching_rect": [21.0, y, 122.0, 22.0],
            "text": text,
        }
    }


def build_patch() -> dict[str, object]:
    payload = json.loads(SOURCE_PATCH.read_text(encoding="utf-8"))
    patcher = payload["patcher"]
    boxes = patcher["boxes"]
    codeboxes = [
        item["box"]
        for item in boxes
        if item["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 1:
        raise RuntimeError(f"Expected one Gen codebox, found {len(codeboxes)}")
    codeboxes[0]["code"] = GENEXPR.read_text(encoding="utf-8")

    controllers = [
        item["box"]
        for item in boxes
        if item["box"].get("text")
        == "js qmw_platonic_geometry_controller_v1.js"
    ]
    if len(controllers) != 1:
        raise RuntimeError(
            f"Expected one Platonic controller, found {len(controllers)}"
        )
    controller_id = controllers[0]["id"]

    boxes.append(
        {
            "box": {
                "id": "obj-noise-title",
                "maxclass": "comment",
                "numinlets": 1,
                "numoutlets": 0,
                "patching_rect": [21.0, 282.0, 145.0, 20.0],
                "text": "NOISE EXCITATION",
            }
        }
    )
    for index, (text, y) in enumerate(CONTROL_MESSAGES, start=1):
        identifier = f"obj-noise-{index}"
        boxes.append(message_box(identifier, text, y))
        patcher["lines"].append(
            {
                "patchline": {
                    "source": [identifier, 0],
                    "destination": [controller_id, 0],
                }
            }
        )
    return payload


def validate(payload: dict[str, object]) -> None:
    patcher = payload["patcher"]
    boxes = [item["box"] for item in patcher["boxes"]]
    code = next(box["code"] for box in boxes if box.get("id") == "obj-1")
    if code != GENEXPR.read_text(encoding="utf-8"):
        raise RuntimeError("Embedded GenExpr differs from the forked source")
    messages = {
        box.get("text") for box in boxes if box.get("id", "").startswith("obj-noise-")
    }
    expected = {text for text, _ in CONTROL_MESSAGES}
    if not expected.issubset(messages):
        raise RuntimeError("Noise control messages are incomplete")
    if code.count("Delay dl") != 20 or code.count(".write(") != 20:
        raise RuntimeError("Embedded GenExpr failed delay-network checks")


def main() -> int:
    payload = build_patch()
    validate(payload)
    OUTPUT_PATCH.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated noise-excitation Max patch: {OUTPUT_PATCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
