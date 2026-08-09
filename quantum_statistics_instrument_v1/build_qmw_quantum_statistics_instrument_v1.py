#!/usr/bin/env python3
"""Generate the Max 9 Fermi/Bose equation-of-state comparison instrument."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .quantum_statistics_model import BOSE_CRITICAL_REDUCED_DENSITY, compare_statistics
except ImportError:
    from quantum_statistics_model import BOSE_CRITICAL_REDUCED_DENSITY, compare_statistics


ROOT = Path(__file__).resolve().parent
ENERGIES = np.linspace(0.08, 6.0, 10)


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def wrap(
    boxes: list[dict[str, Any]],
    lines: list[dict[str, Any]],
    rect: list[float],
    dependencies: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    patcher: dict[str, Any] = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": rect,
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "autosave": 0,
    }
    if dependencies:
        patcher["dependency_cache"] = dependencies
    return {"patcher": patcher}


def lookup_rows() -> list[dict[str, Any]]:
    critical_log = math.log10(BOSE_CRITICAL_REDUCED_DENSITY)
    grid = sorted(set(np.linspace(-3.0, 2.0, 121).tolist() + [critical_log]))
    rows = []
    for log_density in grid:
        density = 10.0**log_density
        states = compare_statistics(density)
        fermi = states["fermi"]
        bose = states["bose"]
        rows.append(
            {
                "x": round(log_density, 10),
                "d": density,
                "fz": fermi.log_fugacity,
                "bz": bose.log_fugacity,
                "fp": fermi.pressure_ratio,
                "bp": bose.pressure_ratio,
                "c": bose.condensate_fraction,
                "fo": [fermi.mean_occupation(float(x)) for x in ENERGIES],
                "bo": [bose.mean_occupation(float(x)) for x in ENERGIES],
                "fw": fermi.spectral_particle_weights(ENERGIES).tolist(),
                "bw": bose.spectral_particle_weights(ENERGIES).tolist(),
            }
        )
    return rows


def controller_source(rows: list[dict[str, Any]]) -> str:
    table = json.dumps(rows, separators=(",", ":"), allow_nan=False)
    return f'''autowatch = 1;
inlets = 1;
outlets = 7;

// Generated from the tested 3D ideal-gas model. x is log10(n*lambda_T^3).
var TABLE = {table};
var logDensity = 0.0;
var baseHz = 110.0;
var spacingHz = 38.0;
var detectionEfficiency = 0.30;

function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(hi, Number(v))); }}
function logdensity(v) {{ logDensity = clamp(v, -3.0, 2.0); update(); }}
function density(v) {{ logDensity = Math.log(Math.max(0.001, Number(v))) / Math.LN10; logDensity = clamp(logDensity, -3.0, 2.0); update(); }}
function base(v) {{ baseHz = clamp(v, 30.0, 1000.0); update(); }}
function spacing(v) {{ spacingHz = clamp(v, 1.0, 200.0); update(); }}
function detection(v) {{ detectionEfficiency = clamp(v, 0.01, 1.0); }}
function bang() {{ update(); }}

function blend(a, b, t) {{ return a + (b - a) * t; }}
function sample() {{
    var hi = 1;
    while (hi < TABLE.length && TABLE[hi].x < logDensity) hi++;
    if (hi >= TABLE.length) hi = TABLE.length - 1;
    var lo = Math.max(0, hi - 1);
    var span = TABLE[hi].x - TABLE[lo].x;
    var t = span > 0 ? (logDensity - TABLE[lo].x) / span : 0.0;
    var out = {{}};
    var scalar = ["d", "fz", "bz", "fp", "bp", "c"];
    for (var k = 0; k < scalar.length; k++) {{
        var key = scalar[k]; out[key] = blend(TABLE[lo][key], TABLE[hi][key], t);
    }}
    out.fo = []; out.bo = []; out.fw = []; out.bw = [];
    for (var i = 0; i < 10; i++) {{
        out.fo[i] = blend(TABLE[lo].fo[i], TABLE[hi].fo[i], t);
        out.bo[i] = blend(TABLE[lo].bo[i], TABLE[hi].bo[i], t);
        out.fw[i] = blend(TABLE[lo].fw[i], TABLE[hi].fw[i], t);
        out.bw[i] = blend(TABLE[lo].bw[i], TABLE[hi].bw[i], t);
    }}
    return out;
}}

function update() {{
    var s = sample();
    var fDisplay = [];
    var bDisplay = [];
    var thermalBose = Math.sqrt(Math.max(0.0, 1.0 - s.c));
    for (var i = 0; i < 10; i++) {{
        var position = i / 9.0;
        outlet(0, "target", i + 1);
        outlet(0, "freq", baseHz + i * spacingHz * s.fp);
        outlet(0, "gain", 1.0);
        outlet(0, "pan", -0.88 + 0.34 * position);
        outlet(1, "target", i + 1);
        outlet(1, "freq", baseHz + i * spacingHz * s.bp);
        outlet(1, "gain", 1.0);
        outlet(1, "pan", 0.54 + 0.34 * position);
        fDisplay.push(s.fw[i]); bDisplay.push((1.0 - s.c) * s.bw[i]);
    }}
    outlet(2, fDisplay);
    outlet(3, bDisplay);
    outlet(4, 0.36 * Math.sqrt(Math.max(0.0, s.c)));
    outlet(5, s.d, s.fp, s.bp, s.c, baseHz * 0.5);
    var regime = s.d < 0.1 ? "CLASSICAL" : (s.c > 0.0 ? "BOSE CONDENSED" : "QUANTUM DEGENERATE");
    outlet(6, "set", regime + " | D=n*lambda^3=" + s.d.toFixed(4) +
        " | Fermi P/nkT=" + s.fp.toFixed(4) + " (blocking/stiffening)" +
        " | Bose P/nkT=" + s.bp.toFixed(4) + " | condensate=" + (100*s.c).toFixed(1) + "%");
}}

// One detector window. A fermionic one-particle state is Bernoulli-valued:
// n is exactly 0 or 1. A bosonic state is geometrically distributed and can
// produce n=0,1,2,... simultaneous detections. Loss/detection efficiency
// preserves both distribution families while controlling event density.
function tick() {{
    var s = sample();
    var thermalBose = Math.max(0.0, 1.0 - s.c);
    for (var i = 0; i < 10; i++) {{
        var fMean = Math.min(1.0, detectionEfficiency * s.fo[i]);
        if (Math.random() < fMean) {{
            var fShell = Math.sqrt(Math.max(0.0, s.fw[i]));
            outlet(0, "target", i + 1);
            outlet(0, "event", 0.12 + 0.22 * fShell, 14.0);
        }}

        var bMean = detectionEfficiency * thermalBose * s.bo[i];
        if (bMean > 0.0) {{
            var ratio = bMean / (1.0 + bMean);
            var count = Math.min(32, Math.floor(Math.log(1.0 - Math.random()) / Math.log(ratio)));
            if (count > 0) {{
                var bShell = Math.sqrt(Math.max(0.0, s.bw[i]));
                var burst = Math.sqrt(count) / Math.sqrt(1.0 + 0.35 * count);
                outlet(1, "target", i + 1);
                outlet(1, "event", (0.10 + 0.20 * bShell) * burst, Math.min(260.0, 34.0 + 14.0 * count));
            }}
        }}
    }}
}}
'''


def build_voice() -> dict[str, Any]:
    boxes = [
        box("in", "newobj", [20.0, 20.0, 34.0, 22.0], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route", "newobj", [70.0, 20.0, 185.0, 22.0], text="route freq gain pan event", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
        box("freq_pack", "newobj", [25.0, 65.0, 72.0, 22.0], text="pack f 35", numinlets=2, numoutlets=1, outlettype=[""]),
        box("freq_line", "newobj", [25.0, 95.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("osc", "newobj", [25.0, 130.0, 70.0, 22.0], text="cycle~ 110.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_pack", "newobj", [120.0, 65.0, 72.0, 22.0], text="pack f 35", numinlets=2, numoutlets=1, outlettype=[""]),
        box("gain_line", "newobj", [120.0, 95.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("gain", "newobj", [70.0, 165.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("event_message", "message", [385.0, 65.0, 88.0, 22.0], text="$1, 0. $2", numinlets=2, numoutlets=1, outlettype=[""]),
        box("event_line", "newobj", [385.0, 95.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("event_gain", "newobj", [70.0, 195.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("pan_l", "newobj", [215.0, 65.0, 150.0, 22.0], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pan_r", "newobj", [215.0, 95.0, 150.0, 22.0], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pan_l_sig", "newobj", [215.0, 130.0, 45.0, 22.0], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("pan_r_sig", "newobj", [285.0, 130.0, 45.0, 22.0], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("left", "newobj", [45.0, 235.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("right", "newobj", [115.0, 235.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("out_l", "newobj", [45.0, 270.0, 48.0, 22.0], text="out~ 1", numinlets=1, numoutlets=0),
        box("out_r", "newobj", [115.0, 270.0, 48.0, 22.0], text="out~ 2", numinlets=1, numoutlets=0),
    ]
    lines = [
        line("in", 0, "route"),
        line("route", 0, "freq_pack"), line("freq_pack", 0, "freq_line"), line("freq_line", 0, "osc"),
        line("route", 1, "gain_pack"), line("gain_pack", 0, "gain_line"),
        line("osc", 0, "gain", 0), line("gain_line", 0, "gain", 1),
        line("route", 3, "event_message"), line("event_message", 0, "event_line"),
        line("gain", 0, "event_gain", 0), line("event_line", 0, "event_gain", 1),
        line("route", 2, "pan_l"), line("route", 2, "pan_r"),
        line("pan_l", 0, "pan_l_sig"), line("pan_r", 0, "pan_r_sig"),
        line("event_gain", 0, "left", 0), line("pan_l_sig", 0, "left", 1),
        line("event_gain", 0, "right", 0), line("pan_r_sig", 0, "right", 1),
        line("left", 0, "out_l"), line("right", 0, "out_r"),
    ]
    return wrap(boxes, lines, [100.0, 100.0, 500.0, 330.0])


def build_instrument() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [25.0, 18.0, 1050.0, 28.0], text="QMW QUANTUM STATISTICS INSTRUMENT v1 — PAULI'S IDEAL GAS", fontsize=18.0),
        box("subtitle", "comment", [25.0, 50.0, 1100.0, 38.0], text="One control D = n lambda_T^3. Listen to 20 ms detector windows: Fermi modes emit only singleton pips; Bose modes admit geometrically distributed multiparticle bursts and condensation.", fontsize=12.0),
        box("control_title", "comment", [25.0, 102.0, 500.0, 22.0], text="PHASE-SPACE DENSITY / WAVEFUNCTION OVERLAP", fontsize=14.0),
        box("log_label", "comment", [25.0, 140.0, 150.0, 20.0], text="log10(n lambda_T^3)"),
        box("log_density", "flonum", [180.0, 137.0, 85.0, 22.0], minimum=-3.0, maximum=2.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("log_pre", "newobj", [275.0, 137.0, 125.0, 22.0], text="prepend logdensity", numinlets=1, numoutlets=1, outlettype=[""]),
        box("sweep", "message", [415.0, 137.0, 145.0, 22.0], text="-1., 2. 30000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("sweep_line", "newobj", [570.0, 137.0, 38.0, 22.0], text="line", numinlets=2, numoutlets=1, outlettype=[""]),
        box("audition", "message", [620.0, 137.0, 42.0, 22.0], text="0.", annotation="audible D=1 comparison", numinlets=2, numoutlets=1, outlettype=[""]),
        box("critical", "message", [670.0, 137.0, 82.0, 22.0], text="0.417036", annotation="log10(zeta(3/2))", numinlets=2, numoutlets=1, outlettype=[""]),
        box("critical_note", "comment", [762.0, 140.0, 308.0, 20.0], text="D=1 audition | Bose condensation threshold"),
        box("base_label", "comment", [25.0, 180.0, 75.0, 20.0], text="base Hz"),
        box("base", "flonum", [95.0, 177.0, 75.0, 22.0], minimum=30.0, maximum=1000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("base_pre", "newobj", [180.0, 177.0, 90.0, 22.0], text="prepend base", numinlets=1, numoutlets=1, outlettype=[""]),
        box("spacing_label", "comment", [300.0, 180.0, 85.0, 20.0], text="spacing Hz"),
        box("spacing", "flonum", [385.0, 177.0, 75.0, 22.0], minimum=1.0, maximum=200.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("spacing_pre", "newobj", [470.0, 177.0, 105.0, 22.0], text="prepend spacing", numinlets=1, numoutlets=1, outlettype=[""]),
        box("event_toggle", "toggle", [610.0, 177.0, 22.0, 22.0], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("event_label", "comment", [640.0, 180.0, 115.0, 20.0], text="statistics events"),
        box("event_metro", "newobj", [760.0, 177.0, 65.0, 22.0], text="metro 20", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("tick_message", "message", [835.0, 177.0, 38.0, 22.0], text="tick", numinlets=2, numoutlets=1, outlettype=[""]),
        box("detect_label", "comment", [885.0, 180.0, 70.0, 20.0], text="detector"),
        box("detection", "flonum", [950.0, 177.0, 60.0, 22.0], minimum=0.01, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("detection_pre", "newobj", [1015.0, 177.0, 112.0, 22.0], text="prepend detection", numinlets=1, numoutlets=1, outlettype=[""]),
        box("controller", "newobj", [25.0, 225.0, 285.0, 22.0], text="js qmw_quantum_statistics_controller_v1.js", numinlets=1, numoutlets=7, outlettype=["", "", "", "", "", "", ""]),
        box("status", "message", [325.0, 225.0, 745.0, 22.0], text="initializing ideal quantum gas...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("fermi_title", "comment", [25.0, 275.0, 500.0, 24.0], text="FERMI–DIRAC — ANTISYMMETRIC / BLOCKING", fontsize=14.0),
        box("bose_title", "comment", [570.0, 275.0, 500.0, 24.0], text="BOSE–EINSTEIN — SYMMETRIC / BUNCHING", fontsize=14.0),
        box("fermi_note", "comment", [25.0, 305.0, 500.0, 38.0], text="Bernoulli occupation n={0,1}: at most one short detection per mode/window. Degeneracy pressure expands carrier spacing."),
        box("bose_note", "comment", [570.0, 305.0, 500.0, 38.0], text="Geometric occupation n={0,1,2,...}: same-mode multiparticle bursts. Above zeta(3/2), the coherent condensate grows."),
        box("fermi_slider", "multislider", [25.0, 350.0, 500.0, 115.0], size=10, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("bose_slider", "multislider", [570.0, 350.0, 500.0, 115.0], size=10, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("fermi_poly", "newobj", [25.0, 490.0, 325.0, 22.0], text="poly~ qmw_quantum_statistics_voice_v1 10 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("bose_poly", "newobj", [570.0, 490.0, 325.0, 22.0], text="poly~ qmw_quantum_statistics_voice_v1 10 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("metrics_unpack", "newobj", [350.0, 535.0, 225.0, 22.0], text="unpack f f f f f", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
        box("d_label", "comment", [25.0, 540.0, 55.0, 20.0], text="D"),
        box("d_value", "flonum", [65.0, 537.0, 90.0, 22.0], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("fp_label", "comment", [25.0, 575.0, 95.0, 20.0], text="Fermi P/nkT"),
        box("fp_value", "flonum", [125.0, 572.0, 85.0, 22.0], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("bp_label", "comment", [230.0, 575.0, 90.0, 20.0], text="Bose P/nkT"),
        box("bp_value", "flonum", [325.0, 572.0, 85.0, 22.0], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("cond_label", "comment", [430.0, 575.0, 115.0, 20.0], text="condensate fraction"),
        box("cond_value", "flonum", [550.0, 572.0, 85.0, 22.0], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("cond_pack", "newobj", [660.0, 537.0, 72.0, 22.0], text="pack f 40", numinlets=2, numoutlets=1, outlettype=[""]),
        box("cond_line", "newobj", [740.0, 537.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("cond_osc", "newobj", [805.0, 537.0, 70.0, 22.0], text="cycle~ 55.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("cond_gain", "newobj", [890.0, 537.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("cond_note", "comment", [650.0, 575.0, 420.0, 38.0], text="The central subharmonic is the macroscopic zero-momentum mode; it is silent below the critical density."),
        box("sum_l1", "newobj", [80.0, 635.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_l2", "newobj", [130.0, 635.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r1", "newobj", [250.0, 635.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("sum_r2", "newobj", [300.0, 635.0, 36.0, 22.0], text="+~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_label", "comment", [390.0, 640.0, 65.0, 20.0], text="master"),
        box("master", "flonum", [455.0, 637.0, 75.0, 22.0], minimum=0.0, maximum=0.5, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("master_pack", "newobj", [540.0, 637.0, 72.0, 22.0], text="pack f 40", numinlets=2, numoutlets=1, outlettype=[""]),
        box("master_line", "newobj", [620.0, 637.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("master_l", "newobj", [130.0, 680.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [300.0, 680.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("clip_l", "newobj", [130.0, 715.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("clip_r", "newobj", [300.0, 715.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [420.0, 685.0, 18.0, 60.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [450.0, 685.0, 18.0, 60.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [500.0, 690.0, 52.0, 52.0], numinlets=2, numoutlets=0),
        box("footer", "comment", [600.0, 680.0, 500.0, 64.0], text="Event multiplicities sample the exact Bernoulli (Fermi) and geometric (Bose) one-mode laws. Carrier spacing retains the equation-of-state mapping through the exact P/(nkT)."),
        box("init_log", "newobj", [25.0, 770.0, 100.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_base", "newobj", [135.0, 770.0, 105.0, 22.0], text="loadmess 110.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_spacing", "newobj", [250.0, 770.0, 98.0, 22.0], text="loadmess 38.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_master", "newobj", [358.0, 770.0, 98.0, 22.0], text="loadmess 0.18", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_events", "newobj", [466.0, 770.0, 88.0, 22.0], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_detection", "newobj", [564.0, 770.0, 98.0, 22.0], text="loadmess 0.3", numinlets=1, numoutlets=1, outlettype=[""]),
    ]
    lines = [
        line("log_density", 0, "log_pre"), line("log_pre", 0, "controller"),
        line("sweep", 0, "sweep_line"), line("sweep_line", 0, "log_density"),
        line("audition", 0, "log_density"), line("critical", 0, "log_density"),
        line("base", 0, "base_pre"), line("base_pre", 0, "controller"),
        line("spacing", 0, "spacing_pre"), line("spacing_pre", 0, "controller"),
        line("event_toggle", 0, "event_metro"), line("event_metro", 0, "tick_message"), line("tick_message", 0, "controller"),
        line("detection", 0, "detection_pre"), line("detection_pre", 0, "controller"),
        line("controller", 0, "fermi_poly"), line("controller", 1, "bose_poly"),
        line("controller", 2, "fermi_slider"), line("controller", 3, "bose_slider"),
        line("controller", 4, "cond_pack"), line("cond_pack", 0, "cond_line"),
        line("controller", 5, "metrics_unpack"),
        line("metrics_unpack", 0, "d_value"), line("metrics_unpack", 1, "fp_value"),
        line("metrics_unpack", 2, "bp_value"), line("metrics_unpack", 3, "cond_value"), line("metrics_unpack", 4, "cond_osc"),
        line("controller", 6, "status", 1),
        line("cond_osc", 0, "cond_gain", 0), line("cond_line", 0, "cond_gain", 1),
        line("fermi_poly", 0, "sum_l1", 0), line("bose_poly", 0, "sum_l1", 1),
        line("sum_l1", 0, "sum_l2", 0), line("cond_gain", 0, "sum_l2", 1),
        line("fermi_poly", 1, "sum_r1", 0), line("bose_poly", 1, "sum_r1", 1),
        line("sum_r1", 0, "sum_r2", 0), line("cond_gain", 0, "sum_r2", 1),
        line("master", 0, "master_pack"), line("master_pack", 0, "master_line"),
        line("sum_l2", 0, "master_l", 0), line("master_line", 0, "master_l", 1),
        line("sum_r2", 0, "master_r", 0), line("master_line", 0, "master_r", 1),
        line("master_l", 0, "clip_l"), line("master_r", 0, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"),
        line("clip_l", 0, "dac", 0), line("clip_r", 0, "dac", 1),
        line("init_log", 0, "log_density"), line("init_base", 0, "base"),
        line("init_spacing", 0, "spacing"), line("init_master", 0, "master"),
        line("init_events", 0, "event_toggle"), line("init_detection", 0, "detection"),
    ]
    return wrap(
        boxes,
        lines,
        [60.0, 40.0, 1170.0, 825.0],
        [
            {"name": "qmw_quantum_statistics_controller_v1.js", "type": "TEXT"},
            {"name": "qmw_quantum_statistics_voice_v1.maxpat", "type": "JSON"},
        ],
    )


def validate(payload: dict[str, Any], required_text: str) -> None:
    patcher = payload["patcher"]
    identifiers = {entry["box"]["id"] for entry in patcher["boxes"]}
    if len(identifiers) != len(patcher["boxes"]):
        raise RuntimeError("duplicate Max identifiers")
    for entry in patcher["lines"]:
        source = entry["patchline"]["source"][0]
        destination = entry["patchline"]["destination"][0]
        if source not in identifiers or destination not in identifiers:
            raise RuntimeError(f"dangling line {source} -> {destination}")
    texts = [entry["box"].get("text", "") for entry in patcher["boxes"]]
    if not any(text.startswith(required_text) for text in texts):
        raise RuntimeError(f"missing required object {required_text}")


def main() -> None:
    rows = lookup_rows()
    voice = build_voice()
    instrument = build_instrument()
    validate(voice, "route freq gain pan event")
    validate(instrument, "poly~ qmw_quantum_statistics_voice_v1")
    (ROOT / "qmw_quantum_statistics_controller_v1.js").write_text(controller_source(rows), encoding="utf-8")
    (ROOT / "qmw_quantum_statistics_voice_v1.maxpat").write_text(json.dumps(voice, indent=2) + "\n", encoding="utf-8")
    (ROOT / "QMW_Quantum_Statistics_Instrument_v1.maxpat").write_text(json.dumps(instrument, indent=2) + "\n", encoding="utf-8")
    print(f"generated quantum-statistics Max instrument with {len(rows)} thermodynamic states")


if __name__ == "__main__":
    main()
