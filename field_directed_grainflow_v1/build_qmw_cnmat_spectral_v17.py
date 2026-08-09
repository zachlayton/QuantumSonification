#!/usr/bin/env python3
"""Add CNMAT resonators~/sinusoids~ A/B spectral modeling to V16."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_Ringing_Zeeman_Grainflow_v16.maxpat"
target=ROOT/"QMW_CNMAT_Zeeman_Spectral_Grainflow_v17.maxpat"
doc=json.loads(source.read_text()); p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW CNMAT ZEEMAN SPECTRAL GRAINFLOW v17 — A/B"

def box(id_,cls,rect,**kw):
    d={"id":id_,"maxclass":cls,"patching_rect":rect}; d.update(kw); p["boxes"].append({"box":d})
def line(s,so,d,di=0): p["lines"].append({"patchline":{"source":[s,so],"destination":[d,di]}})

# Remove V16 direct output; it becomes side A of the comparison.
p["lines"]=[e for e in p["lines"] if not (
    e["patchline"]["source"][0] in {"zr_l_out","zr_r_out"}
    and e["patchline"]["destination"][0]=="dac"
)]

box("cn_label","comment",[20.,1400.,900.,20.],text="CNMAT MODEL: eigenfield cells → paired Zeeman frequency/gain/decay triples")
box("cn_route","newobj",[20.,1425.,760.,22.],text="o.route /qmw/conductor/eigenfield/grid/4 /qmw/conductor/zeeman /qmw/density_field/coherence /qmw/density_field/entropy",numinlets=1,numoutlets=5,outlettype=["list","list","float","float","FullPacket"])
box("cn_js","newobj",[20.,1460.,250.,22.],text="js qmw_cnmat_zeeman_model_v17.js",numinlets=4,numoutlets=3,outlettype=["list","list",""])
box("cn_status","message",[285.,1460.,370.,22.],text="waiting for CNMAT spectral model",numinlets=2,numoutlets=1,outlettype=[""])
box("cn_res_l","newobj",[20.,1500.,135.,22.],text="resonators~ smooth",numinlets=1,numoutlets=2,outlettype=["signal","list"])
box("cn_res_r","newobj",[170.,1500.,135.,22.],text="resonators~ smooth",numinlets=1,numoutlets=2,outlettype=["signal","list"])
box("cn_sines","newobj",[320.,1500.,115.,22.],text="sinusoids~ bwe",numinlets=1,numoutlets=1,outlettype=["signal"])
box("cn_sine_level","flonum",[450.,1500.,70.,22.],minimum=0.,maximum=.3,numinlets=1,numoutlets=2,outlettype=["","bang"])
box("cn_sine_init","newobj",[530.,1500.,85.,22.],text="loadmess 0.",numinlets=1,numoutlets=1,outlettype=[""])
box("cn_sine_gain","newobj",[625.,1500.,45.,22.],text="*~ 0.",numinlets=2,numoutlets=1,outlettype=["signal"])
line("osc",0,"cn_route")
for i in range(4): line("cn_route",i,"cn_js",i)
line("cn_js",0,"cn_res_l"); line("cn_js",0,"cn_res_r"); line("cn_js",1,"cn_sines"); line("cn_js",2,"cn_status")
line("gain",0,"cn_res_l"); line("gainr",0,"cn_res_r")
line("cn_sine_init",0,"cn_sine_level"); line("cn_sine_level",0,"cn_sine_gain",1); line("cn_sines",0,"cn_sine_gain")

# Constant-power-ish A/B control: 0=V16 reson~, 1=CNMAT resonators~.
box("ab_label","comment",[20.,1545.,240.,20.],text="RESONATOR A/B: 0=V16, 1=CNMAT")
box("ab","flonum",[265.,1545.,70.,22.],minimum=0.,maximum=1.,numinlets=1,numoutlets=2,outlettype=["","bang"])
box("ab_init","newobj",[345.,1545.,85.,22.],text="loadmess 1.",numinlets=1,numoutlets=1,outlettype=[""])
box("ab_inv","newobj",[440.,1545.,52.,22.],text="!- 1.",numinlets=2,numoutlets=1,outlettype=[""])
line("ab_init",0,"ab"); line("ab",0,"ab_inv")
for side,old,new,y,dacin in (("l","zr_l_out","cn_res_l",1580.,0),("r","zr_r_out","cn_res_r",1615.,1)):
    box(f"ab_old_{side}","newobj",[20.,y,48.,22.],text="*~",numinlets=2,numoutlets=1,outlettype=["signal"])
    box(f"ab_new_{side}","newobj",[80.,y,48.,22.],text="*~",numinlets=2,numoutlets=1,outlettype=["signal"])
    box(f"ab_sum_{side}","newobj",[140.,y,38.,22.],text="+~",numinlets=2,numoutlets=1,outlettype=["signal"])
    box(f"ab_plus_{side}","newobj",[190.,y,38.,22.],text="+~",numinlets=2,numoutlets=1,outlettype=["signal"])
    line(old,0,f"ab_old_{side}"); line("ab_inv",0,f"ab_old_{side}",1)
    line(new,0,f"ab_new_{side}"); line("ab",0,f"ab_new_{side}",1)
    line(f"ab_old_{side}",0,f"ab_sum_{side}"); line(f"ab_new_{side}",0,f"ab_sum_{side}",1)
    line(f"ab_sum_{side}",0,f"ab_plus_{side}"); line("cn_sine_gain",0,f"ab_plus_{side}",1)
    line(f"ab_plus_{side}",0,"dac",dacin)

deps=p.setdefault("dependency_cache",[])
deps.extend([{"name":"qmw_cnmat_zeeman_model_v17.js","bootpath":"~/QuantumSonification/field_directed_grainflow_v1","type":"TEXT"},{"name":"resonators~.mxo","type":"iLaX"},{"name":"sinusoids~.mxo","type":"iLaX"}])
target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
