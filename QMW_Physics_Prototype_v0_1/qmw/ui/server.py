"""Local inspectable GUI server: state access never advances the model."""
from __future__ import annotations
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import threading
import time
from urllib.parse import urlparse, parse_qs
from qmw.runtime import PhysicsEngine
from qmw.core.serialization import jsonable


def specs_payload(engine):
    from qmw.ui.metadata import module_specs
    from qmw.observables import module_specs as observable_specs
    from qmw.conservation import module_specs as conservation_specs
    from qmw.projection import MODULE_SPECS
    specs=list(module_specs())+list(observable_specs())+list(conservation_specs())+list(MODULE_SPECS)
    if hasattr(engine.model,"module_specs"):specs+=list(engine.model.module_specs())
    distinct={spec.id:spec.to_dict() for spec in specs}
    return {"modules":list(distinct.values()),"model":engine.model_kind,
        "controls":dict(engine.controls),"schema_version":engine.frame.schema_version}


def make_server(engine:PhysicsEngine,host="127.0.0.1",port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass

        def _send(self,data,status=200,content_type="application/json; charset=utf-8"):
            payload=data if isinstance(data,bytes) else json.dumps(jsonable(data),allow_nan=False).encode()
            self.send_response(status);self.send_header("Content-Type",content_type)
            self.send_header("Content-Length",str(len(payload)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers();self.wfile.write(payload)

        def do_GET(self):
            path=urlparse(self.path).path
            try:
                if path in ("/","/index.html"):
                    return self._send(Path(__file__).with_name("index.html").read_bytes(),content_type="text/html; charset=utf-8")
                if path=="/harmonics":
                    return self._send(Path(__file__).with_name("harmonics.html").read_bytes(),content_type="text/html; charset=utf-8")
                if path=="/harmonic-worklet.js":
                    return self._send(Path(__file__).with_name("harmonic-worklet.js").read_bytes(),content_type="application/javascript")
                if path=="/api/state":return self._send(engine.snapshot())
                if path=="/string-worklet.js":
                    return self._send(Path(__file__).with_name("string-worklet.js").read_bytes(),content_type="application/javascript")
                if path=="/api/string":
                    from qmw.sound.stiff_string import StiffString
                    rate=int(parse_qs(urlparse(self.path).query).get('sample_rate',['48000'])[0])
                    if not 8000<=rate<=192000:raise ValueError("Sample rate must be in 8000..192000")
                    string=StiffString(sample_rate=rate)
                    coefficients={name:jsonable(getattr(string,name)) for name in ('k','a11','a12','a21','a22','bq','bv','frequency_hz','modal_mass')}
                    coefficients['length_m']=string.parameters.length_m
                    return self._send(coefficients)
                if path=="/api/specs":
                    with engine.lock:return self._send(specs_payload(engine))
                return self._send({"error":"Not found"},404)
            except (ValueError,TypeError) as exc:return self._send({"error":str(exc)},400)

        def do_POST(self):
            try:
                origin=self.headers.get("Origin")
                if origin and origin not in (f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}"):
                    return self._send({"error":"Only this local inspector may change controls"},403)
                length=int(self.headers.get("Content-Length",0))
                if not 0<=length<=65536:raise ValueError("Request is too large")
                data=json.loads(self.rfile.read(length) or b"{}")
                path=urlparse(self.path).path
                if path=="/api/control":engine.set_controls(data)
                elif path=="/api/reset":engine.reset()
                elif path=="/api/step":engine.step()
                else:return self._send({"error":"Not found"},404)
                return self._send({"ok":True,"sequence":engine.frame.sequence,"controls":dict(engine.controls)})
            except (ValueError,TypeError,KeyError) as exc:return self._send({"error":str(exc)},400)
    return ThreadingHTTPServer((host,port),Handler)


def serve(engine,port=8765,tick_rate=50.0,steps_per_tick=10,osc_publisher=None,open_browser=False):
    if tick_rate<=0 or not 1<=steps_per_tick<=10000:raise ValueError("Invalid publication timing")
    server=make_server(engine,port=port)
    stop=threading.Event()

    def loop():
        while not stop.is_set():
            start=time.monotonic()
            try:
                if engine.controls["running"]:
                    frame,sound=engine.step(steps_per_tick)
                    if osc_publisher:osc_publisher.publish(sound,frame)
            except Exception as exc:
                with engine.lock:
                    engine.controls["running"]=False
                    engine.frame.diagnostics.notes.append(f"Evolution paused: {type(exc).__name__}: {exc}")
                print(f"Evolution paused: {exc}",flush=True)
            stop.wait(max(0.0,1/tick_rate-(time.monotonic()-start)))

    worker=threading.Thread(target=loop,name="qmw-physics",daemon=True);worker.start()
    url=f"http://127.0.0.1:{server.server_port}"
    print(f"QMW {engine.model_kind} inspector: {url}",flush=True)
    print(f"Simulation dt={engine.controls['dt']} × {steps_per_tick} substeps per publication; target {tick_rate:g} publications/wall second.",flush=True)
    if open_browser:
        import webbrowser
        webbrowser.open(url)
    try:server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:pass
    finally:
        stop.set();worker.join(timeout=5);server.server_close()
        if osc_publisher:osc_publisher.close()
