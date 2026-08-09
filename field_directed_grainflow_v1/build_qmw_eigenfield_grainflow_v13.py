#!/usr/bin/env python3
"""Add an eight-sector eigenfield-density monitor to V12.1."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_Full_Conductor_Grainflow_Zeeman_v12_1.maxpat"
target=ROOT/"QMW_Eigenfield_Spatial_Grainflow_Zeeman_v13.maxpat"
doc=json.loads(source.read_text()); p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW EIGENFIELD-SPATIAL GRAINFLOW + ZEEMAN v13"

def box(id_,cls,rect,**kw):
    d={"id":id_,"maxclass":cls,"patching_rect":rect}; d.update(kw); p["boxes"].append({"box":d})
def line(s,so,d,di=0): p["lines"].append({"patchline":{"source":[s,so],"destination":[d,di]}})

box("shape_label","comment",[20.,985.,620.,20.],text="EIGENFIELD PARTICLE DENSITY — 8 SPATIAL GRAINFLOW STREAMS")
box("shape_js","newobj",[20.,1010.,260.,22.],text="js qmw_eigenfield_density_display_v13.js",numinlets=1,numoutlets=1,outlettype=["list"])
box("shape_view","multislider",[295.,985.,520.,100.],setminmax=[0.,1.],size=8,sliderstyle=1,orientation=0,numinlets=1,numoutlets=2,outlettype=["","list"])
box("shape_note","comment",[20.,1042.,260.,42.],text="Each lane is one x-sector. Height follows local particle occupancy + eigenfield magnitude; empty sectors stop producing grains.")
line("event_gate",0,"shape_js"); line("shape_js",0,"shape_view")
p.setdefault("dependency_cache",[]).append({"name":"qmw_eigenfield_density_display_v13.js","bootpath":"~/QuantumSonification/field_directed_grainflow_v1","type":"TEXT"})
target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
