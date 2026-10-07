"""Read-only gauge-flow projection into resonant-excitation descriptors.

This module deliberately stops before sound generation.  It turns invariant
transport into declared excitation, release, routing, and transient quantities
that a later acoustic or electromagnetic adapter may consume.  It never
changes a ``GaugeFlowFrame``, a Hamiltonian, a density matrix, or a resonator
frequency.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from qmw.flow.gauge_transport import GaugeFlowFrame


Array = np.ndarray


def _nonnegative(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative.")
    return result


@dataclass(frozen=True)
class GaugeResonantExcitationConfig:
    """Linear calibration for a later resonant body; no frequency is present."""

    sustain_gain: float = 1.0
    release_gain: float = 1.0
    transient_gain: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "sustain_gain", _nonnegative("sustain_gain", self.sustain_gain))
        object.__setattr__(self, "release_gain", _nonnegative("release_gain", self.release_gain))
        object.__setattr__(self, "transient_gain", _nonnegative("transient_gain", self.transient_gain))


@dataclass(frozen=True)
class GaugeDirectedRoute:
    """One currently directed graph link, expressed in physical transport order."""

    edge_index: int
    source_node: int | None
    destination_node: int | None
    signed_current: float
    sustained_transport: float
    transient_strength: float


@dataclass(frozen=True)
class GaugeResonantExcitationFrame:
    """Resonant-body controls derived solely from gauge-invariant transport.

    ``node_sustained_excitation`` derives from signed net incoming current's
    positive link contributions.  ``node_energy_release`` is the analogous
    outgoing transport descriptor; it is *not* a physical damping command.
    Link transient strength is ``abs(dJ/dt)`` when temporal information is
    available.  A downstream sonic body retains authority over how any of
    these controls excite material resonance.
    """

    time: float
    source: str
    node_sustained_excitation: Array
    node_energy_release: Array
    edge_transient_strength: Array
    directed_routes: tuple[GaugeDirectedRoute, ...]
    current_derivative_available: bool
    frequency_policy: str = "fixed_resonator_frequencies_unchanged"
    provenance: str = "downstream_read_only_gauge_flow_to_resonant_excitation"


def gauge_flow_to_resonant_excitation(
    frame: GaugeFlowFrame,
    *,
    config: GaugeResonantExcitationConfig | None = None,
) -> GaugeResonantExcitationFrame:
    """Project a gauge-flow observation to resonance descriptors.

    The mapping is intentionally linear and inspectable:

    ``incoming transport -> sustained excitation``
    ``outgoing transport -> energy-release descriptor``
    ``abs(dJ/dt) -> link transient strength``
    """
    if not isinstance(frame, GaugeFlowFrame):
        raise TypeError("frame must be a GaugeFlowFrame.")
    settings = config or GaugeResonantExcitationConfig()
    current = np.asarray(frame.edge_currents, dtype=float)
    edges = np.asarray(frame.edge_indices, dtype=int)
    if current.ndim != 1 or edges.shape != (current.size, 2):
        raise ValueError("GaugeFlowFrame edge current and topology shapes are inconsistent.")
    if not np.all(np.isfinite(current)):
        raise ValueError("GaugeFlowFrame edge currents must be finite.")
    derivative = frame.current_derivative
    if derivative is None:
        transient = np.zeros_like(current)
        has_derivative = False
    else:
        derivative = np.asarray(derivative, dtype=float)
        if derivative.shape != current.shape or not np.all(np.isfinite(derivative)):
            raise ValueError("GaugeFlowFrame current_derivative must be finite and match edge currents.")
        transient = settings.transient_gain * np.abs(derivative)
        has_derivative = True

    routes: list[GaugeDirectedRoute] = []
    for index, ((left, right), signed) in enumerate(zip(edges, current)):
        if signed > 0.0:
            source, destination = int(left), int(right)
        elif signed < 0.0:
            source, destination = int(right), int(left)
        else:
            source = destination = None
        routes.append(GaugeDirectedRoute(
            edge_index=index,
            source_node=source,
            destination_node=destination,
            signed_current=float(signed),
            sustained_transport=float(abs(signed)),
            transient_strength=float(transient[index]),
        ))

    return GaugeResonantExcitationFrame(
        time=float(frame.time),
        source=frame.current_source,
        node_sustained_excitation=np.array(
            settings.sustain_gain * np.asarray(frame.incoming_strength, dtype=float), copy=True,
        ),
        node_energy_release=np.array(
            settings.release_gain * np.asarray(frame.outgoing_strength, dtype=float), copy=True,
        ),
        edge_transient_strength=np.array(transient, copy=True),
        directed_routes=tuple(routes),
        current_derivative_available=has_derivative,
    )


__all__ = [
    "GaugeDirectedRoute",
    "GaugeResonantExcitationConfig",
    "GaugeResonantExcitationFrame",
    "gauge_flow_to_resonant_excitation",
]
