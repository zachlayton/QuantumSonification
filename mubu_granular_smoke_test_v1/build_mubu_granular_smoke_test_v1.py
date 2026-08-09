#!/usr/bin/env python3
"""Build a minimal, known-source MuBu granular audio smoke test."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def build() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [25.0, 15.0, 720.0, 28.0], text="QMW MuBu GRANULAR AUDIO SMOKE TEST v1", fontsize=18.0),
        box("purpose", "comment", [25.0, 48.0, 760.0, 38.0], text="Known-good Max file → same-named buffer~/MuBu container → mubu.granular~ → stereo output. No atlas, scheduler, MC, or corpus."),

        # This is the exact source/container relationship used by MuBu's help patch.
        box("reload", "message", [25.0, 105.0, 145.0, 22.0], text="replace cherokee.aif", numinlets=2, numoutlets=1, outlettype=[""]),
        box("autoload", "newobj", [180.0, 105.0, 180.0, 22.0], text="loadmess replace cherokee.aif", numinlets=1, numoutlets=1, outlettype=[""]),
        box("source", "newobj", [25.0, 140.0, 235.0, 22.0], text="buffer~ qmw_mubu_audio_test", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("length_label", "comment", [275.0, 142.0, 90.0, 20.0], text="length (ms)"),
        box("length", "flonum", [365.0, 140.0, 80.0, 22.0], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("ready", "newobj", [460.0, 140.0, 42.0, 22.0], text="t b b", numinlets=1, numoutlets=2, outlettype=["bang", "bang"]),
        box("status", "message", [515.0, 140.0, 285.0, 22.0], text="waiting for cherokee.aif...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("status_set", "message", [515.0, 105.0, 285.0, 22.0], text="set AUDIO LOADED — MuBu should now play", numinlets=2, numoutlets=1, outlettype=[""]),
        box("source_container", "imubu", [25.0, 180.0, 775.0, 150.0], name="qmw_mubu_audio_test", numinlets=1, numoutlets=1, outlettype=[""], embed=0, autobounds=0, autoupdate=250.0, autorefreshrate=1, toolbar_visible=2, tabs_visible=1, bufferchooser_visible=0, domain_bounds=[0.0, 3000.0], domainruler_visible=1, domainscrollbar_visible=1, tool="cursor"),

        box("engine_label", "comment", [25.0, 350.0, 440.0, 22.0], text="ONE MuBu ENGINE — stereo, stock file, explicit level 100", fontsize=14.0),
        box("engine", "newobj", [25.0, 382.0, 755.0, 28.0], text="mubu.granular~ 2 qmw_mubu_audio_test @play 0 @period 180 @position 900 @positionvar 80 @duration 300 @level 100 @duplicatechannels 1 @outputposition 1", numinlets=1, numoutlets=3, outlettype=["signal", "signal", ""]),
        box("ready_delay", "newobj", [25.0, 425.0, 65.0, 22.0], text="delay 50", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("config", "message", [100.0, 425.0, 680.0, 35.0], text="position 900, positionvar 80, duration 300, durationvar 60, resampling 0, resamplingvar 120, level 100, levelvar 0, window cosine, duplicatechannels 1, play 1", numinlets=2, numoutlets=1, outlettype=[""]),

        box("manual_label", "comment", [25.0, 480.0, 112.0, 20.0], text="manual grain"),
        box("manual", "button", [140.0, 477.0, 26.0, 26.0], numinlets=1, numoutlets=1, outlettype=["bang"]),
        box("play_label", "comment", [195.0, 480.0, 75.0, 20.0], text="auto play"),
        box("play", "toggle", [270.0, 477.0, 26.0, 26.0], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("play_pre", "newobj", [306.0, 479.0, 82.0, 22.0], text="prepend play", numinlets=1, numoutlets=1, outlettype=[""]),
        box("metadata", "message", [415.0, 479.0, 365.0, 22.0], text="grain position / duration metadata", numinlets=2, numoutlets=1, outlettype=[""]),

        box("gain_l", "newobj", [145.0, 535.0, 58.0, 22.0], text="*~ 0.18", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_r", "newobj", [285.0, 535.0, 58.0, 22.0], text="*~ 0.18", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [215.0, 525.0, 18.0, 65.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [355.0, 525.0, 18.0, 65.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [430.0, 525.0, 55.0, 55.0], numinlets=2, numoutlets=0),
        box("instruction", "comment", [505.0, 526.0, 295.0, 54.0], text="CLICK THE SPEAKER TO ENABLE DSP.\nMeters should move continuously; press manual grain for an immediate trigger.", fontsize=13.0),
        box("init_play", "newobj", [25.0, 535.0, 75.0, 22.0], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
    ]

    lines = [
        line("reload", 0, "source"), line("autoload", 0, "source"),
        line("source", 0, "length"), line("source", 1, "ready"),
        line("ready", 1, "status_set"), line("status_set", 0, "status", 1),
        line("ready", 0, "ready_delay"), line("ready_delay", 0, "config"), line("config", 0, "engine"),
        line("manual", 0, "engine"), line("play", 0, "play_pre"), line("play_pre", 0, "engine"),
        line("engine", 2, "metadata", 1),
        line("engine", 0, "gain_l"), line("engine", 1, "gain_r"),
        line("gain_l", 0, "meter_l"), line("gain_r", 0, "meter_r"),
        line("gain_l", 0, "dac", 0), line("gain_r", 0, "dac", 1),
        line("init_play", 0, "play"),
    ]

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [60.0, 60.0, 840.0, 650.0],
            "gridsize": [15.0, 15.0],
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {"name": "mubu.granular~.mxo", "type": "iLaX"},
                {"name": "imubu.mxo", "type": "iLaX"},
            ],
            "autosave": 0,
        }
    }


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    order = [entry["box"]["id"] for entry in patcher["boxes"]]
    if len(boxes) != len(patcher["boxes"]):
        raise RuntimeError("duplicate box id")
    if not order.index("source") < order.index("source_container") < order.index("engine"):
        raise RuntimeError("MuBu source must construct as buffer~, container, then engine")
    if not boxes["engine"]["text"].startswith("mubu.granular~ 2 qmw_mubu_audio_test"):
        raise RuntimeError("missing stereo MuBu granular engine")
    connections = {
        (entry["patchline"]["source"][0], entry["patchline"]["source"][1],
         entry["patchline"]["destination"][0], entry["patchline"]["destination"][1])
        for entry in patcher["lines"]
    }
    required = {
        ("source", 1, "ready", 0), ("config", 0, "engine", 0),
        ("engine", 0, "gain_l", 0), ("engine", 1, "gain_r", 0),
        ("gain_l", 0, "dac", 0), ("gain_r", 0, "dac", 1),
    }
    if required - connections:
        raise RuntimeError(f"missing connection(s): {sorted(required - connections)}")


def main() -> None:
    payload = build()
    validate(payload)
    output = ROOT / "QMW_MuBu_Granular_Audio_Test_v1.maxpat"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")


if __name__ == "__main__":
    main()
