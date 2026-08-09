#!/usr/bin/env python3
"""Create V6 from the frozen V5 workshop patch."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_QAC_QFT_Spectral_Synthesizer_v5.maxpat"
target=ROOT/"QMW_QAC_QFT_Coherence_Comparator_v6.maxpat"
renderer_v6=ROOT/"qmw_compact_state_renderer_v6.js"
renderer_v6.write_text(
    (ROOT/"qmw_compact_state_renderer_v5.js").read_text(encoding="utf-8")
    .replace("qmw_v5_","qmw_v6_"), encoding="utf-8"
)
doc=json.loads(source.read_text(encoding="utf-8"))
p=doc["patcher"]
for entry in p["boxes"]:
    box=entry["box"]
    if isinstance(box.get("text"),str):
        box["text"]=box["text"].replace("qmw_v5_","qmw_v6_").replace(
            "qmw_compact_state_renderer_v5.js","qmw_compact_state_renderer_v6.js")
    if box.get("filename")=="qmw_compact_state_renderer_v5.js":
        box["filename"]="qmw_compact_state_renderer_v6.js"
    attrs=box.get("saved_object_attributes",{})
    if attrs.get("filename")=="qmw_compact_state_renderer_v5.js":
        attrs["filename"]="qmw_compact_state_renderer_v6.js"
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
route=boxes["oroute"]
route["text"] += " /qmw/workshop/density_lines"
route["numoutlets"] = 13
route["outlettype"] = [""]*12+["FullPacket"]
for entry in p["lines"]:
    line=entry["patchline"]
    if line["source"]==["oroute",11] and line["destination"][0]=="print": line["source"]=["oroute",12]

add=[
 {"id":"v6_compare","maxclass":"newobj","text":"js qmw_pauli_coherence_v6.js","patching_rect":[1200.,900.,220.,22.],"numinlets":1,"numoutlets":5,"outlettype":["","list","list","list","list"]},
 {"id":"v6_local_unpack","maxclass":"newobj","text":"unpack "+" ".join(["f"]*15),"patching_rect":[10.,630.,880.,22.],"numinlets":1,"numoutlets":15,"outlettype":["float"]*15},
 {"id":"v6_ibm_unpack","maxclass":"newobj","text":"unpack "+" ".join(["f"]*15),"patching_rect":[10.,660.,880.,22.],"numinlets":1,"numoutlets":15,"outlettype":["float"]*15},
 {"id":"v6_delta_unpack","maxclass":"newobj","text":"unpack "+" ".join(["f"]*15),"patching_rect":[10.,690.,880.,22.],"numinlets":1,"numoutlets":15,"outlettype":["float"]*15},
 {"id":"v6_rows_label","maxclass":"comment","text":"LOCAL / IBM / IBM-LOCAL: XI YI ZI | IX IY IZ | XX XY XZ | YX YY YZ | ZX ZY ZZ","patching_rect":[10.,605.,880.,20.],"presentation":1,"presentation_rect":[10.,625.,880.,20.]},
]
for prefix,y in (("local",650.),("ibm",680.),("delta",710.)):
    for i,label in enumerate(("XI","YI","ZI","IX","IY","IZ","XX","XY","XZ","YX","YY","YZ","ZX","ZY","ZZ")):
        add.append({"id":f"v6_{prefix}_{label}","maxclass":"flonum","patching_rect":[10.+i*58,y,54.,22.],"presentation":1,"presentation_rect":[10.+i*58,y,54.,22.],"numinlets":1,"numoutlets":2,"outlettype":["","bang"]})
for name in ("local","ibm","difference"):
    add.extend([
      {"id":f"v6_coh_buf_{name}","maxclass":"newobj","text":f"buffer~ qmw_v6_coherence_{name} @samps 256 @channels 1","patching_rect":[1200.,940.+40*(name!="local"),300.,22.],"numinlets":1,"numoutlets":2,"outlettype":["float","bang"]},
      {"id":f"v6_coh_wave_{name}","maxclass":"newobj","text":f"wave~ qmw_v6_coherence_{name}","patching_rect":[1200.,1060.+30*(name!="local"),190.,22.],"numinlets":3,"numoutlets":1,"outlettype":["signal"]},
    ])
add.extend([
 {"id":"v6_coh_local_mul","maxclass":"newobj","text":"*~","patching_rect":[1200.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_ibm_mul","maxclass":"newobj","text":"*~","patching_rect":[1250.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_source_sum","maxclass":"newobj","text":"+~","patching_rect":[1300.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_difference_mul","maxclass":"newobj","text":"*~","patching_rect":[1350.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_mix_sum","maxclass":"newobj","text":"+~","patching_rect":[1400.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_gain","maxclass":"flonum","minimum":0.0,"maximum":1.0,"patching_rect":[1080.,1080.,75.,22.],"presentation":1,"presentation_rect":[1080.,1038.,75.,22.],"numinlets":1,"numoutlets":2,"outlettype":["","bang"]},
 {"id":"v6_coh_gain_label","maxclass":"comment","text":"coherence voice","patching_rect":[1160.,1082.,110.,20.],"presentation":1,"presentation_rect":[1160.,1040.,110.,20.]},
 {"id":"v6_coh_gain_default","maxclass":"newobj","text":"loadmess 0.2","patching_rect":[1080.,1110.,82.,22.],"numinlets":1,"numoutlets":1,"outlettype":[""]},
 {"id":"v6_coh_gain_sig","maxclass":"newobj","text":"sig~ 0.","patching_rect":[1450.,1160.,52.,22.],"numinlets":1,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_coh_gain_mul","maxclass":"newobj","text":"*~","patching_rect":[1510.,1160.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_final_sum","maxclass":"newobj","text":"+~","patching_rect":[760.,1180.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
])
add.extend([
 {"id":"v6_density_line_slice","maxclass":"newobj","text":"zl.slice 2","patching_rect":[1200.,1220.,70.,22.],"numinlets":2,"numoutlets":2,"outlettype":["list","list"]},
 {"id":"v6_density_line_unpack","maxclass":"newobj","text":"unpack "+" ".join(["f"]*18),"patching_rect":[1280.,1220.,500.,22.],"numinlets":1,"numoutlets":18,"outlettype":["float"]*18},
 {"id":"v6_density_line_gain","maxclass":"flonum","minimum":0.0,"maximum":1.0,"patching_rect":[1275.,1080.,75.,22.],"presentation":1,"presentation_rect":[1275.,1038.,75.,22.],"numinlets":1,"numoutlets":2,"outlettype":["","bang"]},
 {"id":"v6_density_line_label","maxclass":"comment","text":"density-H lines","patching_rect":[1355.,1082.,105.,20.],"presentation":1,"presentation_rect":[1355.,1040.,105.,20.]},
 {"id":"v6_density_line_gain_sig","maxclass":"newobj","text":"sig~ 0.","patching_rect":[1450.,1220.,52.,22.],"numinlets":1,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_density_line_sum","maxclass":"newobj","text":"+~","patching_rect":[1510.,1220.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_density_line_gain_mul","maxclass":"newobj","text":"*~","patching_rect":[1560.,1220.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
 {"id":"v6_density_line_final_sum","maxclass":"newobj","text":"+~","patching_rect":[820.,1180.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
])
for i in range(6):
    add.extend([
      {"id":f"v6_z_cycle_{i}","maxclass":"newobj","text":"cycle~","patching_rect":[1200.+i*70,1260.,55.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
      {"id":f"v6_z_amp_{i}","maxclass":"newobj","text":"*~","patching_rect":[1200.+i*70,1290.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]},
      {"id":f"v6_z_phase_{i}","maxclass":"newobj","text":"expr $f1 / 6.283185307","patching_rect":[1200.+i*70,1360.,120.,22.],"numinlets":1,"numoutlets":1,"outlettype":[""]},
      {"id":f"v6_z_phase_sig_{i}","maxclass":"newobj","text":"sig~","patching_rect":[1200.+i*70,1390.,42.,22.],"numinlets":1,"numoutlets":1,"outlettype":["signal"]},
    ])
p["boxes"].extend({"box":b} for b in add)

lines=p["lines"]
def edge(s,d): lines.append({"patchline":{"source":s,"destination":d}})
edge(["oroute",7],["v6_compare",0])
edge(["oroute",11],["v6_density_line_slice",0]); edge(["v6_density_line_slice",1],["v6_density_line_unpack",0])
edge(["v6_compare",1],["v6_local_unpack",0]); edge(["v6_compare",2],["v6_ibm_unpack",0]); edge(["v6_compare",3],["v6_delta_unpack",0])
for row,prefix in (("v6_local_unpack","local"),("v6_ibm_unpack","ibm"),("v6_delta_unpack","delta")):
    for i,label in enumerate(("XI","YI","ZI","IX","IY","IZ","XX","XY","XZ","YX","YY","YZ","ZX","ZY","ZZ")): edge([row,i],[f"v6_{prefix}_{label}",0])
for name in ("local","ibm","difference"): edge(["phasor",0],[f"v6_coh_wave_{name}",0])
for entry in lines:
    line=entry["patchline"]
    if line["source"] == ["comparison_sum",0] and line["destination"][0] in {"ir_convolver","ir_mix_sum"}: line["source"]=["v6_final_sum",0]
    if line["source"] == ["v6_final_sum",0] and line["destination"][0] in {"ir_convolver","ir_mix_sum"}: line["source"]=["v6_density_line_final_sum",0]
for s,d in (
 (["v6_coh_wave_local",0],["v6_coh_local_mul",0]),(["source_xfade_inverse",0],["v6_coh_local_mul",1]),
 (["v6_coh_wave_ibm",0],["v6_coh_ibm_mul",0]),(["source_xfade_line",0],["v6_coh_ibm_mul",1]),
 (["v6_coh_local_mul",0],["v6_coh_source_sum",0]),(["v6_coh_ibm_mul",0],["v6_coh_source_sum",1]),
 (["v6_coh_wave_difference",0],["v6_coh_difference_mul",0]),(["difference_gain_sig",0],["v6_coh_difference_mul",1]),
 (["v6_coh_source_sum",0],["v6_coh_mix_sum",0]),(["v6_coh_difference_mul",0],["v6_coh_mix_sum",1]),
 (["v6_coh_gain_default",0],["v6_coh_gain",0]),(["v6_coh_gain",0],["v6_coh_gain_sig",0]),
 (["v6_coh_mix_sum",0],["v6_coh_gain_mul",0]),(["v6_coh_gain_sig",0],["v6_coh_gain_mul",1]),
 (["comparison_sum",0],["v6_final_sum",0]),(["v6_coh_gain_mul",0],["v6_final_sum",1]),
): edge(s,d)
edge(["v6_density_line_gain",0],["v6_density_line_gain_sig",0])
previous=None
for i in range(6):
    edge(["v6_density_line_unpack",i*3],[f"v6_z_cycle_{i}",0])
    edge(["v6_density_line_unpack",i*3+1],[f"v6_z_amp_{i}",1])
    edge(["v6_density_line_unpack",i*3+2],[f"v6_z_phase_{i}",0]); edge([f"v6_z_phase_{i}",0],[f"v6_z_phase_sig_{i}",0]); edge([f"v6_z_phase_sig_{i}",0],[f"v6_z_cycle_{i}",1])
    edge([f"v6_z_cycle_{i}",0],[f"v6_z_amp_{i}",0])
    if previous is None: previous=f"v6_z_amp_{i}"
    else:
        sid=f"v6_z_sum_{i}"; p["boxes"].append({"box":{"id":sid,"maxclass":"newobj","text":"+~","patching_rect":[1200.+i*55,1330.,42.,22.],"numinlets":2,"numoutlets":1,"outlettype":["signal"]}})
        edge([previous,0],[sid,0]); edge([f"v6_z_amp_{i}",0],[sid,1]); previous=sid
edge([previous,0],["v6_density_line_gain_mul",0]); edge(["v6_density_line_gain_sig",0],["v6_density_line_gain_mul",1])
edge(["v6_final_sum",0],["v6_density_line_final_sum",0]); edge(["v6_density_line_gain_mul",0],["v6_density_line_final_sum",1])

# Ensure the new JS is packaged with the patch.
p.setdefault("dependency_cache",[]).append({"name":"qmw_pauli_coherence_v6.js","bootpath":"~/QuantumSonification/max","patcherrelativepath":".","type":"TEXT","implicit":1})
for dep in p["dependency_cache"]:
    if dep.get("name")=="qmw_compact_state_renderer_v5.js": dep["name"]="qmw_compact_state_renderer_v6.js"
target.write_text(json.dumps(doc,indent="\t")+"\n",encoding="utf-8")
print(f"created {target.name}")
