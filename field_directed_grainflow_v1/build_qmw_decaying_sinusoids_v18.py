#!/usr/bin/env python3
"""Build a minimal CNMAT decaying-sinusoids~ Zeeman diagnostic."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
boxes=[]; lines=[]
def b(i,c,r,**kw): d={"id":i,"maxclass":c,"patching_rect":r}; d.update(kw); boxes.append({"box":d})
def l(s,so,d,di=0): lines.append({"patchline":{"source":[s,so],"destination":[d,di]}})
b("title","comment",[20,15,850,28],text="QMW DECAYING ZEEMAN SINUSOIDS v18 — MINIMAL CNMAT TEST",fontsize=18.)
b("note","comment",[20,48,850,38],text="OSC updates the spectral model; RING resets virtual time to zero. No GrainFlow, resonators~, or convolution is present.")
b("udp","newobj",[20,100,120,22],text="udpreceive 7400",numinlets=1,numoutlets=1,outlettype=["FullPacket"])
b("route","newobj",[155,100,500,22],text="o.route /qmw/conductor/eigenfield/grid/4 /qmw/conductor/zeeman",numinlets=1,numoutlets=3,outlettype=["list","list","FullPacket"])
b("js","newobj",[20,140,245,22],text="js qmw_decaying_zeeman_model_v18.js",numinlets=2,numoutlets=2,outlettype=["list",""])
b("status","message",[280,140,490,22],text="waiting for conductor model",numinlets=2,numoutlets=1,outlettype=[""])
b("decay","newobj",[20,230,170,22],text="decaying-sinusoids~",numinlets=1,numoutlets=1,outlettype=["signal"])
b("ring","button",[20,180,24,24],numinlets=1,numoutlets=1,outlettype=["bang"])
b("ring_label","comment",[52,181,70,20],text="RING")
b("goto","message",[125,180,52,22],text="goto 0.",numinlets=2,numoutlets=1,outlettype=[""])
b("test","message",[205,180,390,22],text="220. 0.22 2.5 330. 0.16 3.2 440. 0.1 4.",numinlets=2,numoutlets=1,outlettype=[""])
b("test_label","comment",[605,181,180,20],text="manual three-mode model")
b("gain","newobj",[20,270,62,22],text="*~ 0.3",numinlets=2,numoutlets=1,outlettype=["signal"])
b("dac","ezdac~",[110,255,55,55],numinlets=2,numoutlets=0)
l("udp",0,"route"); l("route",0,"js",0); l("route",1,"js",1); l("js",0,"decay"); l("js",1,"status")
l("ring",0,"goto"); l("goto",0,"decay"); l("test",0,"decay"); l("decay",0,"gain"); l("gain",0,"dac",0); l("gain",0,"dac",1)
doc={"patcher":{"fileversion":1,"appversion":{"major":9,"minor":0,"revision":5,"architecture":"x64"},"rect":[0,0,900,360],"boxes":boxes,"lines":lines,"dependency_cache":[{"name":"qmw_decaying_zeeman_model_v18.js","bootpath":"~/QuantumSonification/field_directed_grainflow_v1","type":"TEXT"},{"name":"decaying-sinusoids~.mxo","type":"iLaX"},{"name":"o.route.mxo","type":"iLaX"}]}}
(R/"QMW_Decaying_Zeeman_Sinusoids_v18.maxpat").write_text(json.dumps(doc,indent=2)+"\n")
print("generated QMW_Decaying_Zeeman_Sinusoids_v18.maxpat")
