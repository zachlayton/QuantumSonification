#!/usr/bin/env python3
"""Extend the user-edited native GrainFlow v9 patch with OSC and Zeeman audio."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
source = ROOT / "QMW_Native_Grainflow_v9.maxpat"
target = ROOT / "QMW_Grainflow_Zeeman_v10.maxpat"
# Keep Max dependencies beside the generated patch. Max's dependency_cache
# metadata does not itself add arbitrary sibling folders to the search path.
controller_name = "qmw_fdg_zeeman_controller_v12.js"
voice_name = "qmw_fdg_zeeman_ring_voice_v12.maxpat"
(ROOT / controller_name).write_text(
    (PROJECT / "zeeman_resonator_v1/qmw_zeeman_controller_v1.js").read_text()
)
(ROOT / voice_name).write_text(
    (PROJECT / "zeeman_resonator_v1/qmw_zeeman_ring_voice_v1.maxpat").read_text()
)
doc = json.loads(source.read_text())
p = doc["patcher"]
boxes = {entry["box"]["id"]: entry["box"] for entry in p["boxes"]}
boxes["title"]["text"] = "QMW GRAINFLOW + ZEEMAN v10 — OSC FIELD / RESONATOR INTEGRATION"

def box(id_, maxclass, rect, **kwargs):
    payload = {"id": id_, "maxclass": maxclass, "patching_rect": rect}
    payload.update(kwargs)
    p["boxes"].append({"box": payload})

def line(src, outlet, dst, inlet=0):
    p["lines"].append({"patchline": {"source": [src, outlet], "destination": [dst, inlet]}})

# OSC telemetry.  A gate keeps the user's manual V9 controls authoritative
# until QUANTUM MAP is enabled.
box("osc_label", "comment", [20., 410., 650., 20.], text="OSC 7400: density-field telemetry → GrainFlow + Zeeman")
box("osc", "newobj", [20., 435., 125., 22.], text="udpreceive 7400", numinlets=1, numoutlets=1, outlettype=["FullPacket"])
box("osc_route", "newobj", [155., 435., 665., 22.], text="o.route /qmw/density_field/magnitude /qmw/density_field/phase /qmw/density_field/purity /qmw/density_field/entropy /qmw/density_field/coherence", numinlets=1, numoutlets=6, outlettype=["float"]*5+["FullPacket"])
box("map_label", "comment", [20., 470., 115., 20.], text="QUANTUM MAP")
box("map_enable", "toggle", [135., 468., 24., 24.], numinlets=1, numoutlets=1, outlettype=["int"])
box("map_init", "newobj", [165., 470., 78., 22.], text="loadmess 0", numinlets=1, numoutlets=1, outlettype=[""])

for name, x in (("mag", 20.), ("phase", 180.), ("purity", 340.), ("entropy", 500.), ("coherence", 660.)):
    box(name+"_gate", "newobj", [x, 505., 58., 22.], text="gate 1", numinlets=2, numoutlets=1, outlettype=[""])
line("osc", 0, "osc_route")
line("map_init", 0, "map_enable")
for index, name in enumerate(("mag", "phase", "purity", "entropy", "coherence")):
    line("map_enable", 0, name+"_gate", 0)
    line("osc_route", index, name+"_gate", 1)

# Meaningful safe ranges: phase spans one octave around unity; coherence never
# maps AM to zero; purity sets event density; entropy increases delay scatter.
box("phase_map", "newobj", [180., 540., 180., 22.], text=r"expr pow(2.\, $f1/3.14159265)", numinlets=1, numoutlets=1, outlettype=["float"])
box("phase_clip", "newobj", [180., 570., 92., 22.], text="clip 0.25 4.", numinlets=3, numoutlets=1, outlettype=[""])
box("coh_map", "newobj", [660., 540., 150., 22.], text="scale 0. 1. 0.15 1.", numinlets=6, numoutlets=1, outlettype=[""])
box("entropy_map", "newobj", [500., 540., 145., 22.], text="scale 0. 1. 0. 500.", numinlets=6, numoutlets=1, outlettype=[""])
line("phase_gate", 0, "phase_map"); line("phase_map", 0, "phase_clip"); line("phase_clip", 0, "rate")
line("coherence_gate", 0, "coh_map"); line("coh_map", 0, "amp")
line("purity_gate", 0, "obj-43")
line("entropy_gate", 0, "entropy_map"); line("entropy_map", 0, "obj-31")

# Zeeman quadrature ring-resonator bank. Magnitude becomes a bounded physical
# field control; presets retain the normal/D1/D2 line geometry.
box("zee_label", "comment", [20., 620., 500., 20.], text="ZEEMAN RESONATORS: field magnitude controls spectral splitting")
box("zee_field_map", "newobj", [20., 650., 145., 22.], text="scale 0. 1. 0. 8.", numinlets=6, numoutlets=1, outlettype=[""])
box("zee_field", "flonum", [175., 650., 72., 22.], minimum=0., maximum=20., numinlets=1, numoutlets=2, outlettype=["","bang"])
box("zee_field_pre", "newobj", [255., 650., 88., 22.], text="prepend field", numinlets=1, numoutlets=1, outlettype=[""])
box("zee_controller", "newobj", [355., 650., 235., 22.], text=f"js {controller_name}", numinlets=1, numoutlets=5, outlettype=["","float","list","list",""])
box("zee_poly", "newobj", [600., 650., 315., 22.], text=f"poly~ qmw_fdg_zeeman_ring_voice_v12 8 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal","signal"])
box("zee_gain_l", "newobj", [580., 690., 62., 22.], text="*~ 0.18", numinlets=2, numoutlets=1, outlettype=["signal"])
box("zee_gain_r", "newobj", [650., 690., 62., 22.], text="*~ 0.18", numinlets=2, numoutlets=1, outlettype=["signal"])
box("zee_normal", "message", [20., 690., 92., 22.], text="preset normal", numinlets=2, numoutlets=1, outlettype=[""])
box("zee_d1", "message", [120., 690., 117., 22.], text="preset sodium_d1", numinlets=2, numoutlets=1, outlettype=[""])
box("zee_d2", "message", [245., 690., 117., 22.], text="preset sodium_d2", numinlets=2, numoutlets=1, outlettype=[""])
box("zee_init", "newobj", [370., 690., 105., 22.], text="loadmess normal", numinlets=1, numoutlets=1, outlettype=[""])
line("mag_gate", 0, "zee_field_map"); line("zee_field_map", 0, "zee_field"); line("zee_field", 0, "zee_field_pre"); line("zee_field_pre", 0, "zee_controller")
for preset in ("zee_normal", "zee_d1", "zee_d2", "zee_init"): line(preset, 0, "zee_controller")
line("zee_controller", 0, "zee_poly")
line("zee_poly", 0, "zee_gain_l"); line("zee_poly", 1, "zee_gain_r")
line("zee_gain_l", 0, "dac", 0); line("zee_gain_r", 0, "dac", 1)

deps = p.setdefault("dependency_cache", [])
deps.extend([
    {"name":controller_name, "bootpath":"~/QuantumSonification/field_directed_grainflow_v1", "type":"TEXT"},
    {"name":voice_name, "bootpath":"~/QuantumSonification/field_directed_grainflow_v1", "type":"JSON"},
    {"name":"o.route.mxo", "type":"iLaX"},
])
target.write_text(json.dumps(doc, indent=2) + "\n")
print(f"generated {target.name}")
