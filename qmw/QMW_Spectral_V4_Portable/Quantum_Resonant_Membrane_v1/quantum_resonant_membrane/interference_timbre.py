"""Portable phase-interference timbre projection for the QRM modal body.

This module is intentionally local to the copied instrument package.  It is a
downstream observer/mapping: it reads an admitted density matrix when asked,
but never changes rho, H, geometry, modal frequencies, or event identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


def _finite(value: object, name: str) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _phase(value: float) -> float:
    result = float(np.arctan2(np.sin(value), np.cos(value)))
    return 0.0 if result == 0.0 else result


@dataclass(frozen=True)
class InterferenceTimbreControl:
    revision: int = 0
    phase_radians: float = 0.0
    phase_spread_radians: float = 0.0
    depth: float = 0.0
    slew_seconds: float = 0.08
    phase_source: str = "designed_control"
    provenance: tuple[str, ...] = ("manual downstream timbre control",)

    def __post_init__(self) -> None:
        if type(self.revision) is not int or self.revision < 0:
            raise ValueError("control revision must be a nonnegative integer")
        phase = _finite(self.phase_radians, "phase_radians")
        spread = _finite(self.phase_spread_radians, "phase_spread_radians")
        depth = _finite(self.depth, "depth")
        slew = _finite(self.slew_seconds, "slew_seconds")
        if not 0.0 <= depth <= 1.0:
            raise ValueError("depth must be in [0, 1]")
        if not 0.0 <= slew <= 10.0:
            raise ValueError("slew_seconds must be in [0, 10]")
        if not isinstance(self.phase_source, str) or not self.phase_source:
            raise ValueError("phase_source must be a nonempty string")
        provenance = tuple(self.provenance)
        if any(not isinstance(item, str) or not item for item in provenance):
            raise ValueError("provenance entries must be nonempty strings")
        object.__setattr__(self, "phase_radians", _phase(phase))
        object.__setattr__(self, "phase_spread_radians", _phase(spread))
        object.__setattr__(self, "depth", depth)
        object.__setattr__(self, "slew_seconds", slew)
        object.__setattr__(self, "provenance", provenance)


def _validate_density(rho: object, tolerance: float) -> np.ndarray:
    density = np.array(rho, dtype=complex, copy=True)
    if density.ndim != 2 or density.shape[0] != density.shape[1] or not density.size:
        raise ValueError("rho must be a nonempty square density matrix")
    if not np.all(np.isfinite(density)):
        raise ValueError("rho must be finite")
    if not np.allclose(density, density.conj().T, atol=tolerance, rtol=0.0):
        raise ValueError("rho must be Hermitian")
    if abs(complex(np.trace(density)) - 1.0) > tolerance:
        raise ValueError("rho must have unit trace")
    if float(np.min(np.linalg.eigvalsh(density).real)) < -tolerance:
        raise ValueError("rho must be positive semidefinite")
    return density


@dataclass(frozen=True)
class InterferenceTimbrePolicy:
    revision: int = 0
    phase_offset_radians: float = 0.0
    phase_spread_radians: float = 0.0
    depth: float = 0.0
    slew_seconds: float = 0.08
    source_kind: str = "manual"
    coherence_row: int = 0
    coherence_column: int = 1
    tolerance: float = 1.0e-10

    def __post_init__(self) -> None:
        InterferenceTimbreControl(
            self.revision,
            self.phase_offset_radians,
            self.phase_spread_radians,
            self.depth,
            self.slew_seconds,
        )
        if self.source_kind not in {"manual", "density_coherence"}:
            raise ValueError("source_kind must be manual or density_coherence")
        for name in ("coherence_row", "coherence_column"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.coherence_row == self.coherence_column:
            raise ValueError("density coherence requires two distinct indices")
        tolerance = _finite(self.tolerance, "tolerance")
        if tolerance <= 0.0:
            raise ValueError("tolerance must be positive")
        object.__setattr__(self, "tolerance", tolerance)

    def resolve(self, rho: object | None = None) -> InterferenceTimbreControl:
        if self.source_kind == "manual":
            return InterferenceTimbreControl(
                self.revision,
                self.phase_offset_radians,
                self.phase_spread_radians,
                self.depth,
                self.slew_seconds,
                "designed_control",
                ("manual downstream timbre control",),
            )
        if rho is None:
            raise ValueError("density_coherence source requires rho")
        density = _validate_density(rho, self.tolerance)
        row, column = self.coherence_row, self.coherence_column
        if row >= density.shape[0] or column >= density.shape[0]:
            raise ValueError("coherence pair is outside rho")
        coherence = complex(density[row, column])
        pair_population = float(density[row, row].real + density[column, column].real)
        visibility = 0.0 if pair_population <= self.tolerance else min(
            1.0,
            max(0.0, 2.0 * abs(coherence) / pair_population),
        )
        has_phase = abs(coherence) > self.tolerance
        phase = self.phase_offset_radians + (
            float(np.angle(coherence)) if has_phase else 0.0
        )
        return InterferenceTimbreControl(
            self.revision,
            phase,
            self.phase_spread_radians,
            self.depth * visibility,
            self.slew_seconds,
            f"rho[{row},{column}]" if has_phase else f"rho[{row},{column}]:absent",
            (
                "density_coherence",
                "phase observer is read-only; modal spread remains a designed sonification mapping",
                f"rho_pair:{row},{column};pair_visibility:{visibility:.17g};"
                f"designed_depth:{self.depth:.17g}",
            ),
        )


@dataclass(frozen=True)
class InterferenceTimbreFrame:
    gain_factors: np.ndarray
    output_amplitudes: np.ndarray
    base_power: float
    output_power: float
    complete_cancellation: bool
    provenance: tuple[str, ...]


class InterferenceTimbreProjector:
    """Project two-path relative phase into power-normalized modal gains."""

    def __init__(self, *, cancellation_tolerance: float = 1.0e-15) -> None:
        tolerance = _finite(cancellation_tolerance, "cancellation_tolerance")
        if tolerance <= 0.0:
            raise ValueError("cancellation_tolerance must be positive")
        self.cancellation_tolerance = tolerance

    def process(
        self,
        *,
        base_amplitudes: Sequence[float] | np.ndarray,
        mode_ids: Sequence[str],
        source_id: str,
        source_revision: int,
        control: InterferenceTimbreControl,
        provenance: Sequence[str] = (),
    ) -> InterferenceTimbreFrame:
        base = np.array(base_amplitudes, dtype=float, copy=True)
        ids = tuple(mode_ids)
        if base.ndim != 1 or not 1 <= base.size <= 64 or base.size != len(ids):
            raise ValueError("base amplitudes require 1 to 64 mode IDs")
        if not np.all(np.isfinite(base)) or np.any(base < 0.0):
            raise ValueError("base amplitudes must be finite and nonnegative")
        if len(set(ids)) != len(ids) or any(not isinstance(item, str) or not item for item in ids):
            raise ValueError("mode IDs must be unique nonempty strings")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source_id must be a nonempty string")
        if type(source_revision) is not int or source_revision < 0:
            raise ValueError("source_revision must be a nonnegative integer")

        offsets = control.phase_radians + np.arange(base.size) * control.phase_spread_radians
        raw_factors = np.maximum(
            2.0 * (1.0 + control.depth * np.cos(offsets)),
            0.0,
        )
        base_power = float(np.dot(base, base))
        interfered_power = float(np.dot(base * base, raw_factors))
        if control.depth == 0.0:
            factors = np.ones_like(base)
            output = base.copy()
            cancelled = base_power <= self.cancellation_tolerance
        elif (
            base_power <= self.cancellation_tolerance
            or interfered_power <= self.cancellation_tolerance * max(1.0, base_power)
        ):
            factors = np.zeros_like(base)
            output = np.zeros_like(base)
            cancelled = True
        else:
            factors = np.sqrt(raw_factors * (base_power / interfered_power))
            output = base * factors
            cancelled = False
        factors.setflags(write=False)
        output.setflags(write=False)
        return InterferenceTimbreFrame(
            factors,
            output,
            base_power,
            float(np.dot(output, output)),
            bool(cancelled),
            tuple(provenance) + control.provenance + (
                "qmw.interference_timbre.v1",
                "two_equal_pathways:a_j=A_j;b_j=A_j*exp(i*j*spread)",
                "power_policy:preserve_sum_base_amplitude_squared_except_complete_cancellation",
                "frequencies_and_authoritative_quantum_state_unchanged",
            ),
        )
