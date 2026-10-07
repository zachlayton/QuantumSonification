import dataclasses
import numpy as np
import pytest

from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureId, FeatureValue, FeatureFrame,
    Provenance, MappingSpec, frozen_array, AnalysisBasis,
)


def context():
    return BasisMetadata('computational', 2, 'computational', 'q0_lsb'), ClockStamp(0., 's', 'simulation', 'elapsed', 'run:1')


def source(path='state.rho', quantity='density_matrix', value=None):
    basis, clock = context()
    p = Provenance('frame:1', path, 'source_capture', '1', {}, '1', 'trace_one', basis, clock, 'numpy', 'simulated')
    return FeatureValue(FeatureId(path, quantity, 'matrix'), np.eye(2)/2 if value is None else value, p)


def test_freezes_nested_values_and_arrays_irreversibly():
    raw = np.array([1.,2.]); a = frozen_array(raw); raw[0] = 9
    assert a[0] == 1
    with pytest.raises(ValueError): a.setflags(write=True)
    f = source(); assert not f.value.flags.writeable
    with pytest.raises(dataclasses.FrozenInstanceError): f.availability = 'missing'
    with pytest.raises(TypeError): f.provenance.parameters['x'] = 1


def test_provenance_retains_all_dependencies_and_serializes():
    a=source(); b=source('operator.A','operator',np.eye(2))
    p=a.provenance.derive('weighted','matrix_element_times_population','1',{'exponent':.5},units='1',normalization='none',parents=(a.provenance,b.provenance))
    assert len(p.parents)==2 and len(p.to_dict()['parents'])==2
    assert p.digest == p.digest
    assert b.provenance.digest != a.provenance.digest


def test_missingness_not_zero_and_invalid_metadata_rejected():
    p=source().provenance
    with pytest.raises(ValueError): FeatureValue(FeatureId('data.time','event_time'),None,p)
    with pytest.raises(ValueError): FeatureValue(FeatureId('data.time','event_time'),None,p,availability='missing')
    f=FeatureValue(FeatureId('data.time','event_time'),None,p,availability='missing',reason='not measured')
    with pytest.raises(ValueError): f.require_available()
    with pytest.raises(ValueError): source(value=np.array([[np.nan,0],[0,1]]))
    with pytest.raises(ValueError): ClockStamp(1.,'s','','elapsed','run')
    with pytest.raises(ValueError): FeatureFrame('1',(source(),source()))


def test_mapping_declares_inputs_and_parameters():
    f=source(); spec=MappingSpec('map','1','identity',(f.id,),'1','none',{'nested':{'a':[1,2]}})
    assert spec.parameters['nested']['a'] == (1,2)
    with pytest.raises(TypeError): spec.parameters['nested']['a']=()
    with pytest.raises(ValueError): MappingSpec('map','1','identity',(),'1','none',{})


def test_direct_basis_rejects_empty_missing_provenance_and_wrong_fingerprint():
    p=source().provenance
    with pytest.raises(ValueError):AnalysisBasis(BasisMetadata('none',0,'none'),np.zeros((0,0)),p)
    with pytest.raises(ValueError):AnalysisBasis(p.basis,np.eye(2),None)
    other=dataclasses.replace(p,basis=BasisMetadata('different',2,'computational'))
    with pytest.raises(ValueError):AnalysisBasis(p.basis,np.eye(2),other)
    bad=dataclasses.replace(p,parameters={'vectors_sha256':'0'*64})
    with pytest.raises(ValueError):AnalysisBasis(p.basis,np.eye(2),bad)
