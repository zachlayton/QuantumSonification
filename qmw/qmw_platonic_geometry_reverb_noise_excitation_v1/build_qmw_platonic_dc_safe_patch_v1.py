#!/usr/bin/env python3
"""Build the v5 Max fork with click-resistant, DC-safe spectral noise."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_PATCH = HERE / "QMW_Platonic_Noise_Excitation_v4.maxpat"
GENEXPR = HERE / "qmw_platonic_geometry_reverb_dual_spectral_dc_safe_v1.genexpr"
SOURCE_CONTROLLER = "qmw_platonic_geometry_controller_dual_spectral_v1.js"
CONTROLLER = "qmw_platonic_geometry_controller_dual_spectral_dc_safe_v1.js"
OUTPUT_PATCH = HERE / "QMW_Platonic_Noise_Excitation_v5.maxpat"


def box(identifier: str, maxclass: str, rect: list[float], **fields) -> dict:
    payload = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    payload.update(fields)
    return {"box": payload}


def newobj(identifier: str, text: str, rect: list[float], inlets=1, outlets=1):
    return box(
        identifier,
        "newobj",
        rect,
        numinlets=inlets,
        numoutlets=outlets,
        outlettype=[""] * outlets,
        text=text,
    )


def message(identifier: str, text: str, rect: list[float]):
    return box(
        identifier,
        "message",
        rect,
        numinlets=2,
        numoutlets=1,
        outlettype=[""],
        text=text,
    )


def flonum(identifier: str, rect: list[float]):
    return box(
        identifier,
        "flonum",
        rect,
        numinlets=1,
        numoutlets=2,
        outlettype=["", "bang"],
        parameter_enable=0,
        format=6,
    )


def line(source: str, destination: str, source_outlet=0, destination_inlet=0):
    return {
        "patchline": {
            "source": [source, source_outlet],
            "destination": [destination, destination_inlet],
        }
    }


def build() -> dict:
    payload = json.loads(SOURCE_PATCH.read_text(encoding="utf-8"))
    patcher = payload["patcher"]
    patcher["rect"][3] = max(float(patcher["rect"][3]), 960.0)
    boxes = patcher["boxes"]
    lines = patcher["lines"]

    codeboxes = [
        item["box"] for item in boxes if item["box"].get("maxclass") == "gen.codebox~"
    ]
    if len(codeboxes) != 1:
        raise RuntimeError(f"Expected one Gen codebox, found {len(codeboxes)}")
    codeboxes[0]["code"] = GENEXPR.read_text(encoding="utf-8")

    controllers = [
        item["box"]
        for item in boxes
        if item["box"].get("text") == f"js {SOURCE_CONTROLLER}"
    ]
    if len(controllers) != 1:
        raise RuntimeError(f"Expected one controller, found {len(controllers)}")
    controller_id = controllers[0]["id"]
    controllers[0]["text"] = f"js {CONTROLLER}"

    additions = [
        box(
            "obj-dc-safe-title",
            "comment",
            [800.0, 818.0, 205.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="CLICK / DC SAFETY",
        ),
        flonum("obj-noise-attack", [800.0, 846.0, 57.0, 22.0]),
        box(
            "obj-noise-attack-label",
            "comment",
            [863.0, 848.0, 88.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="attack ms",
        ),
        message(
            "obj-noise-attack-message",
            "noise_attack_ms $1",
            [952.0, 846.0, 134.0, 22.0],
        ),
        newobj("obj-noise-attack-load", "loadmess 3.", [1092.0, 846.0, 75.0, 22.0]),
        flonum("obj-spectral-transition", [800.0, 876.0, 57.0, 22.0]),
        box(
            "obj-spectral-transition-label",
            "comment",
            [863.0, 878.0, 88.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="xfade ms",
        ),
        message(
            "obj-spectral-transition-message",
            "noise_spectral_transition_ms $1",
            [952.0, 876.0, 205.0, 22.0],
        ),
        newobj(
            "obj-spectral-transition-load",
            "loadmess 40.",
            [1163.0, 876.0, 82.0, 22.0],
        ),
        flonum("obj-dc-block", [800.0, 906.0, 57.0, 22.0]),
        box(
            "obj-dc-block-label",
            "comment",
            [863.0, 908.0, 88.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="DC block Hz",
        ),
        message(
            "obj-dc-block-message",
            "dc_block_hz $1",
            [952.0, 906.0, 104.0, 22.0],
        ),
        newobj("obj-dc-block-load", "loadmess 18.", [1062.0, 906.0, 82.0, 22.0]),
    ]

    existing_ids = {item["box"]["id"] for item in boxes}
    added_ids = {item["box"]["id"] for item in additions}
    collisions = existing_ids & added_ids
    if collisions:
        raise RuntimeError(f"Duplicate Max IDs: {sorted(collisions)}")
    boxes.extend(additions)

    lines.extend(
        [
            line("obj-noise-attack-load", "obj-noise-attack"),
            line("obj-noise-attack", "obj-noise-attack-message"),
            line("obj-noise-attack-message", controller_id),
            line("obj-spectral-transition-load", "obj-spectral-transition"),
            line("obj-spectral-transition", "obj-spectral-transition-message"),
            line("obj-spectral-transition-message", controller_id),
            line("obj-dc-block-load", "obj-dc-block"),
            line("obj-dc-block", "obj-dc-block-message"),
            line("obj-dc-block-message", controller_id),
        ]
    )
    return payload


def validate(payload: dict) -> None:
    patcher = payload["patcher"]
    boxes = [item["box"] for item in patcher["boxes"]]
    ids = [item["id"] for item in boxes]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate box IDs in generated patch")
    code = next(item["code"] for item in boxes if item.get("maxclass") == "gen.codebox~")
    required = (
        "Param noise_attack_ms(3);",
        "Param noise_spectral_transition_ms(40);",
        "Param dc_block_hz(18);",
        "spectral_mode_z",
        "excitation_dc_x1",
        "output_dc_l_x1",
        "output_dc_r_x1",
    )
    if not all(token in code for token in required):
        raise RuntimeError("Embedded DC-safe GenExpr is incomplete")
    texts = {item.get("text", "") for item in boxes}
    if f"js {CONTROLLER}" not in texts:
        raise RuntimeError("DC-safe controller was not installed")
    for control in (
        "noise_attack_ms $1",
        "noise_spectral_transition_ms $1",
        "dc_block_hz $1",
    ):
        if control not in texts:
            raise RuntimeError(f"Missing Max control: {control}")


def main() -> int:
    payload = build()
    validate(payload)
    OUTPUT_PATCH.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated DC-safe Max patch: {OUTPUT_PATCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
