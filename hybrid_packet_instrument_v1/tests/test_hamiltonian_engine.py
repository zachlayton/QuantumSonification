"""Run: python -m unittest discover -s hybrid_packet_instrument_v1/tests -v"""
import importlib.util
from pathlib import Path
import struct
import sys
import unittest
import numpy as np

MODULE = Path(__file__).resolve().parents[1] / 'python' / 'hamiltonian_engine.py'
spec = importlib.util.spec_from_file_location('hybrid_hamiltonian', MODULE)
engine_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine_module
spec.loader.exec_module(engine_module)
Engine = engine_module.HamiltonianEngine
Parameters = engine_module.Parameters


class EvolutionTests(unittest.TestCase):
    def test_conservation_both_potentials(self):
        for potential in (0, 1):
            engine = Engine(64, Parameters(potential=potential))
            initial = engine.diagnostics()
            for _ in range(80):
                engine.advance(.007)
            final = engine.diagnostics()
            self.assertAlmostEqual(final['norm'], 1, places=11)
            self.assertAlmostEqual(final['energy'], initial['energy'], places=9)
            self.assertAlmostEqual(final['energy'], final['kinetic']+final['potential'], places=12)

    def test_momentum_moves_packet(self):
        engine = Engine(128, Parameters(potential=0, center=0, width=.12, momentum=3))
        before = engine.diagnostics()['mean_x']
        engine.advance(.02)
        moved = engine.diagnostics()['mean_x']-before
        self.assertGreater(moved, .05)
        self.assertLess(moved, .07)

    def test_projection_normalization_and_phase(self):
        engine = Engine(64)
        initial = engine.overlaps()
        self.assertLessEqual(np.sum(abs(initial)**2), 1+1e-12)
        engine.control('/qmw/hybrid/physics/phase', [np.pi/2])
        np.testing.assert_allclose(engine.overlaps(), 1j*initial, atol=1e-12)
        engine.control('/qmw/hybrid/physics/center', [.4])
        self.assertGreater(np.linalg.norm(engine.overlaps()-1j*initial), .1)

    def test_rate_does_not_reset(self):
        engine = Engine(32)
        engine.advance(.1)
        state = engine.psi.copy()
        engine.control('/qmw/hybrid/physics/rate', [.5])
        np.testing.assert_array_equal(engine.psi, state)
        self.assertEqual(engine.model_time, .1)
        engine.control('/qmw/hybrid/reset', [])
        self.assertEqual(engine.model_time, 0)

    def test_invalid_controls(self):
        engine = Engine(32)
        for key, values in [('width', [0]), ('momentum', [float('nan')]),
                            ('potential', [.5]), ('temperature', [1]), ('center', [])]:
            with self.assertRaises(ValueError):
                engine.control('/qmw/hybrid/physics/'+key, values)


class OSCTests(unittest.TestCase):
    def test_projection_wire_contract(self):
        frame = Engine(32).frame(42)
        raw = engine_module.encode_osc('/qmw/hybrid/projection', frame)
        address, values = engine_module.decode_osc(raw)
        self.assertEqual(address, '/qmw/hybrid/projection')
        self.assertEqual(len(values), 38)
        self.assertEqual(values[0], 42)
        np.testing.assert_allclose(values, frame, rtol=1e-6, atol=1e-7)

    def test_malformed_messages_rejected(self):
        valid = engine_module.encode_osc('/qmw/hybrid/physics/rate', [.1])
        for packet in [b'', b'#bundle\0', valid[:-1], valid+b'\0',
                       valid[:-4]+struct.pack('>f', float('nan'))]:
            with self.assertRaises((ValueError, UnicodeError)):
                engine_module.decode_osc(packet)


if __name__ == '__main__':
    unittest.main()
