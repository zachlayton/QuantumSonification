#!/usr/bin/env python3
"""Build the high-level Hamiltonian transform control panel for Max."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("QMW_Hamiltonian_Transform_Control_v4.maxpat")


def box(
    box_id: str,
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    **attrs: object,
) -> dict:
    body: dict[str, object] = {
        "id": box_id,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        body["text"] = text
    body.update(attrs)
    return {"box": body}


def line(source: str, outlet: int, target: str, inlet: int) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [target, inlet],
        }
    }


def build() -> dict:
    cyan = [0.12, 0.82, 0.92, 1.0]
    orange = [0.95, 0.55, 0.18, 1.0]
    boxes = [
        box(
            "title",
            "comment",
            [30.0, 18.0, 930.0, 32.0],
            text="QMW · HAMILTONIAN TRANSFORM CONTROL v4",
            fontsize=20.0,
            textcolor=cyan,
        ),
        box(
            "subtitle",
            "comment",
            [30.0, 52.0, 930.0, 22.0],
            text=(
                "Preview rebuilds the exact representation · Commit runs "
                "paired 81-setting Full Pauli tomography"
            ),
        ),
        box(
            "launch",
            "comment",
            [30.0, 78.0, 930.0, 22.0],
            text=(
                "Start: python workshop_lightweight/"
                "qmw_representation_hamiltonian_v4.py"
            ),
            textcolor=[0.68, 0.7, 0.75, 1.0],
        ),
        box("j_label", "comment", [30.0, 122.0, 180.0, 20.0], text="COUPLING  J"),
        box(
            "j",
            "flonum",
            [220.0, 118.0, 92.0, 26.0],
            minimum=-4.0,
            maximum=4.0,
        ),
        box("ht_label", "comment", [30.0, 162.0, 180.0, 20.0], text="TRANSVERSE FIELD  h⊥"),
        box(
            "ht",
            "flonum",
            [220.0, 158.0, 92.0, 26.0],
            minimum=-4.0,
            maximum=4.0,
        ),
        box("hl_label", "comment", [30.0, 202.0, 180.0, 20.0], text="LONGITUDINAL FIELD  h∥"),
        box(
            "hl",
            "flonum",
            [220.0, 198.0, 92.0, 26.0],
            minimum=-4.0,
            maximum=4.0,
        ),
        box("time_label", "comment", [30.0, 242.0, 180.0, 20.0], text="EVOLUTION TIME  t"),
        box(
            "time",
            "flonum",
            [220.0, 238.0, 92.0, 26.0],
            minimum=-100.0,
            maximum=100.0,
        ),
        box("mode_label", "comment", [370.0, 122.0, 130.0, 20.0], text="MODE"),
        box("mode_eigen", "message", [510.0, 118.0, 102.0, 24.0], text="eigenbasis"),
        box("mode_evolution", "message", [620.0, 118.0, 92.0, 24.0], text="evolution"),
        box("boundary_label", "comment", [370.0, 162.0, 130.0, 20.0], text="BOUNDARY"),
        box("boundary_open", "message", [510.0, 158.0, 62.0, 24.0], text="open"),
        box("boundary_periodic", "message", [580.0, 158.0, 82.0, 24.0], text="periodic"),
        box("preset_label", "comment", [370.0, 202.0, 130.0, 20.0], text="STATE"),
        box("preset_ghz", "message", [510.0, 198.0, 48.0, 24.0], text="ghz"),
        box("preset_bell", "message", [566.0, 198.0, 48.0, 24.0], text="bell"),
        box("preset_weave", "message", [622.0, 198.0, 58.0, 24.0], text="weave"),
        box("shots_label", "comment", [370.0, 242.0, 130.0, 20.0], text="SHOTS / SETTING"),
        box("shots", "number", [510.0, 238.0, 78.0, 26.0], minimum=1),
        box("sampling_label", "comment", [30.0, 298.0, 180.0, 20.0], text="SAMPLING"),
        box("sampling_fixed", "message", [220.0, 294.0, 58.0, 24.0], text="fixed"),
        box("sampling_resample", "message", [286.0, 294.0, 74.0, 24.0], text="resample"),
        box("sampling_sequence", "message", [368.0, 294.0, 74.0, 24.0], text="sequence"),
        box("seed_label", "comment", [480.0, 298.0, 48.0, 20.0], text="SEED"),
        box("seed", "number", [536.0, 294.0, 96.0, 26.0], minimum=0),
        box(
            "pak",
            "newobj",
            [30.0, 350.0, 470.0, 24.0],
            text="pak i f f f f s s s i s i",
        ),
        box("speedlim", "newobj", [520.0, 350.0, 92.0, 24.0], text="speedlim 150"),
        box(
            "preview_pack",
            "newobj",
            [628.0, 350.0, 260.0, 24.0],
            text="o.pack /qmw/v4/hamiltonian/preview",
        ),
        box("commit_store", "newobj", [30.0, 390.0, 58.0, 24.0], text="zl reg"),
        box(
            "commit",
            "textbutton",
            [106.0, 386.0, 180.0, 34.0],
            text="COMMIT TOMOGRAPHY",
            texton="COMMIT TOMOGRAPHY",
            bgcolor=orange,
        ),
        box(
            "commit_pack",
            "newobj",
            [304.0, 390.0, 260.0, 24.0],
            text="o.pack /qmw/v4/hamiltonian/commit",
        ),
        box(
            "reset",
            "message",
            [590.0, 390.0, 108.0, 24.0],
            text="reset tracking",
        ),
        box(
            "reset_pack",
            "newobj",
            [714.0, 390.0, 230.0, 24.0],
            text="o.pack /qmw/v4/hamiltonian/reset_tracking",
        ),
        box(
            "send",
            "newobj",
            [628.0, 438.0, 170.0, 24.0],
            text="udpsend 127.0.0.1 7445",
        ),
        box(
            "notice",
            "comment",
            [30.0, 446.0, 560.0, 42.0],
            text=(
                "Parameter changes are throttled to exact previews. "
                "Only COMMIT launches stochastic tomography."
            ),
            textcolor=orange,
        ),
    ]
    defaults = {
        "load_j": ("loadmess 0.7", "j"),
        "load_ht": ("loadmess 0.45", "ht"),
        "load_hl": ("loadmess 0.13", "hl"),
        "load_time": ("loadmess 1.", "time"),
        "load_mode": ("loadmess eigenbasis", "pak"),
        "load_boundary": ("loadmess open", "pak"),
        "load_preset": ("loadmess ghz", "pak"),
        "load_shots": ("loadmess 256", "shots"),
        "load_sampling": ("loadmess fixed", "pak"),
        "load_seed": ("loadmess 23", "seed"),
    }
    for index, (box_id, (text, _target)) in enumerate(defaults.items()):
        boxes.append(
            box(
                box_id,
                "newobj",
                [30.0 + index * 86.0, 510.0, 80.0, 22.0],
                text=text,
                hidden=1,
            )
        )

    lines = [
        line("j", 0, "pak", 1),
        line("ht", 0, "pak", 2),
        line("hl", 0, "pak", 3),
        line("time", 0, "pak", 4),
        line("mode_eigen", 0, "pak", 5),
        line("mode_evolution", 0, "pak", 5),
        line("boundary_open", 0, "pak", 6),
        line("boundary_periodic", 0, "pak", 6),
        line("preset_ghz", 0, "pak", 7),
        line("preset_bell", 0, "pak", 7),
        line("preset_weave", 0, "pak", 7),
        line("shots", 0, "pak", 8),
        line("sampling_fixed", 0, "pak", 9),
        line("sampling_resample", 0, "pak", 9),
        line("sampling_sequence", 0, "pak", 9),
        line("seed", 0, "pak", 10),
        line("pak", 0, "speedlim", 0),
        line("pak", 0, "commit_store", 1),
        line("speedlim", 0, "preview_pack", 0),
        line("preview_pack", 0, "send", 0),
        line("commit", 0, "commit_store", 0),
        line("commit_store", 0, "commit_pack", 0),
        line("commit_pack", 0, "send", 0),
        line("reset", 0, "reset_pack", 0),
        line("reset_pack", 0, "send", 0),
        line("load_j", 0, "j", 0),
        line("load_ht", 0, "ht", 0),
        line("load_hl", 0, "hl", 0),
        line("load_time", 0, "time", 0),
        line("load_mode", 0, "pak", 5),
        line("load_boundary", 0, "pak", 6),
        line("load_preset", 0, "pak", 7),
        line("load_shots", 0, "shots", 0),
        line("load_sampling", 0, "pak", 9),
        line("load_seed", 0, "seed", 0),
    ]
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
            "rect": [40.0, 50.0, 1000.0, 580.0],
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {"name": "o.pack.mxo", "type": "iLaX", "implicit": 1}
            ],
            "autosave": 0,
        }
    }


def validate(document: dict) -> None:
    texts = {
        item["box"].get("text", "")
        for item in document["patcher"]["boxes"]
    }
    assert "o.pack /qmw/v4/hamiltonian/preview" in texts
    assert "o.pack /qmw/v4/hamiltonian/commit" in texts
    assert "udpsend 127.0.0.1 7445" in texts
    assert "speedlim 150" in texts
    assert "pak i f f f f s s s i s i" in texts


def main() -> int:
    document = build()
    validate(document)
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
