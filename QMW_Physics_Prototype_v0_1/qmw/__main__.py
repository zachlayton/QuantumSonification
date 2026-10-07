from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import time
from qmw.runtime import PhysicsEngine
from qmw.core.serialization import jsonable


def main():
    parser=argparse.ArgumentParser(description="QMW inspectable physics prototype")
    sub=parser.add_subparsers(dest="command",required=True)
    string_demo=sub.add_parser("string-demo",help="Render physical stiff-string listening comparisons and flux-driven string")
    string_demo.add_argument("--output",type=Path,default=Path("output/stiff_string"))
    string_demo.add_argument("--sample-rate",type=int,default=48000)
    for name in ("serve","demo"):
        command=sub.add_parser(name)
        command.add_argument("--model",choices=["schrodinger","lindblad","scalar"],default="schrodinger")
        command.add_argument("--points",type=int,default=2048)
        command.add_argument("--length",type=float,default=64)
        command.add_argument("--dt",type=float,default=.002)
        command.add_argument("--control",action="append",default=[],metavar="NAME=VALUE",help="Override a model or musical control; strings accepted for init")
    serve=sub.choices["serve"]
    serve.add_argument("--port",type=int,default=8765)
    serve.add_argument("--tick-rate",type=float,default=50)
    serve.add_argument("--steps-per-tick",type=int,default=10)
    serve.add_argument("--osc-port",type=int,default=17900)
    serve.add_argument("--no-osc",action="store_true")
    serve.add_argument("--open",action="store_true",help="Open the local inspector in your default browser")
    demo=sub.choices["demo"]
    demo.add_argument("--duration",type=float,default=16,help="Simulation seconds, also used as preview audio seconds")
    demo.add_argument("--output",type=Path,default=Path("output"))
    demo.add_argument("--record-every",type=int,default=25)
    demo.add_argument("--sample-rate",type=int,default=48000)
    demo.add_argument("--renderer",choices=["stiff-string","legacy-harmonic"],default="stiff-string")
    demo.add_argument("--string-param",action="append",default=[],metavar="NAME=NUMBER")
    args=parser.parse_args()
    if args.command=="string-demo":
        from qmw.sound.string_demo import build_examples
        build_examples(args.output,args.sample_rate)
        return
    updates={"dt":args.dt}
    for entry in args.control:
        if "=" not in entry:parser.error("Controls must be NAME=VALUE")
        name,value=entry.split("=",1)
        try:updates[name]=json.loads(value)
        except json.JSONDecodeError:updates[name]=value
    try:engine=PhysicsEngine(args.model,args.points,args.length,updates)
    except (ValueError,TypeError) as exc:parser.error(str(exc))
    if args.command=="serve":
        from qmw.ui.server import serve as run_server
        from qmw.io.osc import OscPublisher
        publisher=None if args.no_osc else OscPublisher(port=args.osc_port)
        run_server(engine,args.port,args.tick_rate,args.steps_per_tick,publisher,args.open)
        return
    import math
    if not math.isfinite(args.duration) or args.duration<=0 or args.record_every<=0:
        parser.error("Duration and record-every must be positive")
    from qmw.sound.render import render,write_wav
    args.output.mkdir(parents=True,exist_ok=True)
    events=[];physics_events=[];start=time.perf_counter()
    steps=math.ceil(args.duration/args.dt)
    history=args.output/"history.jsonl.gz"
    final=None
    def exported_snapshot(include_state=False):
        record=engine.snapshot(include_state=include_state)
        if args.renderer=="stiff-string":
            record["legacy_sound"]=record.pop("sound")
            record["legacy_event_history"]=record.pop("event_history")
            record["acoustic_renderer"]="stiff-string; see acoustic_model.json; legacy harmonic mapping is not used"
        return record
    with gzip.open(history,"wt",encoding="utf-8",compresslevel=4) as out:
        out.write(json.dumps(exported_snapshot(),allow_nan=False)+"\n")
        for step in range(steps):
            frame,sound=engine.step()
            events.extend(sound.events)
            physics_events.extend(frame.events)
            if (step+1)%args.record_every==0 or step==steps-1:
                out.write(json.dumps(exported_snapshot(),allow_nan=False)+"\n")
    elapsed=time.perf_counter()-start
    final=exported_snapshot(include_state=True)
    (args.output/"final_frame.json").write_text(json.dumps(final,indent=2,allow_nan=False))
    (args.output/("legacy_sound_events.json" if args.renderer=="stiff-string" else "events.json")).write_text(json.dumps(jsonable(events),indent=2,allow_nan=False))
    (args.output/"physics_events.json").write_text(json.dumps(jsonable(physics_events),indent=2,allow_nan=False))
    acoustic={"renderer":args.renderer}
    if args.renderer=="stiff-string":
        from dataclasses import asdict
        from qmw.sound.stiff_string import StringParameters,render_force_events,force_events_from_physics
        parameters={}
        for entry in args.string_param:
            if "=" not in entry:parser.error("String parameters must be NAME=NUMBER")
            key,value=entry.split("=",1)
            parameters[key]=int(value) if key=="modes" else float(value)
        string_parameters=StringParameters(**parameters)
        force_events=force_events_from_physics(physics_events)
        preview,string_model=render_force_events(force_events,args.duration+8,string_parameters,args.sample_rate)
        # A declared pickup output gain, with common whole-file headroom reduction if needed.
        output_gain=min(1.0,.9/max(float(abs(preview).max()),1e-30));preview*=output_gain
        acoustic.update({"parameters":asdict(string_parameters),"fundamental_hz":float(string_model.frequency_hz[0]),
            "pickup_output_gain_per_m_s":output_gain,"force_events":[asdict(e) for e in force_events],
            "note":"No region-to-pitch assignment. One persistent string; scaled flux maps to force impulse."})
        (args.output/"acoustic_model.json").write_text(json.dumps(acoustic,indent=2,allow_nan=False))
    else:
        preview=render(events,args.duration+8*engine.controls["decay_s"],args.sample_rate)
    write_wav(args.output/"preview.wav",preview,args.sample_rate)
    summary={"model":engine.frame.model_id,"points":engine.model.domain.size,"steps":steps,
        "simulation_seconds":engine.t,"wall_seconds":elapsed,
        "legacy_synth_events":len(events),
        "physical_force_events":len(acoustic.get("force_events",[])),
        "record_every_steps":args.record_every,
        "diagnostics":jsonable(engine.frame.diagnostics),"controls":engine.controls,
        "acoustic_renderer":acoustic,
        "audio_note":"One simulation second maps to one audio second. Stiff-string frequencies/losses derive from mechanical parameters; legacy synth pitch/decay values are unused by that renderer."}
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False))
    print(json.dumps(summary,indent=2,allow_nan=False))


if __name__=="__main__":main()
