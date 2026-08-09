import unittest
import numpy as np
from quantum_geometry.modal_geometry_mixer import ModalWorld,mix_modal_lineages,parallel_transport_gauge,synthesize_modal_comparison,validate_lineage_compatibility


class ModalGeometryMixerTests(unittest.TestCase):
    def world(self,name,ids,amps,topology="mesh:x"):
        n=len(ids); return ModalWorld(name,np.array(ids),np.linspace(100,200,n),np.ones(n),np.array(amps,complex),topology,"mass_weighted_invariant_subspace")

    def test_normalizes_conditional_states(self):
        worlds=(self.world("g0",[0],[1]),self.world("g1",[0],[1]))
        a=mix_modal_lineages(np.array([[3,4]],complex),worlds); b=mix_modal_lineages(np.array([[.6,.8]],complex),worlds)
        self.assertTrue(np.allclose(a.population_strength,b.population_strength)); self.assertTrue(np.allclose(a.complex_strength,b.complex_strength))

    def test_lineage_alignment_uses_ids_not_positions(self):
        worlds=(self.world("g0",[4,9],[1,2]),self.world("g1",[9,4],[3,5]))
        frames=mix_modal_lineages(np.array([[1,0],[0,1]],complex),worlds)
        self.assertEqual(frames.lineage_ids.tolist(),[4,9]); self.assertTrue(np.allclose(frames.dominant_strength,[[1,2],[5,3]]))

    def test_compatibility_rejects_missing_tracking_metadata(self):
        with self.assertRaises(ValueError): validate_lineage_compatibility((ModalWorld("g",np.array([0]),np.array([100.]),np.array([1.]),np.array([1.])),))
    def test_global_phase_invariance(self):
        states=np.array([[1,.5j],[np.exp(.3j),.5j*np.exp(.3j)]],complex)/np.sqrt(1.25)
        worlds=(self.world("g0",[0],[1]),self.world("g1",[0],[1j]))
        a=mix_modal_lineages(states,worlds); b=mix_modal_lineages(states*np.exp(1j*np.array([.7,1.1]))[:,None],worlds)
        self.assertTrue(np.allclose(a.complex_strength,b.complex_strength)); self.assertTrue(np.allclose(np.exp(1j*a.complex_phase),np.exp(1j*b.complex_phase)))

    def test_interference_differs_from_population(self):
        worlds=(self.world("g0",[4],[1]),self.world("g1",[4],[1]))
        states=np.array([[1,1],[1,-1]],complex)/np.sqrt(2); frames=mix_modal_lineages(states,worlds)
        self.assertGreater(frames.complex_strength[0,0],1.0); self.assertLess(frames.complex_strength[1,0],1e-12); self.assertTrue(np.allclose(frames.population_strength[:,0],1.0))

    def test_synthesis_shape_and_finite(self):
        worlds=(self.world("g0",[0],[1]),self.world("g1",[0],[1j]))
        frames=mix_modal_lineages(np.array([[1,0],[0,1]],complex),worlds); audio,d=synthesize_modal_comparison(frames,duration_seconds=.05,sample_rate=2000)
        self.assertEqual(audio.shape,(3,100,2)); self.assertTrue(np.all(np.isfinite(audio))); self.assertEqual(len(d["population_complex_rms_divergence"]),2)
        self.assertTrue(np.allclose(audio[:,0,:],0.0)); self.assertTrue(np.allclose(audio[:,-1,:],0.0))
        self.assertEqual(d["voice_envelopes"],"continuous_no_frame_retrigger")


if __name__=="__main__": unittest.main()
