"""A derived discrete boundary Hilbert observer for the V3 resonant field.

This is the ordinary signal/geometric Hilbert transform on a sampled periodic
boundary.  It is not a Hilbert-space transform and its phase-current-like
diagnostic is not a quantum probability current.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import AcousticFieldFrame, GeometryBoundaryFrame


_EPS = 1.0e-10


def _provenance(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("provenance must be a nonempty string.")
    return value


def _readonly(values: object, *, dtype: object) -> np.ndarray:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class BoundaryHilbertFrame:
    """One complex boundary-field observation from a real periodic field."""

    revision: int
    time: float
    field_revision: int
    boundary_revision: int
    boundary_field: np.ndarray
    analytic_field: np.ndarray
    amplitude: np.ndarray
    phase: np.ndarray
    phase_gradient: np.ndarray
    circulation: np.ndarray
    winding_number: float
    provenance: str = "derived_boundary_hilbert_conjugate_v1_not_quantum_current"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if not math.isfinite(float(self.time)):
            raise ValueError("time must be finite.")
        if int(self.field_revision) != self.field_revision or self.field_revision < 0:
            raise ValueError("field_revision must be a nonnegative integer.")
        if int(self.boundary_revision) != self.boundary_revision or self.boundary_revision < 0:
            raise ValueError("boundary_revision must be a nonnegative integer.")
        boundary = _readonly(self.boundary_field, dtype=float)
        analytic = _readonly(self.analytic_field, dtype=np.complex128)
        amplitude = _readonly(self.amplitude, dtype=float)
        phase = _readonly(self.phase, dtype=float)
        gradient = _readonly(self.phase_gradient, dtype=float)
        circulation = _readonly(self.circulation, dtype=float)
        if boundary.ndim != 1 or boundary.size < 3:
            raise ValueError("boundary fields require at least three samples.")
        if any(value.shape != boundary.shape or not np.all(np.isfinite(value)) for value in (analytic, amplitude, phase, gradient, circulation)):
            raise ValueError("boundary observations must be finite, equally sized vectors.")
        if not np.allclose(analytic.real, boundary, atol=1.0e-9, rtol=0.0):
            raise ValueError("analytic_field real part must preserve boundary_field.")
        if np.any(amplitude < 0.0) or not math.isfinite(float(self.winding_number)):
            raise ValueError("amplitude and winding number must be finite.")
        for name, value in (("boundary_field", boundary), ("analytic_field", analytic), ("amplitude", amplitude), ("phase", phase), ("phase_gradient", gradient), ("circulation", circulation)):
            object.__setattr__(self, name, value)
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "time", float(self.time))
        object.__setattr__(self, "field_revision", int(self.field_revision))
        object.__setattr__(self, "boundary_revision", int(self.boundary_revision))
        object.__setattr__(self, "winding_number", float(self.winding_number))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


def synthesize_boundary_field(modal_coefficients: object, boundary_basis: object) -> np.ndarray:
    """Synthesize a real boundary field from declared modal coefficients/basis.

    The basis is deliberately supplied by the geometry layer; this utility does
    not imply that a computational basis is a physical boundary.
    """

    coefficients = np.asarray(modal_coefficients, dtype=np.complex128)
    basis = np.asarray(boundary_basis, dtype=float)
    if coefficients.ndim != 1 or basis.ndim != 2 or basis.shape[1] != coefficients.size or basis.shape[0] < 3:
        raise ValueError("boundary_basis must be samples-by-modes matching modal_coefficients.")
    if not np.all(np.isfinite(coefficients)) or not np.all(np.isfinite(basis)):
        raise ValueError("modal coefficients and boundary basis must be finite.")
    return np.real(basis @ coefficients)


def _analytic_mask(size: int) -> np.ndarray:
    mask = np.zeros(size, dtype=float)
    mask[0] = 1.0
    if size % 2 == 0:
        mask[size // 2] = 1.0
        mask[1:size // 2] = 2.0
    else:
        mask[1:(size + 1) // 2] = 2.0
    return mask


def observe_boundary_hilbert_field(
    boundary_field: object,
    *,
    revision: int,
    time: float,
    field_revision: int,
    boundary_revision: int,
) -> BoundaryHilbertFrame:
    """Produce ``q + i H[q]`` and declared boundary phase diagnostics."""

    field = np.asarray(boundary_field, dtype=float)
    if field.ndim != 1 or field.size < 3 or not np.all(np.isfinite(field)):
        raise ValueError("boundary_field must be a finite one-dimensional field with >= 3 samples.")
    analytic = np.fft.ifft(np.fft.fft(field) * _analytic_mask(field.size))
    amplitude = np.abs(analytic)
    phase = np.unwrap(np.angle(analytic))
    step = (2.0 * np.pi) / field.size
    phase_gradient = np.gradient(phase, step, edge_order=1)
    circulation = amplitude * amplitude * phase_gradient
    # Exclude a contour containing a nodal zero: phase winding is then not a
    # stable topological diagnostic.  Summing the cyclic local increments,
    # including the last-to-first edge, closes a sampled contour exactly.
    winding = 0.0 if float(np.min(amplitude)) <= _EPS else float(
        np.sum(np.angle(np.roll(analytic, -1) * np.conj(analytic))) / (2.0 * np.pi)
    )
    return BoundaryHilbertFrame(
        revision=revision,
        time=time,
        field_revision=field_revision,
        boundary_revision=boundary_revision,
        boundary_field=field,
        analytic_field=analytic,
        amplitude=amplitude,
        phase=phase,
        phase_gradient=phase_gradient,
        circulation=circulation,
        winding_number=winding,
    )


def observe_acoustic_boundary_hilbert(
    field: AcousticFieldFrame,
    boundary: GeometryBoundaryFrame,
    *,
    revision: int | None = None,
) -> BoundaryHilbertFrame:
    """Evaluate a declared field boundary, then observe its Hilbert conjugate."""

    if not isinstance(field, AcousticFieldFrame):
        raise TypeError("field must be an AcousticFieldFrame.")
    if not isinstance(boundary, GeometryBoundaryFrame):
        raise TypeError("boundary must be a GeometryBoundaryFrame.")
    if field.mode_ids != boundary.mode_ids:
        raise ValueError("field and boundary must use the same stable mode ordering.")
    if not math.isclose(field.time, boundary.time, abs_tol=1.0e-12, rel_tol=0.0):
        raise ValueError("field and boundary must have the same observation time.")
    return observe_boundary_hilbert_field(
        synthesize_boundary_field(field.modal_coefficients, boundary.boundary_basis),
        revision=field.revision if revision is None else revision,
        time=field.time,
        field_revision=field.revision,
        boundary_revision=boundary.revision,
    )


__all__ = [
    "BoundaryHilbertFrame", "observe_acoustic_boundary_hilbert",
    "observe_boundary_hilbert_field", "synthesize_boundary_field",
]
