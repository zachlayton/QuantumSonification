#!/usr/bin/env python3
"""Generate the Pauli MuBu Corpus Instrument for Max 9."""

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
    mode_seed = (
        "clear, append -1 -1 -2 0.083333 1 mode_1, "
        "append -1 1 0 0.25 2 mode_2, "
        "append 0 -1 -1 0.416667 3 mode_3, "
        "append 0 1 1 0.583333 4 mode_4, "
        "append 1 -1 0 0.75 5 mode_5, "
        "append 1 1 2 0.916667 6 mode_6"
    )
    boxes = [
        box("title", "comment", [25.0, 15.0, 1080.0, 28.0], text="QMW PAULI MuBu CORPUS INSTRUMENT v1 — THE ENERGY SHELL AS MEMORY", fontsize=18.0),
        box("subtitle", "comment", [25.0, 45.0, 1180.0, 35.0], text="Quantum wavetable atlas + exact Pauli occupations + per-event MuBu grains + persistent mode/state/grain tracks. MuBu 1.10.7; six MC mode outputs."),

        box("source_title", "comment", [25.0, 90.0, 450.0, 22.0], text="DOUBLE-BUFFERED QUANTUM SOURCE", fontsize=14.0),
        box("source", "newobj", [25.0, 120.0, 285.0, 22.0], text="buffer~ qmw_wavetable @samps 256", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("atlas_a", "newobj", [25.0, 150.0, 345.0, 22.0], text="buffer~ qmw_pauli_mubu_atlas_A @samps 98304", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        box("atlas_b", "newobj", [25.0, 180.0, 345.0, 22.0], text="buffer~ qmw_pauli_mubu_atlas_B @samps 98304", numinlets=1, numoutlets=2, outlettype=["float", "bang"]),
        # A MuBu container automatically associates with a same-named buffer~.
        # The granular engines resolve these containers, not bare buffers.
        box("atlas_mubu_a", "newobj", [25.0, 210.0, 235.0, 22.0], text="mubu qmw_pauli_mubu_atlas_A", numinlets=1, numoutlets=1, outlettype=[""], hidden=1),
        box("atlas_mubu_b", "newobj", [270.0, 210.0, 235.0, 22.0], text="mubu qmw_pauli_mubu_atlas_B", numinlets=1, numoutlets=1, outlettype=[""], hidden=1),
        box("atlas_js", "newobj", [395.0, 120.0, 238.0, 22.0], text="js qmw_mubu_wavetable_atlas_v1.js", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("capture", "message", [395.0, 152.0, 65.0, 22.0], text="render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("seed", "message", [470.0, 152.0, 112.0, 22.0], text="seed, render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("atlas_status", "message", [395.0, 184.0, 335.0, 22.0], text="waiting for atlas commit...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_b_pack", "newobj", [395.0, 216.0, 82.0, 22.0], text="pack f 120", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_b", "newobj", [487.0, 216.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("xfade_a_expr", "newobj", [545.0, 216.0, 82.0, 22.0], text="expr 1.-$f1", numinlets=1, numoutlets=1, outlettype=[""]),
        box("xfade_a_pack", "newobj", [637.0, 216.0, 82.0, 22.0], text="pack f 120", numinlets=2, numoutlets=1, outlettype=[""]),
        box("xfade_a", "newobj", [729.0, 216.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),

        box("corpus_title", "comment", [790.0, 90.0, 410.0, 22.0], text="MuBu CORPUS: MODES / STATES / GRAINS", fontsize=14.0),
        # MuBu predefinitions must be instantiated before the named container.
        box("mode_track", "newobj", [790.0, 305.0, 420.0, 22.0], text="mubu.track qmw_pauli_mubu_corpus 1 modes @matrixcols 5 @matrixcolnames ml two_ms g position mode @extradata label @info gui \"interface multiwave, bounds -2 6, autobounds 0\" @predef yes", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("state_track", "newobj", [790.0, 335.0, 420.0, 22.0], text="mubu.track qmw_pauli_mubu_corpus 2 states @matrixcols 11 @matrixcolnames N M Omega entropy B occ1 occ2 occ3 occ4 occ5 occ6 @timetagged yes @extradata label @maxsize 4096 @ring 1 @info gui \"interface multibpf, bounds 0 12, autobounds 0, paramcols occ1 occ2 occ3 occ4 occ5 occ6\" @predef yes", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("grain_track", "newobj", [790.0, 365.0, 420.0, 22.0], text="mubu.track qmw_pauli_mubu_corpus 3 grains @matrixcols 5 @matrixcolnames mode position_ms resampling_cents duration_ms level_db @timetagged yes @extradata label @maxsize 16384 @ring 1 @info gui \"interface bpf, bounds 0 6, autobounds 0, paramcols mode\" @predef yes", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("corpus", "imubu", [790.0, 120.0, 420.0, 175.0], name="qmw_pauli_mubu_corpus", numinlets=1, numoutlets=1, outlettype=[""], embed=0, autobounds=0, autoupdate=500.0, autorefreshrate=1, maintrack=2, tabs_visible=1, toolbar_visible=2, bufferchooser_visible=0, domain_bounds=[0.0, 30000.0], domainruler_visible=1, domainscrollbar_visible=1, tool="cursor"),
        box("mode_seed", "message", [790.0, 395.0, 420.0, 22.0], text=mode_seed, numinlets=2, numoutlets=1, outlettype=[""]),
        box("corpus_note", "comment", [790.0, 423.0, 420.0, 32.0], text="The state and grain tracks are bounded ring memories. Double-click a mubu.track or use imubu tabs to inspect the corpus while playing."),
        box("state_append_route", "newobj", [790.0, 460.0, 88.0, 22.0], text="route append", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("state_time", "newobj", [888.0, 460.0, 65.0, 22.0], text="unpack f", numinlets=1, numoutlets=1, outlettype=[""]),
        box("view_speedlim", "newobj", [963.0, 460.0, 100.0, 22.0], text="speedlim 1000", numinlets=2, numoutlets=1, outlettype=[""]),
        box("view_trigger", "newobj", [1073.0, 460.0, 50.0, 22.0], text="t f f", numinlets=1, numoutlets=2, outlettype=["float", "float"]),
        box("view_start", "newobj", [790.0, 495.0, 165.0, 22.0], text="expr max(0.,$f1-30000.)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("view_end", "newobj", [965.0, 495.0, 165.0, 22.0], text="expr max(30000.,$f1)", numinlets=1, numoutlets=1, outlettype=[""]),
        box("view_pack", "newobj", [1140.0, 495.0, 80.0, 22.0], text="pack f f", numinlets=2, numoutlets=1, outlettype=[""]),
        box("view_freeze_label", "comment", [790.0, 533.0, 82.0, 20.0], text="freeze view"),
        box("view_freeze", "toggle", [875.0, 530.0, 24.0, 24.0], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("view_freeze_pre", "newobj", [910.0, 530.0, 105.0, 22.0], text="prepend freeze", numinlets=1, numoutlets=1, outlettype=[""]),
        box("view_domain", "newobj", [1035.0, 530.0, 185.0, 22.0], text="prepend domain bounds", numinlets=1, numoutlets=1, outlettype=[""]),

        box("stats_title", "comment", [25.0, 270.0, 500.0, 22.0], text="EXACT OCCUPATION → ASYNCHRONOUS GRAIN EVENTS", fontsize=14.0),
        box("stats_label", "comment", [25.0, 304.0, 82.0, 20.0], text="statistics"),
        box("stats", "umenu", [110.0, 301.0, 120.0, 22.0], items=["fermion", ",", "boson", ",", "classical"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("stats_pre", "newobj", [240.0, 301.0, 112.0, 22.0], text="prepend statistics", numinlets=1, numoutlets=1, outlettype=[""]),
        box("particles_label", "comment", [370.0, 304.0, 76.0, 20.0], text="particles N"),
        box("particles", "number", [450.0, 301.0, 60.0, 22.0], minimum=0, maximum=12, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("particles_pre", "newobj", [520.0, 301.0, 108.0, 22.0], text="prepend particles", numinlets=1, numoutlets=1, outlettype=[""]),
        box("run", "toggle", [650.0, 300.0, 24.0, 24.0], numinlets=1, numoutlets=1, outlettype=["int"]),
        box("run_label", "comment", [680.0, 304.0, 90.0, 20.0], text="emit grains"),
        box("metro", "newobj", [25.0, 335.0, 72.0, 22.0], text="metro 55", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("scheduler", "newobj", [110.0, 335.0, 245.0, 22.0], text="js qmw_pauli_mubu_scheduler_v1.js", numinlets=1, numoutlets=6, outlettype=["", "", "", "", "", ""]),
        box("occupancy", "multislider", [370.0, 332.0, 250.0, 38.0], size=6, setminmax=[0.0, 12.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("stat_status", "message", [25.0, 375.0, 730.0, 22.0], text="initializing statistical shell...", numinlets=2, numoutlets=1, outlettype=[""]),

        box("field_label", "comment", [25.0, 414.0, 56.0, 20.0], text="field B"),
        box("field", "flonum", [82.0, 411.0, 62.0, 22.0], minimum=0.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("field_pre", "newobj", [150.0, 411.0, 90.0, 22.0], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""]),
        box("center_label", "comment", [250.0, 414.0, 80.0, 20.0], text="shell center"),
        box("center", "flonum", [330.0, 411.0, 62.0, 22.0], minimum=-20.0, maximum=20.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("center_pre", "newobj", [400.0, 411.0, 95.0, 22.0], text="prepend center", numinlets=1, numoutlets=1, outlettype=[""]),
        box("width_label", "comment", [505.0, 414.0, 72.0, 20.0], text="shell width"),
        box("width", "flonum", [580.0, 411.0, 62.0, 22.0], minimum=0.0, maximum=40.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("width_pre", "newobj", [650.0, 411.0, 92.0, 22.0], text="prepend width", numinlets=1, numoutlets=1, outlettype=[""]),

        box("explore_label", "comment", [25.0, 450.0, 76.0, 20.0], text="exploration"),
        box("explore", "flonum", [102.0, 447.0, 62.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("explore_pre", "newobj", [170.0, 447.0, 98.0, 22.0], text="prepend entropy", numinlets=1, numoutlets=1, outlettype=[""]),
        box("coherence_label", "comment", [278.0, 450.0, 72.0, 20.0], text="coherence"),
        box("coherence", "flonum", [350.0, 447.0, 62.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("coherence_pre", "newobj", [420.0, 447.0, 108.0, 22.0], text="prepend coherence", numinlets=1, numoutlets=1, outlettype=[""]),
        box("density_label", "comment", [538.0, 450.0, 54.0, 20.0], text="density"),
        box("density", "flonum", [595.0, 447.0, 62.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("density_pre", "newobj", [665.0, 447.0, 95.0, 22.0], text="prepend density", numinlets=1, numoutlets=1, outlettype=[""]),

        box("period_label", "comment", [25.0, 486.0, 78.0, 20.0], text="event ms"),
        box("period", "flonum", [102.0, 483.0, 62.0, 22.0], minimum=5.0, maximum=2000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("period_pre", "newobj", [170.0, 483.0, 115.0, 22.0], text="prepend grainperiod", numinlets=1, numoutlets=1, outlettype=[""]),
        box("duration_label", "comment", [295.0, 486.0, 74.0, 20.0], text="duration ms"),
        box("duration", "flonum", [370.0, 483.0, 62.0, 22.0], minimum=2.0, maximum=5000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("duration_pre", "newobj", [440.0, 483.0, 102.0, 22.0], text="prepend duration", numinlets=1, numoutlets=1, outlettype=[""]),
        box("positionvar_label", "comment", [552.0, 486.0, 82.0, 20.0], text="position var"),
        box("positionvar", "flonum", [635.0, 483.0, 62.0, 22.0], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("positionvar_pre", "newobj", [705.0, 483.0, 118.0, 22.0], text="prepend positionvar", numinlets=1, numoutlets=1, outlettype=[""]),

        box("deviation_label", "comment", [25.0, 522.0, 92.0, 20.0], text="deviation st"),
        box("deviation", "flonum", [118.0, 519.0, 62.0, 22.0], minimum=0.0, maximum=24.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("deviation_pre", "newobj", [188.0, 519.0, 110.0, 22.0], text="prepend deviation", numinlets=1, numoutlets=1, outlettype=[""]),
        box("fm_label", "comment", [310.0, 522.0, 100.0, 20.0], text="grain FM cents"),
        box("fm", "flonum", [410.0, 519.0, 62.0, 22.0], minimum=0.0, maximum=2400.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("fm_pre", "newobj", [480.0, 519.0, 100.0, 22.0], text="prepend fmindex", numinlets=1, numoutlets=1, outlettype=[""]),
        box("sr", "newobj", [600.0, 519.0, 72.0, 22.0], text="adstatus sr", numinlets=1, numoutlets=1, outlettype=[""]),
        box("sr_pre", "newobj", [680.0, 519.0, 125.0, 22.0], text="prepend samplerate", numinlets=1, numoutlets=1, outlettype=[""]),

        box("mubu_title", "comment", [25.0, 565.0, 500.0, 22.0], text="MuBu PER-GRAIN PARAMETERS", fontsize=14.0),
        box("window_label", "comment", [25.0, 600.0, 58.0, 20.0], text="window"),
        box("window", "umenu", [85.0, 597.0, 110.0, 22.0], items=["cosine", ",", "trapezoid", ",", "sine"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
        box("window_pre", "newobj", [205.0, 597.0, 100.0, 22.0], text="prepend window", numinlets=1, numoutlets=1, outlettype=[""]),
        box("filtermode_label", "comment", [320.0, 600.0, 72.0, 20.0], text="filter mode"),
        box("filtermode", "number", [395.0, 597.0, 52.0, 22.0], minimum=0, maximum=4, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("filtermode_pre", "newobj", [455.0, 597.0, 115.0, 22.0], text="prepend filtermode", numinlets=1, numoutlets=1, outlettype=[""]),
        box("filterfreq_label", "comment", [585.0, 600.0, 66.0, 20.0], text="filter Hz"),
        box("filterfreq", "flonum", [650.0, 597.0, 70.0, 22.0], minimum=20.0, maximum=20000.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("filterfreq_pre", "newobj", [730.0, 597.0, 110.0, 22.0], text="prepend filterfreq", numinlets=1, numoutlets=1, outlettype=[""]),
        box("filterq_label", "comment", [855.0, 600.0, 52.0, 20.0], text="Q"),
        box("filterq", "flonum", [900.0, 597.0, 62.0, 22.0], minimum=0.1, maximum=100.0, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("filterq_pre", "newobj", [970.0, 597.0, 95.0, 22.0], text="prepend filterq", numinlets=1, numoutlets=1, outlettype=[""]),
        box("reset", "message", [1080.0, 597.0, 125.0, 22.0], text="resetoutputs 100", numinlets=2, numoutlets=1, outlettype=[""]),

        # The same-named MuBu containers now exist before these constructors,
        # matching the working mc.mubu.granular~ help-patch topology.
        box("mubu_a", "newobj", [25.0, 645.0, 565.0, 22.0], text="mc.mubu.granular~ 6 qmw_pauli_mubu_atlas_A @play 0 @cyclic 1 @microtiming 1 @centered 1 @outputposition 1 @maxresampling 4800", numinlets=1, numoutlets=2, outlettype=["multichannelsignal", ""]),
        box("mubu_b", "newobj", [25.0, 680.0, 565.0, 22.0], text="mc.mubu.granular~ 6 qmw_pauli_mubu_atlas_B @play 0 @cyclic 1 @microtiming 1 @centered 1 @outputposition 1 @maxresampling 4800", numinlets=1, numoutlets=2, outlettype=["multichannelsignal", ""]),
        box("metadata_a", "message", [610.0, 645.0, 285.0, 22.0], text="A actual grain position / duration", numinlets=2, numoutlets=1, outlettype=[""]),
        box("metadata_b", "message", [610.0, 680.0, 285.0, 22.0], text="B actual grain position / duration", numinlets=2, numoutlets=1, outlettype=[""]),
        box("gain_a", "newobj", [920.0, 645.0, 58.0, 22.0], text="mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("gain_b", "newobj", [920.0, 680.0, 58.0, 22.0], text="mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("sum", "newobj", [1010.0, 663.0, 58.0, 22.0], text="mc.+~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("mixdown", "newobj", [1090.0, 663.0, 145.0, 22.0], text="mc.mixdown~ 2 @autogain 1", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("unpack", "newobj", [1115.0, 705.0, 90.0, 22.0], text="mc.unpack~ 2", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("master_label", "comment", [790.0, 745.0, 55.0, 20.0], text="master"),
        box("master", "flonum", [845.0, 742.0, 65.0, 22.0], minimum=0.0, maximum=0.5, numinlets=1, numoutlets=2, outlettype=["", "bang"]),
        box("master_pack", "newobj", [920.0, 742.0, 75.0, 22.0], text="pack f 30", numinlets=2, numoutlets=1, outlettype=[""]),
        box("master_line", "newobj", [1005.0, 742.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("master_l", "newobj", [1080.0, 742.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("master_r", "newobj", [1170.0, 742.0, 36.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("clip_l", "newobj", [1080.0, 777.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("clip_r", "newobj", [1170.0, 777.0, 82.0, 22.0], text="clip~ -0.95 0.95", numinlets=3, numoutlets=1, outlettype=["signal"]),
        box("meter_l", "meter~", [1010.0, 775.0, 18.0, 65.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("meter_r", "meter~", [1040.0, 775.0, 18.0, 65.0], numinlets=1, numoutlets=1, outlettype=["float"]),
        box("dac", "ezdac~", [1110.0, 820.0, 52.0, 52.0], numinlets=2, numoutlets=0),

        box("init", "newobj", [25.0, 745.0, 105.0, 22.0], text="loadmess initialize", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_render", "message", [140.0, 745.0, 65.0, 22.0], text="render", numinlets=2, numoutlets=1, outlettype=[""]),
        box("loadbang", "newobj", [255.0, 745.0, 62.0, 22.0], text="loadbang", numinlets=1, numoutlets=1, outlettype=["bang"]),
        box("atlas_start", "newobj", [327.0, 745.0, 42.0, 22.0], text="t b b", numinlets=1, numoutlets=2, outlettype=["bang", "bang"]),
        box("atlas_attach_delay", "newobj", [379.0, 745.0, 72.0, 22.0], text="delay 100", numinlets=2, numoutlets=1, outlettype=["bang"]),
        box("init_atlas_a", "message", [461.0, 745.0, 220.0, 22.0], text="mubuname qmw_pauli_mubu_atlas_A", numinlets=2, numoutlets=1, outlettype=[""]),
        box("init_atlas_b", "message", [691.0, 745.0, 220.0, 22.0], text="mubuname qmw_pauli_mubu_atlas_B", numinlets=2, numoutlets=1, outlettype=[""]),
        box("init_stats", "newobj", [25.0, 780.0, 110.0, 22.0], text="loadmess 0", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_particles", "newobj", [145.0, 780.0, 82.0, 22.0], text="loadmess 4", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_field", "newobj", [237.0, 780.0, 82.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_center", "newobj", [329.0, 780.0, 82.0, 22.0], text="loadmess 0.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_width", "newobj", [421.0, 780.0, 82.0, 22.0], text="loadmess 4.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_explore", "newobj", [513.0, 780.0, 90.0, 22.0], text="loadmess 0.35", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_coherence", "newobj", [613.0, 780.0, 90.0, 22.0], text="loadmess 0.75", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_density", "newobj", [713.0, 780.0, 90.0, 22.0], text="loadmess 0.88", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_period", "newobj", [25.0, 815.0, 82.0, 22.0], text="loadmess 55.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_duration", "newobj", [117.0, 815.0, 90.0, 22.0], text="loadmess 140.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_positionvar", "newobj", [217.0, 815.0, 90.0, 22.0], text="loadmess 0.18", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_deviation", "newobj", [317.0, 815.0, 82.0, 22.0], text="loadmess 1.5", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_fm", "newobj", [409.0, 815.0, 82.0, 22.0], text="loadmess 35.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_window", "newobj", [501.0, 815.0, 105.0, 22.0], text="loadmess 0", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_filtermode", "newobj", [616.0, 815.0, 82.0, 22.0], text="loadmess 0", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_filterfreq", "newobj", [708.0, 815.0, 98.0, 22.0], text="loadmess 5000.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_filterq", "newobj", [25.0, 850.0, 82.0, 22.0], text="loadmess 1.", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_master", "newobj", [117.0, 850.0, 90.0, 22.0], text="loadmess 0.16", numinlets=1, numoutlets=1, outlettype=[""]),
        box("init_run", "newobj", [217.0, 850.0, 82.0, 22.0], text="loadmess 1", numinlets=1, numoutlets=1, outlettype=[""]),
    ]

    lines = [
        line("capture", 0, "atlas_js"), line("seed", 0, "atlas_js"),
        line("atlas_js", 1, "atlas_status", 1),
        line("atlas_js", 0, "xfade_b_pack"), line("xfade_b_pack", 0, "xfade_b"),
        line("atlas_js", 0, "xfade_a_expr"), line("xfade_a_expr", 0, "xfade_a_pack"), line("xfade_a_pack", 0, "xfade_a"),
        line("loadbang", 0, "mode_seed"), line("mode_seed", 0, "mode_track"),
        line("stats", 1, "stats_pre"), line("stats_pre", 0, "scheduler"),
        line("particles", 0, "particles_pre"), line("particles_pre", 0, "scheduler"),
        line("run", 0, "metro"), line("metro", 0, "scheduler"), line("scheduler", 3, "metro", 1),
        line("scheduler", 0, "mubu_a"), line("scheduler", 0, "mubu_b"),
        line("scheduler", 1, "occupancy"), line("scheduler", 2, "stat_status", 1),
        line("scheduler", 4, "state_track"), line("scheduler", 5, "grain_track"),
        line("scheduler", 4, "state_append_route"), line("state_append_route", 0, "state_time"),
        line("state_time", 0, "view_speedlim"), line("view_speedlim", 0, "view_trigger"),
        line("view_trigger", 1, "view_end"), line("view_end", 0, "view_pack", 1),
        line("view_trigger", 0, "view_start"), line("view_start", 0, "view_pack", 0),
        line("view_pack", 0, "view_domain"), line("view_domain", 0, "corpus"),
        line("view_freeze", 0, "view_freeze_pre"), line("view_freeze_pre", 0, "corpus"),
        line("field", 0, "field_pre"), line("field_pre", 0, "scheduler"),
        line("center", 0, "center_pre"), line("center_pre", 0, "scheduler"),
        line("width", 0, "width_pre"), line("width_pre", 0, "scheduler"),
        line("explore", 0, "explore_pre"), line("explore_pre", 0, "scheduler"),
        line("coherence", 0, "coherence_pre"), line("coherence_pre", 0, "scheduler"),
        line("density", 0, "density_pre"), line("density_pre", 0, "scheduler"),
        line("period", 0, "period_pre"), line("period_pre", 0, "scheduler"),
        line("duration", 0, "duration_pre"), line("duration_pre", 0, "scheduler"),
        line("positionvar", 0, "positionvar_pre"), line("positionvar_pre", 0, "scheduler"),
        line("deviation", 0, "deviation_pre"), line("deviation_pre", 0, "scheduler"),
        line("fm", 0, "fm_pre"), line("fm_pre", 0, "scheduler"),
        line("loadbang", 0, "sr"), line("sr", 0, "sr_pre"), line("sr_pre", 0, "scheduler"),
        line("window", 1, "window_pre"), line("window_pre", 0, "mubu_a"), line("window_pre", 0, "mubu_b"),
        line("filtermode", 0, "filtermode_pre"), line("filtermode_pre", 0, "mubu_a"), line("filtermode_pre", 0, "mubu_b"),
        line("filterfreq", 0, "filterfreq_pre"), line("filterfreq_pre", 0, "mubu_a"), line("filterfreq_pre", 0, "mubu_b"),
        line("filterq", 0, "filterq_pre"), line("filterq_pre", 0, "mubu_a"), line("filterq_pre", 0, "mubu_b"),
        line("reset", 0, "mubu_a"), line("reset", 0, "mubu_b"),
        line("mubu_a", 0, "gain_a"), line("xfade_a", 0, "gain_a", 1),
        line("mubu_b", 0, "gain_b"), line("xfade_b", 0, "gain_b", 1),
        line("mubu_a", 1, "metadata_a", 1), line("mubu_b", 1, "metadata_b", 1),
        line("gain_a", 0, "sum", 0), line("gain_b", 0, "sum", 1), line("sum", 0, "mixdown"),
        line("mixdown", 0, "unpack"), line("master", 0, "master_pack"), line("master_pack", 0, "master_line"),
        line("unpack", 0, "master_l"), line("master_line", 0, "master_l", 1),
        line("unpack", 1, "master_r"), line("master_line", 0, "master_r", 1),
        line("master_l", 0, "clip_l"), line("master_r", 0, "clip_r"),
        line("clip_l", 0, "meter_l"), line("clip_r", 0, "meter_r"),
        line("clip_l", 0, "dac", 0), line("clip_r", 0, "dac", 1),
        line("init", 0, "scheduler"),
        line("loadbang", 0, "atlas_start"), line("atlas_start", 1, "init_render"),
        line("init_render", 0, "atlas_js"), line("atlas_start", 0, "atlas_attach_delay"),
        line("atlas_attach_delay", 0, "init_atlas_a"), line("atlas_attach_delay", 0, "init_atlas_b"),
        line("init_atlas_a", 0, "mubu_a"), line("init_atlas_b", 0, "mubu_b"),
        line("init_stats", 0, "stats"), line("init_particles", 0, "particles"), line("init_field", 0, "field"),
        line("init_center", 0, "center"), line("init_width", 0, "width"), line("init_explore", 0, "explore"),
        line("init_coherence", 0, "coherence"), line("init_density", 0, "density"), line("init_period", 0, "period"),
        line("init_duration", 0, "duration"), line("init_positionvar", 0, "positionvar"),
        line("init_deviation", 0, "deviation"), line("init_fm", 0, "fm"), line("init_window", 0, "window"),
        line("init_filtermode", 0, "filtermode"), line("init_filterfreq", 0, "filterfreq"), line("init_filterq", 0, "filterq"),
        line("init_master", 0, "master"), line("init_run", 0, "run"),
    ]

    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [40.0, 30.0, 1280.0, 930.0],
        "gridsize": [15.0, 15.0],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "qmw_pauli_mubu_scheduler_v1.js", "type": "TEXT"},
            {"name": "qmw_mubu_wavetable_atlas_v1.js", "type": "TEXT"},
            {"name": "mc.mubu.granular~.mxo", "type": "iLaX"},
            {"name": "mubu.mxo", "type": "iLaX"},
            {"name": "mubu.track.mxo", "type": "iLaX"},
            {"name": "imubu.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
    return {"patcher": patcher}


def validate(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes_by_id = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    box_order = [entry["box"]["id"] for entry in patcher["boxes"]]
    if len(boxes_by_id) != len(patcher["boxes"]):
        raise RuntimeError("duplicate box identifier")
    connections: set[tuple[str, int, str, int]] = set()
    for entry in patcher["lines"]:
        source, source_outlet = entry["patchline"]["source"]
        destination, destination_inlet = entry["patchline"]["destination"]
        if source not in boxes_by_id or destination not in boxes_by_id:
            raise RuntimeError(f"dangling patchline {source} -> {destination}")
        if source_outlet >= boxes_by_id[source].get("numoutlets", 0):
            raise RuntimeError(f"invalid outlet {source}[{source_outlet}]")
        if destination_inlet >= boxes_by_id[destination].get("numinlets", 0):
            raise RuntimeError(f"invalid inlet {destination}[{destination_inlet}]")
        connections.add((source, source_outlet, destination, destination_inlet))

    texts = [entry["box"].get("text", "") for entry in patcher["boxes"]]
    if sum(text.startswith("mc.mubu.granular~ 6 ") for text in texts) != 2:
        raise RuntimeError("expected two six-channel MuBu granular engines")
    if sum(text.startswith("mubu.track qmw_pauli_mubu_corpus") for text in texts) != 3:
        raise RuntimeError("expected mode, state, and grain corpus tracks")
    if any("@channels" in text for text in texts if text.startswith("buffer~")):
        raise RuntimeError("buffer~ channel count must not use an unsupported @channels attribute")
    if any(box_order.index(track) > box_order.index("corpus") for track in ("mode_track", "state_track", "grain_track")):
        raise RuntimeError("predefined MuBu tracks must precede the corpus container")
    for buffer_id, container_id, engine_id in (
        ("atlas_a", "atlas_mubu_a", "mubu_a"),
        ("atlas_b", "atlas_mubu_b", "mubu_b"),
    ):
        if not box_order.index(buffer_id) < box_order.index(container_id) < box_order.index(engine_id):
            raise RuntimeError(f"{engine_id} source must initialize buffer~, MuBu container, then engine")
    if boxes_by_id["init_stats"].get("text") != "loadmess 0" or boxes_by_id["init_window"].get("text") != "loadmess 0":
        raise RuntimeError("umenu defaults must be selected by zero-based index")
    required = {
        ("scheduler", 0, "mubu_a", 0), ("scheduler", 0, "mubu_b", 0),
        ("scheduler", 4, "state_track", 0), ("scheduler", 5, "grain_track", 0),
        ("scheduler", 4, "state_append_route", 0), ("view_domain", 0, "corpus", 0),
        ("init_atlas_a", 0, "mubu_a", 0), ("init_atlas_b", 0, "mubu_b", 0),
        ("mubu_a", 0, "gain_a", 0), ("mubu_b", 0, "gain_b", 0),
        ("clip_l", 0, "dac", 0), ("clip_r", 0, "dac", 1),
    }
    missing = required - connections
    if missing:
        raise RuntimeError(f"missing required connection(s): {sorted(missing)}")
    corpus = boxes_by_id["corpus"]
    if corpus.get("autobounds") != 0 or corpus.get("autoupdate") != 500.0:
        raise RuntimeError("imubu must use bounded, throttled rendering")
    if corpus.get("domain_bounds") != [0.0, 30000.0]:
        raise RuntimeError("imubu must start with a fixed 30-second domain")


def main() -> None:
    payload = build()
    validate(payload)
    output = ROOT / "QMW_Pauli_MuBu_Corpus_Instrument_v1.maxpat"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"generated {output.name}")


if __name__ == "__main__":
    main()
