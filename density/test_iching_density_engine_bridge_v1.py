import unittest

import numpy as np

import iching_density_engine_bridge_v1 as live
import qmw_iching_density_laplacian_bridge_v1 as source


class FakeBohm:
    configuration_revision = 0
    def reset(self, rho, logical_time=0.0):
        self.last_reset = np.array(rho); self.configuration_revision += 1


class FakeControlBridge:
    def __init__(self): self.handlers = {}
    def add_control_handler(self, route, handler): self.handlers[route] = handler


class FakeEngine:
    def __init__(self):
        self.rho = np.eye(16, dtype=complex) / 16
        self.state_revision = 4; self.logical_time = 0.0
        self.last_event_id = 0; self.last_event_type = "test"
        self.configuration_revision = 0; self.bohm = FakeBohm()
        self.qmw_bridge = FakeControlBridge(); self.persisted = []
        self.hamiltonians_seen = []
    def hamiltonian(self): return np.zeros((16, 16), complex)
    def step(self, dt):
        self.hamiltonians_seen.append(self.hamiltonian().copy())
        self.logical_time += dt
        return self.rho
    def _persist_transition(self, **kwargs): self.persisted.append(kwargs)


def feed(assembler, messages, include_end=True):
    dispatch = {
        "/begin": assembler.begin, "/reading": assembler.reading,
        "/metrics": assembler.metrics, "/primary_phase": assembler.primary_phase,
        "/pauli": assembler.pauli, "/line_phase": assembler.line_phase,
        "/edge": assembler.edge, "/flux": assembler.flux,
        "/density/real_row": assembler.density_real_row,
        "/density/imag_row": assembler.density_imag_row, "/end": assembler.end,
    }
    for address, args in messages:
        suffix = address.removeprefix(live.NETWORK_ROOT)
        if suffix == "/end" and not include_end: continue
        dispatch[suffix](address, *args)


class TestLiveBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_result = source.build_control_frame(seed=42, depth=1, revision=108)
        cls.source_frame, cls.source_rho = cls.source_result[:2]
        cls.messages = list(source.osc_messages(cls.source_frame, cls.source_rho))

    def test_projection_is_isometric_and_hamiltonian_is_hermitian(self):
        projection = live.hexagram_projection()
        self.assertTrue(np.allclose(projection.T @ projection, np.eye(16)))
        hamiltonian = live.project_laplacian_to_hamiltonian(self.source_result[4])
        self.assertTrue(np.allclose(hamiltonian, hamiltonian.conj().T, atol=1e-12))
        self.assertAlmostEqual(np.trace(hamiltonian).real, 0.0, places=12)
        self.assertLessEqual(np.max(np.abs(np.linalg.eigvalsh(hamiltonian))), 1 + 1e-12)

    def test_incomplete_transaction_never_commits(self):
        committed = []
        assembler = live.IChingNetworkFrameAssembler(committed.append)
        feed(assembler, self.messages, include_end=False)
        self.assertEqual(committed, [])

    def test_complete_transaction_commits_once(self):
        committed = []
        assembler = live.IChingNetworkFrameAssembler(committed.append)
        feed(assembler, self.messages)
        self.assertEqual(len(committed), 1)
        frame = committed[0]
        self.assertEqual(frame.transformed, frame.primary ^ frame.moving_mask)
        self.assertTrue(np.allclose(frame.hamiltonian_16, frame.hamiltonian_16.conj().T))
        self.assertAlmostEqual(np.trace(frame.density_q0_lsb).real, 1.0, places=12)

    def test_commit_occurs_only_at_engine_step_boundary(self):
        engine = FakeEngine(); bridge = live.LiveIChingDensityEngineBridge(engine)
        feed(bridge.assembler, self.messages)
        before = engine.rho.copy()
        self.assertTrue(np.array_equal(engine.rho, before))
        bridge.step(0.01)
        self.assertFalse(np.allclose(engine.rho, before))
        self.assertEqual(bridge.applied_revision, 108)
        self.assertEqual(engine.state_revision, 5)
        self.assertEqual(len(engine.persisted), 1)
        self.assertGreater(np.linalg.norm(engine.hamiltonians_seen[-1]), 0.0)

    def test_density_mix_is_convex_and_physical(self):
        engine = FakeEngine(); bridge = live.LiveIChingDensityEngineBridge(engine, density_mix=0.25)
        feed(bridge.assembler, self.messages); bridge.step(0.01)
        self.assertAlmostEqual(np.trace(engine.rho).real, 1.0, places=12)
        self.assertGreaterEqual(np.linalg.eigvalsh(engine.rho).min(), -1e-10)

    def test_registration_uses_existing_control_server(self):
        engine = FakeEngine(); bridge = live.LiveIChingDensityEngineBridge(engine).register()
        self.assertIn(live.NETWORK_ROOT + "/begin", engine.qmw_bridge.handlers)
        self.assertIn("/qmw/iching/laplacian/gain", engine.qmw_bridge.handlers)


if __name__ == "__main__": unittest.main()
