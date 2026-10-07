"""Read-only Parseval descriptors for the canonical 16-level QHO.

The density matrix remains authoritative.  This module exposes two explicit
sound mappings without changing it:

``fixed_rms_basis_timbre``
    Probabilities in fixed orthonormal analysis bases become harmonic power
    shares.  Active shares may be renormalized downstream to hold carrier RMS.

``purity_to_energy``
    A unitary two-dimensional FFT of ``rho`` is power-pooled into sixteen
    harmonic bins.  The bin powers sum to ``Tr(rho**2)``, so normalization is
    deliberately omitted when mixedness is meant to control audio energy.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .schema import OscillatorFrame


Array = np.ndarray
BASIS_NAMES = ("fock", "qft", "hadamard")
EPS = 1.0e-12


def _readonly(values: object, *, dtype: object = float) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.flags.writeable = False
    return result


def _validated_density(frame: OscillatorFrame) -> Array:
    if frame.dimension != 16:
        raise ValueError("QHO Parseval mapping requires dimension 16")
    if frame.rho is None:
        raise ValueError("QHO Parseval mapping requires frame.rho")
    rho = np.asarray(frame.rho, dtype=np.complex128)
    if rho.shape != (16, 16) or not np.all(np.isfinite(rho)):
        raise ValueError("frame.rho must be a finite 16 x 16 matrix")
    if not np.allclose(rho, rho.conj().T, atol=1.0e-9):
        raise ValueError("frame.rho must be Hermitian")
    trace = complex(np.trace(rho))
    if abs(trace.imag) > 1.0e-9 or trace.real <= EPS:
        raise ValueError("frame.rho must have positive real trace")
    return rho / trace.real


def _qft_analysis(dimension: int) -> Array:
    indices = np.arange(dimension, dtype=float)
    return np.exp(
        -2j * np.pi * np.outer(indices, indices) / float(dimension)
    ) / math.sqrt(dimension)


def _hadamard_analysis(dimension: int) -> Array:
    if dimension < 1 or dimension & (dimension - 1):
        raise ValueError("Hadamard analysis requires a power-of-two dimension")
    matrix = np.ones((1, 1), dtype=float)
    while matrix.shape[0] < dimension:
        matrix = np.block([[matrix, matrix], [matrix, -matrix]])
    return matrix / math.sqrt(dimension)


def _basis_probabilities(rho: Array, analysis: Array) -> Array:
    probabilities = np.real(np.diag(analysis @ rho @ analysis.conj().T))
    probabilities = np.clip(probabilities, 0.0, None)
    total = float(np.sum(probabilities))
    if total <= EPS:
        raise ValueError("analysis basis produced zero probability")
    return probabilities / total


@dataclass(frozen=True)
class QHOParsevalDescriptorV1:
    basis_names: tuple[str, ...]
    basis_probabilities: tuple[Array, ...]
    matrix_power_bins: Array
    matrix_phase_bins: Array
    matrix_phase_reliability: Array
    trace: float
    purity: float
    matrix_power_sum: float
    parseval_residual: float
    mapping_id: str = "qmw_qho_parseval_modes_v1"
    provenance: str = "read_only_basis_probabilities_and_hilbert_schmidt_spectrum"

    def probabilities(self, basis: str) -> Array:
        try:
            return self.basis_probabilities[self.basis_names.index(str(basis))]
        except ValueError as exc:
            raise KeyError(basis) from exc


def observe_qho_parseval(frame: OscillatorFrame) -> QHOParsevalDescriptorV1:
    """Observe basis power shares and an exact purity-preserving spectrum."""

    rho = _validated_density(frame)
    identity = np.eye(16, dtype=np.complex128)
    analyses = (identity, _qft_analysis(16), _hadamard_analysis(16))
    basis_probabilities = tuple(
        _readonly(_basis_probabilities(rho, analysis)) for analysis in analyses
    )

    # ``norm='ortho'`` makes FFT2 unitary on vec(rho). Pooling each complete
    # row by squared magnitude reduces 256 complex coordinates to 16 audio
    # power bins without changing their total Hilbert--Schmidt norm.
    matrix_spectrum = np.fft.fft2(rho, norm="ortho")
    squared_magnitudes = np.abs(matrix_spectrum) ** 2
    power_bins = np.sum(squared_magnitudes, axis=1).real
    phase_phasors = np.sum(np.abs(matrix_spectrum) * matrix_spectrum, axis=1)
    phase_bins = np.angle(phase_phasors)
    phase_reliability = np.divide(
        np.abs(phase_phasors),
        power_bins,
        out=np.zeros_like(power_bins),
        where=power_bins > EPS,
    ).clip(0.0, 1.0)

    trace = float(np.trace(rho).real)
    purity = float(np.trace(rho @ rho).real)
    matrix_power_sum = float(np.sum(power_bins))
    return QHOParsevalDescriptorV1(
        basis_names=BASIS_NAMES,
        basis_probabilities=basis_probabilities,
        matrix_power_bins=_readonly(power_bins),
        matrix_phase_bins=_readonly(phase_bins),
        matrix_phase_reliability=_readonly(phase_reliability),
        trace=trace,
        purity=purity,
        matrix_power_sum=matrix_power_sum,
        parseval_residual=abs(matrix_power_sum - purity),
    )


def harmonic_amplitudes_for_rms(
    power_shares: Array,
    target_rms: float,
    *,
    normalize: bool,
) -> Array:
    """Return cosine amplitudes for a declared RMS policy.

    For distinct integer harmonics over a complete fundamental period,
    ``RMS**2 = 0.5 * sum(amplitude**2)``.  ``normalize=True`` implements the
    fixed-RMS comparison; ``False`` preserves the input norm for purity mode.
    """

    shares = np.asarray(power_shares, dtype=float)
    if shares.ndim != 1 or not np.all(np.isfinite(shares)) or np.any(shares < 0):
        raise ValueError("power_shares must be a finite nonnegative vector")
    rms = float(target_rms)
    if not math.isfinite(rms) or rms < 0.0:
        raise ValueError("target_rms must be finite and nonnegative")
    total = float(np.sum(shares))
    if normalize and total > EPS:
        shares = shares / total
    amplitudes = math.sqrt(2.0) * rms * np.sqrt(shares)
    return _readonly(amplitudes)


__all__ = [
    "BASIS_NAMES",
    "QHOParsevalDescriptorV1",
    "harmonic_amplitudes_for_rms",
    "observe_qho_parseval",
]
