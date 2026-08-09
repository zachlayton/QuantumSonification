#!/usr/bin/env python3
"""Build the full 16-state CPS flow Max instrument."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_Wilson_Probability_Flow_Instrument_v4.maxpat"
OUTPUT = ROOT / "QMW_Complete_CPS_Flow_Instrument_v5.maxpat"


def main() -> int:
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    boxes["title"]["text"] = "QMW · COMPLETE 16-STATE WILSON CPS FLOW INSTRUMENT v5"
    boxes["instructions"]["text"] = (
        "Run examples/qmw_complete_cps_flow_v5.py · EMPTY/CLEAR is silent · BELL, "
        "GHZ, and WEAVE now commit and audition immediately · ranks 0)4…4)4 occupy "
        "successive registers · temperature explores Pascal grades 1–4–6–4–1 · "
        "circuit topology derives the Wilson master set and MOS address · "
        "LOOP sequences programmed columns; RECURSE explores probabilistically · "
        "XY moves within grades and H crosses grades"
    )
    boxes["receive_label"]["text"] = "COMPLETE CPS FLOW · 1–4–6–4–1 · all 16 basis states"
    boxes["route_recursive"]["text"] = (
        "OSC-route /cps_flow_note /modulation /status /error /running /seed_accepted"
    )
    boxes["route_recursive"]["patching_rect"][2] = 560.0
    if boxes["route_recursive"].get("presentation_rect"):
        boxes["route_recursive"]["presentation_rect"][2] = 560.0
    boxes["midi_label"]["text"] = (
        "MPE CPS OUTPUT · dynamic channels 2–16 · Ch. 1 master · from Max 1 → Ableton"
    )
    boxes["midi_note"]["text"] = (
        "0000 is the low identity pole; 1111 is the high total-product pole.\n"
        "Circuit commit gives a short population fingerprint; it never creates a background drone.\n"
        "Temperature 0 follows occupied vertices; 2 approaches Pascal-weighted exploration.\n"
        "Circuit tuning ON: paired/global/woven interaction geometry retunes the same basis identities."
    )

    # Inserting /modulation as outlet 1 shifts the existing status/error/
    # running outlets by one. Note outlet 0 remains unchanged.
    for entry in patcher["lines"]:
        source = entry["patchline"]["source"]
        if source[0] == "route_recursive" and source[1] >= 1:
            source[1] += 1

    # All three MIDI lanes must target the same virtual port.  Without an
    # explicit port, Max commonly selects AU DLS Synth, which sounds locally
    # but never reaches an Ableton track listening to ``from Max 1``.
    patcher["boxes"].extend(
        [
            {
                "box": {
                    "id": "midi_port_load",
                    "maxclass": "newobj",
                    "patching_rect": [1300.0, 530.0, 60.0, 22.0],
                    "text": "loadbang",
                }
            },
            {
                "box": {
                    "id": "midi_port_message",
                    "maxclass": "message",
                    "patching_rect": [1290.0, 570.0, 125.0, 22.0],
                    "text": 'port "from Max 1"',
                    "presentation": 1,
                    "presentation_rect": [1290.0, 570.0, 125.0, 22.0],
                }
            },
        ]
    )
    for source, outlet, destination, inlet in (
        ("midi_port_load", 0, "midi_port_message", 0),
        ("midi_port_message", 0, "noteout", 0),
        ("midi_port_message", 0, "midiout", 0),
        ("midi_port_message", 0, "ctlout", 0),
    ):
        patcher["lines"].append(
            {
                "patchline": {
                    "source": [source, outlet],
                    "destination": [destination, inlet],
                }
            }
        )

    # Global modulation bank. Values arrive atomically as normalized floats,
    # receive modest message-rate smoothing, and leave on channel 1 so they do
    # not collide with MPE member-channel CC74 expression.
    patcher["rect"][3] = max(float(patcher["rect"][3]), 1080.0)
    patcher["boxes"].extend(
        [
            {
                "box": {
                    "id": "mod_bank_label",
                    "maxclass": "comment",
                    "patching_rect": [20.0, 830.0, 1180.0, 22.0],
                    "text": "ABLETON GLOBAL MODULATION · OSC → smoothed MIDI CC · channel 1",
                    "fontsize": 14.0,
                    "presentation": 1,
                    "presentation_rect": [20.0, 830.0, 1180.0, 22.0],
                }
            },
            {
                "box": {
                    "id": "mod_unpack",
                    "maxclass": "newobj",
                    "patching_rect": [20.0, 858.0, 520.0, 22.0],
                    "text": "unpack i f f f f f f f f",
                    "presentation": 1,
                    "presentation_rect": [20.0, 858.0, 520.0, 22.0],
                }
            },
        ]
    )
    modulation_lanes = (
        ("entropy", 20),
        ("coherence", 21),
        ("entanglement", 22),
        ("participation", 23),
        ("phase_order", 24),
        ("grade_centroid", 25),
        ("hexany_mass", 26),
        ("flow_strength", 27),
    )
    for index, (name, cc_number) in enumerate(modulation_lanes):
        column = index % 4
        row = index // 4
        x = 20.0 + column * 360.0
        y = 892.0 + row * 78.0
        label = name.replace("_", " ") + f" · CC{cc_number}"
        lane_boxes = (
            (f"mod_{name}_label", "comment", [x, y, 180.0, 20.0], {"text": label}),
            (f"mod_{name}_slide", "newobj", [x, y + 25.0, 65.0, 22.0], {"text": "slide 2 4"}),
            (f"mod_{name}_scale", "newobj", [x + 72.0, y + 25.0, 125.0, 22.0], {"text": "scale 0. 1. 0 127"}),
            (f"mod_{name}_int", "newobj", [x + 204.0, y + 25.0, 24.0, 22.0], {"text": "i"}),
            (f"mod_{name}_change", "newobj", [x + 235.0, y + 25.0, 54.0, 22.0], {"text": "change"}),
            (f"mod_{name}_ctlout", "newobj", [x + 296.0, y + 25.0, 62.0, 22.0], {"text": f"ctlout {cc_number} 1"}),
        )
        for box_id, maxclass, rect, extras in lane_boxes:
            box = {
                "id": box_id,
                "maxclass": maxclass,
                "patching_rect": rect,
                "presentation": 1,
                "presentation_rect": rect,
            }
            box.update(extras)
            patcher["boxes"].append({"box": box})
        for source, outlet, destination, inlet in (
            ("mod_unpack", index + 1, f"mod_{name}_slide", 0),
            (f"mod_{name}_slide", 0, f"mod_{name}_scale", 0),
            (f"mod_{name}_scale", 0, f"mod_{name}_int", 0),
            (f"mod_{name}_int", 0, f"mod_{name}_change", 0),
            (f"mod_{name}_change", 0, f"mod_{name}_ctlout", 0),
            ("midi_port_message", 0, f"mod_{name}_ctlout", 0),
        ):
            patcher["lines"].append(
                {
                    "patchline": {
                        "source": [source, outlet],
                        "destination": [destination, inlet],
                    }
                }
            )
    patcher["lines"].append(
        {
            "patchline": {
                "source": ["route_recursive", 1],
                "destination": ["mod_unpack", 0],
            }
        }
    )

    # Phase 4 navigation.  Grade is an instrumentation filter (-1 auditions
    # the whole Pascal row); MOS numerator/denominator selects a related
    # Scale-Tree node; progress crossfades entering/leaving generator powers
    # while their voice IDs remain stable.
    navigation_boxes = [
        ("navigation_label", "comment", [20.0, 684.0, 760.0, 20.0],
         {"text": "PHASE 4 NAVIGATION · Pascal grade as instrument · MOS Scale-Tree morph"}),
        ("grade_label", "comment", [20.0, 714.0, 115.0, 20.0],
         {"text": "grade -1/all, 0–4"}),
        ("grade", "number", [140.0, 712.0, 55.0, 22.0],
         {"minimum": -1, "maximum": 4, "valueof": -1}),
        ("grade_pack", "newobj", [205.0, 712.0, 235.0, 22.0],
         {"text": "o.pack /qmw/wilson/navigation/grade"}),
        ("mos_label", "comment", [20.0, 746.0, 115.0, 20.0],
         {"text": "MOS target L/s"}),
        ("mos_numerator", "number", [140.0, 744.0, 45.0, 22.0],
         {"minimum": 1, "valueof": 3}),
        ("mos_denominator", "number", [190.0, 744.0, 45.0, 22.0],
         {"minimum": 2, "valueof": 7}),
        ("mos_pair", "newobj", [245.0, 744.0, 55.0, 22.0],
         {"text": "pak 3 7"}),
        ("mos_pack", "newobj", [310.0, 744.0, 270.0, 22.0],
         {"text": "o.pack /qmw/wilson/navigation/mos_target"}),
        ("morph_label", "comment", [20.0, 778.0, 115.0, 20.0],
         {"text": "morph 0–1"}),
        ("morph", "flonum", [140.0, 776.0, 70.0, 22.0],
         {"minimum": 0.0, "maximum": 1.0, "valueof": 1.0}),
        ("morph_pack", "newobj", [220.0, 776.0, 270.0, 22.0],
         {"text": "o.pack /qmw/wilson/navigation/mos_progress"}),
        ("default_grade", "newobj", [500.0, 712.0, 85.0, 22.0],
         {"text": "loadmess -1"}),
        ("default_mos_num", "newobj", [590.0, 712.0, 80.0, 22.0],
         {"text": "loadmess 3"}),
        ("default_mos_den", "newobj", [675.0, 712.0, 80.0, 22.0],
         {"text": "loadmess 7"}),
        ("default_morph", "newobj", [760.0, 712.0, 90.0, 22.0],
         {"text": "loadmess 1."}),
        ("tuning_label", "comment", [500.0, 778.0, 155.0, 20.0],
         {"text": "circuit-derived tuning"}),
        ("tuning_enabled", "toggle", [660.0, 776.0, 24.0, 24.0],
         {"valueof": 1}),
        ("tuning_pack", "newobj", [694.0, 776.0, 230.0, 22.0],
         {"text": "o.pack /qmw/wilson/tuning/enabled"}),
        ("default_tuning", "newobj", [860.0, 712.0, 85.0, 22.0],
         {"text": "loadmess 1"}),
    ]
    for box_id, maxclass, rect, extras in navigation_boxes:
        box = {
            "id": box_id,
            "maxclass": maxclass,
            "patching_rect": rect,
            "presentation": 1,
            "presentation_rect": rect,
        }
        box.update(extras)
        patcher["boxes"].append({"box": box})

    for source, outlet, destination, inlet in (
        ("grade", 0, "grade_pack", 0),
        ("grade_pack", 0, "control_udp", 0),
        ("mos_numerator", 0, "mos_pair", 0),
        ("mos_denominator", 0, "mos_pair", 1),
        ("mos_pair", 0, "mos_pack", 0),
        ("mos_pack", 0, "control_udp", 0),
        ("morph", 0, "morph_pack", 0),
        ("morph_pack", 0, "control_udp", 0),
        ("default_grade", 0, "grade", 0),
        ("default_mos_num", 0, "mos_numerator", 0),
        ("default_mos_den", 0, "mos_denominator", 0),
        ("default_morph", 0, "morph", 0),
        ("tuning_enabled", 0, "tuning_pack", 0),
        ("tuning_pack", 0, "control_udp", 0),
        ("default_tuning", 0, "tuning_enabled", 0),
    ):
        patcher["lines"].append(
            {
                "patchline": {
                    "source": [source, outlet],
                    "destination": [destination, inlet],
                }
            }
        )

    # makenote's optional channel inlet remembers the channel with each note
    # and reproduces it at its channel outlet for the scheduled note-off.  A
    # direct unpack→noteout channel connection makes overlapping note-offs use
    # whichever later voice most recently changed noteout's channel inlet.
    for entry in patcher["lines"]:
        patchline = entry["patchline"]
        if (
            patchline["source"] == ["note_unpack", 12]
            and patchline["destination"] == ["noteout", 2]
        ):
            patchline["source"] = ["makenote", 2]
    OUTPUT.write_text(json.dumps(document, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
