import unittest
import numpy as np
from qmw.core import Domain,StateData,ObservableData,PhysicsFrame,RegionalData
from qmw.events import FlowEventDetector


def frame(seq,t,flux):
    d=Domain.basis(len(flux))
    return PhysicsFrame(seq,t,.01,"test",d,StateData(rho=np.eye(d.size)/d.size),
        ObservableData(),regions=RegionalData(np.arange(d.size),incoming_energy_flux=np.array(flux,float)))


class FluxEvents(unittest.TestCase):
    def test_hysteresis_refractory_and_duplicate(self):
        detector=FlowEventDetector(threshold=1,refractory=.2)
        self.assertEqual(detector.update(None,frame(0,0,[0])),[])
        events=detector.update(None,frame(1,.01,[1.1]))
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].source_observable,"regions.incoming_energy_flux")
        self.assertEqual(detector.update(None,frame(1,.01,[1.1])),[])
        self.assertEqual(detector.update(None,frame(2,.02,[1.2])),[])
        self.assertEqual(detector.update(None,frame(3,.05,[.4])),[])
        self.assertEqual(detector.update(None,frame(4,.1,[1.2])),[])
        self.assertEqual(len(detector.update(None,frame(5,.25,[1.2]))),1)

    def test_outgoing_flux_is_not_an_arrival(self):
        detector=FlowEventDetector(threshold=1)
        self.assertEqual(detector.update(None,frame(0,0,[-3,-2])),[])

    def test_backward_time_and_invalid_config(self):
        detector=FlowEventDetector();detector.update(None,frame(0,1,[0]))
        with self.assertRaises(ValueError):detector.update(None,frame(1,.9,[0]))
        for kwargs in [{"threshold":0},{"threshold":float('nan')},{"hysteresis":1},{"refractory":-.1}]:
            with self.assertRaises(ValueError):FlowEventDetector(**kwargs)
