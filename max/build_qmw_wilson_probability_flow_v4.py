#!/usr/bin/env python3
"""Build the v4 Max probability-flow front panel from the working v3.3 UI."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_Recursive_Wilson_Circuit_Instrument_v3_3.maxpat"
OUTPUT = ROOT / "QMW_Wilson_Probability_Flow_Instrument_v4.maxpat"


def main() -> int:
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["title"]["text"] = "QMW · WILSON HEXANY PROBABILITY-FLOW INSTRUMENT v4"
    boxes["instructions"]["text"] = (
        "Run examples/qmw_wilson_probability_flow_v4.py · each exchange sounds as "
        "departure → arrival · probability current = velocity · θ = travel time · "
        "β + interference phase = CC74"
    )
    boxes["receive_label"]["text"] = "DIRECTED HEXANY FLOW · sparse movement on J(4,2)"
    boxes["route_recursive"]["text"] = (
        "OSC-route /wilson_flow_note /status /error /running /seed_accepted"
    )
    boxes["note_unpack"]["text"] = "unpack i i i i i i f f f f i i i i"
    boxes["midi_label"]["text"] = (
        "MPE FLOW OUTPUT · departure then arrival on stable vertex channels 2–7"
    )
    boxes["midi_note"]["text"] = (
        "Only the strongest directed probability current sounds each generation.\n"
        "θ controls travel time; flow magnitude controls velocity.\n"
        "β + interference phase controls CC74; exact Wilson ratios remain the vertices."
    )

    for entry in patcher["lines"]:
        patchline = entry["patchline"]
        source = patchline["source"]
        destination = patchline["destination"]
        if source[0] != "note_unpack":
            continue
        target, inlet = destination
        if target == "makenote" and inlet == 3:
            source[1] = 12
        elif target == "noteout" and inlet == 2:
            source[1] = 12
        elif target == "xbendout" and inlet == 0:
            source[1] = 10
        elif target == "xbendout" and inlet == 1:
            source[1] = 12
        elif target == "ctlout" and inlet == 0:
            source[1] = 11
        elif target == "ctlout" and inlet == 2:
            source[1] = 12

    OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
