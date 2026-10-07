"""Unitary motion of a measurement aperture under its own generator G."""

from __future__ import annotations

import math
import numpy as np

from qmw.quantum.hilbert_current import hermitian_matrix
from .projector import ProjectorBank
from .projector_bank import transform_projector_bank


class ProjectorBasisMotion:
    def __init__(self, bank: ProjectorBank, generator: object, *, hbar: float = 1.0) -> None:
        self.bank = bank
        self.generator = hermitian_matrix("measurement generator", generator)
        if self.generator.shape != (bank.dimension, bank.dimension):
            raise ValueError("measurement generator and projector bank must share a dimension.")
        if not math.isfinite(float(hbar)) or hbar <= 0.0:
            raise ValueError("hbar must be finite and positive.")
        self.hbar = float(hbar)
        self._eigenvalues, self._eigenvectors = np.linalg.eigh(self.generator)

    def unitary_at(self, time: float) -> np.ndarray:
        if not math.isfinite(float(time)):
            raise ValueError("time must be finite.")
        return (
            self._eigenvectors * np.exp(-1j * self._eigenvalues * float(time) / self.hbar)
        ) @ self._eigenvectors.conj().T

    def bank_at_parameter(self, parameter: float) -> ProjectorBank:
        return transform_projector_bank(
            self.bank, self.unitary_at(parameter), identifier=f"{self.bank.identifier}:moving",
        )

    def derivatives_at_parameter(
        self, parameter: float, *, parameter_rate: float = 1.0,
    ) -> tuple[np.ndarray, ...]:
        rate = float(parameter_rate)
        if not math.isfinite(rate):
            raise ValueError("parameter_rate must be finite.")
        return tuple(
            rate * (-1j / self.hbar) * (
                self.generator @ item.matrix - item.matrix @ self.generator
            )
            for item in self.bank_at_parameter(parameter).projectors
        )

    def bank_at(self, time: float) -> ProjectorBank:
        return self.bank_at_parameter(time)

    def derivatives_at(self, time: float) -> tuple[np.ndarray, ...]:
        return self.derivatives_at_parameter(time)


__all__ = ["ProjectorBasisMotion"]
