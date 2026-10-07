"""Typed envelopes around the actual state/transition/note/timbre implementations."""
from __future__ import annotations
import hashlib
import numpy as np
from qmw.core.transition import FrameContext, QuantumUnits, TransitionFrame
from qmw.core.state_frame import QuantumStateFrame
from .contracts import BasisMetadata, ClockStamp, FeatureId, FeatureValue, FeatureFrame, Provenance


def _basis(context,dimension):
    return BasisMetadata(context.basis_id,dimension,'computational','q0_lsb',
        details={'source_coordinate_basis':context.basis_id})


def _source(value,field,quantity,units,context,*,parameters=None,kind='matrix',backend='numpy'):
    shape=np.shape(value);dimension=shape[0] if shape else 0
    clock=ClockStamp(context.time,context.time_unit,'simulation','elapsed',context.source_id)
    p=Provenance(f'{context.source_id}:frame:{context.frame_id}',field,'source_capture','1',
        {'legacy_provenance':context.provenance,'dt':context.dt,
         'value_sha256':hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
         'shape':shape,'dtype':str(np.asarray(value).dtype),**(parameters or {})},units,
        'none',_basis(context,dimension),clock,backend,'simulated')
    return FeatureValue(FeatureId(field,quantity,kind),value,p)


def state_features(state:QuantumStateFrame,context:FrameContext,units:QuantumUnits,*,backend='numpy'):
    if (state.t,state.dt,state.source_name)!=(context.time,context.dt,context.source_id):
        raise ValueError('state/context source and timing mismatch')
    if state.hamiltonian is None:raise ValueError('Hamiltonian snapshot is unavailable')
    rho=_source(state.rho,'quantum.state.rho','density_matrix','1',context,backend=backend)
    h=_source(state.hamiltonian,'quantum.state.hamiltonian','hamiltonian',units.energy_unit,context,
        parameters={'hbar':units.hbar,'hbar_unit':units.hbar_unit},backend=backend)
    return FeatureFrame(rho.provenance.record_id,(rho,h),{'adapter':'QuantumStateFrame snapshot; no state evolution'})


def operator_feature(A,context,units,*,backend='numpy'):
    return _source(A,'quantum.operator.A','operator',units.operator_unit,context,backend=backend)


def engine_msb_to_lsb(feature):
    """Passive coordinate conversion using the existing engine's bit reversal.

    Apply to every state and operator captured in the same native coordinates.
    Bit reversal is self-inverse; this function requires an explicit q0_msb
    source to prevent double conversion. It never installs a state in an owner.
    """
    from density.density_state_injection import bit_reversal_permutation
    if not isinstance(feature,FeatureValue) or feature.id.kind!='matrix':
        raise ValueError('bit-order adapter requires a typed matrix')
    p=feature.provenance
    if p.basis.kind!='computational' or p.basis.subsystem_order!='q0_msb':
        raise ValueError('native density-engine q0_msb coordinates must be declared')
    n=p.basis.dimension;matrix=np.asarray(feature.require_available())
    if n<2 or n&(n-1) or matrix.shape!=(n,n):
        raise ValueError('qubit matrix dimension must be a matching power of two')
    permutation=bit_reversal_permutation(n.bit_length()-1)
    basis=BasisMetadata('computational',n,'computational','q0_lsb',
        details={'source_coordinate_basis':'computational'})
    provenance=p.derive(p.record_id+':q0_lsb','density.bit_reversal_permutation',
        parameters={'permutation':permutation,'source_subsystem_order':'q0_msb',
            'target_subsystem_order':'q0_lsb','formula':'M_lsb[i,j] = M_native[reverse(i),reverse(j)]',
            'state_evolution':False,'state_installation':False},basis=basis)
    uncertainty=None if feature.uncertainty is None else {
        'kind':'source_coordinate_uncertainty_retained','source_uncertainty':feature.uncertainty,
        'source_subsystem_order':'q0_msb','target_subsystem_order':'q0_lsb','permutation':permutation,
        'output_covariance':None,'policy':'source uncertainty retained; numeric covariance transformation requires its declared convention'}
    return FeatureValue(feature.id,matrix[np.ix_(permutation,permutation)],provenance,
        uncertainty=uncertainty)


def transition_features(frame:TransitionFrame,rho:FeatureValue,H:FeatureValue,A:FeatureValue)->FeatureFrame:
    if not isinstance(frame,TransitionFrame):raise TypeError('requires the actual TransitionEngine frame')
    for f in (rho,H,A):f.require_available()
    v=frame.spectrum.energy_eigenvectors
    expected=((rho.value,v@frame.spectrum.rho_in_energy_basis@v.conj().T),
        (H.value,(v*frame.spectrum.energy_eigenvalues)@v.conj().T),
        (A.value,v@frame.operator_in_energy_basis@v.conj().T))
    for raw,recovered in expected:
        scale=max(float(np.linalg.norm(raw)),np.finfo(float).tiny)
        if np.shape(raw)!=np.shape(recovered) or np.linalg.norm(raw-recovered)>1e-8*scale:
            raise ValueError('transition frame does not describe declared source values')
    c=frame.context;clock=rho.provenance.clock
    for f in (rho,H,A):
        if f.provenance.clock!=clock or f.provenance.basis!=rho.provenance.basis:
            raise ValueError('transition inputs require identical coordinates/clock')
        if f.provenance.record_id!=f'{c.source_id}:frame:{c.frame_id}':
            raise ValueError('transition source frame identity mismatch')
    if clock.value!=c.time or clock.unit!=c.time_unit or clock.origin!=c.source_id:
        raise ValueError('transition source clock mismatch')
    basis=BasisMetadata(f'{c.basis_id}:energy:{c.frame_id}',frame.spectrum.dimension,'hamiltonian','q0_lsb',
        'ascending_energy_frame_local','eigensolver_gauge',{'degenerate_groups':frame.energy_degenerate_groups,
        'label_convention':frame.label_convention,'phase_convention':frame.phase_convention})
    basis_p=H.provenance.derive(f'{c.frame_id}:energy_basis','qmw.core.transition:hamiltonian_eigh',
        parameters={'gap_tolerance':frame.diagnostics['energy_gap_tolerance']},basis=basis)
    a_p=A.provenance.derive(f'{c.frame_id}:A_energy','V_dagger_A_V',parents=(basis_p,A.provenance),basis=basis)
    rho_p=rho.provenance.derive(f'{c.frame_id}:rho_energy','V_dagger_rho_V',parents=(basis_p,rho.provenance),basis=basis)
    features=[]
    for e in frame.edges:
        prefix=f'transition.n{e.source}.m{e.target}';eid=f'{c.source_id}:{c.frame_id}:{e.source}->{e.target}'
        params={'source_n':e.source,'target_m':e.target,'ordering':frame.label_convention,
            'sequence_origin':0,'zero_gap':e.zero_gap,'degenerate_endpoint':e.basis_dependent_degenerate_endpoint}
        def emit(suffix,quantity,value,units,operation,parents,extra=None,kind='scalar'):
            p=parents[0].derive(eid+':'+suffix,operation,parameters=params|(extra or {}),units=units,
                normalization='none',parents=parents,basis=basis,source_path=prefix+'.'+suffix)
            f=FeatureValue(FeatureId(prefix+'.'+suffix,quantity,kind),value,p);features.append(f);return f
        gap=emit('delta_E','energy_gap',e.delta_E,frame.units.energy_unit,'E_m-E_n',(basis_p,))
        emit('omega','angular_frequency',e.omega,frame.units.omega_unit,'delta_E/hbar',(gap.provenance,),
            {'hbar':frame.units.hbar,'hbar_unit':frame.units.hbar_unit})
        emit('endpoints','transition_endpoints',np.array([e.source,e.target]),'index','frame_local_endpoints',(basis_p,),kind='vector')
        magnitude=emit('matrix_element_magnitude','matrix_element_magnitude',e.magnitude,frame.units.operator_unit,'abs(A_mn)',(a_p,))
        pop=emit('source_population','population',e.source_population,'1','rho_nn',(rho_p,))
        emit('state_weighted_magnitude','state_weighted_magnitude',e.magnitude*np.sqrt(max(e.source_population,0)),
            frame.units.operator_unit,'abs(A_mn)*sqrt(max(rho_nn,0))',(magnitude.provenance,pop.provenance),{'roundoff_floor':0})
        emit('diagnostic_activity','diagnostic_activity',max(e.source_population,0)*e.magnitude**2,
            frame.units.operator_unit+'^2','max(rho_nn,0)*abs(A_mn)^2',(magnitude.provenance,pop.provenance),
            {'interpretation':'diagnostic activity; neither physical rate nor selection probability'})
        emit('signed_order','signed_order',e.target-e.source,'index','m-n',(basis_p,))
        emit('absolute_order','absolute_order',abs(e.target-e.source),'index','abs(m-n)',(basis_p,))
    return FeatureFrame(f'{c.source_id}:{c.frame_id}:transitions',tuple(features),
        {'actual_engine':'qmw.core.transition.TransitionEngine','edge_count':len(frame.edges),
         'activity_model':frame.activity_name,'legacy_provenance':frame.provenance})


def _matching_context(feature,context,record_id):
    p=feature.provenance;clock=p.clock
    if (p.record_id!=record_id or clock.value!=context.time or clock.unit!=context.time_unit
        or clock.domain!='simulation' or clock.origin!=context.source_id or clock.semantics!='elapsed'):
        raise ValueError('feature and native frame context identity/clock differ')


def note_pitch_feature(note,endpoint_feature,projector,*,admission_feature):
    """Retain the actual pitch projector configuration and originating event ID."""
    c=note.context;edge=f'{c.source_id}:{c.frame_id}:{note.source_state}->{note.target_state}'
    _matching_context(endpoint_feature,c,edge+':endpoints')
    _matching_context(admission_feature,c,edge+':diagnostic_activity')
    if endpoint_feature.provenance.basis.to_dict()!=admission_feature.provenance.basis.to_dict():
        raise ValueError('note feature bases differ')
    if tuple(np.asarray(endpoint_feature.require_available()))!=(note.source_state,note.target_state):
        raise ValueError('note and endpoint feature mismatch')
    if note.target_degree!=projector.state_degrees[note.target_state] or not np.isclose(note.target_frequency_hz,projector.ratio_field.frequency_hz(note.target_degree),atol=0,rtol=1e-12):
        raise ValueError('note and declared pitch mapping differ')
    expected=f'transition.n{note.source_state}.m{note.target_state}.diagnostic_activity'
    if admission_feature.id.path!=expected or not np.isclose(admission_feature.require_available(),note.strength,rtol=1e-10,atol=0):
        raise ValueError('note requires the actual admission activity and its rho/A ancestry')
    params={'state_degrees':projector.state_degrees,'ratios':projector.ratio_field.ratios,
        'period':projector.ratio_field.period,'reference_hz':projector.ratio_field.reference_hz,
        'ratio_field':projector.ratio_field.name,'min_activity':projector.min_activity,
        'max_events':projector.max_events,'source_degree':note.source_degree,'target_degree':note.target_degree,
        'originating_event_id':note.event_id,'legacy_provenance':note.provenance}
    p=endpoint_feature.provenance.derive(note.event_id+':pitch','qmw.TransitionPitchProjector','1',params,
        units='Hz',normalization='explicit_ratio_field',source_path='note.pitch',
        parents=(endpoint_feature.provenance,admission_feature.provenance))
    return FeatureValue(FeatureId('note.pitch','excitation_frequency'),note.target_frequency_hz,p)


def timbre_features(body,rho_feature,geometry_feature):
    """Actual independent body output; preserve decomposition and modal parents."""
    from qmw.acoustics.note_timbre import ModalResonatorFrame
    if not isinstance(body,ModalResonatorFrame):raise TypeError('requires actual ModalResonatorFrame')
    c=body.context
    _matching_context(rho_feature,c,f'{c.source_id}:frame:{c.frame_id}')
    if rho_feature.provenance.basis.basis_id!=c.basis_id or geometry_feature.provenance.basis.to_dict()!=rho_feature.provenance.basis.to_dict():
        raise ValueError('body source and geometry coordinate context differ')
    geometry_clock=geometry_feature.provenance.clock
    if geometry_clock.domain!='configuration' and geometry_clock!=rho_feature.provenance.clock:
        raise ValueError('dynamic geometry and source context clocks differ; static geometry must declare configuration clock')
    if not np.allclose(body.geometry_hilbert_vectors,geometry_feature.require_available(),atol=1e-10):
        raise ValueError('body and declared geometry basis differ')
    rho=rho_feature.require_available();rec=(body.density_eigenvectors*body.density_eigenvalues)@body.density_eigenvectors.conj().T
    if not np.allclose(rho,rec,atol=1e-10):raise ValueError('body and source density differ')
    phi=geometry_feature.value
    expected=np.real(np.diag(phi.conj().T@rho@phi))
    if not np.allclose(body.modal_probability_weights,expected,atol=1e-10,rtol=1e-10):
        raise ValueError('body modal weights do not match the actual density-to-geometry projection')
    if not np.allclose(body.amplitude_gains,np.sqrt(np.maximum(expected,0)),atol=1e-10,rtol=1e-10):
        raise ValueError('body gains do not match sqrt(modal weights)')
    p=rho_feature.provenance.derive(f'{body.context.frame_id}:body','qmw.QuantumTimbreProjector','1',
        {'formula':'sum_k lambda_k*abs(phi_j_dagger_psi_k)^2','geometry_id':body.geometry_id,
         'mode_ids':body.mode_ids,'captured_weight':body.captured_weight,
         'legacy_provenance':body.provenance},units='1',normalization='raw_captured_weight',
        parents=(rho_feature.provenance,geometry_feature.provenance))
    return FeatureFrame(f'{body.context.frame_id}:body',(
        FeatureValue(FeatureId('body.modal_weights','modal_probability_weights','vector'),body.modal_probability_weights,p),
        FeatureValue(FeatureId('body.amplitude_gains','modal_amplitude_gains','vector'),body.amplitude_gains,
            p.derive(f'{body.context.frame_id}:body_gains','sqrt(max(modal_weights,0))',units='1')),
    ),{'density_reconstruction_error':float(np.linalg.norm(rec-rho)),'diagnostics':dict(body.diagnostics)})


def lorentz_features(frame,provenance):
    """Envelope the registered Lorentz frame with caller-declared source clock.

    The bundled model is an effective analogue. A physical force calibration
    would require a separate named adapter and cannot be asserted by unit text.
    """
    from .upstream import load_lorentz_frame_type
    if not isinstance(frame,load_lorentz_frame_type()):
        raise TypeError('requires the registered actual LorentzFrame')
    if not isinstance(provenance,Provenance) or provenance.parameters.get('force_interpretation')!='effective_analogue':
        raise ValueError('effective analogue force interpretation must be declared')
    if provenance.units in ('N','newton','newtons'):
        raise ValueError('physical force units require a separate calibration adapter')
    for name in ('position','velocity','electric_field','magnetic_field','force_vector','excitation_position'):
        value=np.asarray(getattr(frame,name))
        if value.shape!=(3,) or np.iscomplexobj(value) or not np.all(np.isfinite(value)):
            raise ValueError('Lorentz vectors must be finite real xyz coordinates')
    if not np.isfinite(frame.force_magnitude) or frame.force_magnitude<0 or not np.isclose(np.linalg.norm(frame.force_vector),frame.force_magnitude,atol=1e-12,rtol=1e-10):
        raise ValueError('Lorentz force magnitude must match the vector')
    p=provenance.derive(provenance.record_id+':lorentz','actual_LorentzFrame_capture',
        parameters={'frame_type':frame.frame_type,'schema_version':frame.schema_version,
            'declared_native_frame':frame.to_dict(),'clock_supplied_by_source_adapter':True},
        source_path='lorentz.force_vector')
    vector=FeatureValue(FeatureId('lorentz.force_vector','force_vector','vector'),frame.force_vector,p)
    magnitude=FeatureValue(FeatureId('lorentz.force_magnitude','force_magnitude'),frame.force_magnitude,
        p.derive(p.record_id+':magnitude','euclidean_force_norm',source_path='lorentz.force_magnitude'))
    derivative=FeatureValue(FeatureId('lorentz.force_derivative','force_magnitude_time_derivative'),frame.force_derivative,
        p.derive(p.record_id+':derivative','native_LorentzFrame_force_derivative',
            parameters={'meaning':'signed derivative of force magnitude; supplied by native engine'},
            units=provenance.units+'/'+provenance.clock.unit,source_path='lorentz.force_derivative'))
    return FeatureFrame(provenance.record_id+':lorentz',(vector,magnitude,derivative))
