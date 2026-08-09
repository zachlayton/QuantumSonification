#!/usr/bin/env python3
"""Build the lightweight QAC/IBM 256-point wavetable oscillator patch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_SENDER = ROOT / "qac_quantumsonification_sender_v1.maxpat"
OUTPUT_SENDER = ROOT / "qac_wavetable_sender_v1.maxpat"
OUTPUT_PATCH = ROOT / "QMW_QAC_Wavetable_Oscillator_v1.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def main() -> int:
    sender = SOURCE_SENDER.read_text(encoding="utf-8").replace(
        "udpsend 127.0.0.1 7401", "udpsend 127.0.0.1 7411"
    )
    OUTPUT_SENDER.write_text(sender, encoding="utf-8")

    patcher = {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [80.0, 80.0, 980.0, 680.0],
        "openinpresentation": 1,
        "gridsize": [15.0, 15.0],
        "boxes": [
            box("panel", "panel", [10.0,10.0,940.0,625.0], presentation=1, presentation_rect=[10.0,10.0,940.0,625.0], bgcolor=[0.045,0.06,0.09,1.0]),
            box("title", "comment", [28.0,22.0,850.0,28.0], text="QAC → LOCAL / IBM QUANTUM → 256-POINT WAVETABLE", fontsize=18.0, presentation=1, presentation_rect=[28.0,22.0,850.0,28.0], textcolor=[0.85,0.93,1.0,1.0]),
            box("instructions", "comment", [28.0,56.0,880.0,38.0], text="Build a circuit in QAC, export QASM, then hear the local table immediately and the IBM-count table when the job completes.", presentation=1, presentation_rect=[28.0,56.0,880.0,38.0], textcolor=[0.65,0.72,0.82,1.0]),
            box("qac", "newobj", [28.0,110.0,235.0,22.0], text="och.microqiskit qc 4 4 sim 256 1", numinlets=1, numoutlets=2, presentation=1, presentation_rect=[28.0,110.0,235.0,22.0]),
            box("bell", "message", [28.0,146.0,420.0,22.0], text="QuantumCircuit qc 4 4, qc h 0, qc cx 0 1, Simulator sim qc 256", presentation=1, presentation_rect=[28.0,146.0,420.0,22.0]),
            box("getqasm", "message", [470.0,146.0,92.0,22.0], text="sim get_qasm", presentation=1, presentation_rect=[470.0,146.0,92.0,22.0]),
            box("sender", "newobj", [285.0,110.0,180.0,22.0], text="qac_wavetable_sender_v1", numinlets=1, numoutlets=1),
            box("sendstatus", "message", [485.0,110.0,360.0,22.0], text="sender ready", presentation=1, presentation_rect=[485.0,110.0,360.0,22.0]),
            box("udp", "newobj", [28.0,210.0,132.0,22.0], text="udpreceive 7412", numinlets=1, numoutlets=2),
            box("oroute", "newobj", [175.0,210.0,610.0,22.0], text="o.route /qmw/wavetable/points /qmw/wavetable/status /qmw/wavetable/error /qmw/wavetable/correlations", numinlets=1, numoutlets=5),
            box("rawprint", "newobj", [625.0,250.0,135.0,22.0], text="print WTABLE_RAW"),
            box("loader", "newobj", [28.0,260.0,195.0,22.0], text="js qmw_wavetable_receiver_v1.js", numinlets=1, numoutlets=3),
            box("buffer", "newobj", [28.0,305.0,265.0,22.0], text="buffer~ qmw_wavetable @samps 256 @channels 1"),
            box("display", "multislider", [28.0,350.0,880.0,150.0], size=256, setminmax=[-1.0,1.0], presentation=1, presentation_rect=[28.0,350.0,880.0,150.0], bgcolor=[0.08,0.1,0.14,1.0], slidercolor=[0.34,0.78,1.0,1.0]),
            box("freq", "flonum", [28.0,525.0,75.0,22.0], value=110.0, presentation=1, presentation_rect=[28.0,525.0,75.0,22.0]),
            box("freqlabel", "comment", [110.0,525.0,95.0,20.0], text="frequency Hz", presentation=1, presentation_rect=[110.0,525.0,95.0,20.0], textcolor=[0.7,0.76,0.84,1.0]),
            box("phasor", "newobj", [28.0,565.0,62.0,22.0], text="sig~ 110."),
            box(
                "wave", "gen.codebox~", [110.0,555.0,390.0,105.0],
                code='Buffer table("qmw_wavetable");\nHistory phase(0);\nfreq = max(in1, 0);\nphase = fract(phase + freq / samplerate);\nsample, idx = wave(table, phase, 0, 256, 0, channels=1);\nout1 = sample;\nout2 = phase;',
                numinlets=1, numoutlets=2, outlettype=["signal", "signal"],
            ),
            box("gain", "newobj", [520.0,565.0,52.0,22.0], text="*~ 0.12"),
            box("dac", "newobj", [345.0,560.0,48.0,32.0], text="ezdac~", presentation=1, presentation_rect=[345.0,555.0,48.0,32.0]),
            box("statuslabel", "comment", [430.0,525.0,62.0,20.0], text="STATUS", presentation=1, presentation_rect=[430.0,525.0,62.0,20.0], textcolor=[0.34,0.78,1.0,1.0]),
            box("status", "message", [500.0,522.0,408.0,24.0], text="waiting for wavetable", presentation=1, presentation_rect=[500.0,522.0,408.0,24.0]),
            box("print", "newobj", [780.0,210.0,150.0,22.0], text="print WTABLE_OTHER"),
            box("corr_unpack", "newobj", [505.0,250.0,90.0,22.0], text="unpack i f f f"),
            box("xx", "flonum", [610.0,250.0,65.0,22.0], presentation=1, presentation_rect=[610.0,305.0,65.0,22.0]),
            box("yy", "flonum", [690.0,250.0,65.0,22.0], presentation=1, presentation_rect=[690.0,305.0,65.0,22.0]),
            box("zz", "flonum", [770.0,250.0,65.0,22.0], presentation=1, presentation_rect=[770.0,305.0,65.0,22.0]),
            box("corr_label", "comment", [610.0,278.0,230.0,20.0], text="XX                 YY                 ZZ", presentation=1, presentation_rect=[610.0,332.0,230.0,20.0], textcolor=[0.51,0.81,1.0,1.0]),
        ],
        "lines": [
            line("bell",0,"qac"), line("getqasm",0,"qac"), line("qac",0,"sender"), line("sender",0,"sendstatus"),
            line("udp",0,"oroute"), line("udp",0,"rawprint"),
            line("oroute",0,"loader"), line("oroute",1,"status"), line("oroute",2,"status"), line("oroute",3,"corr_unpack"), line("oroute",4,"print"),
            line("corr_unpack",1,"xx"), line("corr_unpack",2,"yy"), line("corr_unpack",3,"zz"),
            line("loader",1,"display"), line("loader",2,"status"),
            line("freq",0,"phasor"), line("phasor",0,"wave"), line("wave",0,"gain"), line("gain",0,"dac",0), line("gain",0,"dac",1),
        ],
        "dependency_cache": [
            {"name":"qmw_wavetable_receiver_v1.js","bootpath":str(ROOT),"patcherrelativepath":".","type":"TEXT","implicit":1},
            {"name":"qac_wavetable_sender_v1.maxpat","bootpath":str(ROOT),"patcherrelativepath":".","type":"JSON","implicit":1},
            {"name":"qac_qasm_sender_v1.js","bootpath":str(ROOT),"patcherrelativepath":".","type":"TEXT","implicit":1},
            {"name":"o.route.mxo","type":"iLaX"},
        ],
    }
    OUTPUT_PATCH.write_text(json.dumps({"patcher": patcher}, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT_PATCH.name} and {OUTPUT_SENDER.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
