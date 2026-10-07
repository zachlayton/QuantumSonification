import unittest
import numpy as np
from qmw.core.transition import TransitionEngine
from qmw.acoustics.transition_harmony import chord_matrix, QUALITY_RATIOS, validate_harmony_arguments

class HarmonyTests(unittest.TestCase):
    def project(self,rho,H=None,A=None,**kwargs):
        H=np.diag(np.arange(16,dtype=float)) if H is None else H
        A=np.kron(np.eye(8),[[0,1],[1,0]]) if A is None else A
        f=TransitionEngine().compute(H,rho,A)
        return chord_matrix(rho,f,**kwargs),f

    def test_all_four_qualities_and_four_inversions_have_four_distinct_notes(self):
        h,_=self.project(np.eye(16)/16)
        self.assertTrue(validate_harmony_arguments(h.arguments()))
        self.assertEqual(h.cells.shape,(16,12))
        for i,row in enumerate(h.cells):
            q,inv=divmod(i,4);base=np.array(QUALITY_RATIOS[q])
            expected=np.r_[base[inv:],2*base[:inv]]
            np.testing.assert_allclose(row[4:8]/row[0],expected)
            self.assertTrue(np.all(np.diff(row[4:8])>0))
            self.assertAlmostEqual(row[8:].sum(),1)

    def test_population_changes_quality_inversion_key_and_position(self):
        results=[]
        for i in [0,5,10,15]:
            rho=np.zeros((16,16));rho[i,i]=1
            h,_=self.project(rho)
            self.assertEqual(h.active_cell,i)
            self.assertAlmostEqual(h.position_cv,i/15)
            self.assertEqual(h.size_cv,0)
            results.append(h.cells[i])
        self.assertEqual([int(row[1]) for row in results],[0,1,2,3])
        self.assertEqual([int(row[2]) for row in results],[0,1,2,3])
        self.assertGreater(results[-1][0],results[0][0])

    def test_coherence_changes_size_cv_without_changing_populations(self):
        mixed,_=self.project(np.eye(16)/16)
        pure,_=self.project(np.ones((16,16))/16)
        self.assertAlmostEqual(mixed.position_cv,pure.position_cv)
        self.assertEqual(mixed.size_cv,0)
        self.assertAlmostEqual(pure.size_cv,1)

    def test_transition_activity_changes_cell_weights_without_density_change(self):
        rho=np.eye(16)/16
        a=np.zeros((16,16));a[0,1]=a[1,0]=1
        b=np.zeros((16,16));b[14,15]=b[15,14]=1
        first,_=self.project(rho,A=a);last,_=self.project(rho,A=b)
        self.assertGreater(first.cells[0,3],last.cells[0,3])
        self.assertGreater(last.cells[15,3],first.cells[15,3])

    def test_projection_respects_eigenvector_phase_and_does_not_mutate_inputs(self):
        rho=np.eye(16,dtype=complex)/16;copy=rho.copy()
        h,f=self.project(rho)
        # Rephasing V leaves |V|^2 unchanged; test with an interface stand-in.
        from types import SimpleNamespace
        phases=np.exp(1j*np.linspace(0,6,16))
        other=chord_matrix(rho,SimpleNamespace(diagnostic_activity=f.diagnostic_activity,
                                            eigenvectors=f.eigenvectors*phases))
        np.testing.assert_allclose(h.cells,other.cells)
        np.testing.assert_array_equal(rho,copy)
        self.assertFalse(h.cells.flags.writeable)

    def test_fixed_H_can_preserve_energy_activity_while_computational_density_moves(self):
        H=np.kron(np.eye(8),[[0,1],[1,0]])*.5
        ket=np.zeros(16,complex);ket[0]=1
        rho=np.outer(ket,ket.conj())
        ket2=ket.copy();ket2[0]=np.cos(.7);ket2[1]=-1j*np.sin(.7)
        evolved=np.outer(ket2,ket2.conj())
        a,f=self.project(rho,H=H,A=np.diag(np.arange(16,dtype=float)))
        b,g=self.project(evolved,H=H,A=np.diag(np.arange(16,dtype=float)))
        np.testing.assert_allclose(f.diagnostic_activity,g.diagnostic_activity,atol=1e-12)
        self.assertNotAlmostEqual(a.position_cv,b.position_cv)

    def test_extreme_pitch_controls_remain_in_audio_range_and_bad_packets_reject(self):
        for base in [55,880]:
            for octave in [-2,2]:
                h,_=self.project(np.diag([0.]*15+[1.]),base_hz=base,octave=octave)
                self.assertTrue(validate_harmony_arguments(h.arguments()))
        good=h.arguments()
        for index,value in [(0,2),(1,-.1),(2,1.1),(3,16),(8,20000),(12,-.1),(7,4)]:
            bad=good.copy();bad[index]=value
            with self.subTest(index=index),self.assertRaises(ValueError):validate_harmony_arguments(bad)
        with self.assertRaises(ValueError):validate_harmony_arguments(good[:-1])
