"""FieldEngine: evolve -> observe -> check the physics -> project.

    engine = FieldEngine(SchrodingerModel(cfg), dt=0.002, projector=RegionProjector(...))
    frame = engine.step()            # or engine.step(ControlState(potential=V))

Each call returns a FieldFrame. Event detection (stage 5) and sonification policy
(stage 7) consume FieldFrames; nothing here knows about sound.
"""
from __future__ import annotations

import time

import numpy as np

from qmw.core.field_frame import ConservationData, Diagnostics, FieldFrame
from qmw.physics.base import ControlState


class FieldEngine:
    def __init__(self, model, dt: float, projector=None, check_energy_continuity: bool = False):
        self.model, self.dt, self.projector = model, dt, projector
        self.check_energy_continuity = check_energy_continuity
        self.state = model.initialize()
        self.t, self.steps = 0.0, 0
        self.absorbed, self.work = 0.0, 0.0
        obs = model.compute_observables(self.state)
        self.N0, self.E0 = obs.norm, obs.total_energy
        self.frame = self._frame(obs, Diagnostics())

    def _frame(self, obs, diag) -> FieldFrame:
        cons = self.model.conserved_quantities(self.state, obs)
        cons = ConservationData(norm=cons.norm, energy=cons.energy, charge=cons.charge,
                                absorbed_probability=self.absorbed, external_work=self.work)
        regions = None
        if self.projector is not None:
            sink = None
            if hasattr(self.model, "W") and np.any(self.model.W):
                sink = (2 / self.model.hbar) * self.model.W * obs.probability_density
            regions = self.projector.project(obs, sink)
        return FieldFrame(self.t, self.dt, self.steps, self.model.model_id, self.model.domain,
                          self.state, obs, cons, diag, regions)

    def step(self, controls: ControlState | None = None) -> FieldFrame:
        t0 = time.perf_counter()
        self.work += self.model.apply_controls(self.state, controls)
        before = self.state
        self.state = self.model.step(before, self.dt)
        mid = self.model.last_midpoint
        if mid is not None and hasattr(self.model, "absorption_rate"):
            self.absorbed += self.model.absorption_rate(mid) * self.dt
        self.t += self.dt
        self.steps += 1
        obs = self.model.compute_observables(self.state)
        absorbing = hasattr(self.model, "W") and np.any(self.model.W)
        diag = Diagnostics(
            norm_error=float(obs.norm + self.absorbed - self.N0),
            energy_drift=None if absorbing else float((obs.total_energy - self.E0 - self.work) / max(abs(self.E0), 1e-300)),
            probability_continuity_error=self.model.continuity_residual(before, self.state, self.dt),
            energy_continuity_error=(self.model.energy_continuity_residual(before, self.state, self.dt)
                                     if self.check_energy_continuity else None),
        )
        self.frame = self._frame(obs, diag)
        diag.step_seconds = time.perf_counter() - t0
        return self.frame
