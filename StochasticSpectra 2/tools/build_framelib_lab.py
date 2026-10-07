#!/usr/bin/env python3
"""Build the optional FrameLib companion instrument as reviewable Max JSON."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "patchers" / "StochasticSpectra_FrameLib_Lab.maxpat"


def box(box_id: str, maxclass: str, rect: list[float], **attributes: object) -> dict:
    payload = {"id": box_id, "maxclass": maxclass, "patching_rect": rect}
    payload.update(attributes)
    return {"box": payload}


def message(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "message", rect, text=text)


def comment(box_id: str, text: str, rect: list[float], fontsize: float = 12.0) -> dict:
    return box(box_id, "comment", rect, text=text, fontsize=fontsize)


def newobj(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "newobj", rect, text=text)


def panel(box_id: str, rect: list[float], color: list[float]) -> dict:
    return box(
        box_id,
        "panel",
        rect,
        background=1,
        bgcolor=color,
        border=1,
        bordercolor=[0.70, 0.72, 0.76, 1.0],
        rounded=10,
    )


def line(
    source: str,
    outlet: int,
    destination: str,
    inlet: int,
    *,
    hidden: bool = False,
    order: int | None = None,
) -> dict:
    payload: dict[str, object] = {
        "source": [source, outlet],
        "destination": [destination, inlet],
    }
    if hidden:
        payload["hidden"] = 1
    if order is not None:
        payload["order"] = order
    return {"patchline": payload}


def build() -> dict:
    boxes = [
        panel("source_panel", [20.0, 85.0, 1160.0, 215.0], [0.91, 0.95, 0.99, 1.0]),
        panel("frame_panel", [20.0, 315.0, 1160.0, 230.0], [0.96, 0.93, 0.99, 1.0]),
        panel("env_panel", [20.0, 560.0, 1160.0, 135.0], [0.99, 0.93, 0.93, 1.0]),
        panel("monitor_panel", [20.0, 710.0, 1160.0, 280.0], [0.91, 0.97, 0.94, 1.0]),
        comment("title", "Stochastic Spectra × FrameLib Lab", [30.0, 17.0, 720.0, 32.0], 22.0),
        comment(
            "subtitle",
            "v0.5.0 companion patch • direct stochastic voice + FrameLib statistical spectral memory • separate packet envelope and explicit *~",
            [32.0, 53.0, 1100.0, 22.0],
        ),
        comment("source_title", "1  CONTINUOUS STOCHASTIC SOURCE", [35.0, 96.0, 390.0, 24.0], 16.0),
        message(
            "morph_preset",
            "modes 24, slope 0., interp 400., slew 20., ampdepth 1., phasedepth 1., evolve 1, next",
            [38.0, 132.0, 760.0, 22.0],
        ),
        comment("morph_label", "AUDIBLE MORPH PRESET", [815.0, 134.0, 190.0, 20.0], 10.0),
        message("evolve_on", "evolve 1", [38.0, 172.0, 88.0, 22.0]),
        message("evolve_off", "evolve 0", [136.0, 172.0, 88.0, 22.0]),
        message("next", "next", [234.0, 172.0, 60.0, 22.0]),
        comment("rate_label", "RATE targets/sec", [314.0, 174.0, 115.0, 20.0]),
        box("rate_value", "flonum", [426.0, 172.0, 70.0, 22.0], minimum=0.01, maximum=100.0),
        newobj("rate_prepend", "prepend rate", [508.0, 172.0, 98.0, 22.0]),
        message("rate_slow", "0.5", [622.0, 172.0, 45.0, 22.0]),
        message("rate_mid", "2.", [677.0, 172.0, 40.0, 22.0]),
        message("rate_fast", "8.", [727.0, 172.0, 40.0, 22.0]),
        newobj("rate_load", "loadmess 2.", [782.0, 172.0, 90.0, 22.0]),
        message("spectral_status", "status", [890.0, 172.0, 66.0, 22.0]),
        newobj("stoch", "stochspectra~", [965.0, 210.0, 135.0, 22.0]),
        comment(
            "source_note",
            "This remains the authoritative continuous voice. FrameLib is an additive analysis/resynthesis branch, not part of the external.",
            [38.0, 246.0, 900.0, 22.0],
        ),
        comment("frame_title", "2  FRAMELIB STATISTICAL SPECTRAL MEMORY", [35.0, 326.0, 520.0, 24.0], 16.0),
        comment(
            "frame_dependency",
            "Requires installed FrameLib 1.0.1. fl-freeze-stoch analyses overlapping FFT frames and regenerates magnitudes/phase deltas statistically.",
            [485.0, 328.0, 675.0, 22.0],
        ),
        box("capture_now", "button", [42.0, 374.0, 24.0, 24.0]),
        comment("capture_now_label", "CAPTURE / UPDATE MODEL", [76.0, 376.0, 190.0, 20.0]),
        box("capture_auto", "toggle", [42.0, 414.0, 24.0, 24.0]),
        comment("capture_auto_label", "AUTO UPDATE", [76.0, 416.0, 100.0, 20.0]),
        newobj("capture_metro", "qmetro 1000", [190.0, 414.0, 90.0, 22.0]),
        box("capture_ms", "number", [293.0, 414.0, 70.0, 22.0], minimum=100, maximum=10000),
        comment("capture_ms_label", "ms", [369.0, 416.0, 28.0, 20.0]),
        newobj("capture_toggle_load", "loadmess 1", [42.0, 450.0, 82.0, 22.0]),
        newobj("capture_ms_load", "loadmess 1000", [135.0, 450.0, 105.0, 22.0]),
        newobj("freeze", "fl-freeze-stoch", [420.0, 405.0, 125.0, 22.0]),
        comment("freeze_note", "FrameLib tutorial abstraction", [409.0, 437.0, 190.0, 18.0], 10.0),
        message("choose_direct", "0 0 1., 1 0 0.", [630.0, 374.0, 145.0, 22.0]),
        comment("choose_direct_label", "DIRECT", [780.0, 376.0, 65.0, 20.0], 10.0),
        message("choose_frame", "0 0 0., 1 0 1.", [630.0, 410.0, 145.0, 22.0]),
        comment("choose_frame_label", "FRAMELIB", [780.0, 412.0, 75.0, 20.0], 10.0),
        newobj("direct_delay", "delay~ 4096 4096", [630.0, 452.0, 125.0, 22.0]),
        newobj("matrix", "matrix~ 2 1 0. @ramp 50", [870.0, 395.0, 175.0, 22.0]),
        newobj("direct_load", "loadmess 0 0 1.", [870.0, 435.0, 130.0, 22.0]),
        comment(
            "frame_note",
            "The direct path is delayed 4096 samples to match FrameLib source latency. The 50 ms matrix ramp avoids hard switching; resynthesis is intentionally not phase-identical.",
            [38.0, 500.0, 1060.0, 22.0],
        ),
        comment("env_title", "3  SEPARATE EVENT ENVELOPE", [35.0, 571.0, 360.0, 24.0], 16.0),
        message("env_off", "mode off", [38.0, 612.0, 82.0, 22.0]),
        message(
            "env_gamma",
            "mode gamma, density 3., shape 2., duration 150., window gaussian, polyphony 16, reset",
            [135.0, 612.0, 690.0, 22.0],
        ),
        message("env_status", "status", [840.0, 612.0, 66.0, 22.0]),
        newobj("env", "stochpacketenv~", [925.0, 612.0, 145.0, 22.0]),
        newobj("multiply", "*~", [1090.0, 612.0, 45.0, 22.0]),
        comment(
            "env_note",
            "FrameLib/direct voice enters the left inlet; stochpacketenv~ amplitude enters the right inlet. Multiplication remains explicit.",
            [38.0, 656.0, 930.0, 22.0],
        ),
        comment("monitor_title", "4  FRAMELIB OBSERVER + AUDIO MONITOR", [35.0, 721.0, 470.0, 24.0], 16.0),
        newobj("analysis_interval", "fl.interval~ 1024", [40.0, 765.0, 110.0, 22.0]),
        newobj("analysis_source", "fl.source~ /length 4096", [165.0, 765.0, 160.0, 22.0]),
        newobj("analysis_window", "fl.window~ hann /compensate linear", [340.0, 765.0, 220.0, 22.0]),
        newobj("analysis_fft", "fl.fft~", [575.0, 765.0, 62.0, 22.0]),
        newobj("analysis_magnitude", "fl.hypot~", [652.0, 765.0, 72.0, 22.0]),
        newobj("centroid", "fl.centroid~", [740.0, 750.0, 88.0, 22.0]),
        newobj("flatness", "fl.flatness~", [740.0, 785.0, 88.0, 22.0]),
        newobj("delta", "fl.framedelta~", [740.0, 820.0, 100.0, 22.0]),
        newobj("delta_rms", "fl.rms~", [855.0, 820.0, 60.0, 22.0]),
        newobj("centroid_to_max", "fl.tomax~", [845.0, 750.0, 70.0, 22.0]),
        newobj("flatness_to_max", "fl.tomax~", [845.0, 785.0, 70.0, 22.0]),
        newobj("delta_to_max", "fl.tomax~", [930.0, 820.0, 70.0, 22.0]),
        box("centroid_value", "flonum", [930.0, 750.0, 72.0, 22.0]),
        box("flatness_value", "flonum", [930.0, 785.0, 72.0, 22.0]),
        box("delta_value", "flonum", [1015.0, 820.0, 72.0, 22.0]),
        comment("centroid_label", "centroid bin", [1010.0, 752.0, 95.0, 20.0], 10.0),
        comment("flatness_label", "flatness", [1010.0, 787.0, 75.0, 20.0], 10.0),
        comment("delta_label", "frame Δ RMS", [1090.0, 822.0, 82.0, 20.0], 10.0),
        newobj("atten", "*~ 0.35", [420.0, 860.0, 75.0, 22.0]),
        box("meter", "meter~", [520.0, 846.0, 18.0, 80.0]),
        box("scope", "scope~", [565.0, 850.0, 235.0, 85.0], range=[-1.0, 1.0]),
        box(
            "spectrogram",
            "spectroscope~",
            [40.0, 895.0, 350.0, 70.0],
            logfreq=1,
            monochrome=0,
            range=[0.0, 1.0],
            scroll=2,
            sono=1,
        ),
        box("dac", "ezdac~", [840.0, 880.0, 45.0, 45.0]),
        comment("dac_note", "Audio starts OFF", [900.0, 894.0, 120.0, 20.0]),
        comment(
            "footer",
            "Observer metrics are read-only and measured before the packet envelope. They do not drive the voice in this first integration slice.",
            [35.0, 1002.0, 1000.0, 22.0],
        ),
    ]

    lines = []
    for control in ("morph_preset", "evolve_on", "evolve_off", "next", "rate_prepend", "spectral_status"):
        lines.append(line(control, 0, "stoch", 0, hidden=True))
    for control in ("env_off", "env_gamma", "env_status"):
        lines.append(line(control, 0, "env", 0, hidden=True))
    lines.extend(
        [
            line("rate_value", 0, "rate_prepend", 0),
            line("rate_slow", 0, "rate_value", 0),
            line("rate_mid", 0, "rate_value", 0),
            line("rate_fast", 0, "rate_value", 0),
            line("rate_load", 0, "rate_value", 0, hidden=True),
            line("stoch", 0, "freeze", 0, order=0),
            line("stoch", 0, "direct_delay", 0, order=1),
            line("direct_delay", 0, "matrix", 0),
            line("capture_now", 0, "freeze", 1),
            line("capture_auto", 0, "capture_metro", 0),
            line("capture_metro", 0, "freeze", 1),
            line("capture_ms", 0, "capture_metro", 1),
            line("capture_toggle_load", 0, "capture_auto", 0, hidden=True),
            line("capture_ms_load", 0, "capture_ms", 0, hidden=True),
            line("freeze", 0, "matrix", 1),
            line("choose_direct", 0, "matrix", 0),
            line("choose_frame", 0, "matrix", 0),
            line("direct_load", 0, "matrix", 0, hidden=True),
            line("matrix", 0, "multiply", 0, order=0),
            line("matrix", 0, "analysis_source", 0, order=1),
            line("env", 0, "multiply", 1),
            line("analysis_interval", 0, "analysis_source", 1),
            line("analysis_source", 0, "analysis_window", 0),
            line("analysis_window", 0, "analysis_fft", 0),
            line("analysis_fft", 0, "analysis_magnitude", 0),
            line("analysis_fft", 1, "analysis_magnitude", 1),
            line("analysis_magnitude", 0, "centroid", 0, order=0),
            line("analysis_magnitude", 0, "flatness", 0, order=1),
            line("analysis_magnitude", 0, "delta", 0, order=2),
            line("delta", 0, "delta_rms", 0),
            line("centroid", 0, "centroid_to_max", 0),
            line("flatness", 0, "flatness_to_max", 0),
            line("delta_rms", 0, "delta_to_max", 0),
            line("centroid_to_max", 0, "centroid_value", 0),
            line("flatness_to_max", 0, "flatness_value", 0),
            line("delta_to_max", 0, "delta_value", 0),
            line("multiply", 0, "atten", 0),
            line("atten", 0, "meter", 0, order=0),
            line("atten", 0, "scope", 0, order=1),
            line("atten", 0, "spectrogram", 0, order=2),
            line("atten", 0, "dac", 0, order=3),
            line("atten", 0, "dac", 1, order=4),
        ]
    )

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [45.0, 30.0, 1210.0, 1050.0],
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
            "description": "FrameLib statistical spectral-memory companion for Stochastic Spectra.",
            "digest": "Direct and FrameLib-resynthesized stochastic voices through a separate packet envelope.",
            "tags": "FrameLib stochastic spectral freeze wavetable envelope analysis",
            "boxes": boxes,
            "lines": lines,
        }
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
