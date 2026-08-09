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


def main():
    write("qmw_analytic_phase_projector16_v1.gendsp", build_projector_gendsp())
    write("qmw_poly_harmonic_voice16_v1.maxpat", build_voice())
    write("qmw_analytic_audition16_v1.maxpat", build_audition())
    write("QMW_Polyphonic_Complex_Hilbert_Lab_v6.maxpat", build_host())


if __name__ == "__main__":
    main()
