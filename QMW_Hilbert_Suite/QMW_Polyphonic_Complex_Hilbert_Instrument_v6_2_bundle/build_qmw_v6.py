#!/usr/bin/env python3
"""Generate the QMW polyphonic complex Hilbert v6 Max patch set.

This script is kept beside the artifacts so future edits remain reproducible.
It uses only Max JSON structures and does not require Max or third-party code.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def box(identifier, maxclass, rect, text=None, **extra):
    b = {"id": identifier, "maxclass": maxclass, "patching_rect": list(rect)}
    if text is not None:
        b["text"] = text
    defaults = {
        "newobj": (1, 1, [""]),
        "message": (2, 1, [""]),
        "comment": (1, 0, []),
        "inlet": (1, 1, [""]),
        "outlet": (1, 0, []),
        "flonum": (1, 2, ["", "bang"]),
        "number": (1, 2, ["", "bang"]),
        "button": (1, 1, ["bang"]),
        "toggle": (1, 1, ["int"]),
    }
    if maxclass in defaults:
        ni, no, ot = defaults[maxclass]
        b.update(numinlets=ni, numoutlets=no, outlettype=ot)
    b.update(extra)
    return {"box": b}


def line(source, sout, destination, din, order=None):
    p = {"source": [source, sout], "destination": [destination, din]}
    if order is not None:
        p["order"] = order
    return {"patchline": p}


def patcher(rect=(0.0, 0.0, 1400.0, 900.0)):
    return {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 7, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": list(rect),
        "boxes": [],
        "lines": [],
    }


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2) + "\n")


def build_voice():
    p = patcher((0, 0, 980, 670))
    p["boxes"] = [
        box("title", "comment", (25, 18, 660, 30), "QMW Poly Harmonic Voice 16 v1 — one MIDI note, sixteen harmonic lanes", fontsize=18.0),
        box("note-in", "newobj", (35, 80, 35, 22), "in 1"),
        box("note-label", "comment", (80, 81, 190, 20), "midinote pitch velocity"),
        box("unpack", "newobj", (35, 120, 75, 22), "unpack 0 0", numoutlets=2, outlettype=["int", "int"]),
        box("mtof", "newobj", (35, 165, 38, 22), "mtof"),
        box("freq-pack", "newobj", (35, 200, 80, 22), "pack 0. 12."),
        box("freq-line", "newobj", (35, 235, 42, 22), "line~", outlettype=["signal"]),
        box("vel-scale", "newobj", (150, 165, 48, 22), "/ 127."),
        box("attack-in", "newobj", (330, 80, 35, 22), "in 2"),
        box("decay-in", "newobj", (390, 80, 35, 22), "in 3"),
        box("sustain-in", "newobj", (450, 80, 35, 22), "in 4"),
        box("release-in", "newobj", (510, 80, 35, 22), "in 5"),
        box("adsr", "newobj", (150, 235, 158, 22), "adsr~ 18. 140. 0.72 850.", numinlets=5, numoutlets=4, outlettype=["signal", "signal", "signal", "list"]),
        box("field-r", "newobj", (375, 165, 120, 22), "r qmw.v6.field"),
        box("gen", "newobj", (35, 320, 468, 22), "mc.gen~ @gen qmw_density_field_harmonic_modal_resonator16_mc_v3 @chans 16", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("env-mul", "newobj", (35, 380, 56, 22), "mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("norm", "newobj", (35, 425, 75, 22), "mc.*~ 0.32", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("out", "newobj", (35, 480, 145, 22), "mc.out~ 1 @chans 16"),
        box("thispoly", "newobj", (330, 235, 135, 22), "thispoly~ @automute 1", numinlets=1, numoutlets=3, outlettype=["int", "int", "int"]),
        box("note-comment", "comment", (35, 535, 720, 40), "mcs.poly~ sums matching harmonic lanes across voices. The shared conductor field shapes timbre; MIDI pitch and ADSR remain independent per note.", linecount=2),
    ]
    p["lines"] = [
        line("note-in", 0, "unpack", 0),
        line("unpack", 0, "mtof", 0),
        line("mtof", 0, "freq-pack", 0),
        line("freq-pack", 0, "freq-line", 0),
        line("unpack", 1, "vel-scale", 0),
        line("vel-scale", 0, "adsr", 0),
        line("attack-in", 0, "adsr", 1),
        line("decay-in", 0, "adsr", 2),
        line("sustain-in", 0, "adsr", 3),
        line("release-in", 0, "adsr", 4),
        line("freq-line", 0, "gen", 0),
        line("field-r", 0, "gen", 0),
        line("gen", 0, "env-mul", 0),
        line("adsr", 0, "env-mul", 1),
        line("adsr", 0, "thispoly", 0),
        line("env-mul", 0, "norm", 0),
        line("norm", 0, "out", 0),
    ]
    return {"patcher": p}


def build_audition():
    p = patcher((0, 0, 1160, 620))
    p["boxes"] = [
        box("title", "comment", (25, 18, 760, 30), "QMW Direct Analytic Audition 16 v1", fontsize=18.0),
        box("desc", "comment", (25, 50, 990, 20), "Aligned pre/post complex rails share one phase rotator: conductor phase + per-harmonic spread + continuous SSB motion."),
        box("pre-i", "inlet", (35, 105, 30, 30)),
        box("pre-q", "inlet", (175, 105, 30, 30)),
        box("post-r", "inlet", (315, 105, 30, 30)),
        box("post-i", "inlet", (455, 105, 30, 30)),
        box("phase", "inlet", (595, 105, 30, 30)),
        box("control", "inlet", (790, 105, 30, 30)),
        box("labels", "comment", (25, 80, 760, 20), "pre I             pre Q             rho real           rho imag           phase[16]                       control"),
        box("smooth", "newobj", (570, 170, 160, 22), "mc.rampsmooth~ 2400 2400", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("gen", "newobj", (245, 245, 535, 22), "mc.gen~ @gen qmw_analytic_phase_projector16_v1 @chans 16", numinlets=5, numoutlets=3, outlettype=["multichannelsignal"]*3),
        box("route", "newobj", (790, 170, 345, 22), "route hilbertdepth phasedepth phasespread phasebias ssbhz deltagain", numinlets=1, numoutlets=7, outlettype=[""]*7),
        box("h", "newobj", (790, 215, 135, 22), "prepend hilbert_depth"),
        box("pd", "newobj", (790, 250, 125, 22), "prepend phase_depth"),
        box("ps", "newobj", (790, 285, 132, 22), "prepend phase_spread"),
        box("pb", "newobj", (790, 320, 120, 22), "prepend phase_bias"),
        box("ssb", "newobj", (790, 355, 105, 22), "prepend ssb_hz"),
        box("dg", "newobj", (790, 390, 115, 22), "prepend delta_gain"),
        box("unknown", "newobj", (920, 430, 185, 22), "print qmw.analytic.unknown"),
        box("pre-out", "outlet", (280, 455, 30, 30)),
        box("post-out", "outlet", (450, 455, 30, 30)),
        box("delta-out", "outlet", (620, 455, 30, 30)),
        box("out-label", "comment", (240, 500, 500, 20), "analytic pre-rho                 full matrix wet                 matrix-only delta"),
        box("load", "newobj", (25, 250, 60, 22), "loadbang"),
        box("defaults", "message", (25, 285, 190, 22), "hilbertdepth 1., phasedepth 1., phasespread 0., ssbhz 0., deltagain 2."),
    ]
    p["lines"] = [
        line("pre-i", 0, "gen", 0), line("pre-q", 0, "gen", 1),
        line("post-r", 0, "gen", 2), line("post-i", 0, "gen", 3),
        line("phase", 0, "smooth", 0), line("smooth", 0, "gen", 4),
        line("control", 0, "route", 0),
        line("route", 0, "h", 0), line("route", 1, "pd", 0),
        line("route", 2, "ps", 0), line("route", 3, "pb", 0),
        line("route", 4, "ssb", 0), line("route", 5, "dg", 0),
        line("route", 6, "unknown", 0),
        line("h", 0, "gen", 0), line("pd", 0, "gen", 0),
        line("ps", 0, "gen", 0), line("pb", 0, "gen", 0),
        line("ssb", 0, "gen", 0), line("dg", 0, "gen", 0),
        line("gen", 0, "pre-out", 0), line("gen", 1, "post-out", 0), line("gen", 2, "delta-out", 0),
        line("load", 0, "defaults", 0), line("defaults", 0, "route", 0),
    ]
    return {"patcher": p}


def build_projector_gendsp():
    """Wrap the editable GenExpr source in a loadable .gendsp document."""
    p = patcher((100, 100, 1180, 760))
    p["classnamespace"] = "dsp.gen"
    code = (ROOT / "qmw_analytic_phase_projector16_v1.genexpr").read_text()
    p["boxes"] = [
        box(f"in{i}", "newobj", (30 + (i - 1) * 95, 30, 45, 22), f"in {i}", numinlets=0, numoutlets=1, outlettype=[""])
        for i in range(1, 6)
    ]
    p["boxes"].append(
        box("code", "codebox", (30, 85, 1080, 545), numinlets=5, numoutlets=3, outlettype=["", "", ""], code=code)
    )
    p["boxes"].extend([
        box(f"out{i}", "newobj", (250 + (i - 1) * 220, 670, 55, 22), f"out {i}", numinlets=1, numoutlets=0, outlettype=[])
        for i in range(1, 4)
    ])
    p["lines"] = [line(f"in{i}", 0, "code", i - 1) for i in range(1, 6)]
    p["lines"].extend(line("code", i - 1, f"out{i}", 0) for i in range(1, 4))
    return {"patcher": p}


def build_host():
    source = json.loads((ROOT / "QMW_Complex_Matrix_Performance_Lab_v5.maxpat").read_text())
    d = copy.deepcopy(source)
    p = d["patcher"]
    p["rect"] = [0.0, 0.0, 2200.0, 1120.0]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW Polyphonic Complex Hilbert Performance Laboratory v6"
    boxes["obj-2"]["text"] = "Eight MIDI voices -> shared sixteen-harmonic field -> Hilbert/rho/complex feedback. Direct analytic audition makes phase audible without requiring high feedback."
    boxes["obj-13"]["text"] = "2  EIGHT NOTES / SIXTEEN SHARED HARMONIC LANES"
    boxes["obj-15"]["text"] = "feedback reference Hz"
    boxes["obj-17"].update(
        text="mcs.poly~ qmw_poly_harmonic_voice16_v1 8 @steal 1 @parallel 1",
        numinlets=5,
        numoutlets=1,
        outlettype=["multichannelsignal"],
        patching_rect=[40, 515, 405, 22],
    )
    boxes["obj-35"]["outlettype"] = [
        "multichannelsignal", "multichannelsignal", "multichannelsignal", "",
        "multichannelsignal", "multichannelsignal"
    ]
    boxes["obj-18"]["text"] = "Each note owns a 16-harmonic resonator. Matching harmonic indices sum into one shared MC field before rho."
    boxes["obj-55"]["text"] = "5  DIRECT ANALYTIC AUDITION + SAFE STEREO"
    boxes["obj-61"]["text"] = "Choose an audition mode, then turn Analytic Wet upward. RAW remains an exact baseline; feedback stays bounded."

    # Existing gen parameter messages become a broadcast received in every voice.
    reroute_sources = {"obj-11", "obj-73", "obj-76", "obj-79", "obj-82", "obj-90"}
    new_lines = []
    for item in p["lines"]:
        pl = item["patchline"]
        src, dst = pl["source"], pl["destination"]
        if dst == ["obj-17", 0] and src[0] in reroute_sources:
            continue
        if src == ["obj-16", 0] and dst == ["obj-17", 0]:
            continue
        if src == ["obj-35", 0] and dst == ["obj-102", 0]:
            continue
        new_lines.append(item)
    p["lines"] = new_lines

    additions = [
        box("v6-field-send", "newobj", (470, 515, 105, 22), "s qmw.v6.field"),
        box("v6-poly-label", "comment", (40, 575, 530, 20), "MIDI input and onscreen keyboard allocate eight independent notes with voice stealing."),
        box("v6-notein", "newobj", (590, 610, 48, 22), "notein", numoutlets=3, outlettype=["int", "int", "int"]),
        box("v6-kslider", "kslider", (590, 650, 480, 75), numinlets=2, numoutlets=2, outlettype=["int", "int"], range=49, offset=36, parameter_enable=0),
        box("v6-flush", "newobj", (590, 745, 48, 22), "flush", numinlets=2, numoutlets=2, outlettype=["int", "int"]),
        box("v6-pack", "newobj", (660, 745, 65, 22), "pack 0 0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("v6-midiprep", "newobj", (750, 745, 112, 22), "prepend midinote"),
        box("v6-notesoff", "button", (590, 785, 28, 28)),
        box("v6-notesoff-label", "comment", (625, 790, 90, 20), "all notes off"),
        box("v6-chord-on", "message", (750, 785, 330, 22), "midinote 48 92, midinote 55 86, midinote 60 82, midinote 64 76"),
        box("v6-chord-off", "message", (750, 820, 300, 22), "midinote 48 0, midinote 55 0, midinote 60 0, midinote 64 0"),
        box("v6-a", "flonum", (590, 875, 60, 22)),
        box("v6-d", "flonum", (665, 875, 60, 22)),
        box("v6-s", "flonum", (740, 875, 60, 22)),
        box("v6-r", "flonum", (815, 875, 60, 22)),
        box("v6-env-label", "comment", (590, 845, 360, 20), "Voice ADSR: attack ms / decay ms / sustain / release ms"),
        box("v6-a-def", "message", (590, 915, 35, 22), "18."),
        box("v6-d-def", "message", (665, 915, 42, 22), "140."),
        box("v6-s-def", "message", (740, 915, 38, 22), "0.72"),
        box("v6-r-def", "message", (815, 915, 42, 22), "850."),

        box("v6-section", "comment", (40, 950, 450, 28), "6  DEEP HILBERT / PHASE AUDITION", fontsize=16.0),
        box("v6-phase-sig", "newobj", (40, 990, 155, 22), "mcs.sig~ 0. @chans 16", numinlets=1, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v6-audition", "newobj", (225, 990, 235, 22), "qmw_analytic_audition16_v1", numinlets=6, numoutlets=3, outlettype=["multichannelsignal"]*3),
        box("v6-selector", "newobj", (500, 990, 105, 22), "mc.selector~ 5", numinlets=6, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v6-menu", "umenu", (500, 950, 175, 22), numinlets=1, numoutlets=3, outlettype=["int", "", ""], items=["RAW", ",", "ANALYTIC ROTATION", ",", "FULL MATRIX WET", ",", "MATRIX DELTA", ",", "COMPLEX FEEDBACK"], parameter_enable=0),
        box("v6-menu-plus", "newobj", (690, 950, 35, 22), "+ 1"),
        box("v6-wet", "flonum", (750, 950, 65, 22)),
        box("v6-wet-label", "comment", (825, 952, 100, 20), "Analytic Wet"),
        box("v6-wet-clip", "newobj", (750, 990, 68, 22), "clip 0. 1."),
        box("v6-wet-trigger", "newobj", (835, 990, 42, 22), "t f f", numoutlets=2, outlettype=["float", "float"]),
        box("v6-wet-pack", "newobj", (895, 990, 80, 22), "pack 0. 30."),
        box("v6-wet-line", "newobj", (990, 990, 42, 22), "line~", outlettype=["signal"]),
        box("v6-dry-sub", "newobj", (835, 1025, 42, 22), "!- 1."),
        box("v6-dry-pack", "newobj", (895, 1025, 80, 22), "pack 1. 30."),
        box("v6-dry-line", "newobj", (990, 1025, 42, 22), "line~", outlettype=["signal"]),
        box("v6-proc-mul", "newobj", (1060, 990, 52, 22), "mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v6-raw-mul", "newobj", (1060, 1025, 52, 22), "mc.*~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v6-sum", "newobj", (1140, 1005, 52, 22), "mc.+~", numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),

        box("v6-hdepth", "flonum", (1240, 950, 65, 22)),
        box("v6-hmsg", "newobj", (1240, 980, 140, 22), "prepend hilbertdepth"),
        box("v6-hlabel", "comment", (1315, 952, 110, 20), "Hilbert Depth"),
        box("v6-pdepth", "flonum", (1450, 950, 65, 22)),
        box("v6-pmsg", "newobj", (1450, 980, 135, 22), "prepend phasedepth"),
        box("v6-plabel", "comment", (1525, 952, 125, 20), "Phase Depth (0–4)"),
        box("v6-spread", "flonum", (1660, 950, 65, 22)),
        box("v6-smsg", "newobj", (1660, 980, 145, 22), "prepend phasespread"),
        box("v6-slabel", "comment", (1735, 952, 160, 20), "Harmonic Phase Spread"),
        box("v6-ssb", "flonum", (1900, 950, 65, 22)),
        box("v6-ssbmsg", "newobj", (1900, 980, 115, 22), "prepend ssbhz"),
        box("v6-ssblabel", "comment", (1975, 952, 150, 20), "SSB Motion Hz"),
        box("v6-dgain", "flonum", (1240, 1035, 65, 22)),
        box("v6-dgmsg", "newobj", (1240, 1065, 130, 22), "prepend deltagain"),
        box("v6-dglabel", "comment", (1315, 1037, 155, 20), "Matrix Delta Gain"),
        box("v6-wet-def", "message", (1490, 1065, 30, 22), "1."),
        box("v6-h-def", "message", (1530, 1065, 30, 22), "1."),
        box("v6-p-def", "message", (1570, 1065, 30, 22), "1."),
        box("v6-spread-def", "message", (1610, 1065, 42, 22), "0.08"),
        box("v6-ssb-def", "message", (1665, 1065, 30, 22), "0."),
        box("v6-dg-def", "message", (1705, 1065, 30, 22), "2."),
        box("v6-mode-def", "message", (1745, 1065, 30, 22), "1"),
        box("v6-direct-note", "comment", (1810, 1035, 360, 42), "Strong start: Analytic Rotation, Wet 1, Hilbert 1, Phase Depth 1.5, Spread 0.08. Add ±0.1–3 Hz SSB motion slowly.", linecount=2),
    ]
    p["boxes"].extend(additions)

    # Broadcast every conductor-derived and manual resonator parameter to all voices.
    for src in sorted(reroute_sources):
        p["lines"].append(line(src, 0, "v6-field-send", 0))

    # MIDI / keyboard / envelope.
    p["lines"].extend([
        line("v6-notein", 0, "v6-flush", 0), line("v6-notein", 1, "v6-flush", 1),
        line("v6-kslider", 0, "v6-flush", 0), line("v6-kslider", 1, "v6-flush", 1),
        line("v6-notesoff", 0, "v6-flush", 0),
        line("v6-flush", 0, "v6-pack", 0), line("v6-flush", 1, "v6-pack", 1),
        line("v6-pack", 0, "v6-midiprep", 0), line("v6-midiprep", 0, "obj-17", 0),
        line("v6-chord-on", 0, "obj-17", 0), line("v6-chord-off", 0, "obj-17", 0),
        line("v6-a", 0, "obj-17", 1), line("v6-d", 0, "obj-17", 2),
        line("v6-s", 0, "obj-17", 3), line("v6-r", 0, "obj-17", 4),
    ])

    # Aligned direct complex rails and audition selection.
    p["lines"].extend([
        line("obj-7", 1, "v6-phase-sig", 0),
        line("obj-35", 4, "v6-audition", 0), line("obj-35", 5, "v6-audition", 1),
        line("obj-35", 1, "v6-audition", 2), line("obj-35", 2, "v6-audition", 3),
        line("v6-phase-sig", 0, "v6-audition", 4),
        line("obj-17", 0, "v6-selector", 1),
        line("v6-audition", 0, "v6-selector", 2), line("v6-audition", 1, "v6-selector", 3),
        line("v6-audition", 2, "v6-selector", 4), line("obj-35", 0, "v6-selector", 5),
        line("v6-menu", 0, "v6-menu-plus", 0), line("v6-menu-plus", 0, "v6-selector", 0),
        line("v6-selector", 0, "v6-proc-mul", 0), line("v6-wet-line", 0, "v6-proc-mul", 1),
        line("obj-17", 0, "v6-raw-mul", 0), line("v6-dry-line", 0, "v6-raw-mul", 1),
        line("v6-proc-mul", 0, "v6-sum", 0), line("v6-raw-mul", 0, "v6-sum", 1),
        line("v6-sum", 0, "obj-102", 0),
        line("v6-wet", 0, "v6-wet-clip", 0), line("v6-wet-clip", 0, "v6-wet-trigger", 0),
        line("v6-wet-trigger", 0, "v6-wet-pack", 0), line("v6-wet-pack", 0, "v6-wet-line", 0),
        line("v6-wet-trigger", 1, "v6-dry-sub", 0), line("v6-dry-sub", 0, "v6-dry-pack", 0),
        line("v6-dry-pack", 0, "v6-dry-line", 0),
        line("v6-hdepth", 0, "v6-hmsg", 0), line("v6-hmsg", 0, "v6-audition", 5),
        line("v6-pdepth", 0, "v6-pmsg", 0), line("v6-pmsg", 0, "v6-audition", 5),
        line("v6-spread", 0, "v6-smsg", 0), line("v6-smsg", 0, "v6-audition", 5),
        line("v6-ssb", 0, "v6-ssbmsg", 0), line("v6-ssbmsg", 0, "v6-audition", 5),
        line("v6-dgain", 0, "v6-dgmsg", 0), line("v6-dgmsg", 0, "v6-audition", 5),
    ])

    # Load defaults. The menu uses zero-based indices; message 1 selects Analytic Rotation.
    for default, target in [
        ("v6-wet-def", "v6-wet"), ("v6-h-def", "v6-hdepth"),
        ("v6-p-def", "v6-pdepth"), ("v6-spread-def", "v6-spread"),
        ("v6-ssb-def", "v6-ssb"), ("v6-dg-def", "v6-dgain"),
        ("v6-mode-def", "v6-menu"), ("v6-a-def", "v6-a"),
        ("v6-d-def", "v6-d"), ("v6-s-def", "v6-s"), ("v6-r-def", "v6-r"),
    ]:
        p["lines"].append(line("obj-63", 0, default, 0))

    return d


def build_operator_v2():
    """Version the outlet-order fix so Max cannot reuse a cached v1 abstraction."""
    d = json.loads((ROOT / "qmw_density_matrix_hilbert_operator16_mc_v1.maxpat").read_text())
    p = d["patcher"]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW Density-Matrix Hilbert Operator — 16 MC v2"
    boxes["obj-2"]["text"] = "v2 fixes physical outlet order: y_re / y_im / audition / diagnostics. Status can never enter a signal rail."
    # Max may recompute abstraction outlet order from horizontal position.
    boxes["obj-28"]["patching_rect"][0] = 170.0
    boxes["obj-29"]["patching_rect"][0] = 635.0
    boxes["obj-47"]["patching_rect"][0] = 1130.0
    boxes["obj-62"]["patching_rect"][0] = 1350.0
    return d


def build_feedback_v3():
    d = json.loads((ROOT / "qmw_density_matrix_dualrail_feedback16_mc_v2.maxpat").read_text())
    p = d["patcher"]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW Dual-Rail Complex Resonator Feedback — 16 MC v3"
    boxes["obj-2"]["text"] = "v3 uses the outlet-safe v2 Hilbert operator; diagnostics are message-only and isolated from all DSP rails."
    boxes["obj-19"]["text"] = "qmw_density_matrix_hilbert_operator16_mc_v2"
    return d


def build_feedback_v4():
    """Make dual-rail memory non-commutative by offsetting the Q delay."""
    d = build_feedback_v3()
    p = d["patcher"]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW Dual-Rail Complex Resonator Feedback — 16 MC v4"
    boxes["obj-2"]["text"] = "v4 gives Complex Memory a real phase state: the imaginary rail gains up to 8 ms additional delay before projection."
    # v2 used the same delay for both complex rails, so delay commuted with
    # projection and the Complex Memory crossfade was nearly null.
    p["lines"] = [x for x in p["lines"] if not (
        x["patchline"]["source"] == ["obj-34", 0]
        and x["patchline"]["destination"] == ["obj-78", 0]
    )]
    p["boxes"].extend([
        box("v4-q-offset-scale", "newobj", (660, 590, 82, 22), "mc.*~ 8.",
            numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v4-q-delay-add", "newobj", (660, 620, 58, 22), "mc.+~",
            numinlets=2, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v4-q-delay-clip", "newobj", (660, 650, 125, 22), "mc.clip~ 1. 2000.",
            numinlets=3, numoutlets=1, outlettype=["multichannelsignal"]),
        box("v4-q-note", "comment", (790, 620, 300, 35),
            "Complex Memory: Q delay = harmonic delay + depth × 8 ms", linecount=2),
    ])
    p["lines"].extend([
        line("obj-97", 0, "v4-q-offset-scale", 0),
        line("obj-34", 0, "v4-q-delay-add", 0),
        line("v4-q-offset-scale", 0, "v4-q-delay-add", 1),
        line("v4-q-delay-add", 0, "v4-q-delay-clip", 0),
        line("v4-q-delay-clip", 0, "obj-78", 0),
    ])
    return d


def build_matrixctrl_v2():
    """Give the editor unambiguous inlet/outlet order for abstraction use."""
    d = json.loads((ROOT / "qmw_complex_matrixctrl16_v1.maxpat").read_text())
    p = d["patcher"]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["title"]["text"] = "QMW COMPLEX MATRIX PERFORMANCE EDITOR v2 — 16 × 16"
    for identifier, index in [("in-control", 1), ("in-re", 2), ("in-im", 3)]:
        boxes[identifier]["index"] = index
    for identifier, index in [("out-re", 1), ("out-im", 2),
                              ("out-commit", 3), ("out-status", 4)]:
        boxes[identifier]["index"] = index
    return d


def build_presentation_host():
    d = build_host()
    p = d["patcher"]
    p["openinpresentation"] = 1
    p["presentation_rect"] = [0.0, 0.0, 1440.0, 900.0]
    p["rect"] = [0.0, 0.0, 1800.0, 1050.0]
    p["bgcolor"] = [0.055, 0.065, 0.078, 1.0]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW POLYPHONIC COMPLEX HILBERT INSTRUMENT  v6.1"
    boxes["obj-2"]["text"] = "Eight notes · sixteen shared harmonic modes · direct analytic phase · complex density matrix · bounded memory"
    boxes["obj-35"]["text"] = "qmw_density_matrix_dualrail_feedback16_mc_v4"
    boxes["obj-96"]["text"] = "js qmw_coherence_feedback_gain16_v2.js"
    boxes["obj-105"]["text"] = "js qmw_complex_matrix_presets16_v2.js"
    boxes["obj-150"]["text"] = "qmw_complex_matrixctrl16_v2"

    # Nothing inherited appears accidentally; only explicitly placed performance
    # controls are visible in Presentation Mode.
    for item in p["boxes"]:
        item["box"].pop("presentation", None)
        item["box"].pop("presentation_rect", None)

    def present(identifier, rect):
        b = boxes[identifier]
        b["presentation"] = 1
        b["presentation_rect"] = list(rect)

    # Existing controls, deliberately grouped into a compact instrument panel.
    placements = {
        "obj-1": (24, 13, 850, 32), "obj-2": (25, 46, 930, 20),
        "obj-8": (1110, 24, 24, 24), "obj-9": (1142, 26, 205, 20),
        "v6-kslider": (45, 130, 555, 92),
        "v6-notesoff": (45, 281, 28, 28), "v6-notesoff-label": (82, 286, 95, 20),
        "v6-a": (55, 337, 62, 22), "v6-d": (150, 337, 62, 22),
        "v6-s": (245, 337, 62, 22), "v6-r": (340, 337, 62, 22),
        "obj-72": (685, 144, 72, 22), "obj-75": (685, 207, 72, 22),
        "obj-78": (685, 270, 72, 22), "obj-89": (850, 144, 72, 22),
        "obj-81": (850, 207, 72, 22), "obj-97": (850, 270, 72, 22),
        "obj-14": (685, 337, 72, 22), "obj-135": (850, 337, 58, 22),
        "v6-menu": (1045, 140, 250, 24), "v6-wet": (1045, 205, 72, 22),
        "v6-hdepth": (1045, 268, 72, 22), "v6-pdepth": (1045, 331, 72, 22),
        "v6-spread": (1045, 394, 72, 22), "v6-ssb": (1045, 457, 72, 22),
        "v6-dgain": (1045, 520, 72, 22),
        "obj-112": (55, 481, 70, 24), "obj-113": (135, 481, 78, 24),
        "obj-114": (223, 481, 142, 24), "obj-115": (375, 481, 132, 24),
        "obj-116": (517, 481, 112, 24), "obj-117": (639, 481, 55, 24),
        "obj-107": (55, 558, 62, 24), "obj-108": (127, 558, 62, 24),
        "obj-109": (199, 558, 62, 24), "obj-110": (271, 558, 62, 24),
        "obj-119": (390, 558, 72, 22), "obj-128": (520, 558, 72, 22),
        "obj-150": (55, 620, 260, 24),
        "obj-38": (725, 481, 38, 38), "obj-39": (772, 490, 85, 20),
        "obj-41": (725, 548, 38, 38), "obj-42": (772, 557, 120, 20),
        "obj-47": (725, 615, 38, 38), "obj-48": (772, 624, 125, 20),
        "obj-102": (1025, 675, 250, 150), "obj-60": (1325, 730, 52, 52),
    }
    for identifier, rect in placements.items():
        present(identifier, rect)

    # Presentation-only section backgrounds and labels.
    panel_specs = [
        ("ui-play", (20, 88, 620, 305), [0.10, 0.13, 0.17, 1.0]),
        ("ui-body", (655, 88, 340, 305), [0.10, 0.13, 0.17, 1.0]),
        ("ui-complex", (1010, 88, 410, 505), [0.085, 0.115, 0.155, 1.0]),
        ("ui-matrix", (20, 420, 680, 285), [0.10, 0.13, 0.17, 1.0]),
        ("ui-safety", (710, 420, 285, 285), [0.115, 0.105, 0.10, 1.0]),
        ("ui-output", (1010, 620, 410, 240), [0.10, 0.13, 0.17, 1.0]),
        ("ui-detection", (20, 720, 975, 140), [0.085, 0.115, 0.135, 1.0]),
    ]
    panels = []
    for identifier, rect, color in panel_specs:
        panels.append(box(identifier, "panel", rect, numinlets=1, numoutlets=0,
            presentation=1, presentation_rect=list(rect), rounded=12,
            background=1, border=1, bgcolor=color, bgfillcolor={"type": "color", "color": color,
            "color1": color, "color2": color, "angle": 270.0, "proportion": 0.5,
            "autogradient": 0.0}))

    def ui_comment(identifier, text_value, rect, size=13.0, color=(0.78, 0.86, 0.95, 1.0), face=0):
        return box(identifier, "comment", rect, text_value, presentation=1,
            presentation_rect=list(rect), fontsize=size, fontface=face,
            textcolor=list(color))

    labels = [
        ui_comment("ui-play-title", "PLAY / VOICES", (40, 100, 200, 24), 15, face=1),
        ui_comment("ui-env", "ATTACK       DECAY       SUSTAIN      RELEASE", (52, 314, 390, 20), 11),
        ui_comment("ui-chord-on-label", "PLAY TEST CHORD", (80, 249, 130, 20), 11),
        ui_comment("ui-chord-off-label", "RELEASE CHORD", (300, 249, 130, 20), 11),
        ui_comment("ui-body-title", "HARMONIC BODY", (675, 100, 220, 24), 15, face=1),
        ui_comment("ui-lock", "Harmonic Lock", (765, 146, 100, 20), 11),
        ui_comment("ui-motion", "Motion Drive", (765, 209, 100, 20), 11),
        ui_comment("ui-decay", "Ring Decay ms", (765, 272, 100, 20), 11),
        ui_comment("ui-reference", "Reference Tone", (930, 146, 100, 20), 11),
        ui_comment("ui-noise", "Noise Floor", (930, 209, 90, 20), 11),
        ui_comment("ui-fbdepth", "Feedback Depth", (930, 272, 110, 20), 11),
        ui_comment("ui-fbref", "Feedback reference Hz", (685, 314, 145, 20), 11),
        ui_comment("ui-scope", "Scope lane", (850, 314, 90, 20), 11),
        ui_comment("ui-complex-title", "DIRECT HILBERT / PHASE", (1035, 100, 270, 24), 15, face=1),
        ui_comment("ui-wet", "Analytic Wet", (1128, 207, 110, 20), 11),
        ui_comment("ui-hdepth", "Hilbert Depth", (1128, 270, 110, 20), 11),
        ui_comment("ui-pdepth", "Phase Depth", (1128, 333, 110, 20), 11),
        ui_comment("ui-spread", "Harmonic Phase Spread", (1128, 396, 170, 20), 11),
        ui_comment("ui-ssb", "SSB Motion Hz", (1128, 459, 120, 20), 11),
        ui_comment("ui-delta", "Matrix Delta Gain", (1128, 522, 140, 20), 11),
        ui_comment("ui-matrix-title", "COMPLEX MATRIX", (40, 438, 240, 24), 15, face=1),
        ui_comment("ui-matrix-help", "Presets", (55, 462, 90, 18), 11),
        ui_comment("ui-modes", "Rotation       Pairs          Full rho       Complex memory", (55, 535, 330, 18), 11),
        ui_comment("ui-imag", "Imaginary coupling", (390, 535, 125, 18), 11),
        ui_comment("ui-memory", "Complex memory", (520, 535, 115, 18), 11),
        ui_comment("ui-editor", "Double-click to open the 16 × 16 matrix editor", (325, 623, 320, 20), 11),
        ui_comment("ui-safety-title", "FEEDBACK / SAFETY", (730, 438, 240, 24), 15, face=1),
        ui_comment("ui-output-title", "OUTPUT", (1030, 638, 150, 24), 15, face=1),
        ui_comment("ui-dsp", "DSP", (1327, 708, 50, 18), 11),
        ui_comment("ui-detection-title", "FIELD DETECTION", (40, 735, 220, 24), 15, face=1),
        ui_comment("ui-threshold-label", "Motion Threshold — lower detects smaller movements", (50, 775, 280, 20), 11),
        ui_comment("ui-transient-label", "Population Transient Sensitivity", (365, 775, 230, 20), 11),
        ui_comment("ui-phasechange-label", "Phase-Change Sensitivity", (680, 775, 200, 20), 11),
        ui_comment("ui-detection-help", "Sensitive starting point: Threshold 0.01 · Population 18 · Phase 0.04", (50, 835, 620, 18), 11, color=(0.55, 0.8, 0.95, 1.0)),
        ui_comment("ui-tip", "Start: ANALYTIC ROTATION · Wet 1 · Hilbert 1 · Phase 1.5 · Spread 0.08", (25, 870, 850, 20), 12, color=(0.55, 0.8, 0.95, 1.0)),
    ]
    performance_buttons = [
        box("ui-chord-on-button", "button", (45, 244, 28, 28), presentation=1,
            presentation_rect=[45, 244, 28, 28]),
        box("ui-chord-off-button", "button", (265, 244, 28, 28), presentation=1,
            presentation_rect=[265, 244, 28, 28]),
    ]
    p["lines"].extend([
        line("ui-chord-on-button", 0, "v6-chord-on", 0),
        line("ui-chord-off-button", 0, "v6-chord-off", 0),
    ])
    detection_controls = [
        box("v61-motion-threshold", "flonum", (50, 802, 82, 22),
            presentation=1, presentation_rect=[50, 802, 82, 22]),
        box("v61-transient-sensitivity", "flonum", (365, 802, 82, 22),
            presentation=1, presentation_rect=[365, 802, 82, 22]),
        box("v61-phase-change", "flonum", (680, 802, 82, 22),
            presentation=1, presentation_rect=[680, 802, 82, 22]),
        box("v61-threshold-msg", "newobj", (50, 1160, 165, 22), "prepend motion_threshold"),
        box("v61-transient-msg", "newobj", (230, 1160, 190, 22), "prepend transient_sensitivity"),
        box("v61-phasechange-msg", "newobj", (435, 1160, 190, 22), "prepend phase_change_drive"),
    ]
    p["lines"].extend([
        line("v61-motion-threshold", 0, "v61-threshold-msg", 0),
        line("v61-threshold-msg", 0, "v6-field-send", 0),
        line("v61-transient-sensitivity", 0, "v61-transient-msg", 0),
        line("v61-transient-msg", 0, "v6-field-send", 0),
        line("v61-phase-change", 0, "v61-phasechange-msg", 0),
        line("v61-phasechange-msg", 0, "v6-field-send", 0),
    ])
    # Audition-mode behavior is explicit. Selecting Complex Feedback opens the
    # recursive gate and refreshes gain/delay; leaving it closes the gate so no
    # hidden state accumulates. Matrix preset buttons select their audible path.
    mode_helpers = [
        box("v61-feedback-select", "newobj", (960, 1160, 48, 22), "sel 4",
            numinlets=1, numoutlets=2, outlettype=["bang", "int"]),
        box("v61-feedback-trigger", "newobj", (1020, 1160, 58, 22), "t b b b",
            numinlets=1, numoutlets=3, outlettype=["bang", "bang", "bang"]),
        box("v61-feedback-on", "message", (1090, 1160, 52, 22), "mode 2"),
        box("v61-feedback-off", "message", (1155, 1160, 52, 22), "mode 1"),
        box("v61-menu-raw", "message", (1220, 1160, 30, 22), "0"),
        box("v61-menu-analytic", "message", (1260, 1160, 30, 22), "1"),
        box("v61-menu-matrix", "message", (1300, 1160, 30, 22), "2"),
        box("v61-menu-feedback", "message", (1340, 1160, 30, 22), "4"),
    ]
    p["lines"].extend([
        line("v6-menu", 0, "v61-feedback-select", 0),
        line("v61-feedback-select", 0, "v61-feedback-trigger", 0),
        line("v61-feedback-trigger", 2, "obj-96", 0),
        line("v61-feedback-trigger", 1, "obj-93", 0),
        line("v61-feedback-trigger", 0, "v61-feedback-on", 0),
        line("v61-feedback-on", 0, "obj-35", 6),
        line("v61-feedback-select", 1, "v61-feedback-off", 0),
        line("v61-feedback-off", 0, "obj-35", 6),
        line("v6-hmsg", 0, "obj-35", 6),
        line("v6-pmsg", 0, "obj-35", 6),
        # Matrix presets immediately select Full Matrix Wet.
        line("obj-112", 0, "v61-menu-matrix", 0),
        line("obj-113", 0, "v61-menu-matrix", 0),
        line("obj-114", 0, "v61-menu-matrix", 0),
        line("obj-115", 0, "v61-menu-matrix", 0),
        line("obj-116", 0, "v61-menu-matrix", 0),
        line("obj-117", 0, "v61-menu-matrix", 0),
        line("v61-menu-matrix", 0, "v6-menu", 0),
        # The four complexity buttons choose the path they actually control.
        line("obj-107", 0, "v61-menu-analytic", 0),
        line("obj-108", 0, "v61-menu-matrix", 0),
        line("obj-109", 0, "v61-menu-matrix", 0),
        line("obj-110", 0, "v61-menu-feedback", 0),
        line("v61-menu-analytic", 0, "v6-menu", 0),
        line("v61-menu-feedback", 0, "v6-menu", 0),
        # Safety buttons keep audition state consistent with the engine gate.
        line("obj-38", 0, "v61-menu-raw", 0),
        line("obj-41", 0, "v61-menu-feedback", 0),
        line("obj-47", 0, "v61-menu-raw", 0),
        line("v61-menu-raw", 0, "v6-menu", 0),
    ])
    # Dedicated initialization for the instrument host. This avoids relying on
    # the old laboratory patch's large unordered loadbang fan-out and guarantees
    # an audible analytic state on every fresh open.
    initializers = [
        box("init-menu", "newobj", (20, 1080, 75, 22), "loadmess 1"),
        box("init-wet", "newobj", (105, 1080, 80, 22), "loadmess 1."),
        box("init-hdepth", "newobj", (195, 1080, 80, 22), "loadmess 1."),
        box("init-pdepth", "newobj", (285, 1080, 92, 22), "loadmess 1.5"),
        box("init-spread", "newobj", (387, 1080, 92, 22), "loadmess 0.08"),
        box("init-ssb", "newobj", (489, 1080, 80, 22), "loadmess 0."),
        box("init-delta", "newobj", (579, 1080, 80, 22), "loadmess 2."),
        box("init-lock", "newobj", (669, 1080, 80, 22), "loadmess 1."),
        box("init-motion", "newobj", (759, 1080, 92, 22), "loadmess 0.1"),
        box("init-ring", "newobj", (861, 1080, 92, 22), "loadmess 25."),
        box("init-reference", "newobj", (963, 1080, 92, 22), "loadmess 0.2"),
        box("init-noise", "newobj", (1065, 1080, 110, 22), "loadmess 0.0002"),
        box("init-feedback", "newobj", (1185, 1080, 92, 22), "loadmess 0.5"),
        box("init-fbref", "newobj", (1287, 1080, 80, 22), "loadmess 55."),
        box("init-scope", "newobj", (1377, 1080, 75, 22), "loadmess 1"),
        box("init-attack", "newobj", (20, 1115, 92, 22), "loadmess 18."),
        box("init-decay", "newobj", (122, 1115, 95, 22), "loadmess 140."),
        box("init-sustain", "newobj", (227, 1115, 95, 22), "loadmess 0.72"),
        box("init-release", "newobj", (332, 1115, 95, 22), "loadmess 850."),
        box("init-threshold", "newobj", (640, 1160, 95, 22), "loadmess 0.025"),
        box("init-transient", "newobj", (745, 1160, 92, 22), "loadmess 14."),
        box("init-phasechange", "newobj", (847, 1160, 95, 22), "loadmess 0.02"),
    ]
    init_targets = [
        ("init-menu", "v6-menu"), ("init-wet", "v6-wet"),
        ("init-hdepth", "v6-hdepth"), ("init-pdepth", "v6-pdepth"),
        ("init-spread", "v6-spread"), ("init-ssb", "v6-ssb"),
        ("init-delta", "v6-dgain"), ("init-lock", "obj-72"),
        ("init-motion", "obj-75"), ("init-ring", "obj-78"),
        ("init-reference", "obj-89"), ("init-noise", "obj-81"),
        ("init-feedback", "obj-97"), ("init-fbref", "obj-14"),
        ("init-scope", "obj-135"), ("init-attack", "v6-a"),
        ("init-decay", "v6-d"), ("init-sustain", "v6-s"),
        ("init-release", "v6-r"),
        ("init-threshold", "v61-motion-threshold"),
        ("init-transient", "v61-transient-sensitivity"),
        ("init-phasechange", "v61-phase-change"),
    ]
    p["lines"].extend(line(source, 0, target, 0) for source, target in init_targets)
    # Panels must precede controls so they remain behind them.
    p["boxes"] = (panels + labels + performance_buttons + detection_controls
        + mode_helpers + p["boxes"] + initializers)
    return d


def build_presentation_host_v6_2():
    d = build_presentation_host()
    p = d["patcher"]
    boxes = {x["box"]["id"]: x["box"] for x in p["boxes"]}
    boxes["obj-1"]["text"] = "QMW POLYPHONIC COMPLEX HILBERT INSTRUMENT  v6.2"
    boxes["obj-2"]["text"] = "Audible feedback gate · guaranteed feedback depth · true I/Q memory · canonical matrix display"
    boxes["ui-imag"]["text"] = "Imag coupling (auto-ring)"
    boxes["ui-memory"]["text"] = "I/Q memory (0–8 ms)"
    return d


def main():
    write("qmw_density_matrix_hilbert_operator16_mc_v2.maxpat", build_operator_v2())
    write("qmw_density_matrix_dualrail_feedback16_mc_v3.maxpat", build_feedback_v3())
    write("qmw_density_matrix_dualrail_feedback16_mc_v4.maxpat", build_feedback_v4())
    write("qmw_complex_matrixctrl16_v2.maxpat", build_matrixctrl_v2())
    write("qmw_analytic_phase_projector16_v1.gendsp", build_projector_gendsp())
    write("qmw_poly_harmonic_voice16_v1.maxpat", build_voice())
    write("qmw_analytic_audition16_v1.maxpat", build_audition())
    write("QMW_Polyphonic_Complex_Hilbert_Lab_v6.maxpat", build_host())
    write("QMW_Polyphonic_Complex_Hilbert_Instrument_v6_1.maxpat", build_presentation_host())
    write("QMW_Polyphonic_Complex_Hilbert_Instrument_v6_2.maxpat", build_presentation_host_v6_2())


if __name__ == "__main__":
    main()
