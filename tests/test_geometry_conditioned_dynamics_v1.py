import unittest
import numpy as np
from quantum_geometry.geometry_conditioned_dynamics import GeometryConditionedConfig,effective_hamiltonian,geometry_conditioned_history,local_geometry_operators


class GeometryConditionedDynamicsTests(unittest.TestCase):
    def setUp(self):
        self.A=np.zeros((4,4)); self.A[np.arange(3),np.arange(1,4)]=1; self.A+=self.A.T; self.L=np.diag(self.A.sum(1))-self.A; self.v=np.linspace(-.2,.2,4); self.local=local_geometry_operators(self.A,self.v)

    def test_effective_hamiltonian_is_hermitian(self):
        psi=np.array([1,1j,.3,-.2j]); psi=psi/np.linalg.norm(psi); rho=np.outer(psi,psi.conj()); h=effective_hamiltonian(rho,.2*self.L+np.diag(self.v),self.local,self.A)
        self.assertTrue(np.allclose(h,h.conj().T)); self.assertAlmostEqual(np.trace(h).real,0.0)

    def test_evolution_preserves_norm_and_changes_generator(self):
        psi=np.ones(4,dtype=complex)/2; history=geometry_conditioned_history(psi,.2*self.L+np.diag(self.v),self.A,self.v,steps=8,dt=.4)
        self.assertTrue(np.allclose(np.linalg.norm(history.states,axis=1),1)); self.assertTrue(np.allclose(history.weights.sum(axis=1),1)); self.assertGreater(np.max(history.hamiltonian_change_norms),0)
        self.assertGreater(np.std(history.step_fidelities),1e-8)


if __name__=="__main__": unittest.main()
