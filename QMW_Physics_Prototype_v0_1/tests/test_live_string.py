import json
import threading
import unittest
from urllib.request import urlopen
from qmw.runtime import PhysicsEngine
from qmw.ui.server import make_server


class LiveStringTests(unittest.TestCase):
    def test_independent_engine_runs_have_distinct_event_namespaces(self):
        first=PhysicsEngine(n=128);second=PhysicsEngine(n=128)
        self.assertNotEqual(first.run_id,second.run_id)
        original=first.run_id;first.reset()
        self.assertEqual(first.run_id,original)

    def test_force_history_contains_source_impulse_without_pitch(self):
        engine=PhysicsEngine(n=128)
        engine.step(4000)
        history=engine.snapshot()['force_history']
        self.assertTrue(history)
        self.assertTrue(all(e['impulse_ns']>0 and 0<e['position']<1 for e in history))
        self.assertEqual(len({e['event_id'] for e in history}),len(history))
        self.assertTrue(all('frequency_hz' not in e for e in history))
        engine.reset()
        self.assertEqual(engine.snapshot()['force_history'],[])

    def test_sample_rate_specific_coefficients_and_worklet_route(self):
        server=make_server(PhysicsEngine(n=128),port=0)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            root=f'http://127.0.0.1:{server.server_port}'
            with urlopen(root+'/api/string?sample_rate=44100') as response:
                data=json.load(response)
            from qmw.sound.stiff_string import StiffString
            model=StiffString(sample_rate=44100)
            self.assertEqual(data['a11'],model.a11.tolist())
            with urlopen(root+'/string-worklet.js') as response:
                self.assertIn(b"registerProcessor('physical-string'",response.read())
        finally:
            server.shutdown();server.server_close();worker.join()
