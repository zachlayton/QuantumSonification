#!/usr/bin/env python3
"""Build Surface Reverb v2 with a four-voice resonance-grain event layer.

Version 1 remains the stable drone-oriented instrument.  This builder imports
its proven surface FDN and adds an excitation envelope layer without modifying
or regenerating any v1 file.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import build_qmw_realtime_surface_reverb_v1 as v1


MAX_ROOT = Path(__file__).resolve().parent
MODULE_ROOT = MAX_ROOT / "control_room_modules"
OUTPUT = MODULE_ROOT / "QMW_Realtime_Surface_Reverb_v2.maxpat"
SCHEDULER = MAX_ROOT / "qmw_resonance_grain_scheduler_v2.js"


def add_internal_noise_to_genexpr(code: str) -> str:
    """Install compact onset/quantum-shaped noise inside the v2 FDN."""
    parameter_anchor = "Param output_gain(0.72);"
    parameters = r"""Param output_gain(0.72);

// Internal geometry excitation: onset burst + continuously adjustable floor.
Param noise_amount(0.28);
Param noise_decay_ms(45);
Param onset_threshold(0.012);
Param onset_sensitivity(10);
Param noise_color(0.72);
Param noise_floor(0.008);
Param noise_spectral_mode(0);
Param noise_spectral_amount(0.75);
Param noise_spectral_q(7);
Param noise_spectral_gain(2.5);
Param noise_spectral_base_hz(55);
Param noise_spectral_smooth_ms(80);"""
    if code.count(parameter_anchor) != 1:
        raise RuntimeError("Could not install v2 internal-noise parameters")
    code = code.replace(parameter_anchor, parameters)

    history_anchor = "History dc_r_x(0); History dc_r_y(0);"
    histories = r"""History dc_r_x(0); History dc_r_y(0);
History noise_onset_fast(0); History noise_onset_slow(0);
History noise_env(0); History noise_lp(0);
History noise_w0(1); History noise_w1(0); History noise_w2(0); History noise_w3(0);
History noise_h0(1); History noise_h1(3); History noise_h2(5); History noise_h3(7);
History noise_ic1_0(0); History noise_ic2_0(0);
History noise_ic1_1(0); History noise_ic2_1(0);
History noise_ic1_2(0); History noise_ic2_2(0);
History noise_ic1_3(0); History noise_ic2_3(0);"""
    if code.count(history_anchor) != 1:
        raise RuntimeError("Could not install v2 internal-noise histories")
    code = code.replace(history_anchor, histories)

    excitation_anchor = "excite = in1 * input_gain * (1 - fr) * 0.42;"
    excitation = r"""// Input and noise are combined *inside* the geometry excitation path.
input_signal = in1 * input_gain;
input_abs = abs(input_signal);
noise_fast_coeff = exp(-1 / max(0.0015 * sr, 1));
noise_slow_coeff = exp(-1 / max(0.035 * sr, 1));
noise_onset_fast = input_abs + noise_fast_coeff * (noise_onset_fast - input_abs);
noise_onset_slow = input_abs + noise_slow_coeff * (noise_onset_slow - input_abs);
noise_onset = clamp(
    (noise_onset_fast - noise_onset_slow - max(onset_threshold, 0))
    * max(onset_sensitivity, 0),
    0,
    1
);
noise_decay_samples = max(noise_decay_ms, 0.1) * 0.001 * sr;
noise_decay_coeff = exp(-1 / max(noise_decay_samples, 1));
noise_env = max(noise_env * noise_decay_coeff, noise_onset);

raw_internal_noise = noise();
noise_color_norm = clamp(noise_color, 0, 1);
noise_cut_hz = min(350 + 15000 * noise_color_norm, 0.45 * sr);
noise_cut_coeff = 1 - exp((-pi2 * noise_cut_hz) / sr);
noise_lp = noise_lp + noise_cut_coeff * (raw_internal_noise - noise_lp);
colored_internal_noise = mix(noise_lp, raw_internal_noise, noise_color_norm);

// Four inexpensive state-variable bands follow paired qm magnitudes and qh
// Hamiltonian ratios. This retains the earlier quantum spectral character
// without importing the twenty-delay research core.
noise_smooth_seconds = max(noise_spectral_smooth_ms, 0.1) * 0.001;
noise_smooth_coeff = 1 - exp(-1 / max(sr * noise_smooth_seconds, 1));
noise_w0_target = sqrt(max(0, qm0 + qm1));
noise_w1_target = sqrt(max(0, qm2 + qm3));
noise_w2_target = sqrt(max(0, qm4 + qm5));
noise_w3_target = sqrt(max(0, qm6 + qm7));
noise_w0 = noise_w0 + noise_smooth_coeff * (noise_w0_target - noise_w0);
noise_w1 = noise_w1 + noise_smooth_coeff * (noise_w1_target - noise_w1);
noise_w2 = noise_w2 + noise_smooth_coeff * (noise_w2_target - noise_w2);
noise_w3 = noise_w3 + noise_smooth_coeff * (noise_w3_target - noise_w3);
noise_h0 = noise_h0 + noise_smooth_coeff * (max(qh0, 0.01) - noise_h0);
noise_h1 = noise_h1 + noise_smooth_coeff * (max(qh2, 0.01) - noise_h1);
noise_h2 = noise_h2 + noise_smooth_coeff * (max(qh4, 0.01) - noise_h2);
noise_h3 = noise_h3 + noise_smooth_coeff * (max(qh6, 0.01) - noise_h3);
noise_base = clamp(noise_spectral_base_hz, 20, 2000);
noise_k = 1 / max(noise_spectral_q, 0.5);

noise_f0 = clamp(noise_base * noise_h0, 20, 0.45 * sr);
noise_g0 = tan(0.5 * pi2 * noise_f0 / sr);
noise_a1_0 = 1 / (1 + noise_g0 * (noise_g0 + noise_k));
noise_a2_0 = noise_g0 * noise_a1_0; noise_a3_0 = noise_g0 * noise_a2_0;
noise_v3_0 = colored_internal_noise - noise_ic2_0;
noise_v1_0 = noise_a1_0 * noise_ic1_0 + noise_a2_0 * noise_v3_0;
noise_v2_0 = noise_ic2_0 + noise_a2_0 * noise_ic1_0 + noise_a3_0 * noise_v3_0;
noise_ic1_0 = 2 * noise_v1_0 - noise_ic1_0; noise_ic2_0 = 2 * noise_v2_0 - noise_ic2_0;

noise_f1 = clamp(noise_base * noise_h1, 20, 0.45 * sr);
noise_g1 = tan(0.5 * pi2 * noise_f1 / sr);
noise_a1_1 = 1 / (1 + noise_g1 * (noise_g1 + noise_k));
noise_a2_1 = noise_g1 * noise_a1_1; noise_a3_1 = noise_g1 * noise_a2_1;
noise_v3_1 = colored_internal_noise - noise_ic2_1;
noise_v1_1 = noise_a1_1 * noise_ic1_1 + noise_a2_1 * noise_v3_1;
noise_v2_1 = noise_ic2_1 + noise_a2_1 * noise_ic1_1 + noise_a3_1 * noise_v3_1;
noise_ic1_1 = 2 * noise_v1_1 - noise_ic1_1; noise_ic2_1 = 2 * noise_v2_1 - noise_ic2_1;

noise_f2 = clamp(noise_base * noise_h2, 20, 0.45 * sr);
noise_g2 = tan(0.5 * pi2 * noise_f2 / sr);
noise_a1_2 = 1 / (1 + noise_g2 * (noise_g2 + noise_k));
noise_a2_2 = noise_g2 * noise_a1_2; noise_a3_2 = noise_g2 * noise_a2_2;
noise_v3_2 = colored_internal_noise - noise_ic2_2;
noise_v1_2 = noise_a1_2 * noise_ic1_2 + noise_a2_2 * noise_v3_2;
noise_v2_2 = noise_ic2_2 + noise_a2_2 * noise_ic1_2 + noise_a3_2 * noise_v3_2;
noise_ic1_2 = 2 * noise_v1_2 - noise_ic1_2; noise_ic2_2 = 2 * noise_v2_2 - noise_ic2_2;

noise_f3 = clamp(noise_base * noise_h3, 20, 0.45 * sr);
noise_g3 = tan(0.5 * pi2 * noise_f3 / sr);
noise_a1_3 = 1 / (1 + noise_g3 * (noise_g3 + noise_k));
noise_a2_3 = noise_g3 * noise_a1_3; noise_a3_3 = noise_g3 * noise_a2_3;
noise_v3_3 = colored_internal_noise - noise_ic2_3;
noise_v1_3 = noise_a1_3 * noise_ic1_3 + noise_a2_3 * noise_v3_3;
noise_v2_3 = noise_ic2_3 + noise_a2_3 * noise_ic1_3 + noise_a3_3 * noise_v3_3;
noise_ic1_3 = 2 * noise_v1_3 - noise_ic1_3; noise_ic2_3 = 2 * noise_v2_3 - noise_ic2_3;

noise_weight_energy = noise_w0 * noise_w0 + noise_w1 * noise_w1
    + noise_w2 * noise_w2 + noise_w3 * noise_w3;
quantum_internal_noise = (
    noise_v1_0 * noise_w0 + noise_v1_1 * noise_w1
    + noise_v1_2 * noise_w2 + noise_v1_3 * noise_w3
) / sqrt(max(noise_weight_energy, 0.000001));
spectral_internal_noise = tanh(quantum_internal_noise * clamp(noise_spectral_gain, 0, 8));
shaped_internal_noise = mix(
    colored_internal_noise,
    spectral_internal_noise,
    clamp(noise_spectral_amount, 0, 1)
);
internal_noise = shaped_internal_noise * (
    clamp(noise_floor, 0, 0.25)
    + noise_env * clamp(noise_amount, 0, 1)
);
excite = (input_signal + internal_noise) * (1 - fr) * 0.42;"""
    if code.count(excitation_anchor) != 1:
        raise RuntimeError("Could not install v2 internal-noise excitation")
    code = code.replace(excitation_anchor, excitation)
    return code.replace(
        "qmw_compact_realtime_surface_fdn_v1.genexpr",
        "qmw_compact_realtime_surface_fdn_v2_noise.genexpr",
        1,
    )


def add_box(
    patcher: dict[str, Any],
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    presentation: bool = False,
    **properties: Any,
) -> str:
    numeric_ids = [
        int(entry["box"]["id"][4:])
        for entry in patcher["boxes"]
        if entry["box"]["id"].startswith("obj-")
        and entry["box"]["id"][4:].isdigit()
    ]
    identifier = f"obj-{max(numeric_ids, default=0) + 1}"
    box: dict[str, Any] = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        box["text"] = text
    if presentation:
        box["presentation"] = 1
        box["presentation_rect"] = list(rect)
    box.update(properties)
    patcher["boxes"].append({"box": box})
    return identifier


def connect(
    patcher: dict[str, Any], source: str, outlet: int,
    destination: str, inlet: int = 0,
) -> None:
    patcher["lines"].append(
        {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}
    )


def add_labeled_number(
    patcher: dict[str, Any], scheduler: str, *,
    label: str, selector: str, default: float, minimum: float,
    maximum: float, x: float, width: float = 65.0, y: float = 516.0,
) -> str:
    add_box(
        patcher, "comment", [x, y, width + 8.0, 18.0],
        text=label, presentation=True, fontface=1, fontsize=8.0,
    )
    number = add_box(
        patcher, "flonum", [x, y + 21.0, width, 22.0],
        presentation=True, minimum=minimum, maximum=maximum,
        parameter_enable=0, numinlets=1, numoutlets=2,
        outlettype=["", "bang"],
    )
    prepend = add_box(
        patcher, "newobj", [1660.0, 500.0 + len(patcher["boxes"]) % 10 * 28.0, 110.0, 22.0],
        text=f"prepend {selector}",
    )
    load = add_box(
        patcher, "newobj", [1540.0, 500.0 + len(patcher["boxes"]) % 10 * 28.0, 105.0, 22.0],
        text=f"loadmess {default:g}",
    )
    connect(patcher, load, 0, number)
    connect(patcher, number, 0, prepend)
    connect(patcher, prepend, 0, scheduler)
    return number


def build_patch() -> dict[str, Any]:
    payload = deepcopy(v1.build_patch())
    patcher = payload["patcher"]
    patcher["rect"] = [30.0, 80.0, 1780.0, 850.0]

    boxes = [entry["box"] for entry in patcher["boxes"]]
    by_id = {box["id"]: box for box in boxes}
    title = next(box for box in boxes if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v1")
    title["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v2"
    subtitle = next(box for box in boxes if str(box.get("text", "")).startswith("20 field probes"))
    subtitle["text"] = "20 field probes → compact FDN · four independently timed qbit grains"

    codebox_box = next(box for box in boxes if box.get("maxclass") == "gen.codebox~")
    codebox_box["code"] = add_internal_noise_to_genexpr(codebox_box["code"])
    codebox = codebox_box["id"]
    input_lines = [
        line for line in patcher["lines"]
        if line["patchline"]["destination"] == [codebox, 0]
        and by_id[line["patchline"]["source"][0]].get("text") == "+~"
    ]
    if len(input_lines) != 1:
        raise RuntimeError(f"Expected one FDN excitation line; found {len(input_lines)}")
    excitation_source = input_lines[0]["patchline"]["source"]
    patcher["lines"].remove(input_lines[0])

    # Grain control panel below the stable v1 surface controls.
    add_box(
        patcher, "panel", [10.0, 505.0, 760.0, 215.0], presentation=True,
        background=1, bgcolor=[0.075, 0.065, 0.12, 1.0], border=1, rounded=12,
    )
    add_box(
        patcher, "comment", [25.0, 510.0, 360.0, 22.0],
        text="RESONANCE GRAINS + QUANTUM RHYTHM MATRIX", presentation=True,
        fontsize=13.0, fontface=1, textcolor=[0.86, 0.78, 1.0, 1.0],
    )

    scheduler = add_box(
        patcher, "newobj", [1780.0, 340.0, 245.0, 22.0],
        text="js qmw_resonance_grain_scheduler_v2.js",
        numinlets=1, numoutlets=7,
        outlettype=["", "", "", "", "float", "float", ""],
    )

    mode_menu = add_box(
        patcher, "umenu", [25.0, 556.0, 100.0, 22.0], presentation=True,
        items=["DRONE", ",", "GRAINS", ",", "HYBRID"],
        parameter_enable=0, numinlets=1, numoutlets=3,
        outlettype=["int", "", ""],
    )
    source_menu = add_box(
        patcher, "umenu", [135.0, 556.0, 105.0, 22.0], presentation=True,
        items=["LOCAL", ",", "QUANTUM", ",", "OSC"],
        parameter_enable=0, numinlets=1, numoutlets=3,
        outlettype=["int", "", ""],
    )
    add_box(patcher, "comment", [25.0, 536.0, 80.0, 18.0], text="MODE", presentation=True, fontface=1, fontsize=8.0)
    add_box(patcher, "comment", [135.0, 536.0, 80.0, 18.0], text="TRIGGER SOURCE", presentation=True, fontface=1, fontsize=8.0)
    mode_prepend = add_box(patcher, "newobj", [1780.0, 380.0, 88.0, 22.0], text="prepend mode")
    source_prepend = add_box(patcher, "newobj", [1880.0, 380.0, 138.0, 22.0], text="prepend trigger_source")
    mode_load = add_box(patcher, "newobj", [1780.0, 410.0, 72.0, 22.0], text="loadmess 2")
    source_load = add_box(patcher, "newobj", [1880.0, 410.0, 72.0, 22.0], text="loadmess 0")
    for load, menu, prepend in ((mode_load, mode_menu, mode_prepend), (source_load, source_menu, source_prepend)):
        connect(patcher, load, 0, menu)
        connect(patcher, menu, 0, prepend)
        connect(patcher, prepend, 0, scheduler)

    add_box(patcher, "comment", [250.0, 536.0, 52.0, 18.0], text="EVENTS", presentation=True, fontface=1, fontsize=8.0)
    enable_toggle = add_box(
        patcher, "toggle", [262.0, 556.0, 22.0, 22.0],
        presentation=True, parameter_enable=0,
        numinlets=1, numoutlets=1, outlettype=["int"],
    )
    enable_load = add_box(patcher, "newobj", [1980.0, 410.0, 72.0, 22.0], text="loadmess 1")
    enable_prepend = add_box(patcher, "newobj", [1980.0, 380.0, 98.0, 22.0], text="prepend enable")
    # A fixed scheduler tick resolves four independent rates. The musical
    # rates themselves come from Local UI, Quantum telemetry, or OSC.
    metro = add_box(patcher, "newobj", [1780.0, 450.0, 72.0, 22.0], text="metro 50")
    connect(patcher, enable_load, 0, enable_toggle)
    connect(patcher, enable_load, 0, metro)
    connect(patcher, enable_load, 0, enable_prepend)
    connect(patcher, enable_toggle, 0, metro)
    connect(patcher, enable_toggle, 0, enable_prepend)
    connect(patcher, enable_prepend, 0, scheduler)
    connect(patcher, metro, 0, scheduler)

    rate_defaults = (0.85, 1.10, 1.45, 1.90)
    rate_controls: list[str] = []
    for voice, (x, default) in enumerate(zip((302.0, 352.0, 402.0, 452.0), rate_defaults)):
        rate_controls.append(
            add_labeled_number(
                patcher, scheduler, label=f"Q{voice} Hz",
                selector=f"local_rate{voice}", default=default,
                minimum=0.0, maximum=20.0, x=x, width=44.0,
            )
        )
    probability = add_labeled_number(
        patcher, scheduler, label="PROB", selector="probability",
        default=0.8, minimum=0.0, maximum=1.0, x=502.0, width=52.0,
    )
    add_labeled_number(
        patcher, scheduler, label="DUR ms", selector="duration",
        default=180.0, minimum=12.0, maximum=4000.0, x=560.0, width=65.0,
    )
    add_labeled_number(
        patcher, scheduler, label="ATK ms", selector="attack",
        default=12.0, minimum=0.5, maximum=1000.0, x=632.0, width=58.0,
    )
    coherence_duration = add_labeled_number(
        patcher, scheduler, label="COH→DUR", selector="coherence_duration",
        default=0.65, minimum=-1.0, maximum=1.0, x=698.0, width=55.0,
    )
    cell_threshold = add_labeled_number(
        patcher, scheduler, label="CELL", selector="cell_threshold",
        default=0.20, minimum=0.0, maximum=0.99,
        x=235.0, width=58.0, y=587.0,
    )
    quantum_threshold = add_labeled_number(
        patcher, scheduler, label="Q GATE", selector="quantum_threshold",
        default=0.012, minimum=0.001, maximum=0.25,
        x=302.0, width=58.0, y=587.0,
    )
    quantum_step = add_labeled_number(
        patcher, scheduler, label="STEP ms", selector="quantum_step",
        default=90.0, minimum=5.0, maximum=2000.0,
        x=368.0, width=60.0, y=587.0,
    )
    refractory = add_labeled_number(
        patcher, scheduler, label="REFRACT ms", selector="refractory",
        default=400.0, minimum=0.0, maximum=4000.0,
        x=435.0, width=68.0, y=587.0,
    )
    groove = add_labeled_number(
        patcher, scheduler, label="GROOVE", selector="groove",
        default=0.35, minimum=0.0, maximum=1.0,
        x=510.0, width=55.0, y=587.0,
    )

    add_box(patcher, "comment", [25.0, 588.0, 70.0, 18.0], text="GRAIN LEVEL", presentation=True, fontface=1, fontsize=8.0)
    level = add_box(
        patcher, "flonum", [25.0, 608.0, 65.0, 22.0],
        presentation=True, minimum=0.0, maximum=3.0, parameter_enable=0,
        numinlets=1, numoutlets=2, outlettype=["", "bang"],
    )
    add_box(patcher, "comment", [102.0, 588.0, 70.0, 18.0], text="DRONE MIX", presentation=True, fontface=1, fontsize=8.0)
    drone = add_box(
        patcher, "flonum", [102.0, 608.0, 65.0, 22.0],
        presentation=True, minimum=0.0, maximum=1.0, parameter_enable=0,
        numinlets=1, numoutlets=2, outlettype=["", "bang"],
    )
    for control, selector, default, x in ((level, "level", 1.35, 1780.0), (drone, "drone_mix", 0.65, 1900.0)):
        prepend = add_box(patcher, "newobj", [x, 735.0, 112.0, 22.0], text=f"prepend {selector}")
        load = add_box(patcher, "newobj", [x, 765.0, 90.0, 22.0], text=f"loadmess {default:g}")
        connect(patcher, load, 0, control)
        # Also initialize the scheduler directly.  The parallel UI connection
        # keeps the displayed value correct even in an embedded bpatcher.
        connect(patcher, load, 0, prepend)
        connect(patcher, control, 0, prepend)
        connect(patcher, prepend, 0, scheduler)

    manual = add_box(patcher, "button", [182.0, 608.0, 23.0, 23.0], presentation=True, parameter_enable=0)
    add_box(patcher, "comment", [176.0, 588.0, 52.0, 18.0], text="FIRE", presentation=True, fontface=1, fontsize=8.0)
    manual_message = add_box(patcher, "message", [2040.0, 450.0, 52.0, 22.0], text="trigger")
    connect(patcher, manual, 0, manual_message)
    connect(patcher, manual_message, 0, scheduler)

    status = add_box(
        patcher, "message", [573.0, 600.0, 169.0, 34.0],
        text="grain hybrid local matrix 0000/0000/0000/0000 ready",
        presentation=True, linecount=2,
    )
    connect(patcher, scheduler, 6, status)

    # Internal noise controls address Gen~ directly. The first amount is the
    # onset burst; floor is the self-excitation that remains without input.
    noise_specs = (
        ("NOISE", "noise_amount", 0.28, 0.0, 1.0, 25.0, 60.0),
        ("FLOOR", "noise_floor", 0.008, 0.0, 0.25, 95.0, 60.0),
        ("COLOR", "noise_color", 0.72, 0.0, 1.0, 165.0, 60.0),
        ("DECAY", "noise_decay_ms", 45.0, 0.1, 500.0, 235.0, 68.0),
        ("Q SHAPE", "noise_spectral_amount", 0.75, 0.0, 1.0, 313.0, 68.0),
        ("Q GAIN", "noise_spectral_gain", 2.5, 0.0, 8.0, 391.0, 64.0),
        ("BASE Hz", "noise_spectral_base_hz", 55.0, 20.0, 2000.0, 465.0, 72.0),
        ("Q", "noise_spectral_q", 7.0, 0.5, 30.0, 547.0, 58.0),
    )
    noise_controls: list[str] = []
    for index, (label, parameter, default, minimum, maximum, x, width) in enumerate(noise_specs):
        add_box(
            patcher, "comment", [x, 647.0, width + 4.0, 18.0],
            text=label, presentation=True, fontface=1, fontsize=8.0,
        )
        control = add_box(
            patcher, "flonum", [x, 668.0, width, 22.0], presentation=True,
            minimum=minimum, maximum=maximum, parameter_enable=0,
            numinlets=1, numoutlets=2, outlettype=["", "bang"],
        )
        prepend = add_box(
            patcher, "newobj", [1780.0 + (index % 4) * 155.0, 1230.0 + (index // 4) * 35.0, 148.0, 22.0],
            text=f"prepend {parameter}",
        )
        load = add_box(
            patcher, "newobj", [1780.0 + (index % 4) * 155.0, 1300.0 + (index // 4) * 35.0, 112.0, 22.0],
            text=f"loadmess {default:g}",
        )
        connect(patcher, load, 0, control)
        connect(patcher, load, 0, prepend)
        connect(patcher, control, 0, prepend)
        connect(patcher, prepend, 0, codebox)
        noise_controls.append(control)

    noise_control = add_box(
        patcher, "newobj", [1780.0, 1375.0, 128.0, 22.0],
        text="r qmw.noise.control",
    )
    noise_route = add_box(
        patcher, "newobj", [1920.0, 1375.0, 720.0, 22.0],
        text=(
            "route amount floor color decay_ms spectral_amount "
            "spectral_gain base_hz q"
        ),
    )
    connect(patcher, noise_control, 0, noise_route)
    for index, control in enumerate(noise_controls):
        connect(patcher, noise_route, index, control)

    add_box(
        patcher, "comment", [615.0, 647.0, 78.0, 18.0],
        text="GRAIN DRY", presentation=True, fontface=1, fontsize=8.0,
    )
    grain_dry_control = add_box(
        patcher, "flonum", [615.0, 668.0, 72.0, 22.0], presentation=True,
        minimum=0.0, maximum=2.0, parameter_enable=0,
        numinlets=1, numoutlets=2, outlettype=["", "bang"],
    )
    grain_dry_load = add_box(
        patcher, "newobj", [2410.0, 900.0, 92.0, 22.0], text="loadmess 0.5"
    )
    grain_dry_ramp_message = add_box(
        patcher, "message", [2410.0, 935.0, 55.0, 22.0], text="$1 30"
    )
    grain_dry_gain = add_box(
        patcher, "newobj", [2410.0, 970.0, 45.0, 22.0], text="line~"
    )
    connect(patcher, grain_dry_load, 0, grain_dry_control)
    connect(patcher, grain_dry_load, 0, grain_dry_ramp_message)
    connect(patcher, grain_dry_control, 0, grain_dry_ramp_message)
    connect(patcher, grain_dry_ramp_message, 0, grain_dry_gain)

    # Four independent audio-rate envelopes, one for each post-resonator qbit
    # bus. Articulation happens before the lanes are summed into the FDN, so
    # each qbit can produce its own rhythm and natural reverb decay.
    envelope_lines: list[str] = []
    grain_voice_signals: list[str] = []
    for voice in range(4):
        line = add_box(patcher, "newobj", [1780.0 + voice * 105.0, 855.0, 45.0, 22.0], text="line~")
        connect(patcher, scheduler, voice, line)
        envelope_lines.append(line)
        receive = add_box(
            patcher, "newobj", [1780.0 + voice * 155.0, 895.0, 142.0, 22.0],
            text=f"receive~ qmw_qubit_{voice}",
        )
        gate = add_box(
            patcher, "newobj", [1780.0 + voice * 155.0, 930.0, 32.0, 22.0],
            text="*~",
        )
        connect(patcher, receive, 0, gate, 0)
        connect(patcher, line, 0, gate, 1)
        grain_voice_signals.append(gate)

    grain_stereo_l = add_box(patcher, "newobj", [1780.0, 970.0, 32.0, 22.0], text="+~")
    grain_stereo_r = add_box(patcher, "newobj", [1870.0, 970.0, 32.0, 22.0], text="+~")
    connect(patcher, grain_voice_signals[0], 0, grain_stereo_l, 0)
    connect(patcher, grain_voice_signals[2], 0, grain_stereo_l, 1)
    connect(patcher, grain_voice_signals[1], 0, grain_stereo_r, 0)
    connect(patcher, grain_voice_signals[3], 0, grain_stereo_r, 1)
    grain_mono_sum = add_box(patcher, "newobj", [1825.0, 1005.0, 32.0, 22.0], text="+~")
    grain_mono_trim = add_box(patcher, "newobj", [1870.0, 1005.0, 48.0, 22.0], text="*~ 0.5")
    connect(patcher, grain_stereo_l, 0, grain_mono_sum, 0)
    connect(patcher, grain_stereo_r, 0, grain_mono_sum, 1)
    connect(patcher, grain_mono_sum, 0, grain_mono_trim)

    drone_gain_message = add_box(patcher, "message", [2070.0, 900.0, 55.0, 22.0], text="$1 30")
    grain_gain_message = add_box(patcher, "message", [2140.0, 900.0, 55.0, 22.0], text="$1 30")
    drone_gain = add_box(patcher, "newobj", [2070.0, 935.0, 45.0, 22.0], text="line~")
    grain_gain = add_box(patcher, "newobj", [2140.0, 935.0, 45.0, 22.0], text="line~")
    connect(patcher, scheduler, 4, drone_gain_message)
    connect(patcher, scheduler, 5, grain_gain_message)
    connect(patcher, drone_gain_message, 0, drone_gain)
    connect(patcher, grain_gain_message, 0, grain_gain)

    drone_branch = add_box(patcher, "newobj", [1975.0, 975.0, 32.0, 22.0], text="*~")
    grain_branch = add_box(patcher, "newobj", [2025.0, 1005.0, 32.0, 22.0], text="*~")
    excitation_mix = add_box(patcher, "newobj", [2000.0, 1010.0, 32.0, 22.0], text="+~")
    connect(patcher, excitation_source[0], excitation_source[1], drone_branch, 0)
    connect(patcher, drone_gain, 0, drone_branch, 1)
    connect(patcher, grain_mono_trim, 0, grain_branch, 0)
    connect(patcher, grain_gain, 0, grain_branch, 1)
    connect(patcher, drone_branch, 0, excitation_mix, 0)
    connect(patcher, grain_branch, 0, excitation_mix, 1)
    connect(patcher, excitation_mix, 0, codebox, 0)

    # The master dry branch in v1 is intentionally continuous.  In v2 it must
    # follow the event mode as well; otherwise GRAINS still sounds like DRONE
    # even when the FDN excitation is correctly articulated.
    dry_l = next(
        box["id"] for box in boxes
        if box.get("text") == "*~" and box.get("patching_rect")[:2] == [1310.0, 390.0]
    )
    dry_r = next(
        box["id"] for box in boxes
        if box.get("text") == "*~" and box.get("patching_rect")[:2] == [1310.0, 426.0]
    )
    mix_l = next(
        box["id"] for box in boxes
        if box.get("text") == "+~" and box.get("patching_rect")[:2] == [1490.0, 330.0]
    )
    mix_r = next(
        box["id"] for box in boxes
        if box.get("text") == "+~" and box.get("patching_rect")[:2] == [1490.0, 366.0]
    )
    dry_ramp = next(
        box["id"] for box in boxes
        if box.get("text") == "line~" and box.get("patching_rect")[:2] == [1555.0, 490.0]
    )
    dry_destinations = {dry_l: mix_l, dry_r: mix_r}
    stereo_grains = {dry_l: grain_stereo_l, dry_r: grain_stereo_r}
    for channel, (dry_source, mix_destination) in enumerate(dry_destinations.items()):
        matching = [
            line for line in patcher["lines"]
            if line["patchline"]["source"] == [dry_source, 0]
            and line["patchline"]["destination"] == [mix_destination, 1]
        ]
        if len(matching) != 1:
            raise RuntimeError("Could not isolate the v1 dry-bypass connection")
        patcher["lines"].remove(matching[0])
        x = 2210.0 + channel * 185.0
        mode_dry = add_box(patcher, "newobj", [x, 975.0, 32.0, 22.0], text="*~")
        grain_dry_level = add_box(patcher, "newobj", [x + 40.0, 975.0, 32.0, 22.0], text="*~")
        grain_dry_scaled = add_box(patcher, "newobj", [x + 80.0, 975.0, 32.0, 22.0], text="*~")
        grain_dry_master = add_box(patcher, "newobj", [x + 120.0, 975.0, 32.0, 22.0], text="*~")
        dry_event_sum = add_box(patcher, "newobj", [x + 160.0, 975.0, 32.0, 22.0], text="+~")
        connect(patcher, dry_source, 0, mode_dry, 0)
        connect(patcher, drone_gain, 0, mode_dry, 1)
        connect(patcher, stereo_grains[dry_source], 0, grain_dry_level, 0)
        connect(patcher, grain_gain, 0, grain_dry_level, 1)
        connect(patcher, grain_dry_level, 0, grain_dry_scaled, 0)
        connect(patcher, grain_dry_gain, 0, grain_dry_scaled, 1)
        connect(patcher, grain_dry_scaled, 0, grain_dry_master, 0)
        connect(patcher, dry_ramp, 0, grain_dry_master, 1)
        connect(patcher, mode_dry, 0, dry_event_sum, 0)
        connect(patcher, grain_dry_master, 0, dry_event_sum, 1)
        connect(patcher, dry_event_sum, 0, mix_destination, 1)

    # Quantum probability and explicit OSC events.
    raw = add_box(patcher, "newobj", [1780.0, 1080.0, 95.0, 22.0], text="r qmw.osc.raw")
    qmw = add_box(patcher, "newobj", [1890.0, 1080.0, 98.0, 22.0], text="OSC-route /qmw")
    density_route = add_box(patcher, "newobj", [2005.0, 1060.0, 145.0, 22.0], text="OSC-route /density_field")
    density_guard = add_box(patcher, "newobj", [2165.0, 1030.0, 162.0, 22.0], text="route float int list symbol")
    entropy_route = add_box(patcher, "newobj", [2165.0, 1060.0, 168.0, 22.0], text="OSC-route /entropy /magnitude")
    entropy_prepend = add_box(patcher, "newobj", [2290.0, 1060.0, 105.0, 22.0], text="prepend entropy")
    magnitude_prepend = add_box(patcher, "newobj", [2410.0, 1060.0, 125.0, 22.0], text="prepend magnitudes")
    event_route = add_box(patcher, "newobj", [2005.0, 1100.0, 112.0, 22.0], text="OSC-route /event")
    event_guard = add_box(patcher, "newobj", [2130.0, 1130.0, 162.0, 22.0], text="route float int list symbol")
    resonance_route = add_box(patcher, "newobj", [2130.0, 1100.0, 140.0, 22.0], text="OSC-route /resonance")
    external_prepend = add_box(patcher, "newobj", [2285.0, 1100.0, 112.0, 22.0], text="prepend external")
    connect(patcher, raw, 0, qmw)
    connect(patcher, qmw, 0, density_route)
    connect(patcher, density_route, 0, density_guard)
    connect(patcher, density_guard, 4, entropy_route)
    connect(patcher, entropy_route, 0, entropy_prepend)
    connect(patcher, entropy_prepend, 0, scheduler)
    connect(patcher, entropy_route, 1, magnitude_prepend)
    connect(patcher, magnitude_prepend, 0, scheduler)
    connect(patcher, qmw, 0, event_route)
    connect(patcher, event_route, 0, event_guard)
    connect(patcher, event_guard, 4, resonance_route)
    connect(patcher, resonance_route, 0, external_prepend)
    connect(patcher, external_prepend, 0, scheduler)

    # OSC can either send explicit resonance events or an independently
    # authored four-rate clock: /qmw/grain/rates r0 r1 r2 r3.
    grain_route = add_box(patcher, "newobj", [2005.0, 1165.0, 112.0, 22.0], text="OSC-route /grain")
    grain_rates_route = add_box(patcher, "newobj", [2130.0, 1165.0, 205.0, 22.0], text="OSC-route /rates /quantum_state")
    osc_rates_prepend = add_box(patcher, "newobj", [2255.0, 1165.0, 118.0, 22.0], text="prepend osc_rates")
    quantum_state_prepend = add_box(patcher, "newobj", [2385.0, 1165.0, 148.0, 22.0], text="prepend quantum_state")
    connect(patcher, qmw, 0, grain_route)
    connect(patcher, grain_route, 0, grain_rates_route)
    connect(patcher, grain_rates_route, 0, osc_rates_prepend)
    connect(patcher, osc_rates_prepend, 0, scheduler)
    connect(patcher, grain_rates_route, 1, quantum_state_prepend)
    connect(patcher, quantum_state_prepend, 0, scheduler)

    # Local automation bus for sequencers and future Eigenfeld clock bridges.
    control = add_box(patcher, "newobj", [1780.0, 1140.0, 128.0, 22.0], text="r qmw.grain.control")
    control_route = add_box(
        patcher, "newobj", [1920.0, 1140.0, 710.0, 22.0],
        text="route enable mode source rates probability duration attack randomness level drone_mix trigger seed grain_dry quantum_threshold refractory quantum_step groove cell_threshold coherence_duration",
    )
    connect(patcher, control, 0, control_route)
    destinations = [enable_toggle, mode_menu, source_menu]
    for index, destination in enumerate(destinations):
        connect(patcher, control_route, index, destination)
    local_rates_prepend = add_box(patcher, "newobj", [1780.0, 1180.0, 128.0, 22.0], text="prepend local_rates")
    connect(patcher, control_route, 3, local_rates_prepend)
    connect(patcher, local_rates_prepend, 0, scheduler)
    connect(patcher, control_route, 4, probability)
    direct_selectors = ("duration", "attack", "randomness", "level", "drone_mix", "trigger", "seed")
    for offset, selector in enumerate(direct_selectors, start=5):
        prepend = add_box(patcher, "newobj", [1780.0 + (offset - 5) * 112.0, 1180.0, 104.0, 22.0], text=f"prepend {selector}")
        connect(patcher, control_route, offset, prepend)
        connect(patcher, prepend, 0, scheduler)
    connect(patcher, control_route, 12, grain_dry_control)
    connect(patcher, control_route, 13, quantum_threshold)
    connect(patcher, control_route, 14, refractory)
    connect(patcher, control_route, 15, quantum_step)
    connect(patcher, control_route, 16, groove)
    connect(patcher, control_route, 17, cell_threshold)
    connect(patcher, control_route, 18, coherence_duration)

    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies.append(
        {
            "name": SCHEDULER.name,
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": "..",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    return payload


def validate_patch(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher["boxes"]]
    texts = [box.get("text", "") for box in boxes]
    code = next(box["code"] for box in boxes if box.get("maxclass") == "gen.codebox~")
    required = (
        "QMW REALTIME IMPLICIT SURFACE REVERB v2",
        "js qmw_resonance_grain_scheduler_v2.js",
        "metro 50",
        "r qmw.grain.control",
        "OSC-route /resonance",
        "OSC-route /entropy /magnitude",
        "prepend magnitudes",
        "prepend quantum_threshold",
        "prepend refractory",
        "prepend quantum_step",
        "prepend groove",
        "prepend cell_threshold",
        "prepend coherence_duration",
        "prepend local_rates",
        "prepend osc_rates",
        "prepend quantum_state",
        "r qmw.noise.control",
        "prepend noise_amount",
        "loadmess 0.5",
    )
    for text in required:
        if text not in texts:
            raise RuntimeError(f"v2 surface module is missing {text!r}")
    if texts.count("line~") < 6:
        raise RuntimeError("v2 requires four envelope and two gain line~ objects")
    for voice in range(4):
        if texts.count(f"receive~ qmw_qubit_{voice}") != 1:
            raise RuntimeError(f"v2 is missing the independent qbit {voice} grain bus")
    for token in (
        "qmw_compact_realtime_surface_fdn_v2_noise.genexpr",
        "Param noise_amount(0.28);",
        "Param noise_spectral_amount(0.75);",
        "quantum_internal_noise",
        "internal_noise = shaped_internal_noise",
        "excite = (input_signal + internal_noise)",
    ):
        if token not in code:
            raise RuntimeError(f"v2 internal-noise GenExpr is missing {token!r}")
    if not SCHEDULER.is_file():
        raise RuntimeError(f"Missing grain scheduler: {SCHEDULER}")


def main() -> int:
    payload = build_patch()
    validate_patch(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
