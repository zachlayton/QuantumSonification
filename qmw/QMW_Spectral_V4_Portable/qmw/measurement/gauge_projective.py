"""Composition seam from gauge-covariant dynamics to projective observation."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from qmw.quantum.gauge_dynamics import GaugeDynamicsEngine, GaugeDynamicsFrame
from .basis_motion import ProjectorBasisMotion
from .engine import MeasurementFrame, ProjectiveMeasurementEngine
from .projector import ProjectorBank


@dataclass(frozen=True)
class GaugeProjectiveFrame:
    revision: int
    time: float
    gauge: GaugeDynamicsFrame
    measurement: MeasurementFrame
    provenance: str = "gauge_covariant_dynamics_to_projective_measurement_v1"


class GaugeProjectiveEngine:
    """Advance one physical world and observe it through a fixed or moving PVM."""

    def __init__(
        self,
        dynamics: GaugeDynamicsEngine,
        bank: ProjectorBank | None = None,
        *,
        motion: ProjectorBasisMotion | None = None,
    ) -> None:
        if (bank is None) == (motion is None):
            raise ValueError("provide exactly one fixed bank or moving projector basis.")
        selected = bank if bank is not None else motion.bank
        if selected.dimension != dynamics.hamiltonian.shape[0]:
            raise ValueError("dynamics and projector bank must share a dimension.")
        self.dynamics = dynamics
        self.bank = bank
        self.motion = motion
        self.measurement_engine = ProjectiveMeasurementEngine()

    def observe(self, rho: object, *, revision: int, time: float) -> GaugeProjectiveFrame:
        gauge = self.dynamics.observe(rho, time=time)
        if self.motion is None:
            measurement = self.measurement_engine.observe(
                gauge.rho, self.bank, revision=revision, time=time, rho_dot=gauge.rho_dot,
            )
        else:
            measurement = self.measurement_engine.observe_motion(
                gauge.rho, self.motion, revision=revision, time=time, rho_dot=gauge.rho_dot,
            )
        return GaugeProjectiveFrame(int(revision), float(time), gauge, measurement)

    def advance(self, rho: object, *, dt: float, revision: int, time: float) -> GaugeProjectiveFrame:
        return self.observe(
            self.dynamics.advance_unitary(rho, dt), revision=revision, time=time,
        )


__all__ = ["GaugeProjectiveEngine", "GaugeProjectiveFrame"]
