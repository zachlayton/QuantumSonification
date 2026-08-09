#!/usr/bin/env python3
"""Build a small QMW modal bank with MaxPyLang 0.1.1.

This is intentionally a pilot rather than shared production infrastructure.  The
normalization step records the small compatibility layer currently required for
Max 9 and removes invalid placeholder patch-cord midpoints emitted by 0.1.1.
"""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_MaxPyLang_Modal_Bank_v1.maxpat"


def normalize_for_max9(document: dict[str, Any]) -> dict[str, Any]:
    """Apply the narrow MaxPyLang 0.1.1-to-Max 9 compatibility fixes."""

    patcher = document["patcher"]
    patcher["appversion"] = {
        "major": 9,
        "minor": 0,
        "revision": 5,
        "architecture": "x64",
        "modernui": 1,
    }
    patcher["rect"] = [80.0, 60.0, 920.0, 590.0]

    for entry in patcher["boxes"]:
        box = entry["box"]
        if box.get("maxclass") == "comment" and box.get("text", "").startswith("comment "):
            box["text"] = box["text"][len("comment ") :]

    for entry in patcher["lines"]:
        patchline = entry["patchline"]
        if patchline.get("midpoints") == [None]:
            del patchline["midpoints"]

    return document


def build_document() -> dict[str, Any]:
    """Construct the graph through MaxPyLang and return normalized Max JSON."""

    import maxpylang as mp

    patch = mp.MaxPatch(verbose=False)

    def place(text: str, rect: list[float]):
        obj = mp.MaxObject(text, patching_rect=rect)
        return patch.place(
            obj,
            spacing_type="custom",
            spacing=[[rect[0], rect[1]]],
            verbose=False,
        )[0]

    # MaxPyLang 0.1.1 prints its picked-object list even with verbose=False.
    # Capture that library noise so this builder behaves like the other QMW tools.
    with redirect_stdout(io.StringIO()):
        place("comment QMW MAXPYLANG MODAL BANK v1", [28.0, 18.0, 700.0, 24.0])
        place(
            "comment Four phase-derived modes; click the speaker to start DSP.",
            [28.0, 47.0, 700.0, 20.0],
        )

        frequencies = (110.0, 138.59, 164.81, 220.0)
        oscillators = []
        attenuators = []
        for index, frequency in enumerate(frequencies):
            x = 30.0 + index * 180.0
            oscillators.append(place(f"cycle~ {frequency}", [x, 120.0, 92.0, 22.0]))
            attenuators.append(place("*~ 0.055", [x, 165.0, 70.0, 22.0]))

        pair_a = place("+~", [130.0, 235.0, 42.0, 22.0])
        pair_b = place("+~", [490.0, 235.0, 42.0, 22.0])
        master = place("+~", [310.0, 300.0, 42.0, 22.0])
        meter = place("meter~", [385.0, 302.0, 180.0, 13.0])
        scope = place("scope~", [310.0, 355.0, 320.0, 145.0])
        dac = place("ezdac~", [690.0, 355.0, 54.0, 45.0])

        for oscillator, attenuator in zip(oscillators, attenuators):
            patch.connect([oscillator.outs[0], attenuator.ins[0]], verbose=False)
        patch.connect([attenuators[0].outs[0], pair_a.ins[0]], verbose=False)
        patch.connect([attenuators[1].outs[0], pair_a.ins[1]], verbose=False)
        patch.connect([attenuators[2].outs[0], pair_b.ins[0]], verbose=False)
        patch.connect([attenuators[3].outs[0], pair_b.ins[1]], verbose=False)
        patch.connect([pair_a.outs[0], master.ins[0]], verbose=False)
        patch.connect([pair_b.outs[0], master.ins[1]], verbose=False)
        patch.connect([master.outs[0], meter.ins[0]], verbose=False)
        patch.connect([master.outs[0], scope.ins[0]], verbose=False)
        patch.connect([master.outs[0], dac.ins[0]], verbose=False)
        patch.connect([master.outs[0], dac.ins[1]], verbose=False)

    with TemporaryDirectory(prefix="qmw_maxpylang_") as temp_dir:
        raw_path = Path(temp_dir) / "raw.maxpat"
        patch.save(str(raw_path), verbose=False, check=False)
        document = json.loads(raw_path.read_text(encoding="utf-8"))

    return normalize_for_max9(document)


def main() -> None:
    document = build_document()
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
