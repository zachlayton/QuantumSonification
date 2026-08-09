#!/usr/bin/env python3
"""Replace V10's one-off mappings with conductor-authored state frames."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / "QMW_Grainflow_Zeeman_v10.maxpat"
target = ROOT / "QMW_Conductor_Grainflow_Zeeman_v11.maxpat"
doc = json.loads(source.read_text())
p = doc["patcher"]
boxes = {entry["box"]["id"]: entry["box"] for entry in p["boxes"]}
boxes["title"]["text"] = "QMW CONDUCTOR GRAINFLOW + ZEEMAN v11 — DENSITY-ENGINE STATE"
boxes["osc_label"]["text"] = "OSC 7400: conductor frames drive the complete GrainFlow + Zeeman state"

def box(id_, maxclass, rect, **kwargs):
    payload = {"id": id_, "maxclass": maxclass, "patching_rect": rect}
    payload.update(kwargs)
    p["boxes"].append({"box": payload})

def line(src, outlet, dst, inlet=0):
    p["lines"].append({"patchline": {"source": [src, outlet], "destination": [dst, inlet]}})

# Disable the earlier scalar derivations. The OSC receiver remains shared.
legacy_gates = {"mag_gate", "phase_gate", "purity_gate", "entropy_gate", "coherence_gate"}
p["lines"] = [
    entry for entry in p["lines"]
    if not (
        entry["patchline"]["source"][0] == "osc_route"
        and entry["patchline"]["destination"][0] in legacy_gates
    )
]

box("conductor_route", "newobj", [20., 750., 555., 22.], text="o.route /qmw/conductor/grainflow /qmw/conductor/zeeman /qmw/conductor/zeeman/preset", numinlets=1, numoutlets=4, outlettype=["list","list","","FullPacket"])
box("grain_frame_gate", "newobj", [20., 785., 58., 22.], text="gate 1", numinlets=2, numoutlets=1, outlettype=[""])
box("zee_frame_gate", "newobj", [90., 785., 58., 22.], text="gate 1", numinlets=2, numoutlets=1, outlettype=[""])
box("preset_gate", "newobj", [160., 785., 58., 22.], text="gate 1", numinlets=2, numoutlets=1, outlettype=[""])
grain_fields = " ".join(["f"] * 14)
box("grain_unpack", "newobj", [20., 820., 430., 22.], text=f"unpack {grain_fields}", numinlets=1, numoutlets=14, outlettype=["float"]*14)
box("zee_unpack", "newobj", [470., 820., 125., 22.], text="unpack f f f f", numinlets=1, numoutlets=4, outlettype=["float"]*4)
box("zee_carrier_pre", "newobj", [600., 820., 115., 22.], text="prepend carrierfreq", numinlets=1, numoutlets=1, outlettype=[""])
box("zee_spread_pre", "newobj", [710., 820., 95., 22.], text="prepend spread", numinlets=1, numoutlets=1, outlettype=[""])
box("preset_pre", "newobj", [815., 820., 95., 22.], text="prepend preset", numinlets=1, numoutlets=1, outlettype=[""])
box("frame_status", "message", [235., 785., 560., 22.], text="waiting for /qmw/conductor/grainflow", numinlets=2, numoutlets=1, outlettype=[""])

line("osc", 0, "conductor_route")
for gate in ("grain_frame_gate", "zee_frame_gate", "preset_gate"):
    line("map_enable", 0, gate, 0)
line("conductor_route", 0, "grain_frame_gate", 1)
line("conductor_route", 1, "zee_frame_gate", 1)
line("conductor_route", 2, "preset_gate", 1)
line("grain_frame_gate", 0, "grain_unpack")
line("grain_frame_gate", 0, "frame_status")
line("zee_frame_gate", 0, "zee_unpack")
line("preset_gate", 0, "preset_pre"); line("preset_pre", 0, "zee_controller")

# Exact order published by grainflow_conductor_state(). Attribute UI objects
# display the conductor values and forward correctly named messages to grainflow~.
destinations = [
    "obj-34", "obj-43", "obj-24", "obj-29", "obj-30", "obj-31",
    "obj-32", "obj-33", "obj-40", "obj-41", "obj-46", "obj-48",
    "rate", "amp",
]
for outlet, destination in enumerate(destinations):
    line("grain_unpack", outlet, destination)

# field, carrier, spread and bank level
line("zee_unpack", 0, "zee_field")
line("zee_unpack", 1, "zee_carrier_pre"); line("zee_carrier_pre", 0, "zee_controller")
line("zee_unpack", 2, "zee_spread_pre"); line("zee_spread_pre", 0, "zee_controller")
line("zee_unpack", 3, "zee_gain_l", 1); line("zee_unpack", 3, "zee_gain_r", 1)

target.write_text(json.dumps(doc, indent=2) + "\n")
print(f"generated {target.name}")
