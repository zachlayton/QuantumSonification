#!/usr/bin/env python3
"""Upgrade V15's bandpass bank to a genuinely ringing reson~ bank."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_Max_Serial_Zeeman_Grainflow_v15.maxpat"
target=ROOT/"QMW_Ringing_Zeeman_Grainflow_v16.maxpat"
doc=json.loads(source.read_text()); p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW RINGING ZEEMAN RESONATOR + EIGENFIELD GRAINFLOW v16"

filter_ids=[]
for side in ("l","r"):
    for index in range(3):
        fid=f"zr_{side}_bp_{index}"
        boxes[fid]["text"]="reson~ 10. 110. 180."
        boxes[fid]["numinlets"]=4
        filter_ids.append(fid)

# bp~ frequency was inlet 1. reson~ uses gain, center, resonance after audio,
# so retarget generated frequency patchcords to center-frequency inlet 2.
for entry in p["lines"]:
    pl=entry["patchline"]
    if pl["destination"][0] in filter_ids and pl["source"][0].startswith("zr_") and "freq" in pl["source"][0]:
        pl["destination"][1]=2

def box(id_,cls,rect,**kw):
    d={"id":id_,"maxclass":cls,"patching_rect":rect}; d.update(kw); p["boxes"].append({"box":d})
def line(s,so,d,di=0): p["lines"].append({"patchline":{"source":[s,so],"destination":[d,di]}})

box("ring_label","comment",[900.,1100.,245.,20.],text="RESONANCE / RING TIME")
box("ring_value","flonum",[900.,1125.,78.,22.],minimum=1.,maximum=1000.,numinlets=1,numoutlets=2,outlettype=["","bang"])
box("ring_init","newobj",[990.,1125.,105.,22.],text="loadmess 180.",numinlets=1,numoutlets=1,outlettype=[""])
box("ring_note","comment",[900.,1160.,300.,54.],text="Higher values produce longer, narrower ringing. Start near 180; try 300–500 for sparse eigenfields.")
line("ring_init",0,"ring_value")
for fid in filter_ids: line("ring_value",0,fid,3)

# Lower the summed bank slightly because six high-Q resonators can accumulate.
boxes["zr_l_out"]["text"]="*~ 0.18"
boxes["zr_r_out"]["text"]="*~ 0.18"
target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
