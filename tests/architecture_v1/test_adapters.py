import numpy as np
import pytest
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
from qmw.core.state_frame import QuantumStateFrame
from qmw.architecture_v1.adapters import state_features, operator_feature, transition_features

def test_actual_transition_features_retain_operator_and_state_ancestors():
    c=FrameContext('fixture',3,0.,.01,'computational'); u=QuantumUnits()
    h=np.diag([0.,2.]); a=np.array([[0.,2.],[2.,0.]]); rho=np.diag([.75,.25])
    s=QuantumStateFrame(0.,.01,rho,h,'fixture')
    sources=state_features(s,c,u); af=operator_feature(a,c,u)
    t=TransitionEngine(units=u).process(h,a,rho,c)
    f=transition_features(t,sources.get('quantum.state.rho'),sources.get('quantum.state.hamiltonian'),af)
    w=f.get('transition.n0.m1.state_weighted_magnitude')
    assert w.value==pytest.approx(np.sqrt(.75)*2)
    assert len(w.provenance.parents)==2
    assert f.get('transition.n0.m1.diagnostic_activity').value==3
    assert f.get('transition.n1.m0.signed_order').value==-1
    assert w.provenance.basis.ordering.startswith('ascending_energy')
    np.testing.assert_array_equal(s.rho,rho)

def test_adapter_rejects_mismatched_authority_source():
    c=FrameContext('fixture',1,0.,.1,'computational');u=QuantumUnits()
    s=QuantumStateFrame(0.,.1,np.eye(2)/2,np.diag([0.,2.]),'fixture')
    f=state_features(s,c,u);a=operator_feature(np.eye(2),c,u)
    t=TransitionEngine().process(s.hamiltonian,np.array([[0,1],[1,0]]),s.rho,c)
    with pytest.raises(ValueError):transition_features(t,f.get('quantum.state.rho'),f.get('quantum.state.hamiltonian'),a)


def test_actual_lorentz_frame_to_selected_amplitude():
    from qmw.architecture_v1.upstream import load_lorentz_frame_type
    from qmw.architecture_v1.adapters import lorentz_features
    from qmw.architecture_v1.amplitude import TransitionAmplitudeProjector
    from qmw.architecture_v1.contracts import BasisMetadata, ClockStamp, Provenance
    cls=load_lorentz_frame_type()
    frame=cls(np.zeros(3),np.zeros(3),np.array([3.,4.,0.]),np.zeros(3),np.array([3.,4.,0.]),5.,0.,np.zeros(3),{'source':'declared fixture'})
    p=Provenance('lorentz:fixture','actual.LorentzFrame','fixture','1',{'force_interpretation':'effective_analogue'},
        'model_force','none',BasisMetadata('xyz',3,'effective_spatial','not_applicable'),
        ClockStamp(0.,'s','simulation','elapsed','fixture'),'numpy','declared_test_fixture')
    f=lorentz_features(frame,p).get('lorentz.force_magnitude')
    amplitude=TransitionAmplitudeProjector('lorentz_force_magnitude',reference=10.,reference_units='model_force').project(f)
    assert amplitude.value==.5 and amplitude.provenance.parents[0]==f.provenance
    frame.force_vector[:]=0
    assert f.value==5.
    with pytest.raises(ValueError,match='magnitude'):lorentz_features(frame,p)


def test_native_engine_qubit_zero_is_converted_to_lsb_for_state_and_operator():
    from qmw.architecture_v1.adapters import engine_msb_to_lsb
    from qmw.architecture_v1.contracts import BasisMetadata,ClockStamp,FeatureId,FeatureValue,Provenance
    from density.density_matrix_engine_4q import local_operator
    from qmw_representation_laboratory_v4.observables import pauli_matrix
    p=Provenance('native:1','density4q','native_snapshot','1',{},'1','none',
        BasisMetadata('native_engine',16,'computational','q0_msb'),
        ClockStamp(0.,'s','simulation','elapsed','native'),'numpy','simulated')
    rho=np.zeros((16,16),complex);rho[8,8]=1.
    source=FeatureValue(FeatureId('rho','density_matrix','matrix'),rho,p)
    output=engine_msb_to_lsb(source)
    assert np.argmax(np.diag(output.value))==1
    assert output.provenance.basis.subsystem_order=='q0_lsb'
    native=local_operator(0,np.diag([1.,-1.]))
    z=engine_msb_to_lsb(FeatureValue(FeatureId('H','hamiltonian','matrix'),native,p))
    np.testing.assert_array_equal(z.value,pauli_matrix('ZIII'))
    assert np.trace(output.value@z.value)==-1
    np.testing.assert_array_equal(source.value,rho)
    with pytest.raises(ValueError):engine_msb_to_lsb(output)
