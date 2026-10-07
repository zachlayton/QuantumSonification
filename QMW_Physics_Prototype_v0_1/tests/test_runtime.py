import json
import threading
import unittest
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from qmw.runtime import PhysicsEngine


class RuntimeIntegration(unittest.TestCase):
    def test_constructor_initial_controls_are_applied(self):
        import numpy as np
        engine=PhysicsEngine(n=128,controls={"packet_center":4.0,"packet_width":1.5,"packet_momentum":.4})
        mean=float(engine.model.domain.integrate(engine.model.domain.coordinates*abs(engine.state.psi)**2))
        self.assertAlmostEqual(mean,4.0,6)
        self.assertEqual(engine.cumulative_work,0)
        scalar=PhysicsEngine("scalar",controls={"init":"qball"})
        self.assertIn("qball",str(scalar.model.initialization_metadata).lower().replace("-",""))

    def test_quench_work_and_monotonic_reset(self):
        engine=PhysicsEngine(n=128)
        engine.step(5)
        old_energy=engine.frame.observables.total_energy
        engine.set_controls({"mass":1.0})
        self.assertAlmostEqual(engine.cumulative_work,engine.frame.observables.total_energy-old_energy,12)
        self.assertLess(engine.frame.diagnostics.energy_drift,1e-11)
        seq=engine.sequence;engine.reset()
        self.assertGreater(engine.sequence,seq)
        self.assertEqual(engine.t,0)

    def test_snapshot_is_read_only_and_invalid_update_is_atomic(self):
        engine=PhysicsEngine(n=128)
        snap=engine.snapshot();engine.snapshot();engine.snapshot()
        self.assertEqual(engine.sequence,snap["physics"]["sequence"])
        controls=dict(engine.controls)
        with self.assertRaises(ValueError):engine.set_controls({"mass":-1})
        self.assertEqual(engine.controls,controls)
        json.dumps(engine.snapshot(include_state=True),allow_nan=False)

    def test_local_http_control_and_readonly_get(self):
        from qmw.ui.server import make_server
        engine=PhysicsEngine(n=128)
        server=make_server(engine,port=0)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        url=f"http://127.0.0.1:{server.server_port}"
        try:
            with urlopen(url+"/api/state") as response:state=json.load(response)
            self.assertEqual(state["physics"]["sequence"],engine.sequence)
            req=Request(url+"/api/control",data=b'{"mass":0.7}',headers={"Content-Type":"application/json"})
            with urlopen(req) as response:self.assertTrue(json.load(response)["ok"])
            self.assertEqual(engine.controls["mass"],.7)
            with self.assertRaises(HTTPError):urlopen(Request(url+"/api/control",data=b'{"unknown":1}'))
            with urlopen(url+"/api/specs") as response:self.assertTrue(json.load(response)["modules"])
        finally:
            server.shutdown();server.server_close();worker.join(timeout=2)
