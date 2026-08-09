#!/usr/bin/env python3
"""Build the Bloch-harmonic control adapter for Spat5 and the surface FDN."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_qmw_realtime_surface_reverb_v1 import PatchBuilder


MAX_ROOT = Path(__file__).resolve().parent
OUTPUT = MAX_ROOT / "control_room_modules" / "QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat"


def build_patch() -> dict[str, Any]:
    builder = PatchBuilder()
    builder.add(
        "comment",
        [25.0, 20.0, 760.0, 28.0],
        text="QMW BLOCH HARMONICS → SPAT5 + MODAL REVERB v1",
        fontsize=18.0,
        fontface=1,
    )
    builder.add(
        "comment",
        [25.0, 52.0, 920.0, 36.0],
        text=(
            "Degree 1 steers four Spat sources. Degrees 2–3 control bounded "
            "FDN resonance, decay, damping, spectral tilt, warp, and mode weights."
        ),
        linecount=2,
    )

    raw = builder.add("newobj", [25.0, 105.0, 100.0, 22.0], text="r qmw.osc.raw")
    qmw = builder.add("newobj", [145.0, 105.0, 100.0, 22.0], text="OSC-route /qmw")
    acoustics = builder.add(
        "newobj", [265.0, 105.0, 135.0, 22.0], text="OSC-route /acoustics"
    )
    domains = builder.add(
        "newobj",
        [420.0, 105.0, 205.0, 22.0],
        text="OSC-route /spat /reverb /modal",
    )
    builder.connect(raw, 0, qmw)
    builder.connect(qmw, 0, acoustics)
    builder.connect(acoustics, 0, domains)

    source_root = builder.add(
        "newobj", [25.0, 165.0, 118.0, 22.0], text="OSC-route /source"
    )
    sources = builder.add(
        "newobj", [165.0, 165.0, 190.0, 22.0], text="OSC-route /1 /2 /3 /4"
    )
    builder.connect(domains, 0, source_root)
    builder.connect(source_root, 0, sources)

    spat_oper = builder.add(
        "newobj",
        [25.0, 430.0, 560.0, 22.0],
        text=(
            'spat5.oper @initwith "/source/number 4, '
            '/source/*/aperture/visible 1, /source/*/constraint/circular 0"'
        ),
        numinlets=1,
        numoutlets=2,
        outlettype=["", ""],
    )
    spat_bus = builder.add(
        "newobj", [610.0, 430.0, 125.0, 22.0], text="s qmw.spat.control"
    )
    control_outlet = builder.add(
        "outlet", [760.0, 430.0, 30.0, 30.0], comment="Spat5 OSC control"
    )
    builder.connect(spat_oper, 0, control_outlet)

    for source_index in range(1, 5):
        y = 210.0 + (source_index - 1) * 48.0
        route = builder.add(
            "newobj",
            [25.0, y, 225.0, 22.0],
            text="OSC-route /aed /aperture /spread",
        )
        builder.connect(sources, source_index - 1, route)
        for outlet_index, field in enumerate(("aed", "aperture", "spread")):
            prepend = builder.add(
                "newobj",
                [275.0 + outlet_index * 205.0, y, 185.0, 22.0],
                text=f"prepend /source/{source_index}/{field}",
            )
            builder.connect(route, outlet_index, prepend)
            builder.connect(prepend, 0, spat_oper)
            builder.connect(prepend, 0, spat_bus)

    reverb_route = builder.add(
        "newobj",
        [25.0, 510.0, 275.0, 22.0],
        text="OSC-route /resonance /decay /damping",
    )
    modal_route = builder.add(
        "newobj",
        [25.0, 555.0, 245.0, 22.0],
        text="OSC-route /tilt /warp /weights",
    )
    builder.connect(domains, 1, reverb_route)
    builder.connect(domains, 2, modal_route)
    surface_bus = builder.add(
        "newobj", [725.0, 535.0, 190.0, 22.0], text="s qmw.acoustic.modal.control"
    )
    mappings = (
        (reverb_route, 0, "resonance", 330.0, 510.0),
        (reverb_route, 1, "decay", 460.0, 510.0),
        (reverb_route, 2, "damping", 570.0, 510.0),
        (modal_route, 0, "spectral_tilt", 300.0, 555.0),
        (modal_route, 1, "modal_warp", 455.0, 555.0),
        (modal_route, 2, "modal_weights", 600.0, 555.0),
    )
    for source, outlet, parameter, x, y in mappings:
        prepend = builder.add(
            "newobj", [x, y, 130.0, 22.0], text=f"prepend {parameter}"
        )
        builder.connect(source, outlet, prepend)
        builder.connect(prepend, 0, surface_bus)

    builder.add(
        "comment",
        [25.0, 620.0, 860.0, 54.0],
        text=(
            "Connect r qmw.spat.control to spat5.spat~ (or use the outlet). "
            "The modal branch is mirrored to qmw.acoustic.modal.control. "
            "Feedback gains remain clipped to each renderer's established stability ceiling."
        ),
        linecount=3,
    )

    audio_inputs: list[str] = []
    for index in range(4):
        inlet = builder.add(
            "inlet",
            [25.0 + index * 70.0, 690.0, 30.0, 30.0],
            comment=f"Spat source {index + 1}",
            index=index + 1,
            numinlets=0,
            numoutlets=1,
            outlettype=["signal"],
        )
        audio_inputs.append(inlet)
    spat_renderer = builder.add(
        "newobj",
        [330.0, 690.0, 590.0, 22.0],
        text=(
            'spat5.spat~ @inputs 4 @internals 8 @outputs 2 @rooms 1 '
            '@initwith "/panning/type binaural"'
        ),
        numinlets=4,
        numoutlets=3,
        outlettype=["signal", "signal", ""],
    )
    for index, inlet in enumerate(audio_inputs):
        builder.connect(inlet, 0, spat_renderer, index)
    # Spat5 signal inlets also accept its OSC control messages. Official
    # examples connect spat5.oper to signal inlet zero.
    builder.connect(spat_oper, 0, spat_renderer, 0)
    audio_left = builder.add(
        "outlet",
        [420.0, 750.0, 30.0, 30.0],
        comment="Binaural left",
        index=1,
        numinlets=1,
        numoutlets=0,
    )
    audio_right = builder.add(
        "outlet",
        [490.0, 750.0, 30.0, 30.0],
        comment="Binaural right",
        index=2,
        numinlets=1,
        numoutlets=0,
    )
    builder.connect(spat_renderer, 0, audio_left)
    builder.connect(spat_renderer, 1, audio_right)

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 0,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [80.0, 80.0, 980.0, 820.0],
            "openinpresentation": 0,
            "boxes": builder.boxes,
            "lines": builder.lines,
            "dependency_cache": [
                {"name": "OSC-route.mxo", "type": "iLaX"},
                {"name": "spat5.oper.mxo", "type": "iLaX"},
                {"name": "spat5.spat~.mxo", "type": "iLaX"},
            ],
            "autosave": 0,
        }
    }


def validate_patch(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    texts = {
        entry["box"].get("text", "") for entry in patcher.get("boxes", [])
    }
    required = {
        "r qmw.osc.raw",
        "s qmw.spat.control",
        "s qmw.acoustic.modal.control",
        "OSC-route /resonance /decay /damping",
        "OSC-route /tilt /warp /weights",
    }
    missing = required.difference(texts)
    if missing:
        raise RuntimeError(f"Spat/modal adapter is incomplete: {sorted(missing)}")
    if not any(text.startswith("spat5.oper ") for text in texts):
        raise RuntimeError("Spat/modal adapter has no spat5.oper")
    if not any(text.startswith("spat5.spat~ ") for text in texts):
        raise RuntimeError("Spat/modal adapter has no audio renderer")


def main() -> int:
    payload = build_patch()
    validate_patch(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
