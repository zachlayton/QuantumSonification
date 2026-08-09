#!/usr/bin/env python3
"""Max comparison: rich GrainFlow source into a serial Zeeman filter bank."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_Eigenfield_Spatial_Grainflow_Zeeman_v13.maxpat"
target=ROOT/"QMW_Max_Serial_Zeeman_Grainflow_v15.maxpat"
doc=json.loads(source.read_text()); p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW MAX: RICH GRAINS → SERIAL ZEEMAN RESONATORS v15"

def box(id_,cls,rect,**kw):
    d={"id":id_,"maxclass":cls,"patching_rect":rect}; d.update(kw); p["boxes"].append({"box":d})
def line(s,so,d,di=0): p["lines"].append({"patchline":{"source":[s,so],"destination":[d,di]}})

# Remove the parallel oscillator bank and the direct GrainFlow-to-DAC edges.
remove_boxes={"zee_poly","zee_gain_l","zee_gain_r"}
p["boxes"]=[e for e in p["boxes"] if e["box"]["id"] not in remove_boxes]
p["lines"]=[e for e in p["lines"] if not (
    e["patchline"]["source"][0] in remove_boxes
    or e["patchline"]["destination"][0] in remove_boxes
    or (e["patchline"]["source"][0] in {"gain","gainr"} and e["patchline"]["destination"][0]=="dac")
)]

box("serial_label","comment",[20.,1100.,800.,20.],text="SERIAL AUDIO: Anton.aif → eigenfield GrainFlow → Zeeman-split bandpass resonators → DAC")
# Three transition pairs: D2-like factors 1/3, 1, 5/3. Each expression
# receives carrier, field and audible spread from the conductor frame.
factors=[0.333333,1.0,1.666667]
left_filters=[]; right_filters=[]
for index,factor in enumerate(factors):
    x=20.+index*285.
    for side,sign,y in (("l",-1,1130.),("r",1,1195.)):
        expr=f"expr max(30.\\, $f1 + ({sign*factor})*$f2*$f3)"
        eid=f"zr_{side}_freq_{index}"; fid=f"zr_{side}_bp_{index}"
        box(eid,"newobj",[x,y,225.,22.],text=expr,numinlets=3,numoutlets=1,outlettype=["float"])
        box(fid,"newobj",[x,y+30,105.,22.],text="bp~ 110. 18.",numinlets=3,numoutlets=1,outlettype=["signal"])
        line("zee_unpack",1,eid,0); line("zee_unpack",0,eid,1); line("zee_unpack",2,eid,2)
        line(eid,0,fid,1)
        line("gain" if side=="l" else "gainr",0,fid,0)
        (left_filters if side=="l" else right_filters).append(fid)

def sum_chain(prefix, filters, y):
    previous=filters[0]
    for i,source_id in enumerate(filters[1:]):
        sid=f"{prefix}_sum_{i}"; box(sid,"newobj",[600.+i*55.,y,38.,22.],text="+~",numinlets=2,numoutlets=1,outlettype=["signal"])
        line(previous,0,sid,0); line(source_id,0,sid,1); previous=sid
    gid=f"{prefix}_out"; box(gid,"newobj",[720.,y,62.,22.],text="*~ 0.45",numinlets=2,numoutlets=1,outlettype=["signal"])
    line(previous,0,gid); return gid

left=sum_chain("zr_l",left_filters,1265.)
right=sum_chain("zr_r",right_filters,1300.)
line(left,0,"dac",0); line(right,0,"dac",1)
box("serial_note","comment",[20.,1340.,850.,38.],text="The Zeeman section contains no oscillators in v15. It tunes paired resonant filters around the conductor carrier; only granular source audio excites them.")

target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
