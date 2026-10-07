"""Downstream order diagnostics over actual TransitionEngine edges.

For the ordered energy endpoints n -> m, alpha = m-n and delta_E = E_m-E_n.
For H = hbar*omega0*(N+1/2), omega_mn = alpha*omega0. Order is a frame-local
index difference; it is not generally an energy gap or temporal frequency.
No transitions, state evolution, event probabilities, or sound are generated.
"""
from __future__ import annotations

import numpy as np

from qmw.core.transition import TransitionFrame
from .contracts import FeatureFrame, FeatureId, FeatureValue


_WEIGHTS = ('magnitude', 'matrix_element_squared', 'population_weighted_matrix_element')


def _nonnegative(value, name):
    if isinstance(value, (bool, np.bool_, complex, np.complexfloating)):
        raise ValueError(f'{name} must be a finite nonnegative real value')
    number = float(value)
    if not np.isfinite(number) or number < 0:
        raise ValueError(f'{name} must be a finite nonnegative real value')
    return number


def _equal(actual, expected, name):
    """Relative check without an energy-unit-sized absolute tolerance floor."""
    scale = max(abs(float(actual)), abs(float(expected)), np.finfo(float).tiny)
    if not np.isfinite(actual) or not np.isfinite(expected) or abs(actual - expected) > 1e-9 * scale:
        raise ValueError(f'{name} disagrees with the actual transition frame')


class TransitionOrderAnalyzer:
    """Aggregate one declared nonnegative diagnostic and retain every edge.

    ``normalization='sum'`` divides by the sum of the selected edge weights;
    this is a normalized diagnostic distribution, not a selection probability.
    ``sequence_origin`` changes display labels only; internal n and m stay
    zero-based. All edge bins, including zero-strength bins, remain present.

    ``source_features`` must contain the supervisor's ``transition_features``
    adapter output for this exact actual frame. A frame with no retained edges
    has no endpoint provenance in that adapter and is rejected explicitly.
    Zero-strength retained edges are supported and produce zero distributions.
    """

    def __init__(self, *, weight='magnitude', normalization='none', sequence_origin=0):
        if weight not in _WEIGHTS:
            raise ValueError(f'weight must be one of {_WEIGHTS}; custom activity needs an explicit adapter')
        if normalization not in ('none', 'sum'):
            raise ValueError('normalization must be none or sum')
        if isinstance(sequence_origin, (bool, np.bool_)) or not isinstance(sequence_origin, (int, np.integer)):
            raise ValueError('sequence_origin must be an integer')
        self.weight = weight
        self.normalization = normalization
        self.sequence_origin = int(sequence_origin)

    def process(self, frame: TransitionFrame, source_features: FeatureFrame) -> FeatureFrame:
        if not isinstance(frame, TransitionFrame):
            raise TypeError('requires the actual qmw.core.transition.TransitionFrame')
        if not isinstance(source_features, FeatureFrame):
            raise TypeError('source_features must be the shared FeatureFrame')
        if not frame.edges:
            raise ValueError('empty transition frame has no endpoint source provenance; no order feature is emitted')
        energies = np.asarray(frame.spectrum.energy_eigenvalues)
        dimension = frame.spectrum.dimension
        if energies.shape != (dimension,) or not np.all(np.isfinite(energies)) or np.any(np.diff(energies) < 0):
            raise ValueError('requires finite ascending energy ordering from the actual engine')
        c = frame.context
        rows, parents, seen = [], [], set()
        weight_units = frame.units.operator_unit + ('^2' if self.weight != 'magnitude' else '')
        signed_axis = np.arange(1 - dimension, dimension, dtype=int)
        absolute_axis = np.arange(dimension, dtype=int)
        signed_raw = np.zeros(len(signed_axis))
        absolute_raw = np.zeros(dimension)

        def source(edge, suffix, quantity, expected, units):
            path = f'transition.n{edge.source}.m{edge.target}.{suffix}'
            try:
                value = source_features.get(path)
            except KeyError as exc:
                raise ValueError(f'missing source evidence {path}') from exc
            raw = value.require_available()
            if value.id.quantity != quantity or value.units != units:
                raise ValueError(f'{path}: incompatible quantity or units')
            p = value.provenance
            eid = f'{c.source_id}:{c.frame_id}:{edge.source}->{edge.target}'
            if p.record_id != eid + ':' + suffix or p.source_path != path:
                raise ValueError(f'{path}: source frame/event identity mismatch')
            if (p.clock.value, p.clock.unit, p.clock.origin) != (c.time, c.time_unit, c.source_id):
                raise ValueError(f'{path}: source clock mismatch')
            if (p.basis.dimension != dimension or p.basis.kind != 'hamiltonian'
                    or p.basis.details.get('label_convention') != frame.label_convention
                    or tuple(p.basis.details.get('degenerate_groups', ())) != frame.energy_degenerate_groups):
                raise ValueError(f'{path}: source basis/ordering mismatch')
            if suffix == 'endpoints':
                if np.shape(raw) != (2,) or not np.array_equal(raw, expected):
                    raise ValueError(f'{path}: source endpoints mismatch')
            else:
                _equal(_nonnegative(raw, path), expected, path)
            return value

        for edge in frame.edges:
            for name, endpoint in (('source', edge.source), ('target', edge.target)):
                if (isinstance(endpoint, (bool, np.bool_)) or not isinstance(endpoint, (int, np.integer))
                        or not 0 <= endpoint < dimension):
                    raise ValueError(f'{name} endpoint must be an in-range zero-based integer')
            n, m = int(edge.source), int(edge.target)
            if (n, m) in seen:
                raise ValueError('duplicate transition endpoint pair in actual engine frame')
            seen.add((n, m))
            _equal(edge.delta_E, float(energies[m] - energies[n]), 'delta_E')
            _equal(edge.omega, edge.delta_E / frame.units.hbar, 'omega')
            magnitude = _nonnegative(edge.magnitude, 'matrix element magnitude')
            _equal(magnitude, abs(edge.A_mn), 'magnitude versus A_mn')
            for name, activity in edge.activity.items():
                _nonnegative(activity, f'activity {name}')
            if 'matrix_element_squared' not in edge.activity:
                raise ValueError('missing matrix_element_squared activity')
            _equal(edge.activity['matrix_element_squared'], magnitude ** 2, 'matrix_element_squared')
            if edge.diagonal != (m == n):
                raise ValueError('diagonal flag disagrees with endpoints')
            endpoint_feature = source(edge, 'endpoints', 'transition_endpoints', [n, m], 'index')
            magnitude_feature = source(edge, 'matrix_element_magnitude', 'matrix_element_magnitude',
                                       magnitude, frame.units.operator_unit)
            if self.weight == 'magnitude':
                weight, weight_p = magnitude, magnitude_feature.provenance
            elif self.weight == 'matrix_element_squared':
                weight = float(edge.activity['matrix_element_squared'])
                weight_p = magnitude_feature.provenance.derive(
                    magnitude_feature.provenance.record_id + ':squared', 'abs(A_mn)^2',
                    parameters={'exponent': 2}, units=weight_units, normalization='none')
            else:
                if self.weight not in edge.activity or frame.activity_name != self.weight:
                    raise ValueError('selected population-weighted diagnostic unavailable in actual frame')
                weight = _nonnegative(edge.activity[self.weight], 'population-weighted activity')
                _equal(weight, max(edge.source_population, 0) * magnitude ** 2, 'population-weighted activity')
                weight_p = source(edge, 'diagnostic_activity', 'diagnostic_activity', weight, weight_units).provenance
            parents.extend((endpoint_feature.provenance, weight_p))
            alpha = m - n
            with np.errstate(over='ignore'):
                signed_raw[alpha + dimension - 1] += weight
                absolute_raw[abs(alpha)] += weight
            eid = f'{c.source_id}:{c.frame_id}:{n}->{m}'
            rows.append({
                'edge_id': eid, 'source_n': n, 'target_m': m,
                'source_label': n + self.sequence_origin, 'target_label': m + self.sequence_origin,
                'signed_order': alpha, 'absolute_order': abs(alpha),
                'delta_E': edge.delta_E, 'energy_unit': frame.units.energy_unit,
                'omega': edge.omega, 'angular_frequency_unit': frame.units.omega_unit,
                'A_mn': edge.A_mn, 'magnitude': magnitude, 'phase_rad': edge.phase_rad,
                'source_population': edge.source_population, 'target_population': edge.target_population,
                'coherence_mn': edge.coherence_mn, 'coherence_nm': edge.coherence_nm,
                'activity': dict(edge.activity), 'diagonal': edge.diagonal, 'zero_gap': edge.zero_gap,
                'basis_dependent_degenerate_endpoint': edge.basis_dependent_degenerate_endpoint,
                'weight': weight, 'weight_source': self.weight, 'weight_units': weight_units,
                'endpoint_source_path': endpoint_feature.id.path,
                'weight_source_record_id': weight_p.record_id,
            })
        with np.errstate(over='ignore'):
            total = float(signed_raw.sum())
        if not np.isfinite(total) or not np.all(np.isfinite(absolute_raw)):
            raise ValueError('order aggregation overflow; use a declared upstream unit rescaling')
        metadata = {
            'actual_engine': 'qmw.core.transition.TransitionEngine', 'source_frame_id': source_features.frame_id,
            'source_id': c.source_id, 'engine_frame_id': c.frame_id, 'dimension': dimension,
            'edge_count': len(rows), 'weight': self.weight, 'weight_units': weight_units,
            'normalization': self.normalization, 'normalization_denominator': total,
            'signed_order_convention': 'alpha=m-n', 'energy_difference_convention': 'E_m-E_n',
            'angular_frequency_convention': '(E_m-E_n)/hbar', 'hbar': frame.units.hbar,
            'hbar_unit': frame.units.hbar_unit, 'angular_frequency_unit': frame.units.omega_unit,
            'ordering': frame.label_convention, 'internal_sequence_origin': 0,
            'sequence_origin': self.sequence_origin, 'energy_degenerate_groups': frame.energy_degenerate_groups,
            'ordering_limit': 'frame-local indices; degenerate eigenspace gauges and level crossings can change order assignments',
            'weight_interpretation': 'nonnegative transition diagnostic; not a physical transition rate or event selection probability',
            'scope': 'all retained actual engine edges, including zero weights; no new event admission',
        }
        prefix = f'{c.source_id}:{c.frame_id}:transition_order:{self.weight}:{self.normalization}'
        edge_p = parents[0].derive(prefix + ':edges', 'retain_transition_edges_and_compute_order',
            parameters=metadata, units='mixed; see per-field units', normalization='none',
            parents=tuple(parents), source_path='transition_order.edges')
        features = [FeatureValue(FeatureId('transition_order.edges', 'ordered_transition_records', 'events'), tuple(rows), edge_p)]
        for name, axis, raw in (('signed', signed_axis, signed_raw), ('absolute', absolute_axis, absolute_raw)):
            path = 'transition_order.' + name
            axis_p = edge_p.derive(prefix + ':' + name + ':axis', 'complete_order_index_axis',
                parameters={'order': name, 'axis_origin': int(axis[0]), 'spacing': 1},
                units='index', normalization='none', source_path=path + '.axis')
            raw_p = edge_p.derive(prefix + ':' + name + ':raw', 'sum_selected_edge_weight_by_order',
                parameters={'order': name, 'weight': self.weight, 'axis': axis},
                units=weight_units, normalization='none', source_path=path + '.raw')
            selected = raw if self.normalization == 'none' else raw / total if total > 0 else np.zeros_like(raw)
            selected_p = raw_p.derive(prefix + ':' + name + ':weights',
                'identity' if self.normalization == 'none' else 'divide_by_total_selected_edge_weight',
                parameters={'denominator': total, 'zero_policy': 'all zero weights remain zero',
                            'interpretation': metadata['weight_interpretation']},
                units=weight_units if self.normalization == 'none' else '1',
                normalization=self.normalization, source_path=path + '.weights')
            features.extend((
                FeatureValue(FeatureId(path + '.axis', name + '_order_axis', 'vector'), axis, axis_p),
                FeatureValue(FeatureId(path + '.raw', 'order_aggregated_diagnostic_weight', 'vector'), raw, raw_p),
                FeatureValue(FeatureId(path + '.weights', 'order_distribution', 'vector'), selected, selected_p),
            ))
        return FeatureFrame(prefix, tuple(features), metadata)


def order_fourier(frame: FeatureFrame, *, order='signed', normalization='ortho') -> FeatureFrame:
    """Explicit DFT over contiguous order bins, with reversible NumPy convention.

    The transform uses array index j=0..N-1, where alpha=axis_origin+j. Its
    conjugate coordinate is cycles per order index. The basis is not a clock;
    these coordinates must not be labeled Hz or physical angular frequency.
    No Fourier transform occurs automatically in TransitionOrderAnalyzer.
    """
    if order not in ('signed', 'absolute') or normalization not in ('backward', 'forward', 'ortho'):
        raise ValueError('select signed/absolute order and backward/forward/ortho FFT normalization')
    if not isinstance(frame, FeatureFrame):
        raise TypeError('requires a shared FeatureFrame')
    source = frame.get(f'transition_order.{order}.weights')
    axis_source = frame.get(f'transition_order.{order}.axis')
    weights = np.asarray(source.require_available())
    axis = np.asarray(axis_source.require_available())
    if (weights.ndim != 1 or not weights.size or axis.shape != weights.shape
            or np.iscomplexobj(weights) or not np.all(np.isfinite(weights)) or np.any(weights < 0)
            or not np.all(np.isfinite(axis)) or np.any(axis != np.round(axis)) or np.any(np.diff(axis) != 1)):
        raise ValueError('DFT requires a finite nonnegative distribution over contiguous integer order bins')
    if source.provenance.basis != axis_source.provenance.basis or source.provenance.clock != axis_source.provenance.clock:
        raise ValueError('order distribution and axis need one basis/clock')
    metadata = {
        'order': order, 'fft_normalization': normalization, 'sample_count': len(weights),
        'input_axis_origin': int(axis[0]), 'input_axis_spacing': 1,
        'index_convention': 'DFT array index j=alpha-input_axis_origin',
        'forward_sign': 'exp(-2*pi*i*j*k/N)', 'inverse': 'numpy.fft.ifft(coefficients, norm=fft_normalization)',
        'interpretation': 'Fourier transform of order-index distribution; not a temporal frequency or automatic sonification',
    }
    coefficients = np.fft.fft(weights, norm=normalization)
    frequencies = np.fft.fftfreq(len(weights), d=1)
    identifier = frame.frame_id + f':fourier:{order}:{normalization}'
    p = source.provenance.derive(identifier, 'numpy.fft.fft_order_distribution',
        parameters=metadata, units=source.units, normalization=normalization,
        parents=(source.provenance, axis_source.provenance), source_path='transition_order.fourier.coefficients')
    fp = axis_source.provenance.derive(identifier + ':index_frequency', 'numpy.fft.fftfreq',
        parameters={'n': len(weights), 'd_order_index': 1}, units='cycles/order_index',
        normalization='none', source_path='transition_order.fourier.index_frequency')
    return FeatureFrame(identifier, (
        FeatureValue(FeatureId('transition_order.fourier.coefficients', 'order_dft_coefficients', 'vector'), coefficients, p),
        FeatureValue(FeatureId('transition_order.fourier.index_frequency', 'order_index_frequency', 'vector'), frequencies, fp),
    ), metadata)
