#!/usr/bin/env python3
"""Build the shared modular Max help patch from a reviewable object graph."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [
    ROOT / "help" / "stochspectra~.maxhelp",
    ROOT / "help" / "stochpacketenv~.maxhelp",
]


def box(box_id: str, maxclass: str, rect: list[float], **attributes: object) -> dict:
    payload = {
        "id": box_id,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    payload.update(attributes)
    return {"box": payload}


def message(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "message", rect, text=text)


def comment(
    box_id: str,
    text: str,
    rect: list[float],
    *,
    fontsize: float = 12.0,
    textcolor: list[float] | None = None,
) -> dict:
    attributes: dict[str, object] = {"text": text, "fontsize": fontsize}
    if textcolor is not None:
        attributes["textcolor"] = textcolor
    return box(box_id, "comment", rect, **attributes)


def newobj(box_id: str, text: str, rect: list[float]) -> dict:
    return box(box_id, "newobj", rect, text=text)


def patchline(
    source: str,
    source_outlet: int,
    destination: str,
    destination_inlet: int,
    *,
    hidden: bool = False,
    order: int | None = None,
) -> dict:
    payload: dict[str, object] = {
        "source": [source, source_outlet],
        "destination": [destination, destination_inlet],
    }
    if hidden:
        payload["hidden"] = 1
    if order is not None:
        payload["order"] = order
    return {"patchline": payload}


def panel(box_id: str, rect: list[float], color: list[float]) -> dict:
    return box(
        box_id,
        "panel",
        rect,
        background=1,
        bgcolor=color,
        border=1,
        bordercolor=[0.72, 0.74, 0.78, 1.0],
        rounded=10,
    )


def build() -> dict:
    boxes = [
        panel("panel_setup", [20.0, 92.0, 1120.0, 185.0], [0.91, 0.95, 0.99, 1.0]),
        panel("panel_listen", [20.0, 292.0, 1120.0, 205.0], [0.91, 0.97, 0.94, 1.0]),
        panel("panel_evolve", [20.0, 512.0, 1120.0, 210.0], [0.96, 0.93, 0.99, 1.0]),
        panel("panel_rhythm", [20.0, 737.0, 1120.0, 245.0], [0.99, 0.93, 0.93, 1.0]),
        panel("panel_buffer", [20.0, 997.0, 1120.0, 130.0], [0.99, 0.96, 0.90, 1.0]),
        panel("panel_spectrogram", [20.0, 1142.0, 1120.0, 190.0], [0.91, 0.94, 0.98, 1.0]),
        comment(
            "title",
            "stochspectra~ — stochastic wavetable and modal synthesis",
            [28.0, 18.0, 980.0, 32.0],
            fontsize=22.0,
            textcolor=[0.10, 0.18, 0.28, 1.0],
        ),
        comment(
            "subtitle",
            "v0.5.0 • Audible stochastic morph preset, adjustable target rate, separate envelope, and click-free controls. Audio is OFF on load.",
            [30.0, 54.0, 1060.0, 24.0],
            fontsize=12.0,
        ),
        comment("setup_title", "1  SETUP + MODAL BEHAVIOR", [35.0, 103.0, 380.0, 24.0], fontsize=16.0),
        comment(
            "setup_note",
            "Parameter changes rebuild/reset the shared state unless noted. gain applies inside the external to both outlets.",
            [410.0, 105.0, 700.0, 22.0],
        ),
        message("freq", "freq 55", [38.0, 143.0, 82.0, 22.0]),
        message("freq110", "freq 110", [130.0, 143.0, 88.0, 22.0]),
        message("modes", "modes 16", [228.0, 143.0, 92.0, 22.0]),
        message("slope", "slope 2", [330.0, 143.0, 82.0, 22.0]),
        message("slope05", "slope 0.5", [422.0, 143.0, 92.0, 22.0]),
        message("seed", "seed 1701", [524.0, 143.0, 105.0, 22.0]),
        message("gain", "gain 0.15", [639.0, 143.0, 100.0, 22.0]),
        message("gain_low", "gain 0.03", [749.0, 143.0, 100.0, 22.0]),
        message("reset", "reset", [859.0, 143.0, 65.0, 22.0]),
        comment("modal_label", "Modal outlet:", [38.0, 190.0, 92.0, 22.0]),
        message("motion0", "motion 0", [142.0, 188.0, 92.0, 22.0]),
        message("motion1", "motion 1", [246.0, 188.0, 92.0, 22.0]),
        message("motion2", "motion 2", [350.0, 188.0, 92.0, 22.0]),
        message("tau15", "tau 1.5", [467.0, 188.0, 92.0, 22.0]),
        message("tau04", "tau 0.4", [571.0, 188.0, 92.0, 22.0]),
        message("tau002", "tau 0.02", [675.0, 188.0, 98.0, 22.0]),
        comment(
            "motion_note",
            "motion 0 = undamped hold   •   motion 1 = free decay   •   motion 2 = stationary stochastic excitation   •   tau = correlation/decay time",
            [38.0, 226.0, 970.0, 22.0],
        ),
        newobj("stoch", "stochspectra~", [940.0, 170.0, 135.0, 22.0]),
        comment("stoch_note", "compiled external", [946.0, 198.0, 128.0, 22.0]),
        message("status", "status", [986.0, 228.0, 72.0, 22.0]),
        comment("listen_title", "2  LISTEN + COMPARE", [35.0, 303.0, 310.0, 24.0], fontsize=16.0),
        comment(
            "listen_note",
            "A/B the two renderers through one identical monitor path. The extra ×0.35 attenuation is deliberate.",
            [350.0, 305.0, 720.0, 22.0],
        ),
        message("select_table", "1", [50.0, 345.0, 36.0, 22.0]),
        comment("table_label", "VOICE / continuous", [94.0, 346.0, 180.0, 22.0]),
        message("select_packet", "2", [50.0, 382.0, 36.0, 22.0]),
        comment("packet_label", "VOICE * ENVELOPE", [94.0, 383.0, 180.0, 22.0]),
        message("select_modal", "3", [50.0, 419.0, 36.0, 22.0]),
        comment("modal_out_label", "MODAL / rotating bank", [94.0, 420.0, 185.0, 22.0]),
        newobj("select", "selector~ 3", [290.0, 371.0, 98.0, 22.0]),
        newobj("load_select", "loadmess 1", [290.0, 408.0, 90.0, 22.0]),
        newobj("multiply", "*~", [395.0, 342.0, 45.0, 22.0]),
        comment("multiply_note", "voice × envelope", [385.0, 318.0, 120.0, 18.0], fontsize=10.0),
        newobj("atten", "*~ 0.35", [420.0, 371.0, 76.0, 22.0]),
        box("meter", "meter~", [520.0, 344.0, 18.0, 90.0]),
        comment("scope_label", "WAVEFORM", [570.0, 326.0, 150.0, 18.0], fontsize=10.0),
        box("scope", "scope~", [570.0, 342.0, 235.0, 102.0], range=[-1.0, 1.0]),
        comment("spectrum_label", "INSTANTANEOUS SPECTRUM", [825.0, 326.0, 220.0, 18.0], fontsize=10.0),
        box("spectrum", "spectroscope~", [825.0, 342.0, 275.0, 102.0], logfreq=1, range=[0.0, 1.0]),
        box("dac", "ezdac~", [433.0, 430.0, 45.0, 45.0]),
        comment("dac_note", "Click to enable/disable DSP", [490.0, 447.0, 210.0, 22.0]),
        comment(
            "evolve_title",
            "3  EVOLVING STOCHASTIC WAVETABLE — select VOICE, enable DSP, click the preset, then vary RATE",
            [35.0, 523.0, 970.0, 24.0],
            fontsize=16.0,
        ),
        message(
            "evolve_preset",
            "modes 24, slope 0., interp 400., slew 20., ampdepth 1., phasedepth 1., evolve 1, next",
            [38.0, 558.0, 770.0, 22.0],
        ),
        comment("evolve_preset_label", "AUDIBLE MORPH PRESET", [825.0, 560.0, 200.0, 22.0], fontsize=10.0),
        message("evolve_on", "evolve 1", [38.0, 602.0, 92.0, 22.0]),
        message("evolve_off", "evolve 0", [142.0, 602.0, 92.0, 22.0]),
        message("next", "next", [246.0, 602.0, 68.0, 22.0]),
        comment("rate_label", "RATE / targets per sec", [326.0, 604.0, 145.0, 22.0]),
        box("rate_value", "flonum", [470.0, 602.0, 72.0, 22.0], minimum=0.01, maximum=100.0),
        newobj("rate", "prepend rate", [554.0, 602.0, 100.0, 22.0]),
        message("rate_slow", "0.5", [670.0, 602.0, 48.0, 22.0]),
        message("rate_mid", "2.", [728.0, 602.0, 42.0, 22.0]),
        message("rate_fast", "8.", [780.0, 602.0, 42.0, 22.0]),
        comment("rate_presets_label", "slow / medium / fast", [832.0, 604.0, 150.0, 22.0], fontsize=10.0),
        newobj("rate_load", "loadmess 2.", [996.0, 602.0, 94.0, 22.0]),
        message("interp30", "interp 30.", [38.0, 641.0, 96.0, 22.0]),
        message("interp400", "interp 400.", [146.0, 641.0, 102.0, 22.0]),
        message("slew5", "slew 5.", [260.0, 641.0, 82.0, 22.0]),
        message("slew250", "slew 250.", [354.0, 641.0, 96.0, 22.0]),
        message("linear", "curve 0", [462.0, 641.0, 82.0, 22.0]),
        message("smooth", "curve 1", [556.0, 641.0, 82.0, 22.0]),
        message("ampdepth", "ampdepth 1.", [670.0, 641.0, 112.0, 22.0]),
        message("phasedepth", "phasedepth 1.", [794.0, 641.0, 125.0, 22.0]),
        comment(
            "evolve_note",
            "RATE = new stochastic targets per second, not ramp time   •   interp = travel time (ms)   •   slew = extra smoothing   •   NEXT forces one target now",
            [38.0, 683.0, 1030.0, 22.0],
        ),
        comment(
            "rhythm_title",
            "4  SEPARATE PACKET ENVELOPE — select VOICE * ENVELOPE; harmonic centers stay fixed",
            [35.0, 748.0, 970.0, 24.0],
            fontsize=16.0,
        ),
        message(
            "gamma_clustered",
            "mode gamma, density 3., shape 0.5, duration 150., window gaussian, polyphony 16, reset",
            [38.0, 786.0, 875.0, 22.0],
        ),
        comment("gamma_clustered_label", "CLUSTERED / GAPS", [930.0, 788.0, 160.0, 22.0], fontsize=10.0),
        message(
            "gamma_poisson",
            "mode gamma, density 3., shape 1., duration 150., window gaussian, polyphony 16, reset",
            [38.0, 820.0, 875.0, 22.0],
        ),
        comment("gamma_poisson_label", "POISSON", [930.0, 822.0, 120.0, 22.0], fontsize=10.0),
        message(
            "gamma_regular",
            "mode gamma, density 3., shape 4., duration 150., window gaussian, polyphony 16, reset",
            [38.0, 854.0, 875.0, 22.0],
        ),
        comment("gamma_regular_label", "MORE REGULAR", [930.0, 856.0, 140.0, 22.0], fontsize=10.0),
        message("envelope_off", "mode off", [38.0, 894.0, 92.0, 22.0]),
        message("envelope_external", "mode external", [142.0, 894.0, 118.0, 22.0]),
        message("envelope_trigger", "trigger", [272.0, 894.0, 76.0, 22.0]),
        message("duration", "duration 150.", [360.0, 894.0, 116.0, 22.0]),
        message("polyphony", "polyphony 16", [488.0, 894.0, 116.0, 22.0]),
        newobj("env", "stochpacketenv~", [730.0, 894.0, 150.0, 22.0]),
        message("env_status", "status", [892.0, 894.0, 70.0, 22.0]),
        comment(
            "rhythm_note",
            "stochspectra~ makes the voice   •   stochpacketenv~ makes only amplitude   •   *~ performs the multiplication   •   external mode accepts triggers",
            [38.0, 938.0, 1060.0, 22.0],
        ),
        comment("buffer_title", "5  EXPORT THE STATIC BASE CYCLE", [35.0, 1008.0, 390.0, 24.0], fontsize=16.0),
        comment(
            "buffer_note",
            "tobuffer copies the original unscaled 8192-sample cycle, not a snapshot of the evolving output.",
            [410.0, 1010.0, 690.0, 22.0],
        ),
        newobj("buffer_size", "loadmess sizeinsamps 8192", [38.0, 1055.0, 202.0, 22.0]),
        message("to_buffer", "tobuffer stochcycle", [255.0, 1055.0, 160.0, 22.0]),
        newobj("buffer", "buffer~ stochcycle", [430.0, 1055.0, 142.0, 22.0]),
        box("waveform", "waveform~", [600.0, 1045.0, 505.0, 62.0], buffername="stochcycle"),
        comment(
            "spectrogram_title",
            "6  LIVE SPECTROGRAM — spectral evolution through time",
            [35.0, 1153.0, 530.0, 24.0],
            fontsize=16.0,
        ),
        comment(
            "spectrogram_note",
            "Max calls this sonogram mode: time runs horizontally, frequency vertically, and color shows amplitude.",
            [555.0, 1155.0, 555.0, 22.0],
        ),
        box(
            "spectrogram",
            "spectroscope~",
            [38.0, 1187.0, 1065.0, 120.0],
            logfreq=1,
            monochrome=0,
            range=[0.0, 1.0],
            scroll=2,
            sono=1,
        ),
        comment(
            "footer",
            "Parameter snapshots crossfade for 20 ms. Envelope bypass outputs unity; overlapping gamma/external windows can exceed 1.",
            [30.0, 1343.0, 1080.0, 22.0],
            textcolor=[0.42, 0.18, 0.12, 1.0],
        ),
    ]

    spectral_controls = [
        "freq",
        "freq110",
        "modes",
        "slope",
        "slope05",
        "seed",
        "gain",
        "gain_low",
        "reset",
        "motion0",
        "motion1",
        "motion2",
        "tau15",
        "tau04",
        "tau002",
        "evolve_preset",
        "evolve_on",
        "evolve_off",
        "next",
        "rate",
        "ampdepth",
        "phasedepth",
        "interp30",
        "interp400",
        "slew5",
        "slew250",
        "linear",
        "smooth",
        "status",
        "to_buffer",
    ]
    envelope_controls = [
        "gamma_clustered",
        "gamma_poisson",
        "gamma_regular",
        "envelope_off",
        "envelope_external",
        "envelope_trigger",
        "duration",
        "polyphony",
        "env_status",
    ]
    lines = [patchline(control, 0, "stoch", 0, hidden=True) for control in spectral_controls]
    lines.extend(patchline(control, 0, "env", 0, hidden=True) for control in envelope_controls)
    lines.extend(
        [
            patchline("rate_value", 0, "rate", 0),
            patchline("rate_load", 0, "rate_value", 0, hidden=True),
            patchline("rate_slow", 0, "rate_value", 0),
            patchline("rate_mid", 0, "rate_value", 0),
            patchline("rate_fast", 0, "rate_value", 0),
            patchline("stoch", 0, "select", 1),
            patchline("stoch", 0, "multiply", 0),
            patchline("env", 0, "multiply", 1),
            patchline("multiply", 0, "select", 2),
            patchline("stoch", 1, "select", 3),
            patchline("select_table", 0, "select", 0),
            patchline("select_packet", 0, "select", 0),
            patchline("select_modal", 0, "select", 0),
            patchline("load_select", 0, "select", 0, hidden=True),
            patchline("select", 0, "atten", 0),
            patchline("atten", 0, "meter", 0, order=0),
            patchline("atten", 0, "scope", 0, order=1),
            patchline("atten", 0, "spectrum", 0, order=2),
            patchline("atten", 0, "spectrogram", 0, order=3),
            patchline("atten", 0, "dac", 0, order=4),
            patchline("atten", 0, "dac", 1, order=5),
            patchline("buffer_size", 0, "buffer", 0),
        ]
    )

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 5,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [70.0, 50.0, 1165.0, 1395.0],
            "bglocked": 0,
            "openinpresentation": 0,
            "default_fontname": "Arial",
            "default_fontsize": 12.0,
            "default_fontface": 0,
            "default_fontcolor": [0.12, 0.12, 0.14, 1.0],
            "gridonopen": 1,
            "gridsize": [15.0, 15.0],
            "gridsnaponopen": 1,
            "objectsnaponopen": 1,
            "statusbarvisible": 2,
            "toolbarvisible": 1,
            "lefttoolbarpinned": 0,
            "toptoolbarpinned": 0,
            "righttoolbarpinned": 0,
            "bottomtoolbarpinned": 0,
            "toolbars_unpinned_last_save": 0,
            "tallnewobj": 0,
            "boxanimatetime": 200,
            "enablehscroll": 1,
            "enablevscroll": 1,
            "devicewidth": 0.0,
            "description": "Modular help for stochspectra~ voices and stochpacketenv~ gamma envelopes.",
            "digest": "A stochastic spectral voice multiplied by a separate gamma-renewal packet envelope.",
            "tags": "stochastic spectrum wavetable envelope packet renewal gamma modal synthesis spectrogram",
            "style": "",
            "subpatcher_template": "",
            "assistshowspatchername": 0,
            "boxes": boxes,
            "lines": lines,
        }
    }


def main() -> None:
    rendered = json.dumps(build(), indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)


if __name__ == "__main__":
    main()
