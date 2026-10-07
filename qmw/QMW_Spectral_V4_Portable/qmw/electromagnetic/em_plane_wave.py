"""Analytic monochromatic plane wave used as the V1 ground truth."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .jones import JonesState


SPEED_OF_LIGHT_M_S = 299_792_458.0


@dataclass(frozen=True, slots=True)
class MonochromaticPlaneWave:
    """A vacuum plane wave propagating along +z.

    The analytic field is used instead of a numerical Maxwell solver.  Jones
    amplitudes are treated as electric-field units; ``B = z_hat cross E / c``.
    """

    jones: JonesState
    frequency_hz: float = 1.0
    propagation_speed: float = SPEED_OF_LIGHT_M_S

    def __post_init__(self) -> None:
        if not math.isfinite(self.frequency_hz) or self.frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be finite and positive")
        if not math.isfinite(self.propagation_speed) or self.propagation_speed <= 0.0:
            raise ValueError("propagation_speed must be finite and positive")

    @property
    def angular_frequency(self) -> float:
        return math.tau * self.frequency_hz

    @property
    def wavelength(self) -> float:
        return self.propagation_speed / self.frequency_hz

    @property
    def wavenumber(self) -> float:
        return math.tau / self.wavelength

    def carrier_phase(self, z: float, time: float) -> float:
        return self.wavenumber * float(z) - self.angular_frequency * float(time)

    def electric_field(self, z: float, time: float) -> np.ndarray:
        phasor = self.jones.vector() * np.exp(1j * self.carrier_phase(z, time))
        return np.array((phasor[0].real, phasor[1].real, 0.0), dtype=np.float64)

    def magnetic_field(self, z: float, time: float) -> np.ndarray:
        electric = self.electric_field(z, time)
        return np.array(
            (-electric[1], electric[0], 0.0), dtype=np.float64
        ) / self.propagation_speed

    def frame(self, time: float, *, z: float = 0.0):
        from .poincare import PoincareState
        from .polarization_density_matrix import PolarizationDensityMatrix
        from .polarization_state import PolarizationFrame
        from .stokes import StokesParameters

        stokes = StokesParameters.from_jones(self.jones)
        return PolarizationFrame(
            time=float(time),
            z=float(z),
            carrier_phase=self.carrier_phase(z, time),
            electric_field=self.electric_field(z, time),
            magnetic_field=self.magnetic_field(z, time),
            jones=self.jones,
            stokes=stokes,
            poincare=PoincareState.from_stokes(stokes),
            density=PolarizationDensityMatrix.from_jones(self.jones),
        )

    def sample_electric_field(
        self, z_positions: np.ndarray, time: float
    ) -> np.ndarray:
        positions = np.asarray(z_positions, dtype=np.float64)
        phase = self.wavenumber * positions - self.angular_frequency * float(time)
        result = np.zeros((positions.size, 3), dtype=np.float64)
        result[:, 0] = np.real(self.jones.ex * np.exp(1j * phase))
        result[:, 1] = np.real(self.jones.ey * np.exp(1j * phase))
        return result


__all__ = ["MonochromaticPlaneWave", "SPEED_OF_LIGHT_M_S"]
