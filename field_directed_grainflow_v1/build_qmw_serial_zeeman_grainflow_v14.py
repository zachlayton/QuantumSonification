#!/usr/bin/env python3
"""Put the Zeeman oscillator bank inside GrainFlow's source path."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/"QMW_Eigenfield_Spatial_Grainflow_Zeeman_v13.maxpat"
target=ROOT/"QMW_Serial_Zeeman_Eigenfield_Grainflow_v14.maxpat"
doc=json.loads(source.read_text()); p=doc["patcher"]
boxes={e["box"]["id"]:e["box"] for e in p["boxes"]}
boxes["title"]["text"]="QMW SERIAL ZEEMAN → EIGENFIELD GRAINFLOW v14"
boxes["grain"]["text"]="grainflow~ qmw_zeeman_live 8 @delayRandom 500"

def box(id_,cls,rect,**kw):
    d={"id":id_,"maxclass":cls,"patching_rect":rect}; d.update(kw); p["boxes"].append({"box":d})
def line(s,so,d,di=0): p["lines"].append({"patchline":{"source":[s,so],"destination":[d,di]}})

# Remove the old parallel Zeeman-to-DAC path.
p["lines"]=[e for e in p["lines"] if not (
    e["patchline"]["source"][0] in {"zee_gain_l","zee_gain_r"}
    and e["patchline"]["destination"][0]=="dac"
)]

box("zee_live_label","comment",[20.,1100.,700.,20.],text="SERIAL SOURCE: Zeeman bank → mono live buffer → GrainFlow → stereo field")
box("zee_live_buf","newobj",[20.,1125.,255.,22.],text="buffer~ qmw_zeeman_live 4000 1",numinlets=1,numoutlets=2,outlettype=["float","bang"])
box("zee_sum","newobj",[290.,1125.,38.,22.],text="+~",numinlets=2,numoutlets=1,outlettype=["signal"])
box("zee_mono_gain","newobj",[340.,1125.,62.,22.],text="*~ 0.5",numinlets=2,numoutlets=1,outlettype=["signal"])
box("zee_record","newobj",[415.,1125.,205.,22.],text="record~ qmw_zeeman_live @loop 1",numinlets=3,numoutlets=1,outlettype=["signal"])
box("zee_record_on","toggle",[635.,1124.,24.,24.],numinlets=1,numoutlets=1,outlettype=["int"])
box("zee_record_init","newobj",[670.,1125.,75.,22.],text="loadmess 1",numinlets=1,numoutlets=1,outlettype=[""])
box("zee_serial_note","comment",[20.,1160.,800.,38.],text="There is no direct Zeeman output in v14. Field motion changes carrier/splitting; the resulting waveform is heard only after it has entered the granular channel.")
line("zee_gain_l",0,"zee_sum",0); line("zee_gain_r",0,"zee_sum",1)
line("zee_sum",0,"zee_mono_gain"); line("zee_mono_gain",0,"zee_record")
line("zee_record_init",0,"zee_record_on"); line("zee_record_on",0,"zee_record")

target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
