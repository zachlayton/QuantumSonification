import json
import tempfile
import unittest
from pathlib import Path
import numpy as np

from quantum_geometry import (CollapseDynamics,ConfigurationGraph,GeometryState,GraphDensityBridge,build_constraint,build_geometry_field,conditional_history,dirichlet_energy,generate_geometry16,solve_constraint)
from quantum_geometry.adapters.living_geometry_adapter import artifact_frame,export_artifact_sequence


class QuantumGeometry16Tests(unittest.TestCase):
    def setUp(self):
        self.states=generate_geometry16(); self.graph=ConfigurationGraph.build(self.states)

    def test_configuration_graph(self):
        self.assertEqual(self.graph.laplacian.shape,(16,16))
        self.assertTrue(np.allclose(self.graph.laplacian,self.graph.laplacian.T))
        self.assertTrue(np.allclose(self.graph.laplacian.sum(axis=1),0))
        self.assertGreaterEqual(np.min(np.linalg.eigvalsh(self.graph.laplacian)),-1e-10)

    def test_graph_density(self):
        rho=GraphDensityBridge.encode(self.graph.laplacian)
        self.assertAlmostEqual(float(np.trace(rho).real),1.0)
        transformed,_,_=GraphDensityBridge.basis(rho,self.graph.laplacian)
        self.assertAlmostEqual(float(np.trace(transformed).real),1.0)

    def test_constraint_and_page_wootters(self):
        potential=np.linspace(-.4,.4,16); matter=np.diag(.06*np.cos(np.arange(16)))
        base=build_constraint(self.graph.laplacian,alpha=.3,geometry_potential=potential,matter_hamiltonian=matter)
        shift=np.linalg.eigvalsh(base)[np.argmin(np.abs(np.linalg.eigvalsh(base)))]
        c=base-shift*np.eye(16); solution=solve_constraint(c)
        self.assertLess(solution.residual_norm,1e-8)
        hist=conditional_history(solution.state,0.18*self.graph.laplacian+np.diag(potential),steps=16,dt=.3)
        self.assertEqual(hist.weights.shape,(16,16)); self.assertTrue(np.allclose(hist.weights.sum(axis=1),1))
        self.assertTrue(np.isclose(np.linalg.norm(hist.history_state),1))

    def test_collapse_off_is_noop_and_artifacts_export(self):
        psi=np.ones(16,dtype=complex)/4; out,event=CollapseDynamics().step(psi,np.arange(16),1.0)
        self.assertIsNone(event); self.assertTrue(np.allclose(out,psi))
        hist=conditional_history(psi,self.graph.laplacian,steps=3); frames=build_geometry_field(hist.times,hist.weights,self.states)
        self.assertEqual(len(artifact_frame(frames[0].weights,self.states)["weights"]),16)
        with tempfile.TemporaryDirectory() as d:
            path=export_artifact_sequence(frames,self.states,Path(d)/"living.json")
            self.assertEqual(len(json.loads(path.read_text())["frames"]),3)

    def test_family_metric_and_dirichlet_energy(self):
        names=("spectrum","modal","material","geometry","ir")
        states=tuple(GeometryState(f"r{i:02d}",np.array([i]),descriptor_families={name:np.array([i,(-1 if name=='geometry' else 1)*i*i]) for name in names}) for i in range(16))
        graph=ConfigurationGraph.build_interpretable(states,family_weights={"spectrum":2.0},neighbors=3)
        self.assertEqual(set(graph.family_distance_squared),set(names)); self.assertAlmostEqual(sum(graph.family_weights.values()),1.0)
        self.assertTrue(np.allclose(graph.laplacian.sum(axis=1),0))
        constant=np.ones(16)/4
        self.assertAlmostEqual(dirichlet_energy(constant,graph.laplacian),0.0,places=10)


if __name__ == "__main__": unittest.main()
