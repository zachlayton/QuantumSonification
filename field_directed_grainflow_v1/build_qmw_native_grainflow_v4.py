#!/usr/bin/env python3
"""Build a minimal native grainflow~ diagnostic instrument."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
boxes=[]; lines=[]
def b(id,cls,rect,**kw):
    d={"id":id,"maxclass":cls,"patching_rect":rect}; d.update(kw); boxes.append({"box":d})
def l(s,so,d,di=0): lines.append({"patchline":{"source":[s,so],"destination":[d,di]}})
b("title","comment",[20,15,900,28],text="QMW NATIVE GRAINFLOW v9 — RATE + AM SIGNAL CONTROL",fontsize=18.)
b("buf","newobj",[20,60,300,22],text="buffer~ qmw_fdg_source Anton.aif",numinlets=1,numoutlets=2,outlettype=["float","bang"])
b("clock","flonum",[20,110,70,22],minimum=0.1,maximum=100.,numinlets=1,numoutlets=2,outlettype=["","bang"])
b("clock_p","newobj",[100,110,80,22],text="phasor~ 10.",numinlets=2,numoutlets=1,outlettype=["signal"])
b("scan","flonum",[20,145,70,22],minimum=0.,maximum=5.,numinlets=1,numoutlets=2,outlettype=["","bang"])
b("scan_p","newobj",[100,145,80,22],text="phasor~ 0.2",numinlets=2,numoutlets=1,outlettype=["signal"])
b("grain","newobj",[280,125,280,22],text="grainflow~ qmw_fdg_source 8 @delayRandom 500",numinlets=4,numoutlets=9,outlettype=["multichannelsignal","list"]+["multichannelsignal"]*7)
b("rate_label","comment",[20,195,150,20],text="inlet 3: playback rate")
b("rate","flonum",[20,218,72,22],minimum=-4.,maximum=4.,numinlets=1,numoutlets=2,outlettype=["","bang"])
b("rate_sig","newobj",[100,218,62,22],text="sig~ 1.",numinlets=1,numoutlets=1,outlettype=["signal"])
b("rate_init","newobj",[20,247,82,22],text="loadmess 1.",numinlets=1,numoutlets=1,outlettype=[""])
b("amp_label","comment",[180,195,165,20],text="inlet 4: amplitude modulation")
b("amp","flonum",[180,218,72,22],minimum=0.,maximum=2.,numinlets=1,numoutlets=2,outlettype=["","bang"])
b("amp_sig","newobj",[260,218,62,22],text="sig~ 1.",numinlets=1,numoutlets=1,outlettype=["signal"])
b("amp_init","newobj",[180,247,82,22],text="loadmess 1.",numinlets=1,numoutlets=1,outlettype=[""])
b("enable","toggle",[235,285,24,24],numinlets=1,numoutlets=1,outlettype=["int"])
b("enable_l","newobj",[155,285,75,22],text="loadmess 1",numinlets=1,numoutlets=1,outlettype=[""])
b("pan","newobj",[280,330,190,22],text="grainflow.util.stereoPan~",numinlets=2,numoutlets=1,outlettype=["multichannelsignal"])
b("unpack","newobj",[300,365,90,22],text="mc.unpack~ 2",numinlets=1,numoutlets=2,outlettype=["signal","signal"])
b("gain","newobj",[410,365,65,22],text="*~ 0.25",numinlets=2,numoutlets=1,outlettype=["signal"])
b("gainr","newobj",[485,365,65,22],text="*~ 0.25",numinlets=2,numoutlets=1,outlettype=["signal"])
b("dac","ezdac~",[570,350,55,55],numinlets=2,numoutlets=0)
l("clock",0,"clock_p"); l("scan",0,"scan_p"); l("clock_p",0,"grain",0); l("scan_p",0,"grain",1); l("rate_init",0,"rate"); l("rate",0,"rate_sig"); l("rate_sig",0,"grain",2); l("amp_init",0,"amp"); l("amp",0,"amp_sig"); l("amp_sig",0,"grain",3); l("enable_l",0,"enable"); l("enable",0,"grain"); l("grain",0,"pan",0); l("grain",2,"pan",1); l("pan",0,"unpack"); l("unpack",0,"gain"); l("unpack",1,"gainr"); l("gain",0,"dac",0); l("gainr",0,"dac",1)
for id,val in (("clock",10.),("scan",0.2)):
    b(id+"_i","newobj",[700,280 if id=="clock" else 310,90,22],text="loadmess "+str(val),numinlets=1,numoutlets=1,outlettype=[""]); l(id+"_i",0,id)
doc={"patcher":{"fileversion":1,"appversion":{"major":9,"minor":0,"revision":0,"architecture":"x64"},"rect":[0,0,900,500],"boxes":boxes,"lines":lines,"dependency_cache":[{"name":"Anton.aif","type":"AIFF"},{"name":"grainflow~.mxo","type":"iLaX"},{"name":"grainflow.util.stereoPan~.maxpat","type":"JSON"}]}}
(R/"QMW_Native_Grainflow_v9.maxpat").write_text(json.dumps(doc,indent=2)+"\n")
print("generated QMW_Native_Grainflow_v9.maxpat")
