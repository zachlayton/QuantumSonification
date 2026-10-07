"""Prepared two-packet phase-collision initial conditions for the 2-D GPE."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qmw.qmw_gpe import GPEConfig, GPEEngine, GPEState


@dataclass(frozen=True)
class PhaseCollisionParameters:
    """Physical preparation parameters; phase is in radians."""
    phase: float = 0.0
    interaction: float = 0.3
    separation: float = 4.0
    width: float = 0.9
    incident_wavenumber: float = 1.25


class PhaseCollisionExperiment2D:
    """Restartable field preparation for ``psi_A + exp(i theta) psi_B``."""
    def __init__(self, *, size: int = 96, spacing: float = 0.15, parameters: PhaseCollisionParameters | None = None) -> None:
        if int(size) < 8 or float(spacing) <= 0.0:
            raise ValueError("size must be >= 8 and spacing must be positive.")
        self.size, self.spacing = int(size), float(spacing)
        self.axis = (np.arange(self.size) - self.size // 2) * self.spacing
        self.parameters = parameters or PhaseCollisionParameters()
        self.engine: GPEEngine
        self.reset(self.parameters)

    def reset(self, parameters: PhaseCollisionParameters | None = None) -> GPEState:
        """Prepare a new t=0 field; this is not an audio-feedback action."""
        self.parameters = parameters or self.parameters
        X, Y = np.meshgrid(self.axis, self.axis, indexing="ij")
        offset = self.parameters.separation / 2.0
        width = self.parameters.width
        left = np.exp(-((X + offset) ** 2 + Y ** 2) / width)
        right = np.exp(-((X - offset) ** 2 + Y ** 2) / width)
        # Equal/opposite phase gradients give the separated packets literal
        # inward probability current, so this is a collision rather than two
        # stationary packets that only spread into one another.
        k = self.parameters.incident_wavenumber
        psi = left * np.exp(1j * k * X) + np.exp(1j * self.parameters.phase) * right * np.exp(-1j * k * X)
        psi /= np.sqrt(np.sum(np.abs(psi) ** 2) * self.spacing ** 2)
        self.engine = GPEEngine(
            psi.shape, spacing=self.spacing,
            config=GPEConfig(interaction_strength=self.parameters.interaction, max_substep=1.0 / 240.0),
        )
        return self.engine.set_wavefunction(psi)

    def set_phase(self, phase: float) -> GPEState:
        return self.reset(PhaseCollisionParameters(
            phase=float(phase), interaction=self.parameters.interaction,
            separation=self.parameters.separation, width=self.parameters.width,
            incident_wavenumber=self.parameters.incident_wavenumber,
        ))

    def set_interaction(self, interaction: float) -> GPEState:
        return self.reset(PhaseCollisionParameters(
            phase=self.parameters.phase, interaction=float(interaction),
            separation=self.parameters.separation, width=self.parameters.width,
            incident_wavenumber=self.parameters.incident_wavenumber,
        ))

    def step(self, dt: float) -> GPEState:
        return self.engine.step(dt)


__all__ = ["PhaseCollisionExperiment2D", "PhaseCollisionParameters"]
