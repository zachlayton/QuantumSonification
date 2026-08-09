#!/usr/bin/env python3
"""Generate the Pauli Statistical Grainflow Max 9 instrument."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def box(identifier: str, maxclass: str, rect: list[float], **values: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    payload.update(values)
    return {"box": payload}


def line(source: str, outlet: int, destination: str, inlet: int = 0) -> dict[str, Any]:
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def build() -> dict[str, Any]:
    boxes = [
        box("title", "comment", [25.0, 16.0, 850.0, 28.0], text="QMW PAULI STATISTICAL GRAINFLOW v1 — THE ENERGY SHELL", fontsize=18.0),
        box("subtitle", "comment", [25.0, 47.0, 1110.0, 38.0], text="Quantum wavetable atlas -> six addressed streams -> exact occupation scheduler -> dual Grainflow 2.1 engines. Grains are events; streams are modes; particle labels never enter the renderer."),
        box("source_title", "comment", [25.0, 96.0, 420.0, 22.0], text="DOUBLE-BUFFERED QUANTUM WAVETABLE ATLAS", fontsize=14.0),
        box("source", "newobj", [25.0, 130.0, 280.0, 22.0], text="buffer~ qmw_wavetable @samps 256 @channels 1", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("atlas_a", "newobj", [25.0, 163.0, 330.0, 22.0], text="buffer~ qmw_pauli_atlas_A @samps 98304 @channels 1", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("atlas_b", "newobj", [25.0, 196.0, 330.0, 22.0], text="buffer~ qmw_pauli_atlas_B @samps 98304 @channels 1", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("atlas_js", "newobj", [385.0, 130.0, 245.0, 22.0], text="js qmw_quantum_wavetable_atlas_v1.js", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("capture", "message", [385.0, 165.0, 88.0, 22.0], text="render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("seed", "message", [483.0, 165.0, 118.0, 22.0], text="seed, render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("capture_note", "comment", [620.0, 163.0, 515.0, 34.0], text="CAPTURE reads the shared qmw_wavetable. SEED+CAPTURE supplies a local test source. Atlas A/B never change while their Grainflow engine is foregrounded."),
        box("atlas_status", "message", [385.0, 202.0, 750.0, 22.0], text="waiting for atlas commit...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_b_pack", "newobj", [650.0, 130.0, 82.0, 22.0], text="pack f 120", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_b", "newobj", [742.0, 130.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("xfade_a_expr", "newobj", [805.0, 130.0, 82.0, 22.0], text="expr 1.-$f1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("xfade_a_pack", "newobj", [897.0, 130.0, 82.0, 22.0], text="pack f 120", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_a", "newobj", [989.0, 130.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),

        box("stats_title", "comment", [25.0, 245.0, 420.0, 22.0], text="CANONICAL OCCUPATION SCHEDULER", fontsize=14.0),
        box("stats_label", "comment", [25.0, 280.0, 92.0, 20.0], text="statistics"),
        box("stats", "umenu", [115.0, 277.0, 130.0, 22.0], items=["fermion", ",", "boson", ",", "classical"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("stats_pre", "newobj", [255.0, 277.0, 112.0, 22.0], text="prepend statistics", numinlets=1, numoutlets=1, outlettype=[""]),
        box("particles_label", "comment", [390.0, 280.0, 80.0, 20.0], text="particles N"),
        box("particles", "number", [475.0, 277.0, 65.0, 22.0], minimum=0, maximum=12, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("particles_pre", "newobj", [550.0, 277.0, 108.0, 22.0], text="prepend particles", numinlets=1, numoutlets=1, outlettype=[""]),
        box("run", "toggle", [680.0, 276.0, 24.0, 24.0], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("run_label", "comment", [710.0, 280.0, 108.0, 20.0], text="sample ensemble"),
        box("metro", "newobj", [825.0, 277.0, 72.0, 22.0], text="metro 400", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("scheduler", "newobj", [25.0, 320.0, 270.0, 22.0], text="js qmw_pauli_grainflow_scheduler_v1.js", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
        box("occupancy", "multislider", [315.0, 315.0, 335.0, 42.0], size=6, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("stat_status", "message", [670.0, 320.0, 465.0, 22.0], text="initializing statistical shell...", numinlets=2, numoutlets=1, outlettype=[""]),

        box("field_label", "comment", [25.0, 378.0, 78.0, 20.0], text="field B"),
        box("field", "flonum", [98.0, 375.0, 70.0, 22.0], minimum=0.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("field_pre", "newobj", [178.0, 375.0, 90.0, 22.0], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""]),
        box("center_label", "comment", [290.0, 378.0, 92.0, 20.0], text="shell center"),
        box("center", "flonum", [382.0, 375.0, 70.0, 22.0], minimum=-20.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("center_pre", "newobj", [462.0, 375.0, 95.0, 22.0], text="prepend center", numinlets=1, numoutlets=1, outlettype=[""]),
        box("width_label", "comment", [580.0, 378.0, 82.0, 20.0], text="shell width"),
        box("width", "flonum", [665.0, 375.0, 70.0, 22.0], minimum=0.0, maximum=40.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("width_pre", "newobj", [745.0, 375.0, 92.0, 22.0], text="prepend width", numinlets=1, numoutlets=1, outlettype=[""]),
        box("entropy_label", "comment", [855.0, 378.0, 82.0, 20.0], text="exploration"),
        box("entropy", "flonum", [938.0, 375.0, 70.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("entropy_pre", "newobj", [1018.0, 375.0, 98.0, 22.0], text="prepend entropy", numinlets=1, numoutlets=1, outlettype=[""]),

        box("coherence_label", "comment", [25.0, 418.0, 82.0, 20.0], text="coherence"),
        box("coherence", "flonum", [98.0, 415.0, 70.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("coherence_pre", "newobj", [178.0, 415.0, 108.0, 22.0], text="prepend coherence", numinlets=1, numoutlets=1, outlettype=[""]),
        box("density_label", "comment", [310.0, 418.0, 76.0, 20.0], text="event density"),
        box("density", "flonum", [392.0, 415.0, 70.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("density_pre", "newobj", [472.0, 415.0, 100.0, 22.0], text="prepend density", numinlets=1, numoutlets=1, outlettype=[""]),
        box("deviation_label", "comment", [595.0, 418.0, 108.0, 20.0], text="energy deviation"),
        box("deviation", "flonum", [705.0, 415.0, 70.0, 22.0], minimum=0.0, maximum=24.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("deviation_pre", "newobj", [785.0, 415.0, 110.0, 22.0], text="prepend deviation", numinlets=1, numoutlets=1, outlettype=[""]),

        box("grain_title", "comment", [25.0, 465.0, 500.0, 22.0], text="GRAINFLOW MULTICHANNEL RENDERER — 6 streams x 4 grains", fontsize=14.0),
        box("clock_label", "comment", [25.0, 500.0, 90.0, 20.0], text="grain clock Hz"),
        box("clock", "flonum", [120.0, 497.0, 72.0, 22.0], minimum=0.05, maximum=200.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("clock_mc", "newobj", [205.0, 497.0, 168.0, 22.0], text="mc.phasor~ 10. @chans 6", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("trav_label", "comment", [395.0, 500.0, 100.0, 20.0], text="atlas scan Hz"),
        box("trav", "flonum", [495.0, 497.0, 72.0, 22.0], minimum=-4.0, maximum=4.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("trav_mc", "newobj", [580.0, 497.0, 170.0, 22.0], text="mc.phasor~ 0.18 @chans 6", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("fm_index_label", "comment", [770.0, 480.0, 70.0, 20.0], text="FM index"),
        box("fm_index", "flonum", [840.0, 497.0, 70.0, 22.0], minimum=0.0, maximum=2.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("fm_index_pack", "newobj", [920.0, 497.0, 78.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("fm_index_line", "newobj", [1008.0, 497.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("fm_cycle", "newobj", [770.0, 535.0, 285.0, 22.0], text="mc.cycle~ @chans 6 @values 0.19 0.23 0.29 0.31 0.37 0.43", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("fm_mult", "newobj", [1065.0, 535.0, 58.0, 22.0], text="mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("am_mc", "newobj", [1010.0, 565.0, 128.0, 22.0], text="mc.sig~ 1. @chans 6", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("env_label", "comment", [25.0, 598.0, 75.0, 20.0], text="envelope"),
        box("env_menu", "umenu", [105.0, 595.0, 185.0, 22.0], items=["qmw_env_hanning", ",", "qmw_env_blackman", ",", "qmw_env_pluck"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("env_pre", "newobj", [300.0, 595.0, 88.0, 22.0], text="prepend env", numinlets=1, numoutlets=1, outlettype=[""]),
        box("env_hanning", "newobj", [410.0, 595.0, 250.0, 22.0], text="buffer~ qmw_env_hanning grainflow.Hanning.aif", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("env_blackman", "newobj", [675.0, 595.0, 255.0, 22.0], text="buffer~ qmw_env_blackman grainflow.Blackman.aif", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("env_pluck", "newobj", [945.0, 595.0, 190.0, 22.0], text="buffer~ qmw_env_pluck grainflow.Pluck.aif", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),

        box("grain_a", "newobj", [25.0, 635.0, 320.0, 22.0], text="grainflow.streams~ 6 4 qmw_pauli_atlas_A", numinlets=4, numoutlets=2, outlettype=["multichannelsignal", ""]),
        box("grain_b", "newobj", [365.0, 635.0, 320.0, 22.0], text="grainflow.streams~ 6 4 qmw_pauli_atlas_B", numinlets=4, numoutlets=2, outlettype=["multichannelsignal", ""]),
        box("gain_a", "newobj", [125.0, 675.0, 58.0, 22.0], text="mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("gain_b", "newobj", [465.0, 675.0, 58.0, 22.0], text="mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("mc_sum", "newobj", [290.0, 710.0, 58.0, 22.0], text="mc.+~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("mixdown", "newobj", [275.0, 745.0, 180.0, 22.0], text="mc.mixdown~ 2 @autogain 1", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("unpack", "newobj", [305.0, 780.0, 90.0, 22.0], text="mc.unpack~ 2", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("master_label", "comment", [485.0, 750.0, 70.0, 20.0], text="master"),
        box("master", "flonum", [550.0, 747.0, 70.0, 22.0], minimum=0.0, maximum=0.5, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("master_pack", "newobj", [630.0, 747.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("master_line", "newobj", [715.0, 747.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("source_monitor_label", "comment", [785.0, 750.0, 105.0, 20.0], text="source monitor"),
        box("source_monitor", "flonum", [895.0, 747.0, 70.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("source_monitor_default", "newobj", [975.0, 747.0, 92.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("source_monitor_phasor", "newobj", [1075.0, 747.0, 78.0, 22.0], text="phasor~ 55.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("source_monitor_wave", "newobj", [1160.0, 747.0, 145.0, 22.0], text="wave~ qmw_wavetable", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("source_monitor_mul", "newobj", [1315.0, 747.0, 42.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_l", "newobj", [280.0, 815.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [380.0, 815.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("clip_l", "newobj", [280.0, 850.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("clip_r", "newobj", [380.0, 850.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [495.0, 805.0, 18.0, 70.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [525.0, 805.0, 18.0, 70.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [575.0, 815.0, 52.0, 52.0], numinlets=2, numoutlets=0),
        box("grain_info_a", "message", [710.0, 635.0, 205.0, 22.0], text="A grain metadata", numinlets=2, numoutlets=1, outlettype=[""]),
        box("grain_info_b", "message", [930.0, 635.0, 205.0, 22.0], text="B grain metadata", numinlets=2, numoutlets=1, outlettype=[""]),

        box("init", "newobj", [25.0, 895.0, 105.0, 22.0], text="loadmess initialize", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_render", "newobj", [140.0, 895.0, 105.0, 22.0], text="loadmess bang", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_render_delay", "newobj", [140.0, 957.0, 70.0, 22.0], text="delay 150", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("init_render_message", "message", [220.0, 957.0, 82.0, 22.0], text="seed, render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("init_stats", "newobj", [255.0, 895.0, 120.0, 22.0], text="loadmess fermion", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_particles", "newobj", [385.0, 895.0, 88.0, 22.0], text="loadmess 4", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_field", "newobj", [483.0, 895.0, 88.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_center", "newobj", [581.0, 895.0, 88.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_width", "newobj", [679.0, 895.0, 88.0, 22.0], text="loadmess 4.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_entropy", "newobj", [777.0, 895.0, 96.0, 22.0], text="loadmess 0.35", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_coherence", "newobj", [883.0, 895.0, 96.0, 22.0], text="loadmess 0.75", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_density", "newobj", [989.0, 895.0, 96.0, 22.0], text="loadmess 0.88", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_deviation", "newobj", [25.0, 927.0, 88.0, 22.0], text="loadmess 1.5", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_clock", "newobj", [123.0, 927.0, 88.0, 22.0], text="loadmess 10.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_trav", "newobj", [221.0, 927.0, 88.0, 22.0], text="loadmess 0.18", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_env", "newobj", [319.0, 927.0, 128.0, 22.0], text="loadmess 0", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_master", "newobj", [457.0, 927.0, 96.0, 22.0], text="loadmess 0.16", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_run", "newobj", [563.0, 927.0, 88.0, 22.0], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_run_delay", "newobj", [563.0, 957.0, 70.0, 22.0], text="delay 250", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("init_run_value", "message", [643.0, 957.0, 32.0, 22.0], text="1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("init_fm_index", "newobj", [661.0, 927.0, 96.0, 22.0], text="loadmess 0.08", numinlets=1, numoutlets=1, outlettype=[""]),
    ]

    lines = [
        line("capture", 0, "atlas_js"), line("seed", 0, "atlas_js"),
        line("atlas_js", 0, "xfade_b_pack"), line("xfade_b_pack", 0, "xfade_b"),
        line("atlas_js", 0, "xfade_a_expr"), line("xfade_a_expr", 0, "xfade_a_pack"), line("xfade_a_pack", 0, "xfade_a"),
        line("atlas_js", 1, "atlas_status", 1),
        line("stats", 1, "stats_pre"), line("stats_pre", 0, "scheduler"),
        line("particles", 0, "particles_pre"), line("particles_pre", 0, "scheduler"),
        line("run", 0, "metro"), line("metro", 0, "scheduler"), line("scheduler", 3, "metro", 1),
        line("scheduler", 0, "grain_a"), line("scheduler", 0, "grain_b"),
        line("run", 0, "grain_a"), line("run", 0, "grain_b"),
        line("scheduler", 1, "occupancy"), line("scheduler", 2, "stat_status", 1),
        line("field", 0, "field_pre"), line("field_pre", 0, "scheduler"),
        line("center", 0, "center_pre"), line("center_pre", 0, "scheduler"),
        line("width", 0, "width_pre"), line("width_pre", 0, "scheduler"),
        line("entropy", 0, "entropy_pre"), line("entropy_pre", 0, "scheduler"),
        line("coherence", 0, "coherence_pre"), line("coherence_pre", 0, "scheduler"),
        line("density", 0, "density_pre"), line("density_pre", 0, "scheduler"),
        line("deviation", 0, "deviation_pre"), line("deviation_pre", 0, "scheduler"),
        line("clock", 0, "clock_mc"), line("trav", 0, "trav_mc"),
        line("clock_mc", 0, "grain_a", 0), line("clock_mc", 0, "grain_b", 0),
        line("trav_mc", 0, "grain_a", 1), line("trav_mc", 0, "grain_b", 1),
        line("fm_index", 0, "fm_index_pack"), line("fm_index_pack", 0, "fm_index_line"),
        line("fm_cycle", 0, "fm_mult", 0), line("fm_index_line", 0, "fm_mult", 1),
        line("fm_mult", 0, "grain_a", 2), line("fm_mult", 0, "grain_b", 2),
        line("am_mc", 0, "grain_a", 3), line("am_mc", 0, "grain_b", 3),
        line("env_menu", 1, "env_pre"), line("env_pre", 0, "grain_a"), line("env_pre", 0, "grain_b"),
        line("grain_a", 0, "gain_a", 0), line("xfade_a", 0, "gain_a", 1),
        line("grain_b", 0, "gain_b", 0), line("xfade_b", 0, "gain_b", 1),
        line("grain_a", 1, "grain_info_a", 1), line("grain_b", 1, "grain_info_b", 1),
        line("gain_a", 0, "mc_sum", 0), line("gain_b", 0, "mc_sum", 1),
        line("mc_sum", 0, "mixdown"), line("mixdown", 0, "unpack"),
        line("master", 0, "master_pack"), line("master_pack", 0, "master_line"),
        line("unpack", 0, "master_l", 0), line("master_line", 0, "master_l", 1),
        line("unpack", 1, "master_r", 0), line("master_line", 0, "master_r", 1),
        line("source_monitor_default", 0, "source_monitor"), line("source_monitor", 0, "source_monitor_mul", 1),
        line("source_monitor_phasor", 0, "source_monitor_wave"), line("source_monitor_wave", 0, "source_monitor_mul"),
        line("source_monitor_mul", 0, "master_l", 0), line("source_monitor_mul", 0, "master_r", 0),
        line("master_l", 0, "clip_l"), line("master_r", 0, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"),
        line("clip_l", 0, "dac", 0), line("clip_r", 0, "dac", 1),
        line("init", 0, "scheduler"),
        line("init_render", 0, "init_render_delay"), line("init_render_delay", 0, "init_render_message"), line("init_render_message", 0, "atlas_js"),
        line("init_stats", 0, "stats"), line("init_particles", 0, "particles"),
        line("init_field", 0, "field"), line("init_center", 0, "center"), line("init_width", 0, "width"),
        line("init_entropy", 0, "entropy"), line("init_coherence", 0, "coherence"),
        line("init_density", 0, "density"), line("init_deviation", 0, "deviation"),
        line("init_clock", 0, "clock"), line("init_trav", 0, "trav"),
        line("init_env", 0, "env_menu"), line("init_master", 0, "master"),
        line("init_run", 0, "init_run_delay"), line("init_run_delay", 0, "init_run_value"), line("init_run_value", 0, "run"),
        line("init_fm_index", 0, "fm_index"),
    ]

    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [55.0, 35.0, 1180.0, 990.0],
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "qmw_quantum_wavetable_atlas_v1.js", "type": "TEXT"},
            {"name": "qmw_pauli_grainflow_scheduler_v1.js", "type": "TEXT"},
            {"name": "grainflow.streams~.maxpat", "type": "JSON"},
            {"name": "grainflow~.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
    return {"patcher": patcher}


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes_by_id = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    identifiers = set(boxes_by_id)
    if len(identifiers) != len(patcher["boxes"]):
        raise RuntimeError("duplicate Max box identifiers")
    connections: set[tuple[str, int, str, int]] = set()
    for entry in patcher["lines"]:
        source, source_outlet = entry["patchline"]["source"]
        destination, destination_inlet = entry["patchline"]["destination"]
        if source not in identifiers or destination not in identifiers:
            raise RuntimeError(f"dangling patchline {source} -> {destination}")
        if source_outlet >= boxes_by_id[source].get("numoutlets", 0):
            raise RuntimeError(f"invalid source outlet {source}[{source_outlet}]")
        if destination_inlet >= boxes_by_id[destination].get("numinlets", 0):
            raise RuntimeError(f"invalid destination inlet {destination}[{destination_inlet}]")
        connections.add((source, source_outlet, destination, destination_inlet))
    texts = [entry["box"].get("text", "") for entry in patcher["boxes"]]
    if texts.count("grainflow.streams~ 6 4 qmw_pauli_atlas_A") != 1:
        raise RuntimeError("missing A Grainflow stream bank")
    if texts.count("grainflow.streams~ 6 4 qmw_pauli_atlas_B") != 1:
        raise RuntimeError("missing B Grainflow stream bank")
    if texts.count("mc.phasor~ 10. @chans 6") != 1 or texts.count("mc.phasor~ 0.18 @chans 6") != 1:
        raise RuntimeError("missing six-channel clock or traversal signal")
    if texts.count("mc.cycle~ @chans 6 @values 0.19 0.23 0.29 0.31 0.37 0.43") != 1:
        raise RuntimeError("missing six-channel FM modulation bank")
    if not {"buffer~ qmw_pauli_atlas_A @samps 98304 @channels 1", "buffer~ qmw_pauli_atlas_B @samps 98304 @channels 1"}.issubset(texts):
        raise RuntimeError("missing double-buffered atlas")
    required_connections = {
        ("scheduler", 0, "grain_a", 0), ("scheduler", 0, "grain_b", 0),
        ("clock_mc", 0, "grain_a", 0), ("clock_mc", 0, "grain_b", 0),
        ("trav_mc", 0, "grain_a", 1), ("trav_mc", 0, "grain_b", 1),
        ("fm_mult", 0, "grain_a", 2), ("fm_mult", 0, "grain_b", 2),
        ("am_mc", 0, "grain_a", 3), ("am_mc", 0, "grain_b", 3),
        ("grain_a", 0, "gain_a", 0), ("grain_b", 0, "gain_b", 0),
        ("clip_l", 0, "dac", 0), ("clip_r", 0, "dac", 1),
    }
    missing = required_connections - connections
    if missing:
        raise RuntimeError(f"missing required signal or message connections: {sorted(missing)}")


def main() -> None:
    payload = build()
    validate(payload)
    output = ROOT / "QMW_Pauli_Statistical_Grainflow_v1.maxpat"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")


if __name__ == "__main__":
    main()
