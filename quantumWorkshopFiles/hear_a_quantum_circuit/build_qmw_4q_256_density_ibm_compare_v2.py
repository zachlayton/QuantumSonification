#!/usr/bin/env python3
"""Build the V2 ideal-rho / IBM-rho-diag comparison workshop patch."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_Four_Qubit_256_Density_Morph_Workshop_v1.maxpat"
OUTPUT = ROOT / "QMW_Four_Qubit_256_Density_IBM_Compare_Workshop_v2.maxpat"
SAVED_IBM_JOB_ID = "d9kb4sjjf64c739huvsg"
SAVED_IBM_BACKEND = "ibm_marrakesh"
SAVED_IBM_REVISION = 20260728
SAVED_IBM_COUNTS = [
    517,
    3,
    14,
    487,
    1,
    0,
    0,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]


def normalized_probabilities(counts: list[int]) -> list[float]:
    total = sum(counts)
    if total <= 0:
        raise ValueError("Saved IBM counts must have a positive total")
    return [count / total for count in counts]


def harmonic_table(probabilities: list[float]) -> list[float]:
    phase = [2.0 * math.pi * index / 256 for index in range(256)]
    table = [
        sum(
            math.sqrt(probability) * math.sin((basis + 1) * value)
            for basis, probability in enumerate(probabilities)
        )
        for value in phase
    ]
    mean = sum(table) / len(table)
    table = [value - mean for value in table]
    peak = max(abs(value) for value in table)
    if peak > 1.0e-15:
        table = [0.95 * value / peak for value in table]
    return [max(-0.95, min(0.95, value)) for value in table]


def density_table(
    probabilities: list[float],
    coherences: list[tuple[int, int, float]] | None = None,
) -> list[float]:
    table = [0.0] * 256
    for basis, probability in enumerate(probabilities):
        table[basis * 16 + basis] = probability
    for row, column, value in coherences or []:
        table[row * 16 + column] = value
    mean = sum(table) / len(table)
    table = [value - mean for value in table]
    peak = max(abs(value) for value in table)
    if peak > 1.0e-12:
        table = [value / peak for value in table]
    return [max(-1.0, min(1.0, value)) for value in table]


def diagonal_metrics(probabilities: list[float]) -> tuple[float, float, float]:
    purity = sum(value * value for value in probabilities)
    entropy = -sum(
        value * math.log2(value)
        for value in probabilities
        if value > 1.0e-15
    ) / 4.0
    return purity, entropy, 0.0


def max_message(selector: str, *atoms: object) -> str:
    def render(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.12g}"
        return str(value)

    return " ".join([selector, *(render(value) for value in atoms)])


def box(identifier: str, maxclass: str, rect: list[float], **attrs) -> dict:
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


def main() -> int:
    saved_layout: dict[str, list[float]] = {}
    saved_patcher_rect: list[float] | None = None
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        saved_patcher_rect = existing["patcher"].get("rect")
        saved_layout = {
            entry["box"]["id"]: entry["box"]["presentation_rect"]
            for entry in existing["patcher"]["boxes"]
            if "presentation_rect" in entry["box"]
        }

    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    removed = {
        "metrics-label",
        "purity",
        "purity-label",
        "entropy",
        "entropy-label",
        "coherence",
        "coherence-label",
        "metrics-unpack",
        "density-udp",
        "density-route",
        "prepend-static",
        "prepend-frame",
        "prepend-metrics",
        "density-receiver",
        "static-buffer",
        "density-buffer-a",
        "density-buffer-b",
        "table-phasor",
        "frequency-default",
        "static-wave",
        "density-wave-a",
        "density-wave-b",
        "density-xfade-pack",
        "density-xfade-line",
        "density-xfade-inverse",
        "density-a-gain",
        "density-b-gain",
        "density-sum",
        "static-source-gain",
        "density-source-gain",
        "source-sum",
        "density-command",
    }
    patcher["boxes"] = [
        entry for entry in patcher["boxes"] if entry["box"]["id"] not in removed
    ]
    patcher["lines"] = [
        entry
        for entry in patcher["lines"]
        if entry["patchline"]["source"][0] not in removed
        and entry["patchline"]["destination"][0] not in removed
    ]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}

    boxes["title"]["text"] = (
        "IDEAL ↔ IBM · HARMONIC ↔ DENSITY WAVETABLE COMPARISON"
    )
    boxes["instructions"]["text"] = (
        "The V1 density engine remains intact. PLAY evolves both sources "
        "locally; use LOCAL ↔ IBM BLEND to audition either source or any mix."
    )
    boxes["wavetable-title"]["text"] = "ACTIVE WAVEFORM · SOURCE × MAPPING"
    boxes["wavetable-note"]["text"] = (
        "STATIC / DENSITY, depth, rate, PLAY, and RESET work as in V1. "
        "ARM IBM JOB authorizes one hardware result; the blend remains manual."
    )
    boxes["spectrum-title"]["text"] = "IDEAL / IBM · HARMONIC / DENSITY SPECTRUM"
    boxes["bridge-label"]["text"] = "IBM COMPARISON STATUS"
    boxes["bridge-label"]["presentation_rect"] = [24.0, 650.0, 205.0, 20.0]
    boxes["status"]["text"] = (
        "Start qac_density_ibm_compare_bridge_v2.py, SEND QASM, choose "
        "STATIC or DENSITY, then press PLAY."
    )
    boxes["status"]["presentation_rect"] = [24.0, 672.0, 1040.0, 38.0]
    boxes["mapping-note"]["text"] = (
        "MEASUREMENT CALLBACK: IDEAL ρ includes off-diagonal coherence. "
        "IBM ρdiag uses the 16 measured populations and therefore reports "
        "zero reconstructed coherence; full hardware tomography needs "
        "additional measurement bases."
    )
    boxes["mapping-note"]["presentation_rect"] = [24.0, 720.0, 1050.0, 44.0]
    boxes["safety-note"]["text"] = (
        "IBM safety: the bridge must be started with --confirm-ibm. "
        "The session default is one 1024-shot hardware job."
    )
    boxes["safety-note"]["presentation"] = 1
    boxes["safety-note"]["presentation_rect"] = [780.0, 518.0, 570.0, 24.0]
    boxes["sendstatus"]["presentation_rect"] = [24.0, 518.0, 740.0, 24.0]

    control_layout = {
        "mode-label": [814.0, 425.0, 128.0, 19.0],
        "mode-toggle": [979.0, 422.0, 26.0, 26.0],
        "depth-label": [1019.0, 425.0, 50.0, 19.0],
        "depth": [1070.0, 422.0, 58.0, 22.0],
        "rate-label": [1138.0, 425.0, 40.0, 19.0],
        "rate": [1180.0, 422.0, 58.0, 22.0],
        "play-label": [1247.0, 425.0, 38.0, 19.0],
        "play-toggle": [1285.0, 422.0, 26.0, 26.0],
        "reset-button": [1320.0, 422.0, 26.0, 26.0],
        "reset-label": [1348.0, 425.0, 48.0, 19.0],
    }
    boxes["depth-label"]["text"] = "DEPTH"
    boxes["rate-label"]["text"] = "RATE"
    for identifier, rect in control_layout.items():
        boxes[identifier]["presentation_rect"] = rect

    saved_ideal_probabilities = [0.0] * 16
    saved_ideal_probabilities[0] = 0.5
    saved_ideal_probabilities[3] = 0.5
    saved_hardware_probabilities = normalized_probabilities(SAVED_IBM_COUNTS)
    saved_ideal_harmonic = harmonic_table(saved_ideal_probabilities)
    saved_ibm_harmonic = harmonic_table(saved_hardware_probabilities)
    saved_ideal_density = density_table(
        saved_ideal_probabilities,
        [(0, 3, 0.5), (3, 0, 0.5)],
    )
    saved_ibm_density = density_table(saved_hardware_probabilities)
    saved_ideal_metrics = (1.0, 0.0, 1.0 / 15.0)
    saved_ibm_metrics = diagonal_metrics(saved_hardware_probabilities)
    saved_population_distance = 0.5 * sum(
        abs(ideal - hardware)
        for ideal, hardware in zip(
            saved_ideal_probabilities,
            saved_hardware_probabilities,
        )
    )

    patcher["boxes"].extend(
        [
            box(
                "compare-label",
                "comment",
                [24.0, 558.0, 162.0, 20.0],
                text="ARM IBM JOB",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 558.0, 162.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
            box(
                "compare-toggle",
                "toggle",
                [190.0, 555.0, 26.0, 26.0],
                presentation=1,
                presentation_rect=[190.0, 555.0, 26.0, 26.0],
                parameter_enable=0,
            ),
            box(
                "compare-help",
                "comment",
                [230.0, 558.0, 480.0, 20.0],
                text=(
                    "ON arms the next SEND QASM · audio remains local until "
                    "the IBM result is ready"
                ),
                fontsize=11.0,
                presentation=1,
                presentation_rect=[230.0, 558.0, 480.0, 20.0],
            ),
            box(
                "source-blend-label",
                "comment",
                [725.0, 558.0, 112.0, 20.0],
                text="LOCAL ↔ IBM BLEND",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[725.0, 558.0, 112.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
            box(
                "source-blend-slider",
                "slider",
                [1215.0, 1040.0, 300.0, 22.0],
                size=1001,
                floatoutput=0,
                presentation=1,
                presentation_rect=[845.0, 555.0, 300.0, 22.0],
                parameter_enable=0,
            ),
            box(
                "source-blend-scale",
                "newobj",
                [1215.0, 1070.0, 140.0, 22.0],
                text="scale 0 1000 0. 1.",
                numinlets=6,
                numoutlets=1,
                outlettype=["float"],
            ),
            box(
                "source-blend-display",
                "flonum",
                [1365.0, 1070.0, 68.0, 22.0],
                minimum=0.0,
                maximum=1.0,
                format=3,
                ignoreclick=1,
                presentation=1,
                presentation_rect=[1155.0, 554.0, 68.0, 24.0],
                parameter_enable=0,
            ),
            box(
                "source-blend-help",
                "comment",
                [1230.0, 558.0, 145.0, 20.0],
                text="0 LOCAL · 1 IBM",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[1230.0, 558.0, 145.0, 20.0],
            ),
            box(
                "source-prepend",
                "newobj",
                [900.0, 1070.0, 88.0, 22.0],
                text="prepend source",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-load-button",
                "button",
                [1050.0, 1210.0, 26.0, 26.0],
                presentation=1,
                presentation_rect=[250.0, 648.0, 26.0, 26.0],
                parameter_enable=0,
            ),
            box(
                "saved-load-label",
                "comment",
                [1085.0, 1213.0, 630.0, 20.0],
                text=(
                    "LOAD SAVED IBM · Bell · ibm_marrakesh · "
                    "job d9kb4sjjf64c739huvsg · 1024 shots"
                ),
                fontsize=11.0,
                presentation=1,
                presentation_rect=[284.0, 651.0, 630.0, 20.0],
                textcolor=[1.0, 0.68, 0.3, 1.0],
            ),
            box(
                "saved-load-help",
                "comment",
                [925.0, 1213.0, 390.0, 20.0],
                text="Offline preset · no bridge or IBM connection required",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[930.0, 651.0, 390.0, 20.0],
            ),
            box(
                "saved-trigger",
                "newobj",
                [1050.0, 1250.0, 164.0, 22.0],
                text="t b b b b b b b b",
                numinlets=1,
                numoutlets=8,
                outlettype=["bang"] * 8,
            ),
            box(
                "saved-ideal-density",
                "message",
                [20.0, 1290.0, 480.0, 22.0],
                text=max_message(
                    "ideal",
                    SAVED_IBM_REVISION,
                    *saved_ideal_density,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-ideal-harmonic",
                "message",
                [20.0, 1320.0, 480.0, 22.0],
                text=max_message(
                    "ideal_harmonic",
                    SAVED_IBM_REVISION,
                    *saved_ideal_harmonic,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-ideal-metrics",
                "message",
                [20.0, 1350.0, 480.0, 22.0],
                text=max_message(
                    "metrics",
                    SAVED_IBM_REVISION,
                    "ideal",
                    *saved_ideal_metrics,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-ibm-density",
                "message",
                [520.0, 1290.0, 480.0, 22.0],
                text=max_message(
                    "ibm",
                    SAVED_IBM_REVISION,
                    *saved_ibm_density,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-ibm-harmonic",
                "message",
                [520.0, 1320.0, 480.0, 22.0],
                text=max_message(
                    "ibm_harmonic",
                    SAVED_IBM_REVISION,
                    *saved_ibm_harmonic,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-ibm-metrics",
                "message",
                [520.0, 1350.0, 480.0, 22.0],
                text=max_message(
                    "metrics",
                    SAVED_IBM_REVISION,
                    "ibm_diag",
                    *saved_ibm_metrics,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-comparison",
                "message",
                [1020.0, 1290.0, 360.0, 22.0],
                text=max_message(
                    "comparison",
                    SAVED_IBM_REVISION,
                    saved_population_distance,
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "saved-status",
                "message",
                [1020.0, 1320.0, 520.0, 22.0],
                text=(
                    'set "SAVED IBM ready · Bell · ibm_marrakesh · '
                    '1024 shots · job d9kb4sjjf64c739huvsg"'
                ),
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "ibm-control-pack",
                "newobj",
                [900.0, 1100.0, 285.0, 22.0],
                text="o.pack /qmw/density_compare/control/ibm",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "ideal-metrics-label",
                "comment",
                [24.0, 596.0, 95.0, 20.0],
                text="IDEAL ρ",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 596.0, 95.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
            box(
                "ideal-purity",
                "flonum",
                [125.0, 593.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[125.0, 593.0, 68.0, 24.0],
            ),
            box(
                "ideal-purity-label",
                "comment",
                [198.0, 596.0, 48.0, 20.0],
                text="purity",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[198.0, 596.0, 48.0, 20.0],
            ),
            box(
                "ideal-entropy",
                "flonum",
                [275.0, 593.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[275.0, 593.0, 68.0, 24.0],
            ),
            box(
                "ideal-entropy-label",
                "comment",
                [348.0, 596.0, 55.0, 20.0],
                text="entropy",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[348.0, 596.0, 55.0, 20.0],
            ),
            box(
                "ideal-coherence",
                "flonum",
                [430.0, 593.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[430.0, 593.0, 68.0, 24.0],
            ),
            box(
                "ideal-coherence-label",
                "comment",
                [503.0, 596.0, 75.0, 20.0],
                text="coherence",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[503.0, 596.0, 75.0, 20.0],
            ),
            box(
                "ibm-metrics-label",
                "comment",
                [24.0, 628.0, 95.0, 20.0],
                text="IBM ρdiag",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 628.0, 95.0, 20.0],
                textcolor=[1.0, 0.68, 0.3, 1.0],
            ),
            box(
                "ibm-purity",
                "flonum",
                [125.0, 625.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[125.0, 625.0, 68.0, 24.0],
            ),
            box(
                "ibm-purity-label",
                "comment",
                [198.0, 628.0, 48.0, 20.0],
                text="purity",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[198.0, 628.0, 48.0, 20.0],
            ),
            box(
                "ibm-entropy",
                "flonum",
                [275.0, 625.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[275.0, 625.0, 68.0, 24.0],
            ),
            box(
                "ibm-entropy-label",
                "comment",
                [348.0, 628.0, 55.0, 20.0],
                text="entropy",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[348.0, 628.0, 55.0, 20.0],
            ),
            box(
                "ibm-coherence",
                "flonum",
                [430.0, 625.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[430.0, 625.0, 68.0, 24.0],
            ),
            box(
                "ibm-coherence-label",
                "comment",
                [503.0, 628.0, 75.0, 20.0],
                text="coherence",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[503.0, 628.0, 75.0, 20.0],
            ),
            box(
                "tvd-label",
                "comment",
                [620.0, 610.0, 150.0, 20.0],
                text="POPULATION DISTANCE",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[620.0, 610.0, 150.0, 20.0],
            ),
            box(
                "tvd",
                "flonum",
                [775.0, 607.0, 76.0, 24.0],
                presentation=1,
                presentation_rect=[775.0, 607.0, 76.0, 24.0],
            ),
            box(
                "tvd-note",
                "comment",
                [860.0, 610.0, 235.0, 20.0],
                text="0 = identical measured populations",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[860.0, 610.0, 235.0, 20.0],
            ),
            box(
                "ideal-metrics-unpack",
                "newobj",
                [930.0, 1040.0, 115.0, 22.0],
                text="unpack 0. 0. 0.",
                numinlets=1,
                numoutlets=3,
                outlettype=["float", "float", "float"],
            ),
            box(
                "ibm-metrics-unpack",
                "newobj",
                [1060.0, 1040.0, 115.0, 22.0],
                text="unpack 0. 0. 0.",
                numinlets=1,
                numoutlets=3,
                outlettype=["float", "float", "float"],
            ),
            box(
                "compare-udp",
                "newobj",
                [24.0, 835.0, 132.0, 22.0],
                text="udpreceive 7412",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "compare-route",
                "newobj",
                [175.0, 835.0, 1040.0, 22.0],
                text=(
                    "o.route /qmw/density_compare/ideal "
                    "/qmw/density_compare/ibm "
                    "/qmw/density_compare/ideal_harmonic "
                    "/qmw/density_compare/ibm_harmonic "
                    "/qmw/density_compare/ideal_frame "
                    "/qmw/density_compare/ibm_frame "
                    "/qmw/density_compare/metrics "
                    "/qmw/density_compare/comparison "
                    "/qmw/density_compare/status "
                    "/qmw/density_compare/error"
                ),
                numinlets=1,
                numoutlets=10,
                outlettype=["", "", "", "", "", "", "", "", "", ""],
            ),
            box(
                "prepend-ideal",
                "newobj",
                [175.0, 875.0, 95.0, 22.0],
                text="prepend ideal",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-ibm",
                "newobj",
                [280.0, 875.0, 90.0, 22.0],
                text="prepend ibm",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-metrics",
                "newobj",
                [800.0, 875.0, 105.0, 22.0],
                text="prepend metrics",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-comparison",
                "newobj",
                [915.0, 875.0, 135.0, 22.0],
                text="prepend comparison",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "compare-receiver",
                "newobj",
                [1065.0, 875.0, 285.0, 22.0],
                text="js qmw_density_ibm_compare_receiver_v2.js",
                numinlets=1,
                numoutlets=8,
                outlettype=["", "float", "", "", "", "float", "int", "int"],
            ),
            box(
                "prepend-ideal-harmonic",
                "newobj",
                [380.0, 875.0, 98.0, 22.0],
                text="prepend ideal_harmonic",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-ibm-harmonic",
                "newobj",
                [485.0, 875.0, 98.0, 22.0],
                text="prepend ibm_harmonic",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-ideal-frame",
                "newobj",
                [590.0, 875.0, 98.0, 22.0],
                text="prepend ideal_frame",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-ibm-frame",
                "newobj",
                [695.0, 875.0, 98.0, 22.0],
                text="prepend ibm_frame",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "ideal-buffer",
                "newobj",
                [24.0, 920.0, 285.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ideal_density_A "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "ibm-buffer",
                "newobj",
                [325.0, 920.0, 275.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ibm_density_A "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "ideal-density-buffer-b",
                "newobj",
                [24.0, 945.0, 310.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ideal_density_B "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "ibm-density-buffer-b",
                "newobj",
                [345.0, 945.0, 305.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ibm_density_B "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "ideal-harmonic-buffer",
                "newobj",
                [615.0, 920.0, 320.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ideal_harmonic "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "ibm-harmonic-buffer",
                "newobj",
                [950.0, 920.0, 315.0, 22.0],
                text=(
                    "buffer~ qmw_compare_ibm_harmonic "
                    "@samps 256 @channels 1"
                ),
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "table-phasor",
                "newobj",
                [24.0, 965.0, 52.0, 22.0],
                text="phasor~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "frequency-default",
                "newobj",
                [24.0, 995.0, 92.0, 22.0],
                text="loadmess 110.",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "ideal-wave",
                "newobj",
                [90.0, 965.0, 155.0, 22.0],
                text="wave~ qmw_compare_ideal_density_A",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-wave",
                "newobj",
                [265.0, 965.0, 150.0, 22.0],
                text="wave~ qmw_compare_ibm_density_A",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-wave-b",
                "newobj",
                [90.0, 995.0, 190.0, 22.0],
                text="wave~ qmw_compare_ideal_density_B",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-wave-b",
                "newobj",
                [300.0, 995.0, 185.0, 22.0],
                text="wave~ qmw_compare_ibm_density_B",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-harmonic-wave",
                "newobj",
                [505.0, 995.0, 195.0, 22.0],
                text="wave~ qmw_compare_ideal_harmonic",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-harmonic-wave",
                "newobj",
                [715.0, 995.0, 190.0, 22.0],
                text="wave~ qmw_compare_ibm_harmonic",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "compare-xfade-pack",
                "newobj",
                [435.0, 965.0, 88.0, 22.0],
                text="pack 0. 300",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "compare-xfade-line",
                "newobj",
                [540.0, 965.0, 42.0, 22.0],
                text="line~",
                numinlets=2,
                numoutlets=2,
                outlettype=["signal", "bang"],
            ),
            box(
                "compare-xfade-inverse",
                "newobj",
                [600.0, 965.0, 58.0, 22.0],
                text="!-~ 1.",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-gain",
                "newobj",
                [90.0, 1115.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-gain",
                "newobj",
                [265.0, 1115.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "compare-sum",
                "newobj",
                [175.0, 1150.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-xfade-pack",
                "newobj",
                [680.0, 965.0, 88.0, 22.0],
                text="pack f 70",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "ideal-density-xfade-line",
                "newobj",
                [785.0, 965.0, 42.0, 22.0],
                text="line~",
                numinlets=2,
                numoutlets=2,
                outlettype=["signal", "bang"],
            ),
            box(
                "ideal-density-xfade-inverse",
                "newobj",
                [845.0, 965.0, 58.0, 22.0],
                text="!-~ 1.",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-xfade-pack",
                "newobj",
                [920.0, 965.0, 78.0, 22.0],
                text="pack f 70",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "ibm-density-xfade-line",
                "newobj",
                [1010.0, 965.0, 42.0, 22.0],
                text="line~",
                numinlets=2,
                numoutlets=2,
                outlettype=["signal", "bang"],
            ),
            box(
                "ibm-density-xfade-inverse",
                "newobj",
                [1065.0, 965.0, 58.0, 22.0],
                text="!-~ 1.",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-a-gain",
                "newobj",
                [90.0, 1025.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-b-gain",
                "newobj",
                [145.0, 1025.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-sum",
                "newobj",
                [115.0, 1055.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-a-gain",
                "newobj",
                [265.0, 1025.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-b-gain",
                "newobj",
                [320.0, 1025.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-sum",
                "newobj",
                [290.0, 1055.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-harmonic-gain",
                "newobj",
                [90.0, 1030.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-density-gain",
                "newobj",
                [145.0, 1030.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ideal-mapping-sum",
                "newobj",
                [115.0, 1070.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-harmonic-gain",
                "newobj",
                [265.0, 1030.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-density-gain",
                "newobj",
                [320.0, 1030.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "ibm-mapping-sum",
                "newobj",
                [290.0, 1070.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "compare-command",
                "comment",
                [24.0, 1080.0, 820.0, 22.0],
                text=(
                    "engine: qac_density_ibm_compare_bridge_v2.py "
                    "--confirm-ibm · 1024 shots · one IBM job"
                ),
            ),
        ]
    )

    patcher["lines"].extend(
        [
            line("saved-load-button", 0, "saved-trigger"),
            line("saved-trigger", 7, "saved-ideal-density"),
            line("saved-trigger", 6, "saved-ideal-harmonic"),
            line("saved-trigger", 5, "saved-ideal-metrics"),
            line("saved-trigger", 4, "saved-ibm-density"),
            line("saved-trigger", 3, "saved-ibm-harmonic"),
            line("saved-trigger", 2, "saved-ibm-metrics"),
            line("saved-trigger", 1, "saved-comparison"),
            line("saved-trigger", 0, "saved-status"),
            line("saved-ideal-density", 0, "compare-receiver"),
            line("saved-ideal-harmonic", 0, "compare-receiver"),
            line("saved-ideal-metrics", 0, "compare-receiver"),
            line("saved-ibm-density", 0, "compare-receiver"),
            line("saved-ibm-harmonic", 0, "compare-receiver"),
            line("saved-ibm-metrics", 0, "compare-receiver"),
            line("saved-comparison", 0, "compare-receiver"),
            line("saved-status", 0, "status"),
            line("source-blend-slider", 0, "source-blend-scale"),
            line("source-blend-scale", 0, "source-blend-display"),
            line("source-blend-scale", 0, "source-prepend"),
            line("source-prepend", 0, "compare-receiver"),
            line("blend-prepend", 0, "compare-receiver"),
            line("compare-toggle", 0, "ibm-control-pack"),
            line("ibm-control-pack", 0, "control-udp"),
            line("compare-udp", 0, "compare-route"),
            line("compare-route", 0, "prepend-ideal"),
            line("compare-route", 1, "prepend-ibm"),
            line("compare-route", 2, "prepend-ideal-harmonic"),
            line("compare-route", 3, "prepend-ibm-harmonic"),
            line("compare-route", 4, "prepend-ideal-frame"),
            line("compare-route", 5, "prepend-ibm-frame"),
            line("compare-route", 6, "prepend-metrics"),
            line("compare-route", 7, "prepend-comparison"),
            line("compare-route", 8, "status"),
            line("compare-route", 9, "status"),
            line("prepend-ideal", 0, "compare-receiver"),
            line("prepend-ibm", 0, "compare-receiver"),
            line("prepend-ideal-harmonic", 0, "compare-receiver"),
            line("prepend-ibm-harmonic", 0, "compare-receiver"),
            line("prepend-ideal-frame", 0, "compare-receiver"),
            line("prepend-ibm-frame", 0, "compare-receiver"),
            line("prepend-metrics", 0, "compare-receiver"),
            line("prepend-comparison", 0, "compare-receiver"),
            line("compare-receiver", 0, "display"),
            line("compare-receiver", 1, "compare-xfade-pack"),
            line("compare-receiver", 2, "status"),
            line("compare-receiver", 3, "ideal-metrics-unpack"),
            line("compare-receiver", 4, "ibm-metrics-unpack"),
            line("compare-receiver", 5, "tvd"),
            line("compare-receiver", 6, "ideal-density-xfade-pack"),
            line("compare-receiver", 7, "ibm-density-xfade-pack"),
            line("ideal-metrics-unpack", 0, "ideal-purity"),
            line("ideal-metrics-unpack", 1, "ideal-entropy"),
            line("ideal-metrics-unpack", 2, "ideal-coherence"),
            line("ibm-metrics-unpack", 0, "ibm-purity"),
            line("ibm-metrics-unpack", 1, "ibm-entropy"),
            line("ibm-metrics-unpack", 2, "ibm-coherence"),
            line("frequency-default", 0, "freq"),
            line("freq", 0, "table-phasor"),
            line("table-phasor", 0, "ideal-wave"),
            line("table-phasor", 0, "ideal-density-wave-b"),
            line("table-phasor", 0, "ibm-wave"),
            line("table-phasor", 0, "ibm-density-wave-b"),
            line("table-phasor", 0, "ideal-harmonic-wave"),
            line("table-phasor", 0, "ibm-harmonic-wave"),
            line("compare-xfade-pack", 0, "compare-xfade-line"),
            line("compare-xfade-line", 0, "ibm-gain", 1),
            line("compare-xfade-line", 0, "compare-xfade-inverse"),
            line("compare-xfade-inverse", 0, "ideal-gain", 1),
            line("ideal-density-xfade-pack", 0, "ideal-density-xfade-line"),
            line("ideal-density-xfade-line", 0, "ideal-density-xfade-inverse"),
            line("ideal-density-xfade-line", 0, "ideal-density-b-gain", 1),
            line("ideal-density-xfade-inverse", 0, "ideal-density-a-gain", 1),
            line("ibm-density-xfade-pack", 0, "ibm-density-xfade-line"),
            line("ibm-density-xfade-line", 0, "ibm-density-xfade-inverse"),
            line("ibm-density-xfade-line", 0, "ibm-density-b-gain", 1),
            line("ibm-density-xfade-inverse", 0, "ibm-density-a-gain", 1),
            line("ideal-wave", 0, "ideal-density-a-gain"),
            line("ideal-density-wave-b", 0, "ideal-density-b-gain"),
            line("ideal-density-a-gain", 0, "ideal-density-sum"),
            line("ideal-density-b-gain", 0, "ideal-density-sum", 1),
            line("ibm-wave", 0, "ibm-density-a-gain"),
            line("ibm-density-wave-b", 0, "ibm-density-b-gain"),
            line("ibm-density-a-gain", 0, "ibm-density-sum"),
            line("ibm-density-b-gain", 0, "ibm-density-sum", 1),
            line("source-xfade-line", 0, "ideal-density-gain", 1),
            line("source-xfade-line", 0, "ibm-density-gain", 1),
            line("source-xfade-inverse", 0, "ideal-harmonic-gain", 1),
            line("source-xfade-inverse", 0, "ibm-harmonic-gain", 1),
            line("ideal-harmonic-wave", 0, "ideal-harmonic-gain"),
            line("ideal-density-sum", 0, "ideal-density-gain"),
            line("ideal-harmonic-gain", 0, "ideal-mapping-sum"),
            line("ideal-density-gain", 0, "ideal-mapping-sum", 1),
            line("ibm-harmonic-wave", 0, "ibm-harmonic-gain"),
            line("ibm-density-sum", 0, "ibm-density-gain"),
            line("ibm-harmonic-gain", 0, "ibm-mapping-sum"),
            line("ibm-density-gain", 0, "ibm-mapping-sum", 1),
            line("ideal-mapping-sum", 0, "ideal-gain"),
            line("ibm-mapping-sum", 0, "ibm-gain"),
            line("ideal-gain", 0, "compare-sum"),
            line("ibm-gain", 0, "compare-sum", 1),
            line("compare-sum", 0, "safe-scale"),
        ]
    )

    dependencies = [
        item
        for item in patcher.setdefault("dependency_cache", [])
        if item.get("name")
        not in {
            "qmw_density_morph_receiver_v1.js",
            "qmw_wavetable_receiver_v1.js",
        }
    ]
    patcher["dependency_cache"] = dependencies
    if not any(
        item.get("name") == "qmw_density_ibm_compare_receiver_v2.js"
        for item in dependencies
    ):
        dependencies.append(
            {
                "name": "qmw_density_ibm_compare_receiver_v2.js",
                "bootpath": str(ROOT),
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1,
            }
        )

    if saved_patcher_rect is not None:
        patcher["rect"] = saved_patcher_rect
    for entry in patcher["boxes"]:
        item = entry["box"]
        if item["id"] in saved_layout:
            item["presentation_rect"] = saved_layout[item["id"]]

    OUTPUT.write_text(
        json.dumps(document, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Built {OUTPUT.name} from {SOURCE.name}; "
        "the working V1 patch was not modified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
