#!/usr/bin/env python3
"""Build the full GrainFlow attribute/message conductor surface."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / "QMW_Conductor_Grainflow_Zeeman_v11.maxpat"
target = ROOT / "QMW_Full_Conductor_Grainflow_Zeeman_v12_1.maxpat"
doc = json.loads(source.read_text())
p = doc["patcher"]
boxes = {entry["box"]["id"]: entry["box"] for entry in p["boxes"]}
boxes["title"]["text"] = "QMW FULL CONDUCTOR GRAINFLOW + ZEEMAN v12"

def box(id_, maxclass, rect, **kwargs):
    payload = {"id": id_, "maxclass": maxclass, "patching_rect": rect}
    payload.update(kwargs); p["boxes"].append({"box": payload})

def line(src, outlet, dst, inlet=0):
    p["lines"].append({"patchline":{"source":[src,outlet],"destination":[dst,inlet]}})

# V12 uses the versioned 28-value frame; stop the 14-value compatibility
# frame from also changing GrainFlow while retaining V11 Zeeman routing.
p["lines"] = [e for e in p["lines"] if not (
    e["patchline"]["source"] == ["conductor_route",0]
    and e["patchline"]["destination"][0] == "grain_frame_gate"
)]

box("full_route","newobj",[20.,870.,285.,22.],text="o.route /qmw/conductor/grainflow/v2",numinlets=1,numoutlets=2,outlettype=["list","FullPacket"])
box("full_gate","newobj",[315.,870.,58.,22.],text="gate 1",numinlets=2,numoutlets=1,outlettype=[""])
box("full_unpack","newobj",[385.,870.,610.,22.],text="unpack "+" ".join(["f"]*28),numinlets=1,numoutlets=28,outlettype=["float"]*28)
box("full_status","message",[20.,900.,600.,22.],text="waiting for /qmw/conductor/grainflow/v2",numinlets=2,numoutlets=1,outlettype=[""])
line("osc",0,"full_route"); line("map_enable",0,"full_gate",0); line("full_route",0,"full_gate",1); line("full_gate",0,"full_unpack"); line("full_gate",0,"full_status")

existing = {
    "state":"obj-34", "density":"obj-43", "amp":"obj-24", "ampRandom":"obj-29",
    "delay":"obj-30", "delayRandom":"obj-31", "transpose":"obj-32",
    "transposeRandom":"obj-33", "space":"obj-40", "spaceRandom":"obj-41",
    "glissonSt":"obj-46", "glissonStRandom":"obj-48",
}
attributes = [
    "state","density","amp","ampOffset","ampRandom","delay","delayOffset","delayRandom",
    "direction","glissonSt","glissonStOffset","glissonStRandom","rate","rateOffset",
    "rateRandom","space","spaceOffset","spaceRandom","transpose","transposeOffset",
    "transposeRandom","window","windowOffset","windowRandom","startPoint","stopPoint",
]
for index, attr in enumerate(attributes):
    destination = existing.get(attr)
    if destination is None:
        destination = "full_attr_" + attr
        column = index // 13; row = index % 13
        box(destination,"attrui",[1000.+column*180.,110.+row*29.,165.,22.],attr=attr,displaymode=2,numinlets=1,numoutlets=1,outlettype=[""])
        line(destination,0,"grain")
    line("full_unpack",index,destination)

# The final two values are deliberately shallow signal-rate modulation and do
# not duplicate the persistent rate/transpose attributes.
line("full_unpack",26,"rate"); line("full_unpack",27,"amp")

# Reserve conductor event messages for addressed grain/stream operations.
box("event_route","newobj",[20.,940.,420.,22.],text="o.route /qmw/conductor/grainflow/event",numinlets=1,numoutlets=2,outlettype=["","FullPacket"])
box("event_gate","newobj",[450.,940.,58.,22.],text="gate 1",numinlets=2,numoutlets=1,outlettype=[""])
box("event_monitor","message",[520.,940.,420.,22.],text="stream / spread / deviate / target events",numinlets=2,numoutlets=1,outlettype=[""])
line("osc",0,"event_route"); line("map_enable",0,"event_gate",0); line("event_route",0,"event_gate",1); line("event_gate",0,"grain"); line("event_gate",0,"event_monitor")

target.write_text(json.dumps(doc,indent=2)+"\n")
print(f"generated {target.name}")
