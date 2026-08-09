#!/usr/bin/env python3
"""Build the Max 9 pfft~ consumer for living spectral history."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def patcher(rect):
    return {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 0,
            "architecture": "x64",
        },
        "rect": rect,
        "boxes": [],
        "lines": [],
    }


def box(doc, identifier, maxclass, rect, **values):
    payload = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    payload.update(values)
    doc["boxes"].append({"box": payload})


def line(doc, source, outlet, destination, inlet=0):
    doc["lines"].append(
        {
            "patchline": {
                "source": [source, outlet],
                "destination": [destination, inlet],
            }
        }
    )


def write(name, doc, dependencies):
    def dependency_type(dependency):
        if dependency.endswith(".js"):
            return "TEXT"
        if dependency.endswith(".mxo"):
            return "iLaX"
        return "JSON"

    doc["dependency_cache"] = [
        {"name": dependency, "type": dependency_type(dependency)}
        for dependency in dependencies
    ]
    output = ROOT / name
    output.write_text(json.dumps({"patcher": doc}, indent=2) + "\n")
    return output


def build_pfft():
    doc = patcher([0, 0, 760, 400])
    box(doc, "title", "comment", [20, 15, 700, 24], text="QMW living spectral magnitude processor - audio STFT phase remains local", fontsize=15.0)
    box(doc, "fftin", "newobj", [35, 75, 70, 22], text="fftin~ 1", numinlets=1, numoutlets=3, outlettype=["signal", "signal", "signal"])
    box(doc, "cartopol", "newobj", [145, 75, 80, 22], text="cartopol~", numinlets=2, numoutlets=2, outlettype=["signal", "signal"])
    box(doc, "mask", "newobj", [145, 145, 205, 22], text="index~ qmw_living_spectral_mask", numinlets=2, numoutlets=1, outlettype=["signal"])
    box(doc, "smooth", "newobj", [380, 145, 135, 22], text="rampsmooth~ 128 128", numinlets=3, numoutlets=1, outlettype=["signal"])
    box(doc, "multiply", "newobj", [145, 215, 45, 22], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"])
    box(doc, "poltocar", "newobj", [145, 275, 80, 22], text="poltocar~", numinlets=2, numoutlets=2, outlettype=["signal", "signal"])
    box(doc, "fftout", "newobj", [145, 335, 75, 22], text="fftout~ 1", numinlets=2, numoutlets=0)
    box(doc, "phase_note", "comment", [275, 270, 440, 44], text="Original cartopol~ phase goes straight to poltocar~. Use framedelta~/frameaccum~ only for an audio phase-vocoder extension; never inject eigenfield phase deltas here.")
    line(doc, "fftin", 0, "cartopol", 0)
    line(doc, "fftin", 1, "cartopol", 1)
    line(doc, "fftin", 2, "mask", 0)
    line(doc, "mask", 0, "smooth", 0)
    line(doc, "cartopol", 0, "multiply", 0)
    line(doc, "smooth", 0, "multiply", 1)
    line(doc, "multiply", 0, "poltocar", 0)
    line(doc, "cartopol", 1, "poltocar", 1)
    line(doc, "poltocar", 0, "fftout", 0)
    line(doc, "poltocar", 1, "fftout", 1)
    return write("qmw_living_spectral_mask_pfft_v1.maxpat", doc, [])


def build_parent():
    doc = patcher([0, 0, 1180, 720])
    box(doc, "title", "comment", [20, 15, 1080, 30], text="QMW LIVING SPECTRAL PFFT v1 - stochastic eigenfield-history masking", fontsize=18.0)
    box(doc, "source", "newobj", [20, 75, 150, 22], text="playlist~ @loop 1", numinlets=1, numoutlets=5, outlettype=["signal", "signal", "signal", "", "dictionary"])
    box(doc, "pfft", "newobj", [220, 75, 315, 22], text="pfft~ qmw_living_spectral_mask_pfft_v1 4096 4", numinlets=1, numoutlets=1, outlettype=["signal"])
    box(doc, "gain", "newobj", [585, 75, 75, 22], text="*~ 0.2", numinlets=2, numoutlets=1, outlettype=["signal"])
    box(doc, "dac", "ezdac~", [720, 70, 52, 52], numinlets=2, numoutlets=0)
    box(doc, "buffer", "newobj", [220, 125, 305, 22], text="buffer~ qmw_living_spectral_mask @samps 2048", numinlets=1, numoutlets=2, outlettype=["float", "bang"])
    box(doc, "waveform", "waveform~", [550, 125, 560, 80], buffername="qmw_living_spectral_mask", numinlets=5, numoutlets=6, outlettype=["float", "float", "float", "float", "list", ""])
    box(doc, "testmask", "message", [20, 140, 80, 22], text="test_mask", numinlets=2, numoutlets=1, outlettype=[""])
    box(doc, "passthrough", "message", [110, 140, 90, 22], text="passthrough", numinlets=2, numoutlets=1, outlettype=[""])
    box(doc, "udp", "newobj", [20, 235, 165, 22], text="udpreceive 7460 cnmat", numinlets=1, numoutlets=1, outlettype=[""])
    box(doc, "osc", "newobj", [215, 235, 130, 22], text="OpenSoundControl", numinlets=1, numoutlets=3, outlettype=["", "", "OSCTimeTag"])
    box(doc, "living", "newobj", [375, 235, 120, 22], text="OSC-route /living", numinlets=1, numoutlets=2, outlettype=["", ""])
    box(doc, "rootroute", "newobj", [525, 235, 225, 22], text="OSC-route /spectral /publication", numinlets=1, numoutlets=3, outlettype=["", "", ""])
    box(doc, "spectralroute", "newobj", [525, 285, 200, 22], text="OSC-route /history /playback", numinlets=1, numoutlets=3, outlettype=["", "", ""])
    box(doc, "historyroute", "newobj", [380, 335, 430, 22], text="OSC-route /shape /magnitudes /frequencies_hz /transients", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""])
    box(doc, "playbackroute", "newobj", [830, 285, 300, 22], text="OSC-route /blur_width /transition /freeze", numinlets=1, numoutlets=4, outlettype=["", "", "", ""])
    box(doc, "publicationroute", "newobj", [815, 235, 110, 22], text="OSC-route /end", numinlets=1, numoutlets=2, outlettype=["", ""])
    commands = (
        ("shape", "prepend shape", 380),
        ("magnitudes", "prepend magnitudes", 510),
        ("frequencies", "prepend frequencies_hz", 665),
        ("transients", "prepend transients", 850),
        ("blur", "prepend blur_width", 805),
        ("transition", "prepend transition", 950),
        ("freeze", "prepend freeze", 1080),
        ("commit", "prepend commit", 805),
    )
    for identifier, text, x in commands:
        y = 385 if identifier in {"shape", "magnitudes", "frequencies", "transients"} else 335
        box(doc, identifier, "newobj", [x, y, 125, 22], text=text, numinlets=1, numoutlets=1, outlettype=[""])
    box(doc, "js", "newobj", [530, 465, 240, 22], text="js qmw_living_spectral_mask_v1.js", numinlets=1, numoutlets=2, outlettype=["", ""])
    box(doc, "status", "message", [530, 515, 395, 22], text="", numinlets=2, numoutlets=1, outlettype=[""])
    box(doc, "transient", "flonum", [950, 465, 75, 22], minimum=0.0, maximum=1.0, numinlets=1, numoutlets=2, outlettype=["", "bang"])
    box(doc, "note", "comment", [20, 610, 1090, 60], text="pfft~ uses a 4096-sample FFT and overlap 4 (hop 1024; latency 3072 samples). fftin~ supplies real, imaginary, and bin-index signals. The eigenfield history becomes a magnitude mask; the audio STFT phase is preserved inside the pfft~ patch.", fontsize=13.0)
    line(doc, "source", 0, "pfft", 0)
    line(doc, "pfft", 0, "gain", 0)
    line(doc, "gain", 0, "dac", 0)
    line(doc, "gain", 0, "dac", 1)
    line(doc, "udp", 0, "osc", 0)
    line(doc, "osc", 0, "living", 0)
    line(doc, "living", 0, "rootroute", 0)
    line(doc, "rootroute", 0, "spectralroute", 0)
    line(doc, "rootroute", 1, "publicationroute", 0)
    line(doc, "spectralroute", 0, "historyroute", 0)
    line(doc, "spectralroute", 1, "playbackroute", 0)
    line(doc, "historyroute", 0, "shape", 0)
    line(doc, "historyroute", 1, "magnitudes", 0)
    line(doc, "historyroute", 2, "frequencies", 0)
    line(doc, "historyroute", 3, "transients", 0)
    line(doc, "playbackroute", 0, "blur", 0)
    line(doc, "playbackroute", 1, "transition", 0)
    line(doc, "playbackroute", 2, "freeze", 0)
    line(doc, "publicationroute", 0, "commit", 0)
    for identifier in ("shape", "magnitudes", "frequencies", "transients", "blur", "transition", "freeze", "commit"):
        line(doc, identifier, 0, "js", 0)
    line(doc, "js", 0, "status", 1)
    line(doc, "js", 1, "transient", 0)
    line(doc, "testmask", 0, "js", 0)
    line(doc, "passthrough", 0, "js", 0)
    return write(
        "QMW_Living_Spectral_PFFT_v1.maxpat",
        doc,
        [
            "qmw_living_spectral_mask_pfft_v1.maxpat",
            "qmw_living_spectral_mask_v1.js",
            "OpenSoundControl.mxo",
            "OSC-route.mxo",
        ],
    )


if __name__ == "__main__":
    for generated in (build_pfft(), build_parent()):
        print(f"generated {generated.name}")
