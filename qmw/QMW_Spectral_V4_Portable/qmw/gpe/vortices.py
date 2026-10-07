"""Topological vortex states and phase-winding observations for 2-D GPE fields.

The winding number is calculated from wrapped phase increments around spatial
plaquettes.  It is a field-topology observable, not an arbitrary rotational
control and not an acoustic mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np


Array = np.ndarray


def _axis(name: str, values: Any) -> tuple[Array, float]:
    axis = np.asarray(values, dtype=float)
    if axis.ndim != 1 or axis.size < 4 or not np.all(np.isfinite(axis)) or np.any(np.diff(axis) <= 0.0):
        raise ValueError(f"{name} must be a finite, strictly increasing coordinate array with length >= 4.")
    spacing = float(axis[1] - axis[0])
    if not np.allclose(np.diff(axis), spacing, rtol=1.0e-9, atol=1.0e-12):
        raise ValueError("vortex observables require uniform coordinate axes.")
    return np.array(axis, copy=True), spacing


def _wrap_phase(values: Array | float) -> Array | float:
    return (np.asarray(values) + np.pi) % (2.0 * np.pi) - np.pi


@dataclass(frozen=True)
class GPEVortex:
    """One integer phase singularity found on an oriented spatial plaquette."""

    x: float
    y: float
    cell_index: tuple[int, int]
    winding: int
    phase_circulation: float


@dataclass(frozen=True)
class GPEVortexFrame:
    """Read-only vortex topology of one complex GPE field."""

    vortices: tuple[GPEVortex, ...]
    net_winding: int
    absolute_winding: int
    phase_circulation: float
    quantum_circulation: float
    provenance: str = "gpe_phase_winding_topological_observable"


def vortex_state_2d(
    x: Any,
    y: Any,
    *,
    winding: int = 1,
    center: Sequence[float] = (0.0, 0.0),
    core_width: float = 0.3,
    envelope_width: float | None = None,
) -> Array:
    """Create a localized vortex order parameter ``f(r) exp(i winding theta)``.

    A single vortex is useful for local studies but is not globally smooth on a
    periodic torus; use :func:`vortex_pair_state_2d` for a periodic net-zero
    initialization.
    """

    x_axis, _ = _axis("x", x)
    y_axis, _ = _axis("y", y)
    if int(winding) != winding:
        raise ValueError("winding must be an integer.")
    if len(center) != 2 or not all(math.isfinite(float(value)) for value in center):
        raise ValueError("center must contain two finite values.")
    if not math.isfinite(float(core_width)) or core_width <= 0.0:
        raise ValueError("core_width must be finite and greater than zero.")
    if envelope_width is not None and (not math.isfinite(float(envelope_width)) or envelope_width <= 0.0):
        raise ValueError("envelope_width must be finite and greater than zero when supplied.")
    X, Y = np.meshgrid(x_axis, y_axis, indexing="ij")
    radial = np.hypot(X - float(center[0]), Y - float(center[1]))
    amplitude = np.tanh(radial / core_width)
    if envelope_width is not None:
        amplitude *= np.exp(-0.5 * (radial / envelope_width) ** 2)
    return amplitude * np.exp(1j * int(winding) * np.arctan2(Y - float(center[1]), X - float(center[0])))


def vortex_pair_state_2d(
    x: Any,
    y: Any,
    *,
    positive_center: Sequence[float] = (-1.0, 0.0),
    negative_center: Sequence[float] = (1.0, 0.0),
    core_width: float = 0.3,
    envelope_width: float | None = None,
) -> Array:
    """Create a net-zero vortex/antivortex field suited to periodic evolution."""

    return vortex_state_2d(x, y, winding=1, center=positive_center, core_width=core_width, envelope_width=envelope_width) * vortex_state_2d(x, y, winding=-1, center=negative_center, core_width=core_width, envelope_width=None)


def detect_vortices_2d(
    psi: Any,
    x: Any,
    y: Any,
    *,
    hbar: float = 1.0,
    mass: float = 1.0,
    periodic: bool = True,
) -> GPEVortexFrame:
    """Detect integer plaquette windings from a complex field's wrapped phase.

    For an unambiguous single-cell record, initialize a vortex core inside a
    plaquette rather than exactly on a sampled grid vertex; a vertex-centered
    zero is physically shared by neighbouring plaquettes.
    """

    x_axis, dx = _axis("x", x)
    y_axis, dy = _axis("y", y)
    if not all(math.isfinite(float(value)) and float(value) > 0.0 for value in (hbar, mass)):
        raise ValueError("hbar and mass must be finite and greater than zero.")
    field = np.asarray(psi, dtype=np.complex128)
    if field.shape != (x_axis.size, y_axis.size) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be finite with shape (len(x), len(y)).")
    phase = np.angle(field)
    x_count = x_axis.size if periodic else x_axis.size - 1
    y_count = y_axis.size if periodic else y_axis.size - 1
    vortices: list[GPEVortex] = []
    for first in range(x_count):
        next_first = (first + 1) % x_axis.size
        for second in range(y_count):
            next_second = (second + 1) % y_axis.size
            loop = (
                _wrap_phase(phase[next_first, second] - phase[first, second])
                + _wrap_phase(phase[next_first, next_second] - phase[next_first, second])
                + _wrap_phase(phase[first, next_second] - phase[next_first, next_second])
                + _wrap_phase(phase[first, second] - phase[first, next_second])
            )
            winding = int(np.rint(float(loop) / (2.0 * np.pi)))
            if winding == 0:
                continue
            vortices.append(GPEVortex(
                x=float(x_axis[first] + 0.5 * dx), y=float(y_axis[second] + 0.5 * dy),
                cell_index=(first, second), winding=winding,
                phase_circulation=float(2.0 * np.pi * winding),
            ))
    net = int(sum(vortex.winding for vortex in vortices))
    absolute = int(sum(abs(vortex.winding) for vortex in vortices))
    return GPEVortexFrame(
        vortices=tuple(vortices), net_winding=net, absolute_winding=absolute,
        phase_circulation=float(2.0 * np.pi * net),
        quantum_circulation=float((hbar / mass) * 2.0 * np.pi * net),
    )


__all__ = [
    "GPEVortex", "GPEVortexFrame", "detect_vortices_2d", "vortex_pair_state_2d",
    "vortex_state_2d",
]
