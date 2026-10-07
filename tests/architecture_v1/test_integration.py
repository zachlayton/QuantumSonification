from dataclasses import replace
import numpy as np
import pytest
from qmw.architecture_v1.contracts import RoutingPreset
from qmw.architecture_v1.router import SonificationRouter
from qmw.architecture_v1.integration import build_four_qubit_demo, render_routed_event, export_demo


def test_actual_four_qubit_chain_and_independent_amplitude():
    a = build_four_qubit_demo(amplitude_reference=4.)
    b = build_four_qubit_demo(amplitude_reference=8.)
    assert a['source'].rho.shape == (16,16)
    assert a['report']['authority_unchanged']
    assert a['report']['maximum_basis_roundtrip_error'] < 1e-10
    assert a['report']['density_reconstruction_error'] < 1e-10
    assert a['report']['modal_weight_error'] < 1e-10
    np.testing.assert_allclose(a['body'].modal_probability_weights,b['body'].modal_probability_weights,atol=1e-12)
    np.testing.assert_allclose(a['render'].audio,2*b['render'].audio,rtol=1e-10,atol=1e-12)
    assert np.max(np.abs(a['render'].audio)) > 0
    assert a['render'].excitation.strength == a['routed'].values['note.amplitude'].value
    assert a['render'].excitation.event_id == a['note'].event_id
    assert a['report']['second_amplitude_source_rejected']
    assert len(a['audit']['active_parameters']) == 8
    for entry in a['audit']['active_parameters'].values():
        assert entry['provenance']['parents']
        assert entry['provenance']['parameters']['primary_source']


def test_junction_rejects_omitted_parameter_and_stale_body():
    a = build_four_qubit_demo()
    fewer = RoutingPreset('incomplete',a['preset'].routes[:-1])
    bad = SonificationRouter(fewer).route(a['bus'])
    with pytest.raises(ValueError,match='exactly'):
        render_routed_event(a['note'],a['body'],bad)
    stale = replace(a['body'],frequencies_hz=a['body'].frequencies_hz*1.01,
        decay_seconds=a['body'].decay_seconds/1.01)
    with pytest.raises(ValueError,match='body'):
        render_routed_event(a['note'],stale,a['routed'])
    stale_gains=replace(a['body'],amplitude_gains=a['body'].amplitude_gains*2)
    with pytest.raises(ValueError,match='gains'):
        render_routed_event(a['note'],stale_gains,a['routed'])
    with pytest.raises(ValueError,match='event'):
        render_routed_event(replace(a['note'],event_id='another_event'),a['body'],a['routed'])


def test_export_is_finite_stereo_with_traceable_raw_level(tmp_path):
    import hashlib
    import json
    from scipy.io import wavfile
    a=build_four_qubit_demo()
    paths=export_demo(a,tmp_path)
    sr,samples=wavfile.read(paths['audio'])
    assert sr==24000 and samples.shape==(6000,2)
    np.testing.assert_allclose(samples,a['render'].audio,rtol=1e-6,atol=1e-9)
    audit=json.loads(paths['audit'].read_text())
    assert audit['renderer']['automatic_normalization'] is False
    assert audit['source']['frame_id']==a['note'].context.frame_id
    assert audit['source']['state_revision']==a['report']['state_revision']
    root=audit['render_provenance']
    assert root['operation']=='actual_offline_modal_junction' and len(root['parents'])==8
    digest=hashlib.sha256(json.dumps(root,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    assert 'architecture_derivation:'+digest in a['render'].provenance


def test_analysis_reconstructs_state_and_keeps_measurement_discrete():
    from qmw.architecture_v1.integration import analyze_four_qubit_demo
    a=build_four_qubit_demo();before=a['source'].rho.copy()
    analysis=analyze_four_qubit_demo(a)
    assert analysis.metadata['complete_pauli_reconstruction_error']<1e-10
    assert analysis.get('resources.contextuality').availability=='unsupported'
    measurement=analysis.get('measurement.discrete_record')
    assert measurement.value['origin']=='simulated_sample'
    assert not analysis.metadata['measurement_update_installed']
    np.testing.assert_array_equal(before,a['source'].rho)


def test_actual_adapter_rejects_wrong_projection_and_stale_identical_values():
    from qmw.architecture_v1.adapters import timbre_features, note_pitch_feature
    from qmw.acoustics.note_timbre import TransitionPitchProjector, RatioField
    a=build_four_qubit_demo();body=a['body'];rho=a['source_features'].get('quantum.state.rho')
    geometry=a['bus'].get('geometry.hilbert_modes')
    weights=np.roll(body.modal_probability_weights,1)
    wrong=replace(body,modal_probability_weights=weights,amplitude_gains=np.sqrt(weights))
    with pytest.raises(ValueError,match='weights'):timbre_features(wrong,rho,geometry)
    stale=replace(rho,provenance=replace(rho.provenance,record_id='other_source:frame:99',
        clock=replace(rho.provenance.clock,value=99)))
    with pytest.raises(ValueError,match='context'):timbre_features(body,stale,geometry)
    note=a['note'];prefix=f'transition.n{note.source_state}.m{note.target_state}'
    endpoint=a['bus'].get(prefix+'.endpoints');activity=a['bus'].get(prefix+'.diagnostic_activity')
    projector=TransitionPitchProjector(state_degrees=tuple(range(16)),
        ratio_field=RatioField((1.,9/8,5/4,4/3,3/2),reference_hz=110.,name='declared_five_ratio_field'),max_events=1)
    bad_endpoint=replace(endpoint,provenance=replace(endpoint.provenance,clock=replace(endpoint.provenance.clock,value=99)))
    with pytest.raises(ValueError,match='context'):
        note_pitch_feature(note,bad_endpoint,projector,admission_feature=activity)
    semantic_change=replace(endpoint,provenance=replace(endpoint.provenance,
        clock=replace(endpoint.provenance.clock,semantics='filter_parameter')))
    with pytest.raises(ValueError,match='context'):
        note_pitch_feature(note,semantic_change,projector,admission_feature=activity)


def test_actual_matrix_manifold_remains_primary_during_explicit_audio_projection():
    from qmw.architecture_v1.integration import project_four_qubit_matrix
    a=build_four_qubit_demo();matrix=a['manifold'].value.copy()
    output=project_four_qubit_matrix(a)
    assert output.get('audio_projection.samples').value.shape==(2400,)
    assert np.all(np.isfinite(output.get('audio_projection.samples').value))
    assert output.get('audio.wavetable').provenance.parameters['routing_mode']=='ANALYSIS'
    assert output.metadata['table_nyquist_policy']=='excluded'
    np.testing.assert_array_equal(a['manifold'].value,matrix)
