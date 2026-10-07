"""Shared checked synthesis preparation and an executable offline junction.

This module does not install quantum states, open network ports, or play audio.
The demo creates a private existing four-qubit owner and only observes its seed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import numpy as np

from qmw.core.state_frame import QuantumStateFrame
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine
from qmw.acoustics.note_timbre import (RatioField, TransitionPitchProjector,
    GeometryModes, QuantumTimbreProjector, OfflineModalResonator,
    QuantumNoteEvent, ModalResonatorFrame)
from .contracts import (BasisMetadata, ClockStamp, Provenance, FeatureId,
    FeatureValue, FeatureFrame, MappingSpec, RouteSpec, RoutingPreset,
    ExecutionRequest, RoutedFrame, plain)
from .adapters import (state_features, operator_feature, transition_features,
    note_pitch_feature, timbre_features, engine_msb_to_lsb)
from .backend import DensitySnapshotBackend, DENSITY
from .basis import BasisProjector
from .router import FeatureBus, SonificationRouter
from .rhythm import RhythmProjector
from .amplitude import TransitionAmplitudeProjector
from .transition_order import TransitionOrderAnalyzer


AUDIBLE = {'note.pitch':'Hz','note.amplitude':'1','note.onset':'s','note.duration':'s',
    'body.modal_weights':'1','body.frequencies':'Hz','body.quality_factors':'1',
    'body.acoustic_phases':'rad'}


def _identity(feature,destination=None):
    destination=destination or feature.id.path
    return RouteSpec(destination,feature.id,MappingSpec('route:'+destination,'1','identity',
        (feature.id,),feature.units,'none',{'input_units':(feature.units,)}))


def _sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def _ancestors(provenance):
    yield provenance
    for parent in provenance.parents:
        yield from _ancestors(parent)


@dataclass(frozen=True)
class PreparedRoutedEvent:
    """The sole checked handoff used by offline audio and the live sender.

    The original event retains transition admission activity; ``excitation``
    explicitly relabels its strength as the mapped linear amplitude. Identity,
    source context, pitch and the independent body remain unchanged.
    """
    original_note: QuantumNoteEvent
    excitation: QuantumNoteEvent
    body: ModalResonatorFrame
    routed: RoutedFrame
    provenance: Provenance


def prepare_routed_event(note, body, routed) -> PreparedRoutedEvent:
    """Validate all eight audible inputs without rendering or scheduling.

    Pitch and modal-body results must match the actual upstream projectors;
    independently mapped rhythm/amplitude replace only the excitation fields.
    Audible source clocks stay in routed provenance; neither this preparation
    nor a representation change modifies the original source frame context.
    """
    if not isinstance(note, QuantumNoteEvent) or not isinstance(body, ModalResonatorFrame):
        raise ValueError('junction requires the actual note and modal-body frame types')
    if not isinstance(routed, RoutedFrame):
        raise ValueError('junction requires the shared routed frame')
    if note.context != body.context or note.context.time_unit != 's':
        raise ValueError('junction requires matching note/body source contexts in seconds')
    if set(routed.values)!=set(AUDIBLE):
        raise ValueError('junction requires exactly the eight declared audible parameters')
    for path,units in AUDIBLE.items():
        feature=routed.values[path]
        feature.require_available()
        if feature.units!=units:raise ValueError(f'{path}: incompatible audible units')
    value=lambda path:routed.values[path].value
    event_ids={p.parameters['originating_event_id'] for p in _ancestors(routed.values['note.pitch'].provenance)
        if 'originating_event_id' in p.parameters}
    if event_ids!={note.event_id}:
        raise ValueError('pitch route must retain the actual originating event identity')
    for path in ('note.pitch', 'note.amplitude', 'note.onset', 'note.duration'):
        scalar = np.asarray(value(path))
        if scalar.ndim != 0 or scalar.dtype.kind not in 'iuf' or not np.isfinite(scalar):
            raise ValueError(f'{path}: audible value must be a finite real scalar')
    if float(value('note.duration')) <= 0:
        raise ValueError('note duration must be positive')
    if not 0<=float(value('note.amplitude'))<=1:
        raise ValueError('note amplitude must be normalized within [0,1]')
    if not np.isclose(value('note.pitch'),note.target_frequency_hz,atol=0,rtol=1e-12):
        raise ValueError('pitch must describe the actual TransitionPitchProjector result')
    for path,actual in [('body.modal_weights',body.modal_probability_weights),
        ('body.frequencies',body.frequencies_hz),('body.quality_factors',body.quality_factors),
        ('body.acoustic_phases',body.acoustic_phases_rad)]:
        if np.shape(value(path))!=np.shape(actual) or not np.allclose(value(path),actual,atol=1e-12,rtol=1e-12):
            raise ValueError(f'{path}: route and actual body differ')
    if not np.allclose(body.amplitude_gains,np.sqrt(np.maximum(body.modal_probability_weights,0)),atol=1e-12,rtol=1e-12):
        raise ValueError('body gains must retain the actual sqrt(modal weights) relation')
    if not np.allclose(body.decay_seconds, body.quality_factors/(np.pi*body.frequencies_hz),
                       rtol=1e-12, atol=0):
        raise ValueError('body decay must retain the actual Q/(pi*f) relation')
    parents=tuple(routed.values[k].provenance for k in sorted(AUDIBLE))
    provenance=parents[0].derive(note.event_id+':routed_preparation','checked_note_body_preparation',
        parameters={'event_id':note.event_id, 'routing_mode':routed.mode.value,
            'preset_id':routed.preset_id, 'audible_parameters':tuple(sorted(AUDIBLE)),
            'original_admission_activity':note.strength,
            'original_activity_name':note.activity_name, 'original_activity_units':note.activity_units,
            'amplitude_policy':'mapped linear excitation amplitude; no extra square root',
            'body_policy':'independent modal frame; sqrt(modal probability weights)',
            'source_context_unchanged':True},
        parents=parents, units='1', normalization='none', source_path='synthesis.prepared_event',
        evidence='musical_mapping')
    mapped=replace(note, strength=float(value('note.amplitude')),
        activity_name='mapped_linear_excitation_amplitude', activity_units='1',
        onset_seconds=float(value('note.onset')), duration_seconds=float(value('note.duration')),
        provenance=note.provenance+('architecture_preparation:'+provenance.digest,))
    return PreparedRoutedEvent(note, mapped, body, routed, provenance)


def render_routed_event(note,body,routed,*,sample_rate=24000,duration_seconds=.25):
    """Render shared checked preparation with the existing offline resonator.

    Native offline buffers start at the original source context time. A live
    monotonic onset must therefore be explicitly rebased for offline replay;
    no silent conversion between musical and source clocks occurs here.
    """
    prepared=prepare_routed_event(note, body, routed)
    parents=prepared.provenance.parents
    derivation=parents[0].derive(note.event_id+':routed_render','actual_offline_modal_junction',
        parameters={'event_id':note.event_id,'sample_rate':sample_rate,'duration_seconds':duration_seconds,
            'prepared_event_digest':prepared.provenance.digest,
            'amplitude_policy':'note.strength = note.amplitude directly; no extra square root',
            'excitation_envelope':'Hann sine burst','excitation_phase_rad':0.,'stereo_pan':0.,
            'body_decay_formula':'Q/(pi*f)','automatic_normalization':False,
            'tail_policy':'finite window truncation'},parents=parents,units='digital_amplitude',
        normalization='none',source_path='audio.offline',evidence='offline_render')
    mapped=replace(prepared.excitation,
        provenance=prepared.excitation.provenance+('architecture_derivation:'+derivation.digest,))
    native=OfflineModalResonator(sample_rate=sample_rate,duration_seconds=duration_seconds).process(excitation=mapped,timbre=prepared.body)
    return native,derivation


def build_four_qubit_demo(*,amplitude_reference=16.,rhythm_time_scale=.002):
    """Actual four-qubit snapshot -> transition -> independent note/body render."""
    from density.density_matrix_engine_4q import DensityMatrixEngine
    from qmw.qho import OscillatorSpec, oscillator_operators
    from quantum_geometry import ConfigurationGraph, generate_geometry16
    from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold

    owner=DensityMatrixEngine(enable_circuit_bridge_control=False,osc_telemetry_hz=0)
    before=np.array(owner.rho,copy=True);revision=owner.state_revision;time=owner.logical_time
    context=FrameContext('architecture_four_qubit_demo',revision,time,.01,'computational',
        provenance=('existing DensityMatrixEngine initial coherent seed; observed without evolution',))
    units=QuantumUnits()
    basis_meta=BasisMetadata('computational',16,'computational','q0_lsb',
        details={'source_coordinate_basis':'computational'})
    native_basis=BasisMetadata('density_engine_native',16,'computational','q0_msb',
        details={'source':'density_matrix_engine_4q.tensor_operator'})
    clock=ClockStamp(time,'s','simulation','elapsed',context.source_id)
    owner_p=Provenance('four_qubit_owner','density/density_matrix_engine_4q.py',
        'existing_owner_initial_state','1',{'state_revision':revision,'rho_sha256':_sha(before),
        'state_seed':'existing coherent seed from owner','evolution_performed':False},
        '1','trace_one',native_basis,clock,'numpy','simulated')
    backend=DensitySnapshotBackend(owner,owner_p)
    snapshot=backend.execute(ExecutionRequest('demo_snapshot','snapshot',frozenset({DENSITY.path}),clock))
    captured=next(f for f in snapshot.features if f.id==DENSITY)
    native_h=np.array(owner.hamiltonian(),copy=True)
    converted_rho=engine_msb_to_lsb(captured)
    captured_h=FeatureValue(FeatureId('quantum.state.hamiltonian','hamiltonian','matrix'),native_h,
        owner_p.derive('native:H','DensityMatrixEngine.hamiltonian',parameters={
            'owner_parameters':dict(owner.params),'hamiltonian_sha256':_sha(native_h),
            'hbar':units.hbar,'hbar_unit':units.hbar_unit},
            parents=(owner_p,captured.provenance),units=units.energy_unit,normalization='none'))
    converted_h=engine_msb_to_lsb(captured_h)
    state=QuantumStateFrame(time,.01,converted_rho.value,converted_h.value,context.source_id)
    source=state_features(state,context,units)
    rho0=source.get('quantum.state.rho');hf0=source.get('quantum.state.hamiltonian')
    rho=replace(rho0,provenance=replace(rho0.provenance,parents=(converted_rho.provenance,)))
    hf=replace(hf0,provenance=replace(hf0.provenance,parents=(converted_h.provenance,)))
    source=FeatureFrame(source.frame_id,(rho,hf))
    qho=oscillator_operators(OscillatorSpec(dimension=16,omega=1.,hbar=1.))
    af0=operator_feature(qho.x,context,units)
    af=replace(af0,provenance=replace(af0.provenance,parameters={**af0.provenance.parameters,
        'operator':'canonical truncated QHO position','source':'qmw/qho/operators.py',
        'encoding':'Fock index n assigned to computational integer n for this observable only',
        'dimension':16,'omega':1.,'hbar':1.,'does_not_define_owner_hamiltonian':True}))
    transitions=TransitionEngine(units=units).process_state(state,af.value,context)
    tf=transition_features(transitions,rho,hf,af)
    pitch=TransitionPitchProjector(state_degrees=tuple(range(16)),
        ratio_field=RatioField((1.,9/8,5/4,4/3,3/2),reference_hz=110.,name='declared_five_ratio_field'),
        max_events=1)
    notes=pitch.process(transitions)
    if not notes:raise ValueError('actual transition source yielded no admissible notes')
    note=notes[0];edge=f'transition.n{note.source_state}.m{note.target_state}'
    pf=note_pitch_feature(note,tf.get(edge+'.endpoints'),pitch,admission_feature=tf.get(edge+'.diagnostic_activity'))
    gap=tf.get(edge+'.delta_E')
    rhythm=RhythmProjector(MappingSpec('gap_period_to_rhythm','1','rhythm',(gap.id,),'s','none',{
        'input_units':(gap.units,),'energy_constant_kind':'hbar','energy_constant':units.hbar,
        'energy_constant_unit':units.hbar_unit,'source_time_unit':units.time_unit,
        'source_seconds_per_unit':1.,'frequency_convention':'angular','time_scale':rhythm_time_scale}))
    event=rhythm.project(gap,note.event_id,ClockStamp(time,'s','musical','elapsed','demo_buffer_start'))
    interval=rhythm.as_feature(event)
    onset=FeatureValue(FeatureId('note.onset','musical_onset'),event.onset.value,
        event.provenance.derive(note.event_id+':onset','explicit_musical_anchor',
            parameters={'onset_anchor':event.onset.to_dict()},units='s',source_path='note.onset'))
    amplitude=TransitionAmplitudeProjector('state_weighted_magnitude',reference=amplitude_reference,
        reference_units=units.operator_unit).project(tf.get(edge+'.state_weighted_magnitude'))

    graph=ConfigurationGraph.build(generate_geometry16(seed=1604))
    eig,phi=np.linalg.eigh(graph.laplacian)
    gp=Provenance('geometry16:1604','quantum_geometry/configuration_graph.py',
        'ConfigurationGraph.build','1',{'seed':1604,'neighbors':4,'sigma_policy':'median_nonzero_distance',
        'laplacian_sha256':_sha(graph.laplacian),'embedding':'abstract graph-mode columns assigned to the declared 16 Hilbert coordinates',
        'physical_surface_claim':False},'1','none',basis_meta,clock,'numpy','declared_geometry_fixture')
    modes=FeatureValue(FeatureId('geometry.hilbert_modes','hilbert_mode_vectors','matrix'),phi,
        gp.derive('geometry16:modes','laplacian_eigh',parameters={'vectors_sha256':_sha(phi)},units='1'))
    spectral_coordinate=FeatureValue(FeatureId('geometry.spectral_coordinate','sqrt_laplacian_eigenvalue','vector'),
        np.sqrt(np.maximum(eig,0)),gp.derive('geometry16:spectral_coordinate','sqrt(max(eigenvalues,0))',
            parameters={'eigenvalues':eig,'roundoff_floor':0},units='1'))
    q=FeatureValue(FeatureId('body.quality_factors','modal_quality_factor','vector'),np.full(16,16.),
        gp.derive('geometry16:Q','declared_body_configuration',parameters={'Q':16.,'mode_count':16},units='1'))
    phase=FeatureValue(FeatureId('body.acoustic_phases','acoustic_phase','vector'),np.zeros(16),
        gp.derive('geometry16:phase','declared_body_configuration',parameters={'phase_rad':0.,'mode_count':16},units='rad'))
    frequency_route=RouteSpec('body.frequencies',spectral_coordinate.id,
        MappingSpec('graph_eigenvalue_to_body_hz','1','affine',(spectral_coordinate.id,),'Hz','none',
            {'input_units':('1',),'scale':180.,'offset':220.}))
    geometry_routes=(frequency_route,_identity(q),_identity(phase))
    geometry_frame=FeatureFrame('geometry16:configuration',(spectral_coordinate,q,phase))
    configured=SonificationRouter(RoutingPreset('geometry_configuration',geometry_routes)).route(geometry_frame)
    geometry=GeometryModes(phi,context.basis_id,'abstract_configuration_graph16',tuple(f'mode_{j+1}' for j in range(16)),
        configured.values['body.frequencies'].value,q.value,phase.value,provenance=(gp.digest,modes.provenance.digest))
    body=QuantumTimbreProjector().process(rho=state.rho,geometry_modes=geometry,context=context)
    body_features=timbre_features(body,rho,modes)
    weights=body_features.get('body.modal_weights')
    frame=FeatureFrame(source.frame_id,source.features+(af,)+tf.features+(pf,interval,onset,amplitude,modes,
        spectral_coordinate,q,phase)+body_features.features)
    bus=FeatureBus(frame)
    routes=(_identity(pf),_identity(amplitude),_identity(onset),
        RouteSpec('note.duration',interval.id,MappingSpec('interval_to_burst_duration','1','affine',(interval.id,),
            's','none',{'input_units':('s',),'scale':1.,'offset':0.})),_identity(weights))+geometry_routes
    preset=RoutingPreset('four_qubit_analysis_v1',routes)
    router=SonificationRouter(preset);routed=router.route(bus)
    rejected=False
    try:SonificationRouter(RoutingPreset('invalid_two_amplitudes',routes+(_identity(amplitude),)))
    except ValueError:rejected=True
    render,render_provenance=render_routed_event(note,body,routed)

    bp=BasisProjector();computational=bp.computational(16,rho.provenance)
    qho_vectors=FeatureValue(FeatureId('qho.analysis_vectors','basis_vectors','matrix'),np.linalg.eigh(qho.hamiltonian)[1],
        af.provenance.derive('qho:analysis_vectors','canonical_QHO_eigenvectors',parameters={
            'encoding':'declared Fock-label observable on qubit coordinates; no oscillator evolution claimed'},units='1'))
    bases={'computational':computational,'hamiltonian':bp.hamiltonian(hf),
        'qho':bp.qho(16,rho.provenance,vectors=qho_vectors),'qft':bp.qft(16,rho.provenance)}
    projected={name:bp.project(rho,basis,operators={'A':af}) for name,basis in bases.items()}
    errors={name:float(np.linalg.norm(bp.inverse(projected[name].rho,basis)-rho.value)) for name,basis in bases.items()}
    order=TransitionOrderAnalyzer().process(transitions,tf)
    manifold=QuantumMatrixManifold(rho.value,computational.vectors,bases['qft'].vectors,
        source_basis_name='computational',target_basis_name='qft')
    mf=FeatureValue(FeatureId('manifold.matrix','density_matrix','matrix'),manifold.matrix_at(.37),
        rho.provenance.derive('demo:matrix_manifold','qmw.QuantumMatrixManifold.matrix_at',
            parameters={'eta':.37,'eta_units':'dimensionless_path_coordinate','physical_evolution':False,
                'source_basis':'computational','target_basis':'qft','branch_shifts':None},
            parents=(rho.provenance,computational.provenance,bases['qft'].provenance),units='1'))
    # Attach the effective path basis explicitly rather than claiming this is rho in the original coordinates.
    mf=replace(mf,provenance=replace(mf.provenance,basis=BasisMetadata('manifold:eta:.37',16,'basis_path',
        details={'reference_basis':basis_meta.to_dict(),'eta':.37})))
    unchanged=bool(np.array_equal(before,owner.rho) and revision==owner.state_revision and time==owner.logical_time)
    if not unchanged:raise RuntimeError('read-only demo unexpectedly changed the source owner')
    expected_weights=np.real(np.diag(phi.conj().T@rho.value@phi))
    report={'authority_unchanged':unchanged,'state_revision':revision,'rho_sha256':_sha(rho.value),
        'actual_engine':'density.density_matrix_engine_4q.DensityMatrixEngine',
        'transition_engine':'qmw.core.transition.TransitionEngine','transition_edge_count':len(transitions.edges),
        'event_id':note.event_id,'basis_roundtrip_errors':errors,'maximum_basis_roundtrip_error':max(errors.values()),
        'density_reconstruction_error':body_features.metadata['density_reconstruction_error'],
        'modal_weight_error':float(np.max(np.abs(weights.value-expected_weights))),
        'second_amplitude_source_rejected':rejected,'peak_abs':float(np.max(np.abs(render.audio))),
        'sample_rate':render.sample_rate,'rendered_seconds':len(render.audio)/render.sample_rate}
    audit={'source':{'source_id':context.source_id,'frame_id':context.frame_id,'time':time,'dt':context.dt,
            'state_revision':revision,'backend':backend.capabilities.backend_id},
        'active_parameters':{k:f.to_dict() for k,f in routed.values.items()},
        'render_provenance':render_provenance.to_dict(),
        'renderer':{'implementation':dict(render.diagnostics),'automatic_normalization':False,
            'fixed_configuration':{'excitation_phase_rad':0.,'stereo_pan':0.,'envelope':'Hann sine burst',
                'sample_rate':render.sample_rate,'buffer_seconds':.25},
            'amplitude_policy':'direct excitation multiplier; body gains separately sqrt(modal weights)',
            'event_id':note.event_id,'mapped_legacy_provenance':render.provenance},'report':report}
    return {'source':state,'source_features':source,'operator':af,'transitions':transitions,'transition_features':tf,
        'note':note,'body':body,'bus':bus,'preset':preset,'routed':routed,'render':render,
        'render_provenance':render_provenance,'bases':bases,
        'basis_projections':projected,'order':order,'manifold':mf,'report':report,'audit':audit}


def analyze_four_qubit_demo(demo):
    """Independent resource/correlation observers and a discrete simulated measurement."""
    from .resources import ResourceAnalyzer
    from .correlations import correlations_from_rho, pair_tensor, multipartite_tensor, reconstruct_density_linear
    from .measurement import MeasurementEngine
    rho=demo['source_features'].get('quantum.state.rho');before=np.array(rho.value,copy=True)
    resources=ResourceAnalyzer().analyze(rho,subsystem_dimensions=(2,2,2,2),partition=(0,2),
        metrics=('purity','entropy_nats','coherence_l1','coherence_relative_entropy_nats',
            'negativity','log_negativity','entanglement_entropy_nats','stabilizer_renyi2_bits','contextuality'))
    correlations=correlations_from_rho(rho)
    reconstructed=reconstruct_density_linear(correlations)
    pair=pair_tensor(correlations,0,1,connected=True)
    tensor=multipartite_tensor(correlations,(0,1,2,3))
    measurement=MeasurementEngine(seed=29).projective(rho,'demo:measurement:1',basis='Z',mode='collapse',
        revision_before=demo['report']['state_revision'],request_id=1)
    record=FeatureValue(FeatureId('measurement.discrete_record','measurement_record','record'),
        {key:plain(getattr(measurement,key)) for key in measurement.__dataclass_fields__ if key!='provenance'},
        measurement.provenance)
    if not np.array_equal(before,rho.value):raise RuntimeError('analysis changed authoritative snapshot')
    error=float(np.linalg.norm(reconstructed.value-rho.value))
    return FeatureFrame('demo:analysis',resources.features+correlations.features+(pair,tensor,reconstructed,record),
        {'authority_unchanged':True,'complete_pauli_reconstruction_error':error,
            'measurement_update_installed':False,'measurement_is_discrete':True,
            'resource_basis':rho.provenance.basis.to_dict(),'pauli_axes':correlations.metadata['axes']})


def project_four_qubit_matrix(demo):
    """Explicitly select, normalize, route and sample a real matrix audio view."""
    from .audio_projection import AudioProjection256
    source=demo['manifold'];projector=AudioProjection256()
    projected=projector.project(source,mode='real_bipolar')
    normalized=projector.normalize(projected.get('audio_projection.raw'),remove_dc=True)
    table=normalized.get('audio_projection.table')
    router=SonificationRouter(RoutingPreset('declared_matrix_audio_view',(_identity(table,'audio.wavetable'),)))
    routed=router.route(normalized)
    return projector.play(routed.values['audio.wavetable'],fundamental_hz=110.,sample_rate=24000,
        sample_count=2400,initial_phase=0.)


def export_demo(demo,output_directory):
    """Save raw float stereo audio and complete JSON provenance without playback."""
    from scipy.io import wavfile
    directory=Path(output_directory).expanduser().resolve();directory.mkdir(parents=True,exist_ok=True)
    paths={'audio':directory/'four_qubit_demo.wav','audit':directory/'provenance.json','report':directory/'report.json'}
    wavfile.write(paths['audio'],demo['render'].sample_rate,np.asarray(demo['render'].audio,dtype=np.float32))
    paths['audit'].write_text(json.dumps(plain(demo['audit']),indent=2,sort_keys=True,allow_nan=False)+'\n')
    paths['report'].write_text(json.dumps(plain(demo['report']),indent=2,sort_keys=True,allow_nan=False)+'\n')
    return paths
