#!/usr/bin/env python3
"""Generate the Max 9 Zeeman Resonator and its quadrature ring-bank voice."""

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
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


def patcher(boxes: list[dict[str, Any]], lines: list[dict[str, Any]], rect: list[float], dependencies: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 5,
            "architecture": "x64",
            "modernui": 1,
        },
        "classnamespace": "box",
        "rect": rect,
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "autosave": 0,
    }
    if dependencies:
        result["dependency_cache"] = dependencies
    return {"patcher": result}


def build_voice() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [20.0, 12.0, 460.0, 20.0], text="QUADRATURE RING VOICE: L=carrier-shift, R=carrier+shift"),
        box("in", "newobj", [20.0, 48.0, 34.0, 22.0], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route", "newobj", [75.0, 48.0, 175.0, 22.0], text="route carrier shift gain", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
        box("carrier_pack", "newobj", [75.0, 84.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("carrier_line", "newobj", [75.0, 116.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("shift_pack", "newobj", [175.0, 84.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("shift_line", "newobj", [175.0, 116.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("gain_pack", "newobj", [275.0, 84.0, 72.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("gain_line", "newobj", [275.0, 116.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("carrier_cos", "newobj", [45.0, 168.0, 105.0, 22.0], text="cycle~ 220. 0.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("carrier_sin", "newobj", [165.0, 168.0, 112.0, 22.0], text="cycle~ 220. 0.25", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mod_cos", "newobj", [45.0, 208.0, 98.0, 22.0], text="cycle~ 40. 0.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("mod_sin", "newobj", [165.0, 208.0, 105.0, 22.0], text="cycle~ 40. 0.25", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ring_cos", "newobj", [60.0, 252.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("ring_sin", "newobj", [180.0, 252.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("lower", "newobj", [80.0, 296.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("upper", "newobj", [190.0, 296.0, 36.0, 22.0], text="-~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("lower_gain", "newobj", [80.0, 340.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("upper_gain", "newobj", [190.0, 340.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("out_l", "newobj", [80.0, 388.0, 48.0, 22.0], text="out~ 1", numinlets=1, numoutlets=0),
        box("out_r", "newobj", [190.0, 388.0, 48.0, 22.0], text="out~ 2", numinlets=1, numoutlets=0),
    ]
    lines = [
        line("in", 0, "route"),
        line("route", 0, "carrier_pack"),
        line("route", 1, "shift_pack"),
        line("route", 2, "gain_pack"),
        line("carrier_pack", 0, "carrier_line"),
        line("shift_pack", 0, "shift_line"),
        line("gain_pack", 0, "gain_line"),
        line("carrier_line", 0, "carrier_cos"),
        line("carrier_line", 0, "carrier_sin"),
        line("shift_line", 0, "mod_cos"),
        line("shift_line", 0, "mod_sin"),
        line("carrier_cos", 0, "ring_cos", 0),
        line("mod_cos", 0, "ring_cos", 1),
        line("carrier_sin", 0, "ring_sin", 0),
        line("mod_sin", 0, "ring_sin", 1),
        line("ring_cos", 0, "lower", 0),
        line("ring_sin", 0, "lower", 1),
        line("ring_cos", 0, "upper", 0),
        line("ring_sin", 0, "upper", 1),
        line("lower", 0, "lower_gain", 0),
        line("upper", 0, "upper_gain", 0),
        line("gain_line", 0, "lower_gain", 1),
        line("gain_line", 0, "upper_gain", 1),
        line("lower_gain", 0, "out_l"),
        line("upper_gain", 0, "out_r"),
    ]
    return patcher(boxes, lines, [100.0, 100.0, 510.0, 450.0])


def build_instrument() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [30.0, 18.0, 720.0, 28.0], text="QMW ZEEMAN RESONATOR — THE TRIPLET BREAKS", fontsize=18.0),
        box("subtitle", "comment", [30.0, 48.0, 920.0, 36.0], text="A quadrature ring-modulator bank. Lower sidebands move left; upper sidebands move right. The optical scale is perceptually magnified while Landé-factor relationships remain intact."),
        box("preset_label", "comment", [30.0, 102.0, 100.0, 20.0], text="transition"),
        box("preset", "umenu", [130.0, 100.0, 190.0, 22.0], items=["normal", ",", "sodium_d1", ",", "sodium_d2"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("preset_prepend", "newobj", [335.0, 100.0, 105.0, 22.0], text="prepend preset", numinlets=1, numoutlets=1, outlettype=[""]),
        box("field_label", "comment", [30.0, 143.0, 100.0, 20.0], text="field B (tesla)"),
        box("field", "flonum", [130.0, 140.0, 90.0, 22.0], minimum=0.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("field_prepend", "newobj", [235.0, 140.0, 90.0, 22.0], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""]),
        box("sweep_open", "message", [340.0, 140.0, 112.0, 22.0], text="0., 5. 12000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("sweep_close", "message", [460.0, 140.0, 112.0, 22.0], text="5., 0. 12000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("sweep_line", "newobj", [585.0, 140.0, 38.0, 22.0], text="line", numinlets=2, numoutlets=1, outlettype=[""]),
        box("spread_label", "comment", [30.0, 183.0, 100.0, 20.0], text="audible Hz/T"),
        box("spread", "flonum", [130.0, 180.0, 90.0, 22.0], minimum=0.0, maximum=1000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("spread_prepend", "newobj", [235.0, 180.0, 98.0, 22.0], text="prepend spread", numinlets=1, numoutlets=1, outlettype=[""]),
        box("carrier_label", "comment", [30.0, 223.0, 100.0, 20.0], text="carrier Hz"),
        box("carrier", "flonum", [130.0, 220.0, 90.0, 22.0], minimum=20.0, maximum=12000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("carrier_prepend", "newobj", [235.0, 220.0, 102.0, 22.0], text="prepend carrier", numinlets=1, numoutlets=1, outlettype=[""]),
        box("bank_label", "comment", [30.0, 263.0, 100.0, 20.0], text="ring-bank level"),
        box("bank", "flonum", [130.0, 260.0, 90.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("bank_prepend", "newobj", [235.0, 260.0, 96.0, 22.0], text="prepend bank", numinlets=1, numoutlets=1, outlettype=[""]),
        box("dry_label", "comment", [30.0, 303.0, 100.0, 20.0], text="pi carrier level"),
        box("dry", "flonum", [130.0, 300.0, 90.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("dry_prepend", "newobj", [235.0, 300.0, 90.0, 22.0], text="prepend dry", numinlets=1, numoutlets=1, outlettype=[""]),
        box("master_label", "comment", [30.0, 343.0, 100.0, 20.0], text="master level"),
        box("master", "flonum", [130.0, 340.0, 90.0, 22.0], minimum=0.0, maximum=0.5, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("master_pack", "newobj", [235.0, 340.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("master_line", "newobj", [320.0, 340.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("controller", "newobj", [30.0, 395.0, 248.0, 22.0], text="js qmw_zeeman_controller_v1.js", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
        box("status", "message", [300.0, 395.0, 720.0, 22.0], text="initializing Zeeman field...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("shift_label", "comment", [30.0, 438.0, 110.0, 20.0], text="sideband shifts"),
        box("shifts", "multislider", [145.0, 435.0, 875.0, 44.0], size=8, setminmax=[0.0, 400.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("gain_label", "comment", [30.0, 492.0, 110.0, 20.0], text="voice amplitudes"),
        box("gains", "multislider", [145.0, 489.0, 875.0, 44.0], size=8, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("poly", "newobj", [30.0, 560.0, 305.0, 22.0], text="poly~ qmw_zeeman_ring_voice_v1 8 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("dry_pack", "newobj", [365.0, 560.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("dry_line", "newobj", [450.0, 560.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("dry_freq_pack", "newobj", [510.0, 560.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("dry_freq_line", "newobj", [595.0, 560.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("dry_cycle", "newobj", [655.0, 560.0, 65.0, 22.0], text="cycle~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("dry_gain", "newobj", [735.0, 560.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_l", "newobj", [145.0, 610.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r", "newobj", [255.0, 610.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_l", "newobj", [145.0, 650.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [255.0, 650.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("clip_l", "newobj", [145.0, 685.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("clip_r", "newobj", [255.0, 685.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [365.0, 620.0, 18.0, 88.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [395.0, 620.0, 18.0, 88.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [445.0, 640.0, 52.0, 52.0], numinlets=2, numoutlets=0),
        box("spatial_note", "comment", [525.0, 622.0, 495.0, 66.0], text="STEREO FIELD\nLEFT  = sigma- / negative-frequency displacement\nRIGHT = sigma+ / positive-frequency displacement\nThe central pi line is equal in both channels."),
        box("init_preset", "newobj", [700.0, 100.0, 104.0, 22.0], text="loadmess normal", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_field", "newobj", [815.0, 100.0, 88.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_spread", "newobj", [915.0, 100.0, 96.0, 22.0], text="loadmess 40.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_carrier", "newobj", [700.0, 140.0, 104.0, 22.0], text="loadmess 220.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_bank", "newobj", [815.0, 140.0, 96.0, 22.0], text="loadmess 0.42", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_dry", "newobj", [915.0, 140.0, 96.0, 22.0], text="loadmess 0.28", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_master", "newobj", [700.0, 180.0, 96.0, 22.0], text="loadmess 0.18", numinlets=1, numoutlets=1, outlettype=[""]),
    ]
    lines = [
        line("preset", 1, "preset_prepend"), line("preset_prepend", 0, "controller"),
        line("field", 0, "field_prepend"), line("field_prepend", 0, "controller"),
        line("sweep_open", 0, "sweep_line"), line("sweep_close", 0, "sweep_line"), line("sweep_line", 0, "field"),
        line("spread", 0, "spread_prepend"), line("spread_prepend", 0, "controller"),
        line("carrier", 0, "carrier_prepend"), line("carrier_prepend", 0, "controller"),
        line("carrier", 0, "dry_freq_pack"), line("dry_freq_pack", 0, "dry_freq_line"), line("dry_freq_line", 0, "dry_cycle"),
        line("bank", 0, "bank_prepend"), line("bank_prepend", 0, "controller"),
        line("dry", 0, "dry_prepend"), line("dry_prepend", 0, "controller"),
        line("master", 0, "master_pack"), line("master_pack", 0, "master_line"),
        line("controller", 0, "poly"), line("controller", 1, "dry_pack"), line("dry_pack", 0, "dry_line"),
        line("controller", 2, "shifts"), line("controller", 3, "gains"), line("controller", 4, "status", 1),
        line("dry_cycle", 0, "dry_gain", 0), line("dry_line", 0, "dry_gain", 1),
        line("poly", 0, "sum_l", 0), line("dry_gain", 0, "sum_l", 1),
        line("poly", 1, "sum_r", 0), line("dry_gain", 0, "sum_r", 1),
        line("sum_l", 0, "master_l", 0), line("master_line", 0, "master_l", 1),
        line("sum_r", 0, "master_r", 0), line("master_line", 0, "master_r", 1),
        line("master_l", 0, "clip_l"), line("master_r", 0, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"),
        line("clip_l", 0, "dac", 0), line("clip_r", 0, "dac", 1),
        line("init_preset", 0, "preset"), line("init_field", 0, "field"), line("init_spread", 0, "spread"),
        line("init_carrier", 0, "carrier"), line("init_bank", 0, "bank"), line("init_dry", 0, "dry"), line("init_master", 0, "master"),
    ]
    dependencies = [
        {"name": "qmw_zeeman_controller_v1.js", "type": "TEXT"},
        {"name": "qmw_zeeman_ring_voice_v1.maxpat", "type": "JSON"},
    ]
    return patcher(boxes, lines, [80.0, 60.0, 1060.0, 760.0], dependencies)


def validate(payload: dict[str, Any], *, expected_poly: bool) -> None:
    data = payload["patcher"]
    identifiers = {entry["box"]["id"] for entry in data["boxes"]}
    if len(identifiers) != len(data["boxes"]):
        raise RuntimeError("duplicate Max box identifiers")
    for entry in data["lines"]:
        source = entry["patchline"]["source"][0]
        destination = entry["patchline"]["destination"][0]
        if source not in identifiers or destination not in identifiers:
            raise RuntimeError(f"dangling patchline {source} -> {destination}")
    texts = {entry["box"].get("text", "") for entry in data["boxes"]}
    if expected_poly and not any(text.startswith("poly~ qmw_zeeman_ring_voice_v1") for text in texts):
        raise RuntimeError("instrument is missing its ring-modulator bank")
    if not expected_poly and not {"*~", "+~", "-~"}.issubset(texts):
        raise RuntimeError("voice is missing quadrature ring-modulation operators")


def main() -> None:
    voice = build_voice()
    instrument = build_instrument()
    validate(voice, expected_poly=False)
    validate(instrument, expected_poly=True)
    (ROOT / "qmw_zeeman_ring_voice_v1.maxpat").write_text(json.dumps(voice, indent=2) + "\n", encoding="utf-8")
    (ROOT / "QMW_Zeeman_Resonator_v1.maxpat").write_text(json.dumps(instrument, indent=2) + "\n", encoding="utf-8")
    print("generated QMW_Zeeman_Resonator_v1.maxpat and qmw_zeeman_ring_voice_v1.maxpat")


if __name__ == "__main__":
    main()
