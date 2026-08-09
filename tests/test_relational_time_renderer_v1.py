import unittest
import numpy as np
from quantum_geometry.modal_geometry_mixer import ModalMixtureFrames
from quantum_geometry.relational_time_renderer import relational_timing,synthesize_continuous_modal


class RelationalTimeRendererTests(unittest.TestCase):
    def test_uniform_motion_gives_uniform_intervals(self):
        theta=np.arange(5)*.1; states=np.stack([np.array([np.cos(x),np.sin(x)]) for x in theta]); timing=relational_timing(states,duration_seconds=4)
        self.assertTrue(np.allclose(timing.interval_seconds,1))

    def test_slowing_motion_lengthens_intervals(self):
        theta=np.array([0,.2,.35,.45,.5]); states=np.stack([np.array([np.cos(x),np.sin(x)]) for x in theta]); timing=relational_timing(states,duration_seconds=4)
        self.assertTrue(np.all(np.diff(timing.interval_seconds)>0)); self.assertAlmostEqual(timing.frame_times_seconds[-1],4)

    def test_continuous_render_has_silent_boundaries(self):
        values=np.ones((3,1)); frames=ModalMixtureFrames(np.array([0]),values,values,np.zeros_like(values),100*values,100*values,values,values,np.zeros_like(values),100*values); timing=relational_timing(np.array([[1,0],[.99,.1],[.96,.28]]),duration_seconds=.1)
        audio=synthesize_continuous_modal(frames,timing,sample_rate=2000)
        self.assertEqual(audio.shape,(200,2)); self.assertTrue(np.allclose(audio[0],0)); self.assertTrue(np.allclose(audio[-1],0))


if __name__=="__main__": unittest.main()
