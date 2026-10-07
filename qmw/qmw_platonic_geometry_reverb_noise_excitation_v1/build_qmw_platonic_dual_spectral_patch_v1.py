#!/usr/bin/env python3
"""Build the v4 Max fork with switchable quantum/input spectral noise."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_PATCH = HERE / "QMW_Platonic_Noise_Excitation_v3.maxpat"
GENEXPR = HERE / "qmw_platonic_geometry_reverb_dual_spectral_v1.genexpr"
CONTROLLER = "qmw_platonic_geometry_controller_dual_spectral_v1.js"
OUTPUT_PATCH = HERE / "QMW_Platonic_Noise_Excitation_v4.maxpat"


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
        if item["box"].get("text") == "js qmw_platonic_geometry_controller_v1.js"
    ]
    if len(controllers) != 1:
        raise RuntimeError(f"Expected one controller, found {len(controllers)}")
    controller_id = controllers[0]["id"]
    controllers[0]["text"] = f"js {CONTROLLER}"

    additions = [
        box(
            "obj-spectral-title",
            "comment",
            [990.0, 340.0, 205.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="DUAL SPECTRAL NOISE",
        ),
        box(
            "obj-spectral-mode",
            "toggle",
            [990.0, 369.0, 24.0, 24.0],
            numinlets=1,
            numoutlets=1,
            outlettype=["int"],
            parameter_enable=0,
        ),
        box(
            "obj-spectral-mode-label",
            "comment",
            [1022.0, 371.0, 184.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="0 QUANTUM   1 INPUT",
        ),
        message(
            "obj-spectral-mode-message",
            "noise_spectral_mode $1",
            [990.0, 400.0, 143.0, 22.0],
        ),
        flonum("obj-spectral-amount", [990.0, 437.0, 57.0, 22.0]),
        box(
            "obj-spectral-amount-label",
            "comment",
            [1053.0, 439.0, 66.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="amount",
        ),
        message(
            "obj-spectral-amount-message",
            "noise_spectral_amount $1",
            [1120.0, 437.0, 159.0, 22.0],
        ),
        newobj("obj-spectral-amount-load", "loadmess 1.", [990.0, 465.0, 75.0, 22.0]),
        flonum("obj-spectral-q", [990.0, 500.0, 57.0, 22.0]),
        box(
            "obj-spectral-q-label",
            "comment",
            [1053.0, 502.0, 66.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="Q",
        ),
        message(
            "obj-spectral-q-message",
            "noise_spectral_q $1",
            [1120.0, 500.0, 128.0, 22.0],
        ),
        newobj("obj-spectral-q-load", "loadmess 7.", [990.0, 528.0, 75.0, 22.0]),
        flonum("obj-spectral-gain", [990.0, 563.0, 57.0, 22.0]),
        box(
            "obj-spectral-gain-label",
            "comment",
            [1053.0, 565.0, 66.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="gain",
        ),
        message(
            "obj-spectral-gain-message",
            "noise_spectral_gain $1",
            [1120.0, 563.0, 139.0, 22.0],
        ),
        newobj("obj-spectral-gain-load", "loadmess 2.5", [990.0, 591.0, 82.0, 22.0]),
        flonum("obj-spectral-base", [990.0, 626.0, 57.0, 22.0]),
        box(
            "obj-spectral-base-label",
            "comment",
            [1053.0, 628.0, 66.0, 20.0],
            numinlets=1,
            numoutlets=0,
            text="base Hz",
        ),
        message(
            "obj-spectral-base-message",
            "noise_spectral_base_hz $1",
            [1120.0, 626.0, 167.0, 22.0],
        ),
        newobj("obj-spectral-base-load", "loadmess 55.", [990.0, 654.0, 82.0, 22.0]),
        newobj("obj-spectrum-route-qmw", "OSC-route /qmw", [990.0, 694.0, 103.0, 22.0], outlets=2),
        newobj(
            "obj-spectrum-route-density",
            "OSC-route /density_field",
            [990.0, 724.0, 143.0, 22.0],
            outlets=2,
        ),
        newobj(
            "obj-spectrum-route-values",
            "OSC-route /magnitude /harmonics",
            [990.0, 754.0, 190.0, 22.0],
            outlets=3,
        ),
        newobj(
            "obj-spectrum-prepend-magnitude",
            "prepend quantum_magnitudes",
            [990.0, 784.0, 174.0, 22.0],
        ),
        newobj(
            "obj-spectrum-prepend-harmonics",
            "prepend quantum_harmonics",
            [1170.0, 784.0, 165.0, 22.0],
        ),
    ]

    existing_ids = {item["box"]["id"] for item in boxes}
    added_ids = {item["box"]["id"] for item in additions}
    collisions = existing_ids & added_ids
    if collisions:
        raise RuntimeError(f"Duplicate Max IDs: {sorted(collisions)}")
    boxes.extend(additions)

    lines.extend(
        [
            line("obj-spectral-mode", "obj-spectral-mode-message"),
            line("obj-spectral-mode-message", controller_id),
            line("obj-spectral-amount-load", "obj-spectral-amount"),
            line("obj-spectral-amount", "obj-spectral-amount-message"),
            line("obj-spectral-amount-message", controller_id),
            line("obj-spectral-q-load", "obj-spectral-q"),
            line("obj-spectral-q", "obj-spectral-q-message"),
            line("obj-spectral-q-message", controller_id),
            line("obj-spectral-gain-load", "obj-spectral-gain"),
            line("obj-spectral-gain", "obj-spectral-gain-message"),
            line("obj-spectral-gain-message", controller_id),
            line("obj-spectral-base-load", "obj-spectral-base"),
            line("obj-spectral-base", "obj-spectral-base-message"),
            line("obj-spectral-base-message", controller_id),
            line("obj-27", "obj-spectrum-route-qmw"),
            line("obj-spectrum-route-qmw", "obj-spectrum-route-density"),
            line("obj-spectrum-route-density", "obj-spectrum-route-values"),
            line("obj-spectrum-route-values", "obj-spectrum-prepend-magnitude", 0),
            line("obj-spectrum-route-values", "obj-spectrum-prepend-harmonics", 1),
            line("obj-spectrum-prepend-magnitude", controller_id),
            line("obj-spectrum-prepend-harmonics", controller_id),
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
        "Param noise_spectral_mode(0);",
        "quantum_shaped_noise",
        "input_shaped_noise",
        "selected_spectral_noise",
    )
    if not all(token in code for token in required):
        raise RuntimeError("Embedded dual-spectral GenExpr is incomplete")
    texts = {item.get("text", "") for item in boxes}
    if f"js {CONTROLLER}" not in texts:
        raise RuntimeError("Dual-spectral controller was not installed")
    if "OSC-route /magnitude /harmonics" not in texts:
        raise RuntimeError("Quantum spectrum OSC routing is missing")


def main() -> int:
    payload = build()
    validate(payload)
    OUTPUT_PATCH.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated dual-spectral Max patch: {OUTPUT_PATCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
