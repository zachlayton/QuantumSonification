"""Explicit matrix views, wavetable normalization, and stationary Fourier audio.

The 16x16 complex matrix is primary. Flattening is reversible; real encodings
are named lossy views. A view becomes a table only through ``normalize`` and
becomes an audio interpretation only after SonificationRouter admission.

Playback evaluates a finite Fourier series with |k| below the table Nyquist
and |k*f0| strictly below the output Nyquist. This covers a fixed table and
constant frequency. Abrupt table/phase/frequency modulation needs an additional
declared strategy. Peak table normalization is separate from audio gain and
does not bound every interpolated value; Fourier overshoot/headroom is exposed.
"""
from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

import numpy as np

from qmw.fields.quantum_matrix_field import QuantumMatrixField
from qmw.transforms.manifold_spectral_transform import ManifoldSpectralTransform

from .contracts import ClockStamp, FeatureFrame, FeatureId, FeatureValue, finite, nonempty, plain


VERSION = "1"
FLATTENING = "k=16*m+n; C row-major"
_ENCODINGS = frozenset({"magnitude", "real_bipolar", "phase_cos"})
_MODES = _ENCODINGS | {"row_bank", "column_bank", "fft2"}
_SCOPE = "stationary waveform and constant frequency; no abrupt modulation guarantee"


def _identity(source, operation, parameters):
    digest = hashlib.sha256(json.dumps(plain({"source": source.provenance.digest,
        "operation": operation, "version": VERSION, "parameters": parameters}),
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return f"{source.provenance.record_id}:{operation}:{digest}"


class AudioProjection256:
    def __init__(self, *, phase_epsilon=0., max_samples=1_000_000):
        epsilon = finite(phase_epsilon, "phase_epsilon", minimum=0)
        if isinstance(max_samples, bool) or not isinstance(max_samples, int) or not 1 <= max_samples <= 1_000_000:
            raise ValueError("max_samples must be an integer in [1,1000000]")
        self.configuration = MappingProxyType(dict(phase_epsilon=epsilon, max_samples=max_samples))

    @staticmethod
    def _matrix(source):
        if not isinstance(source, FeatureValue) or source.id.kind != "matrix":
            raise ValueError("a typed 16x16 complex matrix feature is required")
        matrix = np.asarray(source.require_available())
        if (matrix.shape != (16, 16) or matrix.dtype.kind not in "iufc"
                or not np.all(np.isfinite(matrix)) or source.provenance.basis.dimension != 16):
            raise ValueError("a finite 16x16 matrix and matching source basis are required")
        return QuantumMatrixField(matrix)

    def flatten(self, source: FeatureValue) -> FeatureValue:
        field = self._matrix(source)
        params = {"flattening": FLATTENING, "original_feature": source.id.to_dict(),
                  "original_shape": (16, 16), "reuse": "QuantumMatrixField.flatten",
                  "source_uncertainty": source.uncertainty}
        p = source.provenance.derive(_identity(source, "complex_flatten", params),
            "QuantumMatrixField.flatten", VERSION, params, units=source.units,
            normalization="none", source_path="audio_projection.buffer256")
        return FeatureValue(FeatureId("audio_projection.buffer256", "complex_matrix_buffer", "vector"),
                            field.buffer, p)

    def unflatten(self, buffer: FeatureValue) -> FeatureValue:
        if (not isinstance(buffer, FeatureValue) or buffer.id.quantity != "complex_matrix_buffer"
                or buffer.id.kind != "vector"):
            raise ValueError("a declared reversible complex buffer is required")
        values = np.asarray(buffer.require_available())
        original = buffer.provenance.parameters.get("original_feature")
        if (values.shape != (256,) or values.dtype.kind not in "iufc"
                or buffer.provenance.parameters.get("flattening") != FLATTENING or original is None):
            raise ValueError("buffer must retain 256 values and the explicit flattening convention")
        p = buffer.provenance.derive(_identity(buffer, "complex_unflatten", {}),
            "QuantumMatrixField.unflatten", VERSION, {"flattening": FLATTENING, "dimension": 16},
            units=buffer.units, normalization="none", source_path="audio_projection.restored_matrix")
        return FeatureValue(FeatureId("audio_projection.restored_matrix", original["quantity"], "matrix"),
                            QuantumMatrixField.unflatten(values, 16), p)

    def _encode(self, matrix, encoding):
        mask = np.abs(matrix) > self.configuration["phase_epsilon"]
        if encoding == "magnitude":
            return np.abs(matrix), None
        if encoding == "real_bipolar":
            return matrix.real, None
        return np.where(mask, np.cos(np.angle(matrix)), 0.), mask

    def project(self, source: FeatureValue, *, mode="magnitude", encoding=None,
                frame_id=None) -> FeatureFrame:
        field = self._matrix(source)
        if mode not in _MODES:
            raise ValueError("unknown matrix projection mode")
        if mode in _ENCODINGS and encoding is not None:
            raise ValueError("a direct projection mode already declares its encoding")
        if mode in ("row_bank", "column_bank") and encoding is None:
            raise ValueError("row/column banks require an explicit real encoding")
        if encoding is not None and encoding not in _ENCODINGS:
            raise ValueError("unknown real matrix encoding")
        buffer = self.flatten(source)
        params = {"mode": mode, "encoding": encoding, "flattening": FLATTENING,
                  "phase_epsilon": self.configuration["phase_epsilon"],
                  "phase_epsilon_units": source.units,
                  "zero_phase_policy": "mask to zero; no signal at zero magnitude"}
        frames = [source, buffer]
        parent = buffer.provenance
        matrix = field.complex_matrix
        if mode == "fft2":
            matrix = ManifoldSpectralTransform.fft2(matrix, norm="ortho", shift=False)
            parent = source.provenance.derive(_identity(source, "fft2", {}),
                "ManifoldSpectralTransform.fft2", VERSION,
                {"norm": "ortho", "shift": False, "axes": (0, 1),
                 "source_uncertainty": source.uncertainty,
                 "interpretation": "matrix-index Fourier view; no physical energy/frequency inference"},
                units=source.units, normalization="unitary_fft2")
            if encoding is not None:
                frames.append(FeatureValue(FeatureId("audio_projection.fft2_complex", "complex_spectral_view", "matrix"),
                                           matrix, parent))
        selected = mode if mode in _ENCODINGS else encoding
        mask = None
        if selected is None:
            values, quantity, units, kind = matrix, "complex_spectral_view", source.units, "matrix"
        else:
            values, mask = self._encode(matrix, selected)
            units = "1" if selected == "phase_cos" else source.units
            quantity = "matrix_audio_view"
            if mode in ("row_bank", "column_bank"):
                params["bank_axis"] = "row_m" if mode == "row_bank" else "column_n"
                params["table_length"] = 16
                params["table_count"] = 16
                if mode == "column_bank":
                    values = values.T
                    if mask is not None:
                        mask = mask.T
                kind = "matrix"
            else:
                values = QuantumMatrixField.flatten(values)
                if mask is not None:
                    mask = QuantumMatrixField.flatten(mask)
                kind = "vector"
                params.update(table_length=256, table_count=1)
        params["selected_encoding"] = selected
        ident = frame_id or _identity(source, "matrix_view", params)
        nonempty(ident, "frame_id")
        p = parent.derive(ident+":raw", "declared_matrix_view", VERSION, params,
            units=units, normalization="none", source_path="audio_projection.raw")
        frames.append(FeatureValue(FeatureId("audio_projection.raw", quantity, kind), values, p))
        if mask is not None:
            mask_p = parent.derive(ident+":phase_valid", "magnitude_phase_validity", VERSION,
                params, units="1", normalization="none", source_path="audio_projection.phase_valid")
            frames.append(FeatureValue(FeatureId("audio_projection.phase_valid", "phase_valid", kind), mask, mask_p))
        return FeatureFrame(ident, tuple(frames), {"mode": mode, "complex_matrix_primary": source.id.to_dict(),
            "audio_table_created": False, "physical_evolution": False})

    def normalize(self, view: FeatureValue, *, remove_dc=False, peak_scope="global",
                  frame_id=None) -> FeatureFrame:
        if not isinstance(view, FeatureValue) or view.id.quantity != "matrix_audio_view":
            raise ValueError("normalization requires an explicitly selected real audio view")
        values = np.asarray(view.require_available())
        if (values.shape not in ((256,), (16, 16)) or values.dtype.kind not in "iuf"
                or not np.all(np.isfinite(values))):
            raise ValueError("normalization requires a finite real audio view of length 256 or a 16x16 bank")
        if not isinstance(remove_dc, bool) or peak_scope not in ("global", "per_table"):
            raise ValueError("remove_dc must be Boolean and peak_scope global or per_table")
        values = values.astype(float, copy=False)
        # Scale before the mean to protect valid large/small source magnitudes.
        base = float(np.max(np.abs(values)))
        scaled = values/base if base else np.zeros_like(values)
        dc_scaled = np.mean(scaled, axis=-1, keepdims=True) if remove_dc else np.zeros(scaled.shape[:-1]+(1,))
        centered = scaled-dc_scaled
        peak_scaled = np.max(np.abs(centered), axis=-1, keepdims=True) if peak_scope == "per_table" else np.max(np.abs(centered))
        normalized = np.divide(centered, peak_scaled, out=np.zeros_like(centered), where=peak_scaled != 0)
        with np.errstate(over="ignore", invalid="ignore"):
            denominator = np.asarray(peak_scaled)*base
            dc = dc_scaled*base
        if not np.all(np.isfinite(denominator)) or not np.all(np.isfinite(dc)):
            raise ValueError("normalization calibration exceeds finite source units; rescale explicitly upstream")
        params = {"remove_dc": remove_dc, "peak_scope": peak_scope,
            "dc_removed": dc.squeeze().item() if dc.size == 1 else dc.squeeze(),
            "normalization_denominator": denominator.squeeze().item() if denominator.size == 1 else denominator.squeeze(),
            "denominator_units": view.units, "audio_gain_applied": False,
            "zero_policy": "exact silence", "normalization": "peak after optional per-table DC removal",
            "interpolation_peak_limit": "table peak only; Fourier interpolation may overshoot"}
        ident = frame_id or _identity(view, "audio_table_normalization", params)
        nonempty(ident, "frame_id")
        p = view.provenance.derive(ident+":table", "audio_table_peak_normalization", VERSION, params,
            units="1", normalization="explicit_audio_table_peak", source_path="audio_projection.table",
            evidence="musical_mapping")
        table = FeatureValue(FeatureId("audio_projection.table", "normalized_wavetable" if values.ndim == 1 else "normalized_wavetable_bank", view.id.kind),
                             normalized, p)
        return FeatureFrame(ident, (view, table), {"audio_gain_applied": False, "remove_dc": remove_dc,
                                                 "peak_scope": peak_scope})

    @staticmethod
    def _routed_table(table):
        if (not isinstance(table, FeatureValue) or table.id.path != "audio.wavetable"
                or table.id.quantity != "musical.audio.wavetable"
                or table.provenance.parameters.get("destination") != "audio.wavetable"
                or table.provenance.operation != "identity" or not table.provenance.parents):
            raise ValueError("audio interpretation requires SonificationRouter identity admission to audio.wavetable")
        values = np.asarray(table.require_available())
        if (table.units != "1" or values.shape not in ((256,), (16, 16)) or values.dtype.kind not in "iuf"
                or not np.all(np.isfinite(values)) or np.max(np.abs(values)) > 1+1e-12):
            raise ValueError("routed table must be a finite normalized real vector or bank")
        if table.provenance.parents[0].operation != "audio_table_peak_normalization":
            raise ValueError("SonificationRouter input must retain explicit audio table normalization")
        return values

    @staticmethod
    def _clock_parameters(fundamental_hz, sample_rate):
        fundamental = finite(fundamental_hz, "fundamental_hz")
        rate = finite(sample_rate, "sample_rate")
        if rate <= 0 or not 0 < abs(fundamental) < rate/2:
            raise ValueError("require positive sample_rate and 0 < abs(fundamental_hz) < sample_rate/2")
        return fundamental, rate

    def play(self, table: FeatureValue, *, fundamental_hz, sample_rate, sample_count,
             initial_phase=0., frame_id=None) -> FeatureFrame:
        """Return offline samples for one constant-frequency periodic table/bank."""
        fundamental, rate = self._clock_parameters(fundamental_hz, sample_rate)
        if (isinstance(sample_count, (bool, np.bool_)) or not isinstance(sample_count, (int, np.integer))
                or not 1 <= sample_count <= self.configuration["max_samples"]):
            raise ValueError("sample_count exceeds declared positive integer bounds")
        initial = finite(initial_phase, "initial_phase")
        # Reduce before adding to avoid overflow for a large finite cycle origin.
        phases = (initial % 1) + np.arange(sample_count)*(fundamental/rate)
        params = {"sampling": "constant_frequency", "initial_phase_cycles": initial,
                  "phase_formula": "(initial_phase mod 1) + sample_index*f0/sample_rate",
                  "sample_count": int(sample_count)}
        return self._sample(table, phases, fundamental, rate, params, frame_id)

    def sample_periodic(self, table: FeatureValue, phases_cycles, *, fundamental_hz,
                        sample_rate, frame_id=None) -> FeatureFrame:
        """Inspect periodic interpolation at explicit cycle coordinates.

        The declared f0 selects the coefficient bandlimit. Arbitrary phase
        sequences are not claimed to be alias-free playback trajectories.
        """
        fundamental, rate = self._clock_parameters(fundamental_hz, sample_rate)
        phases = np.asarray(phases_cycles)
        if (phases.ndim != 1 or phases.dtype.kind not in "iuf" or not phases.size
                or phases.size > self.configuration["max_samples"] or not np.all(np.isfinite(phases))):
            raise ValueError("phase coordinates must be a bounded finite real vector in cycles")
        params = {"sampling": "explicit_cycle_coordinates", "phases_cycles": phases,
                  "sample_count": int(phases.size), "trajectory_antialias_guarantee": False}
        return self._sample(table, phases, fundamental, rate, params, frame_id)

    def _sample(self, table, phases, fundamental, rate, sampling, frame_id):
        values = self._routed_table(table)
        length = values.shape[-1]
        harmonics = np.rint(np.fft.fftfreq(length, d=1/length)).astype(int)
        full = np.fft.fft(values, axis=-1)/length
        retained = (np.abs(harmonics) < length/2) & (np.abs(harmonics)*abs(fundamental) < rate/2)
        selected = harmonics[retained]
        coefficients = full[..., retained]
        excluded_nyquist = np.abs(full[..., length//2])
        nyquist_value = float(excluded_nyquist) if np.ndim(excluded_nyquist) == 0 else excluded_nyquist
        params = sampling | {"fundamental_hz": fundamental, "sample_rate_hz": rate,
            "table_length": length, "retained_harmonics": selected,
            "harmonic_policy": "abs(k)<table_length/2 and abs(k*f0)<sample_rate/2",
            "table_nyquist_policy": "excluded", "excluded_table_nyquist_coefficient": nyquist_value,
            "coefficient_normalization": "FFT(table)/table_length", "antialias_scope": _SCOPE,
            "audio_gain_applied": False}
        ident = frame_id or _identity(table, "stationary_fourier_audio", params)
        nonempty(ident, "frame_id")
        clock = ClockStamp(0., "sample", "audio", "buffer_relative_sample_index", ident)
        coefficient_p = table.provenance.derive(ident+":coefficients", "finite_fourier_bandlimit", VERSION,
            params, units="1", normalization="FFT_divide_table_length",
            source_path="audio_projection.fourier_coefficients", clock=clock, backend="numpy",
            evidence="musical_mapping")
        coordinate_p = table.provenance.derive(ident+":coordinates", "declared_audio_phase_coordinates", VERSION,
            sampling | {"fundamental_hz": fundamental, "sample_rate_hz": rate}, units="cycle",
            normalization="periodic_modulo_one", clock=clock, backend="numpy", evidence="musical_mapping")
        samples = np.zeros(values.shape[:-1]+(len(phases),), float)
        # Bounded intermediate memory: never allocate harmonics times all samples.
        for start in range(0, len(phases), 4096):
            block = np.remainder(phases[start:start+4096], 1)
            kernel = np.exp(2j*np.pi*np.outer(selected, block))
            samples[..., start:start+len(block)] = np.real(coefficients @ kernel)
        sample_p = coefficient_p.derive(ident+":samples", "periodic_finite_fourier_interpolation", VERSION,
            params | {"observed_sample_peak": float(np.max(np.abs(samples))),
                      "coefficient_l1_peak_bound": np.sum(np.abs(coefficients), axis=-1),
                      "clipping": "none; amplitude headroom belongs to a separate declared gain stage"},
            units="1", normalization="none", parents=(coefficient_p, coordinate_p),
            source_path="audio_projection.samples", clock=clock, backend="numpy", evidence="offline_audio_projection")
        kind = "vector" if values.ndim == 1 else "matrix"
        features = (
            table,
            FeatureValue(FeatureId("audio_projection.harmonics", "retained_harmonic_indices", "vector"),
                         selected, coefficient_p.derive(ident+":harmonics", "harmonic_index_selection", units="index")),
            FeatureValue(FeatureId("audio_projection.fourier_coefficients", "fourier_coefficients", kind), coefficients, coefficient_p),
            FeatureValue(FeatureId("audio_projection.samples", "audio_samples", kind), samples, sample_p),
        )
        return FeatureFrame(ident, features, {"antialias_scope": _SCOPE, "sampling": sampling["sampling"],
            "table_nyquist_policy": "excluded", "excluded_table_nyquist_coefficient": nyquist_value,
            "audio_gain_applied": False, "sample_rate_hz": rate, "sample_count": len(phases),
            "table_length": length, "audio_device_opened": False})


__all__ = ["AudioProjection256", "FLATTENING"]
