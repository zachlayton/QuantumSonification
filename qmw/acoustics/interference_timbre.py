"""Phase-interference projection for an existing QMW modal body.

This module is downstream of authoritative state and geometry.  It never
changes ``rho``, a Hamiltonian, modal frequencies, or event identity.  Given
non-negative base modal amplitudes ``A_j``, it applies the declared two-path
prototype

    w_j = 2 A_j^2 [1 + v cos(phi + j delta)]

and exposes both final amplitudes and multiplicative gain factors.  Outside
complete cancellation, the factors preserve ``sum(A_j^2)``.  The manual and
density-coherence phase sources are deliberately named rather than conflated.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Sequence

import numpy as np

from qmw.core.transition import validated_spectrum


INTERFERENCE_TIMBRE_SCHEMA = "qmw.interference_timbre.v1"
INTERFERENCE_TIMBRE_ADDRESS = "/qmw/interference_timbre/v1/frame"
INTERFERENCE_TIMBRE_PORT = 17932
_HEADER_COUNT = 12
_MAXIMUM_PACKET_MODES = 64


def _finite(value: object, name: str) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _readonly(value: object, dtype=float) -> np.ndarray:
    result = np.array(value, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _canonical_phase(value: float) -> float:
    phase = float(np.arctan2(np.sin(value), np.cos(value)))
    return 0.0 if phase == 0.0 else phase


@dataclass(frozen=True)
class InterferenceTimbreControl:
    """One immutable downstream control frame.

    ``depth`` is a designed contrast in ``[0, 1]``.  When a density coherence
    supplies the phase, :class:`InterferenceTimbrePolicy` multiplies this
    designed maximum by the selected pair visibility.
    """

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
        if slew < 0.0 or slew > 10.0:
            raise ValueError("slew_seconds must be in [0, 10]")
        if not isinstance(self.phase_source, str) or not self.phase_source:
            raise ValueError("phase_source must be a nonempty string")
        provenance = tuple(self.provenance)
        if any(not isinstance(item, str) or not item for item in provenance):
            raise ValueError("provenance entries must be nonempty strings")
        object.__setattr__(self, "phase_radians", _canonical_phase(phase))
        object.__setattr__(self, "phase_spread_radians", _canonical_phase(spread))
        object.__setattr__(self, "depth", depth)
        object.__setattr__(self, "slew_seconds", slew)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True)
class InterferenceTimbrePolicy:
    """Resolve manual or selected-density-coherence phase into a control.

    For ``density_coherence``, the selected pair uses
    ``phase = arg(rho[row,column]) + phase_offset`` and
    ``visibility = 2 |rho[row,column]| / (rho[row,row] + rho[column,column])``.
    The resolved depth is ``policy.depth * visibility``.  This is a read-only
    two-path observer; the spread across modes remains an explicit sound map.
    """

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
        density = np.array(rho, dtype=complex, copy=True)
        if density.ndim != 2 or density.shape[0] != density.shape[1] or not density.size:
            raise ValueError("rho must be a nonempty square density matrix")
        # Reuse QMW's canonical physical-density admission; the zero H is an
        # inert validator input and no Hamiltonian result is retained.
        validated_spectrum(
            density,
            np.zeros_like(density),
            self.tolerance,
            self.tolerance,
        )
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
        phase = self.phase_offset_radians + (float(np.angle(coherence)) if has_phase else 0.0)
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
    source_id: str
    source_revision: int
    control: InterferenceTimbreControl
    mode_ids: tuple[str, ...]
    base_amplitudes: np.ndarray
    phase_offsets_radians: np.ndarray
    raw_power_weights: np.ndarray
    gain_factors: np.ndarray
    output_amplitudes: np.ndarray
    base_power: float
    interfered_power_before_normalization: float
    output_power: float
    complete_cancellation: bool
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id:
            raise ValueError("source_id must be a nonempty string")
        if type(self.source_revision) is not int or self.source_revision < 0:
            raise ValueError("source_revision must be a nonnegative integer")
        ids = tuple(self.mode_ids)
        if not ids or len(ids) > _MAXIMUM_PACKET_MODES or len(set(ids)) != len(ids):
            raise ValueError("mode_ids must contain 1 to 64 unique entries")
        if any(not isinstance(item, str) or not item for item in ids):
            raise ValueError("mode IDs must be nonempty strings")
        object.__setattr__(self, "mode_ids", ids)
        for name in (
            "base_amplitudes",
            "phase_offsets_radians",
            "raw_power_weights",
            "gain_factors",
            "output_amplitudes",
        ):
            array = _readonly(getattr(self, name))
            if array.shape != (len(ids),) or not np.all(np.isfinite(array)):
                raise ValueError(f"{name} must be a finite per-mode vector")
            object.__setattr__(self, name, array)
        for name in ("base_power", "interfered_power_before_normalization", "output_power"):
            value = _finite(getattr(self, name), name)
            if value < 0.0:
                raise ValueError(f"{name} must be nonnegative")
            object.__setattr__(self, name, value)
        if type(self.complete_cancellation) is not bool:
            raise ValueError("complete_cancellation must be boolean")
        object.__setattr__(self, "provenance", tuple(self.provenance))

    def osc_arguments(self) -> list[object]:
        digest = hashlib.sha256(json.dumps(
            self.provenance,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()).hexdigest()
        arguments: list[object] = [
            INTERFERENCE_TIMBRE_SCHEMA,
            self.source_id,
            self.source_revision,
            self.control.revision,
            len(self.mode_ids),
            self.control.phase_radians,
            self.control.phase_spread_radians,
            self.control.depth,
            self.control.slew_seconds,
            int(self.complete_cancellation),
            self.control.phase_source,
            digest,
        ]
        for mode_id, base, factor, output in zip(
            self.mode_ids,
            self.base_amplitudes,
            self.gain_factors,
            self.output_amplitudes,
        ):
            arguments.extend((mode_id, float(base), float(factor), float(output)))
        return arguments


class InterferenceTimbreProjector:
    """Pure, deterministic and dimension-independent modal projection."""

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
        if base.ndim != 1 or base.size == 0 or base.size != len(ids):
            raise ValueError("base amplitudes require one entry per nonempty mode ID")
        if not np.all(np.isfinite(base)) or np.any(base < 0.0):
            raise ValueError("base amplitudes must be finite and nonnegative")
        if len(set(ids)) != len(ids) or any(not isinstance(item, str) or not item for item in ids):
            raise ValueError("mode IDs must be unique nonempty strings")
        if type(source_revision) is not int or source_revision < 0:
            raise ValueError("source_revision must be a nonnegative integer")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source_id must be a nonempty string")

        indices = np.arange(base.size, dtype=float)
        offsets = control.phase_radians + indices * control.phase_spread_radians
        raw_factors = 2.0 * (1.0 + control.depth * np.cos(offsets))
        raw_factors = np.maximum(raw_factors, 0.0)
        base_power = float(np.dot(base, base))
        raw_weights = base * base * raw_factors
        interfered_power = float(np.sum(raw_weights))
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
        output_power = float(np.dot(output, output))
        frame_provenance = tuple(provenance) + control.provenance + (
            "qmw.interference_timbre.v1",
            "two_equal_pathways:a_j=A_j;b_j=A_j*exp(i*j*spread)",
            "power_policy:preserve_sum_base_amplitude_squared_except_complete_cancellation",
            "frequencies_and_authoritative_quantum_state_unchanged",
        )
        return InterferenceTimbreFrame(
            source_id,
            source_revision,
            control,
            ids,
            base,
            offsets,
            raw_weights,
            factors,
            output,
            base_power,
            interfered_power,
            output_power,
            bool(cancelled),
            frame_provenance,
        )


class InterferenceTimbrePacketReceiver:
    """Reference admission gate for one-datagram generic OSC frames."""

    def __init__(self) -> None:
        self.source_id: str | None = None
        self.source_revision = -1
        self.control_revision = -1
        self.latest: dict[str, object] | None = None

    def accept(self, arguments: Sequence[object]) -> dict[str, object] | None:
        try:
            args = list(arguments)
            if len(args) < _HEADER_COUNT or args[0] != INTERFERENCE_TIMBRE_SCHEMA:
                return None
            source_id = args[1]
            source_revision, control_revision, count = args[2:5]
            if not isinstance(source_id, str) or not source_id:
                return None
            if any(type(value) is not int or value < 0 for value in
                   (source_revision, control_revision, count)):
                return None
            if count < 1 or count > _MAXIMUM_PACKET_MODES:
                return None
            if len(args) != _HEADER_COUNT + 4 * count:
                return None
            if args[9] not in (0, 1):
                return None
            if any(not isinstance(args[index], str) or not args[index]
                   for index in (10, 11)):
                return None
            scalars = np.asarray(args[5:9], dtype=float)
            if not np.all(np.isfinite(scalars)) or not 0.0 <= scalars[2] <= 1.0 \
                    or not 0.0 <= scalars[3] <= 10.0:
                return None
            if self.source_id is not None and source_id != self.source_id:
                return None
            if (source_revision, control_revision) <= (
                self.source_revision,
                self.control_revision,
            ):
                return None
            entries = [args[_HEADER_COUNT + 4 * index:_HEADER_COUNT + 4 * (index + 1)]
                       for index in range(count)]
            ids = tuple(entry[0] for entry in entries)
            if any(not isinstance(item, str) or not item for item in ids) or len(set(ids)) != count:
                return None
            values = np.asarray([entry[1:] for entry in entries], dtype=float)
            if not np.all(np.isfinite(values)) or np.any(values < 0.0):
                return None
            latest = {
                "source_id": source_id,
                "source_revision": source_revision,
                "control_revision": control_revision,
                "mode_ids": ids,
                "base_amplitudes": _readonly(values[:, 0]),
                "gain_factors": _readonly(values[:, 1]),
                "output_amplitudes": _readonly(values[:, 2]),
                "phase_radians": float(scalars[0]),
                "phase_spread_radians": float(scalars[1]),
                "depth": float(scalars[2]),
                "slew_seconds": float(scalars[3]),
                "complete_cancellation": bool(args[9]),
                "phase_source": args[10],
                "provenance_digest": args[11],
            }
            self.source_id = source_id
            self.source_revision = source_revision
            self.control_revision = control_revision
            self.latest = latest
            return latest
        except (IndexError, TypeError, ValueError, OverflowError):
            return None


__all__ = [
    "INTERFERENCE_TIMBRE_ADDRESS",
    "INTERFERENCE_TIMBRE_PORT",
    "INTERFERENCE_TIMBRE_SCHEMA",
    "InterferenceTimbreControl",
    "InterferenceTimbreFrame",
    "InterferenceTimbrePacketReceiver",
    "InterferenceTimbrePolicy",
    "InterferenceTimbreProjector",
]
