import unittest
from dataclasses import replace
import numpy as np
from scipy.linalg import expm
from qmw.sound.stiff_string import StringParameters,StiffString,ForceEvent,render_force_events,force_events_from_physics
from qmw.core import PhysicsEvent,EventType


class StiffStringTests(unittest.TestCase):
    def test_frequencies_follow_physical_parameters_not_harmonic_assignment(self):
        p=StringParameters(modes=20,bending_stiffness_nm2=0)
        s=StiffString(p)
        f0=np.sqrt(p.tension_n/p.linear_density_kg_m)/(2*p.length_m)
        np.testing.assert_allclose(s.frequency_hz,f0*np.arange(1,21),rtol=1e-14)
        stiffer=StiffString(replace(p,bending_stiffness_nm2=.02))
        self.assertGreater(stiffer.frequency_hz[-1]/stiffer.frequency_hz[0],20)
        tension=StiffString(replace(p,tension_n=p.tension_n*4))
        np.testing.assert_allclose(tension.frequency_hz,s.frequency_hz*2,rtol=1e-14)

    def test_free_motion_against_analytic_solution(self):
        s=StiffString(StringParameters(modes=1));s.q[0]=.001;s.v[0]=.03
        q0,v0=s.q[0],s.v[0];sigma=s.sigma[0];omega=s.omega[0]
        s.process(np.zeros(12000),pickups=(.5,))
        t=12000/s.sample_rate;w=np.sqrt(omega**2-sigma**2)
        expected_q=np.exp(-sigma*t)*(q0*np.cos(w*t)+(v0+sigma*q0)*np.sin(w*t)/w)
        expected_v=np.exp(-sigma*t)*(v0*np.cos(w*t)-(omega**2*q0+sigma*v0)*np.sin(w*t)/w)
        self.assertAlmostEqual(s.q[0],expected_q,10)
        self.assertAlmostEqual(s.v[0],expected_v,8)

    def test_forcing_matches_independent_augmented_matrix_exponential(self):
        s=StiffString(StringParameters(modes=1));s.q[0]=.0004;s.v[0]=-.02
        force=np.random.default_rng(123).normal(size=400)
        a=np.array([[0,1,0],[-s.omega2[0],-2*s.sigma[0],1/s.modal_mass],[0,0,0]])
        transition=expm(a/s.sample_rate)
        qv=np.array([s.q[0],s.v[0]])
        expected=[]
        for f in force:
            full=transition@np.array([*qv,f]);qv=full[:2];expected.append(qv[1])
        actual=s.process(force[None,:],pickups=(.5,),pickup_width_m=0)[:,0]
        np.testing.assert_allclose(actual,expected,rtol=1e-8,atol=1e-10)
        np.testing.assert_allclose([s.q[0],s.v[0]],qv,rtol=1e-8,atol=1e-10)

    def test_streaming_preserves_state_across_blocks_and_contacts(self):
        p=StringParameters(modes=12);a=StiffString(p);b=StiffString(p)
        f=np.random.default_rng(3).normal(size=9000)*.1
        whole=a.process(f,position=.13)
        chunks=np.concatenate([b.process(f[i:i+127],position=.13) for i in range(0,len(f),127)])
        np.testing.assert_allclose(chunks,whole,atol=2e-9,rtol=2e-7)
        q=b.q.copy();v=b.v.copy()
        b.process(np.zeros(0),position=.7)
        np.testing.assert_array_equal(b.q,q);np.testing.assert_array_equal(b.v,v)

    def test_energy_conserved_without_loss_and_decreases_with_loss(self):
        p=StringParameters(modes=16,loss0_per_s=0,loss1_m2_s=0)
        s=StiffString(p);s.static_pluck();initial=s.energy_j()
        for _ in range(20):s.process(np.zeros(1024))
        self.assertLess(abs(s.energy_j()/initial-1),1e-7)
        damped=StiffString(replace(p,loss0_per_s=.4,loss1_m2_s=.0005));damped.static_pluck()
        energies=[damped.energy_j()]
        for _ in range(20):
            damped.process(np.zeros(1024));energies.append(damped.energy_j())
        self.assertTrue(np.all(np.diff(energies)<0))

    def test_center_excitation_and_center_pickup_remove_even_modes(self):
        s=StiffString(StringParameters(modes=20))
        s.static_pluck(.001,position=.5)
        self.assertLess(np.max(np.abs(s.q[1::2])),1e-17)
        self.assertLess(np.max(np.abs(s.spatial_weights(.5)[1::2])),1e-14)

    def test_pickup_position_is_observation_and_does_not_change_energy(self):
        a=StiffString(StringParameters(modes=12));b=StiffString(a.parameters)
        a.static_pluck();b.static_pluck()
        ya=a.process(np.zeros(2000),pickups=(.18,));yb=b.process(np.zeros(2000),pickups=(.5,))
        self.assertGreater(np.max(abs(ya-yb)),.01)
        np.testing.assert_array_equal(a.q,b.q);np.testing.assert_array_equal(a.v,b.v)

    def test_static_compliance_and_no_reinitialization(self):
        s=StiffString();hold=s.static_pluck(.001,position=.19,width_m=.004)
        b=s.spatial_weights(.19,.004)
        self.assertAlmostEqual(b@s.q,.001,14)
        np.testing.assert_allclose(s.modal_mass*s.omega2*s.q,hold*b,rtol=1e-14)
        with self.assertRaises(ValueError):s.static_pluck()

    def test_physics_force_mapping_does_not_assign_pitch(self):
        events=[PhysicsEvent(EventType.ENERGY_ARRIVAL,i,.003,"regions.incoming_energy_flux",region=i) for i in range(16)]
        forces=force_events_from_physics(events)
        self.assertEqual(len(forces),16)
        self.assertTrue(all(not hasattr(f,"frequency_hz") for f in forces))
        self.assertAlmostEqual(forces[0].impulse_ns,.0015)
        self.assertLess(forces[0].position,forces[-1].position)

    def test_force_renderer_block_invariance_and_linearity(self):
        p=StringParameters(modes=8)
        e=[ForceEvent(.004,.001,.2,.002),ForceEvent(.029,-.0008,.61,.001)]
        a,s=render_force_events(e,.12,p,block_size=256)
        b,_=render_force_events(e,.12,p,block_size=79)
        np.testing.assert_allclose(a,b,atol=1e-9,rtol=1e-7)
        one,_=render_force_events(e[:1],.12,p)
        two,_=render_force_events(e[1:],.12,p)
        np.testing.assert_allclose(a,one+two,atol=1e-9,rtol=1e-7)

    def test_invalid_inputs_and_bandlimit(self):
        for kwargs in [{"tension_n":-1},{"loss1_m2_s":-1},{"length_m":float('nan')},{"modes":2.5}]:
            with self.assertRaises(ValueError):StringParameters(**kwargs)
        s=StiffString(StringParameters(modes=400))
        self.assertGreater(s.truncated_modes,0);self.assertLess(s.frequency_hz[-1],.45*s.sample_rate)
        with self.assertRaises(ValueError):s.spatial_weights(.01,.1)
        with self.assertRaises(ValueError):s.process([float('nan')])


if __name__=='__main__':unittest.main()
