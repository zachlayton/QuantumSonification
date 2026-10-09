"""Generate the standalone host next to QMW's existing v4 modal DSP."""
from __future__ import annotations
import json
from pathlib import Path


def build() -> dict:
    boxes, lines = [], []

    def box(id, text, x, y, width=220, kind="newobj", **kwargs):
        item = {"id": id, "maxclass": kind, "patching_rect": [x, y, width, 22], **kwargs}
        if text is not None:
            item["text"] = text
        boxes.append({"box": item})

    def wire(source, target, outlet=0, inlet=0):
        lines.append({"patchline": {"source": [source, outlet], "destination": [target, inlet]}})

    box("title", "QMW — Classical SU(2) Yang–Mills / Modal Resonator v1", 20, 15, 620, "comment")
    box("note", "Fixed harmonics; energy drives magnitude and motion. No quantum density is fabricated.", 20, 45, 780, "comment")
    box("udp", "udpreceive 7416", 20, 85)
    box("root", "OSC-route /qmw", 20, 120)
    box("ym", "OSC-route /yang_mills", 20, 155)
    box("version", "OSC-route /v1", 20, 190)
    box("route", "OSC-route /begin /magnitude /speed /diagnostics /end", 20, 225, 560)
    for i, name in enumerate(("begin", "magnitude", "speed", "diagnostics", "end")):
        box(name, "prepend " + name, 20 + 140 * i, 270, 135)
        wire("route", name, i)
        wire(name, "adapter")
    box("adapter", "js qmw_yang_mills_modal_v1.js", 20, 325, 290)
    box("receiver_gain", None, 650, 325, 80, "flonum", minimum=0.0, maximum=1.0)
    box("gainlabel", "Field coupling 0..1 (receiver)", 630, 300, 250, "comment")
    box("gainmsg", "prepend coupling", 650, 360)
    wire("receiver_gain", "gainmsg")
    wire("gainmsg", "adapter")
    box("reset", "reset", 330, 325, 60, "message")
    wire("reset", "adapter")
    box("resetnote", "Reset receiver before restarting sender", 320, 355, 290, "comment")
    box("load", "loadbang", 870, 85, 90)
    box("on", "1", 870, 120, 40, "message")
    box("watchdog", "qmetro 50", 870, 155, 100)
    wire("load", "on")
    wire("on", "watchdog")
    wire("watchdog", "adapter")
    box("init", "reset, coupling 1", 870, 190, 150, "message")
    wire("load", "init")
    wire("init", "adapter")
    box("gaininit", "1.", 870, 225, 50, "message")
    wire("load", "gaininit")
    wire("gaininit", "receiver_gain")
    box("lanes", None, 20, 375, 300, "multislider", size=16, setminmax=[0.0, 1.0], patching_rect=[20, 375, 300, 40])
    wire("adapter", "lanes", 1)
    box("diagnostic", "print YM_energy_drift_Gauss_unitarity_det", 340, 400, 360)
    box("status", "print YM_status", 340, 435)
    wire("adapter", "diagnostic", 2)
    wire("adapter", "status", 3)
    box("base", None, 20, 450, 90, "flonum", minimum=20.0, maximum=1000.0)
    box("baselabel", "Fundamental Hz", 20, 425, 150, "comment")
    box("baseinit", "55.", 870, 270, 50, "message")
    wire("load", "baseinit")
    wire("baseinit", "base")
    box("freq", "sig~ 55", 20, 485, 100)
    wire("base", "freq")
    box("gen", "mc.gen~ @gen qmw_density_field_harmonic_modal_resonator16_mc_v4 @chans 16", 20, 525, 750)
    wire("freq", "gen")
    wire("adapter", "gen")
    box("dspinit", "reference_tone 0, excitation_floor 0, harmonic_lock 1, quantum_spectrum_morph 0", 20, 565, 750, "message")
    wire("load", "dspinit")
    wire("dspinit", "gen")
    box("mix", "mc.mixdown~ 2 @autogain 1", 20, 610, 250)
    box("unpack", "mc.unpack~ 2", 20, 645, 160)
    wire("gen", "mix")
    wire("mix", "unpack")
    box("master", None, 480, 620, 90, "flonum", minimum=0.0, maximum=1.0)
    box("masterlabel", "Master (starts at 0)", 480, 595, 230, "comment")
    box("masterinit", "0.", 870, 305, 50, "message")
    wire("load", "masterinit")
    wire("masterinit", "master")
    box("ramp", "pack 0. 50", 480, 655, 110)
    box("line", "line~", 480, 690, 90)
    wire("master", "ramp")
    wire("ramp", "line")
    for i in range(2):
        box("level" + str(i), "*~", 20 + i * 150, 690, 90)
        box("clip" + str(i), "clip~ -0.95 0.95", 20 + i * 150, 725, 140)
        wire("unpack", "level" + str(i), i)
        wire("line", "level" + str(i), inlet=1)
        wire("level" + str(i), "clip" + str(i))
        wire("clip" + str(i), "dac", inlet=i)
    box("dac", None, 20, 765, 52, "ezdac~", numinlets=2, numoutlets=0,
        patching_rect=[20, 765, 52, 52])
    box("mute", "0.", 650, 620, 60, "message")
    box("mutelabel", "MUTE", 650, 595, 80, "comment")
    wire("mute", "master")
    box("listen", "Enable DSP, then raise Master slowly. CNMAT OSC-route is required.", 170, 765, 650, "comment")
    wire("udp", "root")
    wire("root", "ym")
    wire("ym", "version")
    wire("version", "route")
    return {"patcher": {"fileversion": 1, "appversion": {"major": 8, "minor": 6,
        "revision": 0, "architecture": "x64", "modernui": 1},
        "rect": [80, 80, 1100, 850], "boxes": boxes, "lines": lines}}


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "QMW_Hilbert_Suite" / "QMW_Yang_Mills_Modal_Resonator_v1.maxpat"
    path.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
