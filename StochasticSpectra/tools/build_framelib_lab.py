#!/usr/bin/env python3
"""Build the deliberately simple FrameLib companion instrument."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "patchers" / "StochasticSpectra_FrameLib_Lab.maxpat"


def box(box_id: str, maxclass: str, rect: list[float], **attrs: object) -> dict:
    data = {"id": box_id, "maxclass": maxclass, "patching_rect": rect}
    data.update(attrs)
    return {"box": data}


def newobj(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "newobj", rect, text=text)


def message(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "message", rect, text=text)


def comment(box_id: str, text: str, rect: list[float], size: float = 12.0) -> dict:
    return box(box_id, "comment", rect, text=text, fontsize=size)


def panel(box_id: str, rect: list[float], color: list[float]) -> dict:
    return box(box_id, "panel", rect, background=1, bgcolor=color, border=1,
               bordercolor=[0.70, 0.72, 0.76, 1.0], rounded=10)


def line(source: str, outlet: int, destination: str, inlet: int, *, hidden: bool = False, order: int | None = None) -> dict:
    data: dict[str, object] = {"source": [source, outlet], "destination": [destination, inlet]}
    if hidden:
        data["hidden"] = 1
    if order is not None:
        data["order"] = order
    return {"patchline": data}


def build() -> dict:
    boxes = [
        panel("source_panel", [20.0, 92.0, 960.0, 175.0], [0.91, 0.95, 0.99, 1.0]),
        panel("frame_panel", [20.0, 282.0, 960.0, 175.0], [0.96, 0.93, 0.99, 1.0]),
        panel("env_panel", [20.0, 472.0, 960.0, 125.0], [0.99, 0.93, 0.93, 1.0]),
        panel("monitor_panel", [20.0, 612.0, 960.0, 225.0], [0.91, 0.97, 0.94, 1.0]),
        comment("title", "Stochastic Spectra + FrameLib — Simple Instrument", [28.0, 17.0, 720.0, 32.0], 22.0),
        comment("subtitle", "Four controls only: AUDIO, RATE, VOICE, and ENVELOPE", [30.0, 53.0, 690.0, 24.0], 13.0),
        comment("audio_instruction", "1  CLICK AUDIO", [785.0, 22.0, 145.0, 24.0], 15.0),
        box("dac", "ezdac~", [925.0, 18.0, 45.0, 45.0]),

        comment("source_title", "2  SOURCE — fundamental pitch and stochastic morph rate", [35.0, 103.0, 720.0, 24.0], 15.0),
        comment("source_note", "FUNDAMENTAL changes pitch. RATE changes how often a new spectrum is chosen; evolution is already ON.", [38.0, 135.0, 730.0, 22.0]),
        box("rate_value", "flonum", [45.0, 180.0, 75.0, 24.0], minimum=0.01, maximum=100.0),
        newobj("rate_prepend", "prepend rate", [132.0, 181.0, 100.0, 22.0]),
        message("rate_slow", "0.5", [250.0, 181.0, 48.0, 22.0]),
        message("rate_mid", "2.", [308.0, 181.0, 42.0, 22.0]),
        message("rate_fast", "8.", [360.0, 181.0, 42.0, 22.0]),
        message("next", "next", [425.0, 181.0, 55.0, 22.0]),
        comment("freq_label", "FUNDAMENTAL Hz", [45.0, 225.0, 125.0, 20.0], 11.0),
        box("freq_value", "flonum", [170.0, 222.0, 75.0, 24.0], minimum=1.0, maximum=20000.0),
        newobj("freq_prepend", "prepend freq", [257.0, 223.0, 100.0, 22.0]),
        message("freq_55", "55.", [375.0, 223.0, 45.0, 22.0]),
        message("freq_110", "110.", [430.0, 223.0, 50.0, 22.0]),
        message("freq_220", "220.", [490.0, 223.0, 50.0, 22.0]),
        newobj("freq_load", "loadmess 55.", [555.0, 223.0, 100.0, 22.0]),
        message("morph_preset", "gain 0.2, modes 24, slope 0., interp 400., slew 20., ampdepth 1., phasedepth 1., evolve 1, next", [675.0, 223.0, 130.0, 22.0]),
        comment("preset_label", "RESET EVOLUTION", [815.0, 225.0, 135.0, 20.0], 10.0),
        newobj("stoch", "stochspectra~", [820.0, 181.0, 135.0, 22.0]),
        newobj("preset_load", "loadbang", [700.0, 181.0, 72.0, 22.0]),
        newobj("rate_load", "loadmess 2.", [510.0, 181.0, 90.0, 22.0]),

        comment("frame_title", "3  VOICE — direct stochastic source or FrameLib spectral memory", [35.0, 293.0, 680.0, 24.0], 15.0),
        comment("frame_note", "With AUDIO on, click CAPTURE once; then set VOICE to 1. Set it back to 0 for the direct source.", [38.0, 325.0, 745.0, 22.0]),
        box("capture_now", "button", [48.0, 369.0, 28.0, 28.0]),
        comment("capture_label", "CAPTURE", [84.0, 373.0, 78.0, 20.0], 11.0),
        box("voice_toggle", "toggle", [205.0, 369.0, 28.0, 28.0]),
        comment("voice_label", "VOICE: 0 DIRECT / 1 FRAMELIB", [242.0, 373.0, 240.0, 20.0], 11.0),
        newobj("voice_select", "sel 0 1", [205.0, 412.0, 70.0, 22.0]),
        message("choose_direct", "0 0 1., 1 0 0.", [300.0, 412.0, 145.0, 22.0]),
        message("choose_frame", "0 0 0., 1 0 1.", [460.0, 412.0, 145.0, 22.0]),
        newobj("voice_load", "loadmess 0", [625.0, 412.0, 85.0, 22.0]),
        newobj("direct_delay", "delay~ 4096 4096", [510.0, 369.0, 125.0, 22.0]),
        newobj("freeze", "fl-freeze-stoch", [660.0, 369.0, 125.0, 22.0]),
        newobj("matrix", "matrix~ 2 1 0. @ramp 50", [800.0, 369.0, 165.0, 22.0]),

        comment("env_title", "4  ENVELOPE — continuous sound or gamma-renewal packets", [35.0, 483.0, 620.0, 24.0], 15.0),
        box("env_toggle", "toggle", [48.0, 533.0, 28.0, 28.0]),
        comment("env_label", "ENVELOPE: 0 CONTINUOUS / 1 GAMMA", [86.0, 537.0, 270.0, 20.0], 11.0),
        newobj("env_select", "sel 0 1", [375.0, 534.0, 70.0, 22.0]),
        message("env_off", "mode off", [465.0, 534.0, 82.0, 22.0]),
        message("env_gamma", "mode gamma, density 3., shape 2., duration 150., reset", [560.0, 534.0, 365.0, 22.0]),
        newobj("env_load", "loadmess 0", [375.0, 567.0, 85.0, 22.0]),
        newobj("env", "stochpacketenv~", [790.0, 567.0, 145.0, 22.0]),
        newobj("multiply", "*~", [935.0, 534.0, 38.0, 22.0]),

        comment("monitor_title", "OUTPUT — selected voice × separate envelope", [35.0, 623.0, 480.0, 24.0], 15.0),
        newobj("atten", "*~ 0.5", [430.0, 658.0, 70.0, 22.0]),
        box("meter", "meter~", [525.0, 650.0, 18.0, 92.0]),
        box("scope", "scope~", [570.0, 650.0, 380.0, 90.0], range=[-1.0, 1.0]),
        comment("spectrogram_label", "SCROLLING SPECTROGRAM", [38.0, 665.0, 220.0, 20.0], 10.0),
        box("spectrogram", "spectroscope~", [38.0, 690.0, 365.0, 110.0], logfreq=1, monochrome=0, range=[0.0, 1.0], scroll=2, sono=1),
        comment("footer", "If either custom object is orange, Max has not loaded the external and controls cannot work.", [35.0, 805.0, 770.0, 22.0]),
    ]

    lines = [
        line("preset_load", 0, "morph_preset", 0, hidden=True),
        line("morph_preset", 0, "stoch", 0, hidden=True),
        line("rate_value", 0, "rate_prepend", 0),
        line("rate_prepend", 0, "stoch", 0, hidden=True),
        line("rate_slow", 0, "rate_value", 0),
        line("rate_mid", 0, "rate_value", 0),
        line("rate_fast", 0, "rate_value", 0),
        line("rate_load", 0, "rate_value", 0, hidden=True),
        line("next", 0, "stoch", 0, hidden=True),
        line("freq_value", 0, "freq_prepend", 0),
        line("freq_prepend", 0, "stoch", 0, hidden=True),
        line("freq_55", 0, "freq_value", 0),
        line("freq_110", 0, "freq_value", 0),
        line("freq_220", 0, "freq_value", 0),
        line("freq_load", 0, "freq_value", 0, hidden=True),
        line("stoch", 0, "direct_delay", 0, order=0),
        line("stoch", 0, "freeze", 0, order=1),
        line("direct_delay", 0, "matrix", 0),
        line("freeze", 0, "matrix", 1),
        line("capture_now", 0, "freeze", 1),
        line("voice_toggle", 0, "voice_select", 0),
        line("voice_select", 0, "choose_direct", 0),
        line("voice_select", 1, "choose_frame", 0),
        line("choose_direct", 0, "matrix", 0),
        line("choose_frame", 0, "matrix", 0),
        line("voice_load", 0, "voice_toggle", 0, hidden=True),
        line("matrix", 0, "multiply", 0),
        line("env_toggle", 0, "env_select", 0),
        line("env_select", 0, "env_off", 0),
        line("env_select", 1, "env_gamma", 0),
        line("env_off", 0, "env", 0, hidden=True),
        line("env_gamma", 0, "env", 0, hidden=True),
        line("env_load", 0, "env_toggle", 0, hidden=True),
        line("env", 0, "multiply", 1),
        line("multiply", 0, "atten", 0),
        line("atten", 0, "meter", 0, order=0),
        line("atten", 0, "scope", 0, order=1),
        line("atten", 0, "spectrogram", 0, order=2),
        line("atten", 0, "dac", 0, order=3),
        line("atten", 0, "dac", 1, order=4),
    ]

    return {"patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [60.0, 40.0, 1005.0, 865.0],
        "bglocked": 0,
        "openinpresentation": 0,
        "default_fontname": "Arial",
        "default_fontsize": 12.0,
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "gridsnaponopen": 1,
        "objectsnaponopen": 1,
        "statusbarvisible": 2,
        "toolbarvisible": 1,
        "description": "Simple direct/FrameLib stochastic voice with a separate packet envelope.",
        "digest": "Four visible controls: audio, morph rate, voice selection, and envelope mode.",
        "tags": "FrameLib stochastic wavetable envelope spectrogram",
        "boxes": boxes,
        "lines": lines,
    }}


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
