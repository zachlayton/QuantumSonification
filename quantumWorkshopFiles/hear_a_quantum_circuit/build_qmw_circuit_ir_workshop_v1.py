#!/usr/bin/env python3
"""Build the participant-facing four-qubit circuit-to-IR Max patch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Circuit_Impulse_Response_Workshop_v1.maxpat"


def box(identifier: str, maxclass: str, rect: list[float], **attrs) -> dict:
    value = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    value.update(attrs)
    return {"box": value}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


def comment(
    identifier: str,
    rect: list[float],
    text: str,
    *,
    size: float = 12.0,
    color: list[float] | None = None,
    lines: int = 1,
) -> dict:
    return box(
        identifier,
        "comment",
        rect,
        text=text,
        fontsize=size,
        linecount=lines,
        presentation=1,
        presentation_rect=rect,
        textcolor=color or [0.9, 0.93, 0.97, 1.0],
    )


def main() -> int:
    boxes: list[dict] = []
    lines: list[dict] = []

    def add(value: dict) -> str:
        boxes.append(value)
        return value["box"]["id"]

    def connect(source: str, outlet: int, destination: str, inlet: int = 0) -> None:
        lines.append(line(source, outlet, destination, inlet))

    # Presentation.
    add(
        box(
            "background",
            "panel",
            [10.0, 10.0, 1380.0, 796.0],
            presentation=1,
            presentation_rect=[10.0, 10.0, 1380.0, 796.0],
            background=1,
            bgcolor=[0.055, 0.075, 0.105, 1.0],
            bordercolor=[0.13, 0.18, 0.25, 1.0],
        )
    )
    add(
        comment(
            "title",
            [24.0, 18.0, 1280.0, 36.0],
            "A QUANTUM CIRCUIT BECOMES AN IMPULSE RESPONSE",
            size=25.0,
        )
    )
    add(
        comment(
            "subtitle",
            [24.0, 55.0, 1320.0, 22.0],
            (
                "The same QAC circuit now weights sixteen reverberant decay times. "
                "Build → excite → compare dry and convolved sound."
            ),
            size=14.0,
            color=[0.44, 0.78, 1.0, 1.0],
        )
    )

    qac = add(
        box(
            "qac-ui",
            "jsui",
            [24.0, 88.0, 780.0, 390.0],
            filename="qmw_qac_circuit_programmer_v1.js",
            jsarguments=["qmw_qac_circuit_programmer_v1.js"],
            numinlets=1,
            numoutlets=2,
            outlettype=["", ""],
            presentation=1,
            presentation_rect=[24.0, 88.0, 780.0, 390.0],
        )
    )
    add(
        comment(
            "circuit-label",
            [24.0, 488.0, 62.0, 20.0],
            "CIRCUIT",
            color=[1.0, 0.68, 0.3, 1.0],
        )
    )
    circuit_status = add(
        box(
            "circuit-status",
            "message",
            [90.0, 486.0, 694.0, 24.0],
            text="Choose a preset or place gates, then click BUILD + HEAR.",
            presentation=1,
            presentation_rect=[90.0, 486.0, 694.0, 24.0],
        )
    )

    add(
        box(
            "mapping-panel",
            "panel",
            [24.0, 530.0, 760.0, 258.0],
            presentation=1,
            presentation_rect=[24.0, 530.0, 760.0, 258.0],
            background=1,
            bgcolor=[0.085, 0.115, 0.155, 1.0],
            bordercolor=[0.27, 0.54, 1.0, 1.0],
            rounded=8,
        )
    )
    add(
        comment(
            "mapping-title",
            [42.0, 544.0, 700.0, 26.0],
            "THE WORKSHOP MAPPING",
            size=18.0,
        )
    )
    add(
        comment(
            "mapping-steps",
            [42.0, 578.0, 700.0, 105.0],
            (
                "1  BUILD: calculate 16 basis probabilities.\n"
                "2  DECAY: |0000〉 … |1111〉 select RT60 values from 100 … 1600 ms.\n"
                "3  SCALE: √probability weights sixteen dense reflection clouds.\n"
                "4  EXPORT: save the generated buffer as a WAV impulse response.\n"
                "5  LISTEN: audition here or load the WAV into Ableton Convolution Reverb."
            ),
            size=13.0,
            lines=5,
        )
    )
    add(
        comment(
            "mapping-caveat",
            [42.0, 696.0, 700.0, 40.0],
            (
                "This is a declared sonification mapping—not a claim that a "
                "quantum circuit is an acoustic room. The circuit weights a "
                "repeatable noise-decay model; convolution applies the result."
            ),
            size=12.0,
            lines=2,
            color=[0.63, 0.68, 0.76, 1.0],
        )
    )
    ir_status = add(
        box(
            "ir-status",
            "message",
            [42.0, 748.0, 720.0, 25.0],
            text="IR READY · circuit-weighted RT60 ≈ 100 ms · |0000> 100 ms",
            presentation=1,
            presentation_rect=[42.0, 748.0, 720.0, 25.0],
        )
    )

    add(
        comment(
            "probability-title",
            [826.0, 98.0, 530.0, 25.0],
            "16 BASIS PROBABILITIES",
            size=18.0,
        )
    )
    probabilities = add(
        box(
            "probabilities",
            "multislider",
            [826.0, 130.0, 530.0, 100.0],
            setminmax=[0.0, 1.0],
            size=16,
            spacing=2,
            bgcolor=[0.08, 0.1, 0.14, 1.0],
            slidercolor=[0.27, 0.54, 1.0, 1.0],
            presentation=1,
            presentation_rect=[826.0, 130.0, 530.0, 100.0],
        )
    )
    add(
        comment(
            "probability-labels",
            [828.0, 234.0, 526.0, 18.0],
            " |0000〉                           basis-state order                           |1111〉",
            size=10.0,
            color=[0.55, 0.67, 0.82, 1.0],
        )
    )
    add(
        comment(
            "ir-title",
            [826.0, 269.0, 530.0, 25.0],
            "GENERATED 1.6-SECOND IMPULSE RESPONSE",
            size=18.0,
        )
    )
    ir_waveform = add(
        box(
            "ir-waveform",
            "waveform~",
            [826.0, 300.0, 530.0, 170.0],
            buffername="qmw_workshop_circuit_ir",
            numinlets=5,
            numoutlets=6,
            outlettype=["float", "float", "float", "float", "list", ""],
            presentation=1,
            presentation_rect=[826.0, 300.0, 530.0, 170.0],
            bgcolor=[0.08, 0.1, 0.14, 1.0],
            wavecolor=[1.0, 0.55, 0.2, 1.0],
        )
    )
    add(
        comment(
            "ir-axis",
            [826.0, 474.0, 530.0, 18.0],
            "fixed direct impulse · dense circuit-weighted decay · 0 … 1600 ms",
            size=10.0,
            color=[0.55, 0.67, 0.82, 1.0],
        )
    )

    add(
        box(
            "audio-panel",
            "panel",
            [826.0, 510.0, 530.0, 278.0],
            presentation=1,
            presentation_rect=[826.0, 510.0, 530.0, 278.0],
            background=1,
            bgcolor=[0.085, 0.115, 0.155, 1.0],
            bordercolor=[1.0, 0.5, 0.15, 1.0],
            rounded=8,
        )
    )
    add(
        comment(
            "listen-title",
            [846.0, 526.0, 470.0, 25.0],
            "EXPORT OR AUDITION THE IR",
            size=18.0,
        )
    )
    impulse_button = add(
        box(
            "impulse-button",
            "button",
            [846.0, 562.0, 30.0, 30.0],
            presentation=1,
            presentation_rect=[846.0, 562.0, 30.0, 30.0],
        )
    )
    add(comment("impulse-label", [885.0, 567.0, 130.0, 22.0], "IMPULSE TEST", size=13.0))
    noise_button = add(
        box(
            "noise-button",
            "button",
            [1055.0, 562.0, 30.0, 30.0],
            presentation=1,
            presentation_rect=[1055.0, 562.0, 30.0, 30.0],
        )
    )
    add(comment("noise-label", [1094.0, 567.0, 150.0, 22.0], "NOISE BURST", size=13.0))
    add(comment("wet-label", [846.0, 616.0, 82.0, 22.0], "DRY ↔ WET", size=13.0))
    wet = add(
        box(
            "wet",
            "slider",
            [930.0, 614.0, 185.0, 24.0],
            min=0.0,
            size=1.0,
            floatoutput=1,
            presentation=1,
            presentation_rect=[930.0, 614.0, 185.0, 24.0],
        )
    )
    add(comment("master-label", [846.0, 657.0, 70.0, 22.0], "MASTER", size=13.0))
    master = add(
        box(
            "master",
            "flonum",
            [920.0, 655.0, 62.0, 24.0],
            minimum=0.0,
            maximum=1.0,
            presentation=1,
            presentation_rect=[920.0, 655.0, 62.0, 24.0],
        )
    )
    add(comment("audio-label", [1020.0, 657.0, 55.0, 22.0], "AUDIO", size=13.0))
    dsp_toggle = add(
        box(
            "dsp-toggle",
            "toggle",
            [1080.0, 655.0, 26.0, 26.0],
            presentation=1,
            presentation_rect=[1080.0, 655.0, 26.0, 26.0],
        )
    )
    output_meter = add(
        box(
            "output-meter",
            "meter~",
            [1135.0, 659.0, 190.0, 18.0],
            presentation=1,
            presentation_rect=[1135.0, 659.0, 190.0, 18.0],
        )
    )
    export_ir = add(
        box(
            "export-ir",
            "message",
            [846.0, 704.0, 120.0, 28.0],
            text="writewave",
            presentation=1,
            presentation_rect=[846.0, 704.0, 120.0, 28.0],
            bgcolor=[1.0, 0.5, 0.15, 1.0],
            textcolor=[0.04, 0.05, 0.08, 1.0],
        )
    )
    add(
        comment(
            "export-label",
            [978.0, 708.0, 350.0, 22.0],
            "EXPORT IR WAV…  → Ableton Convolution Reverb",
            size=12.0,
        )
    )
    add(
        comment(
            "listen-note",
            [846.0, 738.0, 480.0, 34.0],
            (
                "Start with IMPULSE TEST: the convolved output is the IR itself. "
                "Then use NOISE BURST and compare dry with wet."
            ),
            size=12.0,
            lines=2,
            color=[0.63, 0.68, 0.76, 1.0],
        )
    )
    convolver_status = add(
        box(
            "convolver-status",
            "message",
            [1265.0, 890.0, 160.0, 24.0],
            text="HIRT audition ready",
        )
    )

    # Backstage circuit adapter and IR renderer.
    adapter = add(
        box(
            "adapter",
            "newobj",
            [24.0, 850.0, 245.0, 22.0],
            text="js qmw_qac_to_16_probabilities_workshop.js",
            numinlets=1,
            numoutlets=2,
            outlettype=["", ""],
        )
    )
    state_split = add(box("state-split", "newobj", [290.0, 850.0, 50.0, 22.0], text="t l l l"))
    probability_set = add(
        box("probability-set", "newobj", [360.0, 850.0, 92.0, 22.0], text="prepend setlist")
    )
    ir_renderer = add(
        box(
            "ir-renderer",
            "newobj",
            [470.0, 850.0, 215.0, 22.0],
            text="js qmw_circuit_ir_workshop_v1.js",
            numinlets=1,
            numoutlets=3,
            outlettype=["", "", ""],
        )
    )
    ir_taps = add(
        box(
            "ir-taps",
            "multislider",
            [705.0, 850.0, 250.0, 70.0],
            setminmax=[0.0, 1.0],
            size=16,
            spacing=2,
        )
    )
    tap_set = add(box("tap-set", "newobj", [705.0, 930.0, 92.0, 22.0], text="prepend setlist"))
    initial_state = add(
        box(
            "initial-state",
            "newobj",
            [24.0, 890.0, 420.0, 22.0],
            text="loadmess 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",
        )
    )
    qac_print = add(box("qac-print", "newobj", [24.0, 930.0, 130.0, 22.0], text="print QMW_IR_QAC"))
    adapter_status_set = add(
        box("adapter-status-set", "newobj", [175.0, 930.0, 75.0, 22.0], text="prepend set")
    )

    ir_buffer = add(
        box(
            "ir-buffer",
            "newobj",
            [975.0, 850.0, 330.0, 22.0],
            text="buffer~ qmw_workshop_circuit_ir 1600 1",
        )
    )
    convolver = add(
        box(
            "convolver",
            "newobj",
            [975.0, 890.0, 180.0, 22.0],
            text="multiconvolve~ 1 1 medium",
        )
    )
    convolver_status_set = add(
        box("convolver-status-set", "newobj", [1175.0, 890.0, 75.0, 22.0], text="prepend set")
    )

    # Excitation sources.
    click = add(box("click", "newobj", [24.0, 990.0, 42.0, 22.0], text="click~"))
    click_gain = add(box("click-gain", "newobj", [80.0, 990.0, 48.0, 22.0], text="*~ 0.35"))
    noise = add(box("noise", "newobj", [24.0, 1030.0, 48.0, 22.0], text="noise~"))
    noise_message = add(
        box("noise-message", "message", [150.0, 1030.0, 115.0, 22.0], text="1. 3, 0. 120 3")
    )
    noise_envelope = add(box("noise-envelope", "newobj", [280.0, 1030.0, 45.0, 22.0], text="line~"))
    noise_vca = add(box("noise-vca", "newobj", [90.0, 1030.0, 32.0, 22.0], text="*~"))
    noise_gain = add(box("noise-gain", "newobj", [340.0, 1030.0, 48.0, 22.0], text="*~ 0.18"))
    source_sum = add(box("source-sum", "newobj", [410.0, 990.0, 32.0, 22.0], text="+~"))

    # Dry/wet and output gain.
    wet_trigger = add(box("wet-trigger", "newobj", [470.0, 990.0, 40.0, 22.0], text="t f f"))
    wet_pack = add(box("wet-pack", "newobj", [530.0, 990.0, 72.0, 22.0], text="pack 0. 40"))
    wet_line = add(box("wet-line", "newobj", [620.0, 990.0, 45.0, 22.0], text="line~"))
    dry_inverse = add(box("dry-inverse", "newobj", [530.0, 1030.0, 42.0, 22.0], text="!- 1."))
    dry_pack = add(box("dry-pack", "newobj", [590.0, 1030.0, 72.0, 22.0], text="pack 0. 40"))
    dry_line = add(box("dry-line", "newobj", [680.0, 1030.0, 45.0, 22.0], text="line~"))
    dry_vca = add(box("dry-vca", "newobj", [760.0, 990.0, 32.0, 22.0], text="*~"))
    wet_vca = add(box("wet-vca", "newobj", [760.0, 1030.0, 32.0, 22.0], text="*~"))
    mix_sum = add(box("mix-sum", "newobj", [820.0, 990.0, 32.0, 22.0], text="+~"))
    master_pack = add(box("master-pack", "newobj", [870.0, 990.0, 72.0, 22.0], text="pack 0. 40"))
    master_line = add(box("master-line", "newobj", [960.0, 990.0, 45.0, 22.0], text="line~"))
    master_vca = add(box("master-vca", "newobj", [1030.0, 990.0, 32.0, 22.0], text="*~"))
    dac = add(box("dac", "ezdac~", [1090.0, 990.0, 48.0, 48.0]))
    wet_default = add(box("wet-default", "newobj", [470.0, 1070.0, 88.0, 22.0], text="loadmess 0.75"))
    master_default = add(box("master-default", "newobj", [870.0, 1070.0, 85.0, 22.0], text="loadmess 0.45"))

    # Circuit and state flow.
    connect(qac, 0, adapter)
    connect(qac, 0, qac_print)
    connect(qac, 1, circuit_status, 1)
    connect(adapter, 0, state_split)
    connect(adapter, 1, adapter_status_set)
    connect(adapter_status_set, 0, circuit_status, 1)
    connect(initial_state, 0, state_split)
    connect(state_split, 2, probability_set)
    connect(probability_set, 0, probabilities)
    connect(state_split, 1, ir_renderer)
    connect(state_split, 0, ir_taps)
    connect(ir_renderer, 0, tap_set)
    connect(tap_set, 0, ir_taps)
    connect(ir_renderer, 1, convolver)
    connect(ir_renderer, 1, convolver_status_set)
    connect(convolver_status_set, 0, convolver_status, 1)
    connect(ir_renderer, 2, ir_status, 1)
    connect(export_ir, 0, ir_buffer)

    # Audio.
    connect(impulse_button, 0, click)
    connect(click, 0, click_gain)
    connect(noise_button, 0, noise_message)
    connect(noise_message, 0, noise_envelope)
    connect(noise, 0, noise_vca)
    connect(noise_envelope, 0, noise_vca, 1)
    connect(noise_vca, 0, noise_gain)
    connect(click_gain, 0, source_sum)
    connect(noise_gain, 0, source_sum, 1)
    connect(source_sum, 0, convolver)
    connect(source_sum, 0, dry_vca)
    connect(convolver, 0, wet_vca)

    connect(wet, 0, wet_trigger)
    connect(wet_trigger, 1, wet_pack)
    connect(wet_pack, 0, wet_line)
    connect(wet_line, 0, wet_vca, 1)
    connect(wet_trigger, 0, dry_inverse)
    connect(dry_inverse, 0, dry_pack)
    connect(dry_pack, 0, dry_line)
    connect(dry_line, 0, dry_vca, 1)
    connect(dry_vca, 0, mix_sum)
    connect(wet_vca, 0, mix_sum, 1)
    connect(mix_sum, 0, master_vca)
    connect(master, 0, master_pack)
    connect(master_pack, 0, master_line)
    connect(master_line, 0, master_vca, 1)
    connect(master_vca, 0, dac)
    connect(master_vca, 0, dac, 1)
    connect(master_vca, 0, output_meter)
    connect(dsp_toggle, 0, dac)
    connect(wet_default, 0, wet)
    connect(master_default, 0, master)

    document = {
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
            "rect": [30.0, 45.0, 1400.0, 816.0],
            "openrect": [30.0, 45.0, 1400.0, 816.0],
            "openinpresentation": 1,
            "bglocked": 0,
            "gridsize": [15.0, 15.0],
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {
                    "name": "qmw_qac_circuit_programmer_v1.js",
                    "bootpath": str(ROOT),
                    "patcherrelativepath": ".",
                    "type": "TEXT",
                    "implicit": 1,
                },
                {
                    "name": "qmw_qac_to_16_probabilities_workshop.js",
                    "bootpath": str(ROOT),
                    "patcherrelativepath": ".",
                    "type": "TEXT",
                    "implicit": 1,
                },
                {
                    "name": "qmw_circuit_ir_workshop_v1.js",
                    "bootpath": str(ROOT),
                    "patcherrelativepath": ".",
                    "type": "TEXT",
                    "implicit": 1,
                },
                {"name": "multiconvolve~.mxo", "type": "iLaX", "implicit": 1},
            ],
        }
    }

    ids = {entry["box"]["id"] for entry in boxes}
    for connection in lines:
        patchline = connection["patchline"]
        assert patchline["source"][0] in ids
        assert patchline["destination"][0] in ids

    OUTPUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
