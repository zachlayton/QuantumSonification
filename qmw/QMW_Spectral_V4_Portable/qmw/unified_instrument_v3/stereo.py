"""Field-first virtual M/S observation for QMW Unified Instrument V3."""

from __future__ import annotations

import math

import numpy as np

from .frames import AcousticFieldFrame, MODE_COUNT, StereoObservationFrame


_EPS = 1.0e-12


def _receiver(values: object, *, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.complex128)
    if result.shape != (MODE_COUNT,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite complex 20-vector.")
    return result


def observe_mid_side_stereo(
    field: AcousticFieldFrame,
    *,
    even_receiver: object,
    odd_receiver: object,
    revision: int | None = None,
    receiver_label: str = "virtual_even_odd_receivers_v1",
) -> StereoObservationFrame:
    """Project a field through declared even/odd receivers.

    The convention is ``M=<R_even,Psi>``, ``S=<R_odd,Psi>``, and
    ``L=M+S, R=M-S``.  This is an observation of the complete complex field,
    not independent mode panning or an audio-to-state feedback route.
    """

    if not isinstance(field, AcousticFieldFrame):
        raise TypeError("field must be an AcousticFieldFrame.")
    even = _receiver(even_receiver, name="even_receiver")
    odd = _receiver(odd_receiver, name="odd_receiver")
    mid = complex(np.vdot(even, field.modal_coefficients))
    side = complex(np.vdot(odd, field.modal_coefficients))
    left, right = mid + side, mid - side
    denominator = abs(left) * abs(right)
    correlation = 1.0 if denominator <= _EPS else float(np.clip(np.real(left * np.conj(right)) / denominator, -1.0, 1.0))
    width = float(abs(side) / max(abs(mid) + abs(side), _EPS))
    return StereoObservationFrame(
        revision=field.revision if revision is None else revision,
        time=field.time,
        field_revision=field.revision,
        receiver_label=receiver_label,
        mid=mid,
        side=side,
        left=left,
        right=right,
        interchannel_correlation=correlation,
        width=width,
    )


__all__ = ["observe_mid_side_stereo"]
