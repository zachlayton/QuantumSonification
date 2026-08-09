#!/usr/bin/env python3
"""Build the QAC programmer with independent reseed and live-gate paths."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_QAC_Circuit_Programmer_v1.maxpat"
OUTPUT = ROOT / "QMW_QAC_Circuit_Programmer_v2.maxpat"


def box(identifier, maxclass, rect, **attrs):
    value = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    value.update(attrs)
    return {"box": value}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


def main() -> int:
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    patcher["rect"] = [80.0, 80.0, 900.0, 650.0]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["title"]["text"] = "QMW QAC CIRCUIT PROGRAMMER v2 · RESEED + LIVE GATE"
    boxes["ui"].update(
        filename="qmw_qac_circuit_programmer_v2.js",
        jsarguments=["qmw_qac_circuit_programmer_v2.js"],
        numoutlets=3,
        outlettype=["", "", ""],
        patching_rect=[25.0, 55.0, 780.0, 425.0],
        presentation_rect=[25.0, 55.0, 780.0, 425.0],
    )
    for identifier in ("status_label", "status"):
        boxes[identifier]["patching_rect"][1] += 42.0
        boxes[identifier]["presentation_rect"][1] += 42.0
    for identifier in ("qac", "tee", "sender", "qac_print", "tx_print"):
        boxes[identifier]["patching_rect"][1] += 42.0

    patcher["boxes"].extend(
        [
            box("gate_pack", "newobj", [25.0, 570.0, 158.0, 22.0], text="o.pack /qmw/qac/gate", numinlets=3, numoutlets=1, outlettype=["FullPacket"]),
            box("gate_udp", "newobj", [200.0, 570.0, 157.0, 22.0], text="udpsend 127.0.0.1 7401", numinlets=1, numoutlets=0),
            box("gate_print", "newobj", [375.0, 570.0, 156.0, 22.0], text="print QAC_LIVE_GATE_TX", numinlets=1, numoutlets=0),
        ]
    )
    patcher["lines"].extend(
        [
            line("ui", 2, "gate_pack"),
            line("gate_pack", 0, "gate_udp"),
            line("ui", 2, "gate_print"),
        ]
    )
    patcher["dependency_cache"] = [
        entry for entry in patcher.get("dependency_cache", [])
        if entry.get("name") != "qmw_qac_circuit_programmer_v1.js"
    ]
    patcher["dependency_cache"].extend(
        [
            {"name": "qmw_qac_circuit_programmer_v2.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1},
            {"name": "qmw_qac_circuit_programmer_v1.js", "bootpath": str(ROOT), "patcherrelativepath": ".", "type": "TEXT", "implicit": 1},
        ]
    )
    OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name} with reseed and incremental live-gate paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
