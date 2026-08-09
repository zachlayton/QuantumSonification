#!/usr/bin/env python3
"""Build the composite Field-Directed Grainflow instrument."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
source_js=(PROJECT/"pauli_statistical_grainflow_v1/qmw_pauli_grainflow_scheduler_v1.js").read_text()
atlas_name="qmw_field_directed_atlas_v1.js"
(ROOT/atlas_name).write_text(
    (PROJECT/"pauli_statistical_grainflow_v1/qmw_quantum_wavetable_atlas_v1.js").read_text()
)
source_js=source_js.replace(
    'var magneticFactors = [-2.0, 0.0, -1.0, 1.0, 0.0, 2.0];',
    '''var magneticFactors = [-1.0, 0.0, 1.0, 99.0, 99.0, 99.0];
var transitionStrengths = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0];
var zeemanPreset = "normal";
var zeemanPresets = {
    normal: {factors:[-1,0,1,99,99,99], strengths:[1,1,1,0,0,0]},
    sodium_d1: {factors:[-4/3,-2/3,2/3,4/3,99,99], strengths:[2/3,1/3,1/3,2/3,0,0]},
    sodium_d2: {factors:[-5/3,-1,-1/3,1/3,1,5/3], strengths:[1/3,1,2/3,2/3,1,1/3]}
};''')
source_js=source_js.replace(
    'function statistics(value) {',
    '''function preset(value) {
    var key=String(value).toLowerCase();
    if (!zeemanPresets[key]) return;
    zeemanPreset=key;
    magneticFactors=zeemanPresets[key].factors.slice();
    transitionStrengths=zeemanPresets[key].strengths.slice();
    tick();
}

function statistics(value) {''')
source_js=source_js.replace(
    'var probability = active ? Math.min(1.0, baseDensity * (1.0 + 0.22 * (occupancy - 1))) : 0.0;\n        var amplitude = active ? Math.sqrt(occupancy / Math.max(1, total)) : 0.0;',
    '''var lineStrength = transitionStrengths[stream];
        var probability = active ? Math.min(1.0, baseDensity * lineStrength * (1.0 + 0.22 * (occupancy - 1))) : 0.0;
        var amplitude = active ? Math.sqrt(occupancy * lineStrength / Math.max(1, total)) : 0.0;''')
source_js=source_js.replace(
    'outlet(2, "set", statisticsName.toUpperCase()',
    'outlet(2, "set", zeemanPreset.toUpperCase() + " | " + statisticsName.toUpperCase()')
(ROOT/"qmw_field_directed_scheduler_v1.js").write_text(source_js)

doc=json.loads((PROJECT/"pauli_statistical_grainflow_v1/QMW_Pauli_Statistical_Grainflow_v1.maxpat").read_text())
p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW FIELD-DIRECTED GRAINFLOW v3 — ZEEMAN ENERGY SHELL"
boxes["subtitle"]["text"]="Zeeman line geometry selects six energy modes; quantum statistics assigns occupations; GrainFlow renders occupied modes as events."
boxes["scheduler"]["text"]="js qmw_field_directed_scheduler_v1.js"
boxes["init_particles"]["text"]="loadmess 2"
boxes["init_stats"]["text"]="loadmess 0"
boxes["atlas_js"]["text"]=f"js {atlas_name}"
if "saved_object_attributes" in boxes["scheduler"]:
    boxes["scheduler"]["saved_object_attributes"]["filename"]="qmw_field_directed_scheduler_v1.js"
buttons=[
 {"id":"fdg_normal","maxclass":"message","text":"preset normal","patching_rect":[620.,205.,100.,22.],"presentation":1,"presentation_rect":[620.,205.,100.,22.],"numinlets":2,"numoutlets":1,"outlettype":[""]},
 {"id":"fdg_d1","maxclass":"message","text":"preset sodium_d1","patching_rect":[730.,205.,125.,22.],"presentation":1,"presentation_rect":[730.,205.,125.,22.],"numinlets":2,"numoutlets":1,"outlettype":[""]},
 {"id":"fdg_d2","maxclass":"message","text":"preset sodium_d2","patching_rect":[865.,205.,125.,22.],"presentation":1,"presentation_rect":[865.,205.,125.,22.],"numinlets":2,"numoutlets":1,"outlettype":[""]},
 {"id":"fdg_label","maxclass":"comment","text":"ZEEMAN MODE GEOMETRY","patching_rect":[620.,180.,370.,20.],"presentation":1,"presentation_rect":[620.,180.,370.,20.]},
]
p["boxes"].extend({"box":b} for b in buttons)
for bid in ("fdg_normal","fdg_d1","fdg_d2"):
    p["lines"].append({"patchline":{"source":[bid,0],"destination":["scheduler",0]}})
for dep in p.get("dependency_cache",[]):
    if dep.get("name")=="qmw_pauli_grainflow_scheduler_v1.js": dep["name"]="qmw_field_directed_scheduler_v1.js"; dep["bootpath"]="~/QuantumSonification/field_directed_grainflow_v1"
    if dep.get("name")=="qmw_quantum_wavetable_atlas_v1.js": dep["name"]=atlas_name; dep["bootpath"]="~/QuantumSonification/field_directed_grainflow_v1"
out=ROOT/"QMW_Field_Directed_Grainflow_v3.maxpat"
out.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {out.name}")
