#!/usr/bin/env python3
"""Build a separate density-morph version of the simple wavetable workshop."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_Four_Qubit_256_Wavetable_Workshop_v1.maxpat"
OUTPUT = ROOT / "QMW_Four_Qubit_256_Density_Morph_Workshop_v1.maxpat"


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
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    removed = {
        "udp",
        "oroute",
        "loader",
        "buffer",
        "phasor",
        "wave",
        "gain",
        "bridge-command",
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

    boxes["title"]["text"] = "QAC/QASM → DENSITY MATRIX → MORPHING WAVETABLE"
    boxes["instructions"]["text"] = (
        "The circuit seeds a physical 16×16 density matrix. Its 256 real "
        "entries become an evolving 256-sample waveform."
    )
    boxes["wavetable-title"]["text"] = "ACTIVE WAVEFORM · STATIC ↔ DENSITY"
    boxes["wavetable-note"]["text"] = (
        "The display and oscillator crossfade together; continuous oscillator "
        "phase is preserved while density frames change."
    )
    boxes["mapping-note"]["text"] = (
        "MEASUREMENT CALLBACK: the diagonal contains outcome probabilities; "
        "off-diagonal entries contain coherence. Flattening real(ρ) makes "
        "all 256 matrix positions audible."
    )
    boxes["mapping-note"]["presentation_rect"] = [24.0, 720.0, 760.0, 42.0]
    boxes["bridge-label"]["text"] = "DENSITY MORPH STATUS"
    boxes["bridge-label"]["presentation_rect"] = [24.0, 650.0, 180.0, 20.0]
    boxes["status"]["text"] = (
        "Start qac_density_morph_bridge_v1.py, build a circuit, then press PLAY."
    )
    boxes["status"]["presentation_rect"] = [24.0, 672.0, 760.0, 38.0]
    boxes["safety-note"]["presentation"] = 0
    boxes["sendstatus"]["presentation_rect"] = [24.0, 518.0, 760.0, 24.0]
    boxes["spectrum-title"]["text"] = "MORPHING WAVETABLE OSCILLATOR SPECTRUM"

    patcher["boxes"].extend(
        [
            box(
                "mode-label",
                "comment",
                [24.0, 558.0, 128.0, 20.0],
                text="STATIC / DENSITY",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 558.0, 128.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
            box(
                "mode-toggle",
                "toggle",
                [155.0, 555.0, 26.0, 26.0],
                presentation=1,
                presentation_rect=[155.0, 555.0, 26.0, 26.0],
                parameter_enable=0,
            ),
            box(
                "depth-label",
                "comment",
                [205.0, 558.0, 95.0, 20.0],
                text="MORPH DEPTH",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[205.0, 558.0, 95.0, 20.0],
            ),
            box(
                "depth",
                "flonum",
                [302.0, 555.0, 68.0, 24.0],
                minimum=0.0,
                maximum=1.0,
                presentation=1,
                presentation_rect=[302.0, 555.0, 68.0, 24.0],
            ),
            box(
                "depth-default",
                "newobj",
                [940.0, 1110.0, 86.0, 22.0],
                text="loadmess 1.",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "blend-expr",
                "newobj",
                [1035.0, 1110.0, 92.0, 22.0],
                text="expr $f1 * $f2",
                numinlets=2,
                numoutlets=1,
                outlettype=["float"],
            ),
            box(
                "blend-prepend",
                "newobj",
                [1135.0, 1110.0, 88.0, 22.0],
                text="prepend blend",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "source-xfade-pack",
                "newobj",
                [1230.0, 1110.0, 86.0, 22.0],
                text="pack 0. 120",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "source-xfade-line",
                "newobj",
                [1325.0, 1110.0, 42.0, 22.0],
                text="line~",
                numinlets=2,
                numoutlets=2,
                outlettype=["signal", "bang"],
            ),
            box(
                "rate-label",
                "comment",
                [390.0, 558.0, 90.0, 20.0],
                text="MORPH RATE",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[390.0, 558.0, 90.0, 20.0],
            ),
            box(
                "rate",
                "flonum",
                [480.0, 555.0, 68.0, 24.0],
                minimum=0.1,
                maximum=4.0,
                presentation=1,
                presentation_rect=[480.0, 555.0, 68.0, 24.0],
            ),
            box(
                "rate-default",
                "newobj",
                [940.0, 1140.0, 86.0, 22.0],
                text="loadmess 1.",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "rate-pack",
                "newobj",
                [1035.0, 1140.0, 238.0, 22.0],
                text="o.pack /qmw/density/control/rate",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "play-label",
                "comment",
                [570.0, 558.0, 42.0, 20.0],
                text="PLAY",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[570.0, 558.0, 42.0, 20.0],
            ),
            box(
                "play-toggle",
                "toggle",
                [612.0, 555.0, 26.0, 26.0],
                presentation=1,
                presentation_rect=[612.0, 555.0, 26.0, 26.0],
                parameter_enable=0,
            ),
            box(
                "play-pack",
                "newobj",
                [1035.0, 1170.0, 238.0, 22.0],
                text="o.pack /qmw/density/control/play",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "reset-button",
                "button",
                [660.0, 555.0, 26.0, 26.0],
                presentation=1,
                presentation_rect=[660.0, 555.0, 26.0, 26.0],
            ),
            box(
                "reset-label",
                "comment",
                [690.0, 558.0, 55.0, 20.0],
                text="RESET",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[690.0, 558.0, 55.0, 20.0],
            ),
            box(
                "reset-pack",
                "newobj",
                [1035.0, 1200.0, 238.0, 22.0],
                text="o.pack /qmw/density/control/reset",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "control-udp",
                "newobj",
                [1285.0, 1170.0, 150.0, 22.0],
                text="udpsend 127.0.0.1 7413",
                numinlets=1,
                numoutlets=0,
            ),
            box(
                "metrics-label",
                "comment",
                [24.0, 610.0, 95.0, 20.0],
                text="ρ METRICS",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 610.0, 95.0, 20.0],
                textcolor=[1.0, 0.68, 0.3, 1.0],
            ),
            box(
                "purity",
                "flonum",
                [125.0, 607.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[125.0, 607.0, 68.0, 24.0],
            ),
            box(
                "purity-label",
                "comment",
                [198.0, 610.0, 48.0, 20.0],
                text="purity",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[198.0, 610.0, 48.0, 20.0],
            ),
            box(
                "entropy",
                "flonum",
                [275.0, 607.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[275.0, 607.0, 68.0, 24.0],
            ),
            box(
                "entropy-label",
                "comment",
                [348.0, 610.0, 55.0, 20.0],
                text="entropy",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[348.0, 610.0, 55.0, 20.0],
            ),
            box(
                "coherence",
                "flonum",
                [430.0, 607.0, 68.0, 24.0],
                presentation=1,
                presentation_rect=[430.0, 607.0, 68.0, 24.0],
            ),
            box(
                "coherence-label",
                "comment",
                [503.0, 610.0, 75.0, 20.0],
                text="coherence",
                fontsize=11.0,
                presentation=1,
                presentation_rect=[503.0, 610.0, 75.0, 20.0],
            ),
            box(
                "metrics-unpack",
                "newobj",
                [940.0, 1065.0, 115.0, 22.0],
                text="unpack 0. 0. 0.",
                numinlets=1,
                numoutlets=3,
                outlettype=["float", "float", "float"],
            ),
            box(
                "density-udp",
                "newobj",
                [24.0, 835.0, 132.0, 22.0],
                text="udpreceive 7412",
                numinlets=1,
                numoutlets=1,
                outlettype=["FullPacket"],
            ),
            box(
                "density-route",
                "newobj",
                [175.0, 835.0, 820.0, 22.0],
                text=(
                    "o.route /qmw/density/static /qmw/density/frame "
                    "/qmw/density/metrics /qmw/density/status "
                    "/qmw/density/error"
                ),
                numinlets=1,
                numoutlets=5,
                outlettype=["", "", "", "", ""],
            ),
            box(
                "prepend-static",
                "newobj",
                [175.0, 875.0, 95.0, 22.0],
                text="prepend static",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-frame",
                "newobj",
                [280.0, 875.0, 95.0, 22.0],
                text="prepend frame",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "prepend-metrics",
                "newobj",
                [385.0, 875.0, 105.0, 22.0],
                text="prepend metrics",
                numinlets=1,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "density-receiver",
                "newobj",
                [510.0, 875.0, 258.0, 22.0],
                text="js qmw_density_morph_receiver_v1.js",
                numinlets=1,
                numoutlets=4,
                outlettype=["", "int", "", ""],
            ),
            box(
                "static-buffer",
                "newobj",
                [24.0, 920.0, 275.0, 22.0],
                text="buffer~ qmw_dm_static @samps 256 @channels 1",
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "density-buffer-a",
                "newobj",
                [310.0, 920.0, 290.0, 22.0],
                text="buffer~ qmw_dm_density_A @samps 256 @channels 1",
                numinlets=1,
                numoutlets=2,
                outlettype=["float", "bang"],
            ),
            box(
                "density-buffer-b",
                "newobj",
                [610.0, 920.0, 290.0, 22.0],
                text="buffer~ qmw_dm_density_B @samps 256 @channels 1",
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
                "static-wave",
                "newobj",
                [90.0, 965.0, 145.0, 22.0],
                text="wave~ qmw_dm_static",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-wave-a",
                "newobj",
                [250.0, 965.0, 165.0, 22.0],
                text="wave~ qmw_dm_density_A",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-wave-b",
                "newobj",
                [430.0, 965.0, 165.0, 22.0],
                text="wave~ qmw_dm_density_B",
                numinlets=3,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-xfade-pack",
                "newobj",
                [610.0, 965.0, 78.0, 22.0],
                text="pack f 70",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "density-xfade-line",
                "newobj",
                [700.0, 965.0, 42.0, 22.0],
                text="line~",
                numinlets=2,
                numoutlets=2,
                outlettype=["signal", "bang"],
            ),
            box(
                "density-xfade-inverse",
                "newobj",
                [755.0, 965.0, 58.0, 22.0],
                text="!-~ 1.",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-a-gain",
                "newobj",
                [250.0, 1005.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-b-gain",
                "newobj",
                [430.0, 1005.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-sum",
                "newobj",
                [340.0, 1040.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "source-xfade-inverse",
                "newobj",
                [1325.0, 1140.0, 58.0, 22.0],
                text="!-~ 1.",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "static-source-gain",
                "newobj",
                [90.0, 1040.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-source-gain",
                "newobj",
                [430.0, 1040.0, 36.0, 22.0],
                text="*~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "source-sum",
                "newobj",
                [250.0, 1075.0, 36.0, 22.0],
                text="+~",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "safe-scale",
                "newobj",
                [300.0, 1075.0, 52.0, 22.0],
                text="*~ 0.16",
                numinlets=2,
                numoutlets=1,
                outlettype=["signal"],
            ),
            box(
                "density-command",
                "comment",
                [24.0, 770.0, 760.0, 20.0],
                text=(
                    "engine: qac_density_morph_bridge_v1.py "
                    "· local density evolution · no IBM job"
                ),
                fontsize=11.0,
                presentation=1,
                presentation_rect=[24.0, 770.0, 760.0, 20.0],
                textcolor=[0.51, 0.81, 1.0, 1.0],
            ),
        ]
    )

    patcher["lines"].extend(
        [
            line("density-udp", 0, "density-route"),
            line("density-route", 0, "prepend-static"),
            line("density-route", 1, "prepend-frame"),
            line("density-route", 2, "prepend-metrics"),
            line("density-route", 3, "status"),
            line("density-route", 4, "status"),
            line("prepend-static", 0, "density-receiver"),
            line("prepend-frame", 0, "density-receiver"),
            line("prepend-metrics", 0, "density-receiver"),
            line("density-receiver", 0, "display"),
            line("density-receiver", 1, "density-xfade-pack"),
            line("density-receiver", 2, "status"),
            line("density-receiver", 3, "metrics-unpack"),
            line("metrics-unpack", 0, "purity"),
            line("metrics-unpack", 1, "entropy"),
            line("metrics-unpack", 2, "coherence"),
            line("mode-toggle", 0, "blend-expr"),
            line("depth-default", 0, "depth"),
            line("depth", 0, "blend-expr", 1),
            line("blend-expr", 0, "blend-prepend"),
            line("blend-prepend", 0, "density-receiver"),
            line("blend-expr", 0, "source-xfade-pack"),
            line("source-xfade-pack", 0, "source-xfade-line"),
            line("source-xfade-line", 0, "density-source-gain", 1),
            line("source-xfade-line", 0, "source-xfade-inverse"),
            line("source-xfade-inverse", 0, "static-source-gain", 1),
            line("rate-default", 0, "rate"),
            line("rate", 0, "rate-pack"),
            line("rate-pack", 0, "control-udp"),
            line("play-toggle", 0, "play-pack"),
            line("play-pack", 0, "control-udp"),
            line("reset-button", 0, "reset-pack"),
            line("reset-pack", 0, "control-udp"),
            line("frequency-default", 0, "freq"),
            line("freq", 0, "table-phasor"),
            line("table-phasor", 0, "static-wave"),
            line("table-phasor", 0, "density-wave-a"),
            line("table-phasor", 0, "density-wave-b"),
            line("density-xfade-pack", 0, "density-xfade-line"),
            line("density-xfade-line", 0, "density-b-gain", 1),
            line("density-xfade-line", 0, "density-xfade-inverse"),
            line("density-xfade-inverse", 0, "density-a-gain", 1),
            line("density-wave-a", 0, "density-a-gain"),
            line("density-wave-b", 0, "density-b-gain"),
            line("density-a-gain", 0, "density-sum"),
            line("density-b-gain", 0, "density-sum", 1),
            line("static-wave", 0, "static-source-gain"),
            line("density-sum", 0, "density-source-gain"),
            line("static-source-gain", 0, "source-sum"),
            line("density-source-gain", 0, "source-sum", 1),
            line("source-sum", 0, "safe-scale"),
            line("safe-scale", 0, "master-multiply"),
        ]
    )

    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies.append(
        {
            "name": "qmw_density_morph_receiver_v1.js",
            "bootpath": str(ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )

    OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name} from {SOURCE.name}; source was not modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
