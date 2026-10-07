"""Typed, auditable routing contracts for the additive V3_Matrix layer.

The matrix describes creative connections between observer, timing, control,
and acoustic adapter ports.  It deliberately is *not* a second evolution
engine: the authoritative QMW state remains an output-only FRAME source.
Only an explicitly armed INTERVENTION request may target the QMW domain, and
the request still requires a receiving gateway to commit it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math


class MatrixDomain(str, Enum):
    """The eight stable V3_Matrix navigation and routing domains."""

    TIME = "time"
    QMW = "qmw"
    GEOMETRY = "geometry"
    SOURCES = "sources"
    EXCITATION = "excitation"
    OPERATORS = "operators"
    ROUTING = "routing"
    SPACE = "space"


class PortType(str, Enum):
    """Signal semantics, rather than a claim about any particular backend."""

    AUDIO = "audio"
    CV = "cv"
    GATE = "gate"
    EVENT = "event"
    FRAME = "frame"
    INTERVENTION = "intervention"


_CONTINUOUS_TYPES = frozenset((PortType.AUDIO, PortType.CV))
_CAUSAL_TYPES = frozenset((PortType.GATE, PortType.EVENT))
VOICE_DECAY_IDS = tuple(f"voice_decay_{index + 1}" for index in range(8))


def _finite(value: float, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite.")
    return result


def _unit_interval(value: float, *, name: str) -> float:
    result = _finite(value, name=name)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1].")
    return result


def _attenuverter(value: float, *, name: str) -> float:
    result = _finite(value, name=name)
    if not -1.0 <= result <= 1.0:
        raise ValueError(f"{name} must lie in [-1, 1].")
    return result


@dataclass(frozen=True)
class MatrixPort:
    """A named, unit-declared input or output on one matrix domain."""

    identifier: str
    domain: MatrixDomain
    port_type: PortType
    direction: str
    units: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.units or not self.provenance:
            raise ValueError("identifier, units, and provenance must be nonempty.")
        if self.direction not in ("input", "output"):
            raise ValueError("direction must be 'input' or 'output'.")


@dataclass(frozen=True)
class MatrixRoute:
    """One matrix connection with its per-route modulation controls.

    Continuous routes have a bipolar base attenuverter and may receive exactly
    one assignable CV source plus a CV-depth attenuverter.  The UI may expose
    more modulation slots later, but this stable first contract makes the
    single-cell behavior explicit and testable.
    """

    source: MatrixPort
    destination: MatrixPort
    amount: float = 0.0
    cv_source: MatrixPort | None = None
    cv_amount: float = 0.0
    smoothing_seconds: float = 0.0
    feedback_delay_seconds: float | None = None
    armed: bool = False
    active: bool = False
    provenance: str = "v3_matrix_route_v1"

    def __post_init__(self) -> None:
        if self.source.direction != "output" or self.destination.direction != "input":
            raise ValueError("a matrix route must connect an output port to an input port.")
        if not self.provenance:
            raise ValueError("provenance must be nonempty.")
        if self.source.port_type is not self.destination.port_type:
            raise ValueError("source and destination port types must match exactly.")

        port_type = self.source.port_type
        smoothing = _finite(self.smoothing_seconds, name="smoothing_seconds")
        if smoothing < 0.0:
            raise ValueError("smoothing_seconds must be nonnegative.")
        object.__setattr__(self, "smoothing_seconds", smoothing)

        if port_type in _CONTINUOUS_TYPES:
            object.__setattr__(self, "amount", _attenuverter(self.amount, name="amount"))
            object.__setattr__(self, "cv_amount", _attenuverter(self.cv_amount, name="cv_amount"))
            if self.cv_source is not None:
                if self.cv_source.direction != "output" or self.cv_source.port_type is not PortType.CV:
                    raise ValueError("cv_source must be a CV output port.")
            elif self.cv_amount != 0.0:
                raise ValueError("cv_amount requires a cv_source.")
        else:
            object.__setattr__(self, "amount", _unit_interval(self.amount, name="amount"))
            if self.cv_source is not None or self.cv_amount != 0.0:
                raise ValueError("only AUDIO and CV routes accept a per-route CV input.")

        if port_type is PortType.FRAME:
            if self.destination.domain is MatrixDomain.QMW:
                raise ValueError("an authoritative QMW frame is output-only and cannot be routed back into QMW.")
            if self.armed:
                raise ValueError("read-only FRAME routes cannot be armed.")
        elif port_type is PortType.INTERVENTION:
            if self.destination.domain is not MatrixDomain.QMW:
                raise ValueError("an INTERVENTION route must terminate at the QMW gateway.")
        elif self.destination.domain is MatrixDomain.QMW:
            raise ValueError("only a declared INTERVENTION route may target the QMW domain.")
        elif self.armed:
            raise ValueError("only an INTERVENTION route may be armed.")

        delay = self.feedback_delay_seconds
        if delay is not None:
            delay = _finite(delay, name="feedback_delay_seconds")
            if port_type not in _CONTINUOUS_TYPES:
                raise ValueError("feedback delay is only valid for AUDIO or CV routes.")
            if delay <= 0.0:
                raise ValueError("feedback routes require a positive delay.")
            object.__setattr__(self, "feedback_delay_seconds", delay)

    @property
    def key(self) -> tuple[str, str]:
        return (self.source.identifier, self.destination.identifier)

    @property
    def is_feedback(self) -> bool:
        return self.feedback_delay_seconds is not None


@dataclass(frozen=True)
class MatrixSnapshot:
    """An immutable set of routes for one V3_Matrix scene or revision."""

    revision: int
    routes: tuple[MatrixRoute, ...] = field(default_factory=tuple)
    provenance: str = "v3_matrix_snapshot_v1"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if not self.provenance:
            raise ValueError("provenance must be nonempty.")
        routes = tuple(self.routes)
        keys = tuple(route.key for route in routes)
        if len(keys) != len(set(keys)):
            raise ValueError("a matrix snapshot cannot contain duplicate source/destination routes.")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "routes", routes)

    def with_route(self, route: MatrixRoute) -> "MatrixSnapshot":
        """Return a new revision with ``route`` inserted or replaced by key."""

        retained = tuple(item for item in self.routes if item.key != route.key)
        return MatrixSnapshot(revision=self.revision + 1, routes=retained + (route,), provenance=self.provenance)


def voice_decay_ports() -> tuple[MatrixPort, ...]:
    """Return the eight normalized-CV inputs that modulate voice lifetimes.

    These are downstream sound-adapter ports.  Their values are interpreted as
    octave offsets around the performer's eight manual decay settings; they do
    not change a Hamiltonian, density matrix, flow frame, or geometry frame.
    """

    return tuple(
        MatrixPort(
            identifier,
            MatrixDomain.OPERATORS,
            PortType.CV,
            "input",
            "normalized_decay_octaves",
            "v3_eight_voice_decay_adapter",
        )
        for identifier in VOICE_DECAY_IDS
    )


def route_voice_decays(
    base_seconds: tuple[float, ...] | list[float],
    source_values: dict[str, float],
    routes: tuple[MatrixRoute, ...] | list[MatrixRoute],
    *,
    modulation_range_octaves: float = 2.0,
) -> tuple[float, ...]:
    """Evaluate active CV routes into eight bounded decay parameters.

    Source values are normalized to ``[0, 1]``. Active route attenuverters are
    summed per destination, clipped to the declared octave range, and applied
    exponentially around each manual base value. Feedback routes remain legal
    only when their :class:`MatrixRoute` carries a positive explicit delay.
    """

    bases = tuple(_finite(value, name="base_seconds") for value in base_seconds)
    if len(bases) != 8:
        raise ValueError("base_seconds must contain exactly eight voice values.")
    if any(value <= 0.0 for value in bases):
        raise ValueError("base_seconds values must be positive.")
    span = _finite(modulation_range_octaves, name="modulation_range_octaves")
    if not 0.0 <= span <= 4.0:
        raise ValueError("modulation_range_octaves must lie in [0, 4].")

    destination_indices = {identifier: index for index, identifier in enumerate(VOICE_DECAY_IDS)}
    offsets = [0.0] * 8
    for route in routes:
        if not route.active:
            continue
        if route.source.port_type is not PortType.CV or route.destination.port_type is not PortType.CV:
            raise ValueError("voice decay modulation accepts CV routes only.")
        if route.destination.identifier not in destination_indices:
            continue
        if route.source.identifier not in source_values:
            raise ValueError(f"missing normalized source value for {route.source.identifier!r}.")
        value = _unit_interval(source_values[route.source.identifier], name=route.source.identifier)
        offsets[destination_indices[route.destination.identifier]] += route.amount * value * span

    return tuple(
        min(6.0, max(0.02, base * (2.0 ** min(span, max(-span, offset)))))
        for base, offset in zip(bases, offsets, strict=True)
    )


def normal_stereo_snapshot() -> MatrixSnapshot:
    """Return V3_Matrix's conservative two-channel startup scene.

    The scene carries observed QMW state to geometry read-only, admitted events
    to sound adapters, and the source body to the primary stereo bus. It has
    no feedback, cross-modulation, or intervention route.
    """

    quantum_frame = MatrixPort(
        "quantum_frame", MatrixDomain.QMW, PortType.FRAME, "output", "immutable_frame", "v3_authoritative_qmw"
    )
    geometry_observer = MatrixPort(
        "geometry_observer", MatrixDomain.GEOMETRY, PortType.FRAME, "input", "immutable_frame", "v3_relational_observer"
    )
    admitted_event = MatrixPort(
        "admitted_event", MatrixDomain.TIME, PortType.EVENT, "output", "event", "v3_temporal_admission"
    )
    excitation_event = MatrixPort(
        "excitation_event", MatrixDomain.EXCITATION, PortType.EVENT, "input", "event", "v3_sound_adapter"
    )
    source_stereo = MatrixPort(
        "source_stereo", MatrixDomain.SOURCES, PortType.AUDIO, "output", "stereo_audio", "v3_sound_adapter"
    )
    primary_stereo = MatrixPort(
        "primary_stereo_1_2", MatrixDomain.SPACE, PortType.AUDIO, "input", "stereo_audio", "v3_primary_output"
    )
    return MatrixSnapshot(
        revision=0,
        routes=(
            MatrixRoute(quantum_frame, geometry_observer, amount=1.0, active=True),
            MatrixRoute(admitted_event, excitation_event, amount=1.0, active=True),
            MatrixRoute(source_stereo, primary_stereo, amount=1.0, active=True),
        ),
        provenance="v3_matrix_normal_stereo_initialization_v1",
    )
