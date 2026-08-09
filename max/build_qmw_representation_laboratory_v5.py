#!/usr/bin/env python3
"""Build the integrated v5 laboratory and its transform-control bpatcher."""

from __future__ import annotations

import json
from pathlib import Path

from build_qmw_pauli_basis_laboratory_v3 import build_patch as build_v3


ROOT = Path(__file__).resolve().parent
CONTROL_NAME = "QMW_Transform_Control_v5.maxpat"
CONTROL_OUTPUT = ROOT / CONTROL_NAME
LAB_OUTPUT = ROOT / "QMW_Representation_Laboratory_v5.maxpat"


def box(
    box_id: str,
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    presentation: bool = False,
    **attrs: object,
) -> dict:
    body: dict[str, object] = {
        "id": box_id,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        body["text"] = text
    if presentation:
        body["presentation"] = 1
        body["presentation_rect"] = rect
    body.update(attrs)
    return {"box": body}


def line(source: str, outlet: int, target: str, inlet: int) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [target, inlet],
        }
    }


def build_control() -> dict:
    cyan = [0.12, 0.82, 0.92, 1.0]
    orange = [0.96, 0.56, 0.18, 1.0]
    dark = [0.08, 0.09, 0.12, 1.0]
    boxes = [
        box(
            "panel",
            "panel",
            [0.0, 0.0, 1540.0, 180.0],
            presentation=True,
            bgcolor=dark,
            border=1,
            background=1,
            ignoreclick=1,
        ),
        box(
            "heading",
            "comment",
            [16.0, 8.0, 420.0, 24.0],
            text="REPRESENTATION TRANSFORM",
            presentation=True,
            fontsize=15.0,
            textcolor=cyan,
        ),
    ]

    numeric = [
        ("j", "J", 16.0, 0.7, -4.0, 4.0),
        ("ht", "h⊥", 146.0, 0.45, -4.0, 4.0),
        ("hl", "h∥", 276.0, 0.13, -4.0, 4.0),
        ("time", "time", 406.0, 1.0, -100.0, 100.0),
    ]
    for name, label, x, _default, minimum, maximum in numeric:
        boxes.extend(
            [
                box(
                    f"{name}_label",
                    "comment",
                    [x, 42.0, 42.0, 20.0],
                    text=label,
                    presentation=True,
                ),
                box(
                    name,
                    "flonum",
                    [x + 44.0, 38.0, 78.0, 25.0],
                    presentation=True,
                    minimum=minimum,
                    maximum=maximum,
                    varname=f"hamiltonian_{name}",
                    parameter_enable=1,
                ),
            ]
        )

    boxes.extend(
        [
            box("transform_label", "comment", [552.0, 42.0, 68.0, 20.0], text="transform", presentation=True),
            box(
                "transform",
                "umenu",
                [622.0, 38.0, 220.0, 24.0],
                presentation=True,
                items=[
                    "identity", ",", "hadamard", ",", "qft", ",",
                    "inverse_qft", ",", "hamiltonian", ",",
                    "graph_laplacian", ",", "floquet", ",",
                    "grover_amplified", ",", "epistrophe",
                ],
                varname="representation_transform",
                parameter_enable=1,
            ),
            box("boundary_label", "comment", [858.0, 42.0, 72.0, 20.0], text="boundary", presentation=True),
            box(
                "boundary",
                "umenu",
                [932.0, 38.0, 114.0, 24.0],
                presentation=True,
                items=["open", ",", "periodic"],
                varname="hamiltonian_boundary",
                parameter_enable=1,
            ),
            box("preset_label", "comment", [16.0, 88.0, 48.0, 20.0], text="state", presentation=True),
            box(
                "preset",
                "umenu",
                [66.0, 84.0, 154.0, 24.0],
                presentation=True,
                items=["ghz", ",", "bell", ",", "weave"],
                varname="hamiltonian_preset",
                parameter_enable=1,
            ),
            box("shots_label", "comment", [238.0, 88.0, 46.0, 20.0], text="shots", presentation=True),
            box(
                "shots",
                "number",
                [286.0, 84.0, 66.0, 25.0],
                presentation=True,
                minimum=1,
                varname="hamiltonian_shots",
                parameter_enable=1,
            ),
            box("sampling_label", "comment", [370.0, 88.0, 68.0, 20.0], text="sampling", presentation=True),
            box(
                "sampling",
                "umenu",
                [440.0, 84.0, 198.0, 24.0],
                presentation=True,
                items=["fixed", ",", "resample", ",", "sequence"],
                varname="hamiltonian_sampling",
                parameter_enable=1,
            ),
            box("seed_label", "comment", [656.0, 88.0, 38.0, 20.0], text="seed", presentation=True),
            box(
                "seed",
                "number",
                [696.0, 84.0, 82.0, 25.0],
                presentation=True,
                minimum=0,
                varname="hamiltonian_seed",
                parameter_enable=1,
            ),
            box(
                "commit",
                "textbutton",
                [800.0, 78.0, 168.0, 36.0],
                text="COMMIT TOMOGRAPHY",
                texton="COMMIT TOMOGRAPHY",
                presentation=True,
                bgcolor=orange,
            ),
            box("reset", "message", [982.0, 84.0, 102.0, 24.0], text="reset tracking", presentation=True),
            box("store1", "message", [1120.0, 38.0, 58.0, 24.0], text="store 1", presentation=True),
            box("recall1", "message", [1184.0, 38.0, 34.0, 24.0], text="1", presentation=True),
            box("write", "message", [1224.0, 38.0, 48.0, 24.0], text="write", presentation=True),
            box("read", "message", [1278.0, 38.0, 44.0, 24.0], text="read", presentation=True),
            box(
                "preset_note",
                "comment",
                [1120.0, 68.0, 240.0, 42.0],
                text="preset 1 · store / recall / write / read",
                presentation=True,
                textcolor=[0.7, 0.72, 0.78, 1.0],
            ),
            box(
                "preview_note",
                "comment",
                [650.0, 132.0, 700.0, 24.0],
                text=(
                    "J / fields / time: Hamiltonian + Floquet · "
                    "graph / marked / steps: operator-specific"
                ),
                presentation=True,
                textcolor=orange,
            ),
            box("graph_label", "comment", [16.0, 136.0, 42.0, 20.0], text="graph", presentation=True),
            box(
                "graph",
                "umenu",
                [60.0, 132.0, 110.0, 24.0],
                presentation=True,
                items=["cycle", ",", "path", ",", "complete"],
                varname="representation_graph",
                parameter_enable=1,
            ),
            box("normalized_label", "comment", [180.0, 136.0, 76.0, 20.0], text="normalized", presentation=True),
            box(
                "normalized",
                "toggle",
                [258.0, 132.0, 24.0, 24.0],
                presentation=True,
                varname="representation_normalized_graph",
                parameter_enable=1,
            ),
            box("marked_label", "comment", [300.0, 136.0, 52.0, 20.0], text="marked", presentation=True),
            box(
                "marked",
                "number",
                [354.0, 132.0, 54.0, 24.0],
                presentation=True,
                minimum=0,
                maximum=15,
                varname="representation_marked_state",
                parameter_enable=1,
            ),
            box("steps_label", "comment", [426.0, 136.0, 40.0, 20.0], text="steps", presentation=True),
            box(
                "steps",
                "number",
                [468.0, 132.0, 54.0, 24.0],
                presentation=True,
                minimum=0,
                varname="representation_steps",
                parameter_enable=1,
            ),
        ]
    )

    hidden = [
        box(
            "pak",
            "newobj",
            [20.0, 220.0, 680.0, 24.0],
            text="pak i s f f f f s s i s i s i i i",
        ),
        box("speedlim", "newobj", [500.0, 220.0, 90.0, 24.0], text="speedlim 150"),
        box("preview_pack", "newobj", [610.0, 220.0, 240.0, 24.0], text="o.pack /qmw/v5/transform/preview"),
        box("commit_store", "newobj", [20.0, 255.0, 58.0, 24.0], text="zl reg"),
        box("commit_pack", "newobj", [100.0, 255.0, 240.0, 24.0], text="o.pack /qmw/v5/transform/commit"),
        box("reset_pack", "newobj", [360.0, 255.0, 230.0, 24.0], text="o.pack /qmw/v5/transform/reset_tracking"),
        box("send", "newobj", [890.0, 220.0, 170.0, 24.0], text="udpsend 127.0.0.1 7445"),
        box("autopattr", "newobj", [650.0, 255.0, 70.0, 24.0], text="autopattr"),
        box(
            "presets",
            "newobj",
            [740.0, 255.0, 300.0, 24.0],
            text="pattrstorage qmw_v5_transform_presets @autorestore 0",
        ),
    ]
    boxes.extend(hidden)

    defaults = [
        ("load_j", "loadmess 0.7", "j", 0),
        ("load_ht", "loadmess 0.45", "ht", 0),
        ("load_hl", "loadmess 0.13", "hl", 0),
        ("load_time", "loadmess 1.", "time", 0),
        ("load_transform", "loadmess 4", "transform", 0),
        ("load_boundary", "loadmess 0", "boundary", 0),
        ("load_preset", "loadmess 0", "preset", 0),
        ("load_shots", "loadmess 256", "shots", 0),
        ("load_sampling", "loadmess 0", "sampling", 0),
        ("load_seed", "loadmess 23", "seed", 0),
        ("load_graph", "loadmess 0", "graph", 0),
        ("load_normalized", "loadmess 0", "normalized", 0),
        ("load_marked", "loadmess 0", "marked", 0),
        ("load_steps", "loadmess 1", "steps", 0),
    ]
    for index, (name, text, _target, _inlet) in enumerate(defaults):
        boxes.append(
            box(
                name,
                "newobj",
                [20.0 + 94.0 * index, 300.0, 88.0, 22.0],
                text=text,
            )
        )

    lines = [
        line("transform", 1, "pak", 1),
        line("j", 0, "pak", 2),
        line("ht", 0, "pak", 3),
        line("hl", 0, "pak", 4),
        line("time", 0, "pak", 5),
        line("boundary", 1, "pak", 6),
        line("preset", 1, "pak", 7),
        line("shots", 0, "pak", 8),
        line("sampling", 1, "pak", 9),
        line("seed", 0, "pak", 10),
        line("graph", 1, "pak", 11),
        line("normalized", 0, "pak", 12),
        line("marked", 0, "pak", 13),
        line("steps", 0, "pak", 14),
        line("pak", 0, "speedlim", 0),
        line("pak", 0, "commit_store", 1),
        line("speedlim", 0, "preview_pack", 0),
        line("preview_pack", 0, "send", 0),
        line("commit", 0, "commit_store", 0),
        line("commit_store", 0, "commit_pack", 0),
        line("commit_pack", 0, "send", 0),
        line("reset", 0, "reset_pack", 0),
        line("reset_pack", 0, "send", 0),
        line("store1", 0, "presets", 0),
        line("recall1", 0, "presets", 0),
        line("write", 0, "presets", 0),
        line("read", 0, "presets", 0),
    ]
    for name, _text, target, inlet in defaults:
        lines.append(line(name, 0, target, inlet))

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 8,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [40.0, 50.0, 1560.0, 360.0],
            "openinpresentation": 1,
            "default_fontname": "Arial",
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {"name": "o.pack.mxo", "type": "iLaX", "implicit": 1}
            ],
            "autosave": 0,
        }
    }


def build_laboratory(control: dict | None = None) -> dict:
    if control is None:
        control = build_control()
    document = build_v3()
    patcher = document["patcher"]
    removed = {
        "title",
        "subtitle",
        "launch",
        "ghz_qft",
        "ghz_hadamard",
        "ghz_hamiltonian",
        "weave_qft",
        "identity",
        "opack_run",
        "udpsend",
        "ping",
        "opack_ping",
        "status",
    }
    patcher["boxes"] = [
        item for item in patcher["boxes"] if item["box"]["id"] not in removed
    ]
    patcher["lines"] = [
        item
        for item in patcher["lines"]
        if item["patchline"]["source"][0] not in removed
        and item["patchline"]["destination"][0] not in removed
    ]
    for item in patcher["boxes"]:
        rect = item["box"].get("patching_rect")
        if rect and rect[1] >= 180.0:
            rect[1] += 130.0

    patcher["boxes"].extend(
        [
            box(
                "v5_title",
                "comment",
                [28.0, 14.0, 1100.0, 32.0],
                text=(
                    "QMW · REPRESENTATION LABORATORY v5 · "
                    "LIVE TRANSFORM INSTRUMENT"
                ),
                fontsize=20.0,
                textcolor=[0.12, 0.82, 0.92, 1.0],
            ),
            box(
                "v5_launch",
                "comment",
                [30.0, 48.0, 1500.0, 22.0],
                text=(
                    "Run only: python workshop_lightweight/"
                    "qmw_representation_laboratory_v5.py"
                ),
                textcolor=[0.68, 0.7, 0.75, 1.0],
            ),
            box(
                "transform_controls",
                "bpatcher",
                [30.0, 78.0, 1560.0, 180.0],
                name=CONTROL_NAME,
                embed=1,
                patcher=control["patcher"],
                border=1,
                numinlets=0,
                numoutlets=0,
                offset=[0.0, 0.0],
                enablehscroll=0,
                enablevscroll=0,
                lockeddragscroll=0,
                lockedsize=0,
            ),
            box(
                "v5_status",
                "message",
                [30.0, 272.0, 1560.0, 26.0],
                text=(
                    "Select a transform and adjust its controls; preview is automatic. "
                    "Press COMMIT TOMOGRAPHY to update the instrument."
                ),
            ),
            box(
                "v4_status_route",
                "newobj",
                [1080.0, 1320.0, 500.0, 24.0],
                text=(
                    "o.route /qmw/v5/transform/status "
                    "/qmw/v5/transform/error"
                ),
                hidden=1,
            ),
            box(
                "v4_prepend_status",
                "newobj",
                [1080.0, 1350.0, 110.0, 24.0],
                text="prepend status",
                hidden=1,
            ),
            box(
                "v4_prepend_error",
                "newobj",
                [1200.0, 1350.0, 110.0, 24.0],
                text="prepend error",
                hidden=1,
            ),
        ]
    )
    patcher["lines"].extend(
        [
            line("udpreceive", 0, "v4_status_route", 0),
            line("v4_status_route", 0, "v4_prepend_status", 0),
            line("v4_status_route", 1, "v4_prepend_error", 0),
            line("v4_prepend_status", 0, "receiver", 0),
            line("v4_prepend_error", 0, "receiver", 0),
            line("receiver", 9, "v5_status", 0),
        ]
    )
    patcher["rect"] = [20.0, 30.0, 1640.0, 1400.0]
    patcher["dependency_cache"].append(
        {"name": CONTROL_NAME, "type": "JSON", "implicit": 1}
    )
    return document


def validate_control(document: dict) -> None:
    boxes = [item["box"] for item in document["patcher"]["boxes"]]
    texts = {item.get("text", "") for item in boxes}
    varnames = {item.get("varname", "") for item in boxes}
    assert "pattrstorage qmw_v5_transform_presets @autorestore 0" in texts
    assert "o.pack /qmw/v5/transform/preview" in texts
    assert "o.pack /qmw/v5/transform/commit" in texts
    assert "hamiltonian_j" in varnames
    assert "hamiltonian_ht" in varnames
    assert "hamiltonian_hl" in varnames
    assert "representation_transform" in varnames
    assert "hamiltonian_sampling" in varnames
    assert "representation_graph" in varnames
    assert "representation_steps" in varnames


def validate_laboratory(document: dict) -> None:
    boxes = [item["box"] for item in document["patcher"]["boxes"]]
    ids = {item["id"] for item in boxes}
    texts = {item.get("text", "") for item in boxes}
    assert "transform_controls" in ids
    transform_control = next(
        item for item in boxes if item["id"] == "transform_controls"
    )
    assert transform_control["embed"] == 1
    assert "patcher" in transform_control
    assert "v5_status" in ids
    assert "o.pack /qmw/basis/run" not in texts
    assert "udpsend 127.0.0.1 7435" not in texts
    assert "udpreceive 7436" in texts
    assert sum(item["maxclass"] == "jit.pwindow" for item in boxes) == 2


def main() -> int:
    control = build_control()
    laboratory = build_laboratory(control)
    validate_control(control)
    validate_laboratory(laboratory)
    CONTROL_OUTPUT.write_text(
        json.dumps(control, indent=2) + "\n",
        encoding="utf-8",
    )
    LAB_OUTPUT.write_text(
        json.dumps(laboratory, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {CONTROL_OUTPUT}")
    print(f"Wrote {LAB_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
